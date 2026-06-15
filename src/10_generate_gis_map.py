import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

def generate_gis_map():
    print("Generating GIS Risk Map...")
    os.makedirs('outputs/figures', exist_ok=True)
    
    # 1. Load Shapefile
    shp_path = 'data/raw/data_related/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp'
    if not os.path.exists(shp_path):
        print("Shapefile not found.")
        return
        
    india_map = gpd.read_file(shp_path)
    
    # Filter for India
    india_map = india_map[india_map['admin'] == 'India']
    
    # 2. Load Risk Data
    risk_df = pd.read_csv('outputs/enhanced/state_risk_scorecard.csv')
    
    # 3. Merge
    # Standardize names for merge (Common issues: 'Jammu and Kashmir' vs 'Jammu & Kashmir')
    name_map = {
        'Andaman and Nicobar': 'Andaman and Nicobar Islands',
        'Orissa': 'Odisha',
        'Uttaranchal': 'Uttarakhand'
    }
    india_map['name'] = india_map['name'].replace(name_map)
    
    # Merge
    merged = india_map.set_index('name').join(risk_df.set_index('State'))
    
    # 4. Plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged.plot(column='Risk Score', ax=ax, legend=True,
                legend_kwds={'label': "Outbreak Risk Score (0-100)", 'orientation': "horizontal"},
                cmap='Reds', edgecolor='black', linewidth=0.5, missing_kwds={'color': 'lightgrey'})
    
    ax.set_title("National Dengue Outbreak Risk Map (Next Month Forecast)", fontsize=14, weight='bold')
    ax.set_axis_off()
    
    plt.tight_layout()
    plt.savefig('outputs/figures/india_risk_map.png', dpi=300)
    print("Saved GIS map to outputs/figures/india_risk_map.png")

if __name__ == "__main__":
    generate_gis_map()
