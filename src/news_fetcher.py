"""
Moodring News Fetcher
=====================
Fetches financial news from Jin10, Yahoo Finance RSS, and CNBC RSS.
Scores each item for relevance, sentiment, impact, and hypothesis mapping.

Usage:
  python news_fetcher.py          # Print JSON to stdout
  from news_fetcher import fetch_news
"""

import json
import re
import logging
from datetime import datetime, timezone
from typing import Optional

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Keyword definitions
# ---------------------------------------------------------------------------

# Geopolitical / Iran / War
GEO_KEYWORDS = [
    "iran", "伊朗", "war", "戰爭", "military", "軍事", "strike", "攻擊",
    "missile", "飛彈", "airstrike", "空襲", "conflict", "衝突",
    "sanction", "制裁", "hamas", "hezbollah", "中東", "middle east",
    "escalation", "升級", "nuclear", "核武", "drone", "無人機",
    "israel", "以色列", "ukraine", "烏克蘭", "russia", "俄羅斯",
    "north korea", "北韓", "taiwan strait", "台海",
]

# Fed / Monetary policy
FED_KEYWORDS = [
    "fed", "federal reserve", "fomc", "聯準會", "powell", "鮑威爾",
    "rate hike", "rate cut", "升息", "降息", "interest rate", "利率",
    "monetary policy", "貨幣政策", "quantitative", "QE", "QT",
    "tapering", "balance sheet", "資產負債表", "inflation", "通膨",
    "cpi", "pce", "核心通膨", "hawkish", "鷹派", "dovish", "鴿派",
    "dot plot", "fomc minutes", "회의록",
]

# AI / Tech bubble
AI_KEYWORDS = [
    "ai", "artificial intelligence", "人工智慧", "chatgpt", "openai",
    "nvidia", "nvda", "amd", "semiconductor", "半導體", "chip", "晶片",
    "tech bubble", "科技泡沫", "valuation", "估值", "overvalued", "高估",
    "microsoft", "google", "alphabet", "meta", "amazon", "apple",
    "mag7", "magnificent", "growth stock", "成長股", "nasdaq", "那斯達克",
    "hyperscaler", "data center", "資料中心", "llm", "large language",
]

# Oil / Energy
OIL_KEYWORDS = [
    "oil", "原油", "crude", "brent", "wti", "opec", "能源", "energy",
    "petroleum", "gasoline", "天然氣", "natural gas", "lng",
    "oil price", "油價", "refinery", "煉油", "barrel", "桶",
    "shale", "頁岩油", "pipeline", "輸油管", "supply cut", "減產",
    "oil shock", "油價衝擊",
]

# Recession / Jobs / Macro
RECESSION_KEYWORDS = [
    "recession", "衰退", "gdp", "growth", "經濟成長", "slowdown", "放緩",
    "unemployment", "失業", "jobs", "就業", "payroll", "非農", "nonfarm",
    "consumer confidence", "消費者信心", "retail sales", "零售",
    "manufacturing", "製造業", "pmi", "ism", "housing", "房市",
    "yield curve", "殖利率曲線", "inversion", "倒掛", "default", "違約",
    "credit", "信貸", "bank", "銀行", "financial stress", "金融壓力",
    "soft landing", "軟著陸", "hard landing", "硬著陸",
]

# Bullish signals
BULLISH_KEYWORDS = [
    "surge", "rally", "gain", "rise", "soar", "jump", "beat", "exceed",
    "record high", "breakout", "upgrade", "buy", "bullish", "optimism",
    "上漲", "大漲", "突破", "創高", "買進", "樂觀", "強勁", "好於預期",
    "recovery", "rebound", "bounce", "positive", "upbeat",
]

# Bearish signals
BEARISH_KEYWORDS = [
    "crash", "plunge", "fall", "drop", "tumble", "sink", "miss", "below",
    "downgrade", "sell", "bearish", "pessimism", "fear", "panic",
    "下跌", "暴跌", "崩盤", "賣出", "悲觀", "恐慌", "疲弱", "差於預期",
    "warning", "risk", "concern", "worry", "threat", "危機", "風險",
]

# High-relevance equity/options terms (boost score)
EQUITY_KEYWORDS = [
    "spy", "s&p 500", "標普", "nasdaq", "道瓊", "dow jones",
    "vix", "volatility", "波動率", "options", "選擇權",
    "futures", "期貨", "market", "股市", "stock", "equity",
    "earnings", "財報", "eps", "revenue", "營收",
]


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _text_lower(headline: str, description: str = "") -> str:
    return (headline + " " + description).lower()


def compute_relevance_score(text: str) -> int:
    """Score 1–10 based on US equity/options keyword density."""
    score = 3  # baseline
    t = text.lower()

    hit_equity = sum(1 for kw in EQUITY_KEYWORDS if kw in t)
    hit_geo = sum(1 for kw in GEO_KEYWORDS if kw in t)
    hit_fed = sum(1 for kw in FED_KEYWORDS if kw in t)
    hit_ai = sum(1 for kw in AI_KEYWORDS if kw in t)
    hit_oil = sum(1 for kw in OIL_KEYWORDS if kw in t)
    hit_rec = sum(1 for kw in RECESSION_KEYWORDS if kw in t)

    score += min(hit_equity * 2, 4)
    score += min((hit_geo + hit_fed + hit_ai + hit_oil + hit_rec), 3)

    return min(max(score, 1), 10)


def compute_sentiment(text: str) -> str:
    t = text.lower()
    bull = sum(1 for kw in BULLISH_KEYWORDS if kw in t)
    bear = sum(1 for kw in BEARISH_KEYWORDS if kw in t)
    if bear > bull:
        return "bearish"
    elif bull > bear:
        return "bullish"
    return "neutral"


def compute_impact(text: str, sentiment: str) -> dict:
    """Estimate rough SPY % move and VIX point change."""
    t = text.lower()

    # Base magnitude from relevance
    rel = compute_relevance_score(text)
    base_spy = round(rel * 0.06, 2)   # up to ~0.6% per point
    base_vix = round(rel * 0.25, 2)   # up to ~2.5 pts

    # Amplify for high-impact themes
    if any(kw in t for kw in ["war", "戰爭", "strike", "攻擊", "nuclear", "核武", "missile"]):
        base_spy *= 1.8
        base_vix *= 2.0
    if any(kw in t for kw in ["recession", "衰退", "crash", "崩盤"]):
        base_spy *= 1.5
        base_vix *= 1.6
    if any(kw in t for kw in ["rate hike", "升息", "hawkish", "鷹派"]):
        base_spy *= 1.3
        base_vix *= 1.2

    spy_sign = -1 if sentiment == "bearish" else (1 if sentiment == "bullish" else 0)
    vix_sign = 1 if sentiment == "bearish" else (-1 if sentiment == "bullish" else 0)

    return {
        "spy": round(spy_sign * base_spy, 2),
        "vix": round(vix_sign * base_vix, 2),
    }


def compute_hypotheses(text: str) -> list:
    """Map to H1–H5 hypotheses."""
    t = text.lower()
    hyps = []
    if any(kw in t for kw in GEO_KEYWORDS):
        hyps.append("H1")
    if any(kw in t for kw in FED_KEYWORDS):
        hyps.append("H2")
    if any(kw in t for kw in AI_KEYWORDS):
        hyps.append("H3")
    if any(kw in t for kw in OIL_KEYWORDS):
        hyps.append("H4")
    if any(kw in t for kw in RECESSION_KEYWORDS):
        hyps.append("H5")
    return hyps


def compute_category(text: str) -> str:
    t = text.lower()
    geo_hits = sum(1 for kw in GEO_KEYWORDS if kw in t)
    fed_hits = sum(1 for kw in FED_KEYWORDS if kw in t)
    ai_hits = sum(1 for kw in AI_KEYWORDS if kw in t)
    oil_hits = sum(1 for kw in OIL_KEYWORDS if kw in t)
    rec_hits = sum(1 for kw in RECESSION_KEYWORDS if kw in t)

    # Earnings detection
    if any(kw in t for kw in ["earnings", "eps", "revenue", "財報", "q1", "q2", "q3", "q4", "quarterly"]):
        return "earnings"

    scores = {
        "geopolitical": geo_hits,
        "policy": fed_hits,
        "technical": ai_hits,
        "macro": rec_hits + oil_hits,
    }
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "macro"
    return best


def _build_item(
    time_str: str,
    source: str,
    headline: str,
    description: str = "",
) -> dict:
    text = headline + " " + description
    sentiment = compute_sentiment(text)
    return {
        "time": time_str,
        "source": source,
        "headline": headline,
        "relevance_score": compute_relevance_score(text),
        "sentiment": sentiment,
        "impact": compute_impact(text, sentiment),
        "related_hypotheses": compute_hypotheses(text),
        "category": compute_category(text),
    }


# ---------------------------------------------------------------------------
# Source: Yahoo Finance RSS
# ---------------------------------------------------------------------------

def _fetch_yahoo() -> list:
    try:
        import feedparser  # type: ignore
    except ImportError:
        logger.warning("feedparser not installed; skipping Yahoo Finance")
        return []

    url = "https://finance.yahoo.com/news/rssindex"
    try:
        import socket as _socket
        old_timeout = _socket.getdefaulttimeout()
        _socket.setdefaulttimeout(10)
        try:
            feed = feedparser.parse(url)
        finally:
            _socket.setdefaulttimeout(old_timeout)
        items = []
        for entry in feed.entries[:30]:
            headline = entry.get("title", "").strip()
            description = entry.get("summary", "")
            if not headline:
                continue
            # Parse publish time
            published = entry.get("published_parsed")
            if published:
                ts = datetime(*published[:6], tzinfo=timezone.utc)
                time_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            items.append(_build_item(time_str, "yahoo", headline, description))
        return items
    except Exception as e:
        logger.warning(f"Yahoo Finance fetch failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Source: CNBC RSS
# ---------------------------------------------------------------------------

def _fetch_cnbc() -> list:
    try:
        import feedparser  # type: ignore
    except ImportError:
        logger.warning("feedparser not installed; skipping CNBC")
        return []

    url = "https://www.cnbc.com/id/100003114/device/rss/rss.html"
    try:
        import socket as _socket
        old_timeout = _socket.getdefaulttimeout()
        _socket.setdefaulttimeout(10)
        try:
            feed = feedparser.parse(url)
        finally:
            _socket.setdefaulttimeout(old_timeout)
        items = []
        for entry in feed.entries[:30]:
            headline = entry.get("title", "").strip()
            description = entry.get("summary", "")
            if not headline:
                continue
            published = entry.get("published_parsed")
            if published:
                ts = datetime(*published[:6], tzinfo=timezone.utc)
                time_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
            else:
                time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            items.append(_build_item(time_str, "cnbc", headline, description))
        return items
    except Exception as e:
        logger.warning(f"CNBC fetch failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Source: Jin10 (金十數據)
# ---------------------------------------------------------------------------

def _fetch_jin10() -> list:
    """
    Attempt to scrape Jin10 flash news from datacenter.jin10.com.
    Falls back to HTML scraping of jin10.com/flash if API fails.
    Gracefully skips on any error.
    """
    try:
        import requests  # type: ignore
        from bs4 import BeautifulSoup  # type: ignore
    except ImportError:
        logger.warning("requests/beautifulsoup4 not installed; skipping Jin10")
        return []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": "https://www.jin10.com/",
    }

    # --- Attempt 1: datacenter API ---
    try:
        api_url = "https://datacenter.jin10.com/flash_newest/0"
        resp = requests.get(api_url, headers=headers, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        items = []
        entries = data if isinstance(data, list) else data.get("data", [])
        for entry in entries[:30]:
            headline = entry.get("title", "") or entry.get("content", "")
            headline = re.sub(r"<[^>]+>", "", headline).strip()
            if not headline:
                continue
            ts_raw = entry.get("time", entry.get("created_at", ""))
            try:
                ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                time_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
            except Exception:
                time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            items.append(_build_item(time_str, "jin10", headline))
        if items:
            return items
    except Exception as e:
        logger.info(f"Jin10 datacenter API failed ({e}), trying HTML scrape")

    # --- Attempt 2: HTML scraping of jin10.com/flash ---
    try:
        html_url = "https://www.jin10.com/flash_newest.html"
        resp = requests.get(html_url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        items = []
        # Jin10 flash items are typically in <div class="jin-flash-item"> or similar
        for tag in soup.find_all(["div", "li"], class_=re.compile(r"flash|item|news")):
            text_el = tag.find(["p", "span", "a"])
            if not text_el:
                continue
            headline = text_el.get_text(strip=True)
            if len(headline) < 5:
                continue
            # Try to find timestamp
            time_el = tag.find(["time", "span"], class_=re.compile(r"time|date"))
            if time_el:
                raw_time = time_el.get_text(strip=True)
                try:
                    # Format: HH:MM or YYYY-MM-DD HH:MM
                    if re.match(r"^\d{2}:\d{2}$", raw_time):
                        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
                        time_str = f"{today}T{raw_time}:00"
                    else:
                        ts = datetime.fromisoformat(raw_time)
                        time_str = ts.strftime("%Y-%m-%dT%H:%M:%S")
                except Exception:
                    time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                time_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

            items.append(_build_item(time_str, "jin10", headline))
            if len(items) >= 20:
                break

        return items
    except Exception as e:
        logger.warning(f"Jin10 HTML scrape failed: {e}")
        return []


# ---------------------------------------------------------------------------
# Summary computation
# ---------------------------------------------------------------------------

def _compute_top_theme(items: list) -> str:
    """Pick top theme label in 繁體中文 based on hypothesis frequency."""
    from collections import Counter
    hyp_counts: Counter = Counter()
    for item in items:
        for h in item.get("related_hypotheses", []):
            hyp_counts[h] += 1

    if not hyp_counts:
        return "一般市場動態"

    top = hyp_counts.most_common(1)[0][0]
    mapping = {
        "H1": "地緣政治風險",
        "H2": "聯準會政策轉向",
        "H3": "AI科技泡沫",
        "H4": "油價衝擊",
        "H5": "經濟衰退疑慮",
    }
    return mapping.get(top, "一般市場動態")


def _build_summary(items: list) -> dict:
    bullish = sum(1 for i in items if i["sentiment"] == "bullish")
    bearish = sum(1 for i in items if i["sentiment"] == "bearish")
    avg_rel = (
        round(sum(i["relevance_score"] for i in items) / len(items), 1)
        if items
        else 0.0
    )
    return {
        "bullish_count": bullish,
        "bearish_count": bearish,
        "neutral_count": len(items) - bullish - bearish,
        "total_items": len(items),
        "avg_relevance": avg_rel,
        "top_theme": _compute_top_theme(items),
    }


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def fetch_news() -> dict:
    """
    Fetch news from Jin10, Yahoo Finance, and CNBC.
    Returns structured dict with items, summary, and updated_at.
    """
    all_items = []

    jin10_items = _fetch_jin10()
    yahoo_items = _fetch_yahoo()
    cnbc_items = _fetch_cnbc()

    all_items.extend(jin10_items)
    all_items.extend(yahoo_items)
    all_items.extend(cnbc_items)

    # Sort by relevance descending, then by time descending
    all_items.sort(key=lambda x: (-x["relevance_score"], x["time"]), reverse=False)
    # Deduplicate by headline similarity (exact match only)
    seen_headlines: set = set()
    deduped = []
    for item in all_items:
        norm = re.sub(r"\s+", " ", item["headline"].lower().strip())
        if norm not in seen_headlines:
            seen_headlines.add(norm)
            deduped.append(item)

    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "news": {
            "items": deduped,
            "summary": _build_summary(deduped),
            "source_counts": {
                "jin10": len(jin10_items),
                "yahoo": len(yahoo_items),
                "cnbc": len(cnbc_items),
            },
            "updated_at": updated_at,
        }
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import subprocess
    import sys

    # Auto-install dependencies if missing
    for pkg in ["feedparser", "beautifulsoup4", "requests"]:
        try:
            __import__(pkg.replace("-", "_").replace("beautifulsoup4", "bs4"))
        except ImportError:
            print(f"Installing {pkg}...", file=sys.stderr)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--break-system-packages", "--quiet", pkg,
            ])

    result = fetch_news()
    print(json.dumps(result, ensure_ascii=False, indent=2))
