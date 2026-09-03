import re
from typing import Dict, Any, List

class QueryUnderstandingAgent:
    """
    Agent 1: Query Understanding Agent
    Analyzes user query intent, extracts entities, expands terms, and reformulates queries.
    """
    
    def process(self, user_query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        cleaned_query = user_query.strip()
        intent = self._classify_intent(cleaned_query)
        entities = self._extract_entities(cleaned_query)
        expanded_subqueries = self._generate_subqueries(cleaned_query, intent, entities)
        
        return {
            "agent_name": "Query Understanding Agent",
            "original_query": cleaned_query,
            "intent": intent,
            "entities": entities,
            "expanded_subqueries": expanded_subqueries,
            "status": "completed"
        }

    def _classify_intent(self, query: str) -> str:
        q_lower = query.lower()
        
        # Out-of-bounds check (e.g. asking about weather, sports, unrelated topics)
        out_of_bounds_keywords = ["weather", "movie", "recipe", "game score", "celebrity", "joke"]
        if any(kw in q_lower for kw in out_of_bounds_keywords):
            return "out_of_bounds"
            
        # Comparative queries
        if any(word in q_lower for word in ["compare", "vs", "versus", "difference between", "distinguish"]):
            return "comparative_analysis"
            
        # Procedural queries
        if any(word in q_lower for word in ["how to", "steps", "procedure", "process", "workflow", "submit"]):
            return "procedural_resolution"
            
        # Factual queries
        return "fact_retrieval"

    def _extract_entities(self, query: str) -> List[str]:
        # Extract capitalized phrases or key nouns
        words = query.split()
        entities = []
        for word in words:
            cleaned = re.sub(r"[^\w\s]", "", word)
            if len(cleaned) > 3 and cleaned.lower() not in ["what", "when", "where", "which", "how", "does", "that", "this", "have", "with"]:
                entities.append(cleaned)
        return list(set(entities))

    def _generate_subqueries(self, query: str, intent: str, entities: List[str]) -> List[str]:
        subqueries = [query]
        
        # Add entity focused subqueries
        if entities:
            subqueries.append(" ".join(entities))
            
        # Add synonym / domain expansion terms
        if "coverage" in query.lower() or "medical" in query.lower():
            subqueries.append(f"{query} policy health insurance waiting period eligible")
        elif "reimbursement" in query.lower() or "expense" in query.lower():
            subqueries.append(f"{query} per diem travel allowance limit claim receipt")
            
        return subqueries
