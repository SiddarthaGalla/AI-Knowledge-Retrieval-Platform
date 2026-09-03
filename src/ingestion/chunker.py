import uuid
from typing import List, Dict, Any

class RecursiveChunker:
    """
    Splits text blocks into overlapping chunks for semantic vector indexing.
    Default target size: 500 characters (~100 tokens), overlap: 100 characters (~20 tokens).
    """
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "; ", ", ", " "]

    def chunk_document(
        self, 
        blocks: List[Dict[str, Any]], 
        doc_id: str, 
        doc_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Processes list of document content blocks and generates chunk dictionary objects.
        """
        chunks = []
        global_chunk_idx = 0
        
        for block in blocks:
            content = block.get("content", "").strip()
            if not content:
                continue
                
            raw_chunks = self._recursive_split(content, self.chunk_size, self.chunk_overlap)
            
            for raw_text in raw_chunks:
                if not raw_text.strip():
                    continue
                
                safe_doc_prefix = "".join(c for c in doc_id if c.isalnum())[-12:]
                chunk_id = f"chunk_{safe_doc_prefix}_{global_chunk_idx:04d}"
                token_estimate = len(raw_text.split())
                
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": doc_id,
                    "chunk_index": global_chunk_idx,
                    "content": raw_text.strip(),
                    "token_count": token_estimate,
                    "metadata": {
                        "file_name": doc_metadata.get("file_name", "unknown"),
                        "file_type": doc_metadata.get("file_type", "unknown"),
                        "domain": doc_metadata.get("domain", "General"),
                        "page_number": block.get("page_number", 1),
                        "section": block.get("section", "General"),
                        "document_id": doc_id
                    }
                })
                global_chunk_idx += 1
                
        return chunks

    def _recursive_split(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """
        Splits text recursively using natural boundaries.
        """
        if len(text) <= chunk_size:
            return [text]
            
        best_sep = " "
        for sep in self.separators:
            if sep in text:
                best_sep = sep
                break
                
        parts = text.split(best_sep)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for part in parts:
            part_len = len(part) + (len(best_sep) if current_chunk else 0)
            if current_length + part_len > chunk_size and current_chunk:
                joined = best_sep.join(current_chunk)
                chunks.append(joined)
                
                # Compute overlap
                overlap_tokens = []
                overlap_len = 0
                for item in reversed(current_chunk):
                    if overlap_len + len(item) <= chunk_overlap:
                        overlap_tokens.insert(0, item)
                        overlap_len += len(item)
                    else:
                        break
                        
                current_chunk = overlap_tokens + [part]
                current_length = sum(len(x) for x in current_chunk) + len(best_sep) * (len(current_chunk) - 1)
            else:
                current_chunk.append(part)
                current_length += part_len
                
        if current_chunk:
            chunks.append(best_sep.join(current_chunk))
            
        return chunks
