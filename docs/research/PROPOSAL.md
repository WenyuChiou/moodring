# Global Retail Investor Sentiment Index (GRISI)

**A Hybrid Data + LLM System for Cross-Market Retail Investor Behavior Tracking**

> **v2.0 — Updated after 4-agent expert panel review (2026-03-16)**
> Key changes: Hybrid architecture (real data + LLM narrative), MVP scope narrowed to US + Taiwan, forward test instead of backtest

---

## 1. Problem Statement

### The Retail Investor Blind Spot

Retail investors now account for a significant share of global trading volume — over 25% in the US, 60%+ in China, 30%+ in Korea and Taiwan. Yet there is **no unified tool that tracks retail investor sentiment across global markets simultaneously**.

Existing indicators have critical gaps:

1. **VIX / Fear & Greed Index** — measures overall market anxiety, not retail-specific behavior
2. **AAII Sentiment Survey** — US only, self-reported, weekly lag
3. **Put/Call Ratio** — institutional-heavy, doesn't isolate retail
4. **Social media NLP** — language-specific, no cross-market comparison, measures what people *say* not how they *behave*

### The Missing Metric

> **What if we could track real retail investor behavior across major markets in real-time, and use AI to explain the cultural dynamics behind their decisions?**

The behavioral differences between retail investors across countries are well-documented in academic literature:
- US retail: options-heavy, meme stock culture, "buy the dip"
- Taiwan retail: technical analysis obsessed, dividend-focused, TSMC-centric
- China retail: policy-driven, extreme herding, short-term gambling
- Korea retail: highest leverage in the world, FOMO-driven, revenge trading
- Japan retail: ultra-conservative, yield-seeking, Mrs. Watanabe carry trades

These behavioral differences are **not noise — they are signal**. When Korean retail goes full FOMO while Japanese retail stays cautious, that divergence pattern has historically preceded market turning points.

---

## 2. Proposed Solution: GRISI (Hybrid Architecture)

### Core Concept

GRISI uses a **hybrid architecture**: real market data to determine WHAT retail investors are doing, and LLM agents to explain WHY from a cultural perspective.

**Layer 1 — Signal (Real Data, Deterministic)**:
1. Collect **retail-specific quantitative indicators** per market (margin balance, retail order flow, put/call ratio)
2. Python calculates per-country retail sentiment score and cross-market divergence
3. This is the **verifiable, backtestable, reproducible** signal

**Layer 2 — Narrative (LLM, Interpretive)**:
1. Cultural LLM agents receive the real data scores
2. Each agent interprets: "Why is Taiwan retail sentiment at 78?" from their cultural perspective
3. This adds **explainability, storytelling, and cultural context** that raw data cannot provide

**Layer 3 — Action (Decision Support)**:
1. Map sentiment patterns to historical analogs
2. Output: "散戶現在偏買還是偏賣？歷史上類似情境後市場怎麼走？"
3. Help users make **contrarian investment decisions** based on retail crowd behavior

### Value Proposition: Retail Investors as Contrarian Indicator

Academic evidence overwhelmingly shows retail investors as a group are wrong at extremes:
- Barber & Odean (2000): More trading → worse returns
- Kumar (2009): Retail-concentrated stocks underperform
- Baker & Wurgler (2006): High retail sentiment predicts low future returns

**GRISI's core value**: Tell you what retail investors across markets are doing, so you can decide whether to go against them.

### What Makes This Different

| Aspect | Traditional Sentiment | **GRISI (Ours)** |
|--------|----------------------|-------------------|
| Signal source | LLM/NLP guessing | **Real retail data (margin, order flow)** |
| Who | All market participants | **Retail investors only, per country** |
| Explainability | "Market is fearful" | **"TW retail greedy because 融資餘額創高 + TSMC ATH"** |
| Cross-market | Single market only | **Multi-country divergence as signal** |
| Actionable? | Vague | **Contrarian indicator with historical analogs** |

---

## 3. System Architecture (Hybrid: Real Data + LLM)

```
┌──────────────────────────────────────────────────────────┐
│  LAYER 1: REAL DATA → SIGNAL (Deterministic, Verifiable) │
│                                                           │
│  🇺🇸 US Retail Indicators:        🇹🇼 TW Retail Indicators: │
│  • AAII Bull/Bear Survey          • 融資餘額 (TWSE)        │
│  • Put/Call Ratio (CBOE)          • 三大法人-散戶買賣超     │
│  • 0DTE Options Volume            • 當沖比率               │
│                                                           │
│  🌐 Global Context:                                       │
│  • yfinance: SPY, ^TWII, 2330.TW, VIX, DXY              │
│  • FRED: Fed rate, CPI, US10Y                            │
│  • pandas_ta: RSI, MACD, Bollinger, MA                   │
│                                                           │
│  → Python: Normalize → Per-country retail score (0-100)  │
│  → Python: Cross-market divergence (σ)                   │
│  → Python: Historical pattern matching (cosine sim)      │
└──────────────────────┬────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────┐
│  LAYER 2: LLM AGENTS → NARRATIVE (Cultural Interpretation)│
│                                                           │
│  Input: Real data scores + raw market data                │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ 🇺🇸 US Agent  │  │ 🇹🇼 TW Agent │  │ 🔧 Control   │    │
│  │              │  │              │  │    Agent     │    │
│  │ Behavioral   │  │ Behavioral   │  │ (No persona, │    │
│  │ anchors:     │  │ anchors:     │  │  baseline)   │    │
│  │ • Buy-dip    │  │ • TSMC-centric│ │              │    │
│  │   mentality  │  │ • 融資追多    │  │              │    │
│  │ • Fed focus  │  │ • 跟單外資    │  │              │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │             │
│  Method: tool_use (structured output)                     │
│  Output: 7-level sentiment × 3-level conviction          │
│  Sampling: 3 runs per agent, majority vote               │
└──────────────────────┬────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────┐
│  LAYER 3: OUTPUT → ACTION (Decision Support)              │
│                                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │  🌡️ GRISI Daily — 2026-03-16                      │   │
│  │                                                    │   │
│  │  全球散戶現在在：   大量買進 📈                     │   │
│  │  散戶共識度：       92% (極高)                      │   │
│  │  歷史相似情境結果： 後續 20 天 -4.3%               │   │
│  │                                                    │   │
│  │  🇺🇸 ████████████░░  62  買入 (AAII bull 48%)     │   │
│  │  🇹🇼 ███████████████  78  買入 (融資餘額創高)      │   │
│  │                                                    │   │
│  │  💡 解讀 (LLM):                                    │   │
│  │  「台灣散戶因台積電法說利多大幅加碼融資，            │   │
│  │   美國散戶受 AI 敘事驅動持續看多。                   │   │
│  │   歷史上雙方同步極度樂觀出現 4 次，                  │   │
│  │   後續 20 天平均回撤 -4.3%。建議提高警覺。」        │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Retail Agent Design (散戶行為模型)

Each agent is an LLM instance with a **retail investor persona prompt** that encodes: the country's retail trading culture, typical behavioral biases, information ecosystem, and decision-making patterns. The key constraint is: **these agents simulate retail investors, not professionals**.

### 4.1 🇺🇸 US Retail Agent (Robinhood / WSB Generation)

- **Who they are**: Robinhood 用戶、WallStreetBets 散戶、年輕世代 options 交易者
- **Decision style**: Narrative-driven, meme-sensitive, options-heavy
- **Behavioral biases**:
  - "Stocks only go up" optimism bias
  - FOMO on momentum plays (GME, NVDA, TSLA)
  - Loss aversion → diamond hands / paper hands extreme
  - Overconfidence in Fed put ("Fed will save us")
- **Information diet**: Reddit WSB, Twitter/X FinTwit, TikTok finance, CNBC headlines
- **Retail-specific data inputs**:
  - Robinhood top holdings / most popular stocks
  - Options flow (0DTE volume as euphoria proxy)
  - Meme stock basket performance
- **Greed triggers**: New ATH, FOMO rally, "this time is different"
- **Fear triggers**: Rate hike surprise, tech selloff, margin calls
- **Signature behavior**: "Buy the dip" → diamond hands → panic sell at bottom

### 4.2 🇹🇼 Taiwan Retail Agent (台灣散戶)

- **Who they are**: 存股族、技術分析派、融資戶、PTT Stock 板鄉民
- **Decision style**: 重度依賴技術分析 (KD/MACD/均線)、高度關注法人動向
- **Behavioral biases**:
  - 台積電 = 信仰 (TSMC home bias)
  - 除息行情 (配息前搶進)
  - 跟單外資買超 (follow smart money fallacy)
  - LINE 群組/PTT 從眾效應
  - 融資追多 → 斷頭恐慌 cycle
- **Information diet**: PTT Stock 板、財經 YouTuber (柴鼠兄弟、Mr. Market)、LINE 群組、三大法人進出
- **Retail-specific data inputs**:
  - 融資餘額 / 融資維持率
  - 三大法人買賣超 (外資 > 投信 > 自營)
  - 台積電股價 & 法說會內容
  - 當沖比率
- **Greed triggers**: 外資連續買超、台積電創新高、殖利率 > 5%
- **Fear triggers**: 外資大賣、融資斷頭、台海地緣風險
- **Signature behavior**: 「存股不賣」→ 融資追高 → 融資斷頭 → 恐慌停損 → 錯過反彈

### 4.3 🇨🇳 China A-Share Retail Agent (中國散戶/韭菜)

- **Who they are**: 6000 萬+ 活躍散戶、「韭菜」、概念股炒作者
- **Decision style**: 政策至上 (政策市)、題材/概念股炒作、極短線
- **Behavioral biases**:
  - 政策崇拜：「國家隊進場了！」
  - 極端羊群效應 (全球最嚴重)
  - 賭場心態：追漲停板、打板族
  - 消息面炒作 > 基本面分析
  - 暴漲暴跌後的「被套」心態
- **Information diet**: 東方財富股吧、雪球、微博財經 KOL、新華社 / 人民日報（政策信號）
- **Retail-specific data inputs**:
  - 新開戶數
  - 兩融餘額 (margin balance)
  - 北向資金 (滬港通/深港通)
  - 漲停/跌停家數比
  - 國務院/人行政策公告
- **Greed triggers**: 國務院利多政策、北向資金大幅流入、「牛市來了」
- **Fear triggers**: 監管打壓、IPO 暫停、中美關係惡化、「國家隊撤了」
- **Signature behavior**: 政策利多 → 全民瘋搶 → 暴漲 3 天 → 套牢 → 陰跌半年

### 4.4 🇰🇷 Korean Retail Agent (韓國散戶 / 개미)

- **Who they are**: 개미 (螞蟻)、20-30 歲年輕世代、빚투 (借錢投資) 族
- **Decision style**: 純動量驅動、極度槓桿、YOLO
- **Behavioral biases**:
  - 全球最高的散戶槓桿率
  - 빚투 (빚내서 투자 = 借錢投資) 文化正常化
  - Revenge trading (虧了加碼想翻本)
  - FOMO 到極致 — 不買 = 落後
  - 對 Samsung/SK Hynix 半導體的本土偏好
- **Information diet**: Naver Finance、KakaoTalk 投資群、YouTube 股票 KOL
- **Retail-specific data inputs**:
  - 信用交易融資餘額 (全球最高水位指標)
  - 散戶淨買賣超
  - Samsung Electronics 股價
  - KOSPI/KOSDAQ 成交量
- **Greed triggers**: 半導體 super cycle 敘事、Samsung 創新高、KOSPI 突破均線
- **Fear triggers**: Margin call 連環爆、外資大撤、韓元貶值
- **Signature behavior**: 借錢 all-in → 槓桿推高 → margin call → 被迫平倉 → 市場崩盤 → 再借錢 all-in
- **⚠️ 核心指標價值**: 韓國散戶槓桿水位是全球風險偏好的「金絲雀」——歷史上韓國散戶槓桿見頂後 1-3 個月，全球常出現修正

### 4.5 🇯🇵 Japan Retail Agent (日本散戶 / 渡邊太太)

- **Who they are**: 渡邊太太 (Mrs. Watanabe)、優待投資族 (stockholder benefit hunters)、新 NISA 投資者
- **Decision style**: 極度保守、殖利率導向、匯率敏感
- **Behavioral biases**:
  - 「失落的 30 年」心理陰影 → 對日股天生保守
  - 偏好海外資產 (carry trade)
  - 對日圓匯率過度敏感
  - 新 NISA 制度帶來的新一代投資者 (相對積極)
  - 優待品投資 (股東優惠) 偏好
- **Information diet**: 日經新聞、Yahoo Finance Japan、投資相關書籍 (非 social media 導向)
- **Retail-specific data inputs**:
  - 日圓匯率 (USDJPY)
  - 新 NISA 開戶數與資金流入
  - 日本散戶海外投資比例
  - BOJ 政策聲明
- **Greed triggers**: 日圓貶值 (海外資產增值)、新 NISA 推動、巴菲特加碼日股
- **Fear triggers**: 日圓急升 (carry trade unwind)、BOJ 升息、全球衰退
- **Signature behavior**: 觀望 → 緩慢進場 → 長期持有 → 日圓升值才恐慌
- **⚠️ 核心指標價值**: 當日本散戶開始恐慌賣出海外資產 → carry trade unwind → 全球流動性收緊的領先指標 (2024年8月就是經典案例)

---

### 4.6 Retail Behavior Comparison Matrix

| Dimension | 🇺🇸 US | 🇹🇼 Taiwan | 🇨🇳 China | 🇰🇷 Korea | 🇯🇵 Japan |
|-----------|---------|-----------|-----------|-----------|-----------|
| **Typical age** | 25-40 | 30-55 | 25-50 | 20-35 | 40-65 |
| **Risk appetite** | High | Medium | Extreme swings | Very High | Very Low |
| **Leverage** | Options (0DTE) | 融資 | 兩融 | 빚투 (highest) | Low (NISA) |
| **Holding period** | Days-weeks | Weeks-months | Hours-days | Hours-days | Months-years |
| **Herd behavior** | High (Reddit) | High (PTT/LINE) | Extreme (股吧) | Very High | Low |
| **Home bias** | Medium | Very High (台積電) | Very High | High (Samsung) | Shifting ↓ |
| **Info source** | Reddit/TikTok | PTT/YouTube | 東財/雪球 | Naver/KakaoTalk | 日經/書籍 |
| **Key trigger** | Fed + memes | TSMC + 外資 | 政策 | Momentum + margin | JPY + BOJ |
| **Fear pattern** | Diamond hands → panic | 融資斷頭 | 政策打壓 → 跌停 | Margin call cascade | Carry unwind |
| **Greed pattern** | YOLO calls | 存股→追融資 | 全民開戶 | 빚투 all-in | Slow NISA inflow |
| **As indicator** | Options sentiment | 融資餘額 | 新開戶數 | **槓桿水位 (canary)** | Carry trade flows |

---

## 5. Key Innovation: Global Retail Divergence Index

### Why "Divergence" Is the Real Signal

Individual retail sentiment is useful but not novel. **The breakthrough is comparing retail sentiment across countries simultaneously.** Different retail investor cultures react to the same global events with different speeds, magnitudes, and sometimes opposite directions.

### Signal Taxonomy

| Pattern | What It Means | Historical Example |
|---------|---------------|-------------------|
| All 5 retail greedy | Global retail euphoria → **top signal** | Nov 2021 (crypto + meme peak) |
| All 5 retail fearful | Global retail capitulation → **bottom signal** | Mar 2020, Oct 2022 |
| 🇰🇷🇹🇼 greedy + 🇯🇵🇺🇸 cautious | Asian retail FOMO leading → **correction warning** | Jan 2021, May 2024 |
| 🇨🇳 greedy alone | Policy pump → **not sustainable** | Apr 2024 policy rally, Sep 2024 |
| 🇯🇵 sudden fear | Carry trade unwind → **global liquidity shock** | Aug 2024 (Yen carry crash) |
| 🇺🇸 greedy + 🇨🇳 fearful | US exceptionalism trade → **EM outflow** | 2023 H2 |
| 🇰🇷 leverage peak → all others flat | **Most dangerous** — Korean retail as global risk canary | Pre most corrections |
| Low divergence (all similar) | Boring market / range-bound | Consolidation periods |
| High divergence (σ > 20) | **Regime shift incoming** — someone is wrong | Transition periods |

### Composite Index Formulas (v3 — Adaptive + Backtestable)

> **v3.0 Design Principle**: Static formulas can't track dynamic attention.
> GRISI uses a **3-layer adaptive architecture**: fixed base indicators (30%) + dynamic attention-weighted indicators (70%).
> Every component must be backtestable against historical data.

#### Layer A: Base Indicators (30% weight, always present)

These have 10+ years of history and are always computed:

```python
# Base indicators — stable, backtestable, always available
BASE_INDICATORS = {
    'US': {
        'aaii_bull_pct': 0.35,       # AAII weekly survey (1987–present)
        'put_call_ratio_inv': 0.25,  # CBOE put/call (2006–present)
        'vix_inv': 0.20,             # VIX inverse (1990–present)
        'spy_vs_52w_high': 0.20,     # SPY relative position
    },
    'TW': {
        'margin_balance_chg': 0.35,  # TWSE 融資餘額 (2000–present)
        'retail_net_buy': 0.30,      # 散戶淨買超 (2004–present)
        'daytrade_ratio': 0.15,      # 當沖比率 (2017–present)
        'taiex_vs_52w_high': 0.20,   # 加權指數相對位置
    }
}

base_score = weighted_zscore(BASE_INDICATORS[market], window=252)
```

#### Layer B: Dynamic Attention-Weighted Indicators (70% weight)

Components and weights **shift automatically** based on what retail investors are paying attention to:

```python
# Step 1: Attention Radar — detect what retail investors are discussing
def detect_attention(date, market):
    """Scan Reddit/PTT/Twitter for top mentioned topics/tickers"""
    mentions = get_social_mentions(date, market)  # top 20 tickers/themes

    # Attention Herfindahl Index (AHI)
    # High AHI = everyone talking about same thing = consensus/bubble signal
    shares = [m.count / total for m in mentions]
    ahi = sum(s**2 for s in shares)

    # Identify dominant narratives
    narratives = classify_narratives(mentions)  # LLM: AI_hype, rate_cut, meme, etc.
    return narratives, ahi

# Step 2: Map narratives → quantifiable indicators
NARRATIVE_INDICATOR_MAP = {
    'AI_hype':     ['nvda_call_volume', 'smh_etf_flow', 'semiconductor_momentum'],
    'rate_cut':    ['tlt_retail_flow', 'fed_futures_gap', 'bank_etf_rotation'],
    'meme_stock':  ['gme_amc_short_interest', 'wsb_yolo_count', 'small_cap_volume'],
    'geopolitical': ['defense_etf_flow', 'gold_retail_demand', 'vix_term_structure'],
    'dividend':    ['div_etf_inflow', 'yield_spread', 'reit_retail_flow'],  # TW-specific
}

# Step 3: Compute dynamic score with attention-driven weights
def dynamic_score(date, market):
    narratives, ahi = detect_attention(date, market)
    indicators = {}
    for n in narratives:
        for ind in NARRATIVE_INDICATOR_MAP.get(n.theme, []):
            indicators[ind] = weight_by_attention(n.intensity)
    return weighted_aggregate(indicators)

# Final GRISI score
GRISI_country = 0.3 * base_score + 0.7 * dynamic_score
```

#### Layer C: Regime Shift Detection (meta-signal)

```python
# Detect when retail attention is shifting to a new narrative
def detect_regime_shift(date, market):
    current_topics = get_topic_ma(date, window=7)
    baseline_topics = get_topic_ma(date, window=30)

    # Golden cross: new topic 7d MA > 30d MA = emerging narrative
    # Death cross: old topic 7d MA < 30d MA = fading narrative

    # Velocity check: topic goes 0 → Top 10 in 3 days = rapid shift
    new_entries = find_new_top10_entries(date, lookback=3)

    # Fund flow confirmation: talking about it AND buying it?
    for topic in new_entries:
        talk = topic.mention_velocity
        money = topic.etf_flow_change
        if talk > threshold and money > threshold:
            trigger_weight_update(topic)  # Real shift, update weights
        # else: mouth shift only, ignore

    return shift_signals
```

#### Cross-Market Composite

```python
# Per-country scores → global index
GRISI_global = (w_US × GRISI_US + w_TW × GRISI_TW + ...)

# Divergence Score — cross-market disagreement
Divergence = σ(GRISI_US, GRISI_TW, GRISI_CN, GRISI_KR, GRISI_JP)

# Attention Herfindahl Index — consensus indicator
AHI_global = mean(AHI_US, AHI_TW, ...)  # High = everyone same narrative = top signal

# Cross-market contagion speed
Contagion = lag_correlation(GRISI_US, GRISI_TW, max_lag=5)

# Historical pattern matching
cosine_similarity([GRISI_US, GRISI_TW, AHI, Divergence], historical_db)
```

### Backtesting Framework

> **Principle**: 不能回測的策略就是在講故事。Every signal must be evaluated against historical data.

#### Prediction Target

Primary target: **散戶淨買超標的未來 N 日報酬** — directly answers "will retail crowd lose money?"

#### Two-Phase Backtest Strategy

```python
# Phase 1: Base indicators only (10+ years history, no social data needed)
class GRISIBacktest:
    def compute_score(self, date, market):
        """Strictly uses data available on or before 'date' — no lookahead"""
        for name in BASE_INDICATORS[market]:
            raw = get_data(name, end_date=date)
            indicators[name] = rolling_zscore(raw, window=252)
        return aggregate(indicators)

    def evaluate(self, score_series, market):
        for horizon in [5, 10, 20, 60]:
            future_returns = get_retail_basket_returns(market, horizon)
            quintiles = pd.qcut(score_series, 5)
            results[horizon] = {
                'ic': spearmanr(score_series, future_returns),  # target |IC| > 0.05
                'hit_rate': pct_correct_direction,               # target > 60%
                'quintile_spread': top_minus_bottom,             # target annual > 10%
                'sharpe': long_short_sharpe,                     # target > 0.5
            }

# Phase 2: Add social/narrative indicators → test incremental alpha
class NarrativeBacktest(GRISIBacktest):
    # Reddit: Pushshift archive 2005-2023
    # PTT: web scraper ~2010-present
    def evaluate_incremental(self):
        base_ic = evaluate(base_only_score)
        full_ic = evaluate(base + narrative_score)
        # incremental IC < 0.02 → social data useless, drop it
        # incremental IC > 0.05 → keep it

# Robustness checks:
# - Per-year breakdown (can't only work in one year)
# - US and TW separately (can't only work in one market)
# - Exclude extreme events (COVID/GME) — still works?
```

#### Historical Data Sources (Confirmed Available)

| Data | Source | History | Cost |
|------|--------|---------|------|
| AAII survey | aaii.com CSV | 1987–present | Free |
| CBOE Put/Call | CBOE website | 2006–present | Free |
| VIX | Yahoo Finance | 1990–present | Free |
| SPY price | Yahoo Finance | 1993–present | Free |
| 0DTE options | CBOE | 2022–present | Free |
| 融資餘額 | TWSE 公開資訊 | 2000–present | Free |
| 三大法人買賣超 | TWSE OpenData | 2004–present | Free |
| 當沖比率 | TWSE | 2017–present | Free |
| Reddit archive | Pushshift | 2005–2023 | Free |
| PTT stock 板 | Web scraper | ~2010–present | Free |

---

## 6. Technical Implementation

### 6.1 Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Language | Python 3.11+ | Ecosystem, rapid prototyping |
| LLM | Claude API (Haiku for cost) | Best reasoning, structured output |
| Market Data | yfinance (free) | Global index data, no API key |
| Macro Data | FRED API (free) | US macro indicators |
| News | RSS feeds (free) | Multi-language headlines |
| Dashboard | Streamlit | Fast, interactive, free hosting |
| Storage | SQLite | Lightweight, historical tracking |
| Scheduling | APScheduler / cron | Daily auto-run |

### 6.2 Project Structure

```
grisi/                              # Global Retail Investor Sentiment Index
├── README.md
├── requirements.txt
├── config.yaml                     # API keys, weights, thresholds
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── market_data.py          # yfinance: per-market price/volume/technicals
│   │   ├── macro_data.py           # FRED: rates, CPI, PMI
│   │   └── news_data.py            # RSS per market
│   ├── agents/
│   │   ├── base_agent.py           # Abstract retail agent (LLM call + schema)
│   │   ├── us_retail.py            # 🇺🇸 Robinhood/WSB agent
│   │   ├── tw_retail.py            # 🇹🇼 PTT/存股族 agent
│   │   ├── cn_retail.py            # 🇨🇳 東財/韭菜 agent
│   │   ├── kr_retail.py            # 🇰🇷 개미/빚투 agent
│   │   └── jp_retail.py            # 🇯🇵 渡邊太太/NISA agent
│   ├── index/
│   │   ├── calculator.py           # GRISI composite index
│   │   ├── divergence.py           # Cross-market divergence scoring
│   │   ├── pattern_matcher.py      # Historical pattern similarity
│   │   └── briefing.py             # Natural language summary generator
│   ├── app.py                      # Streamlit dashboard
│   └── run.py                      # CLI entry point
├── data/
│   └── history.db                  # SQLite: daily GRISI readings
└── tests/
    ├── test_agents.py
    └── test_index.py
```

### 6.3 Core Pipeline

```python
# Pseudocode
def run_grisi():
    # 1. Collect per-market data
    markets = {
        "US":    get_market_data(["SPY", "QQQ", "^VIX"]),
        "TW":    get_market_data(["^TWII", "2330.TW"]),
        "CN":    get_market_data(["000001.SS", "399001.SZ"]),
        "KR":    get_market_data(["^KS11", "005930.KS"]),
        "JP":    get_market_data(["^N225", "USDJPY=X"]),
    }
    macro = get_macro_data()        # Fed rate, CPI, PMI
    news = get_headlines_per_market()

    state = MarketSnapshot(markets, macro, news)

    # 2. Run all 5 retail agents in parallel
    agents = [USRetail(), TWRetail(), CNRetail(), KRRetail(), JPRetail()]
    results = await asyncio.gather(*[a.evaluate(state) for a in agents])
    # Each returns: {score: 0-100, action: BUY/HOLD/SELL,
    #                reasoning: str, emotion: str, key_factors: list}

    # 3. Calculate composite index
    grisi_score = calculate_grisi(results)          # weighted average
    divergence = calculate_divergence(results)       # standard deviation
    pattern = find_historical_match(results)         # cosine similarity
    briefing = generate_briefing(results, grisi_score, divergence, pattern)

    # 4. Store & display
    save_daily_reading(grisi_score, results)
    return GRISIReport(grisi_score, divergence, pattern, briefing, results)
```

---

## 7. Implementation Plan (Step-by-Step with Validation Gates)

> Every phase has a **validation gate** — must pass before proceeding.

### Phase 0: Data Source Feasibility (Day 1-2)
- [ ] Verify yfinance can pull: SPY, ^TWII, 2330.TW, VIX, USDJPY, DXY
- [ ] Verify TWSE OpenData API: 融資餘額, 三大法人買賣超, 當沖比率
- [ ] Verify AAII data accessibility (scrape or API)
- [ ] Verify FRED API: Fed rate, CPI, US10Y
- [ ] Build `data_collector.py` — single script that pulls all data
- [ ] **Gate 0**: Run script → get clean JSON with all required fields? ✅/❌

### Phase 1: Deterministic Scoring Engine (Day 3-5)
- [ ] Design scoring formula: map raw retail indicators → 0-100 score per country
  - US: normalize(AAII_bull_pct, put_call_ratio_inv, 0DTE_volume_zscore)
  - TW: normalize(融資餘額_zscore, 散戶買超_zscore, 當沖比率_zscore)
- [ ] Implement cross-market divergence (σ of country scores)
- [ ] Historical pattern matching (cosine similarity on score vectors)
- [ ] **Gate 1**: Feed 2024 data → do scores correlate with known events?
  - 2024-08 (Yen carry crash): TW/KR scores should drop, JP should spike fear
  - 2024-09 (China policy rally): CN score should spike greed
  - If scores don't match known events → fix formula before proceeding

### Phase 2: LLM Cultural Agents (Day 6-10)
- [ ] Design 2 persona prompts (US + TW) + 1 control agent
  - Use **behavioral anchors** (quantified biases), not identity labels
  - Use **tool_use** for structured output (7-level sentiment × 3 conviction)
- [ ] Run each agent 30 times with same fixed data
- [ ] **Gate 2**: Chi-squared test — are 3 agents' output distributions significantly different?
  - If NOT → iterate prompts until statistically different
  - If YES → persona design is validated

### Phase 3: Integration + Daily Output (Day 11-15)
- [ ] Combine Layer 1 (data scores) + Layer 2 (LLM narrative)
- [ ] Auto-generate daily briefing (中英文, 300 words)
- [ ] SQLite storage for forward test logging
- [ ] EMA smoothing + validation layer (consistency checks)
- [ ] CLI: `python run.py` → outputs complete daily GRISI report
- [ ] **Gate 3**: Run for 5 consecutive days → output stable and meaningful? ✅/❌

### Phase 4: Distribution + Market Validation (Week 3-4)
- [ ] Publish daily briefing to PTT Stock 板 / Twitter / Threads
- [ ] Landing page + email subscription (Substack/Beehiiv)
- [ ] **Gate 4**: 30 days → 500 email subscribers? (market demand validation)
  - If YES → invest in dashboard
  - If NO → pivot content format or audience

### Phase 5: Dashboard + Academic (Month 2+)
- [ ] Streamlit dashboard (if Phase 4 passes)
- [ ] Behavioral validation: agent scores vs AAII / 融資餘額 correlation
- [ ] Ablation study: remove cultural persona → still different? (academic requirement)
- [ ] Paper draft targeting ICAIF or J. Behavioral & Experimental Finance
- [ ] **Gate 5**: r > 0.4 correlation with ground truth indicators? ✅/❌

---

## 8. Differentiation & Academic Value

### 8.1 Why This Is Novel

1. **First "Retail-Only" Cross-Market Sentiment Index** — Existing tools (VIX, AAII, Baker-Wurgler) don't isolate retail behavior across markets. GRISI is the first to track retail investor signals from multiple countries simultaneously.

2. **Hybrid architecture** — Real data for signal (verifiable, backtestable), LLM for narrative (explainable, culturally-grounded). This avoids the "LLM as black box" problem.

3. **Cultural finance operationalized** — Academic literature on cross-cultural investor behavior exists (Chui, Titman & Wei 2010; Chiang & Zheng 2010), but no one has built it into a real-time tool.

4. **Divergence is the product** — Cross-market retail disagreement as a signal is novel and actionable.

5. **LLM as Computational Laboratory** — Positions LLM agents as a cross-cultural behavioral finance research tool, not a prediction engine. This is methodologically defensible.

### 8.2 Theoretical Foundation (Updated per Expert Review)

**Core**: Bounded Rational Social Learning (Herding as primary mechanism)
- Banerjee (1992), Bikhchandani, Hirshleifer & Welch (1992) — information cascades
- **Baker & Wurgler (2006, 2007)** — investor sentiment index construction
- **DeLong, Shleifer, Summers & Waldmann (1990)** — noise trader model
- **Hong & Stein (1999)** — heterogeneous agent model
- **Chiang & Zheng (2010)** — cross-country herding comparison
- Chui, Titman & Wei (2010) — cultural dimensions and momentum
- Cookson, Engelberg & Mullins (2023) — social media and investor disagreement
- Argyle et al. (2023) "Out of One, Many" — LLM as simulated survey respondents

### 8.3 Potential Paper

> **"GRISI: A Hybrid Data-LLM Framework for Cross-Cultural Retail Investor Sentiment Tracking"**
>
> Key contributions:
> 1. First cross-cultural retail sentiment index with real data + LLM narrative
> 2. Methodology: LLM as cultural behavior interpreter (not predictor)
> 3. Ablation study: cultural persona vs. generic → validates cross-cultural differentiation
> 4. Forward test validation: GRISI divergence vs. subsequent market returns
>
> Target venues:
> - **ICAIF** (ACM International Conference on AI in Finance) — best fit
> - **J. Behavioral and Experimental Finance** — behavioral angle
> - **Financial Innovation** — cross-disciplinary
> - **AAMAS** Workshop — agent methodology

### 8.4 Portfolio / Demo Value

- **Unique story**: "I built a system that tracks retail investor behavior across US and Asia using real data + AI cultural interpretation"
- **Visual impact**: Daily briefing with per-country sentiment bars
- **Interdisciplinary**: CS + Finance + Cultural Studies + ABM
- **Practical**: Genuinely useful as contrarian indicator
- **Honest**: Signal from real data, LLM only for narrative (no "AI predicts market" overselling)

---

## 9. Cost Estimate

| Item | Cost | Notes |
|------|------|-------|
| Claude Haiku API | ~$0.05/run | 5 agents x ~1K tokens each |
| yfinance | Free | Open source |
| FRED API | Free | Public data |
| News RSS | Free | No API needed |
| Streamlit hosting | Free | Streamlit Cloud |
| **Total per day** | **~$0.05** | Extremely low cost |

---

## 10. Risk & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM gives similar scores for all agents | Low divergence, useless index | Extensive persona prompt engineering with strong cultural differentiation; temperature tuning |
| LLM hallucinate market data | Wrong sentiment scores | Feed real data in structured JSON; agent only interprets, doesn't recall facts |
| Agents don't capture real retail behavior | Inaccurate simulation | Validate against known retail indicators (AAII, 融資餘額, margin data) |
| Market data delays (yfinance) | Stale signals | Use daily close data; clearly label timestamp |
| Cultural stereotyping concerns | Ethical risk | Ground profiles in academic literature + real market data; avoid stereotypes, focus on documented behavioral patterns |

---

## 11. Future Extensions

1. **More markets** — 🇮🇳 India (Zerodha retail boom), 🇪🇺 Europe (neobrokers), 🇸🇬 Singapore, 🇧🇷 Brazil
2. **Crypto retail sentiment** — Same framework, different agent profiles per country (Korea = kimchi premium, China = OTC, US = Coinbase/Robinhood)
3. **Real-time intraday** — WebSocket feeds + streaming agent updates
4. **Backtesting validation** — Rigorous comparison: GRISI returns prediction vs. VIX, AAII, put/call
5. **Agent learning** — Agents remember past calls, adjust confidence over time
6. **Cross-market contagion** — When Korean retail panics, simulate contagion delay to other markets (network ABM)
7. **API service** — Expose GRISI as API for quant funds to consume
8. **Social media validation layer** — Cross-check agent predictions against actual PTT/Reddit/雪球 sentiment
9. **Newsletter/bot** — Daily GRISI briefing via Discord/LINE/Telegram

---

## 12. Summary

**GRISI (Global Retail Investor Sentiment Index)** 是一個用 LLM multi-agent 模擬全球五大股市散戶行為的系統。

核心差異化：
- 不是「分析情緒」，而是「模擬散戶會怎麼做」
- 不是單一市場，而是 **美國、台灣、中國、韓國、日本** 五國散戶同時比較
- 不是一個數字，而是一張 **散戶行為分歧圖** — 這個分歧本身就是最有價值的信號

技術可行性高、成本極低 ($0.05/天)、4 週內可完成 MVP、可寫論文、可做 demo。

---

*Project by: Wenyu (Eddy) Huang*
*Framework: Multi-Agent LLM + ABM + Cross-Cultural Behavioral Finance*
*Status: Proposal Stage*
*Last updated: 2026-03-16*
