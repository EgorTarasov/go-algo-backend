"""Market API.
/market/search 
 - возращает список алгоритмов, которые подходят под критерии поиска

/market/algorithm/{algorithm_id}

"""


import pandas as pd
import numpy as np
import time
import typing as tp
import logging
import uuid
import os
import datetime


import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status


from app.dependencies import get_current_user, UserTokenData
from app.dependencies.db import get_session
from app.schemas import algorithm
from app.models import Algorithm, AlgorithmVersion, AlgorithmBacktest, UserAlgorithm
from app.models import User
from GoAlgoMlPart.TrainModel import TrainModel
from GoAlgoMlPart.NewBacktest import NewBacktest
from GoAlgoMlPart.ModelInference import ModelInference
from app.schemas.features import MlFeatures


router: tp.Final[APIRouter] = APIRouter(prefix="/market")


@router.post("/search")
async def search_algorithms(
    user: UserTokenData = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Search algorithms by features."""
    stmt = sa.select(Algorithm)
    result = (await session.execute(stmt)).all()
    return [algorithm.AlgorithmSeachResult.model_validate(obj[0]) for obj in result]
