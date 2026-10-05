"""
StrataSentry-NWIS: Master FastAPI Application
National Well Intelligence System & Real-Time Drilling Hazard Mitigation Platform
"""

import os
import sys
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from .middleware.cors import setup_cors
from .middleware.logging import RequestLoggingMiddleware
from .routes.wells import router as wells_router
from .routes.trajectory import router as trajectory_router
from .routes.telemetry import router as telemetry_router
from .routes.risks import router as risks_router
from .routes.documents import router as documents_router
from .routes.assistant import router as assistant_router
from .routes.health import router as health_router
from .routes.stream import router as stream_router
from .services.orchestrator import DomainOrchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Domain Services and Cache
    print("[*] Starting StrataSentry-NWIS Gateway...")
    orc = DomainOrchestrator()
    print(f"[+] Loaded {len(orc.wells)} wells and {len(orc.trajectory_nhk421)} trajectory stations.")
    yield
    print("[*] Shutting down StrataSentry-NWIS Gateway.")

app = FastAPI(
    title="StrataSentry-NWIS API Gateway",
    description="Real-Time Drilling Hazard Mitigation & Grounded Sub-surface Well Intelligence Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Setup Middleware
setup_cors(app)
app.add_middleware(RequestLoggingMiddleware)

# Include Routers
app.include_router(health_router)
app.include_router(wells_router)
app.include_router(trajectory_router)
app.include_router(telemetry_router)
app.include_router(risks_router)
app.include_router(documents_router)
app.include_router(assistant_router)
app.include_router(stream_router)

@app.get("/")
async def root():
    return {
        "system": "StrataSentry-NWIS",
        "status": "OPERATIONAL",
        "description": "National Well Intelligence System Gateway",
        "docs": "/docs",
        "health": "/health"
    }
