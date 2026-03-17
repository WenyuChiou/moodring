# GRISI Implementation Plan

> **v3.0 — Backtest-First, Adaptive Scoring (2026-03-16)**
> Core change: 先用歷史數據證明基底指標有效，再疊加社群/動態權重。每一步都有數字說話。

**每一步都有驗證，不通過不能進下一步。**

---

## Phase 0: 數據源可行性驗證 (Day 1-2)

### Step 0.1: yfinance 拉取測試
```python
# 驗證這些 ticker 都能正常拉到數據
tickers = {
    "US_index": "SPY",
    "US_tech": "QQQ",
    "US_fear": "^VIX",
    "TW_index": "^TWII",       # 台灣加權指數
    "TW_tsmc": "2330.TW",      # 台積電
    "FX_jpyusd": "USDJPY=X",
    "FX_dollar": "DX-Y.NYB",   # DXY
    "US_10y": "^TNX",          # 10年期殖利率
}
```
**驗證**: 每個 ticker 都能拿到最近 90 天的 OHLCV？✅/❌

### Step 0.2: TWSE 台灣數據測試
```
需要拉到:
1. 融資餘額 (每日) → TWSE 公開資訊觀測站
2. 三大法人買賣超 (每日) → TWSE OpenData API
3. 當沖比率 (每日) → TWSE
```
**驗證**: 能拿到最近 30 天的融資餘額和法人買賣超？✅/❌

### Step 0.3: AAII 美國散戶情緒測試
```
需要拉到:
1. AAII Bull/Bear/Neutral % (每週更新)
來源: https://www.aaii.com/sentimentsurvey → 可能需要 scrape
替代: FRED 有 AAII 數據? 或第三方 API?
```
**驗證**: 能拿到最近 12 週的 AAII 數據？✅/❌

### Step 0.4: FRED 宏觀數據測試
```python
# FRED API (free key: https://fred.stlouisfed.org/docs/api/api_key.html)
series = {
    "fed_rate": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "us10y": "GS10",
    "unemployment": "UNRATE",
}
```
**驗證**: FRED API key 申請成功 + 能拿到數據？✅/❌

### Step 0.5: 技術指標計算測試
```python
# 用 pandas_ta 或手算
import pandas_ta as ta
df.ta.rsi(length=14)
df.ta.macd()
df.ta.bbands()
df.ta.sma(length=5)
df.ta.sma(length=20)
df.ta.sma(length=60)
```
**驗證**: 能對 SPY 和 ^TWII 算出完整技術指標？✅/❌

### 🚪 Gate 0 驗證標準
```
所有 5 個 Step 都通過 → 進入 Phase 1
任何一個失敗 → 找替代數據源或調整範圍
```

---

## Phase 1: 確定性評分引擎 (Day 3-5)

### Step 1.1: 設計散戶評分公式

**美國散戶評分 (US Retail Score 0-100)**:
```python
def us_retail_score(data):
    components = {
        # AAII: bull% 高 = 散戶樂觀 → 高分
        "aaii_bull": normalize(data["aaii_bull_pct"], min=20, max=60),  # 歷史範圍

        # Put/Call Ratio: 低 = 散戶樂觀 (買 call 多) → 高分
        "put_call_inv": normalize(1/data["put_call_ratio"], min=0.7, max=1.5),

        # VIX: 低 = 散戶不怕 → 高分
        "vix_inv": normalize(1/data["vix"], min=1/35, max=1/12),

        # SPY 相對位置: 接近 ATH = 散戶樂觀
        "spy_vs_high": normalize(data["spy_close"] / data["spy_52w_high"], min=0.8, max=1.0),
    }

    weights = {"aaii_bull": 0.35, "put_call_inv": 0.25, "vix_inv": 0.20, "spy_vs_high": 0.20}
    return weighted_average(components, weights) * 100
```

**台灣散戶評分 (TW Retail Score 0-100)**:
```python
def tw_retail_score(data):
    components = {
        # 融資餘額變化率: 增加 = 散戶在追 → 高分
        "margin_change": normalize(data["margin_balance_pct_change_20d"], min=-5, max=10),

        # 散戶買賣超 (法人 = 外資+投信+自營, 剩下 = 散戶): 買超 = 高分
        "retail_flow": normalize(data["retail_net_buy_5d_avg"], min=-5e9, max=5e9),

        # 當沖比率: 高 = 投機熱 → 高分
        "daytrade": normalize(data["daytrade_ratio"], min=0.15, max=0.45),

        # 台積電相對位置
        "tsmc_vs_high": normalize(data["tsmc_close"] / data["tsmc_52w_high"], min=0.7, max=1.0),
    }

    weights = {"margin_change": 0.35, "retail_flow": 0.30, "daytrade": 0.15, "tsmc_vs_high": 0.20}
    return weighted_average(components, weights) * 100
```

**驗證**: 手動驗算 3 個日期的分數，看是否合理 ✅/❌

### Step 1.2: 跨市場分歧度

```python
def divergence_score(us_score, tw_score):
    return abs(us_score - tw_score)
    # 0 = 完全一致, 100 = 最大分歧
```

### Step 1.3: 歷史模式匹配

```python
from scipy.spatial.distance import cosine

def find_similar_historical(current_vector, history_db, top_k=3):
    """
    current_vector: [us_score, tw_score]
    history_db: {date: [us_score, tw_score]}
    """
    similarities = []
    for date, hist_vector in history_db.items():
        sim = 1 - cosine(current_vector, hist_vector)
        similarities.append((date, sim))
    return sorted(similarities, key=lambda x: -x[1])[:top_k]
```

### 🚪 Gate 1 驗證標準
```
用 2024 年數據跑分數:
- 2024-08-05 (Yen carry crash): TW score 應該 < 30 ✅/❌
- 2024-07-10 (台積電千元): TW score 應該 > 70 ✅/❌
- 2024-10 (美國大選前): US score 應該 40-60 (觀望) ✅/❌

如果分數不符合已知事件 → 調整公式權重
```

---

## Phase 1B: 歷史回測驗證 (Day 5-8) ⭐ NEW

> **核心原則**: 不能回測的策略就是在講故事。Phase 1 的公式必須通過歷史數據驗證才能繼續。

### Step 1B.1: 下載歷史數據 (2015-2025)

```python
# 需要收集的歷史數據
HISTORICAL_DATA = {
    'US': {
        'aaii_bull_pct': 'AAII CSV (1987-present)',      # aaii.com/sentimentsurvey
        'put_call_ratio': 'CBOE (2006-present)',         # cboe.com
        'vix': 'yfinance ^VIX (1990-present)',
        'spy': 'yfinance SPY (1993-present)',
    },
    'TW': {
        'margin_balance': 'TWSE 公開資訊 (2000-present)',
        'institutional_flow': 'TWSE OpenData (2004-present)',
        'daytrade_ratio': 'TWSE (2017-present)',
        'taiex': 'yfinance ^TWII (1997-present)',
        'tsmc': 'yfinance 2330.TW (1997-present)',
    }
}
```

**驗證**: 所有數據欄位齊全、無缺值超過 5%？✅/❌

### Step 1B.2: 計算歷史 GRISI 分數 (滾動窗口)

```python
# 嚴格 point-in-time: 只用 date 當天及之前的數據
for date in trading_days('2015-01-01', '2025-12-31'):
    us_score[date] = us_retail_score(data[:date])   # 252日 rolling z-score
    tw_score[date] = tw_retail_score(data[:date])
    divergence[date] = abs(us_score[date] - tw_score[date])
```

**驗證**: 分數在 0-100 範圍內、無 NaN、平均約 50？✅/❌

### Step 1B.3: 定義預測目標

```python
# 主要目標: 散戶淨買超標的未來 N 日報酬
TARGET = {
    'TW': 'TAIEX future N-day return (散戶淨買超時段)',
    'US': 'SPY future N-day return',
}

# 測試多個 horizon
HORIZONS = [5, 10, 20, 60]  # 天
```

### Step 1B.4: 評估指標

```python
# 對每個 horizon 計算:
for h in HORIZONS:
    # 1. Information Coefficient (IC)
    ic = spearmanr(grisi_score, future_return_h)
    # 目標: |IC| > 0.05

    # 2. Hit Rate
    # GRISI > 80 時，未來 h 日回檔的比例
    hit = pct(grisi > 80 AND future_return < 0)
    # 目標: > 60%

    # 3. Quintile Spread
    q5_return = mean_return(top_quintile)
    q1_return = mean_return(bottom_quintile)
    spread = q1_return - q5_return  # 低分組應該跑贏高分組
    # 目標: 年化 > 10%

    # 4. Long/Short Sharpe
    # 做空高分期、做多低分期
    ls_sharpe = sharpe_ratio(long_short_strategy)
    # 目標: > 0.5
```

### Step 1B.5: 穩健性檢查

```
- 分年度測試 (2015-2019 vs 2020-2025) — 不能只有某幾年準
- US 和 TW 分開測 — 不能只有一個市場準
- 排除極端事件 (2020-03 COVID, 2021 GME, 2024-08 Yen crash) 後還準嗎？
- Walk-forward test: 用 2015-2019 訓練權重 → 2020-2025 測試
```

### 🚪 Gate 1B 驗證標準
```
至少一個市場 + 一個 horizon 組合:
- |IC| > 0.05? ✅/❌
- Hit rate > 60%? ✅/❌
- Walk-forward 也通過? ✅/❌

全部 ❌ → 公式無效，回 Phase 1 重新設計
部分 ✅ → 記錄哪些有效，帶著結論進 Phase 2
全部 ✅ → 太好了，信心滿滿進 Phase 2
```

---

## Phase 1C: 社群數據增量測試 (Day 8-12) ⭐ NEW

> 在 Phase 1B 基線確立後，測試社群/敘事指標是否有「增量預測力」

### Step 1C.1: 收集歷史社群數據

```
Reddit (Pushshift archive):
- r/wallstreetbets: 2019-2023 (黃金時期)
- r/stocks, r/investing: 2015-2023
- 抽取: 每日提及量 top 20 tickers, sentiment score, post volume

PTT stock 板:
- 爬蟲回溯 2015-present
- 抽取: 每日推文數, 提及個股, 推/噓比

處理: daily aggregation → rolling 7d/30d features
```

### Step 1C.2: 建構社群指標

```python
NARRATIVE_INDICATORS = {
    'attention_hhi': '提及集中度 (Herfindahl Index)',
    'sentiment_momentum': '情緒動量 (7d sentiment MA vs 30d)',
    'volume_spike': '討論量異常 (當日 vs 30d avg)',
    'new_topic_velocity': '新話題出現速度 (0→Top10 天數)',
    'consensus_score': '共識度 (top 1 ticker share of mentions)',
}
```

### Step 1C.3: 增量測試

```python
# 測試社群指標加進去後 IC 是否提升
base_ic = evaluate(base_indicators_only)
full_ic = evaluate(base + narrative_indicators)

incremental_ic = full_ic - base_ic
# < 0.02 → 沒用，砍掉
# 0.02-0.05 → 有點用，保留但低權重
# > 0.05 → 有顯著增量價值
```

### 🚪 Gate 1C 驗證標準
```
社群指標 incremental IC > 0.02? ✅/❌
✅ → 保留，確定權重，進 Phase 2
❌ → 社群數據沒有增量價值，Phase 2 的 LLM agent 只做 narrative 不做 scoring
```

---

## Phase 2: LLM 文化 Agent (Day 12-16)

### Step 2.1: 設計 Persona Prompt

**US Agent (Behavioral Anchors)**:
```
## Decision Framework (STRICTLY FOLLOW)

You are interpreting market data as a typical American retail investor would.

BEHAVIORAL RULES:
1. OPTIMISM BIAS: Your default state is CAUTIOUS_OPTIMISM, not NEUTRAL.
   "Stocks always go up in the long run" is your baseline belief.

2. FED DEPENDENCY: Federal Reserve signals override all other factors.
   - Fed hawkish → immediately shift 2 levels toward fear
   - Fed dovish → immediately shift 1 level toward greed

3. BUY THE DIP: When market drops > 5% from recent high,
   your instinct is "opportunity" not "danger". Shift 1 level toward greed.

4. NARRATIVE SENSITIVITY: If a strong story exists (AI boom, etc.),
   it amplifies your conviction by 1 level.

5. LOSS TRIGGER: Only shift to FEAR when drawdown > 10% AND VIX > 25.
   Below that threshold, you remain optimistic.

When choosing between two adjacent sentiment levels, choose the more OPTIMISTIC one.
```

**TW Agent (Behavioral Anchors)**:
```
## Decision Framework (STRICTLY FOLLOW)

You are interpreting market data as a typical Taiwanese retail investor (台灣散戶) would.

BEHAVIORAL RULES:
1. TSMC ANCHOR: TSMC performance is the single most important signal.
   - TSMC up > 3% this month → shift 1 level toward greed
   - TSMC down > 5% → shift 2 levels toward fear (panic)

2. FOLLOW FOREIGN INVESTORS: 外資買賣超 is your compass.
   - 外資連續 5 日買超 → shift 1 level toward greed ("smart money is buying")
   - 外資連續 5 日賣超 → shift 1 level toward fear ("外資要跑了")

3. MARGIN SENSITIVITY: 融資餘額 increasing makes you MORE confident (herd).
   - 融資增加 → "大家都在買" → shift toward greed
   - This is OPPOSITE of rational behavior (margin increase = risk increase)

4. LOSS AVERSION: You weigh losses 2x more than gains.
   - A 3% drop feels as bad as a 6% gain feels good.

5. DEFAULT STATE: NEUTRAL (more cautious than US investor)

When choosing between two adjacent sentiment levels, choose the more CAUTIOUS one.
```

**Control Agent (No persona)**:
```
Analyze the market data objectively. Output your sentiment assessment.
No cultural bias, no behavioral anchors. Pure data interpretation.
```

### Step 2.2: 統計驗證 Prompt 差異化

```python
# 用同一組固定數據，每個 agent 跑 30 次
results = {"us": [], "tw": [], "control": []}
for _ in range(30):
    results["us"].append(call_agent("us", fixed_data))
    results["tw"].append(call_agent("tw", fixed_data))
    results["control"].append(call_agent("control", fixed_data))

# Chi-squared test: 三個 agent 的 output distribution 是否顯著不同
from scipy.stats import chi2_contingency
contingency_table = build_table(results)  # rows=agents, cols=sentiment_levels
chi2, p, dof, expected = chi2_contingency(contingency_table)
print(f"Chi-squared: {chi2:.2f}, p-value: {p:.4f}")
```

### 🚪 Gate 2 驗證標準
```
p-value < 0.05 → Agent 輸出分布顯著不同 → 通過 ✅
p-value > 0.05 → Persona 沒有效果 → 回去改 prompt ❌

額外檢查:
- US agent 是否比 TW agent 更偏樂觀？(預期: 是)
- Control agent 是否在中間？(預期: 是)
- 三者的 reasoning 文字是否有明確的文化差異？(人工檢查)
```

---

## Phase 3: 整合 + 每日輸出 (Day 11-15)

### Step 3.1: Pipeline 整合

```python
# run.py — 主程式
async def run_grisi():
    # Layer 1: Real data → Score
    us_data = collect_us_data()       # yfinance + AAII + FRED
    tw_data = collect_tw_data()       # yfinance + TWSE

    us_score = us_retail_score(us_data)   # deterministic
    tw_score = tw_retail_score(tw_data)   # deterministic
    divergence = abs(us_score - tw_score)

    # Layer 2: LLM → Narrative
    market_snapshot = format_snapshot(us_data, tw_data, us_score, tw_score)

    us_narrative = await call_agent("us", market_snapshot, runs=3)  # majority vote
    tw_narrative = await call_agent("tw", market_snapshot, runs=3)

    # Layer 3: Output
    briefing = generate_briefing(
        us_score, tw_score, divergence,
        us_narrative, tw_narrative,
        find_historical_match([us_score, tw_score])
    )

    save_to_db(date.today(), us_score, tw_score, divergence, briefing)
    print(briefing)
```

### Step 3.2: EMA 平滑

```python
# 避免每天分數跳動太大
today_score = raw_score
smoothed = 0.3 * today_score + 0.7 * yesterday_smoothed
```

### Step 3.3: 一致性檢查

```python
def validate(agent_output, data_score):
    # 如果真實數據說散戶在賣 (score < 30)，
    # 但 LLM agent 說 EUPHORIA → flag 不一致
    if data_score < 30 and agent_output["sentiment"] in ["OPTIMISM", "EUPHORIA"]:
        return "WARNING: LLM narrative conflicts with data signal"
    return "OK"
```

### 🚪 Gate 3 驗證標準
```
連續跑 5 天:
- 每天都能成功產出報告？✅/❌
- 分數穩定（EMA 後日變動 < 10）？✅/❌
- LLM narrative 和 data score 一致？✅/❌
- 報告可讀、有洞見、不是廢話？✅/❌ (人工判斷)
```

---

## Phase 4: 內容分發 + 市場驗證 (Week 3-4)

### Step 4.1: 每日簡報自動生成

```
格式 (中文版):
---
GRISI 每日散戶指數 — 2026-03-20

📊 散戶在幹嘛？
🇺🇸 美國散戶: 62/100 (偏樂觀) — AAII 看多比例 45%
🇹🇼 台灣散戶: 78/100 (貪婪) — 融資餘額連續 10 天增加

📐 分歧度: 16 (中等)

🤖 AI 解讀:
「台灣散戶因台積電法說利多持續加碼融資，
美國散戶受 AI 敘事支撐偏樂觀但未到極端。
歷史上台灣散戶分數 > 75 且融資增加的情境出現 8 次，
後續 20 天台股平均回撤 -3.2%。」

⚠️ 信號: 台灣散戶偏貪婪，歷史模式偏空
---
```

### Step 4.2: 分發管道

| 管道 | 頻率 | 內容 |
|------|------|------|
| PTT Stock 板 | 每日盤後 | 完整中文簡報 |
| Twitter/X | 每日 | 圖卡 + 一句話摘要 |
| Threads | 每日 | 同 Twitter |
| Substack | 每週 | 週報 + 深度分析 |

### 🚪 Gate 4 驗證標準
```
30 天後:
- Email 訂閱 > 500? → 繼續投資 Dashboard
- Email 訂閱 < 100? → Pivot 內容方向
- PTT 推文反應? → 調整語氣和深度
```

---

## Phase 5: Dashboard + 學術 (Month 2+)

只有通過 Phase 4 才做。

### Step 5.1: Streamlit Dashboard
- 全球 gauge + 各國 bar chart
- Agent reasoning panel
- 歷史趨勢圖
- 分歧度 heatmap

### Step 5.2: 學術驗證
- Behavioral validation: agent score vs AAII / 融資餘額 correlation (target r > 0.4)
- Ablation study: remove persona → output 是否變得相同？
- Granger causality: GRISI → future returns?
- Paper draft: target ICAIF 2026

### 🚪 Gate 5 驗證標準
```
- r > 0.4 correlation with ground truth? ✅/❌
- Ablation study shows significant persona effect? ✅/❌
- GRISI divergence Granger-causes volatility? ✅/❌
```

---

## Summary: 可以今晚先做的

**Phase 0 今晚就能做完**:

```
Step 0.1: pip install yfinance pandas_ta → 拉 SPY, ^TWII, 2330.TW
Step 0.2: 測試 TWSE OpenData API → 拉融資餘額
Step 0.3: 確認 AAII 數據取得方式
Step 0.4: 申請 FRED API key → 拉宏觀數據
Step 0.5: 計算技術指標

目標: 今晚結束前有一個 data_collector.py 能跑出完整的 JSON
```

---

*Last updated: 2026-03-16*
