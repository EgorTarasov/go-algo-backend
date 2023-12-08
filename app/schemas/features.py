"""
features = {
'lags': {'features': ['open', 'close', 'high', 'low', 'value', 'volume', 'target'],
                     'period': [1, 2, 3, 4, 10, 14, 20, 50, 100]},

            'cma': {'features': ['open', 'close', 'high', 'low', 'value', 'volume']},

            'sma': {'features': ['open', 'close', 'high', 'low', 'value', 'volume'],
                    'period': [2, 3, 4, 10, 14, 20, 50, 100]},

            'ema': {'features': ['open', 'close', 'high', 'low', 'value', 'volume'],
                    'period': [2, 3, 4, 10, 14, 20, 50, 100]},

            'green_candles_ratio': {'period': [2, 3, 4, 10, 14, 20, 50, 100]},

            'red_candles_ratio': {'period': [2, 3, 4, 10, 14, 20, 50, 100]},

            'rsi': {'period': [2, 3, 4, 10, 14, 20, 50, 100]},

            'macd': {'period': [(12, 26)]}, # только (12, 26)

            'bollinger': {'period': 20, # выбор один из 2, 3, 4, 10, 14, 20, 50, 100
                          'degree_of_lift': 2},

            'time_features': {'month':True,
                              'week':True,
                              'day_of_month':True,
                              'day_of_week':True,
                              'hour':True,
                              'minute': True},
            'model': 'catboost'}

"""

import typing as tp
from pydantic import BaseModel, ConfigDict

Features = tp.Literal[None, "open", "close", "high", "low", "value", "volume", "target"]
Period = tp.Literal[None, 1, 2, 3, 4, 10, 14, 20, 50, 100]
MacdPeriod = tp.Literal[None, 12, 26]
Model = tp.Literal["lightgbm", "catboost"]


class Lags(BaseModel):
    features: list[Features] | None
    period: list[Period] | None


class Cma(BaseModel):
    features: list[Features] | None


class Sma(BaseModel):
    features: list[Features] | None
    period: list[Period] | None


class Ema(BaseModel):
    features: list[Features] | None
    period: list[Period] | None


class GreenCandlesRatio(BaseModel):
    period: list[Period] | None


class RedCandlesRatio(BaseModel):
    period: list[Period] | None


class Rsi(BaseModel):
    period: list[Period] | None


class Macd(BaseModel):
    period: list[list[MacdPeriod]] | None


class Bollinger(BaseModel):
    period: Period | None
    degree_of_lift: int | None


class TimeFeatures(BaseModel):
    month: bool
    week: bool
    day_of_month: bool
    day_of_week: bool
    hour: bool
    minute: bool


class MlFeatures(BaseModel):
    lags: Lags | None = None
    cma: Cma | None = None
    sma: Sma | None = None
    ema: Ema | None = None
    green_candles_ratio: GreenCandlesRatio | None = None
    red_candles_ratio: RedCandlesRatio | None = None
    rsi: Rsi | bool = False
    macd: Macd | bool = False
    bollinger: Bollinger | bool = False
    time_features: TimeFeatures | None = None
    model: Model
    order: list[str] | None = None
    threshold: float | None = None

    model_config = ConfigDict(from_attributes=True)
