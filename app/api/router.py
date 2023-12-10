from fastapi import APIRouter, Depends
from .ml import router as ml_router
from .auth import router as auth_router
from .user import router as user_router
from .market import router as market_router
from app.middlewares.db import get_db


def create_api_router(prefix: str = "/api") -> APIRouter:
    router = APIRouter(prefix=prefix)
    router.include_router(user_router, tags=["user"])
    router.include_router(ml_router, tags=["ml"])
    router.include_router(auth_router, tags=["auth"])
    router.include_router(market_router, tags=["market"])
    return router
