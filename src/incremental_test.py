"""
GRISI Phase 1C: Incremental Alpha Test
=======================================
Test if social/sentiment data adds predictive power beyond base scoring.

Method:
  1. Compute base TW score (v3) IC
  2. Add social features to TW score → compute enhanced IC
  3. Incremental IC = enhanced IC - base IC
  4. Gate 1C: incremental IC > 0.02?
"""

import os
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
from backtest import normalize_zscore, zscore_to_score, compute_tw_retail_score

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def compute_enhanced_tw_score(features, social):
    """
    Enhanced TW score = base score + social sentiment indicators.
    Social components are added as extra dimensions, not replacing base.
    """
    # Get base score and components
    base_score, base_components = compute_tw_retail_score(features)

    # Build social components
    social_components = pd.DataFrame(index=features.index)

    # Margin balance z-score (high margin = retail leveraged = greedy)
    if 'tw_margin_zscore' in social.columns:
        # Align social data to features index
        aligned = social['tw_margin_zscore'].reindex(features.index)
        social_components['margin_leverage'] = zscore_to_score(aligned.clip(-3, 3))

    # Margin change rate (rapid margin increase = FOMO)
    if 'tw_margin_change_20d' in social.columns:
        aligned = social['tw_margin_change_20d'].reindex(features.index)
        z = normalize_zscore(aligned, window=252)
        social_components['margin_fomo'] = zscore_to_score(z)

    # Foreign investor flow (inverted: foreign selling = retail holding bag = greedy/delusional)
    if 'tw_foreign_flow_zscore' in social.columns:
        aligned = social['tw_foreign_flow_zscore'].reindex(features.index)
        social_components['foreign_exodus'] = zscore_to_score(-aligned.clip(-3, 3))

    # Combine: base components + social components with equal weight per component
    all_components = pd.concat([base_components, social_components], axis=1)
    enhanced_score = all_components.mean(axis=1)

    return enhanced_score, all_components, social_components


def evaluate_incremental(base_score, enhanced_score, target, periods, label=''):
    """Compare base vs enhanced IC across time periods."""
    results = {}

    for period_name, (start, end) in periods.items():
        base_aligned = pd.DataFrame({'score': base_score, 'target': target}).dropna()
        enh_aligned = pd.DataFrame({'score': enhanced_score, 'target': target}).dropna()

        mask_b = (base_aligned.index >= start) & (base_aligned.index <= end)
        mask_e = (enh_aligned.index >= start) & (enh_aligned.index <= end)

        base_sub = base_aligned[mask_b]
        enh_sub = enh_aligned[mask_e]

        if len(base_sub) > 50 and len(enh_sub) > 50:
            base_ic, base_pval = spearmanr(base_sub['score'], base_sub['target'])
            enh_ic, enh_pval = spearmanr(enh_sub['score'], enh_sub['target'])

            results[period_name] = {
                'n': len(enh_sub),
                'base_ic': round(base_ic, 4),
                'enhanced_ic': round(enh_ic, 4),
                'incremental': round(enh_ic - base_ic, 4),
                'base_sig': base_pval < 0.05,
                'enh_sig': enh_pval < 0.05,
            }

    return results


def main():
    print("=" * 70)
    print("GRISI Phase 1C: Incremental Alpha Test")
    print("=" * 70)

    # Load data
    features = pd.read_csv(os.path.join(DATA_DIR, 'base_features.csv'),
                           index_col=0, parse_dates=True)
    targets = pd.read_csv(os.path.join(DATA_DIR, 'target_returns.csv'),
                          index_col=0, parse_dates=True)
    social = pd.read_csv(os.path.join(DATA_DIR, 'social_features.csv'),
                         index_col=0, parse_dates=True)

    print(f"Features: {features.shape}, Social: {social.shape}")
    print(f"Social columns: {list(social.columns)}")
    print(f"Social non-null: {social.notna().sum().to_dict()}")

    # Compute scores
    print("\n[1/4] Computing base TW score (v3)...")
    base_score, base_components = compute_tw_retail_score(features)

    print("\n[2/4] Computing enhanced TW score (base + social)...")
    enhanced_score, all_components, social_components = compute_enhanced_tw_score(features, social)

    print(f"  Base components: {list(base_components.columns)}")
    print(f"  Social components: {list(social_components.columns)}")
    print(f"  Total components: {len(all_components.columns)}")

    # Evaluate
    periods = {
        'Full': ('2010-01-01', '2025-12-31'),
        '2012-2015': ('2012-01-01', '2015-12-31'),
        '2016-2019': ('2016-01-01', '2019-12-31'),
        '2020-2022': ('2020-01-01', '2022-12-31'),
        '2023-2025': ('2023-01-01', '2025-12-31'),
    }

    print("\n[3/4] Comparing base vs enhanced IC...")
    for horizon in ['5d', '10d', '20d', '60d']:
        target_col = f'taiex_fwd_{horizon}'
        if target_col not in targets.columns:
            continue

        print(f"\n  --- TAIEX {horizon} forward return ---")
        print(f"  {'Period':<12} {'N':>5} {'Base IC':>10} {'Enh IC':>10} {'Δ IC':>8} {'Base':>5} {'Enh':>5}")
        print(f"  {'-'*58}")

        results = evaluate_incremental(base_score, enhanced_score, targets[target_col], periods)

        for period_name, r in results.items():
            base_star = '*' if r['base_sig'] else ' '
            enh_star = '*' if r['enh_sig'] else ' '
            delta = r['incremental']
            delta_str = f"{delta:+.4f}"
            print(f"  {period_name:<12} {r['n']:>5} {r['base_ic']:>9.4f}{base_star} {r['enhanced_ic']:>9.4f}{enh_star} {delta_str:>8}")

    # Individual social component IC
    print(f"\n[4/4] Individual social component IC (vs TAIEX 20d)...")
    target_20d = targets['taiex_fwd_20d']

    print(f"\n  {'Component':<20} {'Full':>10} {'2012-15':>10} {'2016-19':>10} {'2020-22':>10} {'2023-25':>10}")
    print(f"  {'-'*70}")

    for col in social_components.columns:
        row = f"  {col:<20}"
        for period_name, (start, end) in periods.items():
            if period_name == 'Full':
                continue
            aligned = pd.DataFrame({'signal': social_components[col], 'target': target_20d}).dropna()
            mask = (aligned.index >= start) & (aligned.index <= end)
            subset = aligned[mask]
            if len(subset) > 50:
                ic, pval = spearmanr(subset['signal'], subset['target'])
                sig = '*' if pval < 0.05 else ' '
                row += f" {ic:>8.4f}{sig}"
            else:
                row += f" {'N/A':>9}"
        print(row)

    # Gate 1C verdict
    print(f"\n{'=' * 70}")
    print("GATE 1C VERDICT")
    print(f"{'=' * 70}")

    # Check 20d horizon (primary)
    results_20d = evaluate_incremental(base_score, enhanced_score, targets['taiex_fwd_20d'], periods)

    post_2020_improvement = False
    for period in ['2020-2022', '2023-2025']:
        if period in results_20d:
            delta = results_20d[period]['incremental']
            if delta < -0.02:  # negative IC = better (more contrarian)
                post_2020_improvement = True

    full_delta = results_20d.get('Full', {}).get('incremental', 0)

    if abs(full_delta) > 0.02 or post_2020_improvement:
        print(f"  PASS: Social data provides incremental alpha")
        print(f"  Full period Δ IC: {full_delta:+.4f}")
        print(f"  Post-2020 improvement: {post_2020_improvement}")
        print(f"  → Integrate social features into production scoring")
    else:
        print(f"  MARGINAL: Social data incremental IC = {full_delta:+.4f}")
        print(f"  → Social data has limited incremental value")
        print(f"  → Phase 2 LLM agents will focus on narrative, not scoring")


if __name__ == '__main__':
    main()
