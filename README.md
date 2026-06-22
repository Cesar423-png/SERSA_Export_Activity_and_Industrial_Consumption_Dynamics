# SERSA Export Activity and Industrial Consumption Dynamics

Satellite project of [SERSA Industrial Bajío — Vending Machine Sales Analysis](https://github.com/Cesar423-png/SERSA_Industrial_Bajio_Sales_Analysis).  
It investigates whether regional automotive export and import activity explains the behavior of industrial vending machine demand across 3 automotive clients in the Bajío region of Mexico.

> **Central question:** Is there a quantifiable relationship between Mexico's automotive parts trade flows and the demand for industrial consumables at the plant level?

---

## Business Context

SERSA Industrial Bajío supplies industrial consumables through vending machines to automotive manufacturers in the Bajío region — one of Mexico's most active automotive export corridors.

The hypothesis is that external trade activity, particularly in automotive parts (HS4 code 8708), acts as a leading indicator of manufacturing intensity at the plant level. When export orders are placed, production plans are confirmed, and plant-level procurement — including vending machine consumables — follows several months later.

This project tests that hypothesis quantitatively using 47 months of overlapping data (April 2022 – February 2026) between:
- **Internal data:** 639,568 vending machine transactions from `master_sales.csv`.
- **External data:** Monthly automotive parts trade values (Exportaciones + Importaciones) from Mexico's Secretaría de Economía — DataMéxico API (HS4 8708).

---

## Key Findings

**No contemporaneous relationship exists** between automotive trade flows and SERSA sales — trade activity and plant-level consumption do not move together in the same month.

**A statistically significant lead-lag relationship emerges at lag +5 months** across all pairs tested:

| Pair | r at lag +5 | p-value |
|---|---|---|
| Exports → Revenue | 0.393 | 0.011 |
| Imports → Revenue | 0.381 | 0.014 |
| Exports → Transactions | 0.411 | 0.008 |
| Imports → Transactions | 0.392 | 0.011 |

**12 of 66 active SKUs** show statistically significant sensitivity to export activity at lag +5 (p < 0.05). Top responders:

| SKU | r at lag +5 | p-value |
|---|---|---|
| JYR-2004AM | 0.590 | 0.001 |
| JYG37510 | 0.439 | 0.004 |
| XSAE82701 | 0.408 | 0.008 |
| ME9683M | 0.381 | 0.014 |
| AN37-175T10 | 0.372 | 0.022 |

**The Industrial Demand Index (IDI)**, built from the 12 significant SKUs weighted by correlation strength, validates and amplifies the aggregate signal:

| IDI version | r vs exports at lag +5 | p-value |
|---|---|---|
| Correlation-weighted | **0.513** | **< 0.001** |
| Equal-weighted | **0.504** | **< 0.001** |

**Interpretation:** Automotive export activity in Mexico serves as a delayed indicator of industrial consumable demand at the plant level. A plausible mechanism: export orders are placed → production schedules are confirmed → plant-level procurement of consumables follows approximately 5 months later.

---

## Methodology

The project is structured as a five-layer analytical pipeline.

### Layer 1 — External Data Preparation
**Notebook:** `01_external_data_preparation.ipynb`

Raw trade flow data cleaned and separated into Exportaciones and Importaciones series. Sales transactions aggregated to monthly totals. Both datasets aligned to the same monthly frequency and merged into `merged_monthly_data.csv` covering the 47-month overlap period.

### Layer 2 — Trend Relationships
**Notebook:** `02_trend_relationships.ipynb`

Visual and statistical examination of structural differences between series. Key finding: trade flows are stationary with seasonal cycles while SERSA revenue shows sustained growth (294% increase 2022–2025). Opposite seasonal patterns — exports peak in August, revenue peaks in January — confirm seasonality is not the transmission mechanism. Growth-rate analysis established as the primary analytical approach.

### Layer 3 — Correlation and Lag Analysis
**Notebook:** `03_correlation_and_lag_analysis.ipynb`

Pearson and Spearman correlations on raw levels and growth rates, plus cross-correlation at lags −6 to +6 months. No contemporaneous signal found. Statistically significant positive correlation confirmed at lag +5 for all four variable combinations. Both Exportaciones and Importaciones produce virtually identical results, suggesting they carry the same demand signal.

### Layer 4 — Product-Level Sensitivity
**Notebook:** `04_product_level_sensitivity.ipynb`

Individual SKU cross-correlations against export growth rate at lags −6 to +6. 12 of 66 active SKUs show significant response at lag +5. Dominant lag distribution across all SKUs confirms the +3 to +6 month range identified at aggregate level, with a secondary cluster at lag −1 (11 SKUs) suggesting some products may anticipate export activity rather than follow it.

### Layer 5 — Industrial Demand Index
**Notebook:** `05_industrial_demand_index.ipynb`

Composite IDI constructed from the 12 significant SKUs, each normalized to [0, 1] and weighted by correlation strength at lag +5. Validated against export growth rate at all lags — IDI achieves r = 0.51 (p < 0.001) against exports at lag +5, stronger than any individual SKU or the aggregate revenue series alone.

---

## Key Methodological Decisions

**Why growth rates instead of levels?**  
Trade flows and SERSA revenue have structurally different dynamics — one stationary, one trending. Raw correlations would be dominated by the growth trend in revenue. Growth rates (`pct_change`) remove the trend and isolate genuine co-movement signals.

**Why Exportaciones only for product-level analysis?**  
Importaciones produced nearly identical results at all lags (r difference < 0.02). Using one flow avoids redundancy. Exportaciones has slightly stronger correlation for transactions and clearer economic interpretation.

**Why lag +5 as the target for the IDI?**  
Determined empirically from aggregate cross-correlation in notebook 03 — the lag with the highest statistically significant correlation across all variable pairs.

**Why correlation-weighted IDI?**  
SKUs with stronger demonstrated response to trade flows should contribute more to a composite indicator. The equal-weighted version is included for comparison — both versions produce nearly identical results (r difference < 0.01), confirming the index is robust to weighting choice.

---

## Data Sources

| Dataset | Source | Coverage | Frequency |
|---|---|---|---|
| Vending machine transactions | SERSA Industrial Bajío (anonymized) | Apr 2022 – May 2026 | Transaction-level |
| Automotive parts trade flows | Secretaría de Economía — DataMéxico API | Jan 2006 – Feb 2026 | Monthly |

**API endpoint:**
```
http://www.economia.gob.mx/datamexico/api/data?HS4+4+Digit=178708&Product+Level=4&cube=economy_foreign_trade_nat&drilldowns=Flow,Month&locale=es&measures=Trade+Value&parents=false
```

---

## Project Structure

```
SERSA_Export_Activity_and_Industrial_Consumption_Dynamics/
├── data/
│   ├── raw/                    ← original trade flow CSV + master_sales.csv
│   ├── processed/              ← pipeline outputs
│   └── external/               ← methodology notes, source metadata
├── notebooks/
│   ├── 01_external_data_preparation.ipynb
│   ├── 02_trend_relationships.ipynb
│   ├── 03_correlation_and_lag_analysis.ipynb
│   ├── 04_product_level_sensitivity.ipynb
│   └── 05_industrial_demand_index.ipynb
├── src/
│   ├── cleaning.py
│   ├── transformations.py
│   ├── correlations.py
│   ├── lag_analysis.py
│   ├── indicators.py
│   └── visualization.py
├── dashboard/
│   └── powerbi/
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── reports/
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Notebook Overview

| # | Notebook | Input | Output |
|---|----------|-------|--------|
| 01 | `01_external_data_preparation` | Raw trade CSV + `master_sales.csv` | `merged_monthly_data.csv` — 47 months |
| 02 | `02_trend_relationships` | `merged_monthly_data.csv` | Normalized plots, growth rate comparison, seasonal patterns |
| 03 | `03_correlation_and_lag_analysis` | `merged_monthly_data_enriched.csv` | Correlation tables, cross-correlation profiles, dominant lag |
| 04 | `04_product_level_sensitivity` | `merged_monthly_data_enriched.csv` + `master_sales.csv` | Sensitivity ranking — 66 SKUs |
| 05 | `05_industrial_demand_index` | Sensitivity ranking + trade data | IDI — 47 months, validated at lag +5 |

---

## How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/Cesar423-png/SERSA_Export_Activity_and_Industrial_Consumption_Dynamics.git
   cd SERSA_Export_Activity_and_Industrial_Consumption_Dynamics
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Copy source files** into `data/raw/`:
   - `master_sales.csv` from the main project.
   - Trade flow CSV from the DataMéxico API.

4. **Run the notebooks in order** from within the `notebooks/` directory:
   ```
   01 → 02 → 03 → 04 → 05
   ```

---

## Related Projects

| Project | Focus |
|---|---|
| [SERSA Industrial Bajío — Sales Analysis](https://github.com/Cesar423-png/SERSA_Industrial_Bajio_Sales_Analysis) | Business KPIs, revenue trends, profitability, Pareto |
| [SERSA Product Demand Relationship Analysis](https://github.com/Cesar423-png/SERSA_Product_Demand_Relationship_Analysis) | Inter-product correlations, lead-lag, demand network |
| **This project** | External trade drivers, lead-lag econometrics, Industrial Demand Index |

---

## Tech Stack

- **Python 3.14** — pandas, numpy, matplotlib, seaborn, scipy
- **Jupyter Notebook**
- **Power BI** — dashboard in progress

---

## Author

Cesar Enrique Banda Martinez — [LinkedIn](https://www.linkedin.com/in/c%C3%A9sar-banda-79b6b3262/?locale=en_US) · [GitHub](https://github.com/Cesar423-png)