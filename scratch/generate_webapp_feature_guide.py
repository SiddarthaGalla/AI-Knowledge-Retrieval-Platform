import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_webapp_guides():
    # -------------------------------------------------------------------------
    # 1. GENERATE TXT FILE
    # -------------------------------------------------------------------------
    txt_content = """================================================================================
WEB APPLICATION USER GUIDE & FEATURE MANUAL
AI-Based Knowledge Retrieval Platform
================================================================================

--------------------------------------------------------------------------------
🚀 SECTION 1: HOW TO LAUNCH AND OPEN THE WEB APP
--------------------------------------------------------------------------------
1. Open your terminal in the project directory:
   Path: s:\\Personal\\My Projects\\AI-Knowledge-Retrieval-Platform

2. Start the FastAPI Application Gateway Server:
   Command: python main.py

3. Open your Web Browser (Chrome, Edge, Firefox):
   URL: http://localhost:8000


================================================================================
SECTION 2: COMPLETE WALKTHROUGH OF WEB APP UI LAYOUT & FEATURES
================================================================================

🌐 FEATURE 1: NAVIGATION HEADER & PLATFORM METRICS BAR
- Brand Logo & Gateway Status: Shows "CogniRetrieve.ai" with a glowing green "Gateway Active" pulse dot.
- Top Stats Bar:
  * Ingested Documents: Shows total files loaded into the knowledge base.
  * Indexed Chunks: Shows total text chunks generated for vector search.
  * Top-3 Retrieval Accuracy: Shows platform accuracy baseline (92.3%).
  * Web Speech Status: Shows "STT & TTS Enabled".


💬 FEATURE 2: RAG & VOICE QUERY PANEL (TAB 1)
- Domain Filter Dropdown: Select to search across "All Domains", "Healthcare Domain", "Finance Domain", or "General".
- Text Query Box: Type any question into the search box and click "Submit Query".
- Voice STT (Speech-to-Text) Microphone Button:
  * Click the Microphone icon next to the textarea.
  * Speak your question into your microphone.
  * Your spoken words are automatically transcribed into text inside the box.
- 5-Agent Workflow Stepper: Real-time visual timeline showing progress as each AI agent executes:
  1. Query Understanding Agent: Classifies intent & expands search terms.
  2. Retrieval Agent: Searches vector database for matching chunks.
  3. Clarification Agent: Evaluates confidence threshold (> 0.30).
  4. Response Generation Agent: Synthesizes grounded answer with citations.
  5. Conversation Memory Agent: Logs turn history & tracks entities.
- Query Classification & Confidence Badges:
  * Query Type Badge: Displays FACTUAL, PROCEDURAL, COMPARATIVE, or AMBIGUOUS.
  * Routing Path Badge: Displays Retrieval Flow vs Clarification Flow.
  * Application Confidence Badge: Displays HIGH CONFIDENCE, MEDIUM CONFIDENCE, or LOW CONFIDENCE with percentage score.
- Synthesized Grounded Response Box: Displays clear, formatted AI response.
- Voice TTS (Text-to-Speech) Audio Toolbar:
  * Play Voice: Click to listen to the AI speak its answer out loud.
  * Pause: Click to temporarily pause speech playback.
  * Resume: Click to resume speech playback.
  * Stop: Click to stop speech playback immediately.
- Source Citation Pills: Clickable citation pills showing exact file name, page/row number, and section heading for every factual statement.


❓ FEATURE 3: CLARIFICATION FEEDBACK LOOP & REFINEMENT BOX
- How it works: Triggers automatically when an underspecified or incomplete question is asked (e.g., "how much?" or "policy").
- Suggested Question Pills: Displays clickable suggestion pills (e.g., "What is the out-of-network claim procedure?", "What is the daily lodging reimbursement limit?").
- Refinement Input Box: Type your specific clarification or click a suggestion pill -> Submits refinement -> Displays refined grounded answer.


🧠 FEATURE 4: MULTI-TURN CONVERSATION MEMORY
- How it works: Allows you to ask follow-up questions without repeating context.
- Example Usage:
  * Turn 1: Type "Tell me about Plan A medical coverage" -> Read overview.
  * Turn 2: Type "What is its deductible?" -> The web app automatically resolves "its" to "Plan A medical coverage" and returns $500 deductible.


📂 FEATURE 5: KNOWLEDGE BASE DOCUMENT INGESTION MODULE (TAB 2)
- Drag-and-Drop Dropzone: Upload any .pdf, .docx, .txt, or .csv file up to 25MB.
- Domain Selector: Tag uploaded file under Healthcare Domain, Finance Domain, or General.
- Chunk Size & Overlap Settings: Adjust target chunk size (default 500 characters) and overlap (default 100 characters).
- Process & Index Document Button: Click to start processing.
- Live Ingestion Terminal Log: Displays real-time progress (Uploading -> Parsing -> Chunking -> Indexing).
- Indexed Document Inventory Table: Displays document ID, file name, domain tag, file type, total chunks created, and a Delete Trash Button to remove files.


🔍 FEATURE 6: RESPONSE TRANSPARENCY PANEL (EVIDENCE INSPECTOR)
- How it works: Provides full visibility into the evidence used by the AI.
- Expandable Summary: Click "Inspect Evidence & Source Transparency Panel" accordion beneath any answer.
- Evidence Chunk Cards:
  * Relevance Score Meter: Visual progress bar showing relevance percentage (e.g., 84.6% relevance).
  * Document Metadata: File name, domain tag, section heading, page/row number.
  * Chunk Text Preview: Displays exact raw text snippet retrieved from the document.


📊 FEATURE 7: RETRIEVAL VALIDATION BENCHMARK DASHBOARD (TAB 3)
- Run Retrieval Evaluation Suite Button: Triggers automated accuracy testing directly inside the website.
- Metric Gauges: Progress meters for Top-1 Accuracy, Top-3 Accuracy, Top-5 Accuracy, and Rejection Accuracy.
- Benchmark Execution Table: Displays query ID, target domain, query type, hit rank, score, and pass/fail status for all 15 benchmark questions.


📐 FEATURE 8: SYSTEM ARCHITECTURE & AGENT ROLES (TAB 4)
- Flowchart Diagram: Visual layout of Web UI -> FastAPI Gateway -> 5-Agent RAG Pipeline -> Vector Store.
- Agent Cards: Detailed role cards for Query Understanding, Retrieval, Clarification, Response Generation, and Conversation Memory Agents.


================================================================================
SECTION 3: HOW TO USE EVERY FEATURE IN THE WEB APP (STEP-BY-STEP ACTIONS)
================================================================================

STEP 1: ASK A FACTUAL QUESTION
- Action: Go to "RAG & Voice Query" tab -> Type "What is the waiting period for medical coverage eligibility?" -> Click "Submit Query".
- What You See:
  * Badges: TYPE: FACTUAL | ROUTE: Retrieval Flow | HIGH CONFIDENCE (84.6%)
  * Answer: "Based on Healthcare Policy 2026: Employees become eligible for full comprehensive medical coverage after completing 30 days of continuous employment [1]."
  * Citation: Pill showing healthcare_policy.txt (Page/Row 1).

STEP 2: TEST VOICE INPUT (SPEECH-TO-TEXT / STT)
- Action: Click the Microphone icon next to query box -> Speak "What are the steps to submit an out of network claim?"
- What You See:
  * Microphone turns red and status shows "Listening... Speak now".
  * Transcribed text appears in box -> Click "Submit Query".
  * Answer: Formatted step-by-step numbered instructions (1. Itemized bill, 2. Form HC-104, 3. Receipts).

STEP 3: TEST VOICE PLAYBACK (TEXT-TO-SPEECH / TTS)
- Action: Click "Play Voice" button next to synthesized answer.
- What You See:
  * AI speaks answer out loud.
  * Toolbar expands with "Pause", "Resume", and "Stop" speech buttons.

STEP 4: INSPECT EVIDENCE TRANSPARENCY PANEL
- Action: Click "Inspect Evidence & Source Transparency Panel" accordion under answer.
- What You See:
  * Accordion expands showing 84.6% relevance meter, file name, section, page number, and chunk text box.

STEP 5: TEST MULTI-TURN CONVERSATION MEMORY
- Action:
  * Turn 1: Type "Tell me about Plan A medical coverage" -> Click Submit.
  * Turn 2: Type "What is its deductible?" -> Click Submit.
- What You See:
  * Web app automatically resolves "its" to "Plan A medical coverage" and returns $500 deductible.

STEP 6: TEST CLARIFICATION FEEDBACK LOOP
- Action: Type "how much?" in query box -> Click Submit.
- What You See:
  * Clarification Card appears displaying suggested question pills + refinement box.
  * Action: Click pill "What is the daily lodging reimbursement limit?" OR type "lodging limit" -> Click "Submit Refinement".
  * Answer: Refines query and returns $250 lodging allowance.

STEP 7: TEST OFF-TOPIC REJECTION
- Action: Type "What is the company policy for pet insurance?" -> Click Submit.
- What You See:
  * Badges: TYPE: OUT_OF_BOUNDS | ROUTE: Clarification Flow
  * Answer: "⚠️ The query falls outside the knowledge base scope. Please ask a question related to uploaded document policies."

STEP 8: UPLOAD A NEW DOCUMENT
- Action: Go to "Document Ingestion" tab -> Drag & drop a .pdf, .docx, .txt, or .csv file -> Click "Process & Index Document".
- What You See:
  * Terminal log shows Parsing -> Chunking -> Indexing.
  * File appears in Indexed Document Table.

STEP 9: RUN RETRIEVAL BENCHMARK TEST
- Action: Go to "Retrieval Validation" tab -> Click "Run Retrieval Evaluation Suite".
- What You See:
  * Progress meters update and benchmark matrix table fills with pass/fail query results.
================================================================================
"""

    txt_path = "s:/Personal/My Projects/AI-Knowledge-Retrieval-Platform/Web_App_User_Guide_and_Feature_Manual.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"Successfully generated {txt_path}")

    # -------------------------------------------------------------------------
    # 2. GENERATE DOCX FILE
    # -------------------------------------------------------------------------
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("WEB APPLICATION USER GUIDE & FEATURE MANUAL")
    r_title.font.name = "Arial"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(30, 58, 138)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("AI-Based Knowledge Retrieval Platform | Full Web App Walkthrough & Instructions")
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(37, 99, 235)

    doc.add_paragraph()

    # QUICK START BOX
    table_qs = doc.add_table(rows=1, cols=1)
    table_qs.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_qs = table_qs.cell(0, 0)
    set_cell_background(cell_qs, "EFF6FF")

    p_qs = cell_qs.paragraphs[0]
    r_qs_bold = p_qs.add_run("🚀 HOW TO LAUNCH AND OPEN THE WEB APP:\n")
    r_qs_bold.font.bold = True
    r_qs_bold.font.color.rgb = RGBColor(30, 58, 138)
    r_qs_text = p_qs.add_run(
        "1. Open Terminal in project folder: s:\\Personal\\My Projects\\AI-Knowledge-Retrieval-Platform\n"
        "2. Run command: python main.py\n"
        "3. Open Browser at: http://localhost:8000"
    )
    r_qs_text.font.size = Pt(10.5)

    doc.add_paragraph()

    # SECTION 2: WEB APP FEATURES
    h2 = doc.add_heading(level=1)
    h2.add_run("1. Complete Web App UI Features Breakdown").font.color.rgb = RGBColor(30, 58, 138)

    features = [
        ("Feature 1: RAG & Voice Query Interface", "Supports text typing, Voice STT (Speech-to-Text microphone recording), Voice TTS (Text-to-Speech playback with Play/Pause/Stop), and domain filtering."),
        ("Feature 2: Classification & Confidence Badges", "Displays query category badges (FACTUAL, PROCEDURAL, COMPARATIVE, AMBIGUOUS), Routing Path badges, and Confidence Indicator badges (HIGH, MEDIUM, LOW)."),
        ("Feature 3: Clarification Feedback & Refinement Loop", "Detects underspecified queries ('how much?'), displays clickable suggestion pills, and accepts refinement inputs via /api/query/refine."),
        ("Feature 4: Multi-Turn Conversation Memory", "Tracks session context across turns and automatically resolves coreference pronouns ('it', 'its', 'that policy') without repeating context."),
        ("Feature 5: Document Ingestion Module", "Drag-and-drop uploader for PDF, DOCX, TXT, CSV files up to 25MB with chunking size/overlap settings, live terminal logs, and deletion controls."),
        ("Feature 6: Response Transparency Panel", "Expandable evidence inspector showing relevance percentage meters, document name, section heading, page/row numbers, and chunk text."),
        ("Feature 7: Retrieval Validation Dashboard", "Triggers automated accuracy testing directly inside the website and displays Top-1/3/5 metrics and query execution matrix.")
    ]

    for title, desc in features:
        bp = doc.add_paragraph(style='List Bullet')
        r_bt = bp.add_run(f"{title}: ")
        r_bt.font.bold = True
        r_bt.font.color.rgb = RGBColor(37, 99, 235)
        bp.add_run(desc)

    doc.add_paragraph()

    # SECTION 3: STEP-BY-STEP ACTIONS IN THE WEB APP
    h3 = doc.add_heading(level=1)
    h3.add_run("2. Step-by-Step Actions to Try in the Website").font.color.rgb = RGBColor(30, 58, 138)

    steps = [
        {
            "num": "1",
            "name": "Factual Query",
            "action": 'Type "What is the waiting period for medical coverage eligibility?" in Query box -> Click Submit.',
            "result": "Badges: TYPE: FACTUAL | HIGH CONFIDENCE (84.6%). Returns 30 days eligibility answer with page citation [1] healthcare_policy.txt."
        },
        {
            "num": "2",
            "name": "Voice Input (STT)",
            "action": 'Click Microphone icon -> Speak "What are the steps to submit an out of network claim?"',
            "result": "Spoken query populates box as text -> Returns formatted step-by-step numbered instructions."
        },
        {
            "num": "3",
            "name": "Voice Playback (TTS)",
            "action": 'Click "Play Voice" button next to answer.',
            "result": "AI speaks answer out loud with Play, Pause, Resume, and Stop controls active."
        },
        {
            "num": "4",
            "name": "Inspect Transparency Panel",
            "action": 'Click "Inspect Evidence & Source Transparency Panel" accordion under answer.',
            "result": "Accordion expands showing 84.6% relevance meter, file name, section, page number, and chunk text."
        },
        {
            "num": "5",
            "name": "Multi-Turn Memory",
            "action": 'Turn 1: Type "Tell me about Plan A medical coverage"\nTurn 2: Type "What is its deductible?"',
            "result": "Web App automatically resolves 'its' to 'Plan A medical coverage' and returns $500 deductible."
        },
        {
            "num": "6",
            "name": "Clarification Loop",
            "action": 'Type "how much?" -> Click suggestion pill "What is the daily lodging reimbursement limit?"',
            "result": "Refines query and returns $250 domestic lodging limit per night."
        },
        {
            "num": "7",
            "name": "Off-Topic Rejection",
            "action": 'Type "What is the company policy for pet insurance?" -> Click Submit.',
            "result": "Badges: TYPE: OUT_OF_BOUNDS | ROUTE: Clarification Flow. Safely rejects off-topic question without making up false info."
        },
        {
            "num": "8",
            "name": "Upload Document",
            "action": 'Go to Document Ingestion tab -> Drag & drop a file -> Click "Process & Index Document".',
            "result": "Terminal log shows chunking progress -> File appears in indexed document inventory table."
        }
    ]

    for st in steps:
        table_s = doc.add_table(rows=3, cols=2)
        table_s.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        cell_h = table_s.cell(0, 0)
        cell_h.merge(table_s.cell(0, 1))
        set_cell_background(cell_h, "1E3A8A")
        p_h = cell_h.paragraphs[0]
        r_h = p_h.add_run(f"STEP {st['num']}: {st['name']}")
        r_h.font.bold = True
        r_h.font.color.rgb = RGBColor(255, 255, 255)
        
        table_s.cell(1, 0).paragraphs[0].add_run("Website Action:").font.bold = True
        table_s.cell(1, 1).paragraphs[0].add_run(st["action"]).font.color.rgb = RGBColor(37, 99, 235)
        
        table_s.cell(2, 0).paragraphs[0].add_run("Web App Output:").font.bold = True
        table_s.cell(2, 1).paragraphs[0].add_run(st["result"])
        
        doc.add_paragraph()

    docx_path = "s:/Personal/My Projects/AI-Knowledge-Retrieval-Platform/Web_App_User_Guide_and_Feature_Manual.docx"
    doc.save(docx_path)
    print(f"Successfully generated {docx_path}")

if __name__ == "__main__":
    generate_webapp_guides()
