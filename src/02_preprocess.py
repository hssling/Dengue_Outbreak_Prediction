"""
Preprocess dengue data for ML training.
Creates lagged features and train/test splits.
"""

import pandas as pd
import numpy as np
from pathlib import Path


def create_lagged_features(df, lag_weeks=[1, 2, 3, 4]):
    """Create lagged climate and case features."""
    df = df.sort_values(['state', 'year', 'month']).copy()
    
    lagged_dfs = []
    for state in df['state'].unique():
        state_df = df[df['state'] == state].copy()
        
        # Lag features
        for lag in lag_weeks:
            state_df[f'cases_lag{lag}'] = state_df['cases'].shift(lag)
            state_df[f'temp_lag{lag}'] = state_df['temperature_c'].shift(lag)
            state_df[f'rain_lag{lag}'] = state_df['rainfall_mm'].shift(lag)
            state_df[f'humidity_lag{lag}'] = state_df['humidity_pct'].shift(lag)
        
        # Rolling averages
        state_df['cases_rolling3'] = state_df['cases'].rolling(3).mean()
        state_df['temp_rolling3'] = state_df['temperature_c'].rolling(3).mean()
        state_df['rain_rolling3'] = state_df['rainfall_mm'].rolling(3).mean()
        
        lagged_dfs.append(state_df)
    
    return pd.concat(lagged_dfs, ignore_index=True)


def add_seasonality_features(df):
    """Add seasonal indicators."""
    df = df.copy()
    
    # Month as cyclic features
    df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
    
    # Season categories
    df['season'] = pd.cut(df['month'], 
                          bins=[0, 3, 6, 9, 12],
                          labels=['winter', 'summer', 'monsoon', 'post_monsoon'])
    
    # Monsoon indicator (peak dengue season)
    df['is_monsoon'] = df['month'].isin([7, 8, 9, 10]).astype(int)
    
    return df


def prepare_ml_dataset(df):
    """Prepare final ML dataset."""
    
    # Feature columns
    feature_cols = [
        'temperature_c', 'rainfall_mm', 'humidity_pct',
        'population_millions', 'month_sin', 'month_cos', 'is_monsoon',
        'cases_lag1', 'cases_lag2', 'cases_lag3', 'cases_lag4',
        'temp_lag1', 'temp_lag2', 'rain_lag1', 'rain_lag2',
        'humidity_lag1', 'humidity_lag2',
        'cases_rolling3', 'temp_rolling3', 'rain_rolling3'
    ]
    
    # Drop rows with NaN (from lagging)
    df_clean = df.dropna(subset=feature_cols)
    
    # Create X and y
    X = df_clean[feature_cols]
    y = df_clean['cases']
    
    # Metadata for analysis
    meta = df_clean[['state', 'year', 'month']]
    
    return X, y, meta, df_clean


def main():
    print("="*60)
    print("PREPROCESSING DENGUE DATA")
    print("="*60)
    
    # Load raw data
    df = pd.read_csv('data/raw/dengue_climate_india.csv')
    print(f"\nLoaded {len(df)} records")
    
    # Add lagged features
    print("Creating lagged features...")
    df = create_lagged_features(df)
    
    # Add seasonality
    print("Adding seasonality features...")
    df = add_seasonality_features(df)
    
    # Prepare ML dataset
    print("Preparing ML dataset...")
    X, y, meta, df_full = prepare_ml_dataset(df)
    
    print(f"\nFinal dataset:")
    print(f"  Samples: {len(X)}")
    print(f"  Features: {X.shape[1]}")
    
    # Train/test split (temporal: last year for testing)
    train_mask = meta['year'] < 2024
    test_mask = meta['year'] >= 2024
    
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    
    print(f"\nTrain set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Save
    import os
    os.makedirs('data/processed', exist_ok=True)
    
    df_full.to_parquet('data/processed/dengue_features.parquet', index=False)
    X.to_parquet('data/processed/X.parquet')
    y.to_frame('cases').to_parquet('data/processed/y.parquet')
    meta.to_parquet('data/processed/meta.parquet')
    
    print("\nSaved to data/processed/")
    
    return X, y, meta


if __name__ == "__main__":
    main()
