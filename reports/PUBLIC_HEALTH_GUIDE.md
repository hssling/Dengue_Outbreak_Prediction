# India Dengue Risk Prediction System
## Public Health Practitioner Guide

---

## Quick Reference: Risk Categories

| Category | Score Range | Action Required |
|----------|-------------|-----------------|
| **VERY HIGH** | 75-100 | Immediate outbreak response, emergency resources |
| **HIGH** | 50-75 | Enhanced surveillance, pre-position resources |
| **MODERATE** | 25-50 | Routine surveillance, awareness campaigns |
| **LOW** | 0-25 | Standard monitoring |

---

## How Risk Score is Calculated

```
Risk Score = (Incidence × 0.50) + (Trend × 0.30) + (Population × 0.20)
```

### Components:
1. **Incidence (50%)**: Cases per 100,000 population
2. **Trend (30%)**: Year-over-year change in cases
3. **Population (20%)**: Higher population = higher risk

---

## Monthly Risk Calendar (Typical Year)

| Month | Risk Level | Recommended Actions |
|-------|------------|---------------------|
| Jan-Mar | LOW | Baseline surveillance |
| Apr-Jun | RISING | Pre-monsoon vector control |
| **Jul-Oct** | **PEAK** | **Maximum surveillance, outbreak ready** |
| Nov-Dec | DECLINING | Assessment, planning |

---

## State Alert Thresholds

| Incidence per 100k | Alert Level |
|--------------------|-------------|
| < 10 | Green (Normal) |
| 10-50 | Yellow (Watch) |
| 50-100 | Orange (Alert) |
| > 100 | Red (Emergency) |

---

## How to Use the Prediction Model

### 1. Check Current Risk Score
```
File: outputs/risk_scores/state_risk_scores.csv
```
- Find your state
- Check risk_category column

### 2. Review Regional Trends
```
File: outputs/risk_scores/region_risk_summary.csv
```
- Compare your region to others
- Identify cross-border risks

### 3. Plan for Upcoming Season
```
File: outputs/predictions/monsoon_2025_forecast.csv
```
- Review predicted cases for your state
- Allocate resources accordingly

---

## Key Findings for Policy

1. **South and West regions have highest risk**
2. **Monsoon months (Jul-Oct) account for ~60% of cases**
3. **Karnataka, Maharashtra, Kerala need priority attention**
4. **Lagged rainfall is key predictor** - can anticipate outbreaks 1-2 months ahead

---

## Model Accuracy

- **R² = 0.888** (Enhanced Multi-Modal Model)
- **Key Upgrade:** Integrated Health Index & GDP data for better vulnerability assessment
- Trained on 35 states, 2021-2025 data + Historical trends

---

## Contact

For questions about interpreting results:
- See reports/MANUSCRIPT_METHODOLOGY.md for technical details
- Model: outputs/models/dengue_predictor.joblib

---

*System developed using NVBDCP and OpenDengue data*
