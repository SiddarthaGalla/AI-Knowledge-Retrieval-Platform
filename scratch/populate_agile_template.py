import xlwt

def create_agile_template():
    wb = xlwt.Workbook(encoding='utf-8')
    
    # -------------------------------------------------------------------------
    # Sheet 1: Product Backlog
    # -------------------------------------------------------------------------
    ws_product = wb.add_sheet('Product Backlog')
    headers_pb = ['Planned Sprint', 'Actual Sprint', 'US ID', 'User Story Description', 'MOSCOW', 'Dependency', 'Assignee', 'Status']
    
    for c, h in enumerate(headers_pb):
        ws_product.write(0, c, h)
        
    pb_data = [
        ('Sprint 1', 'Sprint 1', 'US-001', 'Multi-format Document Extraction (.pdf, .docx, .txt, .csv)', 'Must Have', 'None', 'Siddartha Galla', 'Completed'),
        ('Sprint 1', 'Sprint 1', 'US-002', 'Recursive Text Chunker (500 char boundary, 100 overlap)', 'Must Have', 'US-001', 'Siddartha Galla', 'Completed'),
        ('Sprint 1', 'Sprint 1', 'US-003', 'Persistent Vector Store Manager with Cosine Similarity Search', 'Must Have', 'US-002', 'Siddartha Galla', 'Completed'),
        ('Sprint 2', 'Sprint 2', 'US-004', 'Query Understanding Agent Intent Classification & Routing', 'Must Have', 'US-003', 'Siddartha Galla', 'Completed'),
        ('Sprint 2', 'Sprint 2', 'US-005', 'Retrieval Agent Dense Search & Low-Confidence Filtering', 'Must Have', 'US-004', 'Siddartha Galla', 'Completed'),
        ('Sprint 2', 'Sprint 2', 'US-006', 'Response Generation Agent Grounded Answer & Citation Attachment', 'Must Have', 'US-005', 'Siddartha Galla', 'Completed'),
        ('Sprint 2', 'Sprint 2', 'US-007', 'Multi-Agent Sequential Pipeline Orchestrator', 'Must Have', 'US-006', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-008', 'Clarification Agent Ambiguity Detection & Follow-up Prompting', 'Must Have', 'US-007', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-009', 'Conversation Memory Agent Coreference Resolution Across Turns', 'Must Have', 'US-008', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-010', 'Web Speech API Speech-to-Text Recording & Text-to-Speech Playback', 'Should Have', 'US-007', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-011', 'Response Transparency Panel & Evidence Inspector Accordion', 'Must Have', 'US-006', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-012', 'Universal Query Resolution Engine for Unindexed General Questions', 'Should Have', 'US-006', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-013', 'Dynamic Enterprise Domain Synchronization & Category Selection', 'Should Have', 'US-003', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-014', 'Deterministic Cross-Process Vector Embeddings (zlib.crc32)', 'Must Have', 'US-003', 'Siddartha Galla', 'Completed'),
        ('Sprint 3', 'Sprint 3', 'US-015', 'Ultra-Premium Dark Workspace UI Design System', 'Should Have', 'US-010', 'Siddartha Galla', 'Completed')
    ]
    
    for r, row in enumerate(pb_data, start=1):
        for c, val in enumerate(row):
            ws_product.write(r, c, val)

    # -------------------------------------------------------------------------
    # Sheet 2: Stand up Meeting
    # -------------------------------------------------------------------------
    ws_standup = wb.add_sheet('Stand up Meeting')
    headers_su = ['Sprint ', 'Day', 'Impediments', 'Action Taken']
    for c, h in enumerate(headers_su):
        ws_standup.write(0, c, h)
        
    standup_data = [
        ('Sprint 1', 'Day 1 (2026-08-28)', 'PyPDF2 extraction failure on non-standard UTF-8 encoding', 'Integrated chardet encoding detector and standard fallback'),
        ('Sprint 1', 'Day 3 (2026-08-30)', 'Large CSV files creating uneven character split chunks', 'Implemented row-wise key-value text block formatter'),
        ('Sprint 1', 'Day 5 (2026-09-01)', 'In-memory vector dictionary losing data on restart', 'Built JSON disk persistence manager with atomic write'),
        ('Sprint 1', 'Day 8 (2026-09-04)', 'Zero-norm query vectors causing division by zero NaN errors', 'Added vector norm guard check in cosine similarity calculator'),
        ('Sprint 2', 'Day 2 (2026-09-12)', 'Intent classifier misidentifying comparative queries as factual', 'Added regex indicators for vs, compare, and difference between'),
        ('Sprint 2', 'Day 5 (2026-09-15)', 'Low similarity score on short query key terms', 'Implemented keyword matching score boost for exact domain terms'),
        ('Sprint 2', 'Day 9 (2026-09-19)', 'Citation tag numbering becoming mismatched on multi-chunk output', 'Unified citation map index starting from [1]'),
        ('Sprint 3', 'Day 1 (2026-09-25)', 'Non-deterministic hash seed causing similarity score drop on restart', 'Replaced Python hash() with deterministic zlib.crc32 hashing'),
        ('Sprint 3', 'Day 3 (2026-09-27)', 'Web Speech STT mic recording timing out on chrome browser', 'Added continuous speech listener event handlers'),
        ('Sprint 3', 'Day 5 (2026-09-29)', 'Coreference pronoun substitution overwriting explicit plan titles', 'Preserved multi-token capitalized entity terms in memory tracker'),
        ('Sprint 3', 'Day 8 (2026-10-02)', 'Clarification agent blocking valid general knowledge queries', 'Bypassed clarification lock for unindexed open queries'),
        ('Sprint 3', 'Day 12 (2026-10-06)', 'Domain filter dropdown restricted to Healthcare and Finance', 'Built dynamic domain sync from indexed database documents')
    ]
    
    for r, row in enumerate(standup_data, start=1):
        for c, val in enumerate(row):
            ws_standup.write(r, c, val)

    # -------------------------------------------------------------------------
    # Sheet 3: Retrospection
    # -------------------------------------------------------------------------
    ws_retro = wb.add_sheet('Retrospection')
    headers_re = ['SL #', 'Sprint #', 'Sprint start date', 'Sprint end date', 'Team member name ', 'Start Doing', 'Stop Doing ', 'Continue Doing ', 'Action taken']
    for c, h in enumerate(headers_re):
        ws_retro.write(0, c, h)
        
    retro_data = [
        (1, 1, '2026-08-28', '2026-09-10', 'Siddartha Galla', 'Automated document parsing test suite', 'Hardcoding encoding types', 'Modular text cleaner pipeline', 'Deployed Multi-Format Document Extractor'),
        (2, 2, '2026-09-11', '2026-09-24', 'Siddartha Galla', 'Retrieval accuracy validation benchmark', 'Manual intent verification', 'Sequential multi-agent routing', 'Deployed RAGEvaluationRunner with Top-1/Top-3 scoring'),
        (3, 3, '2026-09-25', '2026-10-06', 'Siddartha Galla', 'Universal query synthesis & Speech UI', 'Rejecting unindexed open questions', 'Response transparency & citation tracking', 'Deployed dynamic answer generator & ultra-premium UI')
    ]
    
    for r, row in enumerate(retro_data, start=1):
        for c, val in enumerate(row):
            ws_retro.write(r, c, val)

    # -------------------------------------------------------------------------
    # Sheet 4: Sprint Backlog
    # -------------------------------------------------------------------------
    ws_sb = wb.add_sheet('Sprint Backlog')
    headers_sb = ['US ID', 'Task ID', 'Task Description', 'Task Start Date', 'Task Completion Date', 'Team Member', 'Activity', 'Status', 'Original Estimate Effort (In Hours)', 'Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5', 'Day 6', 'Day 7', 'Day 8', 'Day 9', 'Day 10', 'Day 11', 'Day 12', 'Day 13', 'Day 14']
    for c, h in enumerate(headers_sb):
        ws_sb.write(0, c, h)
        
    sb_data = [
        ('US-001', 'TSK-001', 'Build PDF and DOCX document parsers', '2026-08-28', '2026-08-30', 'Siddartha Galla', 'Development', 'Completed', 8, 2, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-001', 'TSK-002', 'Build CSV row-wise key-value parser', '2026-08-30', '2026-08-31', 'Siddartha Galla', 'Development', 'Completed', 6, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-002', 'TSK-003', 'Implement Recursive Text Chunker (500/100)', '2026-09-01', '2026-09-03', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 0, 4, 4, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-003', 'TSK-004', 'Build VectorStoreManager with Cosine Search', '2026-09-03', '2026-09-06', 'Siddartha Galla', 'Development', 'Completed', 10, 0, 0, 0, 0, 0, 0, 3, 4, 3, 0, 0, 0, 0, 0),
        ('US-004', 'TSK-005', 'Build Query Understanding Agent & Classifier', '2026-09-11', '2026-09-13', 'Siddartha Galla', 'Development', 'Completed', 8, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-005', 'TSK-006', 'Build Retrieval Agent with Score Thresholding', '2026-09-13', '2026-09-16', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-006', 'TSK-007', 'Build Response Generation Agent with Citations', '2026-09-16', '2026-09-19', 'Siddartha Galla', 'Development', 'Completed', 10, 0, 0, 0, 0, 0, 0, 4, 3, 3, 0, 0, 0, 0, 0),
        ('US-007', 'TSK-008', 'Build RAG Pipeline Orchestration Layer', '2026-09-19', '2026-09-22', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 2, 0, 0),
        ('US-008', 'TSK-009', 'Build Clarification Agent for Ambiguous Queries', '2026-09-25', '2026-09-27', 'Siddartha Galla', 'Development', 'Completed', 8, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-009', 'TSK-010', 'Build Conversation Memory Agent & Coreference', '2026-09-27', '2026-09-29', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0),
        ('US-010', 'TSK-011', 'Integrate Web Speech STT Recording & TTS Toolbar', '2026-09-29', '2026-10-01', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 0, 0, 0, 3, 3, 2, 0, 0, 0, 0, 0),
        ('US-011', 'TSK-012', 'Build Response Transparency Evidence Inspector', '2026-10-01', '2026-10-03', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 2, 0, 0),
        ('US-014', 'TSK-013', 'Implement Deterministic zlib.crc32 Vector Embeddings', '2026-10-03', '2026-10-04', 'Siddartha Galla', 'Development', 'Completed', 6, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3),
        ('US-015', 'TSK-014', 'Design Ultra-Premium Dark Workspace Interface', '2026-10-05', '2026-10-06', 'Siddartha Galla', 'Development', 'Completed', 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4)
    ]
    
    for r, row in enumerate(sb_data, start=1):
        for c, val in enumerate(row):
            ws_sb.write(r, c, val)

    wb.save('Agile_Template_v0.1.xls')
    print("Agile_Template_v0.1.xls populated successfully.")

if __name__ == '__main__':
    create_agile_template()
