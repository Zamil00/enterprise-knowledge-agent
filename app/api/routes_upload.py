import logging
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import get_settings
from app.core.schemas import UploadResponse
from app.services.chunker import chunk_text
from app.services.document_loader import (
    SUPPORTED_EXTENSIONS,
    UnsupportedFileTypeError,
    extract_text,
)
from app.services.embeddings import embed_texts
from app.services.vector_store import add_chunks

router = APIRouter(prefix="/upload", tags=["upload"])
logger = logging.getLogger(__name__)


@router.post("", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    start_time = time.perf_counter()
    settings = get_settings()

    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Supported file types: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds {settings.max_file_size_mb} MB limit",
        )

    document_id = str(uuid.uuid4())[:8]
    filename = f"{document_id}_{file.filename}"
    target_path = Path(settings.upload_dir) / filename
    target_path.write_bytes(content)

    try:
        text = extract_text(str(target_path))
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Failed to extract text")
        raise HTTPException(status_code=500, detail="Failed to process document") from exc

    if not text.strip():
        raise HTTPException(status_code=400, detail="Document appears empty after extraction")

    chunks = chunk_text(
        text=text,
        max_chunk_size=settings.max_chunk_size,
        overlap=settings.chunk_overlap,
    )
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No chunks could be created from the uploaded document",
        )

    try:
        embeddings = embed_texts(chunks)
        chunk_count = add_chunks(
            document_id=document_id,
            filename=file.filename or filename,
            chunks=chunks,
            embeddings=embeddings,
        )
    except Exception as exc:
        logger.exception("Failed to index document")
        raise HTTPException(status_code=500, detail="Failed to index document") from exc

    processing_time_seconds = round(time.perf_counter() - start_time, 3)
    logger.info(
        "Upload completed | document_id=%s | filename=%s | chunks=%s | time=%.3fs",
        document_id,
        file.filename or filename,
        chunk_count,
        processing_time_seconds,
    )

    return UploadResponse(
        document_id=document_id,
        filename=file.filename or filename,
        chunks_created=chunk_count,
        message="Document uploaded and indexed successfully.",
        processing_time_seconds=processing_time_seconds,
    )