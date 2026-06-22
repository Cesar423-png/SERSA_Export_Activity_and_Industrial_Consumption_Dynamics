"""
visualization.py
================
Reusable plot utilities for:
SERSA Export Activity and Industrial Consumption Dynamics

Author: Cesar Enrique Banda Martinez
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Style constants
# ---------------------------------------------------------------------------
COLOR_EXPORTS      = "#2C7BB6"
COLOR_IMPORTS      = "#D7191C"
COLOR_REVENUE      = "#1A9641"
COLOR_TRANSACTIONS = "#FDAE61"
COLOR_IDI_WEIGHTED = "#1A9641"
COLOR_IDI_EQUAL    = "#D7191C"
COLOR_POS_SIG      = "#1A5276"
COLOR_POS          = "#2C7BB6"
COLOR_NEG_SIG      = "#922B21"
COLOR_NEG          = "#D7191C"


def plot_normalized_series(df, output_path=None, figsize=(14, 5)):
    """
    Plot all four series normalized to [0, 1] on a single axis.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: Month, exports_norm, imports_norm,
        revenue_norm, transactions_norm.
    output_path : str or None
    figsize : tuple
    """
    fig, ax = plt.subplots(figsize=figsize)

    ax.plot(df["Month"], df["exports_norm"],      color=COLOR_EXPORTS,      linewidth=2,   label="Exportaciones (HS4 8708)")
    ax.plot(df["Month"], df["imports_norm"],      color=COLOR_IMPORTS,      linewidth=2,   label="Importaciones (HS4 8708)")
    ax.plot(df["Month"], df["revenue_norm"],      color=COLOR_REVENUE,      linewidth=2,   label="SERSA Revenue")
    ax.plot(df["Month"], df["transactions_norm"], color=COLOR_TRANSACTIONS, linewidth=1.5, linestyle="--", label="SERSA Transactions")

    ax.set_title("Normalized Series Comparison (Min-Max)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Normalized Value [0-1]", fontsize=11)
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(axis="y", alpha=0.3)
    sns.despine()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {output_path}")
    plt.show()


def plot_crosscorr_profile(cc_dict, title="Cross-Correlation Profile",
                            max_lag=6, output_path=None, figsize=(10, 4)):
    """
    Plot a cross-correlation bar chart at lags -max_lag to +max_lag.

    Parameters
    ----------
    cc_dict : dict
        {lag: (r, p_value, n)} — output of cross_corr_profile().
    title : str
    max_lag : int
    output_path : str or None
    figsize : tuple
    """
    lags   = sorted(cc_dict.keys())
    rs     = [cc_dict[l][0] if not np.isnan(cc_dict[l][0]) else 0 for l in lags]
    ps     = [cc_dict[l][1] for l in lags]

    colors = []
    for r, p in zip(rs, ps):
        sig = p is not None and not np.isnan(p) and p < 0.05
        if r >= 0:
            colors.append(COLOR_POS_SIG if sig else COLOR_POS)
        else:
            colors.append(COLOR_NEG_SIG if sig else COLOR_NEG)

    fig, ax = plt.subplots(figsize=figsize)
    ax.bar(lags, rs, color=colors, alpha=0.85)
    ax.axhline(y=0,   color="black",  linewidth=0.8)
    ax.axvline(x=0,   color="gray",   linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axhline(y=0.3, color="orange", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.axhline(y=-0.3,color="orange", linewidth=0.8, linestyle=":", alpha=0.7)
    ax.set_ylim(-1, 1)
    ax.set_xticks(range(-max_lag, max_lag + 1))
    ax.set_xlabel("Lag (months)  [+ = trade leads sales]", fontsize=10)
    ax.set_ylabel("Pearson r", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    sns.despine()
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {output_path}")
    plt.show()


def plot_sensitivity_ranking(sensitivity_df, target_lag=5, top_n=20,
                              output_path=None, figsize=(16, 8)):
    """
    Plot horizontal bar charts of top positive and negative SKU responders.

    Parameters
    ----------
    sensitivity_df : pd.DataFrame
        Output of sku_sensitivity_ranking().
    target_lag : int
    top_n : int
        Number of top positive responders to show.
    output_path : str or None
    figsize : tuple
    """
    r_col   = f"r_at_lag{target_lag}"
    sig_col = f"sig_at_lag{target_lag}"

    top_pos = sensitivity_df.head(top_n)
    top_neg = sensitivity_df.tail(10).sort_values(r_col)

    fig, axes = plt.subplots(1, 2, figsize=figsize)

    colors_pos = [COLOR_POS_SIG if s == "Yes" else COLOR_POS for s in top_pos[sig_col]]
    axes[0].barh(top_pos["SKU"][::-1], top_pos[r_col][::-1],
                 color=colors_pos[::-1], alpha=0.85)
    axes[0].axvline(x=0, color="black", linewidth=0.8)
    axes[0].set_xlabel(f"Pearson r (Exports lag +{target_lag} vs SKU)", fontsize=10)
    axes[0].set_title(f"Top {top_n} Positive Responders\n(dark = p < 0.05)",
                      fontsize=11, fontweight="bold")
    axes[0].grid(axis="x", alpha=0.3)
    sns.despine(ax=axes[0])

    colors_neg = [COLOR_NEG_SIG if s == "Yes" else COLOR_NEG for s in top_neg[sig_col]]
    axes[1].barh(top_neg["SKU"], top_neg[r_col], color=colors_neg, alpha=0.85)
    axes[1].axvline(x=0, color="black", linewidth=0.8)
    axes[1].set_xlabel(f"Pearson r (Exports lag +{target_lag} vs SKU)", fontsize=10)
    axes[1].set_title("Top 10 Negative Responders\n(dark = p < 0.05)",
                      fontsize=11, fontweight="bold")
    axes[1].grid(axis="x", alpha=0.3)
    sns.despine(ax=axes[1])

    fig.suptitle(f"SKU Sensitivity to Automotive Exports — Lag +{target_lag} Months",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {output_path}")
    plt.show()


def plot_idi_vs_exports(idi_weighted, idi_equal, exports_norm,
                         output_path=None, figsize=(14, 9)):
    """
    Plot both IDI versions against normalized export series.

    Parameters
    ----------
    idi_weighted : pd.Series
        Correlation-weighted IDI [0-100].
    idi_equal : pd.Series
        Equal-weighted IDI [0-100].
    exports_norm : pd.Series
        Exports normalized to [0-100].
    output_path : str or None
    figsize : tuple
    """
    fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)

    axes[0].plot(idi_weighted.index, idi_weighted.values,
                 color=COLOR_IDI_WEIGHTED, linewidth=2.5, label="IDI (correlation-weighted)")
    axes[0].plot(exports_norm.index, exports_norm.values,
                 color=COLOR_EXPORTS, linewidth=1.5, linestyle="--", alpha=0.8,
                 label="Automotive Exports (normalized)")
    axes[0].set_ylabel("Index [0-100]", fontsize=10)
    axes[0].set_title("Industrial Demand Index (Weighted) vs Automotive Exports",
                      fontsize=12, fontweight="bold")
    axes[0].legend(fontsize=9)
    axes[0].grid(axis="y", alpha=0.3)
    sns.despine(ax=axes[0])

    axes[1].plot(idi_equal.index, idi_equal.values,
                 color=COLOR_IDI_EQUAL, linewidth=2.5, label="IDI (equal-weighted)")
    axes[1].plot(exports_norm.index, exports_norm.values,
                 color=COLOR_EXPORTS, linewidth=1.5, linestyle="--", alpha=0.8,
                 label="Automotive Exports (normalized)")
    axes[1].set_ylabel("Index [0-100]", fontsize=10)
    axes[1].set_xlabel("Month", fontsize=10)
    axes[1].set_title("Industrial Demand Index (Equal-Weighted) vs Automotive Exports",
                      fontsize=12, fontweight="bold")
    axes[1].legend(fontsize=9)
    axes[1].grid(axis="y", alpha=0.3)
    sns.despine(ax=axes[1])

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        print(f"Saved: {output_path}")
    plt.show()
