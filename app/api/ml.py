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

router: tp.Final[APIRouter] = APIRouter(prefix="/algo")


@router.get("/data/{algo_type}/d/{algorithm_uuid}/{version_id}")
async def test(
    algo_type: tp.Literal["ml", "algo"],
    algorithm_uuid: uuid.UUID,
    version_id: uuid.UUID,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    db_version: AlgorithmVersion | None = (
        (
            await db.execute(
                sa.select(AlgorithmVersion)
                .options(orm.joinedload(AlgorithmVersion.backtests))
                .where(AlgorithmVersion.uuid == version_id)
            )
        )
        .unique()
        .scalar_one_or_none()
    )
    if db_version is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # return
    print(db_version.backtests)
    return [
        algorithm.BacktestResultsDto.model_validate(obj) for obj in db_version.backtests
    ]


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


@router.post("/{algo_type}/create")
async def create_algorithm(
    algo_type: tp.Literal["ml", "algo"],
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
        algo_type=algo_type,
        name=payload.name,
        sec_id=payload.sec_id,
        uuid=model_uuid,
    )
    db_user.algorithms.append(db_model)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return algorithm.AlgorithmCreateResponse(
        algo_type=algo_type, uuid=model_uuid, name=payload.name, sec_id=payload.sec_id
    )


@router.get("/{algo_type}/d/{algorithm_uuid}")
async def get_algorithm(
    algorithm_uuid: uuid.UUID,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
) -> algorithm.AlgorithmDto:
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return algorithm.AlgorithmDto.model_validate(db_algorithm)


@router.post("/{algo_type}/d/{algorithm_uuid}/{version_uuid}")
async def update_algorithm(
    algo_type: tp.Literal["ml", "algo"],
    version_uuid: uuid.UUID,
    payload: algorithm.AlgorithmVersionUpdate,
    algorithm_uuid: uuid.UUID | None = None,
    user: UserTokenData = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """POST /a/ml/{UUID}
    Сохранение изменений по кнопке сохраняет (создает новую версию):
        - features
        - management
        - nodes: штука для кубиков
    """
    stmt = (
        sa.select(Algorithm)
        .options(orm.joinedload(Algorithm.versions))
        .where(Algorithm.uuid == algorithm_uuid)
    )
    db_algorithm = (await db.execute(stmt)).unique().scalar()
    if db_algorithm is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    # defining features
    new_features: dict[str, tp.Any] | list[dict[str, tp.Any]]

    if algo_type == "ml" and type(payload.features) == algorithm.MlFeatures:

        new_features = payload.features.model_dump() if payload.features else dict()
    elif algo_type == "algo" and type(payload.features) == list:
        new_features = payload.features
    else:
        print(type(payload.features), payload.features)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid algo features",
        )
    if version_uuid is None:
        db_algorithm.versions.append(
            AlgorithmVersion(
                uuid=version_uuid,
                features=new_features,  # type:ignore
                management=payload.management.model_dump(),
                nodes=payload.nodes,
                algorithm_id=db_algorithm.id,
            )
        )
    versions = [
        index
        for index, obj in enumerate(db_algorithm.versions)
        if obj.uuid == version_uuid
    ]
    # print(versions)
    if len(versions) == 0:

        db_algorithm.versions.append(
            AlgorithmVersion(
                uuid=version_uuid,
                features=new_features,
                management=payload.management.model_dump(),
                nodes=payload.nodes,
                algorithm_id=db_algorithm.id,
            )
        )
    else:
        index = versions[0]
        db_algorithm.versions[index].features = new_features
        db_algorithm.versions[index].management = payload.management.model_dump()
        db_algorithm.versions[index].nodes = payload.nodes if payload.nodes else []

    await db.commit()
    await db.refresh(db_algorithm)
    return algorithm.AlgorithmDto.model_validate(db_algorithm)


async def train_model(
    db: AsyncSession,
    model_id: uuid.UUID,
    payload: algorithm.AlgorithmVersionDto,
    ticker: str = "SBER",
    period: tp.Literal["1m", "5m", "10m", "30m", "60m"] = "1m",
) -> str:
    model_path = f"./models/{str(model_id)}"
    if type(payload.features) != algorithm.MlFeatures:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="invalid algo features",
        )
    final_path = f"{model_path}_{ticker}_{period}_{payload.features.model}.bin"

    if os.path.exists(final_path):
        os.remove(final_path)

    model = TrainModel(
        ticker=ticker,
        timeframe=period,
        features=payload.features.model_dump(),
        model_id=model_path,
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
    return model_path


@router.post("/{algo_type}/d/{algorithm_uuid}/{version_uuid}/backtest/{period}")
async def run_backtest(
    algo_type: tp.Literal["ml", "algo"],
    algorithm_uuid: uuid.UUID,
    version_uuid: uuid.UUID,
    background_tasks: BackgroundTasks,
    period: tp.Literal["1m", "10m", "60m"] = "1m",
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
    versions = [obj for obj in db_algorithm.versions if obj.uuid == version_uuid]
    if len(versions) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    version: AlgorithmVersion = versions[0]
    """
      "management": {
    "balance": 0,
    "max_balance_for_trading": 0,
    "min_balance_for_trading": 0,
    "part_of_balance_for_buy": 0,
    "sum_for_buy_rur": 0,
    "sum_for_buy_num": 0,
    "part_of_balance_for_sell": 0,
    "sum_for_sell_rur": 0,
    "sum_for_sell_num": 0,
    "sell_all": true
  }

    """
    outp: pd.Series[tp.Any]
    backtest: NewBacktest
    if db_algorithm.algo_type == "ml":

        model_path = await train_model(
            db,
            algorithm_uuid,
            algorithm.AlgorithmVersionDto.model_validate(version),
            db_algorithm.sec_id,
            period,
        )

        backtest = NewBacktest(
            "ml_model",
            model_path,
            db_algorithm.sec_id,
            period,
            0.1,
            6,
            version.management["balance"],
            2,
            model_features=version.features,
        )

        logging.info(f"ml training: <user={user.user_id} algorithm={version.uuid}>")
    elif db_algorithm.algo_type == "algo":
        backtest = NewBacktest(
            "if_model",
            None,
            db_algorithm.sec_id,
            period,
            0.1,
            6,
            version.management["balance"],
            2,
            IF_features=version.features
            # model_features=version.features,
        )

    # outp.fillna(None)
    html_path = (
        f"{datetime.datetime.now().isoformat()}-{db_algorithm.uuid}-{version.uuid}.html"
    )

    outp = backtest.do_backtest(html_save_path=f"./backtests/{html_path}")
    outp = outp.replace({np.nan: None})

    raw = algorithm.BacktestResultsRaw.model_validate(outp.to_dict())
    result = algorithm.BacktestResults.model_validate(raw)
    db_backtest = AlgorithmBacktest(
        version_id=version.id,
        data=result.serialize(),
        graph_url=html_path,
    )
    db.add(db_backtest)
    await db.commit()

    return {
        "status": f"/api/static/{html_path}",
        "data": raw,
    }
