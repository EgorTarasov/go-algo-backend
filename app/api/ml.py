"""Интерфейс

GET /a/ml
Получение списка всех алгоритмов пользователя
    - UUID
    - SECID
    - name
    - versions: {id: {features, management}

POST /a/ml/create
Создание мл алгоритма
    - сохранения информации о названии актива (SECID)
    - сохранения информации названия алгоритма
Генерация UUID для дальнейшей работы

POST /a/ml/{UUID}
Сохранение изменений по кнопке сохраняет (создает новую версию):
    - features
    - management

POST /a/ml/{UUID}/backtest
Запускает текущую версию модели для бэктеста и выдает id бэктеста


GET /a/ml/{UUID}
Получения информации об Алгоритме
    - UUID
    - SECID
    - name
    - versions: {id: {features, management}


"""
import time
import typing as tp
import logging
import uuid


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

from GoAlgoMlPart.ModelInference import ModelInference
from app.schemas.features import MlFeatures

router: tp.Final[APIRouter] = APIRouter(prefix="/ml")


@router.get("/test")
async def test():

    start = time.perf_counter()
    features = {
        "lags": {"features": ["open", "close", "target"], "period": [1, 2, 3]},
        "cma": {"features": ["open", "close", "volume"]},
        "sma": {"features": ["open", "close", "volume"], "period": [2, 3, 4]},
        "ema": {"features": ["open", "close", "volume"], "period": [2, 3, 4, 10, 15]},
        "green_candles_ratio": {"period": [2]},
        "red_candles_ratio": {"period": [2]},
        "rsi": False,
        "macd": False,  # только (12, 26)
        "bollinger": False,
        "time_features": {
            "month": True,
            "week": True,
            "day_of_month": True,
            "day_of_week": True,
            "hour": True,
            "minute": True,
        },
        "anomal_value": True,
        "anomal_price_changing": True,
    }
    # train = Еfeatures=features, ticker="SBER", timeframe="1m")
    # train.train()
    return time.perf_counter() - start


@router.post("/inference/{model_uuid}/{period}")
async def test_inference(
    model_id: uuid.UUID,
    period: tp.Literal["1m", "10m", "60m"] = "10m",
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == model_id)
    )
    db_algorithm: Algorithm | None = (await db.execute(stmt)).unique().scalar()
    if db_algorithm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    inference = ModelInference(
        model_id=f"./models/{str(model_id)}",
        ticker=db_algorithm.sec_id,
        features=db_algorithm.versions[-1].features,
        timeframe=period,
        api_data="",
    )
    df, result = inference.get_pred_one_candle()
    return int(result)


@router.get("/")
async def get_algorithms(
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> list[algorithm.AlgorithmDto]:
    """GET /a/ml
    Получение списка всех алгоритмов пользователя
            - UUID
            - SECID
            - name
            - versions: {id: {features, management}
    """

    stmt = (
        sa.select(User)
        .options(orm.selectinload(User.algorithms).selectinload(Algorithm.versions))
        .where(User.id == user.user_id)
    )
    db_user: User | None = (await db.execute(stmt)).unique().scalar()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return [algorithm.AlgorithmDto.model_validate(obj) for obj in db_user.algorithms]


@router.post("/create")
async def create_algorithm(
    payload: algorithm.AlgorithmCreate,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> algorithm.AlgorithmCreateResponse:
    """POST /a/ml/create
    Создание мл алгоритма
        - сохранения информации о названии актива (SECID)
        - сохранения информации названия алгоритма
    Генерация UUID для дальнейшей работы
    """
    stmt = (
        sa.select(User)
        .options(orm.selectinload(User.algorithms))
        .where(User.id == user.user_id)
    )
    db_user: User | None = (await db.execute(stmt)).unique().scalar()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not found"
        )
    model_uuid = uuid.uuid4()
    db_model: Algorithm = Algorithm(
        name=payload.name, sec_id=payload.sec_id, uuid=model_uuid
    )
    db_user.algorithms.append(db_model)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return algorithm.AlgorithmCreateResponse(
        uuid=model_uuid, name=payload.name, sec_id=payload.sec_id
    )


@router.get("/d/{algorithm_uuid}")
async def get_algorithm(
    algorithm_uuid: uuid.UUID,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """GET /a/ml/{UUID}
    Получения информации об Алгоритме
        - UUID
        - SECID
        - name
        - versions: {id: {features, management}
    """

    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == algorithm_uuid)
    )
    db_algorithm = (await db.execute(stmt)).unique().scalar()
    if db_algorithm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return algorithm.AlgorithmDto.model_validate(db_algorithm)


@router.post("/d/{algorithm_uuid}")
async def update_algorithm(
    algorithm_uuid: uuid.UUID,
    payload: algorithm.AlgorithmVersionUpdate,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """POST /a/ml/{UUID}
    Сохранение изменений по кнопке сохраняет (создает новую версию):
        - features
        - management
    """
    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == algorithm_uuid)
    )
    db_algorithm = (await db.execute(stmt)).unique().scalar()
    if db_algorithm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db_algorithm.versions.append(
        AlgorithmVersion(
            features=payload.features.model_dump() if payload.features else {},
            management=payload.management.model_dump(),
            nodes=payload.nodes,
            algorithm_id=db_algorithm.id,
        )
    )
    await db.commit()
    await db.refresh(db_algorithm)
    return algorithm.AlgorithmDto.model_validate(db_algorithm)


# TODO: выбрать формат отправки на backtest


async def train_model(
    db: AsyncSession,
    model_id: uuid.UUID,
    payload: algorithm.AlgorithmVersionDto,
    ticker: str = "SBER",
    period: tp.Literal["1m", "5m", "10m", "30m", "60m"] = "1m",
):
    model = TrainModel(
        ticker=ticker,
        timeframe=period,
        features=payload.features.model_dump(),
        model_id=f"./models/{str(model_id)}",
    )
    logging.info(f"ml training start: <model_id={model_id}>")
    start = time.perf_counter()
    new_features: MlFeatures = MlFeatures.model_validate(model.train())

    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == model_id)
    )

    db_model: Algorithm | None = (await db.execute(stmt)).unique().scalar()
    if db_model is None:
        logging.warning("Model not found")
        raise Exception("not found")
    db_model.versions[-1].features = new_features.model_dump()
    db.add(db_model)
    await db.commit()
    logging.info(
        f"ml training finished: <model_id={model_id}, time={time.perf_counter() - start}>"
    )


@router.post("/d/{algorithm_uuid}/train/{period}")
async def run_backtest(
    algorithm_uuid: uuid.UUID,
    background_tasks: BackgroundTasks,
    period: tp.Literal["1m", "5m", "10m", "30m", "60m"] = "1m",
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == algorithm_uuid)
    )
    db_algorithm: Algorithm | None = (await db.execute(stmt)).unique().scalar()

    if db_algorithm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    logging.info(f"ml training: <user={user.user_id} algorithm={db_algorithm.id}>")
    payload: algorithm.AlgorithmVersionDto = (
        algorithm.AlgorithmVersionDto.model_validate(db_algorithm.versions[-1])
    )
    background_tasks.add_task(
        train_model, db, algorithm_uuid, payload, db_algorithm.sec_id, period
    )

    return payload


# @router.post("/{algorithm_uuid}/backtest")
# async def run_backtest(
#     algorithm_uuid: uuid.UUID,
#     user: UserTokenData = Depends(get_current_user),
#     db: AsyncSession = Depends(get_session),
# ):
#     """POST /a/ml/{UUID}/backtest
#     Запускает текущую версию модели для бэктеста и выдает id бэктеста
#     """
#     stmt = (
#         sa.select(Algorithm)
#         .options(orm.joinedload(Algorithm.versions))
#         .where(Algorithm.uuid == algorithm_uuid)
#     )
#     db_algorithm = (await db.execute(stmt)).unique().scalar()
#     if db_algorithm is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     db_algorithm.versions.append(
#         AlgorithmVersion(
#             features=payload.features.model_dump(),
#             management=payload.management,
#             algorithm_id=db_algorithm.id,
#         )
#     )
#     await db.commit()
#     await db.refresh(db_algorithm)
#     return algorithm.AlgorithmDto.model_validate(db_algorithm)


#
#
# @router.post("/create/{sec_id}/{period}")
# async def create_model(
#     features: MlFeatures,
#     background_tasks: BackgroundTasks,
#     user: UserTokenData = Depends(get_current_user),
#     sec_id: str = "SBER",
#     period: tp.Literal["1m", "10m"] = "1m",
#     db: AsyncSession = Depends(get_session),
# ):
#     db_model: MlAlgorithm = MlAlgorithm(
#         name="Test",
#         sec_id=sec_id,
#         period=period,
#     )
#     db_model.creator_id = user.user_id
#     db.add(db_model)
#     await db.commit()
#     await db.refresh(db_model)
#     # TODO: вынести в отдельную функцию
#     model_id = uuid.uuid5(
#         uuid.NAMESPACE_DNS, str(db_model.id) + str(db_model.created_at)
#     )
#
#     background_tasks.add_task(train_model, str(model_id), features, sec_id, period)
#     # создаем модель в базе данных
#
#     return {"id": model_id, "period": period, "features": features}
