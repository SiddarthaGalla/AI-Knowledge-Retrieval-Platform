import time
from typing import Dict, Any, Optional
from src.vectorstore.chroma_indexer import VectorStoreManager
from src.agents.query_understanding_agent import QueryUnderstandingAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.clarification_agent import ClarificationAgent
from src.agents.response_generation_agent import ResponseGenerationAgent
from src.agents.memory_agent import ConversationMemoryAgent

class RAGPipelineOrchestrator:
    """
    Stateful 5-Agent RAG Orchestrator
    Coordinates execution sequence across Query Understanding, Retrieval, Clarification,
    Response Generation, and Memory agents.
    """
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
        self.qua_agent = QueryUnderstandingAgent()
        self.retrieval_agent = RetrievalAgent(vector_store)
        self.clarification_agent = ClarificationAgent(confidence_threshold=0.65)
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

        # 1. Query Understanding Agent
        qua_res = self.qua_agent.process(user_query)
        agent_execution_log.append({
            "step": 1,
            "agent": "Query Understanding Agent",
            "details": f"Intent: {qua_res['intent']} | Entities: {qua_res['entities']} | Expanded Sub-queries: {len(qua_res['expanded_subqueries'])}",
            "data": qua_res
        })

        # 2. Retrieval Agent
        ret_res = self.retrieval_agent.process(qua_res, top_k=5, domain_filter=domain_filter)
        agent_execution_log.append({
            "step": 2,
            "agent": "Retrieval Agent",
            "details": f"Retrieved {len(ret_res['top_k_chunks'])} chunks | Top Similarity Score: {ret_res['max_similarity_score']:.4f}",
            "data": ret_res
        })

        # 3. Clarification Agent
        clar_res = self.clarification_agent.process(qua_res, ret_res)
        agent_execution_log.append({
            "step": 3,
            "agent": "Clarification Agent",
            "details": f"Clarification Required: {clar_res['clarification_required']} | Reason: {clar_res['reason']}",
            "data": clar_res
        })

        # 4. Response Generation Agent
        resp_res = self.response_agent.process(user_query, ret_res, clar_res)
        agent_execution_log.append({
            "step": 4,
            "agent": "Response Generation Agent",
            "details": f"Confidence: {resp_res['confidence_score']:.2f} | Citations: {len(resp_res['citations'])} | Grounded: {resp_res['grounded']}",
            "data": resp_res
        })

        # 5. Conversation Memory Agent
        mem_res = self.memory_agent.process(session_id, user_query, resp_res)
        agent_execution_log.append({
            "step": 5,
            "agent": "Conversation Memory Agent",
            "details": f"Session: {session_id} | Total Session Turns: {mem_res['total_turns']}",
            "data": mem_res
        })

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "user_query": user_query,
            "session_id": session_id,
            "response_text": resp_res["response_text"],
            "confidence_score": resp_res["confidence_score"],
            "citations": resp_res["citations"],
            "clarification_required": clar_res["clarification_required"],
            "clarification_message": clar_res.get("message") if clar_res["clarification_required"] else None,
            "execution_time_ms": elapsed_ms,
            "agent_execution_log": agent_execution_log,
            "retrieved_chunks": ret_res["top_k_chunks"]
        }
