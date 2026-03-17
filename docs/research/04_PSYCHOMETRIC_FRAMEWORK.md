# GRISI Psychometric Framework

**用心理測量學問卷校準 Agent 行為參數**

---

## 核心概念

不是直接寫「你是保守的日本投資者」這種 persona，而是：

1. 設計一份基於**已驗證心理量表**的投資者行為問卷
2. 讓每個國家的 Agent 以該國典型散戶的身份**填寫問卷**
3. 問卷結果量化成**行為參數**（如 loss aversion = 2.5x, herding = 0.8）
4. 這些參數直接驅動 Agent 的決策邏輯

```
傳統做法：
  "You are a conservative Japanese investor" → LLM 自由發揮 → 不可控

心理測量做法：
  問卷 → 量化行為參數 → 參數驅動決策規則 → 可驗證、可比較
```

---

## Part 1: 選用的心理量表

### 1.1 Financial Risk Tolerance Scale (FRTS)
**來源**: Grable & Lytton (1999), Journal of Financial Planning
**用途**: 測量投資者的風險容忍度
**題數**: 13 題
**已驗證**: Cronbach's α = 0.77

**範例題目**:
```
Q1: 你目前有一份穩定的工作收入。你的雇主提供兩種年終獎金方案：
    A) 確定拿到 50,000 元
    B) 50% 機率拿到 100,000 元，50% 機率拿到 0 元
    你會選？ [A / B]

Q2: 你的投資組合在一個月內下跌了 15%。你會：
    A) 立即全部賣出，避免更大損失
    B) 賣掉一半，保留一半
    C) 不動，等待反彈
    D) 加碼買入，趁低吸納

Q3: 你可以接受的最大單年虧損是多少？
    A) 0%（完全不能虧損）
    B) -5%
    C) -10%
    D) -20%
    E) -30% 或更多
```

### 1.2 Behavioral Biases Questionnaire (BBQ)
**來源**: 基於 Pompian (2012) "Behavioral Finance and Wealth Management"
**用途**: 測量各種認知偏誤的強度

**維度與題目**:

#### A. Loss Aversion (損失趨避) — 3 題
```
LA1: 假設你持有一支股票，買入成本 100 元，現在跌到 85 元。
     分析師說有 60% 機率回到 100 元，40% 機率跌到 70 元。你會：
     1) 立即賣出鎖住虧損 (低 LA)
     2) 繼續持有等反彈 (中 LA)
     3) 絕對不賣，虧損太痛苦了 (高 LA)
     4) 不但不賣，還想加碼攤平 (極高 LA)

LA2: 以下哪個情境讓你感受更強烈？
     A) 賺到 10,000 元的快樂
     B) 虧掉 10,000 元的痛苦
     → 請在 1-7 的量表上評分：
       1 = 賺錢的快樂遠大於虧錢的痛苦
       4 = 一樣
       7 = 虧錢的痛苦遠大於賺錢的快樂

LA3: 當你的投資組合出現未實現虧損時，你查看帳戶的頻率會：
     1) 更頻繁（擔心虧更多）
     2) 不變
     3) 更少（不想面對虧損）
```

#### B. Herding Tendency (羊群傾向) — 4 題
```
HT1: 你在考慮買一支股票。以下哪個因素最影響你的決定？
     1) 自己的研究分析 (低 herding)
     2) 專業分析師的建議 (中 herding)
     3) 身邊朋友/同事都在買 (高 herding)
     4) 社群平台上大家都在討論 (很高 herding)
     5) 看到新聞說「散戶搶買」(極高 herding)

HT2: 如果你做了一個投資決策，後來發現大部分人都做了相反的決定。
     你的反應是：
     1) 更加確信自己是對的 — 大眾通常是錯的 (反向)
     2) 稍微不安但維持原來決定 (低 herding)
     3) 開始動搖，認真考慮改變 (中 herding)
     4) 很焦慮，可能會跟著大多數人走 (高 herding)
     5) 立刻改變決定 — 這麼多人不可能都錯 (極高 herding)

HT3: 你的 LINE/KakaoTalk/WeChat 投資群組正在熱烈討論一支飆股。
     群組裡 8 個人中有 6 個已經買了。你會：
     1) 完全不受影響 (低)
     2) 會去了解一下，但不一定買 (中)
     3) 認真考慮跟著買 (高)
     4) 趕快買，怕錯過 (FOMO)

HT4: 過去一年，你有多少次因為「別人都在買」而買入一支股票？
     1) 0 次
     2) 1-2 次
     3) 3-5 次
     4) 6 次以上
     5) 大部分時候都是這樣
```

#### C. Overconfidence (過度自信) — 3 題
```
OC1: 你認為你的投資績效相比一般散戶投資者如何？
     1) 遠低於平均
     2) 略低於平均
     3) 大約平均
     4) 略高於平均
     5) 遠高於平均

OC2: 你估計明年台股/美股大盤的報酬率是多少？
     你對這個預測有多確定？(1-7 scale)
     1 = 完全不確定，可能差很遠
     7 = 非常確定，誤差不會超過 5%

OC3: 過去一年，你的實際投資報酬率跟你的預期差距大嗎？
     1) 比預期好很多
     2) 比預期好一些
     3) 跟預期差不多
     4) 比預期差一些
     5) 比預期差很多
```

#### D. FOMO (Fear of Missing Out) — 3 題
```
FM1: 當你看到一支股票已經連漲 5 天、漲幅超過 20%：
     1) 我會避開 — 已經漲太多了 (低 FOMO)
     2) 我會觀望，看看會不會回調再買 (中 FOMO)
     3) 我會有很強的衝動想買進 (高 FOMO)
     4) 我幾乎無法抑制買進的衝動 (極高 FOMO)

FM2: 你的朋友告訴你他靠某支股票賺了 50%。你的第一反應是：
     1) 恭喜他，跟我無關 (低)
     2) 有點羨慕但不會行動 (中)
     3) 認真研究那支股票 (高)
     4) 想立刻買入同一支 (極高)

FM3: 在過去一年中，你有多少次因為「怕錯過上漲」而匆忙買入？
     1) 0 次
     2) 1-2 次
     3) 3-5 次
     4) 6 次以上
```

#### E. Anchoring (錨定效應) — 2 題
```
AN1: 你買了一支股票，成本 100 元。現在股價 80 元，
     但公司基本面惡化，分析師目標價下修到 60 元。你會：
     1) 立即賣出 (低 anchoring)
     2) 等回到 90 元再賣 (中 anchoring)
     3) 一定要等回到成本 100 元才賣 (高 anchoring)
     4) 加碼攤平到更低成本 (極高 anchoring)

AN2: 判斷一支股票是否「便宜」時，你最常參考：
     1) 本益比、股價淨值比等估值指標 (低 anchoring)
     2) 52 週高低點 (中 anchoring)
     3) 自己之前的買入價 (高 anchoring)
     4) 歷史最高價 (高 anchoring)
```

#### F. Information Source Dependency (資訊依賴) — 2 題
```
IS1: 你做投資決策前，最依賴哪種資訊來源？（排序前三）
     a) 公司財報/基本面分析
     b) 技術分析圖表
     c) 財經新聞媒體
     d) 社群平台 (PTT/Reddit/雪球/Naver)
     e) 親友/投資群組推薦
     f) 專業分析師報告
     g) YouTube/Podcast KOL
     h) 政府/央行政策公告

IS2: 如果你常用的資訊來源和自己的分析結論矛盾，你會：
     1) 相信自己的分析 (低依賴)
     2) 重新檢視，但傾向相信自己 (中低)
     3) 50/50，很難決定 (中)
     4) 傾向相信外部資訊 (中高)
     5) 幾乎一定跟著外部資訊走 (高依賴)
```

---

## Part 2: 各國 Agent 的問卷預設答案

基於學術文獻和市場觀察，設定每個國家典型散戶的答案：

### 問卷評分對照表

| 量表維度 | 🇺🇸 US Agent | 🇹🇼 TW Agent | (Phase 2: 🇨🇳 CN) | (Phase 2: 🇰🇷 KR) | (Phase 2: 🇯🇵 JP) |
|---------|-------------|-------------|-------------|-------------|-------------|
| **Risk Tolerance** | 65/100 (中高) | 45/100 (中) | 55/100 (中) | 75/100 (高) | 25/100 (低) |
| **Loss Aversion** | 3.5/7 (中) | 5.0/7 (高) | 3.0/7 (低) | 4.0/7 (中高) | 6.0/7 (很高) |
| **Herding** | 3.0/5 (中) | 4.0/5 (高) | 4.8/5 (極高) | 4.5/5 (很高) | 2.0/5 (低) |
| **Overconfidence** | 4.5/5 (高) | 3.0/5 (中) | 4.0/5 (高) | 5.0/5 (極高) | 2.0/5 (低) |
| **FOMO** | 3.5/4 (中高) | 3.5/4 (中高) | 4.0/4 (極高) | 4.0/4 (極高) | 1.5/4 (低) |
| **Anchoring** | 2.5/4 (中) | 3.5/4 (高) | 2.0/4 (低) | 2.5/4 (中) | 3.0/4 (中高) |
| **Info Source** | Social+Media | Tech+KOL | Policy+Social | Social+Momentum | Trad.Media+Books |

### 學術依據

| 參數 | 來源 |
|------|------|
| US Risk Tolerance 中高 | Barber & Odean (2001): US retail trades excessively |
| TW Herding 高 | Barber, Lee, Liu, Odean (2009): Taiwan evidence |
| CN Herding 極高 | Tan et al. (2008): Chinese stock market herding |
| KR Overconfidence 極高 | 빚투 culture, KRX retail leverage data |
| JP Loss Aversion 很高 | Post-bubble risk aversion, NISA slow adoption |

---

## Part 3: 問卷分數 → Agent 行為參數

### 轉換公式

```python
def questionnaire_to_params(scores):
    """將問卷分數轉換為 Agent 決策參數"""
    return {
        # Loss aversion multiplier: 1x (neutral) to 4x (extreme)
        "loss_aversion_multiplier": 1 + (scores["loss_aversion"] / 7) * 3,

        # Herding weight: 0 (independent) to 1 (pure follower)
        "herding_weight": scores["herding"] / 5,

        # Confidence adjustment: -0.5 (under) to +0.5 (over)
        "confidence_adj": (scores["overconfidence"] - 3) / 5,

        # FOMO trigger threshold: 0.1 (easy trigger) to 0.9 (hard trigger)
        "fomo_threshold": 1 - (scores["fomo"] / 4),

        # Anchoring strength: 0 (none) to 1 (strong)
        "anchoring_strength": scores["anchoring"] / 4,

        # Default sentiment state (based on risk tolerance)
        "default_state": map_risk_to_default(scores["risk_tolerance"]),

        # Sentiment shift sensitivity
        "shift_sensitivity": calculate_sensitivity(scores),
    }

def map_risk_to_default(risk_score):
    """Risk tolerance → default sentiment state"""
    if risk_score >= 70: return "CAUTIOUS_OPTIMISM"  # High risk = default bullish
    if risk_score >= 50: return "NEUTRAL"
    if risk_score >= 30: return "CAUTIOUS"
    return "FEAR"                                     # Very low risk = default fearful
```

### 各國 Agent 的具體參數

```python
US_AGENT_PARAMS = {
    "loss_aversion_multiplier": 2.0,   # 中等
    "herding_weight": 0.6,             # 中等
    "confidence_adj": +0.3,            # 偏高
    "fomo_threshold": 0.3,             # 容易觸發
    "anchoring_strength": 0.5,         # 中等
    "default_state": "CAUTIOUS_OPTIMISM",
    "shift_sensitivity": 1.0,          # baseline
}

TW_AGENT_PARAMS = {
    "loss_aversion_multiplier": 2.8,   # 偏高
    "herding_weight": 0.8,             # 高
    "confidence_adj": 0.0,             # 中等
    "fomo_threshold": 0.3,             # 容易觸發
    "anchoring_strength": 0.75,        # 高
    "default_state": "NEUTRAL",
    "shift_sensitivity": 1.2,          # 比美國敏感
}
```

---

## Part 4: 參數驅動的 Agent Prompt

不再寫 "you are conservative"，而是**將量化參數直接嵌入 prompt**：

```
## Your Behavioral Parameters (derived from psychometric assessment)

You have been calibrated with the following behavioral parameters.
These parameters MUST govern your decision-making:

LOSS_AVERSION: 2.8x
→ A potential loss of $100 feels as painful as missing a gain of $280
→ When you see negative signals, weight them 2.8x more than positive signals

HERDING_WEIGHT: 0.80
→ 80% of your conviction comes from what others are doing
→ If margin balance is increasing (others buying), this STRONGLY pushes you toward BUY
→ If foreign investors are selling, this moderately pushes you toward SELL

FOMO_THRESHOLD: 0.30
→ You are easily triggered by fear of missing out
→ When market has risen > 5% in a week, you feel strong urge to buy
→ When others report gains, your FOMO activates

ANCHORING: 0.75
→ You heavily anchor to reference prices
→ TSMC at 1845 vs 52W high of 2015: you see this as "15% discount" (opportunity)
→ TAIEX at 33342 vs 52W high of 35440: you see "room to recover"

DEFAULT_STATE: NEUTRAL
→ Without strong signals, you default to NEUTRAL (not optimistic like US)

SHIFT_SENSITIVITY: 1.2x
→ You react more strongly to new information than baseline
→ Each signal shifts your sentiment 1.2x the normal amount

Given these parameters, analyze the following market data...
```

---

## Part 5: 驗證方法

### 5.1 問卷交叉驗證

**做法**：找 20-30 個真實的台灣/美國散戶填寫同一份問卷。
比較：
- 真實散戶的平均分數 vs Agent 的預設分數
- 如果差距太大 → 調整 Agent 的預設分數

### 5.2 行為一致性驗證

**做法**：用歷史市場數據餵 Agent，看它的決策是否符合該國散戶的實際行為。

```
2020-03-16 (COVID 底部):
- US Agent 應該恐慌但有 "buy the dip" 衝動 (FOMO 觸發)
- TW Agent 應該恐慌且被 herding 推向賣出 (融資斷頭)
- JP Agent 應該極度恐慌 (loss aversion 最高)
```

### 5.3 Ablation Study

**做法**：
1. Full model: 使用問卷校準的行為參數
2. Ablated model A: 所有 agent 用相同參數 (移除文化差異)
3. Ablated model B: 不用參數，只用 identity label ("you are Japanese")

比較三者的 output distribution → 證明問卷參數確實產生有意義的差異。

---

## Part 6: 學術價值

這個方法論本身就是一個貢獻：

> **"Psychometric Calibration of LLM Agents for Cross-Cultural Financial Behavior Simulation"**

1. 將心理測量學的量表應用到 LLM agent 校準 — 這是新方法
2. 提供可量化、可比較、可驗證的 agent 行為參數
3. 避免文化本質主義 — 每個參數都有學術文獻支持
4. 可重複性高 — 任何人用同樣的問卷分數都能重現同樣的 agent

---

## 引用的心理量表

1. Grable, J.E. & Lytton, R.H. (1999). Financial risk tolerance revisited. *Financial Services Review*, 8(3), 163-181.
2. Pompian, M.M. (2012). *Behavioral Finance and Wealth Management* (2nd ed.). Wiley.
3. Weber, E.U., Blais, A.R., & Betz, N.E. (2002). A domain-specific risk-attitude scale: Measuring risk perceptions and risk behaviors. *Journal of Behavioral Decision Making*, 15(4), 263-290.
4. Prosad, J.M., Kapoor, S., & Sengupta, J. (2015). Behavioral biases of Indian investors: a survey of Delhi-NCR region. *Qualitative Research in Financial Markets*, 7(3), 230-263.

---

*This framework provides the psychometric foundation for GRISI agent calibration.*
*Last updated: 2026-03-16*
