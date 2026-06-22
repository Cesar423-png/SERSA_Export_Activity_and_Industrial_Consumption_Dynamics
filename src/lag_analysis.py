"""
lag_analysis.py
===============
Cross-correlation and lead-lag analysis utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import pandas as pd
import numpy as np
from scipy import stats


def cross_corr_at_lag(series_a, series_b, lag):
    """
    Compute Pearson correlation between series_a[t] and series_b[t+lag].

    Positive lag: series_a leads series_b.
    Negative lag: series_b leads series_a.

    Parameters
    ----------
    series_a : pd.Series
        Leading series (e.g. export growth rate).
    series_b : pd.Series
        Lagged series (e.g. SKU growth rate).
    lag : int
        Lag in periods. Positive = series_a leads.

    Returns
    -------
    tuple (r, p_value, n)
    """
    if lag == 0:
        a = series_a.reset_index(drop=True)
        b = series_b.reset_index(drop=True)
    elif lag > 0:
        a = series_a.iloc[:-lag].reset_index(drop=True)
        b = series_b.iloc[lag:].reset_index(drop=True)
    else:
        a = series_a.iloc[-lag:].reset_index(drop=True)
        b = series_b.iloc[:lag].reset_index(drop=True)

    combined = pd.concat([a, b], axis=1).dropna()

    if len(combined) < 5:
        return np.nan, np.nan, 0

    r, p = stats.pearsonr(combined.iloc[:, 0], combined.iloc[:, 1])
    return round(r, 4), round(p, 4), len(combined)


def cross_corr_profile(series_a, series_b, max_lag=6):
    """
    Compute full cross-correlation profile at lags -max_lag to +max_lag.

    Parameters
    ----------
    series_a : pd.Series
    series_b : pd.Series
    max_lag : int
        Maximum lag in both directions. Default: 6.

    Returns
    -------
    pd.DataFrame
        Columns: [lag, Pearson_r, p_value, n, significant]
    """
    records = []
    for lag in range(-max_lag, max_lag + 1):
        r, p, n = cross_corr_at_lag(series_a, series_b, lag)
        records.append({
            "lag"        : lag,
            "Pearson_r"  : r,
            "p_value"    : p,
            "n"          : n,
            "significant": "Yes" if (p is not None and
                                     not np.isnan(p) and
                                     p < 0.05) else "No"
        })
    return pd.DataFrame(records)


def dominant_lag(profile_df):
    """
    Return the lag with the highest absolute cross-correlation.

    Parameters
    ----------
    profile_df : pd.DataFrame
        Output of cross_corr_profile().

    Returns
    -------
    tuple (lag, r, p_value)
    """
    valid = profile_df.dropna(subset=["Pearson_r"])
    if valid.empty:
        return 0, np.nan, np.nan

    idx = valid["Pearson_r"].abs().idxmax()
    row = valid.loc[idx]
    return int(row["lag"]), row["Pearson_r"], row["p_value"]


def sku_sensitivity_ranking(growth_pivot, trade_series, target_lag=5, max_lag=6):
    """
    Compute cross-correlation between a trade series and each SKU
    in a growth-rate pivot, returning a ranked sensitivity DataFrame.

    Parameters
    ----------
    growth_pivot : pd.DataFrame
        Wide-format DataFrame of SKU growth rates (rows=months, cols=SKUs).
    trade_series : pd.Series
        Trade flow growth rate series (e.g. exports_pct).
    target_lag : int
        Primary lag to rank by. Default: 5.
    max_lag : int
        Maximum lag for full profile. Default: 6.

    Returns
    -------
    pd.DataFrame
        Ranked by r_at_target_lag descending.
    """
    records = []

    for sku in growth_pivot.columns:
        sku_s = growth_pivot[sku]

        r_target, p_target, n_target = cross_corr_at_lag(trade_series, sku_s, target_lag)
        r0, p0, _ = cross_corr_at_lag(trade_series, sku_s, 0)

        best_r, best_lag = 0, 0
        for lag in range(-max_lag, max_lag + 1):
            r, p, n = cross_corr_at_lag(trade_series, sku_s, lag)
            if not np.isnan(r) and abs(r) > abs(best_r):
                best_r, best_lag = r, lag

        records.append({
            "SKU"               : sku,
            f"r_at_lag{target_lag}"  : r_target,
            f"p_at_lag{target_lag}"  : p_target,
            f"n_at_lag{target_lag}"  : n_target,
            f"sig_at_lag{target_lag}": "Yes" if (p_target is not None and
                                                   not np.isnan(p_target) and
                                                   p_target < 0.05) else "No",
            "r_contemporaneous" : r0,
            "p_contemporaneous" : p0,
            "dominant_lag"      : best_lag,
            "max_abs_r"         : round(abs(best_r), 4),
        })

    return (
        pd.DataFrame(records)
        .sort_values(f"r_at_lag{target_lag}", ascending=False)
        .reset_index(drop=True)
    )
