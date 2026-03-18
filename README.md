# GRISI

**Global Retail Investor Sentiment Index**

A daily contrarian indicator for 5 global markets, powered by behavioral finance + AI.

**[Dashboard (EN)](https://wenyuchiou.github.io/grisi/index.html)** · **[Dashboard (中文)](https://wenyuchiou.github.io/grisi/tw.html)**

---

## What Makes This Different

| | CNN Fear & Greed | AAII Survey | **GRISI** |
|--|-----------------|------------|-----------|
| Method | 7 fixed indicators | Weekly poll | **Rolling Z-score + behavioral adjustment** |
| Markets | US only | US only | **US, TW, JP, KR, EU** |
| Forward returns | No | No | **Yes — "at this score, what happened historically?"** |
| Behavioral model | No | No | **Loss aversion, FOMO, herding, anchoring** |
| Retail investor voice | No | No | **AI simulates how retail investors think** |
| Sell signal | Weak | None | **TW Greed >70 = near-zero return** |
| Backtested IC | Not published | Weak | **IC = -0.175 (p < 0.0001)** |
| Update | Daily | Weekly | **Daily (automated)** |

### Behavioral Indicators (not just price-based)

Traditional indices use price/volume data. GRISI adds a **behavioral adjustment layer** based on academic research:

| Parameter | Theory | US Value | TW Value | Effect |
|-----------|--------|----------|----------|--------|
| Loss Aversion | Kahneman & Tversky (1979) | 2.0x | 2.8x | Fear amplified more than greed |
| Herding | Banerjee (1992) | 0.60 | 0.80 | TW retail follows crowd more |
| FOMO | Behavioral Finance | 0.30 | 0.30 | Activates near ATH with momentum |
| Anchoring | Tversky & Kahneman (1974) | 0.50 | 0.75 | TW fixated on round numbers |
| Overconfidence | Barber & Odean (2001) | 0.30 | 0.00 | US retail thinks they're smarter |

These parameters only activate at **extreme scores** (conditional gates), adding zero noise during normal markets.

---

## Latest Reading

| Market | Score | Sentiment | 20d Expected Return | Win Rate |
|--------|-------|-----------|---------------------|----------|
| US (SPY) | 32 | Cautious | +1.80% | 66% |
| TW (TAIEX) | 44 | Neutral | -0.21% | 60% |
| JP (Nikkei) | 33 | Cautious | +1.69% | 67% |
| KR (KOSPI) | 35 | Cautious | +1.17% | 65% |
| EU (STOXX50) | 33 | Cautious | +1.38% | 65% |

## Extreme Fear Returns (10yr, 2016–2026)

| Market | 20d Avg | Win Rate |
|--------|---------|----------|
| Korea (KOSPI) | **+9.16%** | **85%** |
| Taiwan (TAIEX) | +6.45% | 87% |
| Japan (Nikkei) | +5.81% | 75% |
| Europe (STOXX50) | +4.28% | 77% |
| US (SPY) | +4.17% | 72% |

## How It Works

```
Market data (Yahoo Finance, FinMind)
  → 5 Z-score indicators per market (252-day rolling, no lookahead)
  → Behavioral adjustment (loss aversion × FOMO × herding)
  → Score 0–100 (high = greedy, low = fearful)
  → Historical forward return lookup
  → AI retail investor voice: "what are retail investors thinking right now?"
```

## Data Sources

| Data | Source |
|------|--------|
| US, JP, KR, EU prices | Yahoo Finance |
| TW prices + margin + institutional flows | Yahoo Finance + FinMind (TWSE) |
| Behavioral parameters | Prospect Theory literature |

---

*Not financial advice. Past performance ≠ future results.*
