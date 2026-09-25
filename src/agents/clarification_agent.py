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
        
        # 1. Multi-part query check
        is_multi_part, sub_parts = self._detect_multi_part_query(user_query)
        if is_multi_part:
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "multi_part_query",
                "message": f"Your query contains multiple parts ({', '.join(sub_parts)}). Please clarify which section you would like to start with, or specify the domain.",
                "multi_parts": sub_parts,
                "status": "triggered"
            }

        # 2. Out of bounds check
        if query_type == "out_of_bounds":
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "out_of_bounds",
                "message": "The query falls outside the knowledge base scope. Please ask a question related to uploaded Healthcare or Financial document policies.",
                "status": "triggered"
            }

        # 3. Ambiguous query check
        if query_type == "ambiguous":
            suggested_questions = self._generate_targeted_suggestions(user_query)
            return {
                "agent_name": "Clarification Agent",
                "clarification_required": True,
                "confidence_score": max_score,
                "reason": "ambiguous_query",
                "message": query_analysis.get("routing_reason") or "Your question is underspecified. Please clarify the specific policy or entity you are asking about.",
                "suggested_questions": suggested_questions,
                "status": "triggered"
            }
            
        # 4. Low confidence check (< 0.30)
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
