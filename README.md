# MoodRing 市場情緒指標

> 透過多維度情緒指標分析美股與台股市場方向的每日儀表板

**[美股儀表板 (US)](https://wenyuchiou.github.io/moodring/)** · **[台股儀表板 (TW)](https://wenyuchiou.github.io/moodring/tw.html)**

---

## 什麼是 MoodRing？

MoodRing 是一個逆向情緒指標系統，每日將市場衍生信號整合為 0–100 的情緒分數：

- **分數 < 30**：市場情緒悲觀（零售投資人恐慌） → 歷史上後續報酬高於平均
- **分數 30–70**：中性區間
- **分數 > 70**：市場情緒樂觀（零售投資人貪婪） → 歷史上後續報酬低於平均

情緒分數基於 252 個交易日滾動 Z-score 標準化，不使用任何未來資料（no lookahead bias）。

---

## 功能特色

### 美股情緒分析
- **VIX 恐慌指數**：市場隱含波動率
- **Put/Call Ratio**：選擇權買賣比率（零售情緒代理指標）
- **信用利差（HY Spread）**：高收益債與美國公債利差
- **RSI 超買超賣**：S&P 500 技術指標
- **保證金餘額變化**：融資使用程度

### 台股情緒分析
- **加權指數（TAIEX）**：台灣大盤走勢
- **融資餘額變化**：散戶槓桿參與程度
- **融券餘額變化**：市場做空強度
- **外資買賣超**：外國機構資金流向
- **MSCI 台灣 ETF（EWT）**：境外台股情緒參考

### 歷史走勢與記憶類比
- 情緒分數歷史折線圖，疊加加權指數走勢
- **記憶類比（Memory Analogy）**：自動搜尋歷史上情緒最相似的日期，顯示當時後續市場表現
- 分位數條件報酬表：依情緒分位數統計歷史勝率與平均報酬

### 每日自動更新
- 由 GitHub Actions 排程執行，無需人工介入
- 資料寫入 `docs/dashboard_data.json`，靜態網頁直接讀取

---

## 儀表板連結

| 市場 | 連結 |
|------|------|
| 美股（US） | https://wenyuchiou.github.io/moodring/ |
| 台股（TW） | https://wenyuchiou.github.io/moodring/tw.html |

---

## 技術架構

```
Python 資料管線
    ↓ yfinance / FinMind API 拉取原始數據
    ↓ 計算情緒分數（Z-score 標準化 + 加權合成）
    ↓ 記憶類比搜尋（餘弦相似度）
    ↓ 輸出 docs/dashboard_data.json
GitHub Pages 靜態儀表板
    ↓ 讀取 JSON
    ↓ Chart.js 渲染折線圖、分位數表、記憶類比卡片
```

**主要技術元件：**
- `Python 3.x`：資料處理與指標計算
- `yfinance`：美股市場數據（VIX、S&P 500、HY Spread ETF 等）
- `FinMind`：台股市場數據（融資融券、外資買賣超）
- `GitHub Actions`：每日自動排程執行
- `GitHub Pages`：靜態網頁托管
- `Chart.js`：互動式圖表

---

## 每日排程

| 任務 | 排程時間（台北）| 說明 |
|------|----------------|------|
| 美股更新 | 每日 22:00 | 美股收盤後（美東 10:00 AM）拉取當日數據 |
| 台股更新 | 每日 09:30 | 亞股開盤後確認前日收盤數據完整性 |
| **信號重新校準** | **每週六 14:00** | 自動偵測 IC 衰退並重新最佳化信號權重 |

排程定義於 `.github/workflows/` 內的 GitHub Actions YAML 檔。

---

## 自動重新校準機制（Auto-Recalibration）

### 什麼是 IC 衰退？

MoodRing 使用**信息係數（IC, Information Coefficient）**衡量情緒分數與未來 20 日報酬的 Spearman 相關性。當市場進入不同的走勢形態（如趨勢市轉震盪市），原有信號權重的預測力會下降，稱為 IC 衰退。

### 重新校準策略

情緒分數由三個子信號加權合成：

| 子信號 | 預設權重 | 說明 |
|--------|---------|------|
| RSI-14 | 33% | 超買超賣（直接 0-100） |
| vs 52 週高點 | 33% | 距歷史高點距離（對比指標） |
| 20 日動能 | 33% | 近期趨勢動能 |

當某市場 IC 低於閾值（`|IC| < 0.10` = 訊號差、`< 0.15` = 訊號弱），系統會：

1. **拉取 2 年歷史價格**（yfinance）
2. **重新計算**每日三個子信號值
3. **格點搜尋**最佳化權重組合（10 種權重比例 × 4 × 4 × 4 種映射參數 = 640 組候選）
4. 以 Walk-Forward 驗證（前75%訓練、後25%驗樣本外）評估新參數：若樣本外（OOS）IC 改善則**自動採用**；當驗證集過小時，退回要求樣本內 IC 提升超過 10% 的備用判準。結果寫入 `data/calibration_params.json`
5. **記錄事件**至 `data/recalibration_log.json`
6. 下次 `daily_update.py` 執行時**自動套用**新權重

### 校準狀態

儀表板的 **Signal Health** 區塊會顯示：
- 當前信號健康度（Good / Warning / Poor）
- 若已重新校準：套用日期、新權重比例、IC 改善幅度
- 系統整體健康度 + 最後重新校準時間

### 手動觸發

```bash
# 對所有健康狀況差的市場執行重新校準
python src/recalibrate.py

# 指定市場
python src/recalibrate.py --markets us tw jp

# 強制重新校準（忽略健康狀態）
python src/recalibrate.py --force

# 查看當前校準狀態
python src/recalibrate.py --status
```

### 相關檔案

| 檔案 | 說明 |
|------|------|
| `src/recalibrate.py` | 重新校準引擎主程式 |
| `data/calibration_params.json` | 各市場當前最佳化參數 |
| `data/recalibration_log.json` | 歷次校準事件紀錄 |
| `.github/workflows/monthly-recalibrate.yml` | 每月1日自動觸發排程 |

---

## 資料來源

- **yfinance**：S&P 500、VIX、HY Spread（HYG/LQD）、Put/Call Ratio 代理指標
- **FinMind**：台股融資餘額、融券餘額、外資買賣超（公開市場數據）
- **公開市場數據**：TAIEX（加權指數）、EWT（MSCI 台灣 ETF）

---

## 本地執行

```bash
# 安裝相依套件
pip install yfinance pandas numpy scipy FinMind requests tqdm

# 執行全市場數據更新（US / TW / JP / KR / EU）
python src/daily_update.py

# 僅更新特定市場
python src/daily_update.py --us --tw

# 重建儀表板 JSON
python src/rebuild_dashboard_daily.py

# 執行信號重新校準（自動偵測 IC 衰退）
python src/recalibrate.py

# 本地預覽儀表板（開啟 docs/index.html）
```

---

## 免責聲明

本專案所有資料、指標與分析結果均為**歷史觀察與統計呈現**，不構成任何投資建議或預測保證。

- 歷史報酬不代表未來績效
- 情緒指標反映過去統計規律，不保證未來相同結果
- 本儀表板僅供研究與學習用途，不應作為投資決策依據
- 投資有風險，請自行評估風險承受能力並諮詢專業財務顧問

---

*MoodRing — 市場情緒的溫度計，不是水晶球。*
