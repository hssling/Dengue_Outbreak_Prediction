# Supplementary Material

**Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India**

This supplement documents the data sources, full predictor set, validation detail and sensitivity analyses underpinning the main text. Every item is regenerable from the released pipeline (`src/11_rigorous_pipeline.py`).

## S1. Study panel
- Unit of analysis: state-month. Panel: **1,740 state-months** = 15 states × 116 months (**May 2015 – December 2024**).
- States (15): Andhra Pradesh, Bihar, Delhi, Gujarat, Haryana, Karnataka, Kerala, Maharashtra, Odisha, Punjab, Rajasthan, Tamil Nadu, Telangana, Uttar Pradesh, West Bengal.
- Cumulative reported cases in panel: **1,266,346**.
- States were retained only where continuous monthly reporting was available; states with sparse or annual-only data were excluded rather than disaggregated to monthly resolution.

## S2. Data sources
| Domain | Source | Access |
| :--- | :--- | :--- |
| Dengue case counts | National Vector Borne Disease Control Programme (NVBDCP / NCVBDC) | https://ncvbdc.mohfw.gov.in (accessed 5 Jan 2025) |
| Case-count reconciliation | OpenDengue v1.x (Clarke et al., *Sci Data* 2024) | https://opendengue.org (accessed 5 Jan 2025) |
| Climate (temperature, rainfall, humidity) | India Meteorological Department gridded products | IMD |
| Health system capacity | NITI Aayog Health Index 2019-20 (Round IV) | NITI Aayog, 2021 |
| Economic | State GDP per capita | Government of India / MoSPI |
| Environmental resilience | State Energy & Climate Index (SECI), Round I | NITI Aayog |
| Urbanisation & density | Census of India 2011 (urban share, population density) | Census 2011 |

## S3. Full feature set (25 predictors, four blocks)
| Block | Features |
| :--- | :--- |
| Autoregressive (5) | cases_lag1, cases_lag2, cases_lag3, cases_lag4, cases_rolling3 |
| Seasonality (3) | month_sin, month_cos, is_monsoon |
| Climate (11) | temperature_c, rainfall_mm, humidity_pct, temp_lag1, temp_lag2, rain_lag1, rain_lag2, humidity_lag1, humidity_lag2, temp_rolling3, rain_rolling3 |
| Vulnerability (6) | health_index_2019_20, gdp_pc, seci_score, urban_pct_2011, density_2011, population_millions |

## S4. Model configuration
- **Regressor:** GradientBoostingRegressor — 300 trees, max_depth 3, learning_rate 0.05, subsample 0.9, least-squares loss on log(1 + cases); predictions back-transformed (expm1) and clipped at 0.
- **Classifier:** GradientBoostingClassifier (same ensemble settings); outbreak = month above the state-specific 75th percentile of cases (435/1,740 positives; 25.0%).
- Hyperparameters fixed a priori (no tuning on test folds), eliminating validation leakage.

## S5. Cross-validation detail (5-fold blocked TimeSeriesSplit, case scale)
| Fold | R² | RMSE | MAE |
| :--- | :--- | :--- | :--- |
| 1 | 0.850 | 226.0 | 122.0 |
| 2 | 0.886 | 236.7 | 134.1 |
| 3 | 0.933 | 189.8 | 113.3 |
| 4 | 0.884 | 258.0 | 134.5 |
| 5 | 0.909 | 251.9 | 154.3 |
| **Mean ± SD** | **0.892 ± 0.028** | **232.5 ± 24.2** | **131.6 ± 13.8** |

Classifier: pooled out-of-fold AUC = 0.936; mean per-fold AUC = 0.938 ± 0.018; sensitivity (Youden-optimal threshold) = 0.909.

## S6. Driver decomposition (grouped Gini importance)
| Block | Importance (%) |
| :--- | :--- |
| Seasonality | 74.0 |
| Autoregressive | 20.8 |
| Vulnerability | 4.0 |
| Climate | 1.2 |

Leading individual features: month_sin (70.0%), cases_rolling3 (18.1%), month_cos (3.8%), urban_pct_2011 (3.0%), cases_lag1 (1.3%), health_index_2019_20 (0.7%).

## S7. Between-state vulnerability association (Spearman, n = 15 states)
| Indicator vs mean monthly burden | ρ | p |
| :--- | :--- | :--- |
| GDP per capita | 0.51 | 0.05 |
| SECI | 0.28 | 0.31 |
| NITI Health Index | 0.23 | 0.41 |

## S8. Field Scorecard validation
The 0–6 ordinal Field Scorecard (active monsoon; prior month above local median; elevated 2-month-lagged rainfall; seasonal peak window) correlated with the full model's forecast at **Spearman ρ = 0.76 (p < 0.001)** across all 1,740 state-months.

## S9. Sensitivity analysis and data notes
- **Missing-value sensitivity.** The NITI Aayog Health Index 2019-20 value for West Bengal was absent in the source release and median-imputed. Re-running the full cross-validation **excluding West Bengal** changed the headline R² from 0.8925 to 0.8899 (**ΔR² = 0.003**) and preserved the driver hierarchy (seasonality 74.5%, autoregressive 18.3%, vulnerability 6.2%, climate 1.0%). The imputation is therefore non-influential.
- **Static covariates.** Structural indices are single-year and inform between-state contrasts rather than within-state temporal change; this is why they contribute modestly to month-ahead prediction yet pattern cross-state burden (S7).

## S10. Full state risk scorecard (all 15 states)
| State | Forecast cases | Health Index (2019-20) | Risk score (0–100) | Category |
| :--- | :--- | :--- | :--- | :--- |
| West Bengal | 1,658 | 51.3* | 100.0 | High |
| Tamil Nadu | 1,411 | 69.1 | 74.8 | High |
| Karnataka | 1,059 | 49.3 | 73.2 | High |
| Maharashtra | 1,097 | 57.9 | 68.2 | Moderate |
| Delhi | 847 | 51.9 | 56.8 | Moderate |
| Rajasthan | 694 | 41.3 | 53.0 | Moderate |
| Andhra Pradesh | 602 | 31.0 | 52.6 | Moderate |
| Kerala | 1,136 | 82.2 | 50.1 | Moderate |
| Haryana | 689 | 44.3 | 50.0 | Moderate |
| Gujarat | 617 | 44.2 | 43.1 | Moderate |
| Telangana | 603 | 47.6 | 38.8 | Low |
| Odisha | 485 | 58.1 | 16.2 | Low |
| Uttar Pradesh | 435 | 50.7 | 15.5 | Low |
| Punjab | 551 | 70.0 | 14.4 | Low |
| Bihar | 454 | 72.4 | 0.0 | Low |

*West Bengal Health Index median-imputed (absent in source release).

## S11. Reproducibility
Python 3.14 with scikit-learn 1.7.2, pandas 2.3.3, NumPy 2.3.5, SciPy 1.16.3, GeoPandas 1.1.1, Matplotlib and seaborn. Pipeline: `src/11_rigorous_pipeline.py` (model + metrics), `src/12_generate_figures.py` (figures), `src/13_build_double_column_docx.py` and `src/14_build_latex_pdf.py` (manuscript). Repository: https://github.com/hssling/Dengue_Outbreak_Prediction
