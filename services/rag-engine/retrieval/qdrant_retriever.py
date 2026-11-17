"""Local lexical evidence retrieval (legacy class name retained for callers).

No vector database or trained semantic model is represented by this local mode.
Depth in another well is deliberately not used as a relevance bonus.
"""

import re
from typing import Any, Dict, List, Optional


_STOPWORDS = set("a an and are as at be by can did do does for from happened has have how i in is it me of on or should show tell that the these this to was were what when where which who why with would".split())


def terms(text: str) -> set[str]:
    text = text.casefold().replace("pack-off", "packoff").replace("pack off", "packoff")
    return set(re.findall(r"[a-z0-9]+", text)) - _STOPWORDS


def formation_key(text: str) -> str:
    return " ".join(text.casefold().removesuffix(" formation").split())


class QdrantRetriever:
    def __init__(self, host: str = "localhost", port: int = 6333, collection_name: str = "drilling_knowledge_chunks"):
        self.local_chunks: List[Dict[str, Any]] = []
        self.mode = "local_lexical_search"
        self.client = None

    def add_local_chunks(self, chunks: List[Dict[str, Any]]):
        """Upsert by source chunk ID, keeping repeated indexing idempotent."""
        indexed = {chunk["chunk_id"]: chunk for chunk in self.local_chunks}
        for chunk in chunks:
            indexed[chunk["chunk_id"]] = dict(chunk)
        self.local_chunks = list(indexed.values())

    def retrieve(self, query: str, formation: Optional[str] = None,
                 depth_md: Optional[float] = None, limit: int = 3) -> List[Dict[str, Any]]:
        query_terms = terms(query)
        if not query_terms or limit <= 0:
            return []
        results = []
        # ponytail: linear scan for the small demo corpus; use indexed text search when it grows.
        for chunk in self.local_chunks:
            if formation and formation.casefold() != "all" and formation_key(chunk.get("formation_name") or "") != formation_key(formation):
                continue
            if chunk.get("review_state", "approved") != "approved":
                continue
            document_terms = terms(" ".join(str(chunk.get(key) or "") for key in ("text", "well_name", "formation_name")))
            overlap = query_terms & document_terms
            if not overlap:
                continue
            score = len(overlap) / len(query_terms)
            results.append({
                **{key: chunk.get(key) for key in (
                    "chunk_id", "well_name", "document_name", "formation_name", "md_top",
                    "md_bottom", "page_number", "text", "page_reference_type", "provenance",
                )},
                "score": round(score, 3),
                "retrieval_method": self.mode,
            })
        results.sort(key=lambda item: (-item["score"], item["chunk_id"]))
        return results[:limit]
