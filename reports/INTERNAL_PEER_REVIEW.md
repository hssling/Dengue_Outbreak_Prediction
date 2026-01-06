# Internal Peer Review Report
**Target Journal:** Indian Journal of Medical Research (IJMR)
**Manuscript Title:** Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India

---

## Reviewer 1 (Methodological Expert)

**Summary:**
The study presents a solid application of Gradient Boosting to predict dengue outbreaks using a novel mix of climate and socio-economic data. The R² of 0.888 is impressive. However, the manuscript lacks mathematical rigor in the feature engineering definition.

**Critique & Recommendations:**
1.  **Validation Strategy (Major):** The term "TimeSeriesSplit" is mentioned, but the exact training/testing windows are not defined. *Action:* Specify the exact years used for training vs testing in each fold.
2.  **Feature Engineering (Moderate):** "Lagged features" are mentioned. Please mathematically define the lag operator used. Are you using simple autoregression $AR(p)$ or something more complex?
3.  **Visual Evidence (Critical):** A "Predicted vs Observed" time-series plot for a representative high-burden state is strictly necessary to visually validate the R².

---

## Reviewer 2 (Public Health Expert)

**Summary:**
The integration of the Health Index is innovative. However, the Discussion fails to contextualize this within the broader Indian communicable disease control landscape.

**Critique & Recommendations:**
1.  **Contextual Linking (Major):** The authors miss a key opportunity to compare this surveillance upgrade to the **National TB Elimination Programme (NTEP)**. NTEP’s *Nikshay* system is a digital surveillance model; dengue needs a similar approach. Please elaborate in Discussion.
2.  **Socio-Economic Interpretation (Moderate):** You claim "lower health index = higher risk". Discuss if this is due to reporting bias vs actual control failure.
3.  **Reference Quality:** Ensure all references are from indexed journals and formatted correctly (Vancouver).

---

## Editor's Decision: **Major Revision**
Please address the above points, particularly the Nikshay/TB comparison and the time-series validation plot.
