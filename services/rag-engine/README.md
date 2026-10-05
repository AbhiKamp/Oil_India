# Depth-Aware RAG Engine

Retrieval-Augmented Generation system preserving stratigraphic depth anchors and enforcing grounded citations for drilling operations.

---

## Architecture

- **`chunking/`**:
  - `depth_aware_chunking.py`: Preserves measured depth ($MD$), formation top, and page numbers.
- **`embeddings/`**:
  - `domain_embedder.py`: Produces 768-dimensional dense semantic vectors.
- **`retrieval/`**:
  - `metadata_filter.py`: Constructs payload filter clauses (formation, depth window, incident type).
  - `qdrant_retriever.py`: Hybrid semantic retriever with Qdrant and offline cosine cache.
- **`llm/`**:
  - `mistral_client.py`: Air-gapped and cloud LLM inference interface.
- **`prompts/`**:
  - `drilling_prompts.py`: Structured prompt templates with petroleum engineering directives.
- **`citations/`**:
  - `citation_grounding.py`: Validates citations against verified offset well completion reports.
