const uploadForm = document.getElementById("upload-form");
const queryForm = document.getElementById("query-form");
const uploadStatus = document.getElementById("upload-status");
const queryStatus = document.getElementById("query-status");
const answerEl = document.getElementById("answer");
const analysisEl = document.getElementById("analysis");
const evidenceQualityEl = document.getElementById("evidence-quality");
const chunksEl = document.getElementById("chunks");

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById("file-input");
  if (!fileInput.files.length) return;
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);
  uploadStatus.textContent = "Uploading…";
  try {
    const res = await fetch("/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    uploadStatus.textContent = `Indexed ${data.filename} (${data.chunks_created} chunks)`;
  } catch (err) {
    uploadStatus.textContent = err.message;
  }
});

queryForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const question = document.getElementById("question").value.trim();
  if (!question) return;
  queryStatus.textContent = "Querying…";
  chunksEl.innerHTML = "";
  try {
    const res = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Query failed");
    queryStatus.textContent = "Done.";
    evidenceQualityEl.textContent = data.evidence_quality;
    answerEl.textContent = data.answer;
    analysisEl.textContent = data.analysis_summary;
    for (const chunk of data.retrieved_chunks) {
      const div = document.createElement("div");
      div.className = "chunk";
      div.innerHTML = `<p><strong>${chunk.source}</strong> · chunk ${chunk.chunk_index} · score ${chunk.score ?? "n/a"}</p><p>${chunk.text}</p>`;
      chunksEl.appendChild(div);
    }
  } catch (err) {
    queryStatus.textContent = err.message;
  }
});
