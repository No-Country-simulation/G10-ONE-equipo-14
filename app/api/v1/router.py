from fastapi import APIRouter
from app.api.v1.endpoints import assets, health, process, runs

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(process.router, tags=["processing"])
api_router.include_router(runs.router, tags=["runs"])
api_router.include_router(assets.router, tags=["assets"])
