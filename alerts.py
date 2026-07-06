# -*- coding: utf-8 -*-
"""
alerts.py — 買點警報判斷 + Gmail SMTP 寄信
狀態記錄在 alert_state.json,冷卻期內不重複寄送同一標的。
"""
import json
import os
import smtplib
import ssl
from datetime import datetime, timedelta
from email.header import Header
from email.mime.text import MIMEText

import config


# ------------------------- 狀態管理 -------------------------

def _load_state() -> dict:
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_state(state: dict) -> None:
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _in_cooldown(state: dict, symbol: str) -> bool:
    last = state.get(symbol, {}).get("last_alert")
    if not last:
        return False
    last_dt = datetime.strptime(last, "%Y-%m-%d")
    return datetime.now() - last_dt < timedelta(days=config.ALERT_COOLDOWN_DAYS)


# ------------------------- 警報主流程 -------------------------

def process_alerts(analyses: list, dry_run: bool = False) -> list:
    """
    檢查所有標的,對「啟用警報 + 雙重確認成立 + 不在冷卻期」者寄信。
    回傳實際觸發的標的清單。
    """
    state = _load_state()
    triggered = []

    for a in analyses:
        if not (a["alert_enabled"] and a["buy_signal"]):
            continue
        if _in_cooldown(state, a["symbol"]):
            print(f"[alert] {a['symbol']} 訊號成立,但仍在 "
                  f"{config.ALERT_COOLDOWN_DAYS} 天冷卻期內,略過")
            continue
        triggered.append(a)

    if triggered:
        if dry_run:
            print(f"[alert] (dry-run) 將寄送警報:{[a['symbol'] for a in triggered]}")
        else:
            _send_email(triggered)
            today = datetime.now().strftime("%Y-%m-%d")
            for a in triggered:
                state[a["symbol"]] = {"last_alert": today}
            _save_state(state)
    else:
        print("[alert] 本次無買點訊號觸發")

    return triggered


# ------------------------- Email -------------------------

def _build_body(triggered: list) -> str:
    lines = [
        "長線買點雙重確認成立,以下標的進入加碼區:",
        "",
    ]
    for a in triggered:
        lines += [
            f"■ {a['name']} ({a['symbol']})",
            f"   現價:{a['currency']}{a['price']:,.2f}({a['last_date']})",
            f"   年線乖離:{a['dev200']:+.2f}%(門檻 {a['dev_threshold']:+.1f}%)",
            f"   週 RSI:{a['weekly_rsi']:.1f}(門檻 {a['rsi_threshold']:.0f})",
            f"   月線乖離:{a['dev20']:+.2f}%",
            "",
        ]
    lines += [
        "提醒:訊號僅代表統計上的相對低檔,請搭配資金配置紀律分批佈局。",
        f"(同一標的 {config.ALERT_COOLDOWN_DAYS} 天內不重複通知)",
    ]
    return "\n".join(lines)


def _send_email(triggered: list) -> None:
    if not (config.GMAIL_USER and config.GMAIL_APP_PASSWORD):
        print("[alert] 未設定 GMAIL_USER / GMAIL_APP_PASSWORD 環境變數,無法寄信")
        return

    names = "、".join(a["name"] for a in triggered)
    msg = MIMEText(_build_body(triggered), "plain", "utf-8")
    msg["Subject"] = Header(f"【加碼訊號】{names} 進入長線買點", "utf-8")
    msg["From"] = config.GMAIL_USER
    msg["To"] = config.ALERT_TO

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
        server.sendmail(config.GMAIL_USER, [config.ALERT_TO], msg.as_string())
    print(f"[alert] 已寄出警報:{names} → {config.ALERT_TO}")
