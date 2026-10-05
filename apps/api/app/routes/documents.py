"""
StrataSentry-NWIS: Document Intelligence & Legacy WCR Endpoints
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Dict, Any
from ..services.orchestrator import DomainOrchestrator
from services.document_intelligence.parsers.pdf_parser import PDFParser
from services.rag_engine.chunking.depth_aware_chunking import DepthAwareChunker

router = APIRouter(prefix="/api/v1/documents", tags=["Documents & Knowledge"])

@router.get("")
async def list_documents():
    orc = DomainOrchestrator()
    return [
        {"document_name": "WCR_MOR_118.pdf", "well_name": "MOR-118", "type": "Well Completion Report", "pages": 28, "status": "INDEXED"},
        {"document_name": "WCR_NHK_412.pdf", "well_name": "NHK-412", "type": "Well Completion Report", "pages": 34, "status": "INDEXED"},
        {"document_name": "WCR_BGH_07.pdf", "well_name": "BGH-07", "type": "Well Completion Report", "pages": 22, "status": "INDEXED"}
    ]

@router.get("/evidence")
async def get_evidence_chunks(well_id: str = "NHK-421", depth: float = 2845.0):
    orc = DomainOrchestrator()
    results = orc.retriever.retrieve(
        query="stuck pipe packoff coal caving",
        formation="Barail Coal-Shale",
        depth_md=depth,
        limit=4
    )
    return results
