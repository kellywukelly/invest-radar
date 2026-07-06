# -*- coding: utf-8 -*-
"""
dashboard.py — 將分析結果渲染為靜態 HTML 儀表板 (docs/index.html)
純靜態輸出,GitHub Pages 直接發布,無需後端伺服器。
"""
import os
from datetime import datetime, timezone, timedelta

from jinja2 import Environment, FileSystemLoader

import config

TPE = timezone(timedelta(hours=8))


def _sparkline_points(values: list, w: int = 200, h: int = 44, pad: int = 3) -> str:
    """把收盤序列轉成 SVG polyline 的 points 字串。"""
    if not values or len(values) < 2:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = pad + i * (w - 2 * pad) / (n - 1)
        y = pad + (hi - v) * (h - 2 * pad) / span
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def _gauge_pos(dev: float, lo: float = -30.0, hi: float = 30.0) -> float:
    """把年線乖離率映射到 0~100% 的水位計位置。"""
    if dev is None:
        return 50.0
    clamped = max(lo, min(hi, dev))
    return (clamped - lo) / (hi - lo) * 100.0


def render(analyses: list, triggered: list) -> str:
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=True,
    )
    tpl = env.get_template("dashboard.html")

    cards = []
    for a in analyses:
        c = dict(a)
        c["spark_points"] = _sparkline_points(a["spark"])
        c["spark_up"] = a["spark"][-1] >= a["spark"][0] if a["spark"] else True
        c["gauge_pos"] = round(_gauge_pos(a["dev200"]), 2)
        c["gauge_threshold_pos"] = round(_gauge_pos(a["dev_threshold"]), 2)
        cards.append(c)

    html = tpl.render(
        cards=cards,
        signal_count=sum(1 for a in analyses if a["buy_signal"]),
        triggered_names=[a["name"] for a in triggered],
        updated_at=datetime.now(TPE).strftime("%Y-%m-%d %H:%M"),
    )
    out = config.DASHBOARD_OUT
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[dashboard] 已輸出 {out}")
    return out
