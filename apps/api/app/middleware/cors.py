"""
StrataSentry-NWIS: CORS Middleware Configuration
"""

from fastapi.middleware.cors import CORSMiddleware
import os

def setup_cors(app):
    origins = [value.strip() for value in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",") if value.strip()]
    local_development = os.getenv("ENVIRONMENT", "development").lower() == "development"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=r"http://(?:localhost|127\.0\.0\.1)(?::\d+)?" if local_development else None,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )
