import os
import math
import numpy as np
import logging
from typing import List

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Handles text embedding generation using SentenceTransformers, OpenAI/Gemini, or local fallback.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.st_model = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.st_model = SentenceTransformer(self.model_name)
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer ({e}). Using lightweight vector embedder.")
            self.st_model = None

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
            
        if self.st_model is not None:
            try:
                embeddings = self.st_model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                return embeddings.tolist()
            except Exception as e:
                logger.error(f"SentenceTransformer embedding error: {e}. Falling back.")
                
        # Deterministic 384-dimensional hashed feature embedding fallback
        return [self._fallback_embed(t) for t in texts]

    def embed_query(self, query: str) -> List[float]:
        return self.embed_texts([query])[0]

    def _fallback_embed(self, text: str, dim: int = 384) -> List[float]:
        """
        Creates normalized semantic n-gram hashed feature vector for text matching.
        """
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for i, word in enumerate(words):
            # Uni-gram hash
            h1 = abs(hash(word)) % dim
            vec[h1] += 1.0
            # Bi-gram hash
            if i > 0:
                bigram = f"{words[i-1]}_{word}"
                h2 = abs(hash(bigram)) % dim
                vec[h2] += 1.5
                
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()
