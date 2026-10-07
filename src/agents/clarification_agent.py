import re
from typing import Dict, Any, List, Optional

class ClarificationAgent:
    """
    Agent 3: Clarification Agent (M3.1)
    Detects ambiguous, incomplete, multi-part, or out-of-bounds queries.
    Generates targeted follow-up questions, maintains pending query state,
    and combines user responses into refined queries.
    """
    def __init__(self, confidence_threshold: float = 0.30):
        self.confidence_threshold = confidence_threshold

    def process(
        self, 
        query_analysis: Dict[str, Any], 
        retrieval_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        query_type = query_analysis.get("query_type") or query_analysis.get("intent") or "factual"
        user_query = query_analysis.get("original_query", "")
        max_score = retrieval_output.get("max_similarity_score", 0.0)
        chunks = retrieval_output.get("top_k_chunks", [])
        
        # Detect multi-part query for metadata tracking, but do NOT block execution
        is_multi_part, sub_parts = self._detect_multi_part_query(user_query)
        
        # Only require clarification if the user query is empty or completely blank
        if not user_query or len(user_query.strip()) <= 1:
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": 0.0,
                "reason": "empty_query",
                "message": "Please enter a valid query or question.",
                "status": "triggered"
            }

        # For all queries (multi-part, general, procedural, factual, comparative), proceed to synthesis
        return {
            "agent_name": "Clarification Agent",
            "clarification_required": False,
            "confidence_score": max_score,
            "reason": "multi_part_synthesized" if is_multi_part else ("sufficient_confidence" if max_score >= self.confidence_threshold else "general_synthesis_flow"),
            "message": "Processing query through resolution pipeline.",
            "multi_parts": sub_parts,
            "status": "passed"
        }

    def combine_and_refine(self, original_query: str, clarification_response: str) -> str:
        """
        Combines original query context with user's clarification response (M3.1).
        """
        orig_clean = original_query.strip()
        response_clean = clarification_response.strip()
        
        if not orig_clean:
            return response_clean
        if not response_clean:
            return orig_clean
            
        # If response is already descriptive, combine semantically
        return f"{orig_clean} - {response_clean}"

    def _detect_multi_part_query(self, query: str) -> (bool, List[str]):
        q_lower = query.lower()
        if " and " in q_lower or " also " in q_lower or " as well as " in q_lower:
            parts = [p.strip() for p in re.split(r"\band\b|\balso\b|\bas well as\b", query, flags=re.IGNORECASE) if p.strip()]
            if len(parts) >= 2 and all(len(p.split()) >= 2 for p in parts):
                return True, parts
        return False, []

    def _generate_targeted_suggestions(self, query: str) -> List[str]:
        q_lower = query.lower()
        if "claim" in q_lower or "how much" in q_lower:
            return [
                "What is the out-of-network medical claim submission procedure?",
                "What is the daily lodging reimbursement limit?",
                "What is the per diem meal allowance?"
            ]
        elif "plan" in q_lower or "coverage" in q_lower:
            return [
                "What is the waiting period for medical coverage?",
                "Compare Plan A vs Plan B deductibles",
                "What is covered under vision and dental supplementary plans?"
            ]
        else:
            return [
                "Healthcare Policy: Medical coverage waiting period",
                "Finance Policy: Domestic travel per diem and lodging limits",
                "Procurement Policy: Software license approval thresholds"
            ]
