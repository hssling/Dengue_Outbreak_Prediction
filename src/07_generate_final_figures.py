"""
Generate high-quality publication figures for the Enhanced Dengue Model.
"""
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

def generate_figures():
    print("Generating Publication Figures...")
    os.makedirs('outputs/figures', exist_ok=True)
    
    # Load model and scaler
    try:
        model = joblib.load('outputs/models/robust_dengue_model.joblib')
        # scaler = joblib.load('outputs/models/robust_scaler.joblib') 
    except:
        print("Model not found. Please run 06_enhanced_model.py first.")
        return

    # 1. Feature Importance Plot
    if hasattr(model, 'feature_importances_'):
        # Get feature names from the previous script run (hardcoded for now based on knowledge)
        features = [
            'temp_monthly', 'rain_monthly', 'gdp_pc', 'health_index_2019_20', 'seci_score',
            'month_sin', 'month_cos', 'cases_lag1', 'cases_lag2', 'cases_roll3',
            'rain_temp_interaction', 'annual_mean_temp', 'annual_rainfall'
        ]
        
        # Adjust features assignment if length mismatch (sanity check)
        if len(model.feature_importances_) != len(features):
            print("Warning: Feature length mismatch. Using generic names.")
            features = [f'Feature {i}' for i in range(len(model.feature_importances_))]
            
        feat_imp = pd.DataFrame({
            'Feature': features,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=feat_imp, x='Importance', y='Feature')
        plt.title('Feature Importance (Gradient Boosting)', fontsize=14)
        plt.tight_layout()
        plt.savefig('outputs/figures/feature_importance.png', dpi=300)
        print("Scaved feature_importance.png")
        
    # 2. Risk Score Visualization
    try:
        risk_df = pd.read_csv('outputs/enhanced/state_risk_scorecard.csv')
        
        # Risk Distribution Bar Plot (Top 10)
        plt.figure(figsize=(12, 6))
        top10 = risk_df.head(10)
        sns.barplot(data=top10, x='Risk Score', y='State', palette='Reds_r')
        plt.title('Top 10 States by Dengue Outbreak Risk Score (Next Month)', fontsize=14)
        plt.xlabel('Risk Score (0-100)')
        plt.tight_layout()
        plt.savefig('outputs/figures/top_risk_states.png', dpi=300)
        print("Saved top_risk_states.png")
        
        # Risk Vs Health Index Scatter
        plt.figure(figsize=(8, 6))
        sns.scatterplot(data=risk_df, x='Health Index', y='Risk Score', 
                        hue='Region', s=100, alpha=0.7)
        plt.title('Vulnerability Analysis: Risk Score vs Health Index', fontsize=14)
        plt.axhline(50, ls='--', color='red', alpha=0.5, label='High Risk Threshold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.tight_layout()
        plt.savefig('outputs/figures/risk_vs_vulnerability.png', dpi=300)
        print("Saved risk_vs_vulnerability.png")
        
    except Exception as e:
        print(f"Could not generate risk plots: {e}")

if __name__ == "__main__":
    generate_figures()
