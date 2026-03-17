"""
TW Score Diagnostic: Component-level IC breakdown by time period.
Goal: Find which components work post-2020 and which have decayed.
"""

import sys
import io
import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from backtest import normalize_zscore, zscore_to_score, compute_tw_retail_score

# stdout encoding handled by -X utf8 flag or PYTHONUTF8=1

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def ic_by_period(signal, target, periods):
    """Compute IC for each time period."""
    aligned = pd.DataFrame({'signal': signal, 'target': target}).dropna()
    results = {}
    for name, (start, end) in periods.items():
        mask = (aligned.index >= start) & (aligned.index <= end)
        subset = aligned[mask]
        if len(subset) > 50:
            ic, pval = spearmanr(subset['signal'], subset['target'])
            results[name] = {'ic': round(ic, 4), 'pval': round(pval, 4), 'n': len(subset),
                             'sig': '*' if pval < 0.05 else ''}
    return results


def main():
    features = pd.read_csv(os.path.join(DATA_DIR, 'base_features.csv'),
                           index_col=0, parse_dates=True)
    targets = pd.read_csv(os.path.join(DATA_DIR, 'target_returns.csv'),
                          index_col=0, parse_dates=True)

    target_col = 'taiex_fwd_20d'
    target = targets[target_col]

    periods = {
        '2012-2015': ('2012-01-01', '2015-12-31'),
        '2016-2019': ('2016-01-01', '2019-12-31'),
        '2020-2022': ('2020-01-01', '2022-12-31'),
        '2023-2025': ('2023-01-01', '2025-12-31'),
    }

    # Get TW score components
    _, components = compute_tw_retail_score(features)

    print("=" * 80)
    print("TW SCORE DIAGNOSTIC: Component IC by Period (vs TAIEX 20d fwd return)")
    print("=" * 80)
    print(f"{'Component':<25} {'2012-15':>10} {'2016-19':>10} {'2020-22':>10} {'2023-25':>10}")
    print("-" * 80)

    for col in components.columns:
        results = ic_by_period(components[col], target, periods)
        row = f"{col:<25}"
        for period_name in periods:
            if period_name in results:
                r = results[period_name]
                row += f" {r['ic']:>8.4f}{r['sig']}"
            else:
                row += f" {'N/A':>9}"
        print(row)

    # Composite score
    tw_score = components.mean(axis=1)
    results = ic_by_period(tw_score, target, periods)
    row = f"{'COMPOSITE SCORE':<25}"
    for period_name in periods:
        if period_name in results:
            r = results[period_name]
            row += f" {r['ic']:>8.4f}{r['sig']}"
    print("-" * 80)
    print(row)

    # Also check raw features that AREN'T in the score yet
    print(f"\n{'=' * 80}")
    print("UNUSED FEATURES: IC by Period (looking for post-2020 signals)")
    print("=" * 80)
    print(f"{'Feature':<25} {'2012-15':>10} {'2016-19':>10} {'2020-22':>10} {'2023-25':>10}")
    print("-" * 80)

    unused_features = [
        'tw_taiex_drawdown', 'tw_tsmc_vs_high', 'tw_tsmc_mom_20d',
        'tw_volume_surge', 'us_vix_zscore', 'us_10y_yield',
        'us_10y_change_20d', 'us_vix_spy_corr_20d', 'cross_us_tw_corr_60d',
        'us_spy_drawdown', 'us_spy_vs_high', 'us_spy_mom_20d',
    ]

    for feat in unused_features:
        if feat not in features.columns:
            continue
        z = normalize_zscore(features[feat], window=252)
        score = zscore_to_score(z)
        results = ic_by_period(score, target, periods)
        row = f"{feat:<25}"
        for period_name in periods:
            if period_name in results:
                r = results[period_name]
                row += f" {r['ic']:>8.4f}{r['sig']}"
            else:
                row += f" {'N/A':>9}"
        print(row)

        # Also try inverted
        score_inv = zscore_to_score(-z)
        results_inv = ic_by_period(score_inv, target, periods)
        row_inv = f"  (inverted){'':<13}"
        for period_name in periods:
            if period_name in results_inv:
                r = results_inv[period_name]
                row_inv += f" {r['ic']:>8.4f}{r['sig']}"
        print(row_inv)

    # Check multi-horizon to see if TW has any horizon that works post-2020
    print(f"\n{'=' * 80}")
    print("TW COMPOSITE SCORE: IC by Period x Horizon")
    print("=" * 80)
    print(f"{'Horizon':<15} {'2012-15':>10} {'2016-19':>10} {'2020-22':>10} {'2023-25':>10}")
    print("-" * 80)
    for horizon in ['5d', '10d', '20d', '60d']:
        tcol = f'taiex_fwd_{horizon}'
        if tcol in targets.columns:
            results = ic_by_period(tw_score, targets[tcol], periods)
            row = f"{horizon:<15}"
            for period_name in periods:
                if period_name in results:
                    r = results[period_name]
                    row += f" {r['ic']:>8.4f}{r['sig']}"
            print(row)


if __name__ == '__main__':
    main()
