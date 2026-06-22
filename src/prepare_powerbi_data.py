"""
prepare_powerbi_data.py
=======================
Generates clean CSV files optimized for Power BI import.

Run from the project root:
    python src/prepare_powerbi_data.py

Outputs saved to outputs/tables/powerbi/
"""

import os
import pandas as pd
import numpy as np

ROOT       = os.path.join(os.path.dirname(__file__), "..")
TABLES_DIR = os.path.join(ROOT, "outputs", "tables")
PROC_DIR   = os.path.join(ROOT, "data", "processed")
POWERBI    = os.path.join(TABLES_DIR, "powerbi")
os.makedirs(POWERBI, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Main merged dataset — Page 1 trend visuals
# ---------------------------------------------------------------------------
merged = pd.read_csv(os.path.join(PROC_DIR, "merged_monthly_data_enriched.csv"),
                     parse_dates=["Month"], decimal=",")

# Round for readability
merged["exports_musd"]  = merged["exports_musd"].round(2)
merged["imports_musd"]  = merged["imports_musd"].round(2)
merged["revenue_mxn"]   = merged["revenue_mxn"].round(2)
merged["profit_mxn"]    = merged["profit_mxn"].round(2)
merged["exports_pct"]   = merged["exports_pct"].round(4)
merged["imports_pct"]   = merged["imports_pct"].round(4)
merged["revenue_pct"]   = merged["revenue_pct"].round(4)
merged["transactions_pct"] = merged["transactions_pct"].round(4)

merged.to_csv(os.path.join(POWERBI, "pb_merged_monthly.csv"), index=False)
print(f"pb_merged_monthly.csv          -> {merged.shape}")

# ---------------------------------------------------------------------------
# 2. Cross-correlation results — Page 1 lag analysis visual
# ---------------------------------------------------------------------------
cc = pd.read_csv(os.path.join(TABLES_DIR, "03_crosscorr_results.csv"), decimal=",")
cc.to_csv(os.path.join(POWERBI, "pb_crosscorr_results.csv"), index=False)
print(f"pb_crosscorr_results.csv       -> {cc.shape}")

# ---------------------------------------------------------------------------
# 3. Correlation results summary — Page 1 KPI cards
# ---------------------------------------------------------------------------
corr = pd.read_csv(os.path.join(TABLES_DIR, "03_correlation_results.csv"), decimal=",")
corr.to_csv(os.path.join(POWERBI, "pb_correlation_results.csv"), index=False)
print(f"pb_correlation_results.csv     -> {corr.shape}")

# ---------------------------------------------------------------------------
# 4. Product sensitivity ranking — Page 2
# ---------------------------------------------------------------------------
sensitivity = pd.read_csv(os.path.join(TABLES_DIR, "04_product_sensitivity_ranking.csv"),
                          decimal=",")

# Add readable fields
sensitivity["r_pct"]       = (sensitivity["r_at_lag5"] * 100).round(1)
sensitivity["significant_label"] = sensitivity["sig_at_lag5"].map(
    {"Yes": "Significant (p<0.05)", "No": "Not significant"}
)
sensitivity["rank"] = range(1, len(sensitivity) + 1)

sensitivity.to_csv(os.path.join(POWERBI, "pb_product_sensitivity.csv"), index=False)
print(f"pb_product_sensitivity.csv     -> {sensitivity.shape}")

# ---------------------------------------------------------------------------
# 5. Industrial Demand Index — Page 2
# ---------------------------------------------------------------------------
idi = pd.read_csv(os.path.join(TABLES_DIR, "05_industrial_demand_index.csv"), decimal=",")
idi.to_csv(os.path.join(POWERBI, "pb_industrial_demand_index.csv"), index=False)
print(f"pb_industrial_demand_index.csv -> {idi.shape}")

# ---------------------------------------------------------------------------
# 6. KPI summary — Page 1 cards
# ---------------------------------------------------------------------------
kpis = pd.DataFrame([
    {"KPI": "Total Exports (MUSD)",   "Value": round(merged["exports_musd"].sum(), 1)},
    {"KPI": "Total Revenue (MXN)",    "Value": round(merged["revenue_mxn"].sum(), 0)},
    {"KPI": "Best Correlation (r)",   "Value": 0.513},
    {"KPI": "Best Lag (months)",      "Value": 5},
    {"KPI": "Months analyzed",        "Value": len(merged)},
    {"KPI": "Significant SKUs",       "Value": int(sensitivity["sig_at_lag5"].value_counts().get("Yes", 0))},
])

kpis.to_csv(os.path.join(POWERBI, "pb_kpis.csv"), index=False)
print(f"pb_kpis.csv                    -> {kpis.shape}")

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
print()
print(f"All files saved to: {os.path.normpath(POWERBI)}")