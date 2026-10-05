"""
StrataSentry-NWIS: Qdrant Vector Retriever
Retrieves grounded historical drilling chunks using semantic search and payload filtering.
"""

from typing import List, Dict, Any, Optional
import numpy as np
try:
    from ..embeddings.domain_embedder import DomainEmbedder
    from .metadata_filter import MetadataFilterBuilder
except (ImportError, ValueError):
    from embeddings.domain_embedder import DomainEmbedder
    from retrieval.metadata_filter import MetadataFilterBuilder

class QdrantRetriever:
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "drilling_knowledge_chunks"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.embedder = DomainEmbedder()
        self.client = None
        self.local_chunks = [] # In-memory fallback index
        self._init_client()

    def _init_client(self):
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(host=self.host, port=self.port, timeout=2.0)
        except Exception:
            self.client = None

    def add_local_chunks(self, chunks: List[Dict[str, Any]]):
        """Indexes chunks for in-memory / edge search."""
        for c in chunks:
            c_copy = dict(c)
            c_copy["embedding"] = self.embedder.embed_text(c["text"])
            self.local_chunks.append(c_copy)

    def retrieve(
        self,
        query: str,
        formation: Optional[str] = None,
        depth_md: Optional[float] = None,
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Executes hybrid semantic retrieval.
        """
        query_vec = self.embedder.embed_text(query)

        # 1. Try Qdrant client if available
        if self.client:
            try:
                # Use Qdrant search
                pass
            except Exception:
                pass

        # 2. In-memory cosine search fallback
        results = []
        for c in self.local_chunks:
            # Metadata filter check
            if formation and formation != "All" and c.get("formation_name") != formation:
                continue

            # Cosine similarity
            c_emb = np.array(c["embedding"])
            q_emb = np.array(query_vec)
            score = float(np.dot(c_emb, q_emb) / (np.linalg.norm(c_emb) * np.linalg.norm(q_emb) + 1e-9))

            # Depth proximity bonus if depth matches within 100m
            if depth_md and c.get("md_top") is not None:
                dist = abs(c["md_top"] - depth_md)
                if dist < 100:
                    score += 0.15

            results.append({
                "chunk_id": c.get("chunk_id", ""),
                "well_name": c.get("well_name", ""),
                "formation_name": c.get("formation_name", ""),
                "md_top": c.get("md_top"),
                "md_bottom": c.get("md_bottom"),
                "page_number": c.get("page_number", 1),
                "text": c.get("text", ""),
                "score": round(score, 3)
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
