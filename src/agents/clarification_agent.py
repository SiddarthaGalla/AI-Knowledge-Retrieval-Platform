from typing import Dict, Any

class ClarificationAgent:
    """
    Agent 3: Clarification Agent
    Evaluates retrieval similarity scores against confidence thresholds (<0.65).
    Triggers clarification questions or out-of-bounds fallback notices.
    """
    def __init__(self, confidence_threshold: float = 0.65):
        self.confidence_threshold = confidence_threshold

    def process(
        self, 
        query_analysis: Dict[str, Any], 
        retrieval_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        intent = query_analysis.get("intent", "fact_retrieval")
        max_score = retrieval_output.get("max_similarity_score", 0.0)
        chunks = retrieval_output.get("top_k_chunks", [])
        
        # Out of bounds check
        if intent == "out_of_bounds":
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "out_of_bounds",
                "message": "The query falls outside the knowledge base scope. Please ask a question related to uploaded document policies.",
                "status": "triggered"
            }
            
        # Low confidence check (< 0.65)
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
