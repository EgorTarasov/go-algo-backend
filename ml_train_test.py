from GoAlgoMlPart.TrainModel import TrainModel
from GoAlgoMlPart.Backtest import Backtest
from GoAlgoMlPart.ModelInference import ModelInference

tick = "YNDX"
period = "1m"
train_candles = 10_000
backtest_candles = 1_000

features = {
    "lags": {"features": ["open", "close", "target"], "period": [1, 2, 3]},
    "cma": {"features": ["open", "close", "volume"]},
    "sma": {"features": ["open", "close", "volume"], "period": [2, 3, 4]},
    "ema": {"features": ["open", "close", "volume"], "period": [2, 3, 4]},
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
    "model": "lightgbm",
}  # выбор один из 'lightgbm'


train_model = TrainModel(
    features,
    tick,
    period,
    candles=train_candles,
    model_id="12345678",
)
features = train_model.train()  # возвращает новый features с порогом

management_features = {
    "balance": 100_000,
    "max_balance_for_trading": 200_000,
    "min_balance_for_trading": 0,
    "part_of_balance_for_buy": 0.3,
    "sum_for_buy_rur": None,
    "sum_for_buy_num": None,
    "part_of_balance_for_sell": None,
    "sum_for_sell_rur": None,
    "sum_for_sell_num": None,
    "sell_all": True,
}

backtest = Backtest(
    features,
    balance=management_features["balance"],
    max_balance_for_trading=management_features["max_balance_for_trading"],
    min_balance_for_trading=management_features["min_balance_for_trading"],
    part_of_balance_for_buy=management_features["part_of_balance_for_buy"],
    period=period,
    sum_for_buy_rur=management_features["sum_for_buy_rur"],
    sum_for_buy_num=management_features["sum_for_buy_num"],
    part_of_balance_for_sell=management_features["part_of_balance_for_sell"],
    sum_for_sell_rur=management_features["sum_for_sell_rur"],
    sum_for_sell_num=management_features["sum_for_sell_num"],
    sell_all=management_features["sell_all"],
)

balance, year_income = backtest.do_backtest(tick, period, backtest_candles)
print(balance, year_income)

inference = ModelInference(
    features=features,
    ticker=tick,
    model_id="12345678",
    api_data="amogus",
    timeframe=period,

)

last_candle, signal = inference.get_pred_one_candle()
print(last_candle)
print(signal)
