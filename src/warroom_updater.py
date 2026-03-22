"""Generate docs/data/warroom_data.json for the War Room dashboard."""

from __future__ import annotations

import json
import logging
import math
import os
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yfinance as yf

from macro_data_fetcher import fetch_macro_data
from news_fetcher import fetch_news


ROOT_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = ROOT_DIR / "docs" / "data" / "warroom_data.json"
LEGACY_PATH = ROOT_DIR / "data" / "warroom_data.json"
MOODRING_URL = "https://wenyuchiou.github.io/moodring/data/dashboard_data.json"
LOCAL_DASHBOARD_PATHS = [
    ROOT_DIR / "docs" / "data" / "dashboard_data.json",
    ROOT_DIR / "data" / "dashboard_data.json",
]

MARKET_SYMBOLS: dict[str, dict[str, str]] = {
    "SPY": {"symbol": "SPY", "label": "SPDR S&P 500 ETF"},
    "QQQ": {"symbol": "QQQ", "label": "Invesco QQQ"},
    "VIX": {"symbol": "^VIX", "label": "CBOE Volatility Index"},
    "IWM": {"symbol": "IWM", "label": "iShares Russell 2000 ETF"},
    "NVDA": {"symbol": "NVDA", "label": "NVIDIA"},
    "BRENT": {"symbol": "BZ=F", "label": "Brent Crude Futures"},
    "DXY": {"symbol": "DX-Y.NYB", "label": "US Dollar Index"},
    "TNX": {"symbol": "^TNX", "label": "US 10Y Treasury Yield"},
}

MOODRING_SERIES: dict[str, tuple[str, str]] = {
    "US": ("us_score", "dates"),
    "TW": ("tw_score", "dates"),
    "JP": ("jp_score", "jp_dates"),
    "KR": ("kr_score", "kr_dates"),
    "EU": ("eu_score", "eu_dates"),
}

ACCOUNT_CONFIGS: list[dict[str, Any]] = [
    {
        "name": "cash",
        "acc_id": 283445328432576687,
        "strategy": "stocks",
    },
    {
        "name": "margin",
        "acc_id": 283445329185003354,
        "strategy": "options",
    },
]

LEGACY_MARKET_MAP: dict[str, str] = {
    "SPY": "spy",
    "QQQ": "qqq",
    "VIX": "vix",
    "IWM": "iwm",
    "NVDA": "nvda",
    "BRENT": "brent",
    "DXY": "dxy",
    "TNX": "rate10y",
}

DEFAULT_SCENARIOS: list[dict[str, Any]] = [
    {"id": "S1", "name": "Quick deal + pause", "prob": 5, "spy": 685, "nash": "Not EQ", "duration": "<4 wks"},
    {"id": "S2", "name": "SOF + partial deal", "prob": 20, "spy": 630, "nash": "Weak", "duration": "4-8 wks"},
    {
        "id": "S3",
        "name": "Protracted standoff + stagflation",
        "prob": 42,
        "spy": 575,
        "nash": "Strong",
        "duration": "3-6 mo",
    },
    {"id": "S4", "name": "Ground escalation + recession", "prob": 33, "spy": 510, "nash": "Unstable", "duration": "6+ mo"},
]


def configure_logging() -> None:
    """Configure script logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def read_json_file(path: Path) -> dict[str, Any]:
    """Read JSON from disk, returning an empty dict on failure."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        logging.warning("Failed to read JSON from %s: %s", path, exc)
        return {}


def sanitize_for_json(obj: Any) -> Any:
    """Recursively replace invalid float values for JSON serialization."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, Mapping):
        return {key: sanitize_for_json(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [sanitize_for_json(value) for value in obj]
    return obj


def to_float(value: Any, decimals: int | None = 2) -> float | None:
    """Convert a value to float with optional rounding."""
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return round(number, decimals) if decimals is not None else number


def to_str(value: Any) -> str | None:
    """Convert a value to string if present."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def get_existing_data() -> dict[str, Any]:
    """Load existing War Room JSON, merging docs and legacy copies."""
    docs_existing = read_json_file(OUTPUT_PATH)
    legacy_existing = read_json_file(LEGACY_PATH)
    if not docs_existing:
        return legacy_existing
    if not legacy_existing:
        return docs_existing

    merged = dict(legacy_existing)
    merged.update(docs_existing)

    docs_market = docs_existing.get("market", {})
    if extract_market_spy(docs_market) is None and legacy_existing.get("market"):
        merged["market"] = legacy_existing["market"]

    docs_moodring = docs_existing.get("moodring", {})
    if not docs_moodring or not docs_moodring.get("regions"):
        if legacy_existing.get("moodring"):
            merged["moodring"] = legacy_existing["moodring"]

    return merged


def normalize_existing_sections(existing: dict[str, Any]) -> dict[str, Any]:
    """Normalize existing JSON into the requested top-level schema."""
    return {
        "meta": existing.get("meta", {}),
        "market": existing.get("market", {}),
        "moodring": existing.get("moodring", {}),
        "scenarios": existing.get("scenarios", DEFAULT_SCENARIOS),
        "hypotheses": existing.get("hypotheses", []),
        "positions": existing.get("positions", {}),
        "greeks": existing.get("greeks", []),
        "edges": existing.get("edges", []),
        "stop_rules": existing.get("stop_rules", []),
        "mispricing": existing.get("mispricing", {}),
    }


def fetch_single_market(symbol: str, label: str) -> dict[str, Any]:
    """Fetch one symbol from Yahoo Finance using the last available closes."""
    history = yf.download(
        symbol,
        period="7d",
        interval="1d",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if history.empty:
        raise ValueError(f"No data returned for {symbol}")

    close_series = history["Close"]
    if getattr(close_series, "ndim", 1) > 1:
        close_series = close_series.iloc[:, 0]
    close_series = close_series.dropna()
    if close_series.empty:
        raise ValueError(f"No close prices returned for {symbol}")

    price = to_float(close_series.iloc[-1], 4)
    prev_close = None
    if len(close_series) >= 2:
        prev_close = to_float(close_series.iloc[-2], 4)
    if prev_close in (None, 0):
        prev_close = price

    change_pct = None
    if price is not None and prev_close not in (None, 0):
        change_pct = round(((price - prev_close) / prev_close) * 100, 2)

    as_of = close_series.index[-1]
    if hasattr(as_of, "to_pydatetime"):
        as_of = as_of.to_pydatetime()

    return {
        "symbol": symbol,
        "label": label,
        "price": price,
        "change_pct": change_pct,
        "prev_close": prev_close,
        "as_of": as_of.strftime("%Y-%m-%d"),
    }


def configure_yfinance_cache() -> None:
    """Force yfinance timezone cache into a writable workspace directory."""
    cache_dir = ROOT_DIR / ".cache" / "yfinance"
    cache_dir.mkdir(parents=True, exist_ok=True)
    if hasattr(yf, "set_tz_cache_location"):
        yf.set_tz_cache_location(str(cache_dir))


def legacy_market_fallback(existing_market: dict[str, Any], key: str, symbol: str, label: str) -> dict[str, Any]:
    """Map old flat market data into the new per-instrument structure."""
    fallback: dict[str, Any] = {}
    if isinstance(existing_market, Mapping):
        if key in existing_market and isinstance(existing_market[key], Mapping):
            fallback = dict(existing_market[key])
        elif "items" in existing_market and isinstance(existing_market["items"], Mapping):
            fallback = dict(existing_market["items"].get(key, {}))
        else:
            legacy_key = LEGACY_MARKET_MAP.get(key)
            legacy_price = to_float(existing_market.get(legacy_key), 4) if legacy_key else None
            if legacy_price is not None:
                fallback = {
                    "price": legacy_price,
                    "change_pct": None,
                    "prev_close": None,
                    "as_of": existing_market.get("as_of") or datetime.now().strftime("%Y-%m-%d"),
                }

    fallback.setdefault("symbol", symbol)
    fallback.setdefault("label", label)
    fallback.setdefault("price", None)
    fallback.setdefault("change_pct", None)
    fallback.setdefault("prev_close", None)
    fallback.setdefault("as_of", datetime.now().strftime("%Y-%m-%d"))
    return fallback


def fetch_market_data(existing_market: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Fetch live market data, falling back to existing values per symbol."""
    warnings: list[str] = []
    market_data: dict[str, Any] = {
        "as_of": datetime.now().strftime("%Y-%m-%d"),
        "items": {},
    }
    configure_yfinance_cache()

    for key, config in MARKET_SYMBOLS.items():
        symbol = config["symbol"]
        label = config["label"]
        try:
            logging.info("Fetching market data for %s", symbol)
            market_data["items"][key] = fetch_single_market(symbol, label)
        except Exception as exc:  # noqa: BLE001
            warning = f"Market fetch failed for {symbol}: {exc}"
            warnings.append(warning)
            logging.warning(warning)
            market_data["items"][key] = legacy_market_fallback(existing_market, key, symbol, label)

    item_dates = [
        item.get("as_of")
        for item in market_data["items"].values()
        if isinstance(item, Mapping) and item.get("as_of")
    ]
    if item_dates:
        market_data["as_of"] = max(item_dates)
    return market_data, warnings


def latest_series_value(payload: dict[str, Any], score_key: str, date_key: str) -> tuple[str | None, float | None]:
    """Extract the latest non-null value from parallel date/value arrays."""
    scores = payload.get(score_key, [])
    dates = payload.get(date_key, payload.get("dates", []))
    if not isinstance(scores, list) or not isinstance(dates, list):
        return None, None

    for index in range(min(len(scores), len(dates)) - 1, -1, -1):
        score = to_float(scores[index], 1)
        date = to_str(dates[index])
        if score is not None and date is not None:
            return date, score
    return None, None


def score_to_signal(score: float | None) -> str | None:
    """Map a Moodring score to a Chinese signal label."""
    if score is None:
        return None
    if score < 25:
        return "極度恐懼"
    if score < 40:
        return "偏恐懼"
    if score < 55:
        return "中性"
    if score <= 75:
        return "偏貪婪"
    return "極度貪婪"


def fetch_moodring_data(existing_moodring: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Fetch Moodring dashboard data and summarize the requested regions."""
    warnings: list[str] = []
    moodring = {
        "as_of": None,
        "source_url": MOODRING_URL,
        "regions": {},
    }

    try:
        logging.info("Fetching Moodring dashboard data")
        response = requests.get(MOODRING_URL, timeout=20)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:  # noqa: BLE001
        warning = f"Moodring fetch failed: {exc}"
        warnings.append(warning)
        logging.warning(warning)
        payload = {}
        for candidate in LOCAL_DASHBOARD_PATHS:
            payload = read_json_file(candidate)
            if payload:
                logging.info("Using local Moodring fallback from %s", candidate)
                break
        if payload:
            moodring["source_url"] = f"local-fallback:{candidate.relative_to(ROOT_DIR)}"
        elif isinstance(existing_moodring, Mapping) and existing_moodring:
            fallback = dict(existing_moodring)
            fallback.setdefault("source_url", MOODRING_URL)
            return fallback, warnings
        else:
            return moodring, warnings

    latest_dates: list[str] = []
    for region, (score_key, date_key) in MOODRING_SERIES.items():
        date, score = latest_series_value(payload, score_key, date_key)
        if date:
            latest_dates.append(date)
        moodring["regions"][region] = {
            "date": date,
            "score": score,
            "signal": score_to_signal(score),
        }

    moodring["as_of"] = max(latest_dates) if latest_dates else None
    return moodring, warnings


def prepare_moomoo_environment() -> None:
    """Force moomoo logs into a writable path inside the workspace."""
    appdata_dir = ROOT_DIR / ".cache" / "moomoo_appdata"
    appdata_dir.mkdir(parents=True, exist_ok=True)
    os.environ["APPDATA"] = str(appdata_dir)
    os.environ["appdata"] = str(appdata_dir)


def dataframe_row_to_dict(frame: Any) -> dict[str, Any]:
    """Convert the first DataFrame row to a dict."""
    if frame is None or getattr(frame, "empty", True):
        return {}
    return frame.iloc[0].to_dict()


def extract_position_rows(frame: Any) -> list[dict[str, Any]]:
    """Convert a moomoo positions DataFrame into the required structure."""
    rows: list[dict[str, Any]] = []
    if frame is None or getattr(frame, "empty", True):
        return rows

    for _, row in frame.iterrows():
        rows.append(
            {
                "code": to_str(row.get("code")),
                "name": to_str(row.get("stock_name")),
                "qty": to_float(row.get("qty"), 4),
                "cost_price": to_float(row.get("cost_price"), 4),
                "nominal_price": to_float(row.get("nominal_price"), 4),
                "pl_val": to_float(row.get("pl_val"), 2),
                "pl_ratio": to_float(row.get("pl_ratio"), 4),
                "side": to_str(row.get("position_side")),
            }
        )
    return rows


def extract_funds(row: dict[str, Any]) -> dict[str, Any]:
    """Extract the requested funds fields."""
    return {
        "total_assets": to_float(row.get("total_assets"), 2),
        "cash": to_float(row.get("cash"), 2),
        "market_val": to_float(row.get("market_val"), 2),
        "power": to_float(row.get("power"), 2),
    }


def fetch_moomoo_positions() -> tuple[dict[str, Any], list[str]]:
    """Fetch positions and funds from moomoo OpenD, or return empty accounts."""
    warnings: list[str] = []
    result: dict[str, Any] = {
        "as_of": datetime.now().strftime("%Y-%m-%d"),
        "accounts": [],
        "warnings": [],
    }

    try:
        prepare_moomoo_environment()
        from moomoo import Currency, OpenSecTradeContext, RET_OK, SecurityFirm, TrdEnv, TrdMarket
    except Exception as exc:  # noqa: BLE001
        warning = f"moomoo import unavailable: {exc}"
        warnings.append(warning)
        logging.warning(warning)
        for account in ACCOUNT_CONFIGS:
            result["accounts"].append(
                {
                    "account_name": account["name"],
                    "acc_id": str(account["acc_id"]),
                    "strategy": account["strategy"],
                    "funds": {},
                    "positions": [],
                }
            )
        result["warnings"] = warnings
        return result, warnings

    trade_ctx = None
    try:
        logging.info("Connecting to moomoo OpenD")
        trade_ctx = OpenSecTradeContext(
            host="127.0.0.1",
            port=11111,
            security_firm=SecurityFirm.FUTUINC,
            filter_trdmarket=TrdMarket.NONE,
        )

        for account in ACCOUNT_CONFIGS:
            account_id = account["acc_id"]
            account_name = account["name"]
            logging.info("Querying moomoo account %s", account_name)

            positions: list[dict[str, Any]] = []
            funds: dict[str, Any] = {}

            pos_ret, pos_data = trade_ctx.position_list_query(
                trd_env=TrdEnv.REAL,
                acc_id=account_id,
                position_market=TrdMarket.NONE,
                refresh_cache=True,
            )
            if pos_ret == RET_OK:
                positions = extract_position_rows(pos_data)
            else:
                warning = f"Position query failed for {account_name} ({account_id}): {pos_data}"
                warnings.append(warning)
                logging.warning(warning)

            funds_ret, funds_data = trade_ctx.accinfo_query(
                trd_env=TrdEnv.REAL,
                acc_id=account_id,
                refresh_cache=True,
                currency=Currency.USD,
            )
            if funds_ret == RET_OK:
                funds = extract_funds(dataframe_row_to_dict(funds_data))
            else:
                warning = f"Funds query failed for {account_name} ({account_id}): {funds_data}"
                warnings.append(warning)
                logging.warning(warning)

            result["accounts"].append(
                {
                    "account_name": account_name,
                    "acc_id": str(account_id),
                    "strategy": account["strategy"],
                    "funds": funds,
                    "positions": positions,
                }
            )
    except Exception as exc:  # noqa: BLE001
        warning = f"OpenD unavailable, skipping moomoo data: {exc}"
        warnings.append(warning)
        logging.warning(warning)
        result["accounts"] = [
            {
                "account_name": account["name"],
                "acc_id": str(account["acc_id"]),
                "strategy": account["strategy"],
                "funds": {},
                "positions": [],
            }
            for account in ACCOUNT_CONFIGS
        ]
    finally:
        if trade_ctx is not None:
            try:
                trade_ctx.close()
            except Exception:  # noqa: BLE001
                logging.debug("Failed to close moomoo trade context cleanly", exc_info=True)

    result["warnings"] = warnings
    return result, warnings


def scenario_probability(probability: Any) -> float | None:
    """Convert a scenario probability into a decimal weight."""
    value = to_float(probability, 6)
    if value is None:
        return None
    if value > 1:
        return value / 100
    return value


def extract_market_spy(market: dict[str, Any]) -> float | None:
    """Read SPY market price from the new or legacy market structure."""
    if not isinstance(market, Mapping):
        return None
    if "items" in market and isinstance(market["items"], Mapping):
        return to_float(market["items"].get("SPY", {}).get("price"), 4)
    return to_float(market.get("spy"), 4)


def build_mispricing(
    scenarios: list[dict[str, Any]],
    market: dict[str, Any],
    existing_mispricing: dict[str, Any],
) -> dict[str, Any]:
    """Calculate expected SPY, current mispricing, and update 30-day history."""
    weighted_sum = 0.0
    found_any = False
    for scenario in scenarios:
        if not isinstance(scenario, Mapping):
            continue
        probability = scenario_probability(scenario.get("prob"))
        spy_target = to_float(scenario.get("spy"), 4)
        if probability is None or spy_target is None:
            continue
        weighted_sum += probability * spy_target
        found_any = True

    expected_spy = round(weighted_sum, 4) if found_any else None
    market_spy = extract_market_spy(market)
    mispricing_pct = None
    if market_spy not in (None, 0) and expected_spy is not None:
        mispricing_pct = round(((market_spy - expected_spy) / market_spy) * 100, 4)

    history = existing_mispricing.get("history", []) if isinstance(existing_mispricing, Mapping) else []
    if not isinstance(history, list):
        history = []

    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = {
        "date": today,
        "market_spy": market_spy,
        "expected_spy": expected_spy,
        "mispricing_pct": mispricing_pct,
    }

    retained_history = [
        entry
        for entry in history
        if isinstance(entry, Mapping) and to_str(entry.get("date")) not in {None, today}
    ]
    retained_history.append(new_entry)
    retained_history = sorted(
        retained_history,
        key=lambda item: to_str(item.get("date")) or "",
    )[-30:]

    return {
        "as_of": today,
        "market_spy": market_spy,
        "expected_spy": expected_spy,
        "mispricing_pct": mispricing_pct,
        "history": retained_history,
    }


def build_output(existing: dict[str, Any]) -> dict[str, Any]:
    """Build the complete output payload."""
    sections = normalize_existing_sections(existing)
    warnings: list[str] = []

    market, market_warnings = fetch_market_data(sections["market"])
    moodring, moodring_warnings = fetch_moodring_data(sections["moodring"])
    positions, positions_warnings = fetch_moomoo_positions()
    warnings.extend(market_warnings)
    warnings.extend(moodring_warnings)
    warnings.extend(positions_warnings)

    # Macro data
    macro_data: dict[str, Any] = {}
    try:
        macro_data = fetch_macro_data()
    except Exception as e:
        print(f"Warning: macro data fetch failed: {e}")

    # News data
    news_data: dict[str, Any] = {}
    try:
        news_data = fetch_news()
    except Exception as e:
        print(f"Warning: news fetch failed: {e}")

    scenarios = sections["scenarios"] or DEFAULT_SCENARIOS
    hypotheses = sections["hypotheses"] if isinstance(sections["hypotheses"], list) else []
    mispricing = build_mispricing(scenarios, market, sections["mispricing"])

    output = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "as_of": market.get("as_of") or moodring.get("as_of") or datetime.now().strftime("%Y-%m-%d"),
            "output_path": str(OUTPUT_PATH.relative_to(ROOT_DIR)),
            "warnings": warnings,
        },
        "market": market,
        "moodring": moodring,
        "scenarios": scenarios,
        "hypotheses": hypotheses,
        "positions": positions,
        "macro": macro_data,
        "news": news_data,
        "greeks": sections["greeks"],
        "edges": sections["edges"],
        "stop_rules": sections["stop_rules"],
        "mispricing": mispricing,
    }
    return sanitize_for_json(output)


def write_output(payload: dict[str, Any]) -> None:
    """Write the final JSON to disk."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> None:
    """Entry point."""
    configure_logging()
    logging.info("Generating %s", OUTPUT_PATH)
    existing = get_existing_data()
    payload = build_output(existing)
    write_output(payload)
    logging.info("Wrote %s", OUTPUT_PATH)


if __name__ == "__main__":
    main()
