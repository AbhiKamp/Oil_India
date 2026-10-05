import os
import sys
import pytest

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import importlib.util

def load_mod(name, rel_path):
    full_path = os.path.join(base_dir, rel_path)
    spec = importlib.util.spec_from_file_location(name, full_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

chunker_mod = load_mod("depth_aware_chunking", "chunking/depth_aware_chunking.py")
embedder_mod = load_mod("domain_embedder", "embeddings/domain_embedder.py")
filter_mod = load_mod("metadata_filter", "retrieval/metadata_filter.py")
retriever_mod = load_mod("qdrant_retriever", "retrieval/qdrant_retriever.py")
llm_mod = load_mod("mistral_client", "llm/mistral_client.py")

def test_depth_aware_chunker():
    sample_text = """
[PAGE 19]
Depth: 2,848.0 m MD | Barail Formation
Incident Type: MECHANICAL HOLE PACK-OFF
While drilling ahead at 2,848.0 m MD, the string suffered packoff.
"""
    chunker = chunker_mod.DepthAwareChunker()
    chunks = chunker.chunk_wcr_document(sample_text, well_name="MOR-118")
    assert len(chunks) == 1
    assert chunks[0]["well_name"] == "MOR-118"
    assert chunks[0]["page_number"] == 19
    assert chunks[0]["md_top"] == 2848.0
    assert chunks[0]["has_incident"] is True

def test_domain_embedder():
    embedder = embedder_mod.DomainEmbedder()
    vec = embedder.embed_text("Mechanical stuck pipe in Barail coal sequence")
    assert len(vec) == 768

def test_metadata_filter():
    f = filter_mod.MetadataFilterBuilder.build_qdrant_filter(
        formation_name="Barail Coal-Shale",
        depth_md=2845.0,
        incident_type="hole_packoff"
    )
    assert "must" in f
    assert len(f["must"]) == 3

def test_rag_retriever_and_copilot():
    retriever = retriever_mod.QdrantRetriever()
    retriever.add_local_chunks([
        {
            "chunk_id": "c1",
            "well_name": "MOR-118",
            "formation_name": "Barail Coal-Shale",
            "md_top": 2848.0,
            "md_bottom": 2855.0,
            "page_number": 19,
            "text": "Stuck pipe occurred in Barail coal at 2848m MD due to sloughing coal. Freed by spotting 45 bbls polymer pill and jarring up 85 klbs."
        }
    ])

    results = retriever.retrieve("stuck pipe in Barail coal", formation="Barail Coal-Shale", depth_md=2845.0)
    assert len(results) >= 1
    assert results[0]["well_name"] == "MOR-118"

    copilot = llm_mod.MistralDrillingCopilot()
    resp = copilot.generate_advisory(
        query="How to free stuck pipe at 2845m?",
        current_depth=2845.0,
        formation="Barail Coal-Shale",
        evidence_chunks=results
    )
    assert "MOR-118" in resp["answer"]
    assert len(resp["citations"]) >= 1
    assert resp["citations"][0]["well_name"] == "MOR-118"
