# GRISI Expert Panel Review Report

**Date**: 2026-03-16
**Reviewed by**: 4-Agent Expert Panel
**Subject**: GRISI (Global Retail Investor Sentiment Index) Feasibility Assessment

---

## Panel Members

| Expert | Role | Experience |
|--------|------|-----------|
| A | Senior Quantitative Analyst | 15 yr systematic trading, alternative data |
| B | Professor of Behavioral Finance | Cross-cultural investor behavior, market microstructure |
| C | Senior AI/LLM Engineer | Production multi-agent systems, prompt engineering |
| D | Product Manager / Startup Advisor | Fintech products, B2C/B2B |

---

## Overall Scores

| Dimension | Quant (A) | Professor (B) | AI Engineer (C) | Product (D) | Avg |
|-----------|-----------|---------------|-----------------|-------------|-----|
| Feasibility | 5/10 | B+ | **8/10** | 6.5/10 | ~6.5 |
| Innovation | 7/10 | A- | High | 8/10 | **High** |
| Academic Value | 7/10 | B (publishable) | N/A | N/A | **Good** |
| Commercial Value | 3/10 | N/A | N/A | 5/10 | **Low** |
| Technical Risk | 6/10 | C+ (methods) | 8/10 (doable) | 9/10 (exec) | **Medium** |

---

## Consensus Findings (All 4 Experts Agree)

### 1. LLM 應該是「信號解釋器」，不是「信號生成器」

> **這是四位專家最一致的建議。**

- **量化師 (A)**：「用真實跨國散戶數據建構散度指標，LLM 做事後解釋。這樣量化信號來自真實數據（可回測、可復現），LLM 從信號生成降級為信號解讀。」
- **教授 (B)**：「LLM 不具備真實的認知偏誤，它只是在『演』一個有偏誤的角色。」
- **AI 工程師 (C)**：「Meta-agent 用 deterministic Python code（加權平均）比再呼叫一次 LLM 更可靠。」
- **產品顧問 (D)**：「加入至少 2-3 個真實數據源作為錨定，讓 LLM 不是憑空模擬，而是解讀真實數據。這一步對產品可信度至關重要。」

**→ 行動方案：採用 Hybrid Architecture**
```
真實數據（融資餘額、AAII、散戶淨買超...）
    → Python 計算跨國散度指標（deterministic）
    → LLM agents 解讀「為什麼？」（narrative）
    → 合併輸出：數字 + 故事
```

### 2. 回測有致命缺陷（Look-ahead Bias）

- **量化師 (A)**：「LLM 用包含歷史知識的模型訓練。餵它 2020 年 3 月的數據，它『知道』COVID 後 V 型反轉。你永遠無法做乾淨的樣本外回測。」
- **教授 (B)**：「如果 agent 行為輪廓本身就從市場文獻歸納出來，用同一市場數據驗證就是循環論證。」

**→ 行動方案：放棄歷史回測，改用 Forward Test**
- 從今天開始每天記錄
- 6 個月後才有乾淨的樣本外數據
- 用已知歷史事件做 calibration（不是 prediction）

### 3. MVP 應該聚焦 2 個市場，不是 5 個

- **量化師 (A)**：「美國有 AAII、CNN Fear & Greed；台灣有融資融券餘額（TWSE 公開資料）。把這兩個做扎實，比五個國家都做半吊子強。」
- **產品顧問 (D)**：「先贏台灣市場。你的母語優勢、PTT Stock 板、競品幾乎為零。」

**→ 行動方案：MVP = 美國 + 台灣**

### 4. 論文定位：方法論探索，不是市場預測

- **量化師 (A)**：「不是 'LLM 能預測市場'，而是 'LLM 作為文化行為模擬器的可行性探討'。」
- **教授 (B)**：「定位為 'LLM 作為跨文化行為財務實驗的計算實驗室'。核心貢獻不是預測能力，而是方法論創新。」

---

## Critical Issues Raised

### 理論框架缺漏（教授 B）

**必須補充的文獻：**

| 缺漏 | 文獻 | 為什麼重要 |
|------|------|-----------|
| 情緒指標建構 | **Baker & Wurgler (2006, 2007)** | 專案名叫「情緒指數」卻沒引用情緒指標核心文獻 |
| 噪音交易者 | **DeLong, Shleifer, Summers & Waldmann (1990)** | 散戶=noise trader 的理論基石 |
| 異質代理人 | **Hong & Stein (1999)** | 直接處理不同類型投資人如何互動 |
| 跨國羊群實證 | **Chiang & Zheng (2010)** | 直接比較不同國家的羊群強度 |
| 社群極化 | **Cookson, Engelberg & Mullins (2023)** | 社群媒體上的投資人分歧 |

**理論框架建議擴展：**
- 核心理論從「Herding」擴展為「Bounded Rational Social Learning」
- 必須區分「文化因素」vs「制度因素」（如中國的漲跌停、T+1）
- 加入 ablation study：移除文化差異設定，看結果是否還能區分

### Prompt Engineering 關鍵問題（AI 工程師 C）

**問題 1：LLM 天生會收斂到相同輸出**

不管 persona 怎麼寫，Claude 底層傾向是「理性、平衡、中立」。5 個 agent 很容易輸出幾乎一樣。

**解法：Behavioral Anchors（不是 Identity Labels）**

```
❌ "You are a conservative Japanese investor"

✅ "Decision Framework (STRICTLY FOLLOW):
    1. LOSS AVERSION: Weigh losses 3x more than gains
    2. Default state: CAUTIOUS (not NEUTRAL)
    3. Currency weakness triggers fear disproportionately
    4. When in doubt, ALWAYS choose more conservative option"
```

**問題 2：數字分數不可靠**

LLM 輸出 0-100 分數會錨定在 40-60，各 agent 差異只有 ±5。

**解法：Forced Choice + Mapping**

```
LLM 輸出: EXTREME_FEAR | FEAR | CAUTIOUS | NEUTRAL |
          CAUTIOUS_OPTIMISM | OPTIMISM | EUPHORIA
          × conviction: LOW | MEDIUM | HIGH

Python mapping: EXTREME_FEAR + HIGH = 5, FEAR + LOW = 25, etc.
```

**問題 3：必須有 Control Agent**

加一個沒有文化 persona 的 baseline agent，驗證差異來自 persona 而非 stochastic noise。用 chi-squared test 確認 output distribution 統計顯著不同。

**問題 4：使用 tool_use 強制結構化輸出**

不要在 prompt 裡要求 JSON，用 Anthropic API 的 tool_use 功能。可靠性提升 10 倍。

### 產品定位建議（產品顧問 D）

**不要先做 Dashboard，先做每日電子報。**

```
MVP 驗證路線：
1. 每天產生五國散戶情緒簡報（300 字中英文）
2. 發到 PTT Stock 板 + Twitter/X + Threads
3. Landing page 收集 email 訂閱
4. 驗證標準：30 天內能否達到 500 個 email？
   → 能 → 投資做 Dashboard
   → 不能 → Pivot
```

**最佳定位：個人品牌引擎 + 技術展示 + 學術產出**

不是 startup，而是：
1. 每天的情緒日報 → FinTwit / 台灣投資社群影響力
2. 多代理人系統 demo → 找工作/接案直接價值
3. 跨文化金融行為新方法論 → 可寫論文

---

## Revised Architecture (Based on Panel Feedback)

```
┌─────────────────────────────────────────────────────┐
│              REAL DATA LAYER (Signal)                 │
│                                                      │
│  Quantitative Indicators (deterministic, verifiable) │
│  🇺🇸 AAII Survey, Put/Call, 0DTE Volume              │
│  🇹🇼 融資餘額, 三大法人買賣超, 當沖比率              │
│  🌐 VIX, DXY, yfinance (prices + technicals)        │
│                                                      │
│  → Python: Calculate per-country retail score        │
│  → Python: Calculate cross-market divergence         │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│          LLM INTERPRETATION LAYER (Narrative)        │
│                                                      │
│  Input: Real data scores + divergence numbers        │
│                                                      │
│  5 Cultural Agents (behavioral anchor prompts):      │
│  🇺🇸 US Agent: "Why is US retail sentiment at 62?"  │
│  🇹🇼 TW Agent: "Why is TW margin at historical high?"│
│  + 1 Control Agent (no persona, baseline)            │
│                                                      │
│  Output: Cultural interpretation + reasoning         │
│  Method: tool_use + forced choice (7 levels × 3)    │
│  Sampling: 3 runs per agent, majority vote           │
└──────────────────────┬──────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────┐
│              OUTPUT LAYER                             │
│                                                      │
│  1. Per-country score (from REAL data)               │
│  2. Divergence index (from REAL data)                │
│  3. Cultural narrative (from LLM)                    │
│  4. Daily briefing (中英文, 300 words)               │
│  5. Historical comparison (forward test only)        │
└─────────────────────────────────────────────────────┘
```

---

## Revised Action Plan

### Phase 0: Prompt Validation (Week 0-1) ← NEW
- [ ] Design 2 cultural persona prompts (US + TW) + 1 control
- [ ] Use behavioral anchors, not identity labels
- [ ] Use tool_use for structured output (7 levels × 3 conviction)
- [ ] Run 30 times with fixed data → chi-squared test
- [ ] Confirm persona output distributions are statistically different
- [ ] If NOT different → iterate prompts before proceeding

### Phase 1: Data + Core Engine (Week 1-2)
- [ ] yfinance: SPY, ^TWII, 2330.TW, VIX, FX
- [ ] TWSE OpenData: 融資餘額, 三大法人 (台灣 ground truth)
- [ ] AAII sentiment scraper (美國 ground truth)
- [ ] Python: deterministic scoring from real data
- [ ] Python: divergence calculation
- [ ] LLM: cultural interpretation (2 agents + control)
- [ ] CLI output + forward test logging starts

### Phase 2: Content Distribution (Week 2-3)
- [ ] Auto-generate daily briefing (中英文 300 字)
- [ ] Publish to PTT Stock 板 / Twitter / Threads
- [ ] Landing page + email subscription (Substack/Beehiiv)
- [ ] Track: 30-day → 500 subscribers?

### Phase 3: Dashboard + Validation (Week 3-4)
- [ ] Streamlit dashboard (if content proves demand)
- [ ] Behavioral validation: agent scores vs AAII / 融資餘額 correlation
- [ ] EMA smoothing + validation layer
- [ ] Confidence intervals on display

### Phase 4: Academic Write-up (Month 2+)
- [ ] Supplement theory: Baker-Wurgler, DSSW, Hong-Stein, Chiang-Zheng
- [ ] Ablation study: remove cultural settings → still different?
- [ ] Granger causality: GRISI vs VIX/AAII
- [ ] Target: ICAIF or J. Behavioral & Experimental Finance

---

## Key Risks & Mitigations (Updated)

| Risk | Severity | Mitigation |
|------|----------|------------|
| LLM agents converge to same output | **CRITICAL** | Behavioral anchors + control agent + chi-squared validation |
| Backtest look-ahead bias | **CRITICAL** | Abandon backtest, forward test only |
| LLM ≠ real retail behavior | HIGH | Hybrid: real data for signal, LLM for narrative only |
| Trust deficit ("just AI guessing") | HIGH | Anchor in real data + transparent methodology |
| Model version drift | MEDIUM | Pin model version, calibration benchmark |
| Cultural essentialism criticism | MEDIUM | Distinguish culture vs. institution vs. market structure |

---

## One-Line Verdict from Each Expert

| Expert | Verdict |
|--------|---------|
| **Quant (A)** | 「把 LLM 從信號生成器移到信號解釋器，用真實數據建構指標。」 |
| **Professor (B)** | 「創新性 A-，但方法論需大幅強化。定位為計算實驗室，不是預測工具。」 |
| **AI Engineer (C)** | 「成敗不在 code，在 prompt。花 80% 時間設計 persona prompt + control baseline。」 |
| **Product (D)** | 「先做電子報跑 30 天，連你自己都覺得無聊就該 pivot。」 |

---

*Report compiled: 2026-03-16*
*Panel: 4 independent AI expert agents*
*Methodology: Parallel blind review, no inter-agent communication*
