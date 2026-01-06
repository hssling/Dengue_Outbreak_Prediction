# India Dengue Outbreak Prediction System 🦟🇮🇳

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Model R2](https://img.shields.io/badge/GradientBoosting-R%C2%B2%200.888-green)](outputs/models)

A robust, multi-modal machine learning system for predicting dengue outbreaks in India using epidemiological, climate, and socio-economic vulnerability indicators.

## 🚀 Key Features

*   **Multi-Source Integration**: Merges NVBDCP data, OpenDengue trends, Real-time Climate (IMD/State), and Socio-Economic indices (NITI Aayog Health Index, GDP).
*   **High Performance**: Gradient Boosting Regressor achieving **R² = 0.888** and **RMSE = 311 cases**.
*   **Risk Scoring**: Generates state-wise composite risk scores (0-100) combining forecast magnitude, structural vulnerability, and climate suitability.
*   **Public Health Focus**: Designed for operational use by state health departments.

## 📊 Results Summary

| Model | R² Score | RMSE (Cases) | Key Advantage |
| :--- | :--- | :--- | :--- |
| **Gradient Boosting** | **0.888** | **311.5** | Best non-linear capture of rain-temp interactions |
| Random Forest | 0.867 | 342.6 | Robust baseline |

### Top Risk Drivers
1. **Seasonality (55%)**: Month, Monsoon timing
2. **Climate (25%)**: Lagged Rain-Temp interactions
3. **Vulnerability (20%)**: Health Index, GDP

## 📂 Project Structure

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

## 🛠️ Usage

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run the Pipeline
```bash
# Run the enhanced multi-modal model
python src/06_enhanced_model.py

# Generate visualization figures
python src/07_generate_final_figures.py
```

### 3. Check Outputs
*   **Risk Scorecard**: `outputs/enhanced/state_risk_scorecard.csv`
*   **Manuscript**: `reports/MANUSCRIPT_FINAL.md`

## 👥 Authors

**Dr. Siddalingaiah H S**  
*Lead Investigator & Developer*

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Data Sources
*   **NVBDCP**: State-wise dengue cases
*   **OpenDengue**: Historical trends
*   **NITI Aayog**: Health Index 2019-20
