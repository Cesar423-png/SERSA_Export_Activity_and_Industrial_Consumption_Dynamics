"""
indicators.py
=============
Industrial Demand Index construction utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import pandas as pd
import numpy as np


def minmax_normalize(series):
    """
    Normalize a pandas Series to [0, 1] using min-max scaling.

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
    """
    rng = series.max() - series.min()
    if rng == 0:
        return series * 0
    return (series - series.min()) / rng


def scale_to_100(series):
    """
    Rescale a pandas Series to [0, 100].

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
    """
    return minmax_normalize(series) * 100


def build_demand_index(pivot, weights=None):
    """
    Build a composite Industrial Demand Index from a normalized SKU pivot.

    Parameters
    ----------
    pivot : pd.DataFrame
        Wide-format DataFrame of normalized SKU values (rows=months, cols=SKUs).
        Each column should already be in [0, 1].
    weights : pd.Series or None
        Optional weights indexed by SKU name. If None, equal weights are used.
        Weights are normalized to sum to 1 internally.

    Returns
    -------
    pd.Series
        Composite index scaled to [0, 100], indexed by Month.
    """
    pivot_norm = pivot.apply(minmax_normalize)

    if weights is not None:
        weights = weights.reindex(pivot_norm.columns).dropna()
        weights = weights / weights.sum()
        index = pivot_norm[weights.index].mul(weights, axis=1).sum(axis=1)
    else:
        index = pivot_norm.mean(axis=1)

    return scale_to_100(index)


def validate_index_vs_trade(index_series, trade_series, max_lag=7):
    """
    Validate an index by computing cross-correlation against a trade series
    at lags -3 to max_lag.

    Parameters
    ----------
    index_series : pd.Series
        Industrial Demand Index (e.g. pct_change of IDI).
    trade_series : pd.Series
        Trade flow growth rate (e.g. exports_pct).
    max_lag : int
        Maximum positive lag to test. Default: 7.

    Returns
    -------
    pd.DataFrame
        Columns: [lag, r_weighted, p_weighted, r_equal, p_equal]
        (designed to compare two index versions simultaneously)
    """
    from lag_analysis import cross_corr_at_lag

    records = []
    for lag in range(-3, max_lag + 1):
        r, p, n = cross_corr_at_lag(trade_series, index_series, lag)
        records.append({
            "lag"    : lag,
            "r"      : r,
            "p_value": p,
            "n"      : n,
            "significant": "Yes" if (p is not None and
                                     not np.isnan(p) and
                                     p < 0.05) else "No"
        })

    return pd.DataFrame(records)
