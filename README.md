# Enterprise Knowledge Agent

A production-minded MVP for document-grounded Q&A using a multi-agent RAG workflow.

## What it does
- accepts PDF, DOCX, and TXT uploads
- extracts and chunks text
- stores embeddings in ChromaDB
- runs a LangGraph workflow with:
  - Retrieval Agent
  - Analysis Agent
  - Report Agent
- returns:
  - final answer
  - analysis summary
  - evidence quality flag
  - retrieved evidence chunks

## Why this project matters
This project was built as a credible portfolio asset for a GenAI Solutions Engineer / Solutions Architect track. It demonstrates modular backend design, evidence-aware answer generation, and a clear end-to-end path from document ingestion to grounded response generation.

## Architecture
1. Upload endpoint saves and parses documents.
2. Text is chunked and embedded.
3. Chunks are persisted in ChromaDB.
4. Query endpoint invokes a LangGraph pipeline.
5. Retrieval Agent fetches relevant chunks.
6. Analysis Agent checks evidence sufficiency.
7. Report Agent produces a grounded response.

## Demo Preview

### Overview
![Enterprise Knowledge Agent Overview](docs/images/eka_overview.png)

### Analysis and Evidence View
![Enterprise Knowledge Agent Analysis and Evidence](docs/images/eka_analysis_evidence.png)

## Project structure
```text
enterprise-knowledge-agent/
├── app/
├── ui/
├── tests/
├── sample_docs/
├── requirements.txt
└── README.md


## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Add your OpenAI API key to `.env`.

Run the API:
```bash
uvicorn app.main:app --reload
```

Run the Frontend:
cd ui
npm install
npm run dev


Open:
- API docs: `http://127.0.0.1:8000/docs`
- UI: `http://127.0.0.1:5173`

## API endpoints
- `GET /health`
- `POST /upload`
- `POST /query`

## Example workflow
1. Upload `sample_docs/company_policy.txt`
2. Ask: `What does the policy say about home-office equipment reimbursement?`
3. Inspect answer, analysis summary, and evidence chunks

## Current limitations
- single-tenant MVP
- no authentication
- no async processing
- no evaluation dashboard
- no retry / fallback model strategy

## Future improvements
- user/session isolation
- richer metadata filters
- ingestion job status tracking
- structured citations in final answer
- model fallback and observability dashboard

## Suggested benchmarks before publishing
- average upload/indexing latency for small and medium files
- average query latency
- top-k retrieval quality on 10–20 test questions
- behavior under weak-evidence questions
