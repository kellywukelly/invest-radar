# -*- coding: utf-8 -*-
"""
data_fetcher.py — 透過 yfinance 抓取歷史日線與最新報價
提供 mock 模式,方便在沒有網路 / 測試流程時使用合成資料。
"""
import numpy as np
import pandas as pd

import config


def fetch_history(symbol: str, period: str = config.HISTORY_PERIOD) -> pd.DataFrame:
    """抓取單一標的的歷史日線 (OHLCV),index 為 DatetimeIndex。"""
    import yfinance as yf

    df = yf.Ticker(symbol).history(period=period, interval="1d", auto_adjust=True)
    if df is None or df.empty:
        raise RuntimeError(f"{symbol}: yfinance 回傳空資料,請檢查代號或網路")
    df = df.dropna(subset=["Close"])
    # 移除時區,統一後續 resample 行為
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


def fetch_all(mock: bool = False) -> dict:
    """抓取 config.TICKERS 中所有標的,回傳 {symbol: DataFrame}。"""
    if mock:
        return {sym: _mock_history(sym) for sym in config.TICKERS}

    result = {}
    errors = []
    for sym in config.TICKERS:
        try:
            result[sym] = fetch_history(sym)
            print(f"[data] {sym}: {len(result[sym])} 筆日線,最新收盤 "
                  f"{result[sym]['Close'].iloc[-1]:.2f}")
        except Exception as e:  # 單一標的失敗不中斷整體流程
            errors.append(f"{sym}: {e}")
    if errors:
        print("[data] 以下標的抓取失敗:\n  " + "\n  ".join(errors))
    if not result:
        raise RuntimeError("所有標的皆抓取失敗,終止執行")
    return result


# ------------------------- mock -------------------------

def _mock_history(symbol: str, days: int = 500) -> pd.DataFrame:
    """產生擬真的隨機漫步日線,供 --mock 測試用。"""
    rng = np.random.default_rng(abs(hash(symbol)) % (2**32))
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    base = 100.0 if symbol.endswith(".TW") else 250.0
    rets = rng.normal(0.0002, 0.018, days)
    # 讓 TSLA 的 mock 走出深跌,方便測試警報路徑
    if symbol == "TSLA":
        rets[-60:] -= 0.012
    close = base * np.exp(np.cumsum(rets))
    df = pd.DataFrame({
        "Open": close * (1 + rng.normal(0, 0.003, days)),
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Volume": rng.integers(1e6, 5e7, days),
    }, index=idx)
    return df
