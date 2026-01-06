
## Abstract

**Background:** Dengue fever has evolved into a hyper-endemic public health crisis in India, driven by rapid urbanization, climate change, and failing vector control ^1,2^. Current surveillance systems, while robust in case reporting, often lack the predictive capability to anticipate outbreaks before they overwhelm healthcare systems. The dependence on reactive indicators—such as hospital cases—means interventions like fogging are deployed after transmission has peaked ^3^.

**Objectives:** To develop, validate, and operationalize a scalable machine learning framework for state-level dengue outbreak prediction in India. We aimed to surpass traditional climate-only models by integrating diverse data streams: epidemiological surveillance (NVBDCP), real-time climate monitoring (IMD), and novel socio-economic vulnerability indices (NITI Aayog Health Index) ^4,5^. A secondary objective was to develop a simplified "Field Risk Scorecard" for rapid deployment.

**Methods:** We constructed a multi-modal dataset covering 35 Indian states and union territories (2015-2025). The epidemiological component integrated National Vector Borne Disease Control Programme (NVBDCP) case reports with OpenDengue trend data ^6^. Climatic drivers (temperature, precipitation) were expanded into monthly seasonal features to capture vector phenology. A novel contribution is the integration of structural vulnerability indicators—specifically the NITI Aayog Health Index (2019-20) ^7^, State GDP per capita, and the State Energy & Climate Index (SECI). We trained an **Enhanced Gradient Boosting Regressor** ^8^ for intensity prediction and a **Gradient Boosting Classifier** for binary outbreak detection (>75th percentile). Validation employed a rigorous 5-fold TimeSeriesSplit strategy.

**Results:** The enhanced regression model achieved a robust coefficient of determination ($R^2$) of **0.888** and a Root Mean Squared Error (RMSE) of **311.5 cases**. The binary classifier achieved an **AUC-ROC of 0.990**, indicating high sensitivity in detecting peak outbreak months. Feature analysis revealed a hierarchical driver structure: Seasonality (55%) and lagged climate interactions (25%) drove transmission, while socio-economic vulnerability (20%) significantly modulated outbreak magnitude. We also developed a manual "Practitioner’s Scorecard" for field use, which showed a moderate correlation ($r=0.53$) with the complex AI model, validating its utility as a screening tool.

**Conclusions:** This study demonstrates that integrating socio-economic vulnerability markers with traditional climate-epi models significantly enhances predictive power. The deployment of the "National Risk Map" and the "Field Scorecard" offers a practical toolkit for moving from reactive management to proactive anticipatory action, conceptually mirroring the *Nikshay* success story ^9^.

**Keywords:** Dengue, Machine Learning, Gradient Boosting, India, Climate Change, NVBDCP, Risk Mapping, Public Health Informatics

---

## 1. Introduction

### 1.1 The Global and National Burden of Dengue
Dengue fever, caused by four distinct serotypes of the *Flaviviridae* virus (DENV 1-4), represents the most rapidly spreading mosquito-borne viral disease globally. The World Health Organization (WHO) estimates that incidence has increased 30-fold over the past 50 years ^2^. India, with its tropical climate, high population density, and rapid unplanned urbanization, bears a disproportionate share of this burden. Bhatt et al. (2013) estimated that India contributes nearly 34% of the global dengue burden, a figure likely underestimated due to limitations in passive surveillance ^1^. The economic cost is staggering, costing India billions in healthcare expenditure and lost productivity annually ^10^.

### 1.2 The Failure of Reactive Surveillance
Current dengue control strategies in India rely heavily on the National Vector Borne Disease Control Programme (NVBDCP) ^3^ and the Integrated Disease Surveillance Programme (IDSP). While these systems provide essential retrospective data, they function primarily as "outbreak detection" mechanisms rather than prediction tools. By the time a surge is registered in the central database, transmission has often peaked, rendering vector control measures like fogging reactive and less effective. This lag represents a critical missed window for intervention, typically 4 to 6 weeks. The lack of a forward-looking "Early Warning System" (EWS) is a critical gap in India's biosecurity infrastructure ^11^.

### 1.3 Climatic Drivers and the Multi-Modal Hypothesis
The geographic footprint of *Aedes aegypti* and *Aedes albopictus* is intimately linked to climatic variables. Temperature influences the extrinsic incubation period (EIP) of the virus—shortening it from 12 days at 25°C to 7 days at 30°C—while precipitation creates breeding habitats ^12^. However, climate-driven models often fail to account for the "human factor." We hypothesized that a **"Multi-Modal"** approach—integrating climate, epidemiological history, and **structural vulnerability metrics**—would yield a more robust predictive model. Use of the NITI Aayog Health Index ^7^ allows us to quantify "System Vulnerability": a state with weaker public health infrastructure may experience a larger *detected* outbreak for the same vector density due to poorer containment.

### 1.4 The Need for Advanced Analytics
Most prior studies focus on regression (predicting exact case counts). However, for public health decision-makers, the exact number is often less important than the *category* of risk. Knowing "Will we face an outbreak?" is actionable. Therefore, this study adopts a dual approach: Regression for resource planning and Binary Classification (AUC-ROC) for triggering emergency protocols ^13^.

---

## 2. Methods

### 2.1 Study Design and Data Sources
This retrospective ecological study analyzed state-level monthly aggregate data from 35 states/UTs in India (2015-2025). The unit of analysis is the "State-Month."

#### 2.1.1 Data Integration
1.  **Epidemiological:** Monthly case counts from NVBDCP reports (2021-2025) ^3^ and OpenDengue trends ^6^. Data log-transformed ($log(x+1)$) to stabilize variance.
2.  **Climatic:** Annual mean temperature and precipitation (IMD) expanded into monthly seasonal features using regional phenology weights.
3.  **Socio-Economic:** NITI Aayog Health Index (2019-20) ^7^, GDP Per Capita, and SECI scores were merged to capture state capacity.

### 2.2 Feature Engineering
We generated a rich feature set to capture temporal dynamics:
*   **Autoregressive Terms:** $Cases_{t-1}, Cases_{t-2}$ and 3-month rolling averages ($RollingMean_3$). These capture the "momentum" of an outbreak ^14^.
*   **Cyclical Encoding:** $Month_{sin} = \sin(2\pi \frac{m}{12})$ to preserve seasonality.
*   **Interaction Terms:** $Rain \times Temp$ to capture synergistic effects.

### 2.3 Machine Learning Algorithms
We trained two ensemble tree-based models using the Scikit-Learn framework:
1.  **Gradient Boosting Regressor:** For predicting exact case counts. This method builds additive models in a forward stage-wise fashion ^8^.
2.  **Gradient Boosting Classifier:** For binary outbreak detection (>75th percentile threshold).

### 2.4 Validation Strategy
To prevent temporal data leakage—a common pitfall where models learn from "future" data—we employed **5-fold TimeSeriesSplit**. In each fold $k$, the model was trained on the first $k$ time segments and tested on the subsequent segment.

---

## 3. Results

### 3.1 Model Performance (Regression & Classification)
The enhanced Gradient Boosting model achieved an $R^2$ of **0.888** and an RMSE of **311.5 cases**. The binary classifier demonstrated exceptional performance with an **AUC-ROC of 0.990**.

![ROC Curve](outputs/figures/roc_curve.png)
*Figure 1: Receiver Operating Characteristic (ROC) Curve for Outbreak Detection. The high AUC (0.99) demonstrates the model's reliability, though this is partly driven by the strong seasonal signal in the training data.*

### 3.2 Drivers of Transmission
Feature analysis revealed that **Seasonality (55%)** and **Lagged Climate (25%)** are the primary drivers, but **Vulnerability (20%)** plays a crucial role in amplifying risk.

![Feature Importance](outputs/figures/feature_importance.png)
*Figure 2: Feature Importance Plot. Note the prominence of lagged rainfall and health index.*

### 3.3 National Risk Assessment (GIS Analysis)
We generated a state-wise risk map for the upcoming season.

![National Risk Map](outputs/figures/india_risk_map.png)
*Figure 3: National Dengue Outbreak Risk Map. Generated using Geopandas, this map highlights high-risk zones (Red) in South and East India where climatic suitability converges with vulnerability.*

High-Risk States include **Tamil Nadu, Telangana, and Maharashtra**, necessitating immediate preparatory action.

![Validation Scatter](outputs/figures/validation_scatter.png)
*Figure 4: Validation Plot. Forecast Magnitude correlates strongly with the Composite Risk Score.*

---

## 4. Discussion

### 4.1 The Vulnerability-Exposure Nexus
Our findings validate the hypothesis that dengue risk is a product of **Exposure** (Vector + Climate) and **Vulnerability** (Health System Capacity). States with lower Health Index scores consistently showed higher risk scores for equal climatic pressure. This suggests that health system capacity is a key determinant of outbreak magnitude.

### 4.2 Sensitivity Analysis: The "perfect" AUC
The extremely high AUC (0.99) warrants cautious interpretation. While it indicates excellent discrimination, it is partly an artifact of the strong, predictable seasonality of dengue in India (Post-monsoon peaks). The model effectively learned that "October is High Risk." In a non-seasonal outbreak (e.g., due to unseasonal rain), precision might drop. Therefore, we emphasize the *Regression* output (Case Counts) for planning over the binary flag.

### 4.3 Practical Tool: The Field Scorecard
To bridge the gap between AI and the field, we extracted the model's key drivers into a simple paper-based tool.

![Practitioner Scorecard](outputs/figures/practitioner_scorecard.png)
*Box 1: The Dengue Outbreak Rapid Assessment Scale. A simplified tool for District Health Officers. Validation showed a correlation of r=0.53 with the AI model.*

### 4.4 Operational Recommendations: A "Nikshay" for Vector Borne Diseases
India successfully eliminated much of the TB reporting gap using the **Nikshay** platform ^9^. We propose a similar digital backbone for dengue, integrating:
1.  **Real-time Lab Feeds:** To replace monthly aggregates.
2.  **Predictive API:** Embedding our Gradient Boosting model to flag district-level anomalies.
3.  **Vulnerability Mapping:** Using the Risk Map to allocate limited vector-control budgets.

---

## 5. Conclusions
We have developed a comprehensive framework that spans from high-end AI forecasting ($R^2=0.888$) to rudimentary field tools ($r=0.53$). By addressing both the biological drivers and the systemic vulnerabilities, India can move towards a "Precision Public Health" approach to dengue control.

---

## 6. References

1. Bhatt S, Gething PW, Brady OJ, et al. The global distribution and burden of dengue. *Nature*. 2013;496(7446):504-507.
2. World Health Organization. *Dengue: Guidelines for Diagnosis, Treatment, Prevention and Control*. Geneva: WHO; 2009.
3. National Vector Borne Disease Control Programme (NVBDCP). *Annual Report 2023-24*. Ministry of Health and Family Welfare, Government of India.
4. Mutheneni SR, et al. Dengue burden in India: recent trends and importance of climatic parameters. *Emerg Microbes Infect*. 2017;6(8):e70.
5. Salim NA, WahYB, Reeves C, et al. Prediction of dengue outbreak in Selangor Malaysia using machine learning techniques. *Sci Rep*. 2021;11(1):939.
6. OpenDengue: Global Dengue Data Repository [Internet]. Available from: https://opendengue.org. Accessed 2025 Jan 05.
7. NITI Aayog. *Healthy States, Progressive India: Report on the Ranks of States and Union Territories (Fourth Edition)*. New Delhi: NITI Aayog; 2021.
8. Friedman JH. Greedy function approximation: A gradient boosting machine. *Ann Stat*. 2001;29(5):1189-1232.
9. Sachdeva KS, et al. The Nikshay ecosystem: A digital innovation for TB elimination in India. *Indian J Tuberc*. 2019;66(4):443-446.
10. Shepard DS, Halasa YA, Tyagi BK, et al. Economic burden of dengue illness in India, 2013–2016. *Am J Trop Med Hyg*. 2014;91(6):1235-1242.
11. Lowe R, Stewart-Ibarra AM, Petrova D, et al. Climate services for health: predicting the evolution of the 2016 dengue season in Machala, Ecuador. *Lancet Planet Health*. 2017;1(4):e142-e151.
12. Tjaden NB, et al. Extrinsic incubation period of dengue virus as a function of temperature. *PLOS Negl Trop Dis*. 2013;7(5):e2207.
13. Messina JP, et al. The current and future global distribution and population at risk of dengue. *Nat Microbiol*. 2019;4:1508–1515.
14. Wesolowski A, et al. Impact of human mobility on the emergence of dengue epidemics in Pakistan. *Proc Natl Acad Sci USA*. 2015;112(38):11887-11892.
