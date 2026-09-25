import os
import sys
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.document_parsers import DocumentParser
from src.ingestion.chunker import RecursiveChunker
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.agents.clarification_agent import ClarificationAgent
from src.agents.memory_agent import ConversationMemoryAgent
from src.pipeline.rag_pipeline import RAGPipelineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_milestone3")

def test_milestone3_suite():
    logger.info("=== STARTING MILESTONE 3 VERIFICATION SUITE ===")
    
    # Setup clean vector store
    store_path = "./data/vector_store_m3_test"
    if os.path.exists(os.path.join(store_path, "vector_store_data.json")):
        os.remove(os.path.join(store_path, "vector_store_data.json"))
        
    vector_store = VectorStoreManager(persist_directory=store_path)
    chunker = RecursiveChunker(chunk_size=500, chunk_overlap=100)
    
    # Load Healthcare and Finance sample documents
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hc_path = os.path.join(base_dir, "data", "domain_a_healthcare", "healthcare_policy.txt")
    fin_path = os.path.join(base_dir, "data", "domain_b_finance", "corporate_financial_policy.csv")
    
    if os.path.exists(hc_path):
        blocks, meta = DocumentParser.parse_file(hc_path, domain="Healthcare")
        meta["document_id"] = "doc_hc_m3"
        chunks = chunker.chunk_document(blocks, meta["document_id"], meta)
        vector_store.add_document_and_chunks(meta, chunks)

    if os.path.exists(fin_path):
        blocks, meta = DocumentParser.parse_file(fin_path, domain="Finance")
        meta["document_id"] = "doc_fin_m3"
        chunks = chunker.chunk_document(blocks, meta["document_id"], meta)
        vector_store.add_document_and_chunks(meta, chunks)

    pipeline = RAGPipelineOrchestrator(vector_store)

    # -------------------------------------------------------------------------
    # TEST 1: M3.1 Multi-Part & Ambiguous Query Clarification Refinement
    # -------------------------------------------------------------------------
    logger.info("--- TEST 1: M3.1 Clarification Multi-Part & Refinement ---")
    clar_agent = ClarificationAgent()
    
    # Multi-part query test
    q_multi = "What is the deductible for Plan A and how do I submit an out of network claim?"
    analysis_multi = {"query_type": "factual", "original_query": q_multi}
    ret_dummy = {"max_similarity_score": 0.40, "top_k_chunks": [{"content": "dummy"}]}
    
    clar_res = clar_agent.process(analysis_multi, ret_dummy)
    assert clar_res["clarification_required"] == True
    assert clar_res["reason"] == "multi_part_query"
    assert len(clar_res["multi_parts"]) >= 2

    # Query refinement test
    refined = clar_agent.combine_and_refine("how much?", "lodging reimbursement limit")
    assert "how much?" in refined and "lodging reimbursement limit" in refined
    logger.info("✅ M3.1 Clarification Refinement PASSED!")

    # -------------------------------------------------------------------------
    # TEST 2: M3.2 Multi-Turn Conversation Memory Coreference Resolution
    # -------------------------------------------------------------------------
    logger.info("--- TEST 2: M3.2 Conversation Memory Coreference Resolution ---")
    session_id = "test_m3_session_01"
    
    # Turn 1: Discuss Plan A medical coverage
    turn1_res = pipeline.run_query("Tell me about Plan A medical coverage", session_id=session_id)
    assert turn1_res["query_type"] in ["factual", "comparative"]
    
    # Turn 2: Follow-up question using pronoun "its"
    turn2_query = "What is its deductible?"
    resolved_q = pipeline.memory_agent.resolve_coreference(turn2_query, session_id=session_id)
    logger.info(f"Turn 2 Coreference Resolution: '{turn2_query}' -> '{resolved_q}'")
    assert "its" not in resolved_q.lower() or "plan" in resolved_q.lower() or "coverage" in resolved_q.lower()
    
    turn2_res = pipeline.run_query(turn2_query, session_id=session_id)
    assert turn2_res["confidence_score"] >= 0.30
    assert len(turn2_res["citations"]) > 0
    
    logger.info("✅ M3.2 Conversation Memory Coreference Resolution PASSED!")

    # -------------------------------------------------------------------------
    # TEST 3: M3.4 Response Transparency Evidence Chunk Mapping
    # -------------------------------------------------------------------------
    logger.info("--- TEST 3: M3.4 Response Transparency Evidence Mapping ---")
    trans_res = pipeline.run_query("What is the daily per diem meal allowance?")
    chunks = trans_res["retrieved_chunks"]
    
    assert len(chunks) > 0
    top_chunk = chunks[0]
    assert "similarity_score" in top_chunk
    assert "metadata" in top_chunk
    assert "file_name" in top_chunk["metadata"]
    assert "page_number" in top_chunk["metadata"]
    assert "section" in top_chunk["metadata"]
    
    logger.info("✅ M3.4 Response Transparency Evidence Mapping PASSED!")
    logger.info("=== ALL MILESTONE 3 TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_milestone3_suite()
