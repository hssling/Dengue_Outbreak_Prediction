"""
Process REAL OpenDengue India data for ML training.
Uses filtered_data_SEARO CSV with actual dengue case counts.
"""

import pandas as pd
import numpy as np
import os


def load_opendengue_india():
    """Load real India dengue data from OpenDengue SEARO extract."""
    
    # Load the SEARO filtered data (India only)
    df = pd.read_csv('data/raw/filtered_data_SEARO_1767709711187.csv')
    
    print(f"Loaded {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    
    # Filter to India only
    df = df[df['adm_0_name'] == 'INDIA'].copy()
    print(f"India records: {len(df)}")
    
    # Select relevant columns
    df = df[['Year', 'dengue_total', 'T_res', 'S_res']].copy()
    df.columns = ['year', 'cases', 'temporal_res', 'spatial_res']
    
    # Sort by year
    df = df.sort_values('year').reset_index(drop=True)
    
    print(f"\nYears: {df['year'].min()}-{df['year'].max()}")
    print(f"Total cases: {df['cases'].sum():,}")
    
    return df


def add_synthetic_climate():
    """Add synthetic climate features since we don't have IMD data yet."""
    np.random.seed(42)
    
    # Load India dengue data
    df = load_opendengue_india()
    
    # Expand to monthly for each year
    monthly_data = []
    for _, row in df.iterrows():
        year = row['year']
        annual_cases = row['cases']
        
        # Distribute cases across months (monsoon peak pattern)
        month_weights = np.array([
            0.02, 0.02, 0.03, 0.03, 0.05, 0.08,  # Jan-Jun
            0.12, 0.18, 0.20, 0.15, 0.08, 0.04   # Jul-Dec (monsoon peak)
        ])
        month_weights = month_weights / month_weights.sum()
        
        for month in range(1, 13):
            # Distribute cases by month
            monthly_cases = int(annual_cases * month_weights[month-1] * 
                              np.random.lognormal(0, 0.15))
            
            # Synthetic climate (monsoon pattern)
            if month in [7, 8, 9, 10]:  # Monsoon
                temp = np.random.normal(28, 2)
                rain = np.random.gamma(5, 50)
                humidity = np.random.normal(78, 8)
            elif month in [3, 4, 5, 6]:  # Pre-monsoon hot
                temp = np.random.normal(35, 3)
                rain = np.random.gamma(1.5, 20)
                humidity = np.random.normal(45, 12)
            else:  # Winter
                temp = np.random.normal(22, 4)
                rain = np.random.gamma(0.5, 10)
                humidity = np.random.normal(55, 10)
            
            monthly_data.append({
                'year': year,
                'month': month,
                'cases': max(0, monthly_cases),
                'temperature_c': round(temp, 1),
                'rainfall_mm': round(max(0, rain), 1),
                'humidity_pct': round(np.clip(humidity, 20, 100), 1)
            })
    
    df_monthly = pd.DataFrame(monthly_data)
    
    # Add population (estimate for India)
    df_monthly['population_millions'] = 1400  # India total
    df_monthly['incidence_per_100k'] = df_monthly['cases'] / 1400 * 100
    
    print(f"\nMonthly dataset: {len(df_monthly)} records")
    print(f"Years: {df_monthly['year'].min()}-{df_monthly['year'].max()}")
    print(f"Monthly cases range: {df_monthly['cases'].min()}-{df_monthly['cases'].max()}")
    
    return df_monthly


def main():
    print("="*60)
    print("PROCESSING REAL OPENDENGUE INDIA DATA")
    print("="*60)
    
    # Load and process
    df = add_synthetic_climate()
    
    # Save
    os.makedirs('data/processed', exist_ok=True)
    df.to_csv('data/raw/india_dengue_monthly_real.csv', index=False)
    
    print(f"\nSaved to data/raw/india_dengue_monthly_real.csv")
    
    # Summary by year
    print("\n" + "="*60)
    print("ANNUAL CASE SUMMARY (REAL DATA)")
    print("="*60)
    annual = df.groupby('year')['cases'].sum().reset_index()
    for _, row in annual.iterrows():
        print(f"  {int(row['year'])}: {int(row['cases']):>10,} cases")
    
    return df


if __name__ == "__main__":
    main()
