# Real Data Sources for Dengue Prediction

---

## 🌟 NIAID Data Ecosystem (NDE) - RECOMMENDED

**URL:** https://discovery.biothings.io/portal/nde

**What it is:**
- NIAID-funded data discovery platform
- Aggregates datasets from multiple repositories
- Includes infectious disease datasets (dengue, COVID, etc.)
- Schema-based metadata for easy discovery

**Related Portals:**
- **NIAID CREID:** https://discovery.biothings.io/portal/creid (emerging infectious diseases)
- **Outbreak.info:** https://discovery.biothings.io/portal/outbreak (outbreak data)
- **N3C:** https://discovery.biothings.io/portal/n3c (COVID-19)

**How to use:**
1. Visit the NDE portal
2. Search for "dengue" or "vector-borne disease"
3. Filter by data type (epidemiological, genomic, etc.)
4. Download or access linked datasets

---

## 1. Kaggle: Dengue Cases in India

**URL:** https://www.kaggle.com/datasets/thedevastator/dengue-cases-in-india

**Contents:**
- Dengue cases and deaths by state (2010-2022)
- Source: NVBDCP (National Vector Borne Diseases Control Programme)
- Format: CSV

**Download via Kaggle API:**
```bash
pip install kaggle
kaggle datasets download -d thedevastator/dengue-cases-in-india
```

---

## 2. Dataful.in: IDSP Weekly Reports

**URL:** https://dataful.in/

**Contents:**
- State/District/Disease-wise outbreak data
- 2009-2025 weekly reports
- Format: CSV, XLSX, Parquet

**Key Dataset:** "Master Data: IDSP Weekly Outbreak Reports"

---

## 3. DengAI Competition Data

**URL:** https://www.kaggle.com/c/dengai-predicting-disease-spread

**Contents:**
- Dengue cases for San Juan (Puerto Rico) and Iquitos (Peru)
- Climate variables (temp, precipitation, humidity)
- Weekly resolution, 20+ years

**Best for:** Testing climate-dengue ML methodology

---

## 4. Open Dengue (REAL GLOBAL DATA)

**GitHub:** https://github.com/OpenDengue/master-repo

**Figshare (Direct Download):** https://doi.org/10.6084/m9.figshare.24259573

**Website:** https://opendengue.org

**Contents:**
- Global dengue case counts (102 countries)
- Temporal coverage: 1924-2023
- Spatial resolution: Country/Admin1/Admin2
- Published in Scientific Data (Nature)

**Citation:**
> Clarke J, Lim A, Gupte P, Pigott DM, van Panhuis WG, Brady OJ. 
> A global dataset of publicly available dengue case count data. 
> Sci Data. 2024 Mar 14;11(1):296.

**Data Structure (in GitHub repo):**
```
data/
├── metadata/       # Source documentation
├── raw_data/       # Original source files
└── releases/       # Versioned datasets (V1.3 latest)
```

**How to download:**
1. Visit Figshare: https://doi.org/10.6084/m9.figshare.24259573
2. Download `ODcombined_V1.3.csv` (combined dataset)
3. Or use specific versions from GitHub releases

---

## 5. India Meteorological Department (IMD)

**URL:** https://mausam.imd.gov.in/

**Contents:**
- Historical temperature, rainfall, humidity
- Station and gridded data
- Monthly/daily resolution

---

## Instructions to Replace Synthetic Data

1. Download Kaggle "Dengue Cases in India" dataset
2. Acquire IMD climate data for matching states/years
3. Merge on state + year + month
4. Re-run pipeline:
   ```bash
   python src/02_preprocess.py
   python src/03_train_models.py
   python src/04_interpret.py
   ```

---

## Comparison of Global Dengue Databases

*Source: "A global dataset of publicly available dengue case count data" - OpenDengue*

| Source | Temporal Resolution | Temporal Coverage | Spatial Resolution | Spatial Coverage | Severity | Serotype | Lab Diag. | Mortality | Age | Gender |
|--------|---------------------|-------------------|-------------------|------------------|----------|----------|-----------|-----------|-----|--------|
| **OpenDengue** | W,M,Y | 1924–2023 | Country/A1/A2 | Global (102 countries) | No | No | No | No | No | No |
| **Tycho** | M,Y | 1960–2012 | National/A1/(A2) | Global (80 countries) | Yes | No | No | No | No | No |
| **PAHO PLISA** | W | 2014–current | National/A1 | Americas (56 countries) | Yes | Yes | Yes | Yes | No | No |
| **ECDC** | Y | 2008–current | National | Europe | No | No | No | Yes | Yes | Yes |
| **GIDEON** | W,M,Y* | 1780–current | National/subnational* | Global | Partial* | - | - | - | - | - |
| **ProMED-mail** | W,M,Y* | 1996–current | National/subnational* | Global | Partial* | - | - | - | - | - |

**Legend:**
- W = Weekly, M = Monthly, Y = Yearly
- A1 = Admin level 1 (state/province), A2 = Admin level 2 (district)
- *Partial or variable coverage

### Recommendation for India

For Indian dengue data, use:
1. **OpenDengue** - Best for historical trends (1924-2023)
2. **IDSP via Dataful** - Best for recent subnational data (2009-2025)
3. **Kaggle NVBDCP** - Best for quick state-level analysis

