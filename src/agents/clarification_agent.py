from typing import Dict, Any

class ClarificationAgent:
    """
    Agent 3: Clarification Agent
    Evaluates retrieval similarity scores against confidence thresholds (<0.30).
    Triggers clarification questions or out-of-bounds fallback notices.
    """
    def __init__(self, confidence_threshold: float = 0.30):
        self.confidence_threshold = confidence_threshold

    def process(
        self, 
        query_analysis: Dict[str, Any], 
        retrieval_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        query_type = query_analysis.get("query_type") or query_analysis.get("intent") or "factual"
        max_score = retrieval_output.get("max_similarity_score", 0.0)
        chunks = retrieval_output.get("top_k_chunks", [])
        
        # Out of bounds check
        if query_type == "out_of_bounds":
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "out_of_bounds",
                "message": "The query falls outside the knowledge base scope. Please ask a question related to uploaded document policies.",
                "status": "triggered"
            }

        # Ambiguous query check
        if query_type == "ambiguous":
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "ambiguous_query",
                "message": query_analysis.get("routing_reason") or "Your question is underspecified. Please provide additional details or entity names.",
                "status": "triggered"
            }
            
        # Low confidence check (< 0.30)
        if max_score < self.confidence_threshold or not chunks:
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "low_confidence",
                "message": f"I couldn't find a high-confidence match (Confidence: {max_score:.2f} < Threshold: {self.confidence_threshold:.2f}). Could you please clarify your question or specify the relevant policy section?",
                "status": "triggered"
            }
            
        return {
            "agent_name": "Clarification Agent",
            "clarification_required": False,
            "confidence_score": max_score,
            "reason": "sufficient_confidence",
            "message": "Confidence threshold satisfied.",
            "status": "passed"
        }
