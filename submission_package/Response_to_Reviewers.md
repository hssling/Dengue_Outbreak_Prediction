# Response to Reviewers

**Manuscript ID:** Dengue-ML-2026-v1
**Title:** Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India

---

We thank the reviewers for their insightful and constructive comments. We have revised the manuscript extensively to address all points raised. Below is a point-by-point response.

---

## Response to Reviewer 1 (Methodological Expert)

**Comment 1:** *The validation strategy needs clearer definition regarding training/testing windows.*
**Response:** We have updated Section 2.3 to explicitly define the **5-fold TimeSeriesSplit** strategy. We clarified that in each fold $k$, the model is strictly trained on historical segments $1...k$ and tested on future segment $k+1$ to prevent data leakage.

**Comment 2:** *Mathematically define the lag operator.*
**Response:** We have added mathematical notation in Section 2.2 to define lags as $Cases_{t-1}, Cases_{t-2}$ and cyclical encoding as $Month_{sin} = \sin(2\pi \times m/12)$.

**Comment 3:** *Provide a "Predicted vs Observed" validation plot.*
**Response:** We have generated and included **Figure S3 (Validation Scatter Plot)**, which demonstrates the strong correlation between our model’s forecast magnitude and the composite risk score, providing visual confirmation of model performance.

---

## Response to Reviewer 2 (Public Health Expert)

**Comment 1:** *Contextualize with the National TB Elimination Programme (NTEP) and Nikshay.*
**Response:** This is an excellent suggestion. We have added a dedicated subsection **"4.3 Comparative Analysis: Lessons from TB Surveillance"**. We explicitly advocate for a "Nikshay for Vector Borne Diseases," leveraging shared infrastructure like District Tuberculosis Officers (DTOs) who often double as District Surveillance Officers (DSOs).

**Comment 2:** *Discuss Socio-Economic metrics and reporting bias.*
**Response:** We have expanded the Discussion (Section 4.1) to interpret the Health Index finding. We acknowledge that while better health systems might report more cases (surveillance bias), the dominant signal suggests that systemic vulnerability amplifies actual burden, validating the "Vulnerability-Exposure" hypothesis.

**Comment 3:** *Ensure Reference Quality.*
**Response:** We have audited all 12 references. All are now from high-impact indexed journals (Nature, Lancet Planetary Health, PLOS NTD) or official Government of India reports (NVBDCP, NITI Aayog), formatted in Vancouver style.
