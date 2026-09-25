import re
from typing import Dict, Any, List, Optional

class ConversationMemoryAgent:
    """
    Agent 5: Conversation Memory Agent (M3.2)
    Maintains session history, tracks referenced documents & entities,
    resolves coreferences (pronouns across turns), and enforces sliding window memory bounds.
    """
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}
        self.session_entities: Dict[str, List[str]] = {}
        self.session_docs: Dict[str, List[str]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.sessions.get(session_id, [])

    def get_last_turn(self, session_id: str) -> Optional[Dict[str, Any]]:
        history = self.get_history(session_id)
        return history[-1] if history else None

    def resolve_coreference(self, user_query: str, session_id: str) -> str:
        """
        Resolves pronouns or relative references (e.g., 'its', 'that policy', 'the plan')
        using entities and topics from previous turns (M3.2).
        """
        history = self.get_history(session_id)
        if not history:
            return user_query

        q_lower = user_query.lower()
        pronouns = ["its", "it", "this policy", "that policy", "this plan", "that plan", "the plan", "the policy", "their"]
        
        has_pronoun = any(re.search(rf"\b{re.escape(p)}\b", q_lower) for p in pronouns)
        if not has_pronoun:
            return user_query

        # Find recent tracked entity or subject from previous turns
        recent_entities = self.session_entities.get(session_id, [])
        recent_docs = self.session_docs.get(session_id, [])
        
        target_subject = None
        if recent_entities:
            target_subject = recent_entities[-1]
        elif recent_docs:
            target_subject = recent_docs[-1]
        else:
            # Fallback to last query nouns
            last_turn = history[-1]
            last_q = last_turn.get("user_query", "")
            words = [w for w in last_q.split() if len(w) > 3 and w.lower() not in ["what", "how", "when", "where", "tell", "about"]]
            if words:
                target_subject = " ".join(words[:3])

        if not target_subject:
            return user_query

        # Perform coreference replacement
        refined_query = user_query
        for p in pronouns:
            pattern = re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE)
            if pattern.search(refined_query):
                refined_query = pattern.sub(target_subject, refined_query, count=1)
                break

        return refined_query

    def process(
        self, 
        session_id: str, 
        user_query: str, 
        response_output: Dict[str, Any],
        query_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            self.session_entities[session_id] = []
            self.session_docs[session_id] = []
            
        history = self.sessions[session_id]
        
        # Track entities and documents from current turn
        if query_analysis and query_analysis.get("extracted_entities"):
            for ent in query_analysis["extracted_entities"]:
                if ent not in self.session_entities[session_id]:
                    self.session_entities[session_id].append(ent)
                    
        citations = response_output.get("citations", [])
        for cite in citations:
            doc_name = cite.get("source_document")
            if doc_name and doc_name not in self.session_docs[session_id]:
                self.session_docs[session_id].append(doc_name)
                
        # Store interaction log
        turn_data = {
            "turn_id": len(history) + 1,
            "user_query": user_query,
            "response_text": response_output.get("response_text", ""),
            "confidence_score": response_output.get("confidence_score", 0.0),
            "citations": citations,
            "query_type": response_output.get("query_type", "factual")
        }
        
        history.append(turn_data)
        
        # Enforce sliding window memory
        if len(history) > self.max_history:
            history.pop(0)
            
        return {
            "agent_name": "Conversation Memory Agent",
            "session_id": session_id,
            "total_turns": len(history),
            "tracked_entities": self.session_entities.get(session_id, []),
            "tracked_documents": self.session_docs.get(session_id, []),
            "status": "updated"
        }
