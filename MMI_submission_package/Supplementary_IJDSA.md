# Supplementary Material

**Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India**

This supplement documents the data, full predictor set, validation detail and sensitivity analyses underpinning the main text. All items are regenerable from the released pipeline (`src/11_rigorous_pipeline.py`).

## S1. Study panel
- Unit of analysis: state-month. Panel: **1,740 state-months** = 15 states × 116 months (January 2015 – August 2024).
- States (15): Andhra Pradesh, Bihar, Delhi, Gujarat, Haryana, Karnataka, Kerala, Maharashtra, Odisha, Punjab, Rajasthan, Tamil Nadu, Telangana, Uttar Pradesh, West Bengal.
- Cumulative reported cases in panel: 1,266,346.

## S2. Full feature set (25 predictors, four blocks)
| Block | Features |
| :--- | :--- |
| Autoregressive (5) | cases_lag1, cases_lag2, cases_lag3, cases_lag4, cases_rolling3 |
| Seasonality (3) | month_sin, month_cos, is_monsoon |
| Climate (11) | temperature_c, rainfall_mm, humidity_pct, temp_lag1, temp_lag2, rain_lag1, rain_lag2, humidity_lag1, humidity_lag2, temp_rolling3, rain_rolling3 |
| Vulnerability (6) | health_index_2019_20, gdp_pc, seci_score, urban_pct_2011, density_2011, population_millions |

## S3. Model configuration
- **Regressor:** GradientBoostingRegressor — 300 trees, max_depth 3, learning_rate 0.05, subsample 0.9, least-squares loss on log(1 + cases); predictions back-transformed (expm1) and clipped at 0.
- **Classifier:** GradientBoostingClassifier (same ensemble settings); outbreak = month above the state-specific 75th percentile of cases (435/1,740 positives; 25%).
- Hyperparameters fixed a priori (no tuning on test folds).

## S4. Cross-validation detail (5-fold blocked TimeSeriesSplit, case scale)
| Fold | R² | RMSE | MAE |
| :--- | :--- | :--- | :--- |
| 1 | 0.850 | 226.0 | 122.0 |
| 2 | 0.886 | 236.7 | 134.1 |
| 3 | 0.933 | 189.8 | 113.3 |
| 4 | 0.884 | 258.0 | 134.5 |
| 5 | 0.909 | 251.9 | 154.3 |
| **Mean ± SD** | **0.892 ± 0.028** | **232.5 ± 24.2** | **131.6 ± 13.8** |

Classifier: pooled out-of-fold AUC = 0.936; mean per-fold AUC = 0.938 ± 0.018; sensitivity (Youden) = 0.909.

## S5. Driver decomposition (grouped Gini importance)
| Block | Importance (%) |
| :--- | :--- |
| Seasonality | 74.0 |
| Autoregressive | 20.8 |
| Vulnerability | 4.0 |
| Climate | 1.2 |

Leading individual features: month_sin (70.0%), cases_rolling3 (18.1%), month_cos (3.8%), urban_pct (3.0%), cases_lag1 (1.3%), health_index (0.7%).

## S6. Between-state vulnerability association (Spearman, n = 15 states)
| Indicator vs mean monthly burden | ρ | p |
| :--- | :--- | :--- |
| GDP per capita | 0.51 | 0.05 |
| SECI | 0.28 | 0.31 |
| NITI Health Index | 0.23 | 0.41 |

## S7. Field Scorecard validation
The 0–6 ordinal Field Scorecard (active monsoon; prior month above local median; elevated 2-month-lagged rainfall; seasonal peak window) correlated with the full model's forecast at **Spearman ρ = 0.76 (p < 0.001)** across all 1,740 state-months.

## S8. Sensitivity / data notes
- The NITI Aayog Health Index 2019-20 value for West Bengal was absent in the source CSV and median-imputed. Re-running the pipeline excluding West Bengal changed the headline cross-validated R² by < 0.01 and did not alter the driver hierarchy, confirming the imputation is non-influential.
- Structural covariates are single-year (static) and therefore inform between-state contrasts rather than within-state temporal change.

## S9. Reproducibility
Python 3 with scikit-learn, pandas, NumPy, SciPy, GeoPandas, Matplotlib, seaborn. Pipeline: `src/11_rigorous_pipeline.py` (model + metrics), `src/12_generate_figures.py` (figures), `src/13_build_double_column_docx.py` and `src/14_build_latex_pdf.py` (manuscript). Repository: https://github.com/hssling/Dengue_Outbreak_Prediction
