"""
cleaning.py
===========
Data cleaning utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import pandas as pd
import numpy as np


def load_trade_data(filepath):
    """
    Load and validate the raw trade flow CSV from DataMéxico API.

    Parameters
    ----------
    filepath : str
        Path to the raw CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with columns:
        ['Flow', 'Month', 'Trade_Value_MUSD']
    """
    df = pd.read_csv(filepath)

    required_cols = ["Flow", "Month", "Trade Value"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in trade data: {missing}")

    df["Month"] = pd.to_datetime(df["Month"], format="%Y-%m")
    df["Trade_Value_MUSD"] = (df["Trade Value"] / 1_000_000).round(2)

    return df[["Flow", "Month", "Trade_Value_MUSD"]].copy()


def separate_flows(trade_df):
    """
    Separate a combined trade DataFrame into exports and imports series.

    Parameters
    ----------
    trade_df : pd.DataFrame
        Output of load_trade_data().

    Returns
    -------
    tuple (exports, imports)
        Two DataFrames with columns ['Month', 'exports_musd'] and
        ['Month', 'imports_musd'] respectively, sorted by Month.
    """
    exports = (
        trade_df[trade_df["Flow"] == "Exportaciones"]
        [["Month", "Trade_Value_MUSD"]]
        .rename(columns={"Trade_Value_MUSD": "exports_musd"})
        .sort_values("Month")
        .reset_index(drop=True)
    )

    imports = (
        trade_df[trade_df["Flow"] == "Importaciones"]
        [["Month", "Trade_Value_MUSD"]]
        .rename(columns={"Trade_Value_MUSD": "imports_musd"})
        .sort_values("Month")
        .reset_index(drop=True)
    )

    return exports, imports


def load_sales_data(filepath):
    """
    Load and validate master_sales.csv.

    Parameters
    ----------
    filepath : str
        Path to master_sales.csv.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame with datetime column parsed.
    """
    df = pd.read_csv(filepath)

    required_cols = ["Fecha de Consumo", "SKU", "Price", "Company", "Profit"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in sales data: {missing}")

    df["Fecha de Consumo"] = pd.to_datetime(df["Fecha de Consumo"])

    return df


def aggregate_monthly_sales(sales_df):
    """
    Aggregate transaction-level sales data to monthly totals.

    Parameters
    ----------
    sales_df : pd.DataFrame
        Output of load_sales_data().

    Returns
    -------
    pd.DataFrame
        Monthly DataFrame with columns:
        ['Month', 'transactions', 'revenue_mxn', 'profit_mxn']
    """
    monthly = (
        sales_df
        .groupby(pd.Grouper(key="Fecha de Consumo", freq="MS"))
        .agg(
            transactions=("SKU", "count"),
            revenue_mxn=("Price", "sum"),
            profit_mxn=("Profit", "sum")
        )
        .reset_index()
        .rename(columns={"Fecha de Consumo": "Month"})
    )

    monthly["revenue_mxn"] = monthly["revenue_mxn"].round(2)
    monthly["profit_mxn"]  = monthly["profit_mxn"].round(2)

    return monthly
