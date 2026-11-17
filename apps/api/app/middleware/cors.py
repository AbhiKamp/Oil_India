"""
StrataSentry-NWIS: CORS Middleware Configuration
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import re

def setup_cors(app):
    origins = [value.strip() for value in os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",") if value.strip()]
    local_development = os.getenv("ENVIRONMENT", "development").lower() == "development"
    local_pattern = r"http://(?:localhost|127\.0\.0\.1)(?::\d+)?"

    @app.middleware("http")
    async def reject_cross_origin_writes(request, call_next):
        origin = request.headers.get("origin")
        if origin and request.method in {"POST", "PATCH", "PUT", "DELETE"}:
            allowed = origin in origins or "*" in origins or (
                local_development and re.fullmatch(local_pattern, origin)
            )
            if not allowed:
                return JSONResponse({"detail": "Origin is not allowed for local writes"}, status_code=403)
        return await call_next(request)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_origin_regex=local_pattern if local_development else None,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Content-Type"],
    )
