import pandas as pd
import numpy as np

from GoAlgoMlPart.IfInference import IfInference
from GoAlgoMlPart.SimpleDataset import SimpleDataset

ticker = "YNDX"
timestamp = "1m"

IF_features_example = [
    {
        "type": "and",  # tp.Literal["and", "if"]
        "blocks": [
            {
                "type": "if",
                "feature": "anomaly",
                "condition": "high",  # tp.Literal["high", "low"]
                "param": "value",  # tp.Literal["value", "price_changing"]
            },
            {
                "type": "if",
                "feature": "anomal_rsi",
                "param": {
                    "period": 10,  # tp.Literal[2, 5, 10, 15, 20, 30, 50]
                    "value": 80,  # tp.Literal[50, 55, 60, 65, 70, 75, 80, 85, 90]
                },
            },
            {
                "type": "if",
                "feature": "out_of_limits",
                "condition": "high",  # tp.Literal["high", "low"]
                "param": {
                    "feature_name": "close",  # tp.Literal["close", "high", "low", "open", "value", "volume", "green_candles_ratio", "red_candles_ratio", "price_changing"]
                    "limit": 277.7,  # float
                    "period": None,  # int | None
                },
            },
            {
                "type": "if",
                "feature": "average_cross",
                "param": {
                    "average_type": "ema",  # tp.Literal["ema", "sma", "cma"],
                    "feature_name": "close",  # tp.Literal["close", "high", "low", "open", "value", "volume", "green_candles_ratio", "red_candles_ratio"]
                    "n_fast": 10,  # tp.Literal[2, 5, 10, 15, 50, 100]
                    "n_slow": 100,  # tp.Literal[2, 5, 10, 15, 50, 100]
                },
            },
            {
                "type": "if",
                "feature": "macd_cross",
                "param": {
                    "feature_name": "close",  # tp.Literal["close", "high", "low", "open", "value", "volume", "green_candles_ratio", "red_candles_ratio"]
                    "n_fast": 5,  # tp.Literal[2, 5, 10, 15, 50, 100]
                    "n_slow": 50,  # tp.Literal[2, 5, 10, 15, 50, 100]
                },
            },
        ],
    },
    {
        "type": "and",
        "blocks": [
            {
                "type": "if",
                "feature": "macd_cross",
                "param": {
                    "feature_name": "close",  # tp.Literal["close", "high", "low", "open", "value", "volume", "green_candles_ratio", "red_candles_ratio"]
                    "n_fast": 50,
                    "n_slow": 100,
                },
            }
        ],
    },
]

rsi_periods = [2, 5, 10, 15, 20, 30, 50]

candles_periods = [2, 5, 7, 10, 14, 21, 30, 100]

average_periods = [2, 5, 10, 15, 50, 100]

average_features = ["close", "high", "low", "open", "value", "volume"]

features = {
    "lags": False,
    "cma": {"features": average_features},
    "sma": {"features": average_features, "period": average_periods},
    "ema": {"features": average_features, "period": average_periods},
    "green_candles_ratio": {"period": candles_periods},
    "red_candles_ratio": {"period": candles_periods},
    "rsi": {"period": rsi_periods},
    "macd": False,
    "bollinger": False,
    "time_features": False,
}

test_df = SimpleDataset.create_dataset(
    features=features,
    ticker=ticker,
    timeframe=timestamp,
    candles=5000,
)

if_model = IfInference(
    IF_features=IF_features_example,
    ticker=ticker,
    timestamp=timestamp,
)

test_signals = if_model.predict_candles_dataframe(test_df)

print(f"test_df size: {len(test_df)}, test_signals size: {len(test_signals)}")

last_100_candles, signals = if_model.predict_n_last_candles(candles=100)

print(last_100_candles.date.max(), len(signals), signals.sum())

last_1_candles, signals = if_model.predict_one_last_candle()

print(last_1_candles.date.max(), signals)
