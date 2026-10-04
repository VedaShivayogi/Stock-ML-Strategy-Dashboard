import numpy as np
import pandas as pd


def _rsi(series, window=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    return 100 - (100 / (1 + rs))


def _macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def _bollinger_bands(series, window=20, num_std=2):
    ma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = ma + num_std * std
    lower = ma - num_std * std
    pct_b = (series - lower) / (upper - lower + 1e-10)
    return upper, lower, pct_b


def build_features(df):
    df = df.copy()
    close = df["Close"]
    volume = df.get("Volume", pd.Series(np.ones(len(df)), index=df.index))
    returns = close.pct_change()

    # Trend
    df["ma_20"] = close.rolling(20).mean()
    df["ma_50"] = close.rolling(50).mean()
    df["price_vs_ma20"] = close / df["ma_20"]
    df["price_vs_ma50"] = close / df["ma_50"]
    df["ma_cross"] = df["ma_20"] / df["ma_50"]

    # Returns
    df["return_1d"] = returns
    df["return_2d"] = returns.shift(1)
    df["return_5d"] = close.pct_change(5)
    df["return_10d"] = close.pct_change(10)

    # Volatility
    df["vol_10"] = returns.rolling(10).std()
    df["vol_20"] = returns.rolling(20).std()
    df["vol_ratio"] = df["vol_10"] / (df["vol_20"] + 1e-10)

    # Momentum
    df["rsi_14"] = _rsi(close, 14)
    df["rsi_7"] = _rsi(close, 7)
    macd_line, signal_line, histogram = _macd(close)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = histogram

    # Bollinger Bands
    _, _, df["bb_pct"] = _bollinger_bands(close)

    # Volume features
    df["volume_ma20"] = volume.rolling(20).mean()
    df["volume_ratio"] = volume / (df["volume_ma20"] + 1e-10)

    # Target: next day return
    df["target"] = returns.shift(-1)
    df = df.dropna()
    return df


FEATURE_COLS = [
    "ma_20", "ma_50", "price_vs_ma20", "price_vs_ma50", "ma_cross",
    "return_1d", "return_2d", "return_5d", "return_10d",
    "vol_10", "vol_20", "vol_ratio",
    "rsi_14", "rsi_7",
    "macd", "macd_signal", "macd_hist",
    "bb_pct", "volume_ratio",
]
