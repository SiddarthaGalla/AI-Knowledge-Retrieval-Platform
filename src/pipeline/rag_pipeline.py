import time
import logging
from typing import Dict, Any, Optional
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.agents.query_understanding_agent import QueryUnderstandingAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.clarification_agent import ClarificationAgent
from src.agents.response_generation_agent import ResponseGenerationAgent
from src.agents.memory_agent import ConversationMemoryAgent

logger = logging.getLogger(__name__)

class RAGPipelineOrchestrator:
    """
    Stateful 5-Agent RAG Pipeline Orchestrator (Milestone 3)
    Coordinates sequential agent flow, multi-turn memory coreference resolution,
    and clarification query refinement loops.
    """
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.qua_agent = QueryUnderstandingAgent()
        self.retrieval_agent = RetrievalAgent(vector_store, min_relevance_threshold=0.30)
        self.clarification_agent = ClarificationAgent(confidence_threshold=0.30)
        self.response_agent = ResponseGenerationAgent()
        self.memory_agent = ConversationMemoryAgent()

    def run_query(
        self, 
        user_query: str, 
        session_id: str = "default_session",
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        agent_execution_log = []

        try:
            # 0. M3.2 Coreference Resolution (pronouns -> recent entities)
            resolved_query = self.memory_agent.resolve_coreference(user_query, session_id)
            if resolved_query != user_query:
                agent_execution_log.append({
                    "step": 0,
                    "agent": "Conversation Memory Agent",
                    "details": f"Coreference Resolved: '{user_query}' -> '{resolved_query}'",
                    "data": {"original": user_query, "resolved": resolved_query}
                })

            # 1. Query Understanding Agent (M2.1 & M3.1)
            qua_res = self.qua_agent.process(resolved_query)
            agent_execution_log.append({
                "step": 1,
                "agent": "Query Understanding Agent",
                "details": f"Type: {qua_res['query_type'].upper()} | Confidence: {qua_res['classification_confidence']:.2f} | Path: {qua_res['routing_path']}",
                "data": qua_res
            })

            # 2. Retrieval Agent (M2.2)
            ret_res = self.retrieval_agent.process(qua_res, top_k=5, domain_filter=domain_filter)
            agent_execution_log.append({
                "step": 2,
                "agent": "Retrieval Agent",
                "details": f"Retrieved {len(ret_res['top_k_chunks'])} relevant chunks | Max Relevance: {ret_res['max_similarity_score']:.4f}",
                "data": ret_res
            })

            # 3. Clarification Agent (M3.1)
            clar_res = self.clarification_agent.process(qua_res, ret_res)
            agent_execution_log.append({
                "step": 3,
                "agent": "Clarification Agent",
                "details": f"Clarification Triggered: {clar_res['clarification_required']} | Reason: {clar_res['reason']}",
                "data": clar_res
            })

            # 4. Response Generation Agent (M2.3 & M3.4)
            resp_res = self.response_agent.process(user_query, qua_res, ret_res, clar_res)
            agent_execution_log.append({
                "step": 4,
                "agent": "Response Generation Agent",
                "details": f"Confidence Level: {resp_res['confidence_level']} | Score: {resp_res['confidence_score']:.2f} | Citations: {len(resp_res['citations'])}",
                "data": resp_res
            })

            # 5. Conversation Memory Agent (M3.2)
            mem_res = self.memory_agent.process(session_id, user_query, resp_res, qua_res)
            agent_execution_log.append({
                "step": 5,
                "agent": "Conversation Memory Agent",
                "details": f"Session: {session_id} | Total Session Turns: {mem_res['total_turns']}",
                "data": mem_res
            })

            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            return {
                "user_query": user_query,
                "resolved_query": resolved_query,
                "session_id": session_id,
                "query_type": qua_res["query_type"],
                "classification_confidence": qua_res["classification_confidence"],
                "routing_path": qua_res["routing_path"],
                "response_text": resp_res["response_text"],
                "confidence_score": resp_res["confidence_score"],
                "confidence_level": resp_res["confidence_level"],
                "citations": resp_res["citations"],
                "clarification_required": clar_res["clarification_required"],
                "clarification_message": clar_res.get("message") if clar_res["clarification_required"] else None,
                "suggested_questions": clar_res.get("suggested_questions", []),
                "multi_parts": clar_res.get("multi_parts", []),
                "execution_time_ms": elapsed_ms,
                "agent_execution_log": agent_execution_log,
                "retrieved_chunks": ret_res["top_k_chunks"]
            }
        except Exception as e:
            logger.error(f"Orchestrator error: {e}", exc_info=True)
            return {
                "user_query": user_query,
                "resolved_query": user_query,
                "session_id": session_id,
                "query_type": "error",
                "classification_confidence": 0.0,
                "routing_path": "error_fallback",
                "response_text": f"System Error executing multi-agent workflow: {str(e)}",
                "confidence_score": 0.0,
                "confidence_level": "LOW CONFIDENCE",
                "citations": [],
                "clarification_required": False,
                "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                "agent_execution_log": agent_execution_log,
                "retrieved_chunks": []
            }

    def run_refinement(
        self, 
        session_id: str, 
        clarification_response: str,
        domain_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Processes user clarification feedback loop by combining original pending query
        with user's clarification response (M3.1).
        """
        last_turn = self.memory_agent.get_last_turn(session_id)
        original_query = last_turn.get("user_query", "") if last_turn else ""
        
        refined_query = self.clarification_agent.combine_and_refine(original_query, clarification_response)
        logger.info(f"Refined Query for session {session_id}: '{refined_query}'")
        
        return self.run_query(user_query=refined_query, session_id=session_id, domain_filter=domain_filter)
