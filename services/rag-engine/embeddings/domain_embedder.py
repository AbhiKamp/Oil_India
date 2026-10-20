"""Deterministic token-hash vectors for local lexical matching, not learned embeddings."""

import hashlib
import math
import re
from typing import List


class DomainEmbedder:
    def __init__(self, dimension: int = 768):
        if dimension < 1:
            raise ValueError("dimension must be positive")
        self.dimension = dimension
        self.model = None
        self.method = "untrained_hashed_token_counts"

    def embed_text(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        for token in re.findall(r"[a-z0-9]+", text.casefold()):
            slot = int.from_bytes(hashlib.blake2s(token.encode(), digest_size=4).digest(), "big") % self.dimension
            vector[slot] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector
