"""
macro_data_fetcher.py
Fetches macroeconomic data from FRED API and returns structured dict
for Moodring dashboard integration.
"""

import os
import sys
import json
from datetime import datetime, date, timedelta


def _ensure_fredapi():
    """Import fredapi, installing if missing."""
    try:
        from fredapi import Fred
        return Fred
    except ImportError:
        print("fredapi not found — installing...", file=sys.stderr)
        import subprocess
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "fredapi", "--break-system-packages", "-q"
        ])
        from fredapi import Fred
        return Fred


# ──────────────────────────────────────────────────────────────────────────────
# Yield curve series
# ──────────────────────────────────────────────────────────────────────────────
YIELD_SERIES = {
    "1M":  "DGS1MO",
    "3M":  "DGS3MO",
    "6M":  "DGS6MO",
    "1Y":  "DGS1",
    "2Y":  "DGS2",
    "3Y":  "DGS3",
    "5Y":  "DGS5",
    "10Y": "DGS10",
    "30Y": "DGS30",
}

# ──────────────────────────────────────────────────────────────────────────────
# Economic indicators
# ──────────────────────────────────────────────────────────────────────────────
INDICATOR_SERIES = [
    {"name": "CPI",               "series": "CPIAUCSL",  "label": "消費者物價指數 (CPI)"},
    {"name": "核心PCE",            "series": "PCEPILFE",  "label": "核心個人消費支出 (Core PCE)"},
    {"name": "失業率",             "series": "UNRATE",    "label": "失業率"},
    {"name": "非農就業人數",        "series": "PAYEMS",    "label": "非農就業人數 (NFP)"},
    {"name": "GDP",               "series": "GDP",       "label": "國內生產毛額 (GDP)"},
    {"name": "初領失業救濟金",      "series": "ICSA",      "label": "初領失業救濟金人數"},
    {"name": "消費者信心指數",      "series": "UMCSENT",   "label": "密歇根消費者信心指數"},
]

# ──────────────────────────────────────────────────────────────────────────────
# Economic calendar helpers
# ──────────────────────────────────────────────────────────────────────────────

def _first_friday(year: int, month: int) -> date:
    """Return the first Friday of the given month."""
    d = date(year, month, 1)
    while d.weekday() != 4:  # 4 = Friday
        d += timedelta(days=1)
    return d


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    """Return the n-th occurrence of `weekday` (0=Mon…6=Sun) in month."""
    d = date(year, month, 1)
    while d.weekday() != weekday:
        d += timedelta(days=1)
    d += timedelta(weeks=n - 1)
    return d


# FOMC meeting schedule 2025-2026 (8 meetings per year, hardcoded decision dates)
FOMC_DATES = [
    date(2025, 1, 29), date(2025, 3, 19), date(2025, 5, 7),
    date(2025, 6, 18), date(2025, 7, 30), date(2025, 9, 17),
    date(2025, 10, 29), date(2025, 12, 10),
    date(2026, 1, 28), date(2026, 3, 18), date(2026, 5, 6),
    date(2026, 6, 17), date(2026, 7, 29), date(2026, 9, 16),
    date(2026, 10, 28), date(2026, 12, 9),
]


def _build_calendar(reference_date: date, days_ahead: int = 7) -> list:
    """
    Build a list of upcoming economic events within `days_ahead` days
    from `reference_date` (inclusive).
    """
    window_end = reference_date + timedelta(days=days_ahead)
    events = []

    def add(event_date: date, event: str, importance: str):
        if reference_date <= event_date <= window_end:
            events.append({
                "date": event_date.isoformat(),
                "event": event,
                "importance": importance,
            })

    year = reference_date.year
    # Scan current month + next month to catch boundary crossings
    for y in [year, year + (1 if reference_date.month == 12 else 0)]:
        for m in range(1, 13):
            check = date(y, m, 1)
            if check < date(y if m >= reference_date.month else y - 1, reference_date.month, 1):
                continue
            if check > window_end.replace(day=1):
                break

            # NFP — first Friday of each month (released for prior month)
            nfp = _first_friday(y, m)
            add(nfp, "非農就業報告 (NFP)", "HIGH")

            # CPI — typically released around 10th–15th
            # Approximate: second Wednesday
            cpi_day = _nth_weekday(y, m, 2, 2)  # 2nd Wednesday
            add(cpi_day, "消費者物價指數 (CPI)", "HIGH")

            # Core PCE — last business day region, ~4th Friday
            try:
                pce_day = _nth_weekday(y, m, 4, 4)  # 4th Friday
                add(pce_day, "核心個人消費支出 (Core PCE)", "HIGH")
            except ValueError:
                pass

            # Unemployment claims — every Thursday
            d = date(y, m, 1)
            while d.month == m:
                if d.weekday() == 3:  # Thursday
                    add(d, "初領失業救濟金", "MEDIUM")
                d += timedelta(days=1)

            # ISM Manufacturing — first business day of month
            ism_mfg = date(y, m, 1)
            while ism_mfg.weekday() >= 5:
                ism_mfg += timedelta(days=1)
            add(ism_mfg, "ISM 製造業 PMI", "MEDIUM")

            # ISM Services — typically 3rd business day
            ism_svc = date(y, m, 1)
            biz = 0
            while biz < 3:
                if ism_svc.weekday() < 5:
                    biz += 1
                    if biz == 3:
                        break
                ism_svc += timedelta(days=1)
            add(ism_svc, "ISM 服務業 PMI", "MEDIUM")

            # Retail Sales — ~15th of month (second Wednesday approx)
            retail = _nth_weekday(y, m, 2, 2) + timedelta(days=3)
            add(retail, "零售銷售", "MEDIUM")

    # FOMC dates
    for fd in FOMC_DATES:
        add(fd, "FOMC 利率決議", "HIGH")

    # De-duplicate and sort
    seen = set()
    unique = []
    for e in sorted(events, key=lambda x: x["date"]):
        key = (e["date"], e["event"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return unique


# ──────────────────────────────────────────────────────────────────────────────
# Trend helper
# ──────────────────────────────────────────────────────────────────────────────

def _trend(change: float, threshold: float = 0.01) -> str:
    if change > threshold:
        return "上升"
    elif change < -threshold:
        return "下降"
    return "持平"


# ──────────────────────────────────────────────────────────────────────────────
# Main fetch function
# ──────────────────────────────────────────────────────────────────────────────

def fetch_macro_data() -> dict:
    """
    Fetch macroeconomic data from FRED and return structured dict.

    Returns:
        dict with key "macro" containing yield curve, indicators, and calendar.
    """
    Fred = _ensure_fredapi()

    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        # FRED allows unauthenticated access with rate limits;
        # fredapi accepts empty string and uses the public endpoint.
        # Users should set FRED_API_KEY for reliable access.
        print(
            "警告：未設置 FRED_API_KEY 環境變數，使用匿名存取（可能受速率限制）。",
            file=sys.stderr,
        )

    fred = Fred(api_key=api_key) if api_key else Fred()

    today = date.today()

    # ── 1. Yield curve ────────────────────────────────────────────────────────
    yield_curve = {}
    for label, series_id in YIELD_SERIES.items():
        try:
            s = fred.get_series(series_id, observation_start=str(today - timedelta(days=10)))
            s = s.dropna()
            if not s.empty:
                yield_curve[label] = round(float(s.iloc[-1]), 4)
            else:
                yield_curve[label] = None
        except Exception as e:
            print(f"警告：無法取得 {series_id} ({label}): {e}", file=sys.stderr)
            yield_curve[label] = None

    spread_2s10s = None
    inverted = False
    y2 = yield_curve.get("2Y")
    y10 = yield_curve.get("10Y")
    if y2 is not None and y10 is not None:
        spread_2s10s = round(y10 - y2, 4)
        inverted = spread_2s10s < 0

    # ── 2. Economic indicators ────────────────────────────────────────────────
    indicators = []
    for ind in INDICATOR_SERIES:
        try:
            s = fred.get_series(
                ind["series"],
                observation_start=str(today - timedelta(days=400)),
            )
            s = s.dropna()
            if len(s) >= 2:
                latest_val = float(s.iloc[-1])
                prev_val = float(s.iloc[-2])
                change = round(latest_val - prev_val, 4)
                latest_date = s.index[-1].strftime("%Y-%m-%d")
            elif len(s) == 1:
                latest_val = float(s.iloc[-1])
                prev_val = None
                change = None
                latest_date = s.index[-1].strftime("%Y-%m-%d")
            else:
                raise ValueError("無資料")

            indicators.append({
                "name": ind["name"],
                "label": ind["label"],
                "series": ind["series"],
                "latest": round(latest_val, 4),
                "previous": round(prev_val, 4) if prev_val is not None else None,
                "change": change,
                "trend": _trend(change) if change is not None else "持平",
                "date": latest_date,
            })
        except Exception as e:
            print(f"警告：無法取得 {ind['series']} ({ind['name']}): {e}", file=sys.stderr)
            indicators.append({
                "name": ind["name"],
                "label": ind["label"],
                "series": ind["series"],
                "latest": None,
                "previous": None,
                "change": None,
                "trend": "持平",
                "date": None,
            })

    # ── 3. Economic calendar ──────────────────────────────────────────────────
    calendar = _build_calendar(today, days_ahead=7)

    # ── 4. Assemble output ────────────────────────────────────────────────────
    return {
        "macro": {
            "yield_curve": yield_curve,
            "spread_2s10s": spread_2s10s,
            "yield_curve_inverted": inverted,
            "indicators": indicators,
            "calendar": calendar,
            "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        }
    }


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    data = fetch_macro_data()
    print(json.dumps(data, ensure_ascii=False, indent=2))
