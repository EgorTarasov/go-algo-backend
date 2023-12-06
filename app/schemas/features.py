"""
eatures = {
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
from pydantic import BaseModel

Features = tp.Literal["open", "close", "high", "low", "value", "volume", "target"]
Period = tp.Literal[1, 2, 3, 4, 10, 14, 20, 50, 100]
MacdPeriod = tp.Literal[12, 26]
Model = tp.Literal["lightgbm", "catboost"]


class Lags(BaseModel):
    features: list[Features]
    period: list[Period]


class Cma(BaseModel):
    features: list[Features]


class Sma(BaseModel):
    features: list[Features]
    period: list[Period]


class Ema(BaseModel):
    features: list[Features]
    period: list[Period]


class GreenCandlesRatio(BaseModel):
    period: list[Period]


class RedCandlesRatio(BaseModel):
    period: list[Period]


class Rsi(BaseModel):
    period: list[Period]


class Macd(BaseModel):
    period: list[tuple[MacdPeriod, MacdPeriod]] = [(12, 26)]


class Bollinger(BaseModel):
    period: Period
    degree_of_lift: int


class TimeFeatures(BaseModel):
    month: bool
    week: bool
    day_of_month: bool
    day_of_week: bool
    hour: bool
    minute: bool


class MlFeatures(BaseModel):
    lags: Lags
    cma: Cma
    sma: Sma
    ema: Ema
    green_candles_ratio: GreenCandlesRatio
    red_candles_ratio: RedCandlesRatio
    rsi: Rsi | bool = False
    macd: Macd | bool = False
    bollinger: Bollinger | bool = False
    time_features: TimeFeatures
    model: Model
