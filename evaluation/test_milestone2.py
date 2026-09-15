import os
import sys
import json
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion.document_parsers import DocumentParser
from src.ingestion.chunker import RecursiveChunker
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.agents.query_understanding_agent import QueryUnderstandingAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.response_generation_agent import ResponseGenerationAgent
from src.pipeline.rag_pipeline import RAGPipelineOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_milestone2")

def test_milestone2_suite():
    logger.info("=== STARTING MILESTONE 2 VERIFICATION SUITE ===")
    
    # Setup clean vector store
    store_path = "./data/vector_store_m2_test"
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
        meta["document_id"] = "doc_hc_m2"
        chunks = chunker.chunk_document(blocks, meta["document_id"], meta)
        vector_store.add_document_and_chunks(meta, chunks)

    if os.path.exists(fin_path):
        blocks, meta = DocumentParser.parse_file(fin_path, domain="Finance")
        meta["document_id"] = "doc_fin_m2"
        chunks = chunker.chunk_document(blocks, meta["document_id"], meta)
        vector_store.add_document_and_chunks(meta, chunks)

    pipeline = RAGPipelineOrchestrator(vector_store)
    
    # -------------------------------------------------------------------------
    # TEST 1: M2.1 Query Understanding Classification
    # -------------------------------------------------------------------------
    logger.info("--- TEST 1: M2.1 Query Understanding Agent Classification ---")
    qua = QueryUnderstandingAgent()
    
    q_factual = "What is the deductible for Plan A?"
    res_f = qua.process(q_factual)
    assert res_f["query_type"] == "factual", f"Expected factual, got {res_f['query_type']}"
    assert res_f["routing_path"] == "retrieval_flow"
    
    q_proc = "What are the steps to submit an out of network claim?"
    res_p = qua.process(q_proc)
    assert res_p["query_type"] == "procedural", f"Expected procedural, got {res_p['query_type']}"
    assert res_p["routing_path"] == "retrieval_flow"
    
    q_comp = "Compare coverage for Plan A versus Plan B"
    res_c = qua.process(q_comp)
    assert res_c["query_type"] == "comparative", f"Expected comparative, got {res_c['query_type']}"
    assert res_c["routing_path"] == "retrieval_flow"

    q_ambig = "how much?"
    res_a = qua.process(q_ambig)
    assert res_a["query_type"] == "ambiguous", f"Expected ambiguous, got {res_a['query_type']}"
    assert res_a["routing_path"] == "clarification_flow"
    
    logger.info("✅ M2.1 Query Understanding Agent Classification PASSED!")

    # -------------------------------------------------------------------------
    # TEST 2: M2.2 Retrieval Agent Ranking & Low-Confidence Filtering
    # -------------------------------------------------------------------------
    logger.info("--- TEST 2: M2.2 Retrieval Agent Ranking & Low-Confidence Filtering ---")
    ret_agent = RetrievalAgent(vector_store, min_relevance_threshold=0.30)
    
    ret_output = ret_agent.process(res_f, top_k=5)
    assert len(ret_output["top_k_chunks"]) > 0
    assert ret_output["top_k_chunks"][0]["similarity_score"] >= 0.30
    
    # Check low confidence filtering with dummy query
    dummy_analysis = {
        "original_query": "xyz123 unrepresented alien spaceship",
        "query_type": "factual",
        "routing_path": "retrieval_flow",
        "expanded_subqueries": ["xyz123 unrepresented alien spaceship"]
    }
    ret_dummy = ret_agent.process(dummy_analysis, top_k=5)
    assert len(ret_dummy["top_k_chunks"]) == 0
    assert ret_dummy["status"] == "no_relevant_chunks_found"
    
    logger.info("✅ M2.2 Retrieval Agent Filtering & Ranking PASSED!")

    # -------------------------------------------------------------------------
    # TEST 3: M2.3 Response Generation & Confidence Displays
    # -------------------------------------------------------------------------
    logger.info("--- TEST 3: M2.3 Response Generation Agent & Confidence Display ---")
    resp_agent = ResponseGenerationAgent()
    
    resp_out = resp_agent.process(q_factual, res_f, ret_output, {"clarification_required": False})
    assert resp_out["grounded"] == True
    assert len(resp_out["citations"]) > 0
    assert resp_out["confidence_level"] in ["HIGH CONFIDENCE", "MEDIUM CONFIDENCE", "LOW CONFIDENCE"]
    
    logger.info("✅ M2.3 Response Generation Agent PASSED!")

    # -------------------------------------------------------------------------
    # TEST 4: M2.4 End-to-End Orchestration Execution
    # -------------------------------------------------------------------------
    logger.info("--- TEST 4: M2.4 End-to-End Pipeline Orchestration ---")
    
    e2e_factual = pipeline.run_query("What is the daily per diem meal allowance?")
    logger.info(f"Factual query output: type={e2e_factual['query_type']}, confidence_level={e2e_factual['confidence_level']}, score={e2e_factual['confidence_score']}, clarification_req={e2e_factual['clarification_required']}")
    logger.info(f"Retrieved chunks count: {len(e2e_factual['retrieved_chunks'])}")
    assert len(e2e_factual["citations"]) > 0

    e2e_procedural = pipeline.run_query("What are the steps to submit an out of network claim?")
    assert e2e_procedural["query_type"] == "procedural"
    assert "1." in e2e_procedural["response_text"] or "Procedural Steps" in e2e_procedural["response_text"]

    e2e_comparative = pipeline.run_query("Compare Plan A vs Plan B coverage")
    assert e2e_comparative["query_type"] == "comparative"
    assert "Comparative Overview" in e2e_comparative["response_text"]

    e2e_ambiguous = pipeline.run_query("how much?")
    assert e2e_ambiguous["query_type"] == "ambiguous"
    assert e2e_ambiguous["clarification_required"] == True

    logger.info("✅ M2.4 End-to-End Pipeline Orchestration PASSED!")
    logger.info("=== ALL MILESTONE 2 TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    test_milestone2_suite()
