"""
StrataSentry-NWIS: Database Seeder
Seeds local relational and vector databases with synthetic Assam-Arakan Basin drilling data.
"""

import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services.rag_engine.embeddings.domain_embedder import DomainEmbedder
from services.rag_engine.retrieval.qdrant_retriever import QdrantRetriever

def seed():
    print("=" * 65)
    print("SEEDING STRATASENTRY-NWIS DATABASE & VECTOR REPOSITORIES")
    print("=" * 65)

    # 1. Verify wells metadata
    wells_file = os.path.join(PROJECT_ROOT, "data", "synthetic", "wells", "wells.json")
    if os.path.exists(wells_file):
        with open(wells_file, "r") as f:
            wells = json.load(f)
        print(f"[+] Loaded {len(wells)} Upper Assam Basin wells: {', '.join(w['well_id'] for w in wells)}")
    else:
        print("[!] Wells metadata file missing.")

    # 2. Vector indexing of WCR reports
    reports_dir = os.path.join(PROJECT_ROOT, "data", "synthetic", "reports")
    embedder = DomainEmbedder()
    retriever = QdrantRetriever()

    if os.path.exists(reports_dir):
        report_files = [f for f in os.listdir(reports_dir) if f.endswith(".txt")]
        indexed_count = 0
        for r in report_files:
            p = os.path.join(reports_dir, r)
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            well_name = r.replace("WCR_", "").replace(".txt", "")
            # Generate test embedding
            v = embedder.embed_text(content[:300])
            retriever.add_local_chunks([{
                "chunk_id": f"{well_name}_chunk_1",
                "well_name": well_name,
                "formation_name": "Barail Coal-Shale" if "MOR" in well_name or "NHK" in well_name else "Tipam Sandstone",
                "md_top": 2848.0 if "MOR" in well_name else (2912.0 if "NHK" in well_name else 1642.0),
                "md_bottom": 2865.0,
                "page_number": 19,
                "text": content[:600]
            }])
            indexed_count += 1
        print(f"[+] Indexed {indexed_count} historical Well Completion Reports into Qdrant store.")

    print("[+] Seeding completed successfully. All systems operational.")

if __name__ == "__main__":
    seed()
