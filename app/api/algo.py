import typing as tp
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, BackgroundTasks, Depends
from app.dependencies.db import get_session
from app.schemas.features import MlFeatures, Lags, Macd


router: tp.Final[APIRouter] = APIRouter(prefix="/ml")
