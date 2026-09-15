from typing import Dict, Any, List, Optional
from src.vectorstore.chroma_indexer import VectorStoreManager

class RetrievalAgent:
    """
    Agent 2: Retrieval Agent (M2.2)
    Performs semantic vector search, ranks retrieved document chunks by relevance score,
    applies configurable low-confidence filtering, and preserves rich document metadata.
    """
    def __init__(self, vector_store: VectorStoreManager, min_relevance_threshold: float = 0.30):
        self.vector_store = vector_store
        self.min_relevance_threshold = min_relevance_threshold

    def process(
        self, 
        query_analysis: Dict[str, Any], 
        top_k: int = 5, 
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        
        user_query = query_analysis.get("original_query", "")
        query_type = query_analysis.get("query_type", "factual")
        routing_path = query_analysis.get("routing_path", "retrieval_flow")
        subqueries = query_analysis.get("expanded_subqueries", [user_query])
        
        # If routed to clarification flow directly, bypass vector search
        if routing_path == "clarification_flow":
            return {
                "agent_name": "Retrieval Agent",
                "query_type": query_type,
                "top_k_chunks": [],
                "filtered_chunks": [],
                "max_similarity_score": 0.0,
                "total_retrieved": 0,
                "status": "bypassed_for_clarification"
            }
            
        all_retrieved: Dict[str, Dict[str, Any]] = {}
        
        for sq in subqueries:
            results = self.vector_store.search(sq, top_k=top_k, domain_filter=domain_filter)
            for res in results:
                cid = res["chunk_id"]
                score = res["similarity_score"]
                if cid not in all_retrieved or score > all_retrieved[cid]["similarity_score"]:
                    all_retrieved[cid] = res
                    
        # Sort aggregated results descending by relevance score
        sorted_results = sorted(all_retrieved.values(), key=lambda x: x["similarity_score"], reverse=True)
        
        # Apply Low-Confidence Relevance Filtering (M2.2)
        filtered_chunks = []
        rejected_chunks = []
        
        for chunk in sorted_results:
            score = chunk.get("similarity_score", 0.0)
            if score >= self.min_relevance_threshold:
                filtered_chunks.append(chunk)
            else:
                rejected_chunks.append(chunk)
                
        top_chunks = filtered_chunks[:top_k]
        max_score = top_chunks[0]["similarity_score"] if top_chunks else 0.0
        
        return {
            "agent_name": "Retrieval Agent",
            "query_type": query_type,
            "top_k_chunks": top_chunks,
            "total_retrieved": len(top_chunks),
            "max_similarity_score": max_score,
            "min_relevance_threshold": self.min_relevance_threshold,
            "rejected_low_confidence_count": len(rejected_chunks),
            "status": "completed" if top_chunks else "no_relevant_chunks_found"
        }
