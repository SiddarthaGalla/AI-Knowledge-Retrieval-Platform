from typing import Dict, Any, List, Optional
from src.vectorstore.chroma_indexer import VectorStoreManager

class RetrievalAgent:
    """
    Agent 2: Retrieval Agent
    Performs dense vector retrieval & hybrid matching against indexed knowledge base chunks.
    """
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store

    def process(
        self, 
        query_analysis: Dict[str, Any], 
        top_k: int = 5, 
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        subqueries = query_analysis.get("expanded_subqueries", [query_analysis.get("original_query")])
        intent = query_analysis.get("intent", "fact_retrieval")
        
        all_retrieved: Dict[str, Dict[str, Any]] = {}
        
        for sq in subqueries:
            results = self.vector_store.search(sq, top_k=top_k, domain_filter=domain_filter)
            for res in results:
                cid = res["chunk_id"]
                if cid not in all_retrieved or res["similarity_score"] > all_retrieved[cid]["similarity_score"]:
                    all_retrieved[cid] = res
                    
        # Sort aggregated results
        sorted_results = sorted(all_retrieved.values(), key=lambda x: x["similarity_score"], reverse=True)
        top_results = sorted_results[:top_k]
        
        # Calculate maximum similarity score
        max_score = top_results[0]["similarity_score"] if top_results else 0.0
        
        return {
            "agent_name": "Retrieval Agent",
            "top_k_chunks": top_results,
            "max_similarity_score": max_score,
            "total_retrieved": len(top_results),
            "status": "completed"
        }
