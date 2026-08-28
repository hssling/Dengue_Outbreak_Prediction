# India Dengue Outbreak Prediction System 🦟🇮🇳

> ### ⚠️ Important correction — August 2026
>
> **The results originally published in this repository were computed on a synthetic
> development dataset, not on observed surveillance data, and the model contained
> target leakage.** `data/raw/dengue_climate_india.csv` is bit-identical to the output
> of `create_synthetic_dengue_data()` in `src/01_fetch_data.py` under `numpy` seed 42,
> and the feature matrix used a 3-month rolling case mean computed without lagging the
> outcome. **The previously reported R² = 0.888 / 0.892 and AUC = 0.936 are withdrawn**,
> as is the "seasonality = 55% / 74%" driver decomposition, which reproduced a seasonal
> multiplier hard-coded in the simulation.
>
> The study has been rebuilt on authenticated data. Everything below the
> [Superseded](#-superseded-original-submission) heading is retained for the audit trail
> and **must not be cited**. See [SOURCES.md](SOURCES.md) to verify the audit yourself.

---

## ✅ Current study (IJDSA revision, R1)

**Structural Determinants Without Short-Term Predictability: A Leakage-Controlled
Benchmark of State-Level Dengue Burden in India, 2015–2024**

An authenticated panel of **350 state-years across 35 states and union territories**,
compiled from NCVBDC annual returns archived by OpenDengue. Nothing is interpolated,
imputed or reconstructed. **All 124 state-years overlapping the independent NCVBDC
bulletin reconcile exactly (100%).**

### Headline findings

Under a strictly leakage-free design — every predictor observable before the forecast
origin, outbreak thresholds and decision cut-offs derived inside training windows:

| Model | Pooled R² | Within-state R² |
| :--- | :--- | :--- |
| **State climatology (training mean)** | **0.637** | −0.002 |
| Negative-binomial GLM (full) | 0.607 | −0.084 |
| Gradient boosting (multi-modal) | 0.551 | −0.239 |
| Persistence (previous year) | 0.550 | −0.241 |
| Gradient boosting (history only) | 0.488 | −0.413 |

* **No machine-learning model beats a state's own historical mean.**
* **Within-state R² is at or below zero for every model** — pooled skill is only the
  recovery of stable between-state differences, not anticipation of temporal change.
* **Outbreak-year classification is at chance** (AUC 0.522; average precision 0.468
  against a prevalence of 0.452; Brier 0.326, *worse* than the 0.248 non-informative
  baseline).

### What the data *do* support

A strong between-state structural gradient in observed incidence (n = 32 states/UTs):

| Indicator | Spearman ρ | 95% CI | p |
| :--- | :--- | :--- | :--- |
| Urban population share | **0.635** | 0.33–0.82 | < 0.001 |
| GDP per capita | **0.609** | 0.32–0.80 | < 0.001 |
| GDP per capita, adjusted for Health Index | 0.663 | — | < 0.001 |
| State Energy & Climate Index | 0.349 | −0.03–0.68 | 0.050 |
| NITI Aayog Health Index | 0.159 | −0.20–0.48 | 0.383 |

### Leakage experiment

Quantified on identical real data — how far common design defects inflate performance:

| Specification | R² | Inflation |
| :--- | :--- | :--- |
| Leakage-free year-ahead (primary) | 0.551 | — |
| Non-temporal random-split CV | 0.626 | +0.075 |
| Unshifted 3-year rolling mean (target leakage) | 0.759 | **+0.209** |

## 🔬 Reproducing the current study

A fresh clone is ~18 MB and needs **no large downloads** — the India admin-1 slice is
committed, so the full pipeline runs offline.

```bash
pip install -r requirements.txt

python src/20_build_real_panel.py      # panel + NCVBDC reconciliation
python src/21_real_analysis.py         # benchmarks, classification, leakage experiment
python src/22_real_figures.py          # all seven manuscript figures
python src/23_build_revision_docx.py   # clean + tracked-changes manuscripts
python src/24_build_response_letter.py
python src/25_build_supplementary.py

python src/26_verify_revision.py       # 67 integrity checks
python src/27_audit_revision.py        # 37 adversarial checks
```

Both verification suites exit non-zero on failure. `27_audit_revision.py` includes a
**future-information test**: it corrupts every observation at or after the target year
and asserts that no predictor changes.

Only `fig6_incidence_map.png` needs an extra download (the Natural Earth boundary
archive); see [SOURCES.md](SOURCES.md) for URLs and SHA-256 checksums of every input.

### Current file map

```
├── data/
│   ├── raw/data_related/*.csv                      # NITI, GDP, SECI, Census (tracked)
│   ├── raw/Dengue data India 2022-2025.xlsx        # NCVBDC bulletin, for reconciliation
│   ├── raw/dengue_climate_india.csv                # synthetic data, kept as audit evidence
│   └── processed/
│       ├── opendengue_india_admin1_year.csv        # committed India slice (672 records)
│       └── real_state_year_panel.csv               # 350-state-year analysis panel
├── outputs/
│   ├── real/                                       # metrics, reconciliation, forecasts
│   └── figures_real/                               # seven manuscript figures, 330 dpi
├── reports/MANUSCRIPT_IJDSA_R1.md                  # master manuscript text
├── MMI_submission_package/IJDSA_R1/                # THE 5 FILES TO UPLOAD (see its README)
├── src/20-28                                       # canonical pipeline (see above)
└── SOURCES.md                                      # provenance and checksums
```

**Superseded — do not use for any reported result:** `src/01`–`src/14`,
`reports/MANUSCRIPT_FINAL.md`, `reports/MANUSCRIPT_IJDSA.md`, `outputs/models/`,
`outputs/figures/`, `outputs/enhanced/`, and all `Main_Manuscript_IJMR_*` files.

---

## 🗄️ Superseded (original submission)

> Everything in this section describes the **withdrawn** synthetic-data analysis. It is
> retained unaltered so the correction is auditable. Do not cite these numbers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Model R2](https://img.shields.io/badge/GradientBoosting-R%C2%B2%200.888-red)](outputs/models)

A robust, multi-modal machine learning system for predicting dengue outbreaks in India using epidemiological, climate, and socio-economic vulnerability indicators.

### 🚀 Key Features

*   **Multi-Source Integration**: Merges NVBDCP data, OpenDengue trends, Real-time Climate (IMD/State), and Socio-Economic indices (NITI Aayog Health Index, GDP).
*   **High Performance**: Gradient Boosting Regressor achieving **R² = 0.888** and **RMSE = 311 cases**.
*   **Risk Scoring**: Generates state-wise composite risk scores (0-100) combining forecast magnitude, structural vulnerability, and climate suitability.
*   **Public Health Focus**: Designed for operational use by state health departments.

### 📊 Results Summary

| Model | R² Score | RMSE (Cases) | Key Advantage |
| :--- | :--- | :--- | :--- |
| **Gradient Boosting** | **0.888** | **311.5** | Best non-linear capture of rain-temp interactions |
| Random Forest | 0.867 | 342.6 | Robust baseline |

#### Top Risk Drivers
1. **Seasonality (55%)**: Month, Monsoon timing
2. **Climate (25%)**: Lagged Rain-Temp interactions
3. **Vulnerability (20%)**: Health Index, GDP

### 📂 Project Structure

```
Dengue_Outbreak_Prediction/
├── data/
│   ├── raw/                # Original Datasets (NVBDCP, OpenDengue)
│   └── processed/          # Integrated training data
├── outputs/
│   ├── enhanced/           # Risk scorecards (state_risk_scorecard.csv)
│   ├── figures/            # Feature importance & Risk plots
│   └── models/             # Trained joblib models
├── reports/
│   ├── MANUSCRIPT_FINAL.md # Publication-ready manuscript
│   └── PUBLIC_HEALTH_GUIDE.md # Guide for practitioners
├── src/
│   ├── 01_fetch_data.py    # Data acquisition
│   ├── 06_enhanced_model.py # Main training & risk scoring
│   └── 07_generate_final_figures.py # Visualization
└── requirements.txt
```

### 🛠️ Usage

#### 1. Installation
```bash
pip install -r requirements.txt
```

#### 2. Run the Pipeline
```bash
# Run the enhanced multi-modal model
python src/06_enhanced_model.py

# Generate visualization figures
python src/07_generate_final_figures.py
```

#### 3. Check Outputs
*   **Risk Scorecard**: `outputs/enhanced/state_risk_scorecard.csv`
*   **Manuscript**: `reports/MANUSCRIPT_FINAL.md`

---

## 👥 Authors

**Dr. Siddalingaiah H S**  
*Lead Investigator & Developer*

Sowjanya D · Rangaswamy H V
*Department of Community Medicine, Shridevi Institute of Medical Sciences and Research
Hospital, Tumkur 572106, Karnataka, India*

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Data Sources
*   **NVBDCP / NCVBDC**: State-wise dengue cases (annual; the sole epidemiological source of the current study)
*   **OpenDengue**: Spatial extract V1.3, India admin-1 annual records
*   **NITI Aayog**: Health Index 2019-20; State Energy & Climate Index round 1
*   **MoSPI**: State GDP per capita
*   **Census of India 2011**: Population, urban share, density
*   **Natural Earth**: Admin-1 boundaries (choropleth only)

Full provenance, redistribution notes and SHA-256 checksums: [SOURCES.md](SOURCES.md).
