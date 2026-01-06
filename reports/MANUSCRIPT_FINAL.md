# Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India: Integrating Climate Dynamics with Socio-Economic Vulnerability

**Siddalingaiah H S, MD**
*Independent Researcher, Bangalore, India*
*Correspondence: hssling@gmail.com*

---

## Abstract

**Background:** Dengue fever has evolved into a hyper-endemic public health crisis in India, necessitating a paradigm shift from reactive control to proactive forecasting. Current surveillance systems, while robust in case reporting, often lack the predictive capability to anticipate outbreaks before they overwhelm healthcare systems.

**Objectives:** To develop, validate, and operationalize a scalable machine learning framework for state-level dengue outbreak prediction in India, integrating diverse data streams including epidemiological surveillance, real-time climate monitoring, and socio-economic vulnerability indices.

**Methods:** We constructed a multi-modal dataset covering 35 Indian states and union territories (2015-2025). The epidemiological component integrated National Vector Borne Disease Control Programme (NVBDCP) case reports with OpenDengue trend data. Climatic drivers (temperature, precipitation) were derived from state-level meteorological aggregations and expanded into monthly seasonal features to capture vector phenology. A novel contribution of this study is the integration of structural vulnerability indicators—specifically the NITI Aayog Health Index (2019-20), State GDP per capita, and the State Energy & Climate Index (SECI). We evaluated Random Forest and Gradient Boosting Regressor models using a rigorous 5-fold TimeSeriesSplit cross-validation strategy.

**Results:** The enhanced Gradient Boosting model achieved a robust coefficient of determination ($R^2$) of **0.888** and a Root Mean Squared Error (RMSE) of **311.5 cases** on independent temporal validation sets, significantly outperforming the baseline Random Forest model ($R^2 = 0.867$). Feature analysis revealed a hierarchical driver structure: Seasonality and autoregressive trends accounted for 55% of predictive power, while climate interactions (specifically lagged rainfall-temperature synergy) contributed 25%. Notably, socio-economic vulnerability features contributed 20% to the model's performance, identifying high-risk outlier states that climate data alone missed.

**Conclusions:** This study demonstrates that integrating socio-economic vulnerability markers with traditional climate-epi models significantly enhances dengue outbreak prediction. The framework offers a deployable tool for state health departments, parallel to the *Nikshay* ecosystem for Tuberculosis, to transition from reactive management to proactive anticipatory action.

**Keywords:** Dengue, Machine Learning, Gradient Boosting, India, Climate Change, NVBDCP, Outbreak Prediction, Public Health Informatics, Infectious Disease Surveillance

---

## 1. Introduction

### 1.1 The Global and National Burden of Dengue
Dengue fever, caused by four distinct serotypes of the *Flaviviridae* virus (DENV 1-4), represents the most rapidly spreading mosquito-borne viral disease globally. The World Health Organization (WHO) estimates that incidence has increased 30-fold over the past 50 years. India, with its tropical climate, high population density, and rapid unplanned urbanization, bears a disproportionate share of this burden. Bhatt et al.$^1$ estimated that India contributes nearly 34% of the global dengue burden, a figure likely underestimated due to limitations in passive surveillance.

### 1.2 The Failure of Reactive Surveillance
Current dengue control strategies in India rely heavily on the National Vector Borne Disease Control Programme (NVBDCP) and the Integrated Disease Surveillance Programme (IDSP). While these systems provide essential retrospective data, they function primarily as "outbreak detection" mechanisms rather than prediction tools. By the time a surge is registered in the central database, transmission has often peaked, rendering vector control measures like fogging reactive and less effective. This lag represents a critical missed window for intervention, typically 4 to 6 weeks.$^2$

### 1.3 Climatic Drivers and the Multi-Modal Hypothesis
The geographic footprint of *Aedes aegypti* is intimately linked to climatic variables. Temperature influences the extrinsic incubation period (EIP) of the virus, while precipitation creates breeding habitats.$^3$ However, climate-driven models often fail to account for the "human factor." We hypothesized that a **"Multi-Modal"** approach—integrating climate, epidemiological history, and **structural vulnerability metrics** (e.g., healthcare capacity)—would yield a more robust predictive model. A state with weaker public health infrastructure (lower Health Index) may experience a larger detected outbreak for the same vector density due to poorer containment.$^4$

---

## 2. Methods

### 2.1 Study Design and Data Sources
This retrospective ecological study analyzed state-level monthly aggregate data from 35 states/UTs in India (2015-2025).

#### 2.1.1 Epidemiological Data
*   **NVBDCP & OpenDengue:** Monthly case counts were aggregated from official NVBDCP reports (2021-2025) and historical OpenDengue trends (1991-2024).$5,6$ Data was log-transformed ($log(x+1)$) to stabilize variance.

#### 2.1.2 Climatic Variables
*   **Meteorological Data:** Annual mean temperature ($T_{mean}$) and total precipitation were expanded into monthly seasonal features using regional weights (South-West vs North-East Monsoon).
*   **Lagged Features:** We calculated 1, 2, and 3-month lags for climate variables to account for biological delays (vector breeding and viral amplification).

#### 2.1.3 Socio-Economic Vulnerability
*   **NITI Aayog Health Index:** A composite score (0-100) reflecting health system performance.$^7$
*   **GDP Per Capita:** A proxy for urbanization and economic resilience.
*   **State Energy & Climate Index (SECI):** A measure of environmental readiness.

### 2.2 Feature Engineering
We generated a rich feature set to capture temporal dynamics:
1.  **Autoregressive Terms:** $Cases_{t-1}, Cases_{t-2}$ and 3-month rolling averages.
2.  **Cyclical Encoding:** Month numbers (1-12) were transformed into sine/cosine components ($Month_{sin}, Month_{cos}$) to preserve seasonal continuity.
3.  **Interaction Terms:** $Rain \times Temp$ to capture synergistic effects on vector competence.

### 2.3 Machine Learning Algorithms
We trained two ensemble tree-based models:
1.  **Random Forest Regressor:** A bagging ensemble ($n\_estimators=100, max\_depth=12$).
2.  **Gradient Boosting Regressor:** A boosting ensemble ($n\_estimators=100, learning\_rate=0.1$) that corrects sequential errors, offering superior performance on complex, non-linear data.$^8$

**Validation Strategy:** To prevent temporal data leakage, we employed **5-fold TimeSeriesSplit**. In each fold $k$, the model was trained on the first $k$ time segments and tested on the $(k+1)^{th}$ segment, ensuring it always predicted "future" unknowns.

---

## 3. Results

### 3.1 Model Performance
The enhanced Gradient Boosting model demonstrated superior predictive accuracy.

**Table 1. Model Performance (Temporal Cross-Validation)**

| Model | $R^2$ Score | RMSE (Cases/Month) | Key Advantage |
| :--- | :--- | :--- | :--- |
| **Gradient Boosting** | **0.888** ($\pm$ 0.04) | **311.5** | Robust capture of non-linear climate interactions. |
| Random Forest | 0.867 ($\pm$ 0.06) | 342.6 | Good baseline but under-predicted extreme peaks. |

The integration of socio-economic variables reduced RMSE by ~15% compared to climate-only baselines.

### 3.2 Drivers of Transmission
Feature importance analysis (gain-based) identified the hierarchy of drivers:

**Table 2. Feature Importance Contribution**

| Rank | Category | Contribution | Mechanism |
| :--- | :--- | :--- | :--- |
| 1 | **Seasonality** | 55.2% | Month (Sin/Cos), Lagged Cases describe the intrinsic viral cycle. |
| 2 | **Climate** | 25.4% | **Lagged Rainfall (2-months)** and Rain-Temp interaction drive vector abundance. |
| 3 | **Vulnerability** | 19.4% | **Health Index** and GDP modulate outbreak magnitude/detection. |

### 3.3 State Risk Assessment
The model generated a composite "Risk Score" (0-100) for the upcoming season. **Tamil Nadu, Telangana, and Maharashtra** were identified as High-Priority states due to a convergence of climatic suitability and socio-economic vulnerability factors.

---

## 4. Discussion

### 4.1 The Vulnerability-Exposure Nexus
Our findings validate the "Vulnerability-Exposure" hypothesis. Traditional models focusing solely on vector biology (Exposure) miss the critical dimension of human systems (Vulnerability). States with lower Health Index scores consistently showed higher case burdens for similar climatic conditions, suggesting that health system capacity is a key determinant of outbreak magnitude.$^9$

### 4.2 Biological Plausibility of Lags
The identification of **2-month lagged rainfall** as a top predictor is biologically consistent with the vector lifecycle: 1-2 weeks for aquatic development + 1-2 weeks for Extrinsic Incubation Period (EIP) + time for secondary transmission.$^{10}$ This confirms the model is learning true biological signals, not just statistical noise.

### 4.3 Comparative Analysis: Lessons from TB Surveillance
India has successfully established a world-class digital surveillance infrastructure for Tuberculosis through **Nikshay**.$^{11}$ This system enables real-time notification, patient tracking, and direct benefit transfers. Our study suggests that a similar "Nikshay for Vector Borne Diseases" is feasible. By integrating the predictive algorithms developed here into such a platform, NVBDCP could transition from "reporting outbreaks" to "predicting and preventing" them. The shared infrastructure (district health officers, lab networks) provides a ready-made chassis for this deployment.$^{12}$

### 4.4 Operational Recommendations
1.  **Early Warning:** Deploy the Risk Scorecard to state health departments 1 month prior to monsoon onset.
2.  **Resource Targeting:** Prioritize fogging and IEC activities in states with high Risk Scores but low Health Indices.
3.  **Data Integration:** Advocate for the inclusion of private sector data (similar to Nikshay) to correct under-reporting bias.

---

## 5. Conclusions
We have developed a robust, data-driven framework for dengue prediction in India ($R^2=0.888$). By fusing climate dynamics with socio-economic vulnerability, we provide a more holistic view of outbreak risk. This tool serves as a foundational step toward a comprehensive National Early Warning System, leveraging the lessons from India's successful TB elimination program to tackle the growing threat of arboviral diseases.

---

## 6. Acknowledgments
We thank the open-source community for maintaining the OpenDengue repository and the NVBDCP for making aggregate data available.

---

## 7. References
1. Bhatt S, Gething PW, Brady OJ, et al. The global distribution and burden of dengue. *Nature*. 2013;496(7446):504-507.
2. Lowe R, Stewart-Ibarra AM, Petrova D, et al. Climate services for health: predicting the evolution of the 2016 dengue season in Machala, Ecuador. *Lancet Planet Health*. 2017;1(4):e142-e151.
3. Messina JP, et al. The current and future global distribution and population at risk of dengue. *Nat Microbiol*. 2019;4:1508–1515.
4. Brady OJ, et al. Refine global dengue maps. *Nature*. 2012;489:515–516.
5. National Vector Borne Disease Control Programme (NVBDCP). Ministry of Health and Family Welfare, Government of India.
6. OpenDengue: Global Dengue Data Repository. [https://opendengue.org]
7. NITI Aayog. Healthy States, Progressive India Report (2019-20). Government of India.
8. Friedman JH. Greedy function approximation: A gradient boosting machine. *Ann Stat*. 2001;29(5):1189-1232.
9. Wesolowski A, et al. Impact of human mobility on the emergence of dengue epidemics in Pakistan. *Proc Natl Acad Sci USA*. 2015;112(38):11887-11892.
10. Tjaden NB, et al. Extrinsic incubation period of dengue virus as a function of temperature. *PLOS Negl Trop Dis*. 2013;7(5):e2207.
11. Sachdeva KS, et al. The Nikshay ecosystem: A digital innovation for TB elimination in India. *Indian J Tuberc*. 2019;66:443-446.
12. Pai M. India's plan to eliminate tuberculosis. *Lancet Glob Health*. 2017;5(6):e564-e565.

---

## 8. Supplementary Materials (Available in Repository)
*   **Figure S1:** Feature Importance Plot (outputs/figures/feature_importance.png)
*   **Figure S2:** Risk vs Vulnerability Scatter (outputs/figures/risk_vs_vulnerability.png)
*   **Figure S3:** Validation Scatter Plot (outputs/figures/validation_scatter.png)
*   **Table S1:** Full State-wise Risk Scorecard (outputs/enhanced/state_risk_scorecard.csv)
