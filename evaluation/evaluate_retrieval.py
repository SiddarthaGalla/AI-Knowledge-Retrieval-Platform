import os
import sys
import json
import uuid
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any, List
from src.ingestion.document_parsers import DocumentParser
from src.ingestion.chunker import RecursiveChunker
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.pipeline.rag_pipeline import RAGPipelineOrchestrator

logger = logging.getLogger(__name__)

class RAGEvaluationRunner:
    """
    RAG Retrieval Validation & Accuracy Benchmark Suite (M1.4).
    Evaluates Top-1, Top-3, Top-5 Accuracy, Context Recall, and False Retrieval Rate.
    """
    def __init__(self, vector_store: VectorStoreManager = None):
        self.vector_store = vector_store or VectorStoreManager(persist_directory="./data/vector_store_eval")
        self.chunker = RecursiveChunker(chunk_size=500, chunk_overlap=100)
        self.pipeline = RAGPipelineOrchestrator(self.vector_store)

    def prepare_sample_datasets(self):
        """
        Ingests default sample datasets for Healthcare and Finance domains.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Domain A: Healthcare
        hc_path = os.path.join(base_dir, "data", "domain_a_healthcare", "healthcare_policy.txt")
        if os.path.exists(hc_path):
            blocks, doc_meta = DocumentParser.parse_file(hc_path, domain="Healthcare")
            doc_id = "doc_eval_healthcare_01"
            doc_meta["document_id"] = doc_id
            chunks = self.chunker.chunk_document(blocks, doc_id, doc_meta)
            self.vector_store.add_document_and_chunks(doc_meta, chunks)

        # Domain B: Finance
        fin_path = os.path.join(base_dir, "data", "domain_b_finance", "corporate_financial_policy.csv")
        if os.path.exists(fin_path):
            blocks, doc_meta = DocumentParser.parse_file(fin_path, domain="Finance")
            doc_id = "doc_eval_finance_01"
            doc_meta["document_id"] = doc_id
            chunks = self.chunker.chunk_document(blocks, doc_id, doc_meta)
            self.vector_store.add_document_and_chunks(doc_meta, chunks)

    def run_evaluation(self) -> Dict[str, Any]:
        self.prepare_sample_datasets()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        hc_queries_path = os.path.join(base_dir, "evaluation", "test_queries_domain_a.json")
        fin_queries_path = os.path.join(base_dir, "evaluation", "test_queries_domain_b.json")
        
        queries = []
        if os.path.exists(hc_queries_path):
            with open(hc_queries_path, "r") as f:
                queries.extend(json.load(f))
                
        if os.path.exists(fin_queries_path):
            with open(fin_queries_path, "r") as f:
                queries.extend(json.load(f))
                
        total_queries = len(queries)
        if total_queries == 0:
            return {"error": "No evaluation queries found."}
            
        top1_hits = 0
        top3_hits = 0
        top5_hits = 0
        unavailable_correct = 0
        unavailable_total = 0
        
        results_by_query = []
        
        for item in queries:
            q_id = item["id"]
            q_text = item["query"]
            q_type = item["type"]
            expected = item.get("expected_keywords", [])
            target_domain = item.get("target_domain")
            
            # Run pipeline
            pipeline_res = self.pipeline.run_query(q_text, domain_filter=target_domain)
            retrieved_chunks = pipeline_res.get("retrieved_chunks", [])
            clarification_required = pipeline_res.get("clarification_required", False)
            
            if q_type == "Unavailable":
                unavailable_total += 1
                # Should correctly trigger clarification or low confidence
                if clarification_required or pipeline_res["confidence_score"] < 0.65:
                    unavailable_correct += 1
                    status = "PASS (Correctly Rejected)"
                else:
                    status = "FAIL (False Positive Retrieval)"
                    
                results_by_query.append({
                    "query_id": q_id,
                    "query": q_text,
                    "type": q_type,
                    "domain": target_domain,
                    "status": status,
                    "confidence_score": pipeline_res["confidence_score"]
                })
                continue
                
            # Check presence of expected keywords in top K chunks
            hit_rank = 0
            for rank_idx, chunk in enumerate(retrieved_chunks, start=1):
                chunk_text = chunk["content"].lower()
                if any(kw.lower() in chunk_text for kw in expected):
                    hit_rank = rank_idx
                    break
                    
            if hit_rank == 1:
                top1_hits += 1
            if 1 <= hit_rank <= 3:
                top3_hits += 1
            if 1 <= hit_rank <= 5:
                top5_hits += 1
                
            results_by_query.append({
                "query_id": q_id,
                "query": q_text,
                "type": q_type,
                "domain": target_domain,
                "hit_rank": hit_rank if hit_rank > 0 else "Miss",
                "top_score": pipeline_res["confidence_score"],
                "status": "PASS" if hit_rank > 0 else "FAIL"
            })
            
        valid_query_count = total_queries - unavailable_total
        top1_acc = round((top1_hits / valid_query_count * 100), 2) if valid_query_count > 0 else 0.0
        top3_acc = round((top3_hits / valid_query_count * 100), 2) if valid_query_count > 0 else 0.0
        top5_acc = round((top5_hits / valid_query_count * 100), 2) if valid_query_count > 0 else 0.0
        false_retrieval_rate = round(((unavailable_total - unavailable_correct) / unavailable_total * 100), 2) if unavailable_total > 0 else 0.0
        
        summary = {
            "total_evaluated_queries": total_queries,
            "domain_a_queries": sum(1 for q in queries if q.get("target_domain") == "Healthcare"),
            "domain_b_queries": sum(1 for q in queries if q.get("target_domain") == "Finance"),
            "top_1_accuracy_percent": top1_acc,
            "top_3_accuracy_percent": top3_acc,
            "top_5_accuracy_percent": top5_acc,
            "false_retrieval_rate_percent": false_retrieval_rate,
            "rejection_accuracy_percent": 100.0 - false_retrieval_rate,
            "query_results": results_by_query
        }
        
        return summary

if __name__ == "__main__":
    runner = RAGEvaluationRunner()
    res = runner.run_evaluation()
    print(json.dumps(res, indent=2))
