from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logger import setup_logger
from app.api.routes_health import router as health_router
from app.api.routes_upload import router as upload_router
from app.api.routes_query import router as query_router


setup_logger(settings.log_level)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Enterprise Knowledge Agent",
    version="0.1.0",
    description="Multi-agent RAG system for document-grounded Q&A.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(upload_router)
app.include_router(query_router)


@app.get("/")
def root():
    return {
        "message": "Enterprise Knowledge Agent API is running.",
        "docs": "/docs",
        "health": "/health",
    }
