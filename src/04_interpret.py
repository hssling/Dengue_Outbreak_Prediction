"""
SHAP interpretation for dengue prediction models.
Generates feature importance plots and climate driver analysis.
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


def plot_feature_importance(model, X, save_path):
    """Plot feature importance bar chart."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    else:
        importances = np.abs(model.coef_) if hasattr(model, 'coef_') else None
    
    if importances is None:
        print("Model doesn't have feature_importances_")
        return None
    
    # Create dataframe
    imp_df = pd.DataFrame({
        'feature': X.columns,
        'importance': importances
    }).sort_values('importance', ascending=True)
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(imp_df['feature'], imp_df['importance'], color='steelblue')
    ax.set_xlabel('Feature Importance')
    ax.set_title('XGBoost Feature Importance for Dengue Prediction')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved feature importance plot to {save_path}")
    
    return imp_df


def plot_shap_summary(model, X, save_path):
    """Generate SHAP summary plot."""
    if not HAS_SHAP:
        print("SHAP not available, using feature importance instead")
        return None
    
    # Create explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    # Summary plot
    plt.figure(figsize=(10, 8))
    shap.summary_plot(shap_values, X, show=False, max_display=15)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Saved SHAP summary plot to {save_path}")
    
    return shap_values


def analyze_climate_drivers(imp_df):
    """Analyze which climate factors are most important."""
    # Group features
    climate_features = ['temperature_c', 'rainfall_mm', 'humidity_pct',
                       'temp_lag1', 'temp_lag2', 'rain_lag1', 'rain_lag2',
                       'humidity_lag1', 'humidity_lag2',
                       'temp_rolling3', 'rain_rolling3']
    
    temporal_features = ['month_sin', 'month_cos', 'is_monsoon']
    autoregressive = ['cases_lag1', 'cases_lag2', 'cases_lag3', 'cases_lag4', 'cases_rolling3']
    
    imp_df['category'] = 'other'
    imp_df.loc[imp_df['feature'].isin(climate_features), 'category'] = 'climate'
    imp_df.loc[imp_df['feature'].isin(temporal_features), 'category'] = 'temporal'
    imp_df.loc[imp_df['feature'].isin(autoregressive), 'category'] = 'autoregressive'
    
    # Summary by category
    category_imp = imp_df.groupby('category')['importance'].sum()
    print("\nFeature importance by category:")
    for cat, imp in category_imp.sort_values(ascending=False).items():
        print(f"  {cat}: {imp:.3f}")
    
    return category_imp


def main():
    print("="*60)
    print("INTERPRETING DENGUE PREDICTION MODEL")
    print("="*60)
    
    # Load data and model
    X = pd.read_parquet('data/processed/X.parquet')
    model = joblib.load('outputs/models/xgboost_model.joblib')
    
    print(f"Loaded model and {len(X)} samples")
    
    import os
    os.makedirs('outputs/figures', exist_ok=True)
    
    # Feature importance
    print("\nGenerating feature importance plot...")
    imp_df = plot_feature_importance(model, X, 'outputs/figures/feature_importance.png')
    
    # Climate driver analysis
    category_imp = analyze_climate_drivers(imp_df)
    
    # Top features
    print("\nTop 10 most important features:")
    for _, row in imp_df.sort_values('importance', ascending=False).head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.3f}")
    
    # SHAP if available
    if HAS_SHAP:
        print("\nGenerating SHAP summary plot...")
        plot_shap_summary(model, X.sample(min(500, len(X)), random_state=42), 
                         'outputs/figures/shap_summary.png')
    
    # Save feature importance table
    imp_df.sort_values('importance', ascending=False).to_csv(
        'reports/feature_importance.csv', index=False
    )
    print("\nSaved feature importance table to reports/feature_importance.csv")
    
    print("\nInterpretation complete!")


if __name__ == "__main__":
    main()
