from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.core.config import settings
import logging
from uuid import uuid4
from fastapi import Request

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
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    logger.info("request_completed method=%s path=%s status=%s request_id=%s", request.method, request.url.path, response.status_code, request_id)
    return response

@app.get("/")
def root():
    return {"service": settings.app_name, "docs": "/docs", "health": "/api/v1/health"}
