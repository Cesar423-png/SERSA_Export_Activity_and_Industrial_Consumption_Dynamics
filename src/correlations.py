"""
correlations.py
===============
Correlation utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import pandas as pd
import numpy as np
from scipy import stats


def pearson_with_pvalue(x, y):
    """
    Compute Pearson correlation and p-value between two series,
    dropping NaN pairs automatically.

    Parameters
    ----------
    x, y : pd.Series

    Returns
    -------
    tuple (r, p_value, n)
    """
    mask = ~(x.isna() | y.isna())
    x_c, y_c = x[mask], y[mask]
    if len(x_c) < 3:
        return np.nan, np.nan, 0
    r, p = stats.pearsonr(x_c, y_c)
    return round(r, 4), round(p, 4), len(x_c)


def spearman_with_pvalue(x, y):
    """
    Compute Spearman correlation and p-value between two series,
    dropping NaN pairs automatically.

    Parameters
    ----------
    x, y : pd.Series

    Returns
    -------
    tuple (r, p_value, n)
    """
    mask = ~(x.isna() | y.isna())
    x_c, y_c = x[mask], y[mask]
    if len(x_c) < 3:
        return np.nan, np.nan, 0
    r, p = stats.spearmanr(x_c, y_c)
    return round(r, 4), round(p, 4), len(x_c)


def correlation_table(df, x_cols, y_cols, labels=None):
    """
    Compute Pearson and Spearman correlations for multiple variable pairs.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing all variables.
    x_cols : list of str
        Column names for X variables.
    y_cols : list of str
        Column names for Y variables (paired with x_cols).
    labels : list of str, optional
        Human-readable labels for each pair.

    Returns
    -------
    pd.DataFrame
        Results table with columns:
        [Pair, Method, r, p_value, n, significant]
    """
    if labels is None:
        labels = [f"{x} vs {y}" for x, y in zip(x_cols, y_cols)]

    records = []
    for x_col, y_col, label in zip(x_cols, y_cols, labels):
        for method, func in [("Pearson", pearson_with_pvalue),
                              ("Spearman", spearman_with_pvalue)]:
            r, p, n = func(df[x_col], df[y_col])
            records.append({
                "Pair"       : label,
                "Method"     : method,
                "r"          : r,
                "p_value"    : p,
                "n"          : n,
                "significant": "Yes" if (p is not None and
                                         not np.isnan(p) and
                                         p < 0.05) else "No"
            })

    return pd.DataFrame(records)
