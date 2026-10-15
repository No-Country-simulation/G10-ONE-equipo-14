from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
import logging
from time import perf_counter
from uuid import uuid4
from fastapi import Request
from app.core.observability import configure_observability, log_event

configure_observability()

app = FastAPI(
    title=settings.app_name,
    version=settings.api_schema_version,
    description="CommunityLab MVP API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

logger = logging.getLogger("communitylab.requests")

@app.middleware("http")
async def request_trace(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        log_event(
            logger,
            "request_failed",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
            duration_ms=round((perf_counter() - started) * 1000, 2),
            error_type=type(exc).__name__,
        )
        raise
    response.headers["X-Request-ID"] = request_id
    log_event(
        logger,
        "request_completed",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        request_id=request_id,
        duration_ms=round((perf_counter() - started) * 1000, 2),
    )
    return response

@app.get("/")
def root():
    return {"service": settings.app_name, "docs": "/docs", "health": "/api/v1/health"}
