import re
from typing import Dict, Any, List

class ResponseGenerationAgent:
    """
    Agent 4: Response Generation Agent
    Synthesizes grounded answers strictly adherence to retrieved chunk context
    and attaches exact source citations (file name, page/row, chunk ID).
    """
    
    def process(
        self, 
        user_query: str, 
        retrieval_output: Dict[str, Any],
        clarification_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        # If clarification is required, return clarification message directly
        if clarification_output.get("clarification_required"):
            return {
                "agent_name": "Response Generation Agent",
                "response_text": clarification_output.get("message"),
                "confidence_score": clarification_output.get("confidence_score", 0.0),
                "citations": [],
                "grounded": False,
                "status": "clarification_needed"
            }
            
        chunks = retrieval_output.get("top_k_chunks", [])
        if not chunks:
            return {
                "agent_name": "Response Generation Agent",
                "response_text": "No relevant context found in the knowledge base.",
                "confidence_score": 0.0,
                "citations": [],
                "grounded": False,
                "status": "no_context"
            }
            
        # Synthesize answer strictly based on retrieved chunks
        citations = []
        context_snippets = []
        
        for idx, chunk in enumerate(chunks, start=1):
            content = chunk.get("content", "")
            meta = chunk.get("metadata", {})
            file_name = meta.get("file_name", "Document")
            page_num = meta.get("page_number", 1)
            chunk_id = chunk.get("chunk_id", f"chunk_{idx}")
            
            citations.append({
                "citation_id": f"[{idx}]",
                "source_document": file_name,
                "page_or_row": page_num,
                "section": meta.get("section", "General"),
                "chunk_id": chunk_id,
                "similarity_score": chunk.get("similarity_score", 0.0)
            })
            context_snippets.append(f"[{idx}] {content}")
            
        # Generate synthesized response with citations
        response_text = self._synthesize_grounded_answer(user_query, chunks, citations)
        top_score = chunks[0].get("similarity_score", 0.9)
        
        return {
            "agent_name": "Response Generation Agent",
            "response_text": response_text,
            "confidence_score": top_score,
            "citations": citations,
            "grounded": True,
            "status": "completed"
        }

    def _synthesize_grounded_answer(
        self, 
        query: str, 
        chunks: List[Dict[str, Any]], 
        citations: List[Dict[str, Any]]
    ) -> str:
        """
        Extracted grounding logic synthesizing answers strictly from source text.
        """
        top_content = chunks[0]["content"]
        cite_tag = citations[0]["citation_id"]
        
        # Extracted factual answer synthesis from chunk content
        lines = [line.strip() for line in top_content.split("\n") if line.strip()]
        relevant_lines = []
        
        q_words = [w.lower() for w in query.split() if len(w) > 3]
        for line in lines:
            if any(qw in line.lower() for qw in q_words):
                relevant_lines.append(line)
                
        if not relevant_lines:
            relevant_lines = lines[:2]
            
        summary = " ".join(relevant_lines)
        if not summary.endswith("."):
            summary += "."
            
        answer = f"Based on the Knowledge Base ({citations[0]['source_document']}, Page/Row {citations[0]['page_or_row']}):\n\n{summary} {cite_tag}"
        
        if len(chunks) > 1:
            second_cite = citations[1]["citation_id"]
            second_content = chunks[1]["content"][:150].replace("\n", " ")
            answer += f"\n\nAdditional Details: {second_content}... {second_cite}"
            
        return answer
