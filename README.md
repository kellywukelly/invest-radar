# 長線佈局雷達

台股 ETF(0050 / 0056 / 00878 / 00919)+ TSLA 的全自動長線買點追蹤工具。

- 資料來源:Yahoo Finance(`yfinance`,免金鑰)
- 買點邏輯:**年線(200日均)負乖離** + **週 RSI ≤ 35** 雙重確認
- 儀表板:靜態 HTML,由 GitHub Pages 發布
- 警報:Gmail SMTP 寄送加碼通知,7 天冷卻避免重複轟炸
- 排程:GitHub Actions,台股收盤後(台北 14:10)與美股收盤後(台北 05:10)各跑一次

## 專案結構

```
config.py           標的清單、門檻、Email 設定(所有可調參數都在這)
data_fetcher.py     抓取歷史日線,含 --mock 合成資料模式
indicators.py       均線 / 乖離率 / 週 RSI 計算與訊號判斷
alerts.py           警報冷卻管理 + Gmail 寄信
dashboard.py        渲染 docs/index.html
main.py             主流程入口
templates/          儀表板模板
.github/workflows/  每日排程
```

## 本機測試

```bash
pip install -r requirements.txt
python main.py --mock         # 離線合成資料,測完整流程(不寄信可加 --no-email)
python main.py --no-email     # 真實資料,只更新儀表板
python main.py                # 正式執行
```

本機要測寄信,先設定環境變數(Windows PowerShell):

```powershell
$env:GMAIL_USER="你的帳號@gmail.com"
$env:GMAIL_APP_PASSWORD="16碼應用程式密碼"
$env:ALERT_TO="收件人@gmail.com"
python main.py
```

## Gmail 應用程式密碼申請

1. Google 帳戶 → 安全性 → 開啟「兩步驟驗證」(必須先開)
2. 搜尋「應用程式密碼」→ 建立,名稱隨意(如 invest-radar)
3. 複製產生的 16 碼密碼(空格可留可去),這就是 `GMAIL_APP_PASSWORD`

## GitHub 部署步驟

1. 建立新 repo(可設 private,Pages 需 public 或付費方案),把整個資料夾推上去
2. **Settings → Secrets and variables → Actions → New repository secret**,新增三個:
   - `GMAIL_USER`
   - `GMAIL_APP_PASSWORD`
   - `ALERT_TO`
3. **Settings → Pages** → Source 選 `Deploy from a branch`,Branch 選 `main` / `/docs`
4. **Actions** 頁籤 → 選「長線佈局雷達每日更新」→ `Run workflow` 手動跑一次驗證
5. 幾分鐘後開 `https://你的帳號.github.io/repo名稱/` 就能看到儀表板

## 調整門檻

全部在 `config.py` 的 `TICKERS`:

- `dev_threshold`:年線乖離門檻(0050 預設 -10%、TSLA 預設 -25%)
- `rsi_threshold`:週 RSI 門檻(預設 35)
- `alert`:該檔是否寄信(預設僅 0050 與 TSLA 開啟)

## 免責聲明

訊號僅代表統計上的相對低檔,不構成投資建議,請搭配自身資金配置紀律使用。
