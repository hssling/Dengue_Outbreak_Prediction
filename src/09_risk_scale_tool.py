import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def generate_scorecard_tool():
    print("Generating Practitioner's Risk Scorecard...")
    os.makedirs('outputs/figures', exist_ok=True)
    
    # 1. Define the Checklist (Visual)
    plt.figure(figsize=(8, 10))
    plt.axis('off')
    
    # Draw Checklist
    plt.text(0.5, 0.95, "DENGUE OUTBREAK RAPID ASSESSMENT SCALE", ha='center', va='center', fontsize=16, weight='bold', color='darkred')
    plt.text(0.5, 0.90, "For District Health Officers / Surveillance Units", ha='center', va='center', fontsize=10, style='italic')
    
    y = 0.80
    plt.text(0.1, y, "A. CLIMATE FACTORS (Last 30 Days)", fontsize=12, weight='bold', color='blue')
    y -= 0.05
    plt.text(0.15, y, "[ ] Heavy Rainfall (>200mm) .................................. +3 Points", fontsize=10)
    y -= 0.04
    plt.text(0.15, y, "[ ] Moderate Rainfall (50-200mm) ........................... +2 Points", fontsize=10)
    y -= 0.04
    plt.text(0.15, y, "[ ] High Humidity (>70%) ....................................... +2 Points", fontsize=10)
    y -= 0.04
    plt.text(0.15, y, "[ ] Avg Temperature (25-32°C) ............................... +3 Points", fontsize=10)
    
    y -= 0.08
    plt.text(0.1, y, "B. ENTOMOLOGICAL INDICES", fontsize=12, weight='bold', color='green')
    y -= 0.05
    plt.text(0.15, y, "[ ] House Index (HI) > 10% .................................... +5 Points", fontsize=10)
    y -= 0.04
    plt.text(0.15, y, "[ ] Breteau Index (BI) > 20 .................................... +5 Points", fontsize=10)
    
    y -= 0.08
    plt.text(0.1, y, "C. SYSTEM VULNERABILITY", fontsize=12, weight='bold', color='orange')
    y -= 0.05
    plt.text(0.15, y, "[ ] High Vacancy in Fogging Staff (>20%) ................. +4 Points", fontsize=10)
    y -= 0.04
    plt.text(0.15, y, "[ ] Urban Slum Density > 30% ................................ +3 Points", fontsize=10)
    
    y -= 0.10
    plt.text(0.1, y, "SCORING INTERPRETATION:", fontsize=12, weight='bold')
    y -= 0.05
    plt.text(0.15, y, "0 - 5 : Routine Surveillance (Green)", fontsize=10, color='green')
    plt.text(0.15, y-0.04, "6 - 15: Enhanced Alert (Yellow)", fontsize=10, color='#B8860B')
    plt.text(0.15, y-0.08, "> 15  : OUTBREAK IMMINENT (Red)", fontsize=10, color='red', weight='bold')
    
    # Border
    plt.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color='black', lw=2)
    
    plt.tight_layout()
    plt.savefig('outputs/figures/practitioner_scorecard.png', dpi=300, bbox_inches='tight')
    print("Saved scorecard image to outputs/figures/practitioner_scorecard.png")

    # 2. Validation: Correlate Simplified Score vs Model Prediction
    # We will simulate the "Simplified Score" using our dataset terms roughly mapping to the checklist
    try:
        df = pd.read_csv('outputs/enhanced/state_risk_scorecard.csv')
        
        # Simplified Heuristic Proxy
        # Rain > 200mm -> +3, 50-200 -> +2
        df['Sim_Rain'] = df['Annual Rain'].apply(lambda x: 3 if x/12 > 200 else (2 if x/12 > 50 else 0)) # Crude monthly est
        
        # Health Index (Inverse Proxy for "Vacancy/Slum")
        # Low Index (<40) -> High Vulnerability (+4)
        df['Sim_Vuln'] = df['Health Index'].apply(lambda x: 4 if x < 40 else (2 if x < 60 else 0))
        
        # Total Sim Score
        df['Simplified_Score'] = df['Sim_Rain'] + df['Sim_Vuln'] + 5 # Base +5 for endemicity assumption
        
        correlation = df['Risk Score'].corr(df['Simplified_Score'])
        print(f"Validation: Correlation between Simplified Checklist and AI Risk Score: {correlation:.2f}")
    except Exception as e:
        print(f"Validation skipped: {e}")

if __name__ == "__main__":
    generate_scorecard_tool()
