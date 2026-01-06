"""
Comprehensive Dengue Prediction System
- Integrates OpenDengue + NVBDCP data
- State-wise, region-wise predictions
- Risk scoring for public health practitioners
"""

import pandas as pd
import numpy as np
import os
import json
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except:
    HAS_XGB = False


def load_nvbdcp_data():
    """Load and process NVBDCP state-wise data (2021-2025)."""
    df = pd.read_excel('data/raw/Dengue data India 2022-2025.xlsx')
    
    # Process the multi-column format
    # Columns: Sl.No, State, 2021(C), 2021(D), 2022(C), 2022(D), etc.
    
    records = []
    for idx, row in df.iterrows():
        if idx == 0:  # Skip header row with C/D labels
            continue
        if pd.isna(row['Sl. No.']):
            continue
            
        state = row['Affected States/UTs']
        if pd.isna(state) or 'Total' in str(state):
            continue
        
        # Extract year-wise data (columns alternate between Cases and Deaths)
        years = [2021, 2022, 2023, 2024, 2025]
        col_idx = 2  # Start from column index 2
        
        for year in years:
            try:
                cases = row.iloc[col_idx]
                deaths = row.iloc[col_idx + 1]
                
                if pd.notna(cases) and str(cases) != 'C':
                    records.append({
                        'state': state.strip(),
                        'year': year,
                        'cases': int(cases) if pd.notna(cases) else 0,
                        'deaths': int(deaths) if pd.notna(deaths) else 0,
                        'source': 'NVBDCP'
                    })
            except:
                pass
            col_idx += 2
    
    df_nvbdcp = pd.DataFrame(records)
    print(f"NVBDCP: {len(df_nvbdcp)} state-year records")
    print(f"States: {df_nvbdcp['state'].nunique()}")
    
    return df_nvbdcp


def load_opendengue_data():
    """Load OpenDengue national-level data."""
    df = pd.read_csv('data/raw/filtered_data_SEARO_1767709711187.csv')
    df = df[df['adm_0_name'] == 'INDIA'].copy()
    
    df_od = pd.DataFrame({
        'year': df['Year'],
        'cases': df['dengue_total'],
        'source': 'OpenDengue'
    })
    
    print(f"OpenDengue: {len(df_od)} national-year records")
    
    return df_od


def get_state_populations():
    """State population estimates (2024)."""
    return {
        'Andhra Pradesh': 53.9, 'Arunachal Pradesh': 1.6, 'Assam': 35.6,
        'Bihar': 127.0, 'Chattisgarh': 29.4, 'Goa': 1.6, 'Gujarat': 71.5,
        'Haryana': 30.4, 'Himachal Pradesh': 7.4, 'J & K': 14.1,
        'Jharkhand': 39.4, 'Karnataka': 69.0, 'Kerala': 35.6,
        'Lakshadweep': 0.08, 'Madhya Pradesh': 87.6, 'Maharashtra': 127.0,
        'Manipur': 3.2, 'Meghalaya': 3.8, 'Mizoram': 1.3, 'Nagaland': 2.3,
        'Odisha': 46.4, 'Punjab': 31.3, 'Rajasthan': 82.4, 'Sikkim': 0.7,
        'Tamil Nadu': 78.9, 'Telangana': 39.4, 'Tripura': 4.2,
        'Uttar Pradesh': 235.0, 'Uttarakhand': 11.9, 'West Bengal': 101.0,
        'A & N Islands': 0.4, 'Chandigarh': 1.2, 'DNH & DD': 0.6,
        'Delhi': 20.8, 'Ladakh': 0.3, 'Pondicherry': 1.6, 'The Dadra ...': 0.6
    }


def get_regions():
    """Define regions for India."""
    return {
        'North': ['Delhi', 'Haryana', 'Himachal Pradesh', 'J & K', 'Punjab', 
                  'Rajasthan', 'Uttarakhand', 'Chandigarh', 'Ladakh'],
        'South': ['Andhra Pradesh', 'Karnataka', 'Kerala', 'Tamil Nadu', 
                  'Telangana', 'Pondicherry', 'Lakshadweep', 'A & N Islands'],
        'East': ['Bihar', 'Jharkhand', 'Odisha', 'West Bengal', 'Sikkim'],
        'West': ['Goa', 'Gujarat', 'Maharashtra', 'DNH & DD', 'The Dadra ...'],
        'Central': ['Madhya Pradesh', 'Chattisgarh', 'Uttar Pradesh'],
        'Northeast': ['Arunachal Pradesh', 'Assam', 'Manipur', 'Meghalaya', 
                      'Mizoram', 'Nagaland', 'Tripura']
    }


def create_training_data(df_nvbdcp):
    """Create features for ML training."""
    np.random.seed(42)
    
    # Add population and compute incidence
    pop_map = get_state_populations()
    df = df_nvbdcp.copy()
    
    # Map states to populations (handle fuzzy matching)
    df['population_millions'] = df['state'].apply(
        lambda x: next((v for k, v in pop_map.items() if k.lower() in x.lower() or x.lower() in k.lower()), 10.0)
    )
    
    df['incidence_per_100k'] = df['cases'] / df['population_millions'] * 100
    df['cfr_pct'] = np.where(df['cases'] > 0, df['deaths'] / df['cases'] * 100, 0)
    
    # Add region
    regions = get_regions()
    region_map = {state: region for region, states in regions.items() for state in states}
    df['region'] = df['state'].apply(
        lambda x: next((r for s, r in region_map.items() if s.lower() in x.lower() or x.lower() in s.lower()), 'Other')
    )
    
    # Add synthetic monthly expansion with climate
    monthly_records = []
    
    for _, row in df.iterrows():
        state = row['state']
        year = row['year']
        annual_cases = row['cases']
        annual_deaths = row['deaths']
        pop = row['population_millions']
        region = row['region']
        
        # Monthly distribution (monsoon peak pattern)
        month_weights = np.array([
            0.02, 0.02, 0.03, 0.04, 0.06, 0.09,
            0.14, 0.20, 0.18, 0.12, 0.06, 0.04
        ])
        month_weights = month_weights / month_weights.sum()
        
        for month in range(1, 13):
            # Skip future months for 2025
            if year == 2025 and month > 1:
                continue
            
            monthly_cases = int(annual_cases * month_weights[month-1] * 
                              np.random.lognormal(0, 0.10))
            monthly_deaths = int(annual_deaths * month_weights[month-1] + 
                               np.random.poisson(0.5))
            
            # Synthetic climate based on region and month
            if region in ['South', 'West']:
                base_temp = 30
            elif region in ['North', 'Central']:
                base_temp = 25
            else:
                base_temp = 24
            
            # Monsoon pattern
            if month in [7, 8, 9, 10]:
                temp = base_temp - 3 + np.random.normal(0, 2)
                rain = np.random.gamma(6, 50)
                humidity = np.random.normal(80, 5)
            elif month in [3, 4, 5, 6]:
                temp = base_temp + 5 + np.random.normal(0, 3)
                rain = np.random.gamma(1.5, 15)
                humidity = np.random.normal(50, 10)
            else:
                temp = base_temp - 5 + np.random.normal(0, 3)
                rain = np.random.gamma(0.8, 10)
                humidity = np.random.normal(60, 8)
            
            monthly_records.append({
                'state': state,
                'region': region,
                'year': year,
                'month': month,
                'cases': max(0, monthly_cases),
                'deaths': max(0, monthly_deaths),
                'population_millions': pop,
                'temperature_c': round(temp, 1),
                'rainfall_mm': round(max(0, rain), 1),
                'humidity_pct': round(np.clip(humidity, 20, 100), 1)
            })
    
    df_monthly = pd.DataFrame(monthly_records)
    
    # Add derived features
    df_monthly['incidence_per_100k'] = df_monthly['cases'] / df_monthly['population_millions'] * 100
    df_monthly['month_sin'] = np.sin(2 * np.pi * df_monthly['month'] / 12)
    df_monthly['month_cos'] = np.cos(2 * np.pi * df_monthly['month'] / 12)
    df_monthly['is_monsoon'] = df_monthly['month'].isin([7, 8, 9, 10]).astype(int)
    
    # Encode state and region
    le_state = LabelEncoder()
    le_region = LabelEncoder()
    df_monthly['state_encoded'] = le_state.fit_transform(df_monthly['state'])
    df_monthly['region_encoded'] = le_region.fit_transform(df_monthly['region'])
    
    print(f"Monthly training data: {len(df_monthly)} records")
    print(f"States: {df_monthly['state'].nunique()}")
    
    return df_monthly, le_state, le_region


def add_lag_features(df):
    """Add lagged features per state."""
    df = df.sort_values(['state', 'year', 'month']).copy()
    
    lagged = []
    for state in df['state'].unique():
        state_df = df[df['state'] == state].copy()
        
        for lag in [1, 2, 3]:
            state_df[f'cases_lag{lag}'] = state_df['cases'].shift(lag)
            state_df[f'temp_lag{lag}'] = state_df['temperature_c'].shift(lag)
            state_df[f'rain_lag{lag}'] = state_df['rainfall_mm'].shift(lag)
        
        state_df['cases_rolling3'] = state_df['cases'].rolling(3).mean()
        
        lagged.append(state_df)
    
    return pd.concat(lagged, ignore_index=True)


def train_models(df):
    """Train prediction models."""
    print("\n" + "="*60)
    print("TRAINING DENGUE PREDICTION MODELS")
    print("="*60)
    
    # Define features
    feature_cols = [
        'state_encoded', 'region_encoded', 'population_millions',
        'temperature_c', 'rainfall_mm', 'humidity_pct',
        'month_sin', 'month_cos', 'is_monsoon',
        'cases_lag1', 'cases_lag2', 'cases_lag3',
        'temp_lag1', 'rain_lag1', 'cases_rolling3'
    ]
    
    # Drop NaN from lagging
    df_clean = df.dropna(subset=feature_cols)
    
    X = df_clean[feature_cols]
    y = df_clean['cases']
    
    print(f"Training samples: {len(X)}")
    print(f"Features: {len(feature_cols)}")
    
    # Time series CV
    models = {}
    if HAS_XGB:
        models['XGBoost'] = XGBRegressor(n_estimators=100, max_depth=6, 
                                          learning_rate=0.1, random_state=42)
    models['RandomForest'] = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    models['GradientBoosting'] = GradientBoostingRegressor(n_estimators=100, random_state=42)
    
    results = {}
    best_model = None
    best_rmse = float('inf')
    
    tscv = TimeSeriesSplit(n_splits=3)
    
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        fold_metrics = []
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model_clone = model.__class__(**model.get_params())
            model_clone.fit(X_train, y_train)
            y_pred = model_clone.predict(X_val)
            
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            r2 = r2_score(y_val, y_pred)
            fold_metrics.append({'rmse': rmse, 'r2': r2})
        
        avg_rmse = np.mean([m['rmse'] for m in fold_metrics])
        avg_r2 = np.mean([m['r2'] for m in fold_metrics])
        
        print(f"  RMSE: {avg_rmse:.1f}")
        print(f"  R²: {avg_r2:.3f}")
        
        results[name] = {'rmse': avg_rmse, 'r2': avg_r2}
        
        if avg_rmse < best_rmse:
            best_rmse = avg_rmse
            best_model = name
    
    # Train final model on all data
    print(f"\nBest model: {best_model}")
    final_model = models[best_model]
    final_model.fit(X, y)
    
    return final_model, results, feature_cols, df_clean


def calculate_risk_scores(df, model, feature_cols):
    """Calculate risk scores for each state."""
    print("\n" + "="*60)
    print("CALCULATING RISK SCORES")
    print("="*60)
    
    # Get latest data per state
    latest = df.sort_values(['state', 'year', 'month']).groupby('state').last().reset_index()
    
    risk_scores = []
    
    for _, row in latest.iterrows():
        state = row['state']
        region = row['region']
        pop = row['population_millions']
        cases = row['cases']
        incidence = row['incidence_per_100k']
        
        # Calculate risk score based on:
        # 1. Recent incidence (50%)
        # 2. Historical trend (30%)
        # 3. Population vulnerability (20%)
        
        # Incidence score (0-100)
        if incidence < 5:
            incidence_score = 10
        elif incidence < 20:
            incidence_score = 30
        elif incidence < 50:
            incidence_score = 50
        elif incidence < 100:
            incidence_score = 70
        else:
            incidence_score = 90
        
        # Trend score (based on year-over-year)
        state_data = df[df['state'] == state].groupby('year')['cases'].sum()
        if len(state_data) >= 2:
            trend = (state_data.iloc[-1] - state_data.iloc[-2]) / (state_data.iloc[-2] + 1) * 100
            trend_score = min(100, max(0, 50 + trend / 2))
        else:
            trend_score = 50
        
        # Population score (higher pop = higher risk)
        pop_score = min(100, pop / 2)
        
        # Composite risk score
        risk_score = (incidence_score * 0.50 + 
                     trend_score * 0.30 + 
                     pop_score * 0.20)
        
        # Risk category
        if risk_score < 25:
            risk_category = "LOW"
        elif risk_score < 50:
            risk_category = "MODERATE"
        elif risk_score < 75:
            risk_category = "HIGH"
        else:
            risk_category = "VERY HIGH"
        
        risk_scores.append({
            'state': state,
            'region': region,
            'population_millions': pop,
            'recent_cases': cases,
            'incidence_per_100k': round(incidence, 1),
            'risk_score': round(risk_score, 1),
            'risk_category': risk_category,
            'incidence_component': round(incidence_score * 0.50, 1),
            'trend_component': round(trend_score * 0.30, 1),
            'population_component': round(pop_score * 0.20, 1)
        })
    
    risk_df = pd.DataFrame(risk_scores)
    risk_df = risk_df.sort_values('risk_score', ascending=False)
    
    print("\nTop 10 Highest Risk States:")
    print(risk_df.head(10)[['state', 'risk_score', 'risk_category', 
                            'recent_cases', 'incidence_per_100k']].to_string())
    
    return risk_df


def predict_future_outbreaks(model, df, feature_cols, le_state, le_region):
    """Predict future outbreak risk for 2025."""
    print("\n" + "="*60)
    print("PREDICTING FUTURE OUTBREAKS (2025)")
    print("="*60)
    
    predictions = []
    
    for state in df['state'].unique():
        state_data = df[df['state'] == state].sort_values(['year', 'month'])
        if len(state_data) < 3:
            continue
        
        latest = state_data.iloc[-1]
        region = latest['region']
        pop = latest['population_millions']
        
        # Predict for monsoon months (Jul-Oct 2025)
        for month in [7, 8, 9, 10]:
            # Create feature row
            features = {
                'state_encoded': le_state.transform([state])[0],
                'region_encoded': le_region.transform([region])[0],
                'population_millions': pop,
                'temperature_c': 28 + np.random.normal(0, 2),  # Monsoon temp
                'rainfall_mm': np.random.gamma(5, 50),  # Monsoon rain
                'humidity_pct': 80 + np.random.normal(0, 5),
                'month_sin': np.sin(2 * np.pi * month / 12),
                'month_cos': np.cos(2 * np.pi * month / 12),
                'is_monsoon': 1,
                'cases_lag1': latest['cases'],
                'cases_lag2': state_data.iloc[-2]['cases'] if len(state_data) > 1 else latest['cases'],
                'cases_lag3': state_data.iloc[-3]['cases'] if len(state_data) > 2 else latest['cases'],
                'temp_lag1': latest['temperature_c'],
                'rain_lag1': latest['rainfall_mm'],
                'cases_rolling3': state_data['cases'].tail(3).mean()
            }
            
            X_pred = pd.DataFrame([features])[feature_cols]
            pred_cases = max(0, int(model.predict(X_pred)[0]))
            
            predictions.append({
                'state': state,
                'region': region,
                'year': 2025,
                'month': month,
                'predicted_cases': pred_cases
            })
    
    pred_df = pd.DataFrame(predictions)
    
    # Aggregate by state for monsoon 2025
    state_forecast = pred_df.groupby('state')['predicted_cases'].sum().reset_index()
    state_forecast.columns = ['state', 'predicted_monsoon_2025_cases']
    state_forecast = state_forecast.sort_values('predicted_monsoon_2025_cases', ascending=False)
    
    print("\nMonsoon 2025 Forecast (Top 15 States):")
    print(state_forecast.head(15).to_string())
    
    return pred_df, state_forecast


def create_region_summary(risk_df):
    """Create region-wise summary."""
    print("\n" + "="*60)
    print("REGION-WISE RISK SUMMARY")
    print("="*60)
    
    region_summary = risk_df.groupby('region').agg({
        'risk_score': 'mean',
        'recent_cases': 'sum',
        'population_millions': 'sum',
        'state': 'count'
    }).round(1)
    
    region_summary.columns = ['avg_risk_score', 'total_cases', 'total_pop_millions', 'num_states']
    region_summary['incidence_per_100k'] = (region_summary['total_cases'] / 
                                             region_summary['total_pop_millions'] * 100).round(1)
    region_summary = region_summary.sort_values('avg_risk_score', ascending=False)
    
    print(region_summary.to_string())
    
    return region_summary


def save_outputs(risk_df, region_summary, state_forecast, model, results):
    """Save all outputs."""
    os.makedirs('outputs/predictions', exist_ok=True)
    os.makedirs('outputs/risk_scores', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Save risk scores
    risk_df.to_csv('outputs/risk_scores/state_risk_scores.csv', index=False)
    region_summary.to_csv('outputs/risk_scores/region_risk_summary.csv')
    state_forecast.to_csv('outputs/predictions/monsoon_2025_forecast.csv', index=False)
    
    # Save model
    joblib.dump(model, 'outputs/models/dengue_predictor.joblib')
    
    # Save results
    with open('outputs/models/training_results.json', 'w') as f:
        json.dump({k: {kk: float(vv) for kk, vv in v.items()} for k, v in results.items()}, f, indent=2)
    
    print("\n" + "="*60)
    print("OUTPUTS SAVED")
    print("="*60)
    print("- outputs/risk_scores/state_risk_scores.csv")
    print("- outputs/risk_scores/region_risk_summary.csv")
    print("- outputs/predictions/monsoon_2025_forecast.csv")
    print("- outputs/models/dengue_predictor.joblib")


def main():
    print("="*60)
    print("DENGUE PREDICTION SYSTEM FOR INDIA")
    print("Public Health Risk Assessment Tool")
    print("="*60)
    
    # 1. Load data
    print("\n[1] Loading data...")
    df_nvbdcp = load_nvbdcp_data()
    df_opendengue = load_opendengue_data()
    
    # 2. Create training data
    print("\n[2] Creating training features...")
    df_monthly, le_state, le_region = create_training_data(df_nvbdcp)
    df_monthly = add_lag_features(df_monthly)
    
    # 3. Train models
    print("\n[3] Training models...")
    model, results, feature_cols, df_clean = train_models(df_monthly)
    
    # 4. Calculate risk scores
    print("\n[4] Calculating risk scores...")
    risk_df = calculate_risk_scores(df_monthly, model, feature_cols)
    
    # 5. Region summary
    region_summary = create_region_summary(risk_df)
    
    # 6. Future predictions
    print("\n[5] Predicting future outbreaks...")
    pred_df, state_forecast = predict_future_outbreaks(
        model, df_monthly, feature_cols, le_state, le_region
    )
    
    # 7. Save outputs
    print("\n[6] Saving outputs...")
    save_outputs(risk_df, region_summary, state_forecast, model, results)
    
    print("\n" + "="*60)
    print("✅ DENGUE PREDICTION SYSTEM COMPLETE")
    print("="*60)
    
    return risk_df, region_summary, state_forecast


if __name__ == "__main__":
    main()
