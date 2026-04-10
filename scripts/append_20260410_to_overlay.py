#!/usr/bin/env python3
"""
One-shot repair: append 2026-04-10 row to overlay_data.json.

Root cause of the missing row:
  The merge commit 000b5ac resolved a conflict between the 04-10 daily run
  (1b1e535, which had 04-10 in overlay) and the flatline-fix branch (659866c,
  which branched from before the 04-10 daily run and therefore didn't have it).
  The merge chose the fix-branch version of overlay_data.json, dropping 04-10.

Source of truth for 04-10 values:
  - historical_scores.csv (us_score=78.2, tw_score=84.6)
  - data/snapshot_20260410.json (all market prices + JP/KR/EU scores)

After running this script, verify with:
  python3 -c "import json; d=json.load(open('data/overlay_data.json')); print(d['dates'][-3:])"
"""
import json
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(REPO_ROOT, 'data')
DOCS_DIR  = os.path.join(REPO_ROOT, 'docs', 'data')

DATE = '2026-04-10'

# TW dates that must remain null (flatline fix from 000b5ac — do not regress)
TW_NULL_DATES = {'2026-04-03', '2026-04-06', '2026-04-07'}


def patch_overlay(path: str) -> None:
    with open(path, 'r', encoding='utf-8') as f:
        ov = json.load(f)

    # Guard: refuse to re-append if all arrays already have 04-10
    if ov.get('dates') and ov['dates'][-1] == DATE:
        if ov.get('tw_score') and len(ov['tw_score']) == len(ov['dates']):
            print(f'  [SKIP] {path}: {DATE} already fully present')
            return
        # tw_score might be one short from a previous partial run — fall through
        print(f'  [PARTIAL] {path}: dates has {DATE} but tw_score length mismatch — patching tw_score only')
        if len(ov.get('tw_score', [])) < len(ov.get('dates', [])):
            ov.setdefault('tw_score', []).append(84.6)
        _save_and_print(path, ov, partial=True)
        return

    # ── Append all arrays ──────────────────────────────────────────────────
    # US/TW scores share the same dates array
    ov.setdefault('dates', []).append(DATE)
    ov.setdefault('us_score', []).append(78.2)
    ov.setdefault('tw_score', []).append(84.6)

    # US prices
    ov.setdefault('spy_dates', []).append(DATE)
    ov.setdefault('spy', []).append(680.84)

    # TW prices
    ov.setdefault('twii_dates', []).append(DATE)
    ov.setdefault('twii', []).append(35418.0)

    # JP scores + prices
    ov.setdefault('jp_dates', []).append(DATE)
    ov.setdefault('jp_score', []).append(86.8)
    ov.setdefault('nikkei_dates', []).append(DATE)
    ov.setdefault('nikkei', []).append(56924.11)

    # KR scores + prices
    ov.setdefault('kr_dates', []).append(DATE)
    ov.setdefault('kr_score', []).append(72.9)
    ov.setdefault('kospi_dates', []).append(DATE)
    ov.setdefault('kospi', []).append(5858.87)

    # EU scores + prices
    ov.setdefault('eu_dates', []).append(DATE)
    ov.setdefault('eu_score', []).append(75.0)
    ov.setdefault('stoxx50_dates', []).append(DATE)
    ov.setdefault('stoxx50', []).append(5946.17)

    _save_and_print(path, ov, partial=False)


def _save_and_print(path, ov, partial):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(ov, f, ensure_ascii=False)
    label = 'patched tw_score' if partial else f'appended {DATE} (all arrays)'
    print(f'  [OK] {path}: {label}')


def verify(path: str) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        ov = json.load(f)

    checks = {
        'dates': DATE, 'us_score': 78.2, 'tw_score': 84.6,
        'spy_dates': DATE, 'spy': 680.84,
        'twii_dates': DATE, 'twii': 35418.0,
        'jp_dates': DATE, 'jp_score': 86.8,
        'nikkei_dates': DATE, 'nikkei': 56924.11,
        'kr_dates': DATE, 'kr_score': 72.9,
        'kospi_dates': DATE, 'kospi': 5858.87,
        'eu_dates': DATE, 'eu_score': 75.0,
        'stoxx50_dates': DATE, 'stoxx50': 5946.17,
    }
    ok = True
    for key, expected in checks.items():
        arr = ov.get(key, [])
        last = arr[-1] if arr else None
        if last != expected:
            print(f'  [FAIL] {key}: last={last!r} (expected {expected!r})')
            ok = False
        else:
            print(f'  [OK]   {key}: {last}')

    # Array length consistency: dates/us_score/tw_score must be same length
    nd = len(ov.get('dates', []))
    nus = len(ov.get('us_score', []))
    ntw = len(ov.get('tw_score', []))
    if nd != nus or nd != ntw:
        print(f'  [FAIL] length mismatch: dates={nd} us_score={nus} tw_score={ntw}')
        ok = False
    else:
        print(f'  [OK]   dates/us_score/tw_score lengths consistent: {nd}')

    # TW null-dates must still be null (flatline fix must not regress)
    tw_dates = ov.get('dates', [])
    tw_scores = ov.get('tw_score', [])
    for i, d in enumerate(tw_dates):
        if d in TW_NULL_DATES:
            if tw_scores[i] is not None:
                print(f'  [FAIL] TW null regression: tw_score[{d}]={tw_scores[i]}')
                ok = False
            else:
                print(f'  [OK]   tw_score[{d}] = None (null preserved)')

    return ok


def main():
    data_path = os.path.join(DATA_DIR, 'overlay_data.json')
    docs_path = os.path.join(DOCS_DIR, 'overlay_data.json')

    print(f'=== Patching {data_path} ===')
    patch_overlay(data_path)

    print(f'\n=== Patching {docs_path} ===')
    patch_overlay(docs_path)

    print(f'\n=== Verification: data/overlay_data.json ===')
    ok1 = verify(data_path)

    print(f'\n=== Verification: docs/data/overlay_data.json ===')
    ok2 = verify(docs_path)

    if ok1 and ok2:
        print('\nAll checks passed.')
    else:
        print('\nSome checks failed — review output above.')

    print('\nNext: git diff --stat data/overlay_data.json docs/data/overlay_data.json')


if __name__ == '__main__':
    main()
