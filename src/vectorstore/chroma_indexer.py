import os
import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from src.vectorstore.embedder import EmbeddingGenerator

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages vector index, chunk metadata storage, cosine similarity search,
    and domain filtering. Works with ChromaDB or local in-memory fallback.
    """
    def __init__(self, persist_directory: str = "./data/vector_store"):
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        self.embedder = EmbeddingGenerator()
        
        self.chunks_db: Dict[str, Dict[str, Any]] = {}
        self.embeddings_db: Dict[str, List[float]] = {}
        self.documents_db: Dict[str, Dict[str, Any]] = {}
        
        self.db_file = os.path.join(persist_directory, "vector_store_data.json")
        self._load_store()

    def add_document_and_chunks(
        self, 
        doc_metadata: Dict[str, Any], 
        chunks: List[Dict[str, Any]]
    ):
        """
        Indexes document metadata and chunk embeddings.
        """
        doc_id = doc_metadata.get("document_id")
        if not doc_id:
            return
            
        self.documents_db[doc_id] = doc_metadata
        
        if not chunks:
            self._save_store()
            return
            
        texts = [c["content"] for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        for chunk, emb in zip(chunks, embeddings):
            chunk_id = chunk["chunk_id"]
            self.chunks_db[chunk_id] = chunk
            self.embeddings_db[chunk_id] = emb
            
        self._save_store()
        logger.info(f"Indexed document {doc_id} with {len(chunks)} chunks.")

    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        domain_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Performs cosine similarity search against indexed chunks.
        Supports filtering by domain.
        """
        if not self.chunks_db or not self.embeddings_db:
            return []
            
        query_emb = np.array(self.embedder.embed_query(query), dtype=np.float32)
        q_norm = np.linalg.norm(query_emb)
        if q_norm > 0:
            query_emb = query_emb / q_norm
            
        results = []
        for chunk_id, chunk in self.chunks_db.items():
            metadata = chunk.get("metadata", {})
            if domain_filter and domain_filter.lower() != "all":
                chunk_domain = metadata.get("domain", "").lower()
                if chunk_domain != domain_filter.lower():
                    continue
                    
            emb = np.array(self.embeddings_db[chunk_id], dtype=np.float32)
            e_norm = np.linalg.norm(emb)
            if e_norm > 0:
                emb = emb / e_norm
                
            score = float(np.dot(query_emb, emb))
            # Also calculate keyword match boost for domain accuracy
            content_lower = chunk["content"].lower()
            stop_words = {"what", "where", "when", "which", "how", "this", "that", "with", "from", "for", "the", "and", "are", "is", "a", "an", "in", "of", "or", "to", "does"}
            query_terms = [t.strip("?,.") for t in query.lower().split() if len(t.strip("?,.")) > 2 and t.strip("?,.") not in stop_words]
            match_count = sum(1 for term in query_terms if term in content_lower)
            if query_terms and match_count > 0:
                keyword_boost = 0.35 * (match_count / len(query_terms))
                score = min(1.0, score + keyword_boost)
                
            results.append({
                "chunk_id": chunk_id,
                "document_id": chunk.get("document_id"),
                "content": chunk.get("content"),
                "metadata": metadata,
                "similarity_score": round(score, 4)
            })
            
        # Sort by similarity score descending
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]

    def get_documents(self) -> List[Dict[str, Any]]:
        return list(self.documents_db.values())

    def delete_document(self, doc_id: str) -> bool:
        if doc_id in self.documents_db:
            del self.documents_db[doc_id]
            # Remove associated chunks
            to_remove = [cid for cid, c in self.chunks_db.items() if c.get("document_id") == doc_id]
            for cid in to_remove:
                if cid in self.chunks_db:
                    del self.chunks_db[cid]
                if cid in self.embeddings_db:
                    del self.embeddings_db[cid]
            self._save_store()
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        domains = {}
        for doc in self.documents_db.values():
            dom = doc.get("domain", "General")
            domains[dom] = domains.get(dom, 0) + 1
            
        return {
            "total_documents": len(self.documents_db),
            "total_chunks": len(self.chunks_db),
            "total_vectors": len(self.embeddings_db),
            "domain_breakdown": domains
        }

    def _save_store(self):
        try:
            data = {
                "documents": self.documents_db,
                "chunks": self.chunks_db,
                "embeddings": self.embeddings_db
            }
            with open(self.db_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def _load_store(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents_db = data.get("documents", {})
                    self.chunks_db = data.get("chunks", {})
                    self.embeddings_db = data.get("embeddings", {})
                logger.info(f"Loaded vector store: {len(self.documents_db)} docs, {len(self.chunks_db)} chunks.")
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
