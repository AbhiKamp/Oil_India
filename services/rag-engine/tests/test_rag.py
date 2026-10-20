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
    assert "2,400 lpm" not in resp["answer"].lower()
    assert "45-bbl" not in resp["answer"].lower()

def test_copilot_abstains_without_evidence():
    copilot = llm_mod.MistralDrillingCopilot()
    resp = copilot.generate_advisory(
        query="What should I do about a kick?",
        current_depth=2845.0,
        formation="Barail Coal-Shale",
        evidence_chunks=[]
    )
    assert "insufficient retrieved evidence" in resp["answer"].lower()
    assert resp["citations"] == []
    assert "NHK-412" not in resp["answer"]
    assert "1.34" not in resp["answer"]

def test_copilot_does_not_invent_citation_for_missing_metadata():
    copilot = llm_mod.MistralDrillingCopilot()
    resp = copilot.generate_advisory(
        query="What happened?",
        current_depth=2845.0,
        formation="Barail Coal-Shale",
        evidence_chunks=[{"text": "A reported event."}]
    )
    assert "A reported event." in resp["answer"]
    assert resp["citations"] == []


def test_lexical_search_does_not_rank_by_unrelated_raw_depth_or_random_vectors():
    retriever = retriever_mod.QdrantRetriever()
    chunks = [
        {"chunk_id": "irrelevant", "well_name": "B", "formation_name": "Barail", "md_top": 2845,
         "text": "Cement placement completed."},
        {"chunk_id": "relevant", "well_name": "A", "formation_name": "Barail", "md_top": 3500,
         "text": "Mechanical pack-off and stuck pipe were recorded.", "page_number": None},
    ]
    retriever.add_local_chunks(chunks)
    retriever.add_local_chunks(chunks)
    assert len(retriever.local_chunks) == 2
    results = retriever.retrieve("packoff stuck pipe", formation="Barail", depth_md=2845)
    assert [row["chunk_id"] for row in results] == ["relevant"]
    assert results[0]["page_number"] is None
    assert results[0]["retrieval_method"] == "local_lexical_search"
    assert retriever.retrieve("unrelated satellite equipment") == []


def test_token_vectors_are_stable_and_do_not_mutate_numpy_random_state():
    import numpy as np
    embedder = embedder_mod.DomainEmbedder()
    np.random.seed(7)
    expected = np.random.random()
    np.random.seed(7)
    a = embedder.embed_text("stuck pipe")
    b = embedder.embed_text("pipe stuck")
    assert a == b
    assert np.random.random() == expected
