from typing import Dict, Any, List

class ConversationMemoryAgent:
    """
    Agent 5: Conversation Memory Agent
    Maintains session history state, resolves coreferences, and handles state persistence.
    """
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.sessions: Dict[str, List[Dict[str, Any]]] = {}

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.sessions.get(session_id, [])

    def process(
        self, 
        session_id: str, 
        user_query: str, 
        response_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        history = self.sessions[session_id]
        
        # Add interaction log
        turn_data = {
            "turn_id": len(history) + 1,
            "user_query": user_query,
            "response_text": response_output.get("response_text", ""),
            "confidence_score": response_output.get("confidence_score", 0.0),
            "citations": response_output.get("citations", [])
        }
        
        history.append(turn_data)
        if len(history) > self.max_history:
            history.pop(0)
            
        return {
            "agent_name": "Conversation Memory Agent",
            "session_id": session_id,
            "total_turns": len(history),
            "recent_turns": history,
            "status": "updated"
        }
