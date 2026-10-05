"""
StrataSentry-NWIS: Qdrant Vector Collection Initializer
Initializes the drilling knowledge vector collection with payload indexes.
"""

import os
import sys

def init_qdrant_collection(host="localhost", port=6333, collection_name="drilling_knowledge_chunks"):
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PayloadSchemaType
        
        client = QdrantClient(host=host, port=port)
        collections = [c.name for c in client.get_collections().collections]
        
        if collection_name not in collections:
            print(f"[*] Creating Qdrant collection: {collection_name} (dim=768, Distance=Cosine)...")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
            # Create payload indexes for metadata-filtered RAG
            client.create_payload_index(collection_name, "formation_name", PayloadSchemaType.KEYWORD)
            client.create_payload_index(collection_name, "well_name", PayloadSchemaType.KEYWORD)
            client.create_payload_index(collection_name, "incident_type", PayloadSchemaType.KEYWORD)
            client.create_payload_index(collection_name, "md_top", PayloadSchemaType.FLOAT)
            client.create_payload_index(collection_name, "md_bottom", PayloadSchemaType.FLOAT)
            print(f"[+] Qdrant collection '{collection_name}' initialized successfully with payload indexes.")
        else:
            print(f"[*] Collection '{collection_name}' already exists.")
            
    except Exception as e:
        print(f"[!] Qdrant initialization note: {e}")
        print("[!] Operating in local fallback mode if Qdrant daemon is offline.")

if __name__ == "__main__":
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    name = os.getenv("QDRANT_COLLECTION_NAME", "drilling_knowledge_chunks")
    init_qdrant_collection(host, port, name)
