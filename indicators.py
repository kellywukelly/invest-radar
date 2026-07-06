# -*- coding: utf-8 -*-
"""
indicators.py — 技術指標計算
月線 / 年線移動平均、乖離率、週 RSI(Wilder 平滑)。
"""
import pandas as pd

import config


def sma(close: pd.Series, window: int) -> pd.Series:
    return close.rolling(window).mean()


def deviation_pct(price: float, ma_value: float) -> float:
    """乖離率(%) = (現價 - 均線) / 均線 * 100"""
    if ma_value is None or pd.isna(ma_value) or ma_value == 0:
        return float("nan")
    return (price - ma_value) / ma_value * 100.0


def weekly_rsi(close_daily: pd.Series, period: int = config.RSI_PERIOD) -> float:
    """
    以日線收盤重採樣為週線(週五收盤),計算 Wilder RSI。
    回傳最新一週的 RSI 值。
    """
    weekly = close_daily.resample("W-FRI").last().dropna()
    if len(weekly) < period + 1:
        return float("nan")
    delta = weekly.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100.0 - 100.0 / (1.0 + rs)
    return float(rsi.iloc[-1])


def analyze(symbol: str, df: pd.DataFrame) -> dict:
    """
    對單一標的產出完整分析結果 dict,供警報判斷與儀表板渲染共用。
    """
    cfg = config.TICKERS[symbol]
    close = df["Close"]
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2]) if len(close) >= 2 else price

    ma20 = sma(close, config.MA_MONTH).iloc[-1]
    ma200 = sma(close, config.MA_YEAR).iloc[-1]

    dev20 = deviation_pct(price, ma20)
    dev200 = deviation_pct(price, ma200)
    wrsi = weekly_rsi(close)

    dev_hit = (not pd.isna(dev200)) and dev200 <= cfg["dev_threshold"]
    rsi_hit = (not pd.isna(wrsi)) and wrsi <= cfg["rsi_threshold"]

    return {
        "symbol": symbol,
        "name": cfg["name"],
        "currency": cfg["currency"],
        "price": price,
        "day_change_pct": (price - prev) / prev * 100.0 if prev else 0.0,
        "ma20": None if pd.isna(ma20) else float(ma20),
        "ma200": None if pd.isna(ma200) else float(ma200),
        "dev20": None if pd.isna(dev20) else round(dev20, 2),
        "dev200": None if pd.isna(dev200) else round(dev200, 2),
        "weekly_rsi": None if pd.isna(wrsi) else round(wrsi, 1),
        "dev_threshold": cfg["dev_threshold"],
        "rsi_threshold": cfg["rsi_threshold"],
        "dev_hit": bool(dev_hit),
        "rsi_hit": bool(rsi_hit),
        "buy_signal": bool(dev_hit and rsi_hit),   # 雙重確認
        "alert_enabled": cfg["alert"],
        "spark": [round(float(v), 4) for v in close.tail(60).tolist()],
        "last_date": close.index[-1].strftime("%Y-%m-%d"),
    }
