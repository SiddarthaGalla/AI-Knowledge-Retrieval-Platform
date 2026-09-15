import re
from typing import Dict, Any, List

class QueryUnderstandingAgent:
    """
    Agent 1: Query Understanding Agent (M2.1)
    Analyzes incoming user queries, classifies intent into factual, procedural, 
    comparative, or ambiguous categories, computes classification confidence, 
    and generates structured routing payloads.
    """
    
    def process(self, user_query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        cleaned_query = user_query.strip()
        
        classification = self._classify_query(cleaned_query)
        entities = self._extract_entities(cleaned_query)
        keywords = self._extract_keywords(cleaned_query)
        expanded_subqueries = self._generate_subqueries(cleaned_query, classification["query_type"], entities)
        
        return {
            "agent_name": "Query Understanding Agent",
            "original_query": cleaned_query,
            "query_type": classification["query_type"],
            "classification_confidence": classification["confidence"],
            "routing_path": classification["routing_path"],
            "routing_reason": classification["reason"],
            "extracted_entities": entities,
            "keywords": keywords,
            "expanded_subqueries": expanded_subqueries,
            "status": "completed"
        }

    def _classify_query(self, query: str) -> Dict[str, Any]:
        q_lower = query.lower()
        words = [w for w in re.sub(r"[^\w\s]", "", q_lower).split() if len(w) > 1]
        
        # 1. Out-of-bounds check
        out_of_bounds_keywords = ["weather", "movie", "recipe", "game score", "celebrity", "joke", "sports", "football"]
        if any(kw in q_lower for kw in out_of_bounds_keywords):
            return {
                "query_type": "out_of_bounds",
                "confidence": 0.95,
                "routing_path": "clarification_flow",
                "reason": "Query asks about external topics outside knowledge base scope."
            }

        # 2. Ambiguous query check (very short or missing core noun/verb context)
        # e.g. "how much?", "claim", "details", "policy", "what about it"
        ambiguous_triggers = ["how much", "details", "policy", "claim", "status", "info", "what about it", "help"]
        if len(words) <= 2 or q_lower in ambiguous_triggers:
            # Check if query lacks specific entity context
            return {
                "query_type": "ambiguous",
                "confidence": 0.85,
                "routing_path": "clarification_flow",
                "reason": "Query is underspecified or lacks essential entity context."
            }

        # 3. Comparative query check
        comparative_indicators = ["compare", "vs", "versus", "difference between", "distinguish", "plan a vs plan b", "better than"]
        if any(ind in q_lower for ind in comparative_indicators):
            return {
                "query_type": "comparative",
                "confidence": 0.90,
                "routing_path": "retrieval_flow",
                "reason": "Query requests comparison between two or more items/sections."
            }

        # 4. Procedural query check
        procedural_indicators = ["how to", "steps", "procedure", "process", "workflow", "submit", "how do i", "instructions"]
        if any(ind in q_lower for ind in procedural_indicators):
            return {
                "query_type": "procedural",
                "confidence": 0.92,
                "routing_path": "retrieval_flow",
                "reason": "Query requests step-by-step instructions or operational procedure."
            }

        # 5. Default Factual query
        return {
            "query_type": "factual",
            "confidence": 0.88,
            "routing_path": "retrieval_flow",
            "reason": "Query requests direct factual lookup of specific rules or values."
        }

    def _extract_entities(self, query: str) -> List[str]:
        words = query.split()
        entities = []
        stop_words = {"what", "when", "where", "which", "how", "does", "that", "this", "have", "with", "from", "for", "the", "and", "are"}
        for word in words:
            cleaned = re.sub(r"[^\w\s]", "", word)
            if len(cleaned) > 3 and cleaned.lower() not in stop_words:
                entities.append(cleaned)
        return list(set(entities))

    def _extract_keywords(self, query: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", query.lower())
        stop_words = {"what", "is", "the", "for", "to", "are", "a", "an", "in", "of", "and", "or", "how", "do", "i", "does"}
        return [w for w in cleaned.split() if len(w) > 2 and w not in stop_words]

    def _generate_subqueries(self, query: str, query_type: str, entities: List[str]) -> List[str]:
        subqueries = [query]
        
        if entities:
            subqueries.append(" ".join(entities))
            
        q_lower = query.lower()
        if "coverage" in q_lower or "medical" in q_lower or "health" in q_lower:
            subqueries.append(f"{query} policy health insurance waiting period eligible")
        elif "reimbursement" in q_lower or "expense" in q_lower or "lodging" in q_lower:
            subqueries.append(f"{query} per diem travel allowance limit claim receipt")
            
        return list(dict.fromkeys(subqueries))
