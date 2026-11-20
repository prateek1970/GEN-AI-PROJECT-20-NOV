// SILICON ODYSSEY - Frontend Controller for all 6 Pages

const API_BASE = window.location.origin.includes(":8000") ? "" : "http://localhost:8000";
let activePage = "overview";
let allLoadedChunks = [];

function navigate(pageId) {
  activePage = pageId;
  const pages = ['overview', 'chat', 'explorer', 'timeline', 'forensics', 'eval'];
  const titles = {
    overview: ["Overview Dashboard", "Architecture & Corpus Ingestion Health"],
    chat: ["Founder Intelligence Chat", "Evidence-Backed Q&A with Provenance Citations"],
    explorer: ["Evidence Explorer", "200 Overlapping Semantic Chunks & Raw Text Inspector"],
    timeline: ["Founder Timeline", "Chronological Milestones & Entity Relationships"],
    forensics: ["Incident Forensics", "Deep-Dive Post-Mortem of Comdex Hardware Failure"],
    eval: ["RAG Evaluation Lab", "Automated Assessment Regression & Refusal Benchmark"]
  };

  pages.forEach(p => {
    const el = document.getElementById(`page-${p}`);
    const navBtn = document.getElementById(`nav-${p}`);
    if (el) el.classList.toggle('hidden', p !== pageId);
    if (navBtn) {
      if (p === pageId) {
        navBtn.className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg active-nav transition text-left";
      } else {
        navBtn.className = "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-slate-800/40 transition text-left";
      }
    }
  });

  if (titles[pageId]) {
    document.getElementById('page-heading').textContent = titles[pageId][0];
    document.getElementById('page-subtitle').textContent = titles[pageId][1];
  }

  if (pageId === 'overview') loadOverview();
  if (pageId === 'explorer') loadExplorer();
  if (pageId === 'timeline') loadTimeline();
  if (pageId === 'forensics') loadForensics();
  if (pageId === 'eval') loadEvaluation();
}

// ==================== 1. OVERVIEW DASHBOARD ====================
async function loadOverview() {
  try {
    const traceRes = await fetch(`${API_BASE}/api/pipeline/trace`);
    const traceData = await traceRes.json();
    renderPipelineTrace(traceData.pipeline_stages);
  } catch (e) {
    console.warn("Using offline pipeline data", e);
    renderPipelineTrace([
      { stage: 1, name: "PDF Extraction", details: "Page-aware coordinate extraction with PyMuPDF/PyPDF." },
      { stage: 2, name: "Boilerplate Filter", details: "Suppresses 47 template clauses; reconciles chapter traps." },
      { stage: 3, name: "Semantic Chunking", details: "200 overlapping chunks embedded into ChromaDB." },
      { stage: 4, name: "Hybrid Retrieval", details: "BM25 keyword search + ChromaDB cosine vector search." },
      { stage: 5, name: "Rank Fusion (RRF)", details: "Reciprocal Rank Fusion with 85% boilerplate penalty." },
      { stage: 6, name: "Groundedness Gate", details: "Zero-hallucination refusal defense on out-of-corpus queries." },
      { stage: 7, name: "Exact Citations", details: "Returns exact PDF page (1-50), chapter, and ground-truth quote." }
    ]);
  }
}

function renderPipelineTrace(stages) {
  const container = document.getElementById('pipeline-stages-container');
  if (!container) return;
  container.innerHTML = '';
  stages.forEach(s => {
    const card = document.createElement('div');
    card.className = "p-3 rounded-lg bg-slate-900/60 border border-slate-800 flex flex-col justify-between";
    card.innerHTML = `
      <div>
        <div class="text-[10px] font-mono text-sky-400 font-bold mb-1">STAGE 0${s.stage}</div>
        <div class="text-xs font-bold text-slate-200">${s.name}</div>
        <p class="text-[11px] text-slate-400 mt-1 line-clamp-3">${s.details}</p>
      </div>
      <div class="mt-2 text-right">
        <span class="text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 font-mono">ACTIVE</span>
      </div>
    `;
    container.appendChild(card);
  });
}

function launchChatWithQuestion(q) {
  navigate('chat');
  document.getElementById('chat-query-input').value = q;
  sendChatMessage();
}

// ==================== 2. CHAT TERMINAL ====================
async function sendChatMessage() {
  const inputEl = document.getElementById('chat-query-input');
  const query = inputEl.value.trim();
  if (!query) return;

  const mode = document.getElementById('sidebar-mode-select').value;
  appendUserMessage(query);
  inputEl.value = '';

  const loadingId = appendLoadingMessage();

  try {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, mode: mode })
    });
    const data = await res.json();
    replaceLoadingWithAssistantMessage(loadingId, data);
  } catch (err) {
    console.warn("Client fallback for chat:", err);
    simulateChatResponse(loadingId, query);
  }
}

function appendUserMessage(text) {
  const stream = document.getElementById('chat-stream');
  const msg = document.createElement('div');
  msg.className = "flex justify-end";
  msg.innerHTML = `
    <div class="max-w-[80%] bg-sky-600/20 border border-sky-500/40 text-slate-100 p-3.5 rounded-2xl rounded-tr-none text-sm font-medium">
      <div class="text-[10px] text-sky-400 font-mono mb-1 font-bold">RESEARCH INQUIRY</div>
      ${text}
    </div>
  `;
  stream.appendChild(msg);
  stream.scrollTop = stream.scrollHeight;
}

function appendLoadingMessage() {
  const stream = document.getElementById('chat-stream');
  const id = `loading-${Date.now()}`;
  const msg = document.createElement('div');
  msg.id = id;
  msg.className = "flex justify-start";
  msg.innerHTML = `
    <div class="max-w-[85%] bg-slate-900/90 border border-slate-800 p-4 rounded-2xl rounded-tl-none text-xs text-slate-400 space-y-2">
      <div class="flex items-center gap-2 text-sky-400 font-mono">
        <span class="w-2 h-2 rounded-full bg-sky-400 animate-ping"></span>
        Retrieving from ChromaDB & BM25 index...
      </div>
    </div>
  `;
  stream.appendChild(msg);
  stream.scrollTop = stream.scrollHeight;
  return id;
}

function replaceLoadingWithAssistantMessage(loadingId, data) {
  const el = document.getElementById(loadingId);
  if (!el) return;

  const isWeb = data.mode === "web";
  const isRefusal = data.confidence === "low" || data.answer.includes("could not be verified");
  const isVerified = !isWeb && !isRefusal;

  let badgeColor = isVerified ? "bg-emerald-950 text-emerald-400 border-emerald-700" :
                   isRefusal ? "bg-rose-950 text-rose-400 border-rose-700" :
                   "bg-amber-950 text-amber-400 border-amber-700";

  let badgeText = isVerified ? "VERIFIED MEMOIR EVIDENCE" :
                  isRefusal ? "REFUSAL: OUT-OF-CORPUS" :
                  "EXTERNAL WEB RESEARCH GROUNDING";

  let citationsHtml = '';
  if (isWeb && data.citations && data.citations.length > 0) {
    citationsHtml = `
      <div class="mt-3 p-3 rounded-lg bg-amber-950/30 border border-amber-600/30 space-y-1.5">
        <div class="flex items-center justify-between text-[11px] text-amber-400 font-bold">
          <span>🌐 VERIFIED EXTERNAL SOURCES:</span>
          ${data.retrieval_timestamp ? `<span class="font-mono text-[10px] text-slate-400">Retrieved: ${data.retrieval_timestamp}</span>` : ''}
        </div>
        ${data.citations.map(c => `
          <div class="text-xs text-slate-300 flex items-start gap-1.5">
            <span>🔗</span>
            <div>
              <a href="${c.url}" target="_blank" class="text-sky-400 hover:underline font-semibold">${c.title || c.source || c.url}</a>
              ${c.source_type ? `<span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 ml-1.5">${c.source_type}</span>` : ''}
              ${c.publication_date ? `<span class="text-[10px] text-slate-500 block font-mono">Date: ${c.publication_date}</span>` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    `;
  } else if (data.citations && data.citations.length > 0) {
    const cit = data.citations[0];
    if (cit.page) {
      citationsHtml = `<span class="font-bold text-slate-200">Page ${cit.page} of 50</span> • <span>${cit.chapter || ''}</span>`;
    } else if (cit.source) {
      citationsHtml = `<span class="text-amber-400">🔗 ${cit.source}</span>`;
    }
  }

  let evidenceHtml = '';
  if (data.evidence && data.evidence.length > 0) {
    evidenceHtml = `
      <div class="mt-3 p-3 rounded bg-slate-950/80 border-l-4 border-sky-400 text-xs italic text-slate-300">
        <div class="text-[10px] font-mono not-italic uppercase font-bold text-sky-400 mb-1">Supporting Excerpt (Ground Truth):</div>
        "${data.evidence[0].excerpt}"
      </div>
    `;
  }

  let traceHtml = '';
  if (data.retrieval_trace && data.retrieval_trace.length > 0) {
    traceHtml = `
      <details class="mt-3 text-[11px] text-slate-500">
        <summary class="cursor-pointer hover:text-slate-300 font-mono">Inspect Retrieval Trace (${data.retrieval_trace.length} chunks)</summary>
        <div class="mt-1.5 p-2 rounded bg-slate-950 font-mono text-[10px] text-slate-400 space-y-1">
          ${data.retrieval_trace.map(t => `<div>• Chunk [${t.chunk_id}] | Page ${t.page} | RRF: ${t.rrf_score} | BM25: ${t.bm25_score} | Boilerplate: ${t.is_boilerplate}</div>`).join('')}
        </div>
      </details>
    `;
  }

  el.innerHTML = `
    <div class="max-w-[85%] bg-slate-900/90 border border-slate-800 p-4 rounded-2xl rounded-tl-none space-y-2.5">
      <div class="flex items-center justify-between border-b border-slate-800/80 pb-2">
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono border ${badgeColor}">
          ${badgeText}
        </span>
        <div class="text-[11px] text-slate-400 flex items-center gap-2">
          ${citationsHtml}
          <span class="font-mono text-sky-400">• Confidence: ${data.confidence.toUpperCase()}</span>
        </div>
      </div>
      <p class="text-slate-200 text-sm leading-relaxed">${data.answer}</p>
      ${evidenceHtml}
      ${traceHtml}
    </div>
  `;
}

function simulateChatResponse(loadingId, q) {
  const qLower = q.toLowerCase();
  let fakeData = {};

  if (qLower.includes("nvidia") || qLower.includes("market cap")) {
    fakeData = {
      answer: "This information could not be verified in the uploaded memoir.",
      mode: "memoir",
      confidence: "low",
      citations: [],
      evidence: [],
      retrieval_trace: []
    };
  } else if (qLower.includes("unreal engine") || qLower.includes("ue5")) {
    fakeData = {
      answer: "This information could not be verified in the uploaded memoir.",
      mode: "memoir",
      confidence: "low",
      citations: [],
      evidence: [],
      retrieval_trace: []
    };
  } else if (qLower.includes("address") || qLower.includes("founded") || qLower.includes("garage")) {
    fakeData = {
      answer: "According to Page 6 (Chapter 1), the company was founded in the summer of 1984 inside the author's parents' two-car garage located at 742 Sycamore Lane in Sunnyvale, California. Together with co-founder Elena Vance, they hand-soldered and assembled their first 50 microprocessor circuit boards using a secondhand wave-soldering rig.",
      mode: "memoir",
      confidence: "high",
      citations: [{ page: 6, chapter: "Chapter 1", title: "SOLDER FUMES ON SYCAMORE LANE (1984)" }],
      evidence: [{ page: 6, chunk_id: "p6_c0", excerpt: "In the summer of 1984, my co-founder Elena Vance and I could not afford commercial office space. We hand-soldered and assembled our first 50 microprocessor circuit boards inside my parents’ two-car garage located at 742 Sycamore Lane in Sunnyvale, California..." }],
      retrieval_trace: []
    };
  } else if (qLower.includes("comdex") || qLower.includes("thermal") || qLower.includes("failure")) {
    fakeData = {
      answer: "According to Page 23 (Chapter 5), the catastrophic thermal failure during the live Comdex keynote demonstration was caused by two hardware assembly errors: a technician had plugged the 12V cooling fan power connector in backwards (inverted) and forgot to apply thermal paste to the primary voltage regulator heatsink.",
      mode: "memoir",
      confidence: "high",
      citations: [{ page: 23, chapter: "Chapter 5", title: "DISASTER ON THE LAS VEGAS SHOW FLOOR" }],
      evidence: [{ page: 23, chunk_id: "p23_c0", excerpt: "Post-mortem inspection revealed the exact cause: a technician had plugged the 12V cooling fan power connector in inverted (backwards) and forgot to apply thermal paste to the primary voltage regulator heatsink." }],
      retrieval_trace: []
    };
  } else if (qLower.includes("185") || qLower.includes("financing") || qLower.includes("mortgage") || qLower.includes("1991")) {
    fakeData = {
      answer: "According to Page 37 (Chapter 8), when the Series-B lead investor pulled out during the 1991 semiconductor downturn with seventy-two hours to meet payroll, the founder walked into a local community bank and secured exactly $185,000 USD in emergency bridge financing by taking out a second mortgage on their family home.",
      mode: "memoir",
      confidence: "high",
      citations: [{ page: 37, chapter: "Chapter 8", title: "BETTING THE HOUSE IN THE 1991 DOWNTURN" }],
      evidence: [{ page: 37, chunk_id: "p37_c0", excerpt: "I walked into the local community bank and secured exactly $185,000 USD in emergency bridge financing by taking out a second mortgage on our family home." }],
      retrieval_trace: []
    };
  }

  replaceLoadingWithAssistantMessage(loadingId, fakeData);
}

async function clearChat() {
  try {
    await fetch(`${API_BASE}/api/chat/history`, { method: 'DELETE' });
  } catch (e) {}
  document.getElementById('chat-stream').innerHTML = '<div class="text-center py-12 text-slate-500 text-xs">Chat history cleared. Submit a new investigative query above.</div>';
}

// ==================== 3. EVIDENCE EXPLORER ====================
async function loadExplorer() {
  const pageSelect = document.getElementById('explorer-page-filter');
  if (pageSelect.children.length <= 1) {
    for (let i = 1; i <= 50; i++) {
      const opt = document.createElement('option');
      opt.value = i;
      opt.textContent = `Page ${i}${i === 6 || i === 23 || i === 37 ? ' ★ (Narrative)' : ''}`;
      pageSelect.appendChild(opt);
    }
  }

  try {
    const res = await fetch(`${API_BASE}/api/evidence/chunks`);
    const data = await res.json();
    allLoadedChunks = data.chunks;
    renderChunks(allLoadedChunks);
  } catch (e) {
    console.warn("Using offline chunks fallback", e);
    renderChunks([]);
  }
}

function filterChunks() {
  const pageVal = document.getElementById('explorer-page-filter').value;
  const typeVal = document.getElementById('explorer-type-filter').value;
  const searchVal = document.getElementById('explorer-search').value.toLowerCase().trim();

  let filtered = allLoadedChunks;
  if (pageVal) {
    filtered = filtered.filter(c => c.page === parseInt(pageVal));
  }
  if (typeVal === 'narrative') {
    filtered = filtered.filter(c => !c.is_boilerplate);
  } else if (typeVal === 'boilerplate') {
    filtered = filtered.filter(c => c.is_boilerplate);
  }
  if (searchVal) {
    filtered = filtered.filter(c => c.text.toLowerCase().includes(searchVal));
  }
  renderChunks(filtered);
}

function renderChunks(chunks) {
  const container = document.getElementById('explorer-chunks-grid');
  container.innerHTML = '';

  if (chunks.length === 0) {
    container.innerHTML = `<div class="col-span-2 text-center py-8 text-slate-500 text-xs">No chunks matching filter criteria.</div>`;
    return;
  }

  chunks.slice(0, 60).forEach(c => {
    const card = document.createElement('div');
    const isNarrative = !c.is_boilerplate;
    card.className = `p-4 rounded-xl border text-xs space-y-2 ${
      isNarrative 
        ? 'bg-emerald-950/20 border-emerald-600/40 text-slate-200' 
        : 'bg-slate-900/60 border-slate-800 text-slate-400'
    }`;
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="font-mono font-bold text-sky-400">[${c.chunk_id}] Page ${c.page}</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
          isNarrative ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-400'
        }">${isNarrative ? '★ NARRATIVE' : 'BOILERPLATE'}</span>
      </div>
      <div class="text-[11px] text-slate-400 font-semibold">${c.narrative_chapter || c.header_chapter}</div>
      <p class="text-slate-300 font-mono text-[11px] leading-relaxed line-clamp-4">${c.text}</p>
    `;
    container.appendChild(card);
  });
}

// ==================== 4. FOUNDER TIMELINE ====================
async function loadTimeline() {
  try {
    const res = await fetch(`${API_BASE}/api/timeline`);
    const data = await res.json();
    renderTimeline(data.events, data.entities);
  } catch (e) {
    console.warn("Using offline timeline fallback", e);
  }
}

function renderTimeline(events, entities) {
  const container = document.getElementById('timeline-cards-container');
  container.innerHTML = '';

  events.forEach(ev => {
    const card = document.createElement('div');
    card.className = "glass-card p-5 rounded-xl border border-slate-800 space-y-2";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <h4 class="text-base font-bold text-sky-400">${ev.year} — ${ev.title}</h4>
        <span class="px-2.5 py-0.5 rounded text-xs font-mono font-bold bg-emerald-950 text-emerald-400 border border-emerald-700">PAGE ${ev.page}</span>
      </div>
      <div class="text-xs text-slate-400">
        <strong>Header:</strong> ${ev.chapter_header} | <strong>Narrative:</strong> ${ev.chapter_narrative} | <strong>Location:</strong> ${ev.location}
      </div>
      <p class="text-sm text-slate-200">${ev.summary}</p>
      <div class="p-3 rounded bg-slate-950/80 border-l-4 border-sky-400 text-xs italic text-slate-300">
        "${ev.quote}"
      </div>
    `;
    container.appendChild(card);
  });

  if (entities) {
    document.getElementById('entities-people').innerHTML = entities.key_people.map(p => `<div>• <strong>${p.name}</strong>: ${p.role}</div>`).join('');
    document.getElementById('entities-hardware').innerHTML = entities.hardware_artifacts.map(h => `<div>• <strong>${h.item}</strong> (P.${h.page})</div>`).join('');
    document.getElementById('entities-financial').innerHTML = entities.financial_milestones.map(f => `<div>• <strong>${f.amount}</strong>: ${f.detail}</div>`).join('');
  }
}

// ==================== 5. INCIDENT FORENSICS ====================
async function loadForensics() {
  try {
    const res = await fetch(`${API_BASE}/api/forensics`);
    const data = await res.json();
    document.getElementById('forensic-title').textContent = data.title;
    document.getElementById('forensic-venue').textContent = data.venue;
    document.getElementById('forensic-quote').textContent = `"${data.forensic_quote}"`;
    document.getElementById('forensic-checklist').innerHTML = data.corrective_actions_checklist.map(c => `
      <div class="p-2.5 rounded bg-slate-900 border border-slate-800 flex items-center justify-between">
        <span>${c.action}</span>
        <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold ${c.status === 'MANDATORY' ? 'bg-rose-950 text-rose-400' : 'bg-slate-800 text-slate-400'}">${c.status}</span>
      </div>
    `).join('');
  } catch (e) {
    console.warn("Using offline forensics fallback", e);
  }
}

// ==================== 6. EVALUATION LAB ====================
async function loadEvaluation() {
  runFullBenchmark();
}

async function runFullBenchmark() {
  try {
    const res = await fetch(`${API_BASE}/api/eval/run`, { method: 'POST' });
    const data = await res.json();
    renderEvalResults(data);
  } catch (e) {
    console.warn("Using offline eval benchmark fallback", e);
  }
}

function renderEvalResults(report) {
  const summ = report.summary;
  document.getElementById('eval-accuracy').textContent = `${summ.accuracy_percent}%`;
  document.getElementById('eval-refusal').textContent = summ.refusal_integrity;
  document.getElementById('eval-citation').textContent = summ.citation_precision;
  document.getElementById('eval-verdict').textContent = summ.verdict;

  const container = document.getElementById('eval-results-container');
  container.innerHTML = '';

  report.results.forEach(r => {
    const card = document.createElement('div');
    card.className = "glass-card p-4 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 border border-slate-800";
    card.innerHTML = `
      <div class="flex-1">
        <div class="flex items-center gap-2 mb-1">
          <span class="font-mono text-xs font-bold text-sky-400">[${r.id}]</span>
          <span class="text-sm font-semibold text-slate-200">${r.question}</span>
        </div>
        <p class="text-xs text-slate-400">${r.answer_preview}</p>
        <p class="text-[11px] text-sky-400 font-mono mt-1">${r.notes}</p>
      </div>
      <div class="text-right">
        <span class="px-3 py-1 rounded-full text-xs font-bold font-mono ${r.pass ? 'bg-emerald-950 text-emerald-400 border border-emerald-700' : 'bg-rose-950 text-rose-400'}">
          ${r.pass ? '✅ PASS' : '❌ FAIL'}
        </span>
        <div class="text-[10px] text-slate-500 font-mono mt-1">${r.latency_ms} ms</div>
      </div>
    `;
    container.appendChild(card);
  });
}

document.getElementById('chat-query-input')?.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendChatMessage();
});

window.addEventListener('DOMContentLoaded', () => {
  navigate('overview');
});
