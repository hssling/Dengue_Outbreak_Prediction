# Data Sources and Provenance — IJDSA Revision (R1)

Every input to the revised analysis is listed here with its origin and a
SHA-256 checksum, so a reviewer can confirm they are working from byte-identical
source files.

## What is committed to this repository

Everything needed to reproduce **all** reported results is committed:

| Path | Contents |
| :--- | :--- |
| `data/processed/opendengue_india_admin1_year.csv` | The India admin-1 annual slice (672 records) extracted from the OpenDengue Spatial extract. This is the actual epidemiological input. |
| `data/processed/real_state_year_panel.csv` | The 350-state-year analysis panel with structural covariates merged. |
| `data/raw/data_related/*.csv` | NITI Health Index, state GDP per capita, State Energy & Climate Index, Census 2011 population/urban/density. |
| `data/raw/Dengue data India 2022-2025.xlsx` | NCVBDC annual bulletin used for the independent reconciliation. |
| `outputs/real/` | All metrics, the reconciliation table, per-state performance and out-of-sample forecasts. |
| `outputs/figures_real/` | All seven manuscript figures at 330 dpi. |

Running `python src/20_build_real_panel.py` uses the committed India slice and
therefore needs **no** large download. Delete that file to force a rebuild from
the original archive.

## What is NOT committed, and why

The OpenDengue extracts (~55 MB each), the Natural Earth boundary archive
(~15 MB) and the NITI source PDFs (~20 MB each) are third-party redistributions
and are excluded to keep the repository clonable. They are not required for
reproduction, only for re-deriving the committed India slice and for redrawing
the choropleth. Download them from the sources below; the checksums let you
verify you have the same versions we used.

## Checksums

| File | Description | Source | Size | SHA-256 |
| :--- | :--- | :--- | :--- | :--- |
| `data/raw/opendengue/Spatial_extract_V1_3.zip` | OpenDengue Spatial extract V1.3 | https://opendengue.org/data | 54.69 MB | `69f6f798bc732cf453e405725a1dab2faf595c37bc7b688e783f65ad2dd1e780` |
| `data/raw/opendengue/Temporal_extract_V1_3.zip` | OpenDengue Temporal extract V1.3 | https://opendengue.org/data | 54.87 MB | `7f5df2174404313a36596342bb26e4614c3c08577fab75550725e195326bcda6` |
| `data/raw/opendengue/National_extract_V1_3.zip` | OpenDengue National extract V1.3 | https://opendengue.org/data | 0.32 MB | `d4fa7b1a881481fd5323991cc7a23dbe690112e2c473898ceea76e1e9c85dc59` |
| `data/raw/Dengue data India 2022-2025.xlsx` | NCVBDC state-wise annual dengue bulletin | https://ncvbdc.mohfw.gov.in | 0.01 MB | `20ea27f41309f4be696729026a6d674de42fefa42f75660bba224a437b57cbe7` |
| `data/raw/data_related/health_index_2019_20.csv` | NITI Aayog Health Index 2019-20 (extracted) | https://niti.gov.in | 0.00 MB | `10bec405502ee4f6dc7a8aaf6a71336a2e5531574998db14719ac06aca2a0def` |
| `data/raw/data_related/gdp_per_capita_state.csv` | State GDP per capita | https://mospi.gov.in | 0.00 MB | `bb3cd6b01d9ae49e4ef15ec37fff14edfde1ff0afd8f21cc73f05ae076942d1d` |
| `data/raw/data_related/seci_round1.csv` | NITI State Energy & Climate Index round 1 | https://niti.gov.in | 0.00 MB | `bf9f1dacb0611e917e41374e628f15379a88de4f56fabb254285d8b79cd48182` |
| `data/raw/data_related/population_state.csv` | Census 2011 population, urban share, density | https://censusindia.gov.in | 0.00 MB | `837be7501ad652f4aa8519d593498ee8133ec1dbb1f96f6c630b13f13ccc521f` |
| `data/raw/data_related/ne_10m_admin_1_states_provinces.zip` | Natural Earth admin-1 boundaries 10m | https://naturalearthdata.com | 14.91 MB | `efc59726337323058f9446210adc96673179cd344e053666ee3d28cb58ba2b05` |

## Files deliberately retained but NOT on the analysis path

`src/01_fetch_data.py` contains `create_synthetic_dengue_data()`, the simulation
routine whose output (`data/raw/dengue_climate_india.csv`) was used in the
originally submitted analysis. Both are retained so that the audit reported in
Supplementary Table S6 can be independently verified:

```
python -c "import importlib.util,pandas as pd;   s=importlib.util.spec_from_file_location('f','src/01_fetch_data.py');   m=importlib.util.module_from_spec(s); s.loader.exec_module(m);   a=m.create_synthetic_dengue_data().sort_values(['state','year','month']).reset_index(drop=True);   b=pd.read_csv('data/raw/dengue_climate_india.csv').sort_values(['state','year','month']).reset_index(drop=True);   print('max abs diff:', max((a[c]-b[c]).abs().max() for c in ['cases','temperature_c','rainfall_mm','humidity_pct']))"
```

This prints `max abs diff: 0.0`, confirming that the previously submitted
dataset was simulated. Scripts `src/01`–`src/14` are superseded and must not be
used for any reported result.
