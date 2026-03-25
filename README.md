# Enterprise Knowledge Agent

A production-minded multi-agent RAG system for grounded document Q&A using FastAPI, LangGraph, ChromaDB, and React.

This project allows users to upload PDF, DOCX, and TXT documents, index them into a vector store, and ask grounded questions through a clean demo interface. The system retrieves relevant chunks, evaluates evidence quality, and returns a final answer together with an analysis summary and source evidence.

---

## What it does

- accepts PDF, DOCX, and TXT uploads
- extracts and chunks document text
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
- displays measured timing for:
  - indexing
  - query execution

---

## Why this project matters

Many document-Q&A demos stop at a basic retrieval pipeline and a final generated answer.

This project is designed to go one step further:

- it separates retrieval, evidence analysis, and answer generation
- it exposes evidence quality instead of hiding uncertainty
- it makes the system easier to reason about as a product, not only as a model call
- it demonstrates a more architect-oriented way of thinking about GenAI workflows

This makes the project more suitable as a portfolio asset for a **GenAI Solutions Engineer / Solutions Architect track**.

---

## Architecture overview

### High-level flow

1. User uploads a document
2. Backend extracts the text
3. Text is split into chunks
4. Chunks are embedded and stored in ChromaDB
5. User asks a grounded question
6. Retrieval Agent fetches relevant chunks
7. Analysis Agent checks whether the evidence is actually sufficient
8. Report Agent generates the final grounded answer
9. UI shows:
   - answer
   - analysis summary
   - evidence quality
   - retrieved source chunks

---

## Architecture decisions

### Why FastAPI
FastAPI was chosen because it provides a clean and lightweight backend structure for file upload, indexing, and query orchestration. It is well-suited for modular MVPs and easy to extend into service-oriented architectures later.

### Why LangGraph
LangGraph was used to make the retrieval, analysis, and reporting steps explicit rather than hiding everything inside a single chain.

This improves:
- interpretability
- extensibility
- separation of responsibilities
- portfolio clarity

### Why ChromaDB
ChromaDB was selected for the MVP because it is simple to run locally and integrates well with embedding-based retrieval workflows.

For a larger production setup, this could later be replaced with a more scalable managed vector database if required.

### Why a multi-agent structure
Instead of going directly from query to answer, the workflow is intentionally split into:
- retrieval
- analysis
- reporting

This separation better reflects how enterprise-grade AI systems should reason about evidence rather than only produce fluent outputs.

### Why evidence quality is exposed
A major weakness of many GenAI demos is that they produce confident-looking answers even when evidence is weak.

This project introduces a visible `evidence_quality` signal to make uncertainty explicit and reduce blind trust in the final answer.

---

## Trade-offs

### Why not a single-chain RAG pipeline?
A simpler chain would require less code and fewer moving parts.

However, the multi-agent structure was preferred because it:
- better demonstrates system design thinking
- makes the reasoning flow easier to explain
- creates a stronger foundation for future extensions

### Why not multi-user auth in v1?
Authentication and user isolation were intentionally excluded from the MVP to keep the focus on grounded retrieval quality, evidence handling, and UI clarity.

A production version would add:
- authentication
- user/session isolation
- role-based access
- document scoping

### Why local persistence for now?
The current version is optimized for:
- fast local setup
- clear portfolio demonstration
- easy reproducibility

It is intentionally not yet optimized for:
- multi-user concurrency
- large-scale storage
- long-running hosted environments

---

## Demo preview

### Overview
![Enterprise Knowledge Agent Overview](docs/images/eka_overview.png)

### Analysis and Evidence View
![Enterprise Knowledge Agent Analysis and Evidence](docs/images/eka_analysis_evidence.png)

---

## Project structure

```text
enterprise-knowledge-agent/
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   └── data/
├── sample_docs/
├── tests/
├── ui/
│   ├── src/
│   └── ...
├── docs/
│   └── images/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Local setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the environment file

```bash
cp .env.example .env
```

### 4. Add your OpenAI API key to `.env`

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PERSIST_DIR=app/data/chroma
UPLOAD_DIR=app/data/uploads
LOG_LEVEL=INFO
TOP_K_RESULTS=5
MAX_CHUNK_SIZE=800
CHUNK_OVERLAP=120
MAX_FILE_SIZE_MB=10
COLLECTION_NAME=enterprise_knowledge_agent
```

### 5. Start the backend

```bash
python -m uvicorn app.main:app --reload
```

Backend runs at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the frontend

```bash
cd ui
npm install
npm run dev
```

Frontend runs at:

```text
http://127.0.0.1:5173
```

---

## Main API endpoints

### Health
- `GET /health`

### Upload
- `POST /upload`

### Query
- `POST /query`

---

## Example workflow

1. Upload a document
2. Wait for indexing to complete
3. Ask a grounded question such as:
   - `What is the main purpose of this document?`
   - `Who is the applicant?`
   - `What skills are highlighted?`
4. Inspect:
   - final answer
   - analysis summary
   - evidence quality
   - retrieved source chunks

---
## Evidence behavior and evaluation logic

One of the main goals of this project is not only to answer questions, but to do so in a way that is transparent about evidence strength.

The system is intentionally designed to behave differently depending on how strongly the uploaded document supports the query.

### 1. Directly supported questions

If the uploaded document clearly supports the answer, the system should:

- return a grounded answer
- surface relevant retrieved chunks
- produce an analysis summary that reflects direct support
- assign a stronger evidence-quality signal when appropriate

This is the expected behavior for straightforward document understanding tasks where the answer is explicitly available in the indexed content.

### 2. Partially supported questions

If the document only partially supports the answer, the system should behave conservatively.

In these cases, the workflow should:

- acknowledge what is supported
- identify ambiguity or missing detail
- avoid overcommitting beyond the retrieved evidence
- reflect uncertainty in the analysis layer

This behavior is important because enterprise-facing systems should not treat partial evidence as full certainty.

### 3. Unsupported questions

If the document does not support the question, the system should avoid confident hallucination.

Instead, it should:

- avoid fabricating missing information
- state that evidence is insufficient
- return a weaker evidence-quality signal
- make the lack of support visible through the analysis summary

This is one of the most important design goals of the project: the system should fail transparently rather than fail confidently.

---

## Example evaluation scenarios

### Scenario A — Directly supported

**Document type:** PDF / DOCX / TXT  
**Example question:**  
`What is the main purpose of this document?`

**Expected behavior:**  
The system should produce a grounded summary based on retrieved chunks and return an evidence-quality signal that matches the available support.

### Scenario B — Partially supported

**Example question:**  
`What long-term initiatives does the author want to lead in the future?`

**Expected behavior:**  
If motivation or direction is implied but not explicitly stated, the answer should remain cautious and highlight ambiguity rather than infer unsupported specifics.

### Scenario C — Unsupported

**Example question:**  
`What is the company revenue forecast for 2027?`

**Expected behavior:**  
If the uploaded document contains no such information, the system should avoid inventing an answer and explicitly communicate insufficient evidence.

---

## Why this matters

This evidence-aware behavior is a key differentiator of the project.

Instead of treating document Q&A as a simple retrieval-plus-generation task, the system introduces an intermediate reasoning layer that evaluates support strength before producing the final answer.

That makes the workflow more aligned with enterprise expectations around:

- explainability
- trustworthiness
- conservative answer behavior
- reviewability of generated outputs

In other words, the system is not only optimized to answer — it is also designed to signal when it should *not* answer with confidence.

---


## Benchmark snapshot

| Test Case | Document Type | Chunks Created | Index Time | Query Time | Evidence Quality | Result |
|---|---:|---:|---:|---:|---|---|
| Company Policy | TXT | 2 | 3.747s | 19.875s | Strong | Correct |
| History of Economics | DOCX | 3 | 0.864s | 17.908s | Strong | Correct |
| Ghibli Style Video Prompts | PDF | 12 | 0.908s | 7.908s | Strong | Correct |

---

## What this project demonstrates

This project is designed to show capability in:

- modular GenAI application design
- multi-agent workflow orchestration
- grounded document question answering
- evidence-aware answer generation
- retrieval transparency
- backend/frontend integration
- production-minded MVP thinking
- measurable system behavior through timing metrics

---

## Current limitations

This is an MVP and not a full production deployment.

Current limitations:

- no authentication
- no multi-user document isolation
- no async background indexing jobs
- no hosted deployment by default
- no advanced observability or tracing stack
- no reranking layer beyond the current retrieval flow
- limited benchmark coverage

---

## Production path

This project is intentionally scoped as a production-minded MVP, not a full enterprise deployment.

If expanded into a real production system, the next architectural steps would be:

- add authentication and user/session isolation
- replace local-only persistence with a hosted storage strategy
- move indexing into async background jobs
- add document management across multiple uploads
- improve retrieval quality through reranking and evaluation loops
- introduce tracing, observability, and failure monitoring
- add environment-based deployment configuration and secret management
- support team-based usage and permissions

The current version focuses on the most important first step:
making document-grounded GenAI responses explainable, measurable, and evidence-aware.

---

## Future improvements

- authentication and session isolation
- hosted vector store option
- reranking layer for retrieval quality
- better document management across multiple uploads
- evaluation suite for weak-evidence and unsupported queries
- observability and tracing
- public demo deployment
- richer UI tooltips for evidence interpretation

---

## Portfolio context

This project is part of a broader architect-track portfolio focused on:

- GenAI applications
- evidence-aware workflows
- AI operations and governance
- production-minded AI system design

Within that portfolio, this project represents the **application layer**:
a grounded GenAI workflow that turns uploaded documents into explainable, reviewable answers.

---

## Author

**Zamil Hasanov**

- LinkedIn: https://www.linkedin.com/in/zamillion/
- GitHub: https://github.com/Zamil00