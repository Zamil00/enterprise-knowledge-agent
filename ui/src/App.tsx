import { useMemo, useState } from "react";
import {
  Upload,
  FileText,
  Sparkles,
  ShieldCheck,
  Database,
  Search,
  AlertCircle,
  CheckCircle2,
  Loader2,
} from "lucide-react";
import "./index.css";

const API_BASE = "http://127.0.0.1:8000";

const sampleQuestions = [
  "What is the main purpose of this document?",
  "Who is the applicant?",
  "What skills are highlighted?",
];

type UploadResult = {
  document_id: string;
  filename: string;
  chunks_created: number;
  message: string;
  processing_time_seconds?: number;
};

type RetrievedChunk = {
  text: string;
  source: string;
  chunk_index?: number;
  document_id?: string;
  score?: number;
};

type QueryResult = {
  answer: string;
  analysis_summary: string;
  evidence_quality: string;
  retrieved_chunks: RetrievedChunk[];
  processing_time_seconds?: number;
};

function QualityBadge({ value }: { value: string }) {
  const normalized = (value || "unknown").toLowerCase();

  let className = "badge badge-low";
  if (normalized === "high") className = "badge badge-high";
  if (normalized === "medium") className = "badge badge-medium";

  return <span className={className}>{value || "unknown"}</span>;
}

function StatCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="stat-card">
      <div className="stat-top">
        {icon}
        <span>{label}</span>
      </div>
      <div className="stat-value">{value}</div>
    </div>
  );
}

export default function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [question, setQuestion] = useState("");
  const [uploading, setUploading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [queryStage, setQueryStage] = useState("");
  const [error, setError] = useState("");

  const canAsk = useMemo(() => {
    return !!uploadResult && question.trim().length >= 3 && !querying;
  }, [uploadResult, question, querying]);

  async function handleUpload() {
    if (!selectedFile) return;

    setError("");
    setUploading(true);
    setUploadResult(null);
    setQueryResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch(`${API_BASE}/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Upload failed.");
      }

      const data = await response.json();
      setUploadResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setUploading(false);
    }
  }

  async function handleQuery() {
    if (!canAsk || !uploadResult?.document_id) return;

    setError("");
    setQueryResult(null);
    setQuerying(true);

    try {
      setQueryStage("Retrieving relevant chunks...");
      await new Promise((r) => setTimeout(r, 250));

      setQueryStage("Analyzing evidence...");
      await new Promise((r) => setTimeout(r, 250));

      setQueryStage("Generating final answer...");

      const response = await fetch(`${API_BASE}/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
          document_id: uploadResult.document_id,
        }),
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || "Query failed.");
      }

      const data = await response.json();
      setQueryResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed.");
    } finally {
      setQuerying(false);
      setQueryStage("");
    }
  }

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <div>
            <div className="hero-pill">
              <Sparkles size={14} />
              Enterprise Knowledge Agent
            </div>
            <h1>Multi-Agent Document Intelligence</h1>
            <p>
              Upload a document, ask grounded questions, and inspect answer
              quality through evidence-aware retrieval, analysis, and reporting.
            </p>

            <div className="status-row">
              <span className="status-pill">API Connected</span>
              <span className="status-pill">Vector Store Ready</span>
              <span className="status-pill">Model Ready</span>
            </div>
          </div>

          <div className="stats-grid">
            <StatCard
              label="Vector Store"
              value="ChromaDB"
              icon={<Database size={16} />}
            />
            <StatCard
              label="Evidence"
              value="Grounded"
              icon={<ShieldCheck size={16} />}
            />
            <StatCard
              label="Flow"
              value="LangGraph"
              icon={<Search size={16} />}
            />
          </div>
        </header>

        {error && (
          <div className="error-box">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <main className="main-grid">
          <section className="sidebar">
            <div className="card">
              <div className="card-header">
                <h2>
                  <Upload size={18} />
                  Upload Document
                </h2>
                <p>
                  Supported formats: PDF, DOCX, TXT. The backend extracts text,
                  chunks content, and indexes embeddings into ChromaDB.
                </p>
              </div>

              <div className="card-body">
                <label className="upload-box">
                  <div className="upload-box-inner">
                    <FileText size={18} />
                    <div>
                      <strong>Choose a document</strong>
                      <p>
                        {selectedFile
                          ? selectedFile.name
                          : "Select one file to index for grounded Q&A."}
                      </p>
                    </div>
                  </div>

                  <input
                    type="file"
                    accept=".pdf,.docx,.txt"
                    hidden
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                  />
                </label>

                <button
                  className="primary-btn"
                  onClick={handleUpload}
                  disabled={!selectedFile || uploading}
                >
                  {uploading ? (
                    <>
                      <Loader2 className="spin" size={16} />
                      Indexing document...
                    </>
                  ) : (
                    <>
                      <Upload size={16} />
                      Upload and Index
                    </>
                  )}
                </button>

                {uploadResult && (
                  <div className="success-box">
                    <div className="success-title">
                      <CheckCircle2 size={16} />
                      Document indexed successfully
                    </div>
                    <p>
                      <span>File:</span> {uploadResult.filename}
                    </p>
                    <p>
                      <span>Document ID:</span> {uploadResult.document_id}
                    </p>
                    <p>
                      <span>Chunks created:</span> {uploadResult.chunks_created}
                    </p>
                    {typeof uploadResult.processing_time_seconds === "number" && (
                      <p>
                        <span>Index time:</span>{" "}
                        {uploadResult.processing_time_seconds}s
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2>Ask a Grounded Question</h2>
                <p>
                  The system retrieves evidence first, evaluates support
                  strength, and only then generates a final answer.
                </p>
              </div>

              <div className="card-body">
                <textarea
                  className="question-box"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What is the main purpose of this document?"
                />

                <div className="sample-questions">
                  {sampleQuestions.map((q) => (
                    <button
                      key={q}
                      type="button"
                      className="sample-btn"
                      onClick={() => setQuestion(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>

                <button
                  className="secondary-btn"
                  onClick={handleQuery}
                  disabled={!canAsk}
                >
                  {querying ? (
                    <>
                      <Loader2 className="spin" size={16} />
                      {queryStage || "Running retrieval and analysis..."}
                    </>
                  ) : (
                    <>
                      <Search size={16} />
                      Ask Question
                    </>
                  )}
                </button>
              </div>
            </div>
          </section>

          <section className="content">
            <div className="card">
              <div className="card-header row-between">
                <div>
                  <h2>Final Answer</h2>
                  <p>
                    Business-style output grounded in retrieved source evidence.
                  </p>
                </div>
                <QualityBadge value={queryResult?.evidence_quality || "not run"} />
              </div>

              <div className="card-body">
                <div className="answer-box">
                  {queryResult?.answer ||
                    "Your grounded response will appear here after the system completes retrieval, evidence analysis, and reporting."}
                </div>

                {typeof queryResult?.processing_time_seconds === "number" && (
                  <p className="timing-note">
                    Response time: {queryResult.processing_time_seconds}s
                  </p>
                )}
              </div>
            </div>

            <div className="split-grid">
              <div className="card">
                <div className="card-header">
                  <h2>Analysis Summary</h2>
                  <p>
                    Intermediate reasoning layer used to assess support
                    strength, ambiguity, and missing evidence.
                  </p>
                </div>
                <div className="card-body">
                  <div className="analysis-box">
                    {queryResult?.analysis_summary ||
                      "Evidence review output will appear here, including what is directly supported, ambiguous, or missing."}
                  </div>
                </div>
              </div>

              <div className="card">
                <div className="card-header">
                  <h2>Retrieved Evidence</h2>
                  <p>
                    Top chunks returned by the Retrieval Agent, including source
                    and similarity score.
                  </p>
                </div>
                <div className="card-body">
                  {queryResult?.retrieved_chunks?.length ? (
                    <div className="chunks-list">
                      {queryResult.retrieved_chunks.map((chunk, idx) => (
                        <div className="chunk-card" key={`${chunk.source}-${idx}`}>
                          <div className="chunk-meta">
                            <span>{chunk.source}</span>
                            {typeof chunk.chunk_index !== "undefined" && (
                              <span>chunk {chunk.chunk_index}</span>
                            )}
                            {typeof chunk.score !== "undefined" && (
                              <span>score {Number(chunk.score).toFixed(4)}</span>
                            )}
                          </div>
                          <p>{chunk.text}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="empty-box">
                      Top-ranked source chunks will appear here with source
                      metadata and similarity score.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h2>System Notes</h2>
                <p>
                  This frontend is designed as a portfolio-ready demo surface
                  for a production-minded MVP.
                </p>
              </div>
              <div className="card-body">
                <div className="notes-grid">
                  <div className="note-card">
                    <h3>Retrieval Layer</h3>
                    <p>
                      Vector search over uploaded document chunks using ChromaDB
                      embeddings.
                    </p>
                  </div>
                  <div className="note-card">
                    <h3>Analysis Layer</h3>
                    <p>
                      Intermediate agent checks what is directly supported,
                      ambiguous, or missing.
                    </p>
                  </div>
                  <div className="note-card">
                    <h3>Report Layer</h3>
                    <p>
                      Final answer stays grounded in evidence and returns a
                      visible quality signal.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}