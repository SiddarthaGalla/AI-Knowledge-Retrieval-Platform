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

def create_m3_speaker_notes():
    doc = docx.Document()
    
    # Page Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("MILESTONE 3 PRESENTATION & DEMO SPEAKER NOTES")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(30, 58, 138)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run("AI-Based Knowledge Retrieval Platform | Clarification, Memory, Voice & Transparency")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(37, 99, 235)
    
    doc.add_paragraph() # Spacer
    
    # QUICK START BOX
    table_qs = doc.add_table(rows=1, cols=1)
    table_qs.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_qs = table_qs.cell(0, 0)
    set_cell_background(cell_qs, "EFF6FF")
    
    p_qs = cell_qs.paragraphs[0]
    r_qs_bold = p_qs.add_run("🚀 HOW TO RUN THE PLATFORM FOR YOUR MILESTONE 3 DEMO:\n")
    r_qs_bold.font.bold = True
    r_qs_bold.font.color.rgb = RGBColor(30, 58, 138)
    r_qs_text = p_qs.add_run(
        "1. Open Terminal in project directory (s:\\Personal\\My Projects\\AI-Knowledge-Retrieval-Platform).\n"
        "2. Run command: python main.py\n"
        "3. Open your browser and go to: http://localhost:8000"
    )
    r_qs_text.font.size = Pt(10.5)
    
    doc.add_paragraph()

    # SECTION 1: OVERVIEW OF MILESTONE 3
    h1 = doc.add_heading(level=1)
    r1 = h1.add_run("1. Simple Overview of Milestone 3 (What We Built)")
    r1.font.color.rgb = RGBColor(30, 58, 138)
    
    points = [
        ("M3.1 Clarification Agent: ", "Detects multi-part queries and ambiguous questions, generates targeted follow-up prompts, and combines user responses into refined queries (/api/query/refine)."),
        ("M3.2 Conversation Memory Agent: ", "Tracks multi-turn conversation context, remembers referenced entities and documents, and resolves coreference pronouns ('it', 'its', 'that policy') automatically."),
        ("M3.3 Voice Interaction Module: ", "Integrated Web Speech API Speech-to-Text (STT microphone recording controls) and Text-to-Speech (TTS playback controls: Play, Pause, Resume, Stop)."),
        ("M3.4 Response Transparency Panel: ", "Expandable UI accordion beneath answers displaying retrieved document chunks, similarity percentage meters, document section metadata, and citation mappings.")
    ]
    
    for b_title, b_desc in points:
        bp = doc.add_paragraph(style='List Bullet')
        r_bt = bp.add_run(b_title)
        r_bt.font.bold = True
        r_bt.font.color.rgb = RGBColor(37, 99, 235)
        bp.add_run(b_desc)

    doc.add_paragraph()

    # SECTION 2: DEMO EXAMPLES FOR THE WEBSITE
    h2 = doc.add_heading(level=1)
    r2 = h2.add_run("2. Website Demo Queries (What to Type/Speak in the Web UI)")
    r2.font.color.rgb = RGBColor(30, 58, 138)

    demo_queries = [
        {
            "num": "1",
            "type": "MULTI-TURN COREFERENCE RESOLUTION DEMO (M3.2)",
            "turn1": "Turn 1: 'Tell me about Plan A medical coverage'",
            "turn2": "Turn 2: 'What is its deductible?'",
            "result": "System resolves 'its' to 'Plan A medical coverage' and retrieves the $500 deductible.",
            "notes": "Demonstrates Agent 5 coreference resolution across conversation turns."
        },
        {
            "num": "2",
            "type": "MULTI-PART & CLARIFICATION REFINEMENT DEMO (M3.1)",
            "turn1": "Initial Query: 'how much?'",
            "turn2": "Clarification Input: 'lodging reimbursement limit'",
            "result": "Refines query to 'how much? - lodging reimbursement limit' and returns $250 lodging allowance.",
            "notes": "Demonstrates Agent 3 clarification feedback loop."
        },
        {
            "num": "3",
            "type": "RESPONSE TRANSPARENCY PANEL DEMO (M3.4)",
            "turn1": "Query: 'What is the daily per diem meal allowance?'",
            "turn2": "Action: Click 'Inspect Evidence & Source Transparency Panel' accordion.",
            "result": "Expands retrieved chunk details showing 84.6% relevance meter, corporate_financial_policy.csv, Row 2, Section 1, and exact chunk text.",
            "notes": "Demonstrates evidence transparency and relevance meter display."
        },
        {
            "num": "4",
            "type": "VOICE STT & TTS DEMO (M3.3)",
            "turn1": "Action 1: Click Microphone icon -> Speak 'What are the steps to submit a claim?'",
            "turn2": "Action 2: Click 'Play Voice' button.",
            "result": "Transcribes voice query in real time and speaks synthesized answer out loud with Play/Pause/Stop controls.",
            "notes": "Demonstrates Web Speech STT & TTS integration."
        }
    ]

    for dq in demo_queries:
        table_d = doc.add_table(rows=4, cols=2)
        table_d.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        cell_hdr = table_d.cell(0, 0)
        cell_hdr.merge(table_d.cell(0, 1))
        set_cell_background(cell_hdr, "1E3A8A")
        p_hdr = cell_hdr.paragraphs[0]
        r_hdr = p_hdr.add_run(f"EXAMPLE {dq['num']}: {dq['type']}")
        r_hdr.font.bold = True
        r_hdr.font.color.rgb = RGBColor(255, 255, 255)
        
        table_d.cell(1, 0).paragraphs[0].add_run("Step 1:").font.bold = True
        table_d.cell(1, 1).paragraphs[0].add_run(dq["turn1"]).font.color.rgb = RGBColor(37, 99, 235)
        
        table_d.cell(2, 0).paragraphs[0].add_run("Step 2:").font.bold = True
        table_d.cell(2, 1).paragraphs[0].add_run(dq["turn2"])
        
        table_d.cell(3, 0).paragraphs[0].add_run("Result & Feature:").font.bold = True
        table_d.cell(3, 1).paragraphs[0].add_run(f"{dq['result']} ({dq['notes']})")
        
        doc.add_paragraph()

    # SECTION 3: WORD-FOR-WORD SCRIPT
    h3 = doc.add_heading(level=1)
    r3 = h3.add_run("3. Word-for-Word Live Demo Presentation Script")
    r3.font.color.rgb = RGBColor(30, 58, 138)

    p_script_box = doc.add_table(rows=1, cols=1).cell(0, 0)
    set_cell_background(p_script_box, "F8FAFC")
    p_s = p_script_box.paragraphs[0]
    
    script_text = (
        "\"Good morning / afternoon evaluators. Today I am presenting the final completed Milestone 3 of our AI-Based Knowledge Retrieval Platform.\n\n"
        "Milestone 3 brings full conversational intelligence, speech interaction, and complete response transparency to our platform:\n\n"
        "1. First, let's look at Multi-Turn Conversation Memory. If I ask 'Tell me about Plan A medical coverage' in Turn 1, and then follow up in Turn 2 with 'What is its deductible?', our Memory Agent resolves the pronoun 'its' to 'Plan A medical coverage' and returns the exact $500 deductible.\n\n"
        "2. Second, our Clarification Agent handles underspecified queries. If I ask 'how much?', the system triggers a Clarification Bar with suggested questions. Typing 'lodging limit' refines the query and returns the $250 allowance.\n\n"
        "3. Third, our Web Speech API integration allows hands-free voice input and output. I can click the microphone to speak my question, and click 'Play Voice' to listen to the synthesized answer with Play, Pause, and Stop controls.\n\n"
        "4. Finally, our Response Transparency Panel allows users to inspect the exact retrieved evidence chunks, relevance percentage meters, document name, section, and page numbers supporting the answer.\n\n"
        "All Milestone 3 unit tests and end-to-end multi-turn pipeline benchmarks have passed with 100% test success. Thank you!\""
    )
    p_s.add_run(script_text).font.size = Pt(10.5)

    doc_path = "s:/Personal/My Projects/AI-Knowledge-Retrieval-Platform/Milestone_3_Presentation_Speaker_Notes.docx"
    doc.save(doc_path)
    print(f"Successfully created {doc_path}")

if __name__ == "__main__":
    create_m3_speaker_notes()
