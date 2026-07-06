# -*- coding: utf-8 -*-
"""
main.py — 主流程入口
用法:
    python main.py               正式執行(抓真實資料、寄信、更新儀表板)
    python main.py --mock        用合成資料跑完整流程(離線測試)
    python main.py --no-email    只更新儀表板,不寄信(dry-run 警報)
"""
import argparse
import sys

import config
import data_fetcher
import indicators
import alerts
import dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="長線佈局雷達")
    parser.add_argument("--mock", action="store_true", help="使用合成資料測試")
    parser.add_argument("--no-email", action="store_true", help="不寄送 Email")
    args = parser.parse_args()

    print("=== 長線佈局雷達 開始執行 ===")
    histories = data_fetcher.fetch_all(mock=args.mock)

    analyses = []
    for sym in config.TICKERS:
        if sym not in histories:
            continue
        a = indicators.analyze(sym, histories[sym])
        flag = "★買點" if a["buy_signal"] else ("△乖離達標" if a["dev_hit"] else "")
        print(f"[calc] {a['name']:<8} 現價 {a['price']:>10.2f} | "
              f"年線乖離 {a['dev200']:>+7.2f}% | 週RSI {a['weekly_rsi'] or 0:>5.1f} {flag}")
        analyses.append(a)

    triggered = alerts.process_alerts(analyses, dry_run=args.no_email)
    dashboard.render(analyses, triggered)
    print("=== 執行完成 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
