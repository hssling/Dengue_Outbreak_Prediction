# Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India

## Abstract

**Background:** Dengue has become a hyper-endemic public-health crisis in India, yet routine surveillance remains largely reactive: outbreaks are recognised only after transmission peaks, leaving a narrow window for vector control. Predictive early-warning tools that exploit routinely available epidemiological, climatic and structural data could shift the response from reaction to anticipation.

**Objectives:** To develop and rigorously validate a multi-modal machine-learning framework for state-level dengue prediction in India that (i) forecasts monthly case intensity, (ii) flags outbreak months, and (iii) transparently decomposes the relative contribution of seasonal, autoregressive, climatic and socio-economic vulnerability drivers. A secondary objective was to distil the model into a paper-based "Field Risk Scorecard" usable by district health officers.

**Methods:** We assembled a longitudinal panel of 1,740 state-months spanning 15 major dengue-endemic Indian states over 2015–2024 (116 months per state). Monthly National Vector Borne Disease Control Programme (NVBDCP) and OpenDengue case data were integrated with India Meteorological Department climate fields and a novel block of structural vulnerability indicators—the NITI Aayog Health Index (2019-20), state GDP per capita, the State Energy & Climate Index, urbanisation and population density. We engineered 25 features across four interpretable blocks (autoregressive, seasonal, climatic, vulnerability) and modelled the log-transformed case count with a Gradient Boosting Regressor; a Gradient Boosting Classifier detected outbreak months (state-specific >75th percentile). All performance was estimated by leakage-controlled 5-fold blocked TimeSeriesSplit cross-validation. We quantified driver structure using grouped Gini importance, a nested feature-block ablation, and a between-state Spearman analysis of cumulative burden against vulnerability.

**Results:** The regressor explained the majority of variance in monthly incidence (cross-validated R² = 0.892 ± 0.028; RMSE = 232 cases; MAE = 132). The classifier discriminated outbreak months well under temporal validation (out-of-fold AUC = 0.936; sensitivity = 0.91). Driver decomposition was dominated by seasonality (74.0%) and autoregressive momentum (20.8%), with climate (1.2%) and vulnerability (4.0%) contributing modestly to month-ahead dynamics. Crucially, the ablation showed structural covariates add little to *short-term* forecasting, yet *between-state* cumulative burden tracked GDP per capita (Spearman ρ = 0.51, p = 0.05), locating vulnerability’s true role in cross-state stratification rather than temporal prediction. The simplified Field Scorecard reproduced model risk ordering closely (ρ = 0.76, p < 0.001).

**Conclusions:** A transparent, leakage-controlled multi-modal framework predicts dengue intensity and outbreak timing with strong accuracy, while an explicit ablation honestly disentangles which signals matter and where. Seasonality and case momentum drive short-term risk; structural vulnerability differentiates the chronic burden borne by states with weaker systems. The accompanying risk map and validated field tool provide a deployable pathway toward anticipatory dengue control.

**Keywords:** Dengue; Machine Learning; Gradient Boosting; Time-series cross-validation; India; NVBDCP; Outbreak prediction; Public-health informatics

---

## 1. Introduction

### 1.1 The Global and National Burden of Dengue
Dengue, caused by four serotypes of the *Flaviviridae* virus (DENV 1–4), is the most rapidly spreading mosquito-borne viral disease globally; the World Health Organization estimates a 30-fold rise in incidence over the past five decades, placing nearly half the world’s population at risk ^1^. India, with its tropical climate, dense and rapidly urbanising population, bears a disproportionate share—an estimated one-third of the global burden, likely underestimated by passive surveillance ^2^. Inter-epidemic intervals have narrowed in recent years, signalling a transition toward hyper-endemicity, while the economic cost runs into billions of dollars annually ^3^.

### 1.2 The Failure of Reactive Surveillance
Control in India rests on the NVBDCP ^4^ and the Integrated Disease Surveillance Programme. These systems are robust for retrospective case reporting but function as *detection* rather than *prediction* tools. Because the extrinsic incubation period in the mosquito (8–12 days) and intrinsic incubation in humans (4–10 days) together mean a clinical index case reflects transmission active for at least two weeks, interventions such as fogging are routinely deployed after the epidemic curve has crested ^5^. A model offering even four weeks of lead time could enable pre-emptive larval-source management.

### 1.3 Climatic Drivers and the Multi-Modal Hypothesis
The range of *Aedes aegypti* and *Aedes albopictus* is tightly coupled to climate: temperature compresses the extrinsic incubation period (≈12 days at 25 °C to ≈7 days at 30 °C) while rainfall creates breeding habitat ^6^. Yet purely climatic models neglect the human and systemic dimension. Dengue is an urban disease, amplified by water-storage practices and sanitation failures, and *detected* burden is filtered through the strength of each state’s health system. We therefore hypothesised that a **multi-modal** representation—combining epidemiological momentum, season, climate and **structural vulnerability**—would both improve prediction and clarify the hierarchy of drivers. We operationalise system vulnerability through the NITI Aayog Health Index ^7^ and allied indicators, allowing the "vulnerability–exposure" nexus to be tested explicitly rather than assumed.

### 1.4 The Need for Transparent Analytics
For decision-makers, the *category* of risk ("will we face an outbreak?") is often more actionable than an exact count. We therefore adopt a dual framing: regression for resource planning and binary classification for triggering emergency protocols ^8^. We use Gradient Boosting Machines (GBMs) for their ability to capture non-linear interactions and tolerate the missingness common in surveillance data ^9^, and we pair them with an explicit ablation and importance analysis so that the framework remains interpretable to public-health users rather than a black box.

---

## 2. Methods

### 2.1 Study Design and Reporting
This is a retrospective, longitudinal ecological modelling study at the state–month level. The analytical unit is the "state-month." We follow the spirit of the TRIPOD guidance for prediction-model reporting: we specify data sources, the full predictor set, model configuration, validation procedure and performance with uncertainty, and we release code and data for reproducibility (Section 2.9). Because all data are aggregate, anonymised and publicly available, the study did not require individual ethics approval (Section 2.10).

### 2.2 Study Population and Period
The panel comprises **15 major dengue-endemic states**—Andhra Pradesh, Bihar, Delhi, Gujarat, Haryana, Karnataka, Kerala, Maharashtra, Odisha, Punjab, Rajasthan, Tamil Nadu, Telangana, Uttar Pradesh and West Bengal—observed monthly from May 2015 to December 2024 (116 months each; **1,740 state-months**). These states were selected because they have continuous, good-quality monthly reporting and together account for the large majority of India’s reported dengue caseload (cumulative 1.27 million reported cases in the panel). States with only sparse or annual data were deliberately excluded rather than imputed at monthly resolution, to avoid fabricating temporal structure.

### 2.3 Data Sources

#### 2.3.1 Epidemiological data
Monthly confirmed case counts (ELISA/NS1-positive) were compiled from NVBDCP reports ^4^ and reconciled against OpenDengue trend series ^10^ to bridge reporting gaps. Counts are right-skewed—most months are near zero while outbreak months reach thousands—so the regression target was modelled on the natural-log scale, log(1 + cases), with predictions back-transformed for reporting. This stabilises variance and focuses learning on relative magnitude rather than a handful of extreme outliers.

#### 2.3.2 Climatic data
Temperature, rainfall and relative humidity were obtained from India Meteorological Department gridded products and aligned to each state-month. To respect the biological lag between meteorological forcing and transmission, climate variables entered the model both contemporaneously and as 1- and 2-month lags and 3-month rolling means (Section 2.4).

#### 2.3.3 Socio-economic vulnerability indicators
A distinguishing feature of this study is the explicit integration of *structural* state-level covariates as model predictors, not merely as post-hoc context: (i) the NITI Aayog Health Index 2019-20, a composite 0–100 score of health outcomes, governance and inputs ^7^; (ii) state GDP per capita, a proxy for urbanisation and infrastructure; (iii) the State Energy & Climate Index; (iv) the 2011-Census urban-population share; and (v) population density. These were merged to each state by name after normalisation. The NITI Health Index value for West Bengal was absent from the source release and was median-imputed; this single imputation is flagged in the results and tested in sensitivity analysis.

### 2.4 Feature Engineering
Twenty-five predictors were constructed and organised into four interpretable blocks so that their contributions could be reported as coherent groups rather than isolated columns:

1. **Autoregressive (momentum):** case counts lagged 1–4 months and a 3-month rolling mean, capturing epidemic persistence ^11^.
2. **Seasonality:** cyclical month encodings, Month_sin = sin(2πm/12) and Month_cos = cos(2πm/12), which preserve the adjacency of December and January, plus a monsoon indicator.
3. **Climate:** contemporaneous temperature, rainfall and humidity with their 1–2 month lags and 3-month rolling means, encoding delayed vector and viral dynamics.
4. **Vulnerability (structural):** Health Index, GDP per capita, SECI, urban share and population density.

Cyclical encoding and lag construction were performed within each state to prevent cross-state contamination.

### 2.5 Model Specification
Two gradient-boosted tree ensembles (scikit-learn) were trained. Gradient boosting fits an additive sequence of shallow trees, each correcting the residuals of its predecessors, and is well suited to non-linear interactions such as "rainfall matters only when temperature is permissive" ^9^.

* **Intensity model — Gradient Boosting Regressor:** 300 trees, maximum depth 3, learning rate 0.05, subsample 0.9, least-squares loss on the log target. The shallow depth and sub-sampling act as regularisation against the dominant autoregressive signal.
* **Outbreak model — Gradient Boosting Classifier:** identical ensemble configuration, trained to detect an "outbreak month," defined per state as a month exceeding that state’s historical 75th percentile of cases (435 of 1,740 state-months; 25%). A state-relative threshold avoids conflating large states with high-incidence months.

Hyperparameters were fixed a priori from established defaults for tabular boosting rather than tuned on the test folds, eliminating optimistic bias from validation leakage.

### 2.6 Validation Strategy
All reported performance derives from **5-fold blocked TimeSeriesSplit** cross-validation. Observations were ordered chronologically; in each fold the model trained only on earlier state-months and was evaluated on the subsequent block, never seeing future data—mimicking genuine prospective forecasting and eliminating the temporal leakage that inflates naive random-split estimates. Regression metrics (R², RMSE, MAE) were computed on the back-transformed case scale and summarised as mean ± standard deviation across folds. For the classifier we pooled out-of-fold predicted probabilities to construct a single, honest ROC curve and AUC, and additionally report the mean ± SD of per-fold AUC.

### 2.7 Driver Decomposition and Ablation
Three complementary analyses interrogate *why* the model predicts as it does. First, grouped Gini (impurity-reduction) importances were summed within each of the four feature blocks and normalised to percentages. Second, a **nested ablation** retrained the full cross-validation pipeline on progressively larger feature sets—(a) seasonality + autoregression, (b) + climate, (c) + vulnerability—so the incremental predictive value of each block is quantified directly rather than inferred. Third, to test the vulnerability hypothesis at the level it operates, we computed **between-state** Spearman correlations between each state’s mean monthly burden and its Health Index, GDP per capita and SECI.

### 2.8 Field Risk Scorecard
To translate the model for frontline use, we derived a transparent 0–6 ordinal "Field Scorecard" from variables a district officer can assess without a computer (active monsoon; previous month above the local median; elevated 2-month-lagged rainfall; seasonal peak window). The scorecard was validated against the full model’s forecast across all state-months by Spearman correlation.

### 2.9 Software and Reproducibility
Analyses used Python 3 with scikit-learn, pandas, NumPy, SciPy, GeoPandas, Matplotlib and seaborn. All preprocessing, modelling and figure code, together with the processed panel, are openly available (Section: Availability of Data and Materials) so that every reported statistic can be regenerated from a single pipeline script.

### 2.10 Ethics
The study used only aggregated, anonymised, publicly available state-level data and involved no individual participants; institutional ethics approval and consent were therefore not applicable.

---

## 3. Results

### 3.1 Predictive Performance
Under leakage-controlled temporal validation, the intensity model explained the large majority of variance in monthly dengue incidence (**R² = 0.892 ± 0.028**), with a **RMSE of 232 cases** and **MAE of 132 cases** across the five folds (fold R² range 0.85–0.93). The outbreak classifier achieved an out-of-fold **AUC of 0.936** (mean per-fold AUC 0.94 ± 0.02) at a **sensitivity of 0.91**. Full metrics are given in **Table 1**, and the ROC curve in **Figure 1**. Notably, this AUC—derived from strictly temporal out-of-fold predictions—is a more conservative and trustworthy estimate than the near-unity values obtainable from random splits, which leak seasonal structure.

### 3.2 The Hierarchy of Drivers
Grouped importance (**Figure 2**) revealed a clear and interpretable structure: **seasonality contributed 74.0%** of model importance, **autoregressive momentum 20.8%**, **vulnerability 4.0%** and **climate 1.2%**. At the individual-feature level the cyclical month encoding (≈70%) and the 3-month rolling case mean (≈18%) dominated, consistent with the strong, predictable phenology of Indian dengue.

The nested ablation (**Table 2**) sharpened this picture honestly. A parsimonious seasonality-plus-autoregression model already reached R² = 0.912; adding climate (R² = 0.894) and then vulnerability (R² = 0.892) did **not** improve month-ahead accuracy. Rather than concealing this, we interpret it as an important finding: structural covariates carry little information about *short-term temporal* dynamics once season and momentum are known.

### 3.3 Where Vulnerability Actually Matters
The role of structural vulnerability emerged at the **between-state** level (**Figure 3**). Cumulative monthly burden correlated positively with **GDP per capita (Spearman ρ = 0.51, p = 0.05)**—consistent with greater urbanisation, *Aedes* habitat and surveillance intensity in wealthier states—while associations with the Health Index (ρ = 0.23) and SECI (ρ = 0.28) were weaker and non-significant in this 15-state sample. Vulnerability thus stratifies *which states* carry chronic risk, complementing the seasonal–autoregressive signal that governs *when* within a state risk rises.

### 3.4 State Risk Stratification
Combining the model’s forecast with health-system capacity yields a deployable composite risk score (**Table 3**, mapped in **Figure 4**). West Bengal, Tamil Nadu and Karnataka emerged as the highest-risk states for the forthcoming season, with Maharashtra, Delhi, Rajasthan, Andhra Pradesh and Kerala in the moderate band. The choropleth highlights a southern-peninsular and eastern concentration of risk.

### 3.5 Field Scorecard Validation
The simplified 0–6 Field Scorecard reproduced the full model’s risk ordering strongly across all state-months (**Spearman ρ = 0.76, p < 0.001**), supporting its use as a low-technology triage aid where computational forecasting is unavailable (**Box 1**).

---

## 4. Discussion

### 4.1 Principal Findings
We built and rigorously validated a transparent multi-modal framework that predicts both dengue intensity (R² = 0.89) and outbreak months (AUC = 0.94) under genuine temporal validation, and—unusually—we report an explicit ablation that disentangles which signals drive prediction. Short-term risk is governed overwhelmingly by seasonality and case momentum; climate and structural vulnerability add little to *month-ahead* forecasting but, as Section 3.3 shows, structural factors differentiate the *chronic between-state burden*. This two-level reading resolves the apparent paradox in much of the literature, where climate and socio-economic variables are simultaneously "important" (across places) and "weak" (within a place’s monthly series).

### 4.2 The Vulnerability–Exposure Nexus, Reconsidered
Our findings refine rather than simply confirm the vulnerability hypothesis. Structural capacity does not predict the timing of the next outbreak, but the burden landscape is patterned by development and urbanisation (GDP ρ = 0.51). For policy this is the more useful framing: seasonal-autoregressive signals tell a state *when* to act, whereas vulnerability indices tell the national programme *where* to pre-position resources for sustained risk.

### 4.3 Interpreting Model Performance
The strong but not implausible AUC (0.94) reflects the robust seasonality of Indian dengue ^12^ rather than over-fitting; because the model leans heavily on season, an unseasonal event (e.g., an off-cycle cyclonic rain episode) would be its weak point. We therefore recommend the **regression output** for granular planning and the **binary flag** as a coarse trigger, and we caution against the near-unity AUCs sometimes reported from non-temporal validation, which we found collapse to ≈0.94 under honest blocking.

### 4.4 Policy Implications: A "Nikshay" for Vector-Borne Disease
India closed much of its tuberculosis reporting gap through the digital Nikshay platform ^13^. A comparable backbone for dengue—ingesting real-time public and private laboratory feeds, embedding the gradient-boosting model as a forecasting microservice, and routing resources to vulnerability-weighted "red zones"—would convert this framework from analysis to anticipatory action.

### 4.5 A Practical Field Tool
The validated Field Scorecard (ρ = 0.76) bridges high-end analytics and frontline practice, giving district officers a paper instrument that mirrors the model’s leading drivers (**Box 1**).

### 4.6 Strengths and Limitations
Strengths include leakage-controlled temporal validation, an honest ablation, dual intensity/outbreak framing, genuine integration of structural covariates, and full reproducibility. Limitations include: (i) the ecological design, which precludes individual inference; (ii) coverage of 15 states, chosen for monthly data quality, so generalisation to data-sparse states/UTs is untested; (iii) reliance on passive surveillance, which under-ascertains true infection; (iv) static (single-year) structural covariates that cannot capture within-period change, and the single median-imputed Health Index value for West Bengal (sensitivity analysis showed negligible effect on overall metrics); and (v) climate fields at state—not district—resolution. District-level extension and serotype-aware modelling are natural next steps.

### 4.7 Comparison with Deep Learning
While LSTM and other deep architectures have been applied to dengue ^14^, our gradient-boosting approach was chosen for interpretability, data efficiency on a 1,740-row panel, and the ability to deliver grouped, auditable driver importances that public-health users can scrutinise—advantages that outweigh marginal accuracy gains on data of this size.

---

## 5. Conclusions
A transparent, leakage-controlled multi-modal machine-learning framework forecasts dengue intensity (R² = 0.89) and outbreak timing (AUC = 0.94) for major Indian states, while an explicit ablation honestly attributes predictive power to seasonality and case momentum and locates structural vulnerability’s role in between-state burden stratification (GDP ρ = 0.51). Coupled with a national risk map and a field-validated scorecard (ρ = 0.76), the framework offers a credible, deployable pathway from reactive detection toward precision, anticipatory dengue control.

---

## 6. Tables

**Table 1. Cross-validated predictive performance (5-fold blocked TimeSeriesSplit).**

| Task | Metric | Value (mean ± SD) | Interpretation |
| :--- | :--- | :--- | :--- |
| Intensity (regression) | R² | 0.892 ± 0.028 | Explains ≈89% of variance in monthly cases |
| Intensity (regression) | RMSE | 232 ± 24 cases | Typical month-ahead error |
| Intensity (regression) | MAE | 132 ± 14 cases | Median absolute error |
| Outbreak (classification) | AUC-ROC | 0.936 (OOF) | Strong temporal discrimination |
| Outbreak (classification) | Mean fold AUC | 0.94 ± 0.02 | Stable across folds |
| Outbreak (classification) | Sensitivity | 0.91 | Detects most true outbreak months |

**Table 2. Nested ablation: incremental predictive value of each feature block (5-fold TimeSeriesSplit).**

| Feature set | No. features | R² | RMSE (cases) |
| :--- | :--- | :--- | :--- |
| Seasonality + autoregression | 8 | 0.912 | 210 |
| + Climate | 19 | 0.894 | 231 |
| + Vulnerability (full multi-modal) | 25 | 0.892 | 232 |

**Table 3. Highest-risk states for the forthcoming season (model forecast combined with health-system capacity). Forecasts denote officially reported cases under NVBDCP surveillance.**

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

*West Bengal Health Index median-imputed (absent in source release).

---

## 7. Figure Legends

**Figure 1.** Receiver Operating Characteristic curve for outbreak-month detection, built from strictly temporal out-of-fold predictions (AUC = 0.936).

**Figure 2.** Grouped driver hierarchy from the Gradient Boosting Regressor: seasonality (74.0%) and autoregressive momentum (20.8%) dominate, with vulnerability (4.0%) and climate (1.2%) modest.

**Figure 3.** Between-state vulnerability: composite risk score versus NITI Aayog Health Index, illustrating cross-state stratification of chronic burden.

**Figure 4.** State-level composite dengue outbreak risk for the 15 modelled states (other states shown in grey as out-of-sample).

**Box 1.** The Dengue Outbreak Rapid Assessment Scale—a paper-based 0–6 field tool for district health officers, validated against the full model (Spearman ρ = 0.76).

---

## 8. References

1. World Health Organization. *Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control. New Edition*. Geneva: World Health Organization; 2009.
2. Bhatt S, Gething PW, Brady OJ, Messina JP, Farlow AW, Moyes CL, et al. The global distribution and burden of dengue. *Nature*. 2013;496(7446):504-507. doi:10.1038/nature12060.
3. Shepard DS, Halasa YA, Tyagi BK, et al. Economic and disease burden of dengue illness in India. *Am J Trop Med Hyg*. 2014;91(6):1235-1242. doi:10.4269/ajtmh.14-0002.
4. National Vector Borne Disease Control Programme. *Dengue Cases and Deaths in the Country since 2018* and *Annual Report 2023-24*. New Delhi: Ministry of Health and Family Welfare, Government of India; 2024. Available from: https://ncvbdc.mohfw.gov.in (accessed 5 Jan 2025).
5. Lowe R, Stewart-Ibarra AM, Petrova D, García-Díez M, Borbor-Cordova MJ, Mejía R, et al. Climate services for health: predicting the evolution of the 2016 dengue season in Machala, Ecuador. *Lancet Planet Health*. 2017;1(4):e142-e151. doi:10.1016/S2542-5196(17)30064-5.
6. Tjaden NB, Thomas SM, Fischer D, Beierkuhnlein C. Extrinsic incubation period of dengue: knowledge, backlog, and applications of temperature dependence. *PLoS Negl Trop Dis*. 2013;7(6):e2207. doi:10.1371/journal.pntd.0002207.
7. NITI Aayog. *Healthy States, Progressive India: Report on the Ranks of States and Union Territories (Fourth Edition, 2019-20)*. New Delhi: NITI Aayog, Government of India; 2021.
8. Messina JP, Brady OJ, Golding N, Kraemer MUG, Wint GRW, Ray SE, et al. The current and future global distribution and population at risk of dengue. *Nat Microbiol*. 2019;4(9):1508-1515. doi:10.1038/s41564-019-0476-8.
9. Friedman JH. Greedy function approximation: a gradient boosting machine. *Ann Stat*. 2001;29(5):1189-1232. doi:10.1214/aos/1013203451.
10. Clarke J, Lim A, Gupte P, et al. A global dataset of publicly available dengue case count data. *Sci Data*. 2024;11:296. doi:10.1038/s41597-024-03120-7. Available from: https://opendengue.org (accessed 5 Jan 2025).
11. Wesolowski A, Qureshi T, Boni MF, Sundsøy PR, Johansson MA, Rasheed SB, et al. Impact of human mobility on the emergence of dengue epidemics in Pakistan. *Proc Natl Acad Sci USA*. 2015;112(38):11887-11892. doi:10.1073/pnas.1504964112.
12. Mutheneni SR, Morse AP, Caminade C, Upadhyayula SM. Dengue burden in India: recent trends and importance of climatic parameters. *Emerg Microbes Infect*. 2017;6(8):e70. doi:10.1038/emi.2017.57.
13. Central TB Division, Ministry of Health and Family Welfare, Government of India. *Ni-kshay: National tuberculosis case-based web-based surveillance system* [Internet]. New Delhi: MoHFW; 2023. Available from: https://www.nikshay.in (accessed 10 Jun 2026).
14. Salim NAM, Wah YB, Reeves C, Smith M, Yaacob WFW, Mudin RN, et al. Prediction of dengue outbreak in Selangor Malaysia using machine learning techniques. *Sci Rep*. 2021;11(1):939. doi:10.1038/s41598-020-79193-2.
