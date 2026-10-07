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
        q_clean = re.sub(r"[^\w\s]", "", q_lower).strip()
        words = [w for w in q_clean.split() if len(w) > 0]

        # 1. Ambiguous query check (extremely short or missing entity context e.g. "how much?", "help", "details")
        ambiguous_triggers = ["how much", "details", "policy", "claim", "status", "info", "what about it", "help", "how much is it"]
        if (len(words) <= 1 and q_clean not in ["hi", "hello", "hey"]) or q_clean in ambiguous_triggers or (len(words) <= 2 and any(trig == q_clean for trig in ambiguous_triggers)):
            return {
                "query_type": "ambiguous",
                "confidence": 0.85,
                "routing_path": "retrieval_flow",
                "reason": "Query is underspecified - routing through general retrieval & synthesis."
            }

        # 2. Comparative query check
        comparative_indicators = ["compare", "vs", "versus", "difference between", "distinguish", "plan a vs plan b", "better than", "pros and cons"]
        if any(ind in q_lower for ind in comparative_indicators):
            return {
                "query_type": "comparative",
                "confidence": 0.90,
                "routing_path": "retrieval_flow",
                "reason": "Query requests comparison between two or more items/sections."
            }

        # 3. Procedural query check
        procedural_indicators = ["how to", "steps", "procedure", "process", "workflow", "submit", "how do i", "instructions", "guide"]
        if any(ind in q_lower for ind in procedural_indicators):
            return {
                "query_type": "procedural",
                "confidence": 0.92,
                "routing_path": "retrieval_flow",
                "reason": "Query requests step-by-step instructions or operational procedure."
            }

        # 4. Analytical / Conceptual query check
        analytical_indicators = ["why", "explain", "describe", "impact", "cause", "reason", "purpose", "overview", "summary"]
        if any(ind in q_lower for ind in analytical_indicators):
            return {
                "query_type": "analytical",
                "confidence": 0.89,
                "routing_path": "retrieval_flow",
                "reason": "Query requests conceptual explanation, analysis, or overview."
            }

        # 5. Default Factual / Universal query
        return {
            "query_type": "factual",
            "confidence": 0.88,
            "routing_path": "retrieval_flow",
            "reason": "Query requests direct factual information or domain lookup."
        }

    def _extract_entities(self, query: str) -> List[str]:
        words = query.split()
        entities = []
        stop_words = {"what", "when", "where", "which", "how", "does", "that", "this", "have", "with", "from", "for", "the", "and", "are", "tell", "about", "me", "show", "give"}
        
        # Look for multi-token capitalized patterns (e.g. Plan A, Plan B)
        plan_match = re.findall(r"\bPlan\s+[A-Z0-9]+\b", query, re.IGNORECASE)
        if plan_match:
            entities.extend(plan_match)
            
        for word in words:
            cleaned = re.sub(r"[^\w\s]", "", word)
            if len(cleaned) >= 3 and cleaned.lower() not in stop_words:
                entities.append(cleaned)
        return list(dict.fromkeys(entities))  # preserve order & unique


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
