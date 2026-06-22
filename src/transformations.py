"""
transformations.py
==================
Data transformation utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import pandas as pd
import numpy as np


def merge_trade_and_sales(exports, imports, monthly_sales):
    """
    Merge export, import, and sales data into a single monthly DataFrame.
    Trims automatically to the overlap period.

    Parameters
    ----------
    exports : pd.DataFrame
        Output of separate_flows() — columns ['Month', 'exports_musd'].
    imports : pd.DataFrame
        Output of separate_flows() — columns ['Month', 'imports_musd'].
    monthly_sales : pd.DataFrame
        Output of aggregate_monthly_sales().

    Returns
    -------
    pd.DataFrame
        Merged DataFrame covering the overlap period.
    """
    merged = (
        exports
        .merge(imports, on="Month", how="inner")
        .merge(monthly_sales, on="Month", how="inner")
        .sort_values("Month")
        .reset_index(drop=True)
    )

    return merged


def add_growth_rates(df):
    """
    Add month-over-month percentage change columns for all numeric series.

    Parameters
    ----------
    df : pd.DataFrame
        Merged monthly DataFrame with columns:
        exports_musd, imports_musd, revenue_mxn, transactions.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with added columns:
        exports_pct, imports_pct, revenue_pct, transactions_pct.
    """
    df = df.copy()

    df["exports_pct"]      = df["exports_musd"].pct_change() * 100
    df["imports_pct"]      = df["imports_musd"].pct_change() * 100
    df["revenue_pct"]      = df["revenue_mxn"].pct_change()  * 100
    df["transactions_pct"] = df["transactions"].pct_change()  * 100

    df.replace([np.inf, -np.inf], np.nan, inplace=True)

    return df


def minmax_normalize(series):
    """
    Normalize a pandas Series to the [0, 1] range using min-max scaling.

    Parameters
    ----------
    series : pd.Series

    Returns
    -------
    pd.Series
        Normalized series. Returns zero series if range is zero.
    """
    rng = series.max() - series.min()
    if rng == 0:
        return series * 0
    return (series - series.min()) / rng


def add_normalized_columns(df):
    """
    Add min-max normalized versions of the main series columns.

    Parameters
    ----------
    df : pd.DataFrame
        Merged monthly DataFrame.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with added _norm columns.
    """
    df = df.copy()

    df["exports_norm"]      = minmax_normalize(df["exports_musd"])
    df["imports_norm"]      = minmax_normalize(df["imports_musd"])
    df["revenue_norm"]      = minmax_normalize(df["revenue_mxn"])
    df["transactions_norm"] = minmax_normalize(df["transactions"])

    return df


def build_sku_monthly_pivot(sales_df, overlap_start, overlap_end):
    """
    Build a monthly SKU transaction count pivot trimmed to the overlap period.

    Parameters
    ----------
    sales_df : pd.DataFrame
        Output of load_sales_data().
    overlap_start : pd.Timestamp
        Start of overlap period.
    overlap_end : pd.Timestamp
        End of overlap period.

    Returns
    -------
    pd.DataFrame
        Wide-format pivot: rows = months, columns = SKUs,
        values = integer transaction counts.
    """
    monthly_sku = (
        sales_df
        .groupby([pd.Grouper(key="Fecha de Consumo", freq="MS"), "SKU"])
        .size()
        .reset_index(name="qty")
        .rename(columns={"Fecha de Consumo": "Month"})
    )

    pivot = (
        monthly_sku
        .pivot(index="Month", columns="SKU", values="qty")
        .fillna(0)
        .astype(int)
    )
    pivot.index.name = "Month"
    pivot.columns.name = None

    pivot = pivot.loc[(pivot.index >= overlap_start) & (pivot.index <= overlap_end)]

    return pivot


def filter_skus(pivot, min_total=10, min_active_months=20):
    """
    Filter SKUs by minimum total transactions and minimum active months.

    Parameters
    ----------
    pivot : pd.DataFrame
        Monthly SKU pivot.
    min_total : int
        Minimum total transactions across all months. Default: 10.
    min_active_months : int
        Minimum number of months with at least 1 transaction. Default: 20.

    Returns
    -------
    pd.DataFrame
        Filtered pivot.
    """
    sku_totals    = pivot.sum()
    active_months = (pivot > 0).sum()

    keep = sku_totals[sku_totals >= min_total].index
    keep = keep.intersection(active_months[active_months >= min_active_months].index)

    return pivot[keep]
