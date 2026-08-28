# Structural Determinants Without Short-Term Predictability: A Leakage-Controlled Benchmark of State-Level Dengue Burden in India, 2015–2024

## Abstract

**Background:** Machine-learning early-warning systems for dengue are proliferating, and many report high predictive accuracy. Such claims are fragile: they depend entirely on the provenance of the underlying surveillance data and on whether the evaluation design excludes information that would not be available at the moment a forecast is issued. India, which carries a large share of the global dengue burden, has been a frequent subject of these models, yet no continuous monthly state-level case series is publicly available for the country.

**Objectives:** To (i) assemble and independently verify an authentic state-level dengue panel for India; (ii) establish, under a strictly leakage-free design, how much genuine one-year-ahead predictive skill is attainable and whether machine learning improves on elementary baselines; (iii) quantify how far two common design defects — an unshifted rolling target statistic and non-temporal validation — inflate apparent performance; and (iv) test whether structural vulnerability indicators explain the between-state burden landscape.

**Methods:** We compiled every observed annual state-level dengue total released by India's National Centre for Vector Borne Diseases Control (NCVBDC) and archived by OpenDengue for 2015–2024. Only states with an observed value in all ten years were retained; nothing was interpolated, imputed or reconstructed from higher-level totals. The resulting panel of **350 state-years across 35 states and union territories** was cross-checked against the independent NCVBDC bulletin. Structural covariates comprised the NITI Aayog Health Index (2019-20), state GDP per capita, the State Energy & Climate Index, Census 2011 urban share and population density. Forecasts of year *t* used only information observable to 31 December *t*−1. Seven models — persistence, state climatology, a global annual mean, negative-binomial GLMs and gradient-boosting ensembles — were compared on identical expanding-window splits (origins 2018–2024; 245 out-of-sample forecasts). We report pooled and within-state (state-mean-removed) R², out-of-fold permutation importance, and, for outbreak-year classification, AUC-ROC, precision–recall, Brier score and calibration with thresholds derived inside each training window.

**Results:** All 124 overlapping state-years reconciled **exactly** with the NCVBDC bulletin (100% agreement). No machine-learning model outperformed elementary baselines: state climatology achieved the highest pooled R² (**0.637**), ahead of a negative-binomial GLM (0.607), gradient boosting (0.551) and persistence (0.550). Critically, **within-state R² was approximately zero or negative for every model** (best −0.002; gradient boosting −0.239), showing that pooled skill reflects only the recovery of stable between-state differences in burden, not anticipation of temporal change. Outbreak-year classification was uninformative (AUC 0.522; average precision 0.468 against a prevalence of 0.452; Brier 0.326, worse than the non-informative baseline of 0.248). Reintroducing an unshifted three-year rolling mean raised apparent R² from 0.551 to **0.759**, and non-temporal random-split validation raised it to 0.626. By contrast, the between-state structural gradient was strong and robust: mean annual incidence rose with urbanisation (Spearman ρ = **0.635**, 95% CI 0.33–0.82, p < 0.001) and GDP per capita (ρ = **0.609**, 95% CI 0.32–0.80, p < 0.001), the latter persisting after adjustment for a surveillance-capacity proxy (partial ρ = 0.663, p < 0.001). The NITI Health Index showed no association (ρ = 0.159, p = 0.38).

**Conclusions:** On authenticated Indian surveillance data, state-level dengue burden one year ahead is **not** predictable beyond a state's own historical average, and outbreak-year classification performs at chance. Reported accuracies substantially above this level should be treated as evidence of design leakage rather than of epidemiological signal. Where dengue in India *is* systematically patterned is spatially: burden concentrates in more urbanised and more economically developed states. Surveillance investment and vector control should therefore be allocated on structural and demographic grounds rather than on the promise of short-horizon algorithmic forecasting at this spatial and temporal resolution.

**Keywords:** Dengue; India; Data leakage; Forecast evaluation; Benchmarking; Negative results; Surveillance data provenance; Public-health informatics

---

## 1. Introduction

### 1.1 The Global and National Burden of Dengue
Dengue, caused by four serotypes of the *Flaviviridae* virus (DENV 1–4), is the most rapidly spreading mosquito-borne viral disease globally; the World Health Organization estimates a 30-fold rise in incidence over the past five decades, placing nearly half the world's population at risk ^1^. India, with its tropical climate and dense, rapidly urbanising population, bears a disproportionate share — an estimated one-third of the global burden, likely underestimated by passive surveillance ^2^. Inter-epidemic intervals have narrowed in recent years, while the economic cost runs into billions of dollars annually ^3^.

### 1.2 Prediction Claims and Their Dependence on Design
Control in India rests on the NCVBDC ^4^ and the Integrated Disease Surveillance Programme, systems designed for retrospective case reporting rather than prediction. This gap has motivated a large modelling literature, from climate-driven seasonal forecasting services ^5^ to machine-learning outbreak classifiers, much of it reporting high accuracy — coefficients of determination above 0.85 and near-unity outbreak AUCs are common ^6^.

Two considerations should temper the reading of such results. The first is **provenance**. A predictive claim about India presupposes a case series at the claimed spatial and temporal resolution. NCVBDC publishes state-wise totals annually; OpenDengue, the principal open archive of global dengue counts ^7^, contains for India only annual admin-1 records together with a single year of national monthly values. Where monthly state-level series appear in the literature, they are frequently reconstructed by distributing annual totals across months using an assumed seasonal profile. Any model trained on such a series will recover that assumed profile, and the resulting "seasonality is the dominant driver" finding is an artefact of the reconstruction rather than a discovery about transmission.

The second is **temporal validity**. A forecast is only a forecast if every predictor was observable before the target period began. Rolling statistics computed without first lagging the outcome series embed the target inside the predictor matrix; outbreak thresholds estimated on the whole study period leak future information into the definition of the label; and random-split cross-validation abolishes the temporal ordering that makes the task difficult. Each defect inflates apparent performance without improving prospective utility, and leakage of exactly these kinds has been identified as a leading cause of irreproducible findings across machine-learning-based science ^8^.

### 1.3 The Structural Vulnerability Hypothesis
Beyond climate and epidemic momentum, dengue is shaped by the human and systemic environment: it is an urban disease, amplified by water-storage practices and sanitation failures, and *detected* burden is filtered through the strength of each state's health system. We therefore examine whether structural indicators — the NITI Aayog Health Index ^9^, GDP per capita, the State Energy & Climate Index, urbanisation and population density — explain the burden landscape. We stress at the outset that reported cases are not a direct measure of health-system weakness: stronger systems may record *more* cases through better diagnosis and surveillance, while weaker systems may under-report a greater true burden. This design can identify predictive and between-state associations; it cannot establish a causal vulnerability–exposure mechanism.

### 1.4 Objectives
We set out to establish what an authenticated Indian dengue panel actually supports. Our hypothesis — that combining epidemiological history with structural indicators would improve prediction — is stated here as the hypothesis the study tested. As Section 3 reports, it was **not** supported, and we present that outcome rather than a favourable reformulation of it. Alongside the negative forecasting result we report a formal leakage experiment that quantifies how large the corresponding optimistic bias would have been, and a between-state analysis that locates where systematic structure in Indian dengue does exist.

---

## 2. Methods

### 2.1 Study Design and Reporting
This is a retrospective, longitudinal ecological modelling study at the state–year level; the analytical unit is the "state-year." Reporting follows TRIPOD+AI ^10^: we specify data sources and their provenance, the full predictor set, model configuration, the forecast origin, validation procedure, discrimination *and* calibration with uncertainty, and we release code and data (Section 2.9). Because all data are aggregate, anonymised and publicly available, individual ethics approval was not required (Section 2.10).

### 2.2 Data Provenance
Case data are the observed annual state-level dengue totals reported by NCVBDC ^4^ and archived in the OpenDengue Spatial extract V1.3 ^7^. We retained records with `adm_0_name = INDIA`, `S_res = Admin1`, `T_res = Year` and a `MOH-IND` source identifier, giving 358 state-year records for 2015–2024 across 41 administrative labels. State names were harmonised to a canonical list (for example ORISSA → ODISHA, PONDICHERRY → PUDUCHERRY). Where a state-year appeared under more than one ministry release, the revised return superseded the provisional one; no duplicate was summed.

We deliberately did **not** attempt to construct a monthly series. No continuous monthly admin-1 dengue series exists in the public domain for India: OpenDengue holds only 12 monthly records for the country, all national and all from 2024. Annual data are therefore the finest resolution at which an authentic Indian state-level panel can be assembled, and the study is specified at that resolution.

### 2.3 Eligibility and Exclusions
A state or union territory was eligible only if an observed NCVBDC total was present for **every** one of the ten study years. No missing year was imputed, interpolated or carried forward. Thirty-five of 36 candidate states and union territories met this criterion, yielding **350 state-years**. One state, West Bengal, was excluded for two missing years. Six state-years carry genuine zero counts; these are true reported zeros in small union territories and were retained as observed. Panel construction, the eligibility rule and the full exclusion record are tabulated in **Supplementary Table S1**. Because eligibility is defined solely by completeness of the annual return, the surveillance-related selection pressure is far weaker than in designs that require continuous monthly reporting, but it is not absent, and we address it in Section 4.5.

### 2.4 Independent Reconciliation
To verify that the panel reproduces the official record rather than a derived approximation, we cross-checked it against the NCVBDC state-wise annual bulletin, which overlaps the panel for 2021–2024. All **124 of 124** overlapping state-years matched exactly (100%; median absolute difference 0.0%). The full reconciliation table is provided as **Supplementary Table S2** and plotted in **Figure 1B**.

### 2.5 Structural Covariates
Five time-invariant state-level indicators were merged by harmonised name: the NITI Aayog Health Index 2019-20, a composite 0–100 score of health outcomes, governance and inputs ^9^; state GDP per capita; the NITI State Energy & Climate Index (round 1); the Census 2011 urban population share; and Census 2011 population density. Population was additionally used as a log offset in count models. Coverage gaps were confined to three small union territories (Daman & Diu, Dadra & Nagar Haveli, Lakshadweep); these were median-imputed **and flagged**, and every between-state association in Section 3.4 is computed on states with observed covariates only (n = 32). No climate covariates were included: state-resolution meteorological fields matching the full 2015–2024 window were not available to us at annual resolution, and we prefer to omit a block outright rather than reconstruct it. Annual aggregation would in any case obscure the sub-seasonal temperature dependence through which climate acts on transmission, the extrinsic incubation period shortening from roughly 12 days at 25 °C to 7 days at 30 °C ^11^. This is stated as a limitation in Section 4.5.

### 2.6 Forecast Origin and Feature Construction
The forecasting task is explicit: **using only information observable up to 31 December of year *t*−1, predict the reported dengue case total of year *t***. Predictors comprise cases in years *t*−1 and *t*−2 (log-transformed), the year-on-year log growth rate between them, and the expanding mean and maximum of all prior years — each formed by lagging the outcome series *before* any rolling or expanding statistic is computed — together with the five structural covariates and log population. Counts are right-skewed, so models were fitted on the log(1 + cases) scale and predictions back-transformed where case-scale errors are reported. Because two lags are required, the first modelled target year is 2017 and forecast origins run from 2018 to 2024, giving 245 out-of-sample state-year forecasts.

### 2.7 Benchmarks, Validation and Metrics
All models were evaluated on **identical expanding-window splits**: for each target year, training used every eligible state-year strictly before it. We compared seven specifications:

1. **Persistence** — the previous year's count.
2. **State climatology** — the state's mean count over the training window only.
3. **Global annual mean** — a single national constant.
4. **Negative-binomial GLM (history)** — log-lagged counts with a log-population offset.
5. **Negative-binomial GLM (full)** — as above plus structural covariates.
6. **Gradient boosting (history only)** ^12^ — 300 trees, depth 2, learning rate 0.05, subsample 0.9.
7. **Gradient boosting (multi-modal)** — identical configuration on history plus structural covariates.

Hyperparameters were fixed a priori rather than tuned against the evaluation folds. We report pooled R² on the log scale, MAE and RMSE on the case scale, and mean per-origin R².

Because pooling states with very different baseline burdens can inflate R² through recovery of state means alone, we additionally report a **within-state R²**, computed after subtracting each state's training-window mean from both observed and predicted values. This isolates the component of skill that concerns temporal change, and the state climatology baseline provides the explicit "state mean only" comparator. Performance disaggregated by state is reported in **Supplementary Table S3**, and the complete metric set for every specification in **Supplementary Table S4**.

### 2.8 Outbreak-Year Classification
An "outbreak year" is a state-year exceeding that state's 75th percentile of reported cases. Critically, this threshold was recomputed **inside each training window** rather than over the full panel, so the label definition never uses future data. The decision cut-off applied to the test year was likewise chosen by maximising Youden's J on the *training* predictions only. We report AUC-ROC, average precision against the observed prevalence, the Brier score against a non-informative baseline, a quintile calibration curve, and sensitivity, specificity and PPV at the training-derived cut-off. Reporting discrimination alongside calibration and a prevalence-referenced precision measure, rather than AUC-ROC alone, follows current guidance on evaluation metrics for medical applications of artificial intelligence ^13^.

### 2.9 Interpretability
Impurity-based ("Gini") importance is biased when predictors are correlated and does not indicate the direction of an effect. We therefore report **out-of-fold permutation importance**: for each forecast origin, each predictor in the held-out year is permuted 30 times and the resulting increase in out-of-sample MAE recorded. Values are averaged across origins and aggregated into two blocks — epidemiological history and structural vulnerability. These are predictive importances, not causal contributions.

### 2.10 Between-State Associations
State-level associations were estimated by Spearman correlation between each structural covariate and each of three outcomes — mean annual incidence per 100 000, mean annual cases and cumulative cases — with 95% confidence intervals from 4 000 bootstrap resamples. Incidence is the primary outcome because raw counts largely track population size. To address the concern that wealthier states may report more cases simply because they detect more, we additionally computed the partial Spearman correlation between GDP per capita and incidence adjusting for the NITI Health Index as a proxy for detection and reporting capacity.

### 2.11 Leakage Experiment
To quantify the optimistic bias produced by common design defects, we re-ran the identical pipeline on the identical real data under three additional specifications: (a) adding a three-year rolling mean computed **without** lagging the outcome, so that it contains the target year; (b) replacing temporal splits with five-fold random-split cross-validation; and (c) defining outbreak thresholds on the full panel rather than the expanding training window. Differences from the primary specification measure the inflation attributable to each defect. The specification of each variant is set out in **Supplementary Table S5**.

### 2.12 Software and Reproducibility
Analyses used Python 3 with scikit-learn, pandas, NumPy, SciPy, statsmodels, GeoPandas and Matplotlib. The panel builder (`src/20_build_real_panel.py`), analysis pipeline (`src/21_real_analysis.py`) and figure generator (`src/22_real_figures.py`) regenerate every number and figure reported here from the archived source files in a single pass.

### 2.13 Ethics
The study used only aggregated, anonymised, publicly available state-level data and involved no individual participants; institutional ethics approval and consent were not applicable.

---

## 3. Results

### 3.1 An Authenticated Panel
The analysis panel comprises **350 state-years across 35 states and union territories, 2015–2024**. Reported national totals rise from 91 397 cases in 2015 to a peak of 258 552 in 2023, interrupted by a pronounced fall to 39 419 in 2020 (**Figure 1A**) — consistent with the documented collapse in dengue case detection across the South-East Asia region during the COVID-19 pandemic ^14^, a disruption that any authentic Indian surveillance series must display. All 124 state-years overlapping the independent NCVBDC bulletin matched exactly (**Figure 1B**), confirming that the panel reproduces the official record.

### 3.2 No Model Outperforms Elementary Baselines
Across 245 out-of-sample forecasts, **no machine-learning specification beat the simplest baselines** (**Table 1**, **Figure 2**). State climatology — a state's own training-window mean, carrying no information about the year being forecast — achieved the highest pooled R² (0.637) and the lowest case-scale MAE (2 830 cases). The negative-binomial GLM with structural covariates followed (R² = 0.607), then gradient boosting (0.551), essentially tied with persistence (0.550). Adding structural covariates to gradient boosting improved it (0.488 → 0.551) but only to the level of repeating last year's count.

### 3.3 Pooled Skill Is Entirely Between-State
The within-state analysis explains why. Once each state's mean is removed, **every model has an R² at or below zero** (**Table 1**, light bars in **Figure 2**): state climatology −0.002, the negative-binomial GLM −0.084, gradient boosting −0.239. In other words, the apparently respectable pooled R² of 0.55–0.64 reflects nothing more than the models learning that Kerala reports more dengue than Nagaland. None anticipates whether a given state's burden will rise or fall next year. This is precisely the spatial confounding that pooled evaluation conceals.

Outbreak-year classification tells the same story (**Table 2**, **Figure 3**). Discrimination was at chance (AUC 0.522); average precision (0.468) barely exceeded the 0.452 prevalence; the Brier score (0.326) was **worse** than the non-informative baseline (0.248); and the calibration curve is flat, with observed outbreak frequency near 0.45 across every predicted-probability quintile. At the training-derived cut-off, sensitivity was 0.232 and PPV 0.468 — indistinguishable from guessing at prevalence.

Out-of-fold permutation importance (**Figure 4**) attributes 78.9% of predictive contribution to epidemiological history and 21.1% to structural covariates, the largest single contributions coming from the previous year's count (+0.278 MAE when permuted) and the expanding prior mean (+0.249). Both are summaries of a state's own level, consistent with Section 3.3: the models are recovering state identity, not dynamics.

### 3.4 Where the Structure Is: Between-State Burden
In contrast to the null forecasting results, the between-state analysis showed a strong and statistically robust gradient (**Figure 5**, **Table 3**). Mean annual incidence per 100 000 increased with **urban population share** (ρ = 0.635, 95% CI 0.33–0.82, p < 0.001) and **GDP per capita** (ρ = 0.609, 95% CI 0.32–0.80, p < 0.001); the State Energy & Climate Index was borderline (ρ = 0.349, p = 0.050). The **NITI Aayog Health Index showed no association** with incidence (ρ = 0.159, 95% CI −0.20 to 0.48, p = 0.38), and population density none at all (ρ = −0.004, p = 0.98).

The GDP association is the one most vulnerable to the objection that wealthier states simply detect more cases. Adjusting for the Health Index as a proxy for detection and reporting capacity did not attenuate it (partial ρ = 0.663, p < 0.001). This weakens, but cannot eliminate, the surveillance-intensity explanation, since the Health Index is an imperfect proxy for dengue-specific diagnostic capacity (Section 4.5).

When raw counts rather than incidence are used, the ordering changes as expected: population density (ρ = 0.558, p < 0.001) and SECI (ρ = 0.429, p = 0.014) lead, while GDP falls to ρ = 0.056. This confirms that count-scale associations are dominated by population size and that incidence is the appropriate between-state outcome. The resulting burden landscape is mapped descriptively in **Figure 6**; because the forecasting models carry no demonstrable skill, this map reports observed incidence only and is not a forecast.

### 3.5 How Much Do Design Defects Inflate Performance?
The leakage experiment quantifies the cost of the two defects most common in this literature (**Table 4**, **Figure 7**). Against the leakage-free benchmark of R² = 0.551:

* Adding a **three-year rolling mean computed without lagging the outcome** — so that the predictor contains the target year — raised apparent R² to **0.759**, an inflation of **+0.209**.
* Replacing temporal splits with **random-split cross-validation** raised it to **0.626**, an inflation of **+0.075**.
* Defining outbreak thresholds on the **full panel** rather than the expanding window raised AUC from 0.522 to 0.544.

These are conservative estimates: the defects were introduced one at a time on annual data. At monthly resolution, where autocorrelation is far stronger and a rolling window overlaps the target far more heavily, the same defects would compound substantially.

---

## 4. Discussion

### 4.1 Principal Findings
On an authenticated, independently reconciled panel of Indian dengue surveillance, **one-year-ahead state-level burden is not predictable beyond a state's own historical mean**, and outbreak-year classification performs at chance with worse-than-baseline calibration. Neither gradient boosting nor a negative-binomial GLM, with or without structural covariates, improved on state climatology. The within-state analysis shows why headline R² values in this literature can mislead: pooled skill is dominated by recovery of stable between-state differences, and reporting it without the within-state decomposition conveys an impression of anticipatory capability that the model does not possess.

Where Indian dengue *is* systematically structured is spatially. Burden concentrates in more urbanised and more economically developed states, a gradient that is strong, precisely estimated and robust to adjustment for a surveillance-capacity proxy — while the composite health-system index, often invoked as a vulnerability measure, shows no association with incidence at all.

### 4.2 Reconciling the Two Results
These findings are complementary rather than contradictory. Structural indicators describe a slowly varying spatial equilibrium: they explain *where* dengue is endemic and at what level, but by construction they are almost constant over a decade and cannot explain *when* a state departs from its own average. Epidemiological history, meanwhile, encodes a state's level but carries little information about year-to-year departures at annual resolution. The result is a panel in which the level is highly explicable and the deviation is essentially not.

This has a direct programmatic reading. Deciding *where* to pre-position vector-control capacity, diagnostic supply and entomological surveillance is a structural question, and the observed urbanisation and development gradient is a defensible basis for it. Deciding *when* to trigger an emergency response is a question this data resolution cannot answer, and an annual state-level model should not be used for it.

### 4.3 Implications for the Dengue Prediction Literature
Our leakage experiment shows that an unshifted rolling statistic alone can move R² from 0.55 to 0.76 on the very same data. A reader encountering the latter without the former has no way to distinguish epidemiological signal from design artefact. We therefore suggest three practices as minimum standards for this literature: state the forecast origin explicitly and demonstrate that every predictor was observable before it; report within-state as well as pooled skill whenever data are pooled across spatial units with differing baselines; and benchmark against persistence and climatology, since a model that cannot beat a state mean has not been shown to forecast anything. We add a fourth on provenance: where a monthly series is used for a country whose surveillance system publishes annually, the derivation should be documented in full, because a model trained on an assumed seasonal profile will recover that profile and report it as a finding.

### 4.4 Relation to Prior Work
Studies reporting high accuracy for dengue prediction in India and elsewhere ^15,6^ typically differ from ours in resolution, in evaluation design, or in both. We do not claim these studies are wrong; we claim that at the finest spatial and temporal resolution at which an *authenticated* Indian panel can be constructed, the skill is absent, and that the difference between our result and theirs is more plausibly explained by design and data provenance than by modelling technique. The structural gradient we report is consistent with the established understanding of dengue as an urban disease of dense, well-connected, economically active settlements ^16^.

### 4.5 Strengths and Limitations
Strengths are the authenticated and independently reconciled data source, the explicit forecast origin, the benchmark suite, the within-state decomposition, calibration reporting alongside discrimination, out-of-fold permutation importance in place of impurity importance, and a formal quantification of leakage-induced bias.

Limitations are substantial and we state them plainly.

1. **Temporal resolution.** Annual data cannot capture the within-year dynamics on which operational early warning depends. Our negative forecasting result applies to the annual state-level horizon and should **not** be read as evidence that dengue is unpredictable at finer resolutions, where genuine monthly district data exist.
2. **Series length.** Ten years yield seven forecast origins and a small training set at the earliest origins; power to detect modest predictive skill is correspondingly limited. A wider confidence bound around the null is appropriate.
3. **No climate block.** State-resolution meteorological fields covering the full window were unavailable to us, so a climate block was omitted rather than reconstructed. Its incremental value at annual resolution is untested here.
4. **Passive surveillance.** Reported cases under-ascertain true infection, and ascertainment plausibly varies with the very structural covariates under study. The Health-Index adjustment mitigates but cannot resolve this; the between-state gradient may partly reflect detection intensity, and the causal language of "vulnerability" is deliberately avoided.
5. **Ecological design.** No individual-level inference is possible, and time-invariant covariates cannot capture within-period change.
6. **Selection.** Requiring ten complete annual returns excludes one state and may modestly favour better-reporting jurisdictions.

### 4.6 Correction of the Previously Submitted Analysis
In the interest of full transparency, we record that the analysis in the originally submitted version of this manuscript was performed on a **synthetic development dataset** generated by a data-simulation routine retained in the project repository, not on observed surveillance data, and that its feature matrix contained an unshifted rolling case statistic. We confirmed this by regenerating the simulation and matching it to the analysis file record by record; the full audit is set out in **Supplementary Table S6**. The reported R² of 0.892 and AUC of 0.936 are therefore artefacts of simulated data combined with target leakage and are formally withdrawn; the previously reported 74% "seasonality contribution" reflected a seasonal multiplier hard-coded in the simulation routine. The present manuscript replaces that analysis in its entirety with the authenticated panel and leakage-free design described above. We are grateful to both reviewers, whose diagnosis of the provenance and leakage problems was correct in every particular and directly prompted this reanalysis.

---

## 5. Conclusions
Using the finest-resolution authenticated dengue panel that India's public surveillance record supports — 350 state-years across 35 states and union territories, every overlapping value reconciled exactly against the official bulletin — we find no evidence that state-level dengue burden can be forecast one year ahead beyond a state's own historical average, and no evidence that outbreak years can be classified better than chance. Apparent performance well above this level is readily produced by an unshifted rolling statistic or non-temporal validation, and we quantify both. What the data do support is a strong spatial gradient: dengue incidence in India rises with urbanisation and economic development, independent of a health-system capacity proxy. The practical implication is to direct dengue surveillance and vector-control investment structurally and spatially, and to defer operational early-warning claims until monthly, district-resolution data of verified provenance are available to test them.

---

## 6. Tables

**Table 1. One-year-ahead forecasting performance, expanding-window evaluation (origins 2018–2024; 245 out-of-sample state-year forecasts).** Pooled R² is computed across all forecasts; within-state R² is computed after removing each state's training-window mean from both observed and predicted values, isolating skill at anticipating temporal change.

| Model | Pooled R² (log scale) | Within-state R² | MAE (log scale) | MAE (cases) | RMSE (cases) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| State climatology (training mean) | **0.637** | −0.002 | 0.989 | 2 830 | 5 092 |
| Negative-binomial GLM (full) | 0.607 | −0.084 | 1.055 | 3 110 | 5 721 |
| Gradient boosting (multi-modal) | 0.551 | −0.239 | 1.149 | 3 052 | 5 485 |
| Persistence (previous year) | 0.550 | −0.241 | 1.109 | 3 081 | 5 531 |
| Gradient boosting (history only) | 0.488 | −0.413 | 1.223 | 3 223 | 5 838 |
| Negative-binomial GLM (history) | 0.292 | −0.953 | 1.498 | 8 525 | 16 499 |
| Global annual mean | −0.306 | −2.601 | 1.934 | 4 535 | 6 417 |

**Table 2. Outbreak-year classification, expanding-window thresholds and training-derived decision cut-off (210 state-years; 95 outbreak years).**

| Metric | Value | Non-informative reference |
| :--- | :--- | :--- |
| AUC-ROC | 0.522 | 0.500 |
| Average precision | 0.468 | 0.452 (prevalence) |
| Brier score | 0.326 | 0.248 |
| Sensitivity | 0.232 | — |
| Specificity | 0.783 | — |
| Positive predictive value | 0.468 | 0.452 (prevalence) |

**Table 3. Between-state associations with mean annual dengue incidence per 100 000, 2015–2024 (n = 32 states/UTs with observed covariates; Spearman ρ with bootstrap 95% CI).**

| Structural indicator | ρ | 95% CI | p |
| :--- | :--- | :--- | :--- |
| Urban population share (2011) | **0.635** | 0.33 to 0.82 | < 0.001 |
| GDP per capita | **0.609** | 0.32 to 0.80 | < 0.001 |
| State Energy & Climate Index | 0.349 | −0.03 to 0.68 | 0.050 |
| NITI Aayog Health Index (2019-20) | 0.159 | −0.20 to 0.48 | 0.383 |
| Population density (2011) | −0.004 | −0.45 to 0.41 | 0.983 |
| GDP per capita, adjusted for Health Index | 0.663 | — | < 0.001 |

**Table 4. Leakage experiment: apparent performance under the primary design and under two common design defects, on identical data.**

| Specification | R² (log scale) | Inflation vs. leakage-free |
| :--- | :--- | :--- |
| Leakage-free year-ahead (primary) | 0.551 | — |
| Non-temporal random-split cross-validation | 0.626 | +0.075 |
| Unshifted 3-year rolling mean (target leakage) | 0.759 | +0.209 |
| **Outbreak AUC**, expanding-window threshold | 0.522 | — |
| **Outbreak AUC**, full-panel threshold (look-ahead) | 0.544 | +0.022 |

---

## 7. Figure Legends

**Figure 1.** Panel provenance. **(A)** Observed annual reported dengue cases summed across the 35 states and union territories in the analysis panel, 2015–2024, showing the pronounced COVID-19 reporting disruption in 2020. **(B)** Independent reconciliation of the analysis panel against the NCVBDC state-wise annual bulletin for the 124 overlapping state-years; all values fall exactly on the identity line (100% agreement).

**Figure 2.** One-year-ahead forecasting skill across 245 out-of-sample state-year forecasts. Dark bars show pooled R²; light bars show within-state R² after removing each state's training-window mean. No model exceeds state climatology, and every within-state R² is at or below zero.

**Figure 3.** Outbreak-year classification. **(A)** ROC curve (AUC = 0.522). **(B)** Precision–recall curve against the observed prevalence of 0.452. **(C)** Quintile calibration curve; observed outbreak frequency is flat across predicted-probability quintiles and the Brier score (0.326) exceeds the non-informative baseline (0.248).

**Figure 4.** Out-of-fold permutation importance. **(A)** Increase in out-of-sample MAE when each predictor is permuted in the held-out year, averaged across forecast origins. **(B)** The same importances aggregated into epidemiological-history and structural-vulnerability blocks.

**Figure 5.** Between-state structural gradient in observed mean annual dengue incidence per 100 000 (log scale), 2015–2024, against **(A)** urban population share, **(B)** GDP per capita and **(C)** the NITI Aayog Health Index, with Spearman ρ, bootstrap 95% CI and p-value.

**Figure 6.** Descriptive choropleth of observed mean annual dengue incidence per 100 000 across the 35 panel states and union territories, 2015–2024. States not meeting the completeness criterion are hatched. This map is descriptive of observed burden and is **not** a forecast.

**Figure 7.** Leakage experiment on identical real data. **(A)** Apparent regression R² under the leakage-free design, under non-temporal random-split cross-validation, and after reintroducing an unshifted three-year rolling mean. **(B)** Outbreak-year AUC under expanding-window versus full-panel (look-ahead) outbreak thresholds.

---

## 8. References


1. World Health Organization. *Dengue and Severe Dengue* [Fact sheet]. Geneva: World Health Organization; 2024. Available from: https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue (accessed 20 Aug 2026).

2. Bhatt S, Gething PW, Brady OJ, Messina JP, Farlow AW, Moyes CL, et al. The global distribution and burden of dengue. *Nature*. 2013;496(7446):504-507. doi:10.1038/nature12060.

3. Shepard DS, Halasa YA, Tyagi BK, et al. Economic and disease burden of dengue illness in India. *Am J Trop Med Hyg*. 2014;91(6):1235-1242. doi:10.4269/ajtmh.14-0002.

4. National Centre for Vector Borne Diseases Control. *Dengue Cases and Deaths in the Country since 2015*. New Delhi: Ministry of Health and Family Welfare, Government of India; 2025. Available from: https://ncvbdc.mohfw.gov.in (accessed 20 Aug 2026).

5. Lowe R, Stewart-Ibarra AM, Petrova D, García-Díez M, Borbor-Cordova MJ, Mejía R, et al. Climate services for health: predicting the evolution of the 2016 dengue season in Machala, Ecuador. *Lancet Planet Health*. 2017;1(4):e142-e151. doi:10.1016/S2542-5196(17)30064-5.

6. Salim NAM, Wah YB, Reeves C, Smith M, Yaacob WFW, Mudin RN, et al. Prediction of dengue outbreak in Selangor Malaysia using machine learning techniques. *Sci Rep*. 2021;11(1):939. doi:10.1038/s41598-020-79193-2.

7. Clarke J, Lim A, Gupte P, et al. A global dataset of publicly available dengue case count data. *Sci Data*. 2024;11:296. doi:10.1038/s41597-024-03120-7. Available from: https://opendengue.org (accessed 20 Aug 2026).

8. Kapoor S, Narayanan A. Leakage and the reproducibility crisis in machine-learning-based science. *Patterns*. 2023;4(9):100804. doi:10.1016/j.patter.2023.100804.

9. NITI Aayog. *Healthy States, Progressive India: Report on the Ranks of States and Union Territories (Fourth Edition, 2019-20)*. New Delhi: NITI Aayog, Government of India; 2021.

10. Collins GS, Moons KGM, Dhiman P, Riley RD, Beam AL, Van Calster B, et al. TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ*. 2024;385:e078378. doi:10.1136/bmj-2023-078378.

11. Tjaden NB, Thomas SM, Fischer D, Beierkuhnlein C. Extrinsic incubation period of dengue: knowledge, backlog, and applications of temperature dependence. *PLoS Negl Trop Dis*. 2013;7(6):e2207. doi:10.1371/journal.pntd.0002207.

12. Friedman JH. Greedy function approximation: a gradient boosting machine. *Ann Stat*. 2001;29(5):1189-1232. doi:10.1214/aos/1013203451.

13. Hicks SA, Strümke I, Thambawita V, Hammou M, Riegler MA, Halvorsen P, et al. On evaluation metrics for medical applications of artificial intelligence. *Sci Rep*. 2022;12:5979. doi:10.1038/s41598-022-09954-8.

14. Downey LE, Gadsden T, Del Rio Vilas V, Peiris D, Jan S. The impact of COVID-19 on essential health service provision for endemic infectious diseases in the South-East Asia region: a systematic review. *Lancet Reg Health Southeast Asia*. 2022;1:100011. doi:10.1016/j.lansea.2022.100011.

15. Mutheneni SR, Morse AP, Caminade C, Upadhyayula SM. Dengue burden in India: recent trends and importance of climatic parameters. *Emerg Microbes Infect*. 2017;6(8):e70. doi:10.1038/emi.2017.57.

16. Messina JP, Brady OJ, Golding N, Kraemer MUG, Wint GRW, Ray SE, et al. The current and future global distribution and population at risk of dengue. *Nat Microbiol*. 2019;4(9):1508-1515. doi:10.1038/s41564-019-0476-8.
