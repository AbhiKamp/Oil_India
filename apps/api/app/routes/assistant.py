"""
StrataSentry-NWIS: AI Drilling Assistant / Copilot Endpoint
"""

from fastapi import APIRouter
from ..schemas.pydantic_models import ChatRequest, ChatResponse
from ..services.orchestrator import DomainOrchestrator

router = APIRouter(prefix="/api/v1/assistant", tags=["AI Copilot"])

@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(req: ChatRequest):
    orc = DomainOrchestrator()
    # 1. Retrieve relevant offset evidence
    chunks = orc.retriever.retrieve(
        query=req.query,
        formation=req.formation,
        depth_md=req.current_depth,
        limit=3
    )

    # 2. Generate grounded response
    res = orc.copilot.generate_advisory(
        query=req.query,
        current_depth=req.current_depth,
        formation=req.formation,
        evidence_chunks=chunks
    )

    return {
        "answer": res["answer"],
        "citations": res["citations"],
        "engine": res["engine"],
        "evidence_count": res["evidence_count"]
    }
