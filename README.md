# GRISI

**Global Retail Investor Sentiment Index**

A daily contrarian indicator for US, Taiwan, and global markets.
When retail investors are fearful, markets tend to rise. When they're greedy, markets underperform.

> Open the dashboard. Check the score. See the historical win rate. Decide.

**[Dashboard (EN)](https://wenyuchiou.github.io/grisi/index.html)** · **[Dashboard (TW)](https://wenyuchiou.github.io/grisi/tw.html)**

---

## Latest Reading

| Market | Score | Sentiment | 20d Expected Return | Win Rate |
|--------|-------|-----------|---------------------|----------|
| US (SPY) | 32 | Cautious | +2.2% | 73% |
| TW (TAIEX) | 44 | Neutral | +0.8% | 63% |

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

### Key Result — Fear vs Greed Edge

| Quintile | SPY 20d Avg Return | TAIEX 20d Avg Return |
|----------|-------------------|---------------------|
| Q1 (Extreme Fear) | **+2.43%** | **+1.21%** |
| Q2 (Fear) | +1.39% | +1.18% |
| Q3 (Neutral) | +0.53% | +0.26% |
| Q4 (Greed) | +0.44% | +0.79% |
| Q5 (Extreme Greed) | +0.82% | +0.40% |

Backtest period: 2010–2026 (16 years). IC = -0.175 (p < 0.0001).

---

## Supported Markets

| Market | Status | Data Source |
|--------|--------|------------|
| US (SPY) | Live | Yahoo Finance |
| Taiwan (TAIEX) | Live | Yahoo Finance + FinMind (TWSE) |
| Japan (Nikkei) | Planned | — |
| Korea (KOSPI) | Planned | — |
| Europe (STOXX) | Planned | — |

---

## Data Sources

| Data | Source | Frequency |
|------|--------|-----------|
| US prices (SPY, VIX, Gold, 10Y) | Yahoo Finance | Daily |
| TW prices (TAIEX, TSMC) | Yahoo Finance | Daily |
| TW margin balance | FinMind / TWSE OpenData | Daily |
| TW institutional flows | FinMind / TWSE OpenData | Daily |
| Behavioral parameters | Prospect Theory (Kahneman & Tversky, 1979) | Static |

---

## Auto-Update

GitHub Actions runs Mon–Fri at 22:00 UTC (6PM ET / 6AM TWN):
1. Pulls latest market data from all sources
2. Updates scoring JSON files
3. Syncs to dashboard
4. Commits and pushes

Agent narrative (cultural sentiment analysis) is updated by Claude.

---

## Structure

```
docs/         Dashboard (GitHub Pages)
data/         Market data + scoring results
src/          Python scoring engine + pipelines
.github/      Daily auto-update workflow
```

---

## Disclaimer

Not financial advice. GRISI is a research tool based on historical patterns. Past performance does not guarantee future results.
