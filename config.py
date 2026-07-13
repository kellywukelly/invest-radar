# -*- coding: utf-8 -*-
"""
config.py — 全域設定
所有可調參數集中在此,改門檻不需要動任何邏輯程式碼。
"""
import os

# ---------------------------------------------------------------
# 追蹤標的
#   dev_threshold : 年線(200日均)負乖離門檻(%),小於等於此值視為便宜
#   rsi_threshold : 週 RSI 門檻,小於等於此值視為賣壓釋放
#   alert         : 是否啟用 Email 買點警報
# ---------------------------------------------------------------
TICKERS = {
    "0050.TW": {
        "name": "元大台灣50",
        "currency": "NT$",
        "dev_threshold": -10.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "0056.TW": {
        "name": "元大高股息",
        "currency": "NT$",
        "dev_threshold": -10.0,
        "rsi_threshold": 35.0,
        "alert": False,   # 依需求僅 0050 與 TSLA 發警報,想開啟改 True 即可
    },
    "00878.TW": {
        "name": "國泰永續高股息",
        "currency": "NT$",
        "dev_threshold": -10.0,
        "rsi_threshold": 35.0,
        "alert": False,
    },
    "00919.TW": {
        "name": "群益台灣精選高息",
        "currency": "NT$",
        "dev_threshold": -10.0,
        "rsi_threshold": 35.0,
        "alert": False,
    },
    "TSLA": {
        "name": "Tesla",
        "currency": "US$",
        "dev_threshold": -25.0,   # TSLA 波動大,門檻放深
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "MU": {
        "name": "美光 Micron",
        "currency": "US$",
        "dev_threshold": -25.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "SPCX": {
        "name": "SPCX",
        "currency": "US$",
        "dev_threshold": -20.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "NOK": {
        "name": "諾基亞 Nokia",
        "currency": "US$",
        "dev_threshold": -15.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "MRVL": {
        "name": "邁威爾 Marvell",
        "currency": "US$",
        "dev_threshold": -25.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
    "DELL": {
        "name": "戴爾 Dell",
        "currency": "US$",
        "dev_threshold": -20.0,
        "rsi_threshold": 35.0,
        "alert": True,
    },
}

# 均線視窗
MA_MONTH = 20      # 月線(20 個交易日)
MA_YEAR = 200      # 年線(200 個交易日)
RSI_PERIOD = 14    # 週 RSI 週期

# 歷史資料長度(需大於 200 日 + RSI 暖機)
HISTORY_PERIOD = "2y"

# 同一標的重複警報的冷卻天數(避免連續下跌天天寄信)
ALERT_COOLDOWN_DAYS = 7

# 輸出路徑(GitHub Pages 建議用 /docs 目錄)
DASHBOARD_OUT = os.path.join("docs", "index.html")
STATE_FILE = "alert_state.json"

# ---------------------------------------------------------------
# Email 設定 — 一律從環境變數讀取,絕不把密碼寫進程式碼
# 本機測試:先 set GMAIL_USER=... 等環境變數
# GitHub Actions:到 repo Settings → Secrets 設定
# ---------------------------------------------------------------
GMAIL_USER = os.environ.get("GMAIL_USER", "")           # 寄件 Gmail 帳號
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")  # Gmail 應用程式密碼
ALERT_TO = os.environ.get("ALERT_TO", GMAIL_USER)        # 收件人,預設寄給自己
