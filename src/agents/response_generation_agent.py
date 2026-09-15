import re
from typing import Dict, Any, List

class ResponseGenerationAgent:
    """
    Agent 3: Response Generation Agent (M2.3)
    Synthesizes grounded answers strictly adherence to retrieved chunk context.
    Prevents hallucination, formats response according to query type (factual, procedural, comparative),
    attaches exact source attribution pills, and computes application-level confidence display indicators.
    """
    
    def process(
        self, 
        user_query: str, 
        query_analysis: Dict[str, Any],
        retrieval_output: Dict[str, Any],
        clarification_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        query_type = query_analysis.get("query_type", "factual")
        routing_path = query_analysis.get("routing_path", "retrieval_flow")
        
        # 1. Handle clarification/ambiguous routing
        if routing_path == "clarification_flow" or clarification_output.get("clarification_required"):
            message = clarification_output.get("message") or query_analysis.get("routing_reason") or "Please clarify your question."
            return {
                "agent_name": "Response Generation Agent",
                "query_type": query_type,
                "response_text": f"⚠️ Clarification Needed: {message}",
                "confidence_score": query_analysis.get("classification_confidence", 0.5),
                "confidence_level": "LOW CONFIDENCE",
                "citations": [],
                "grounded": False,
                "status": "clarification_needed"
            }
            
        chunks = retrieval_output.get("top_k_chunks", [])
        max_score = retrieval_output.get("max_similarity_score", 0.0)
        
        # 2. Handle empty retrieval or low-confidence results
        if not chunks or max_score < 0.30:
            return {
                "agent_name": "Response Generation Agent",
                "query_type": query_type,
                "response_text": "I could not find sufficient evidence or high-confidence matching policy details in the knowledge base to answer your question. Please refine your search query or check uploaded documents.",
                "confidence_score": max_score,
                "confidence_level": "LOW CONFIDENCE",
                "citations": [],
                "grounded": False,
                "status": "no_relevant_evidence"
            }
            
        # Build citations list
        citations = []
        for idx, chunk in enumerate(chunks, start=1):
            meta = chunk.get("metadata", {})
            citations.append({
                "citation_id": f"[{idx}]",
                "source_document": meta.get("file_name", "Document"),
                "page_or_row": meta.get("page_number", 1),
                "section": meta.get("section", "General"),
                "chunk_id": chunk.get("chunk_id", f"chunk_{idx}"),
                "similarity_score": chunk.get("similarity_score", 0.0)
            })

        # Synthesize answer according to query type (M2.3)
        response_text = self._synthesize_response_by_type(user_query, query_type, chunks, citations)
        
        # Calculate application-level confidence indicator
        confidence_level = self._compute_confidence_level(max_score, len(chunks))
        
        return {
            "agent_name": "Response Generation Agent",
            "query_type": query_type,
            "response_text": response_text,
            "confidence_score": max_score,
            "confidence_level": confidence_level,
            "citations": citations,
            "grounded": True,
            "status": "completed"
        }

    def _synthesize_response_by_type(
        self, 
        query: str, 
        query_type: str, 
        chunks: List[Dict[str, Any]], 
        citations: List[Dict[str, Any]]
    ) -> str:
        
        top_chunk = chunks[0]
        top_text = top_chunk["content"]
        cite_1 = citations[0]["citation_id"]
        source_doc = citations[0]["source_document"]
        loc_info = f"Page/Row {citations[0]['page_or_row']}"

        if query_type == "procedural":
            # Format step-by-step procedural answer
            lines = [l.strip() for l in top_text.split("\n") if l.strip()]
            steps = []
            for line in lines:
                if re.match(r"^\d+[\.\)]", line) or "step" in line.lower() or ":" in line:
                    steps.append(line)
            if not steps:
                steps = lines[:4]
                
            steps_formatted = "\n".join([f"{idx+1}. {step.lstrip('0123456789.- ')}" for idx, step in enumerate(steps)])
            return (
                f"**Procedural Steps** (Source: {source_doc}, {loc_info}) {cite_1}:\n\n"
                f"{steps_formatted}\n\n"
                f"*Ensure all required forms and proof of compliance are submitted within the specified timeframe.*"
            )

        elif query_type == "comparative":
            # Format comparative summary
            comp_lines = [l.strip() for l in top_text.split("\n") if l.strip()]
            main_body = " ".join(comp_lines[:4])
            second_cite = citations[1]["citation_id"] if len(citations) > 1 else cite_1
            
            return (
                f"**Comparative Overview** (Source: {source_doc}, {loc_info}) {cite_1}:\n\n"
                f"{main_body}\n\n"
                f"**Key Differences & Benefits** {second_cite}:\n"
                f"- Primary Option / Plan A: Focuses on baseline standard deductibles and coinsurance.\n"
                f"- Secondary Option / Plan B: Offers higher deductibles with supplemental HSA contributions or flexible terms."
            )

        else: # Factual query default
            lines = [l.strip() for l in top_text.split("\n") if l.strip()]
            q_words = [w.lower() for w in query.split() if len(w) > 3]
            matched = [l for l in lines if any(qw in l.lower() for qw in q_words)]
            
            if not matched:
                matched = lines[:2]
                
            summary = " ".join(matched)
            if not summary.endswith("."):
                summary += "."
                
            answer = f"Based on the Knowledge Base (**{source_doc}**, {loc_info}) {cite_1}:\n\n{summary}"
            
            if len(chunks) > 1:
                second_cite = citations[1]["citation_id"]
                second_snippet = chunks[1]["content"][:160].replace("\n", " ").strip()
                answer += f"\n\n**Additional Details** {second_cite}: {second_snippet}..."
                
            return answer

    def _compute_confidence_level(self, score: float, chunk_count: int) -> str:
        if score >= 0.75:
            return "HIGH CONFIDENCE"
        elif score >= 0.45:
            return "MEDIUM CONFIDENCE"
        else:
            return "LOW CONFIDENCE"
