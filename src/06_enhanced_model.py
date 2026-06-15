"""
Enhanced Dengue Prediction System with Multi-Modal Data Integration
- Integrates:
  1. NVBDCP Dengue Case Data (2021-2025)
  2. Climate Data (Annual Temp/Precip 2021-2024)
  3. Socio-economic Data (GDP, Health Index, SECI)
  4. Population Data
- Generates state-level risk scores and forecasts
"""

import pandas as pd
import numpy as np
import os
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.model_selection import TimeSeriesSplit, cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, r2_score, roc_curve, auc, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler

# ------------------------------------------------------------------------------
# 1. Data Loading Functions
# ------------------------------------------------------------------------------

def load_nvbdcp_data():
    """Load and process NVBDCP state-wise data (2021-2025)."""
    print("Loading NVBDCP epidemiological data...")
    try:
        df = pd.read_excel('data/raw/Dengue data India 2022-2025.xlsx')
    except Exception as e:
        print(f"Error reading NVBDCP Excel: {e}")
        return pd.DataFrame()
    
    records = []
    for idx, row in df.iterrows():
        if idx == 0: continue # Header row
        if pd.isna(row['Sl. No.']): continue
            
        state = row['Affected States/UTs']
        if pd.isna(state) or 'Total' in str(state): continue
        
        # Hardcoded years based on file structure
        years = [2021, 2022, 2023, 2024, 2025]
        col_idx = 2
        
        for year in years:
            try:
                cases = row.iloc[col_idx]
                deaths = row.iloc[col_idx + 1]
                
                if pd.notna(cases) and str(cases) != 'C':
                    records.append({
                        'state': state.strip(),
                        'year': year,
                        'cases': int(cases) if pd.notna(cases) else 0,
                        'deaths': int(deaths) if pd.notna(deaths) else 0
                    })
            except:
                pass
            col_idx += 2
    
    df_out = pd.DataFrame(records)
    # Standardize state names
    df_out['state'] = df_out['state'].replace({
        'Chattisgarh': 'Chhattisgarh',
        'Odisha': 'Odisha',
        'J & K': 'Jammu & Kashmir',
        'Telangana': 'Telangana'
    })
    return df_out

def load_climate_data():
    """Load state-wise annual climate data."""
    print("Loading Climate data...")
    try:
        df = pd.read_csv('data/raw/data_related/climate_state_annual.csv')
        # Rename columns for clarity
        df = df.rename(columns={'t2m_mean': 'annual_mean_temp', 'precip_total_mm': 'annual_rainfall'})
        return df
    except Exception as e:
        print(f"Warning: Could not load climate data: {e}")
        return pd.DataFrame()

def load_socioeconomic_data():
    """Load and merge socio-economic indicators."""
    print("Loading Socio-economic data...")
    dfs = []
    
    # GDP
    try:
        gdp = pd.read_csv('data/raw/data_related/gdp_per_capita_state.csv')
        dfs.append(gdp.set_index('state'))
    except: pass
    
    # Health Index
    try:
        health = pd.read_csv('data/raw/data_related/health_index_2019_20.csv')
        dfs.append(health.set_index('state'))
    except: pass
    
    # SECI
    try:
        seci = pd.read_csv('data/raw/data_related/seci_round1.csv')
        dfs.append(seci.set_index('state'))
    except: pass
    
    if not dfs:
        return pd.DataFrame()
        
    merged = pd.concat(dfs, axis=1).reset_index()
    return merged

def get_region_map():
    return {
        'North': ['Delhi', 'Haryana', 'Himachal Pradesh', 'Jammu & Kashmir', 'Punjab', 'Rajasthan', 'Uttarakhand', 'Chandigarh', 'Ladakh'],
        'South': ['Andhra Pradesh', 'Karnataka', 'Kerala', 'Tamil Nadu', 'Telangana', 'Puducherry', 'Lakshadweep', 'Andaman and Nicobar Islands'],
        'East': ['Bihar', 'Jharkhand', 'Odisha', 'West Bengal', 'Sikkim'],
        'West': ['Goa', 'Gujarat', 'Maharashtra', 'Dadra and Nagar Haveli and Daman and Diu'],
        'Central': ['Madhya Pradesh', 'Chhattisgarh', 'Uttar Pradesh'],
        'Northeast': ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Tripura']
    }

# ------------------------------------------------------------------------------
# 2. Data Integration
# ------------------------------------------------------------------------------

def integrate_data():
    """Merge all data sources into a single DataFrame."""
    
    # 1. Load NVBDCP
    epidemiology = load_nvbdcp_data()
    if epidemiology.empty:
        raise ValueError("Critical: NVBDCP data not found.")
        
    # 2. Load Climate and merge
    climate = load_climate_data()
    if not climate.empty:
        # Fuzzy merge or standardize names could be better, but doing exact match for now
        epidemiology = pd.merge(epidemiology, climate, on=['state', 'year'], how='left')
        
        # Fill missing climate data (e.g. 2025) with state averages
        state_climate_means = climate.groupby('state')[['annual_mean_temp', 'annual_rainfall']].mean()
        epidemiology = epidemiology.set_index('state')
        epidemiology['annual_mean_temp'] = epidemiology['annual_mean_temp'].fillna(state_climate_means['annual_mean_temp'])
        epidemiology['annual_rainfall'] = epidemiology['annual_rainfall'].fillna(state_climate_means['annual_rainfall'])
        epidemiology = epidemiology.reset_index()
    
    # 3. Load Socio-economic and merge
    socio = load_socioeconomic_data()
    if not socio.empty:
        epidemiology = pd.merge(epidemiology, socio, on='state', how='left')
    
    # 4. Fill remaining missing values with medians/means
    epidemiology['gdp_pc'] = epidemiology['gdp_pc'].fillna(epidemiology['gdp_pc'].median())
    epidemiology['health_index_2019_20'] = epidemiology['health_index_2019_20'].fillna(epidemiology['health_index_2019_20'].mean())
    epidemiology['seci_score'] = epidemiology['seci_score'].fillna(epidemiology['seci_score'].mean())
    epidemiology['annual_mean_temp'] = epidemiology['annual_mean_temp'].fillna(epidemiology['annual_mean_temp'].mean())
    epidemiology['annual_rainfall'] = epidemiology['annual_rainfall'].fillna(epidemiology['annual_rainfall'].mean())

    # 5. Add Region
    regions = get_region_map()
    region_flat = {s: r for r, states in regions.items() for s in states}
    epidemiology['region'] = epidemiology['state'].map(region_flat).fillna('Other')

    print(f"Integrated dataset shape: {epidemiology.shape}")
    return epidemiology

# ------------------------------------------------------------------------------
# 3. Feature Engineering & Monthly Expansion
# ------------------------------------------------------------------------------

def expand_to_monthly(df_annual):
    """
    Expand annual data to monthly for higher resolution training.
    Uses synthetic seasonality weighted by real annual totals.
    """
    print("Expanding annual data to monthly using seasonal weights...")
    monthly_records = []
    
    np.random.seed(42)
    
    for _, row in df_annual.iterrows():
        # Only process years we have partial or full data for
        if row['year'] > 2025: continue
        
        # Monthly weights (Monsoon peak)
        base_weights = np.array([0.02, 0.02, 0.03, 0.04, 0.06, 0.09, 0.14, 0.20, 0.18, 0.12, 0.06, 0.04])
        
        # Adjust weights based on region (simple heuristic)
        if row['region'] == 'South': # Bimodal rainfall
            base_weights = np.array([0.03, 0.03, 0.04, 0.05, 0.06, 0.10, 0.12, 0.15, 0.15, 0.15, 0.08, 0.04])
            
        weights = base_weights / base_weights.sum()
        
        for month in range(1, 13):
            # Skip future months for 2025 (assume data valid till current month, e.g., Dec 2025 is prediction)
            # Actually NVBDCP 2025 data might be partial, but we treat 'cases' as annual total/projection for simplicity in training
            
            # Distribute cases
            est_cases = int(row['cases'] * weights[month-1] * np.random.lognormal(0, 0.1))
            
            # Derived monthly climate (perturb annual mean)
            # Temp: Summer (M3-6) > Monsoon (M7-10) > Winter (M11-2)
            if month in [3, 4, 5, 6]:
                m_temp = row['annual_mean_temp'] + 5
                m_rain = row['annual_rainfall'] * 0.05
            elif month in [7, 8, 9, 10]:
                m_temp = row['annual_mean_temp']
                m_rain = row['annual_rainfall'] * 0.20 # 80% rain in 4 months
            else:
                m_temp = row['annual_mean_temp'] - 5
                m_rain = row['annual_rainfall'] * 0.0
            
            # Add stochasticity
            m_temp += np.random.normal(0, 1.5)
            m_rain *= np.random.gamma(2, 0.5) 
            
            record = row.to_dict()
            record['month'] = month
            record['cases_monthly'] = est_cases
            record['temp_monthly'] = m_temp
            record['rain_monthly'] = m_rain
            
            # Remove annual keys to avoid confusion
            del record['cases']
            del record['deaths']
            
            monthly_records.append(record)
            
    return pd.DataFrame(monthly_records)

def create_features(df):
    """Create ML features."""
    # Lag features
    df['cases_lag1'] = df.groupby('state')['cases_monthly'].shift(1).fillna(0)
    df['cases_lag2'] = df.groupby('state')['cases_monthly'].shift(2).fillna(0)
    
    # Rolling mean
    df['cases_roll3'] = df.groupby('state')['cases_monthly'].shift(1).rolling(3).mean().fillna(0)
    
    # Climate interaction
    df['rain_temp_interaction'] = df['rain_monthly'] * df['temp_monthly']
    
    # Seasonality
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Drop NAs
    df = df.dropna()
    return df

# ------------------------------------------------------------------------------
# 4. Modeling & Validation
# ------------------------------------------------------------------------------

def train_and_validate(df):
    """Train XGBoost/RF and validate."""
    print("\nTraining Enhanced Models...")
    
    features = [
        'temp_monthly', 'rain_monthly', 'gdp_pc', 'health_index_2019_20', 'seci_score',
        'month_sin', 'month_cos', 'cases_lag1', 'cases_lag2', 'cases_roll3',
        'rain_temp_interaction', 'annual_mean_temp', 'annual_rainfall'
    ]
    
    target = 'cases_monthly'
    X = df[features]
    y = df[target]
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)
    
    models = {
        'RandomForest': RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        'GradientBoosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }
    
    results = {}
    
    # Time-series cross-validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    for name, model in models.items():
        print(f"  Evaluating {name}...")
        scores_r2 = cross_val_score(model, X_scaled, y, scoring='r2', cv=tscv)
        scores_neg_rmse = cross_val_score(model, X_scaled, y, scoring='neg_root_mean_squared_error', cv=tscv)
        
        results[name] = {
            'R2_mean': scores_r2.mean(),
            'RMSE_mean': -scores_neg_rmse.mean()
        }
        print(f"    R²: {scores_r2.mean():.4f} (+/- {scores_r2.std():.4f})")
        print(f"    RMSE: {-scores_neg_rmse.mean():.2f}")
    
    # Retrain best model on full data
    best_model_name = max(results, key=lambda k: results[k]['R2_mean'])
    print(f"\nBest Model: {best_model_name}")
    
    final_model = models[best_model_name]
    final_model.fit(X_scaled, y)
    
    # --- ADDED: Classification for ROC Analysis ---
    print("\nTraining Outbreak Classifier (for ROC/AUC)...")
    threshold = np.percentile(y, 75)
    y_class = (y > threshold).astype(int)
    print(f"Outbreak Threshold (>75th percentile): {threshold:.0f} cases")
    
    clf = GradientBoostingClassifier(n_estimators=100, random_state=42)
    # Use last year for validation
    split_idx = int(len(X_scaled) * 0.8)
    X_train, X_test = X_scaled.iloc[:split_idx], X_scaled.iloc[split_idx:]
    y_train, y_test = y_class.iloc[:split_idx], y_class.iloc[split_idx:]
    
    clf.fit(X_train, y_train)
    y_prob = clf.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    print(f"Classification AUC: {roc_auc:.3f}")
    
    # Save classifier and ROC data
    joblib.dump(clf, 'outputs/models/outbreak_classifier.joblib')
    joblib.dump({'fpr': fpr, 'tpr': tpr, 'auc': roc_auc}, 'outputs/models/roc_data.joblib')
    
    return final_model, scaler, features, results, clf, roc_auc

# ------------------------------------------------------------------------------
# 5. Risk Scoring & Forecasting
# ------------------------------------------------------------------------------

def generate_risk_report(model, scaler, df, features):
    """Generate state-wise risk scores and forecasts."""
    print("\nGenerating Risk Scoring System...")
    
    # Get latest data state for each state
    latest_state = df.sort_values(['year', 'month']).groupby('state').tail(1).copy()
    
    # Predict next month (simplified: use current features as proxy for next month forecast basis)
    X_latest = pd.DataFrame(scaler.transform(latest_state[features]), columns=features)
    latest_state['forecast_cases'] = model.predict(X_latest)
    
    risk_scores = []
    for _, row in latest_state.iterrows():
        # Composite Risk Score (0-100)
        # 1. Forecast Magnitude (40%)
        # 2. Structural Vulnerability (Health Index, GDP) (30%)
        # 3. Climate Suitability (Rain/Temp) (30%)
        
        # Normalize inputs roughly to 0-1 range
        norm_case = min(row['forecast_cases'] / 2000, 1.0) # Cap at 2000 monthly cases
        norm_health = 1.0 - (row['health_index_2019_20'] / 100.0) # Invert: Low health index = high risk
        norm_climate = min(row['rain_monthly'] / 300, 1.0) # High rain = high risk
        
        score = (norm_case * 40) + (norm_health * 30) + (norm_climate * 30)
        
        category = 'Low'
        if score > 30: category = 'Moderate'
        if score > 50: category = 'High'
        if score > 75: category = 'Very High'
        
        risk_scores.append({
            'State': row['state'],
            'Region': row['region'],
            'Risk Score': round(score, 1),
            'Risk Category': category,
            'Forecast Cases': int(max(0, row['forecast_cases'])),
            'Health Index': row['health_index_2019_20'],
            'Annual Rain': row['annual_rainfall']
        })
        
    risk_df = pd.DataFrame(risk_scores).sort_values('Risk Score', ascending=False)
    
    print("\nTOP 10 RISK STATES (Next Month Forecast):")
    print(risk_df[['State', 'Risk Score', 'Risk Category', 'Forecast Cases']].head(10).to_string(index=False))
    
    # Save
    os.makedirs('outputs/enhanced', exist_ok=True)
    risk_df.to_csv('outputs/enhanced/state_risk_scorecard.csv', index=False)
    print("\nSaved risk scorecard to outputs/enhanced/state_risk_scorecard.csv")

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------

def main():
    print("="*60)
    print("ROBUST DENGUE MODEL (ENHANCED)")
    print("="*60)
    
    # 1. Integrate
    df_integrated = integrate_data()
    
    # 2. Expand
    df_monthly = expand_to_monthly(df_integrated)
    
    # 3. Feature Engineering
    df_model = create_features(df_monthly)
    print(f"Modeling Dataset: {df_model.shape[0]} samples, {df_model.shape[1]} columns")
    
    # 4. Train & Validate
    model, scaler, feature_names, results, clf, roc_auc = train_and_validate(df_model)
    
    # 5. Risk Scoring
    generate_risk_report(model, scaler, df_model, feature_names)
    
    # Save model artifacts
    joblib.dump(model, 'outputs/models/robust_dengue_model.joblib')
    joblib.dump(scaler, 'outputs/models/robust_scaler.joblib')

if __name__ == "__main__":
    main()
