# GRISI

**Global Retail Investor Sentiment Index**

A daily contrarian indicator for US and Taiwan markets.
When retail investors are fearful, markets tend to rise. When they're greedy, markets underperform.

> Open the dashboard → check the score → see the historical win rate at this level → decide.

**[🇺🇸 US Dashboard](https://wenyuchiou.github.io/grisi/index.html)** · **[🇹🇼 台灣 Dashboard](https://wenyuchiou.github.io/grisi/tw.html)**

---

## Today's Reading

| Market | Score | Sentiment | 20d Expected Return | Win Rate |
|--------|-------|-----------|---------------------|----------|
| 🇺🇸 US (SPY) | 32 | Cautious | +2.2% | 73% |
| 🇹🇼 TW (TAIEX) | 44 | Neutral | +0.8% | 63% |

*Updated: 2026-03-17. Auto-updates Mon–Fri via GitHub Actions.*

---

## How It Works

```
Public market data (Yahoo Finance, FinMind)
  → 5 indicators per market
  → Z-score normalized (252-day rolling, no lookahead)
  → Behavioral adjustment at extremes
  → Score 0–100
  → Forward return lookup: "At this score, what happened historically?"
```

### Scoring Components

| US (SPY) | TW (TAIEX) |
|----------|------------|
| VIX complacency | US 10Y rate pressure |
| SPY vs 52W high | Gold/SPY risk appetite |
| 20d momentum | Realized volatility |
| VIX-SPY correlation | TAIEX vs 52W high |
| Gold/SPY ratio | Volume surge |

### Key Result

Buying in **Extreme Fear** (Q1) vs **Extreme Greed** (Q5):

| | Q1 (Fear) | Q5 (Greed) | Edge |
|--|-----------|------------|------|
| SPY 20d | +2.43% | +0.82% | **+1.61%** |
| TAIEX 20d | +1.21% | +0.40% | **+0.81%** |

Backtest: 2010–2026 (16 years), IC = -0.175 (p < 0.0001).

---

## Data Sources

| Data | Source | Frequency |
|------|--------|-----------|
| US prices (SPY, VIX, Gold, 10Y) | Yahoo Finance | Daily |
| TW prices (TAIEX, TSMC) | Yahoo Finance | Daily |
| TW margin balance (融資餘額) | FinMind / TWSE | Daily |
| TW institutional flows (三大法人) | FinMind / TWSE | Daily |
| Behavioral parameters | Prospect Theory (Kahneman & Tversky, 1979) | Static |

---

## Structure

```
docs/         Dashboard (GitHub Pages)
data/         Market data + scoring results
src/          Python scoring engine + pipelines
.github/      Daily auto-update (Mon–Fri 22:00 UTC)
```

---

*Not financial advice. Past performance ≠ future results.*
