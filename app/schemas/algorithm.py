import datetime
import typing as tp
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from .features import MlFeatures


class BacktestResultsRaw(BaseModel):

    """
    Модель для преобразования из формата Backtesting py в формат для сохранения в базу данных
    https://github.com/kernc/backtesting.py/blob/master/backtesting/_stats.py
    Start                     2023-12-07 20:42:00
    End                       2023-12-08 23:49:00
    Duration                      1 days 03:07:00
    Exposure Time [%]                        99.8
    Equity Final [$]                   9966.33059
    Equity Peak [$]                  10021.884957
    Return [%]                          -0.336694
    Buy & Hold Return [%]               -1.193025
    Return (Ann.) [%]                  -13.455843
    Volatility (Ann.) [%]                     NaN
    Sharpe Ratio                              NaN
    Sortino Ratio                             0.0
    Calmar Ratio                              0.0
    Max. Drawdown [%]                     -0.9311
    Avg. Drawdown [%]                   -0.362783
    Max. Drawdown Duration        0 days 16:36:00
    Avg. Drawdown Duration        0 days 03:23:00
    # Trades                                  422
    Win Rate [%]                        52.369668
    Best Trade [%]                       0.644688
    Worst Trade [%]                     -0.598451
    Avg. Trade [%]                       -0.02484
    Max. Trade Duration           0 days 10:11:00
    Avg. Trade Duration           0 days 00:50:00
    Profit Factor                         0.75137
    Expectancy [%]                      -0.024599
    SQN                                 -1.847145
    """

    start: datetime.datetime = Field(..., alias="Start")
    end: datetime.datetime = Field(..., alias="End")
    duration: datetime.timedelta = Field(..., alias="Duration")
    exposure_time: float = Field(..., alias="Exposure Time [%]")

    equity_final: float = Field(..., alias="Equity Final [$]")
    equity_peak: float = Field(..., alias="Equity Peak [$]")
    backtest_return: float = Field(..., alias="Return [%]")
    buy_hold_return: float = Field(..., alias="Buy & Hold Return [%]")
    return_annualy: float = Field(..., alias="Return (Ann.) [%]")

    violatility: float | None = Field(None, alias="Volatility (Ann.) [%]")
    sharpe_ratio: float | None = Field(None, alias="Sharpe Ratio")
    sortino_ratio: float | None = Field(None, alias="Sortino Ratio")
    calmar_ratio: float | None = Field(None, alias="Calmar Ratio")

    max_drawdown: float | None = Field(None, alias="Max. Drawdown [%]")
    avg_drawdown: float | None = Field(..., alias="Avg. Drawdown [%]")
    max_drawdown_duration: datetime.timedelta | None = Field(
        None, alias="Max. Drawdown Duration"
    )
    avg_drawdown_duration: datetime.timedelta | None = Field(
        None, alias="Avg. Drawdown Duration"
    )
    trades: int = Field(..., alias="# Trades")
    win_rate: float | None = Field(None, alias="Win Rate [%]")
    best_trade: float | None = Field(None, alias="Best Trade [%]")
    worst_trade: float | None = Field(None, alias="Worst Trade [%]")

    avg_trade: float | None = Field(None, alias="Avg. Trade [%]")
    max_trade_duration: datetime.timedelta | None = Field(
        None, alias="Max. Trade Duration"
    )
    avg_trade_duration: datetime.timedelta | None = Field(
        None, alias="Avg. Trade Duration"
    )
    profit_factor: float | None = Field(None, alias="Profit Factor")
    expentancy: float | None = Field(None, alias="Expectancy [%]")
    sqn: float | None = Field(..., alias="SQN")

    model_config = ConfigDict(from_attributes=True)

    def serialize(self) -> dict[str, tp.Any]:
        # convert datetime to string and don't forget about None values and save their aliases
        # data = self.dict(by_alias=True)
        data = self.model_dump(by_alias=True)
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                data[key] = value.isoformat()
            elif isinstance(value, datetime.timedelta):
                data[key] = str(value)
            elif isinstance(value, float) and value.is_integer():
                data[key] = int(value)

        return data


class BacktestResults(BaseModel):

    start: datetime.datetime = Field(...)
    end: datetime.datetime = Field(...)
    duration: datetime.timedelta = Field(...)
    exposure_time: float = Field(...)

    equity_final: float = Field(...)
    equity_peak: float = Field(...)
    backtest_return: float = Field(...)
    buy_hold_return: float = Field(...)
    return_annualy: float = Field(...)

    violatility: float | None = Field(None)
    sharpe_ratio: float | None = Field(None)
    sortino_ratio: float | None = Field(None)
    calmar_ratio: float | None = Field(None)

    max_drawdown: float | None = Field(None)
    avg_drawdown: float | None = Field(...)
    max_drawdown_duration: datetime.timedelta | None = Field(None)
    avg_drawdown_duration: datetime.timedelta | None = Field(None)
    trades: int = Field(...)
    win_rate: float | None = Field(None)
    best_trade: float | None = Field(None)
    worst_trade: float | None = Field(None)

    avg_trade: float | None = Field(None)
    max_trade_duration: datetime.timedelta | None = Field(None)
    avg_trade_duration: datetime.timedelta | None = Field(None)
    profit_factor: float | None = Field(None)
    expentancy: float | None = Field(None)
    sqn: float | None = Field(...)

    model_config = ConfigDict(from_attributes=True)

    def serialize(self) -> dict[str, tp.Any]:

        data = self.model_dump(by_alias=True)
        for key, value in data.items():
            if isinstance(value, datetime.datetime):
                data[key] = value.isoformat()
            elif isinstance(value, datetime.timedelta):
                data[key] = str(value)
            elif isinstance(value, float) and value.is_integer():
                data[key] = int(value)

        return data


class BacktestResultsDto(BaseModel):
    graph_url: str
    data: BacktestResults

    model_config = ConfigDict(from_attributes=True)


class RiskManagementParameters(BaseModel):
    balance: float = Field(..., description="Баланс")
    max_balance_for_trading: float = Field(
        ..., description="Максимальный баланс для торговли"
    )
    min_balance_for_trading: float = Field(
        ..., description="Минимальный баланс для торговли"
    )
    part_of_balance_for_buy: float = Field(..., description="Доля баланса для покупки")
    sum_for_buy_rur: float = Field(..., description="Сумма для покупки в рублях")
    sum_for_buy_num: float = Field(..., description="Сумма для покупки в количестве")
    part_of_balance_for_sell: float = Field(..., description="Доля баланса для продажи")
    sum_for_sell_rur: float = Field(..., description="Сумма для продажи в рублях")
    sum_for_sell_num: float = Field(..., description="Сумма для продажи в количестве")
    sell_all: bool = Field(..., description="Продавать все")


class AlgorithmBase(BaseModel):

    sec_id: str = Field(...)
    name: str = Field(...)


class AlgorithmVersionBase(BaseModel):
    features: MlFeatures | list[dict[str, tp.Any]] | None = Field(...)
    management: RiskManagementParameters = Field(...)
    nodes: list[dict[str, tp.Any]] | dict[str, tp.Any] | None = Field(...)


class AlgorithmVersionUpdate(AlgorithmVersionBase):
    ...


class AlgorithmSeachResult(BaseModel):
    uuid: UUID
    sec_id: str
    name: str
    algo_type: tp.Literal["ml", "algo"]

    model_config = ConfigDict(
        from_attributes=True,
    )


class AlgorithmVersionDto(BaseModel):
    id: int
    uuid: UUID

    features: MlFeatures | list[dict[str, tp.Any]] = Field(...)
    management: RiskManagementParameters | None = None
    nodes: tp.Any | None = None

    created_at: tp.Optional[tp.Any] = None
    updated_at: tp.Optional[tp.Any] = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class AlgorithmCreate(AlgorithmBase):
    ...


class AlgorithmCreateResponse(AlgorithmBase):
    uuid: UUID
    algo_type: tp.Literal["ml", "algo"]


class AlgorithmDto(AlgorithmBase):
    uuid: UUID
    algo_type: tp.Literal["ml", "algo"]
    versions: list[AlgorithmVersionDto]

    model_config = ConfigDict(
        from_attributes=True,
    )
