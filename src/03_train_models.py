"""
Train ML models for dengue outbreak prediction.
XGBoost and Random Forest with temporal cross-validation.
"""

import pandas as pd
import numpy as np
import json
import joblib
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor


def temporal_cv_train(X, y, meta, n_splits=5):
    """Train models using temporal cross-validation."""
    
    # Sort by time
    sort_idx = meta.sort_values(['year', 'month']).index
    X = X.loc[sort_idx]
    y = y.loc[sort_idx]
    meta = meta.loc[sort_idx]
    
    # Models to train
    models = {
        'XGBoost': XGBRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'RandomForest': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    }
    
    results = {}
    best_model = None
    best_rmse = float('inf')
    
    for name, model in models.items():
        print(f"\n{'='*40}")
        print(f"Training {name}...")
        print(f"{'='*40}")
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=n_splits)
        
        fold_metrics = []
        for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            # Train
            model_clone = model.__class__(**model.get_params())
            model_clone.fit(X_train, y_train)
            
            # Predict
            y_pred = model_clone.predict(X_val)
            
            # Metrics
            rmse = np.sqrt(mean_squared_error(y_val, y_pred))
            mae = mean_absolute_error(y_val, y_pred)
            r2 = r2_score(y_val, y_pred)
            
            fold_metrics.append({
                'fold': fold + 1,
                'rmse': rmse,
                'mae': mae,
                'r2': r2
            })
        
        # Average metrics
        avg_rmse = np.mean([m['rmse'] for m in fold_metrics])
        avg_mae = np.mean([m['mae'] for m in fold_metrics])
        avg_r2 = np.mean([m['r2'] for m in fold_metrics])
        
        print(f"  RMSE: {avg_rmse:.1f} ± {np.std([m['rmse'] for m in fold_metrics]):.1f}")
        print(f"  MAE:  {avg_mae:.1f}")
        print(f"  R²:   {avg_r2:.3f}")
        
        results[name] = {
            'mean_rmse': float(avg_rmse),
            'mean_mae': float(avg_mae),
            'mean_r2': float(avg_r2),
            'fold_metrics': fold_metrics
        }
        
        # Track best
        if avg_rmse < best_rmse:
            best_rmse = avg_rmse
            best_model = name
    
    # Train final models on all data
    print("\n" + "="*40)
    print("Training final models on all data...")
    print("="*40)
    
    trained_models = {}
    for name, model in models.items():
        model.fit(X, y)
        trained_models[name] = model
        print(f"  {name}: trained")
    
    results['best_model'] = best_model
    results['n_samples'] = len(X)
    results['n_features'] = X.shape[1]
    
    return results, trained_models


def main():
    print("="*60)
    print("TRAINING DENGUE PREDICTION MODELS")
    print("="*60)
    
    # Load data
    X = pd.read_parquet('data/processed/X.parquet')
    y = pd.read_parquet('data/processed/y.parquet')['cases']
    meta = pd.read_parquet('data/processed/meta.parquet')
    
    print(f"Loaded: {X.shape[0]} samples, {X.shape[1]} features")
    
    # Train with temporal CV
    results, models = temporal_cv_train(X, y, meta)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Best model: {results['best_model']}")
    print(f"Best RMSE: {results[results['best_model']]['mean_rmse']:.1f}")
    print(f"Best R²: {results[results['best_model']]['mean_r2']:.3f}")
    
    # Save
    import os
    os.makedirs('outputs/models', exist_ok=True)
    
    with open('outputs/models/cv_metrics.json', 'w') as f:
        # Filter out non-serializable items
        save_results = {k: v for k, v in results.items() if k in ['XGBoost', 'RandomForest', 'best_model', 'n_samples', 'n_features']}
        json.dump(save_results, f, indent=2)
    
    for name, model in models.items():
        joblib.dump(model, f'outputs/models/{name.lower()}_model.joblib')
    
    print(f"\nSaved models to outputs/models/")
    
    return results, models


if __name__ == "__main__":
    main()
