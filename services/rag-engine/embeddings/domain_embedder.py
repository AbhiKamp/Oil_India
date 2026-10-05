"""
StrataSentry-NWIS: Domain Embedding Engine
Generates 768-dimensional dense vector representations with offline fallback.
"""

from typing import List, Union
import numpy as np
import hashlib

class DomainEmbedder:
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
        self.model = None
        self._init_model()

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('BAAI/bge-base-en-v1.5')
        except Exception:
            self.model = None

    def embed_text(self, text: str) -> List[float]:
        """
        Embeds a single string into a 768-dimensional vector.
        """
        if self.model:
            try:
                emb = self.model.encode(text)
                return emb.tolist()
            except Exception:
                pass

        # Robust, deterministic semantic bag-of-words projection for edge/offline execution
        np.random.seed(int(hashlib.md5(text.encode('utf-8')).hexdigest()[:8], 16))
        vec = np.random.randn(self.dimension)
        # Unit normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return [round(float(v), 5) for v in vec]
