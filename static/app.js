/**
 * CogniRetrieve.ai - Client Application Logic
 * Supports Multi-Agent RAG Orchestration, Document Ingestion, Web Speech API (STT & TTS),
 * and Multi-Domain Retrieval Evaluation.
 */

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initStatsAndDocuments();
    initIngestionModule();
    initQueryAndSpeechModule();
    initEvaluationModule();
});

/* ==========================================================================
   1. NAVIGATION & TAB SYSTEM
   ========================================================================== */
function initNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // Hero buttons
    document.getElementById('hero-get-started')?.addEventListener('click', () => {
        document.querySelector('[data-tab="tab-query"]')?.click();
    });
    document.getElementById('hero-upload-doc')?.addEventListener('click', () => {
        document.querySelector('[data-tab="tab-ingest"]')?.click();
    });
}

/* ==========================================================================
   2. STATS & DOCUMENT LISTING
   ========================================================================== */
async function initStatsAndDocuments() {
    await fetchStats();
    await fetchDocuments();
    document.getElementById('btn-refresh-docs')?.addEventListener('click', fetchDocuments);
}

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (data.status === 'success') {
            const stats = data.data;
            document.getElementById('stat-docs').textContent = stats.total_documents || 0;
            document.getElementById('stat-chunks').textContent = stats.total_chunks || 0;
        }
    } catch (err) {
        console.error('Failed to fetch stats:', err);
    }
}

async function fetchDocuments() {
    const tbody = document.getElementById('docs-table-body');
    if (!tbody) return;

    try {
        const res = await fetch('/api/documents');
        const data = await res.json();
        if (data.status === 'success') {
            const docs = data.documents;
            if (docs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="text-center">No knowledge base documents uploaded yet.</td></tr>';
                return;
            }

            tbody.innerHTML = docs.map(doc => `
                <tr>
                    <td><code>${doc.document_id}</code></td>
                    <td><strong>${escapeHtml(doc.file_name)}</strong></td>
                    <td><span class="badge badge-info">${escapeHtml(doc.domain)}</span></td>
                    <td><span class="badge badge-primary">${(doc.file_type || 'file').toUpperCase()}</span></td>
                    <td>${doc.total_chunks || doc.chunks_count || 0} chunks</td>
                    <td><span class="badge badge-success">Indexed</span></td>
                    <td>
                        <button class="btn btn-secondary btn-sm" onclick="deleteDoc('${doc.document_id}')">
                            <i class="fa-solid fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to fetch documents:', err);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger">Error loading documents.</td></tr>';
    }
}

window.deleteDoc = async function(docId) {
    if (!confirm(`Are you sure you want to delete document ${docId}?`)) return;
    try {
        const res = await fetch(`/api/documents/${docId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.status === 'success') {
            fetchStats();
            fetchDocuments();
        }
    } catch (err) {
        alert(`Delete failed: ${err.message}`);
    }
};

/* ==========================================================================
   3. INGESTION MODULE (PDF, DOCX, TXT, CSV)
   ========================================================================== */
function initIngestionModule() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const selectedInfo = document.getElementById('selected-file-info');
    const selectedFilename = document.getElementById('selected-filename');
    const btnRemove = document.getElementById('btn-remove-selected');
    const ingestForm = document.getElementById('ingest-form');
    const logBox = document.getElementById('ingest-status-log');
    const logText = document.getElementById('ingest-log-text');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('hover');
    });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('hover'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('hover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateSelectedFile();
        }
    });

    fileInput.addEventListener('change', updateSelectedFile);

    function updateSelectedFile() {
        if (fileInput.files.length) {
            selectedFilename.textContent = fileInput.files[0].name;
            selectedInfo.classList.remove('hidden');
        } else {
            selectedInfo.classList.add('hidden');
        }
    }

    btnRemove?.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.value = '';
        updateSelectedFile();
    });

    ingestForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) {
            alert('Please select a file to upload.');
            return;
        }

        const formData = new FormData(ingestForm);
        logBox.classList.remove('hidden');
        logText.textContent = `[Processing] Uploading ${fileInput.files[0].name}...\n[Parsing] Extracting text & structure...\n[Chunking] Generating overlapping vectors...`;

        try {
            const res = await fetch('/api/ingest', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (res.ok && data.status === 'success') {
                logText.textContent += `\n[Success] Ingested document ID: ${data.document.document_id} (${data.chunks_created} chunks indexed in Vector Store)`;
                fileInput.value = '';
                updateSelectedFile();
                fetchStats();
                fetchDocuments();
            } else {
                logText.textContent += `\n[Error] ${data.detail || 'Ingestion failed.'}`;
            }
        } catch (err) {
            logText.textContent += `\n[Error] ${err.message}`;
        }
    });
}

/* ==========================================================================
   4. MULTI-AGENT QUERY & WEB SPEECH API MODULE (STT & TTS)
   ========================================================================== */
function initQueryAndSpeechModule() {
    const queryInput = document.getElementById('user-query-input');
    const btnSubmit = document.getElementById('btn-submit-query');
    const btnClear = document.getElementById('btn-clear-query');
    const btnStt = document.getElementById('btn-stt');
    const sttStatus = document.getElementById('stt-status');
    const btnTts = document.getElementById('btn-tts');
    const outputSection = document.getElementById('query-output-section');
    const responseTextBody = document.getElementById('response-text-body');
    const confidenceBadge = document.getElementById('confidence-badge');
    const citationsContainer = document.getElementById('citations-container');

    let currentResponseText = '';

    // Web Speech API - Speech-to-Text (STT) Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isListening = true;
            btnStt.classList.add('listening');
            sttStatus.classList.add('listening');
            sttStatus.innerHTML = '<i class="fa-solid fa-circle-dot"></i> Listening... Speak now';
        };

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            queryInput.value = transcript;
        };

        recognition.onerror = (event) => {
            console.error('Speech Recognition Error:', event.error);
            stopSTT();
            sttStatus.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> Mic Error: ${event.error}`;
        };

        recognition.onend = () => {
            stopSTT();
        };

        btnStt.addEventListener('click', () => {
            if (isListening) {
                recognition.stop();
            } else {
                try {
                    recognition.start();
                } catch (e) {
                    console.error(e);
                }
            }
        });
    } else {
        btnStt.title = 'Web Speech API (STT) not supported in this browser.';
        sttStatus.textContent = 'STT Not Supported';
    }

    function stopSTT() {
        isListening = false;
        btnStt.classList.remove('listening');
        sttStatus.classList.remove('listening');
        sttStatus.innerHTML = '<i class="fa-solid fa-microphone"></i> Mic Ready';
    }

    // Web Speech API - Text-to-Speech (TTS) Setup
    btnTts.addEventListener('click', () => {
        if (!currentResponseText) return;
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // Stop any ongoing speech
            const utterance = new SpeechSynthesisUtterance(currentResponseText);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        } else {
            alert('Text-to-Speech is not supported in your browser.');
        }
    });

    // Query Submission
    btnSubmit?.addEventListener('click', handleQuerySubmit);
    btnClear?.addEventListener('click', () => {
        queryInput.value = '';
        outputSection.classList.add('hidden');
        resetTimeline();
    });

    async function handleQuerySubmit() {
        const query = queryInput.value.strip ? queryInput.value.strip() : queryInput.value.trim();
        if (!query) {
            alert('Please enter a query.');
            return;
        }

        const domainFilter = document.getElementById('domain-filter-select')?.value || 'all';

        outputSection.classList.remove('hidden');
        responseTextBody.textContent = 'Executing 5-Agent Pipeline...';
        citationsContainer.innerHTML = '';

        animateTimeline();

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: query,
                    session_id: 'web_session_01',
                    domain_filter: domainFilter
                })
            });

            const data = await res.json();
            if (res.ok && data.status === 'success') {
                const payload = data.data;
                currentResponseText = payload.response_text;

                responseTextBody.textContent = payload.response_text;
                
                // M2 Badge Updates
                const qTypeBadge = document.getElementById('query-type-badge');
                const routeBadge = document.getElementById('routing-path-badge');
                const confLevelBadge = document.getElementById('confidence-level-badge');
                
                if (qTypeBadge) {
                    qTypeBadge.innerHTML = `<i class="fa-solid fa-tag"></i> Type: ${(payload.query_type || 'Factual').toUpperCase()}`;
                    qTypeBadge.className = 'badge badge-primary';
                }
                if (routeBadge) {
                    const routeName = payload.routing_path === 'clarification_flow' ? 'Clarification Flow' : 'Retrieval Flow';
                    routeBadge.innerHTML = `<i class="fa-solid fa-route"></i> Route: ${routeName}`;
                    routeBadge.className = payload.routing_path === 'clarification_flow' ? 'badge badge-warning' : 'badge badge-info';
                }
                if (confLevelBadge) {
                    const levelStr = payload.confidence_level || 'HIGH CONFIDENCE';
                    confLevelBadge.innerHTML = `<i class="fa-solid fa-shield"></i> ${levelStr} (${(payload.confidence_score * 100).toFixed(1)}%)`;
                    if (levelStr.includes('HIGH')) confLevelBadge.className = 'badge badge-success';
                    else if (levelStr.includes('MEDIUM')) confLevelBadge.className = 'badge badge-warning';
                    else confLevelBadge.className = 'badge badge-danger';
                } else {
                    confidenceBadge.className = 'badge badge-danger';
                }

                // Render Citations
                if (payload.citations && payload.citations.length > 0) {
                    citationsContainer.innerHTML = payload.citations.map(c => `
                        <div class="citation-pill">
                            <span class="cite-num">${c.citation_id}</span>
                            <strong>${escapeHtml(c.source_document)}</strong>
                            <div style="font-size:0.75rem; color:#94a3b8; margin-top:4px;">
                                Section/Page: ${c.page_or_row} | Similarity: ${(c.similarity_score * 100).toFixed(1)}%
                            </div>
                        </div>
                    `).join('');
                } else {
                    citationsContainer.innerHTML = '<span style="font-size:0.85rem; color:#94a3b8;">No direct citations (General or Clarification Prompt).</span>';
                }

                completeTimeline(payload.agent_execution_log);
            } else {
                responseTextBody.textContent = `Error: ${data.detail || 'Failed to process query.'}`;
            }
        } catch (err) {
            responseTextBody.textContent = `Error executing query: ${err.message}`;
        }
    }
}

/* ==========================================================================
   5-AGENT TIMELINE ANIMATION
   ========================================================================== */
function animateTimeline() {
    const steps = ['step-qua', 'step-ret', 'step-clar', 'step-resp', 'step-mem'];
    steps.forEach((s, idx) => {
        const el = document.getElementById(s);
        if (el) {
            el.classList.add('active');
            el.classList.remove('completed');
            const dataSpan = el.querySelector('.step-data');
            if (dataSpan) dataSpan.textContent = 'Processing...';
        }
    });
}

function completeTimeline(agentLog) {
    if (!agentLog) return;
    const stepIds = ['step-qua', 'step-ret', 'step-clar', 'step-resp', 'step-mem'];
    agentLog.forEach((log, idx) => {
        if (idx < stepIds.length) {
            const el = document.getElementById(stepIds[idx]);
            if (el) {
                el.classList.add('completed');
                const dataSpan = el.querySelector('.step-data');
                if (dataSpan) dataSpan.textContent = log.details;
            }
        }
    });
}

function resetTimeline() {
    const stepIds = ['step-qua', 'step-ret', 'step-clar', 'step-resp', 'step-mem'];
    stepIds.forEach(s => {
        const el = document.getElementById(s);
        if (el) {
            el.classList.remove('active', 'completed');
            const dataSpan = el.querySelector('.step-data');
            if (dataSpan) dataSpan.textContent = 'Status: Idle';
        }
    });
}

/* ==========================================================================
   5. RETRIEVAL EVALUATION MODULE
   ========================================================================== */
function initEvaluationModule() {
    const btnRunEval = document.getElementById('btn-run-eval');
    const tbody = document.getElementById('eval-table-body');

    btnRunEval?.addEventListener('click', async () => {
        btnRunEval.disabled = true;
        btnRunEval.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Evaluation Benchmark...';
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Executing evaluation queries across Healthcare & Finance domains...</td></tr>';

        try {
            const res = await fetch('/api/evaluate', { method: 'POST' });
            const data = await res.json();
            if (res.ok && data.status === 'success') {
                const evalData = data.evaluation;

                // Update Metric Gauges
                updateMetric('val-top1', 'bar-top1', evalData.top_1_accuracy_percent);
                updateMetric('val-top3', 'bar-top3', evalData.top_3_accuracy_percent);
                updateMetric('val-top5', 'bar-top5', evalData.top_5_accuracy_percent);
                updateMetric('val-rejection', 'bar-rejection', evalData.rejection_accuracy_percent);

                // Update Table
                if (evalData.query_results && evalData.query_results.length > 0) {
                    tbody.innerHTML = evalData.query_results.map(r => `
                        <tr>
                            <td><code>${r.query_id}</code></td>
                            <td><span class="badge badge-info">${escapeHtml(r.domain || 'General')}</span></td>
                            <td><span class="badge badge-primary">${escapeHtml(r.type)}</span></td>
                            <td>${escapeHtml(r.query)}</td>
                            <td><strong>${r.hit_rank || 'N/A'}</strong></td>
                            <td>${r.top_score ? (r.top_score * 100).toFixed(1) + '%' : '--'}</td>
                            <td>
                                <span class="badge ${r.status.includes('PASS') ? 'badge-success' : 'badge-danger'}">
                                    ${r.status}
                                </span>
                            </td>
                        </tr>
                    `).join('');
                }
            } else {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">${data.detail || 'Evaluation failed.'}</td></tr>`;
            }
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Error: ${err.message}</td></tr>`;
        } finally {
            btnRunEval.disabled = false;
            btnRunEval.innerHTML = '<i class="fa-solid fa-vial-circle-check"></i> Run Retrieval Evaluation Suite';
        }
    });
}

function updateMetric(valId, barId, percent) {
    const valEl = document.getElementById(valId);
    const barEl = document.getElementById(barId);
    if (valEl) valEl.textContent = `${percent}%`;
    if (barEl) barEl.style.width = `${percent}%`;
}

function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
