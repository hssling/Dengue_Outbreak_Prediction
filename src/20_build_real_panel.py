"""
20_build_real_panel.py
======================
Build the AUTHENTIC state-year dengue panel for the IJDSA revision.

This script replaces the synthetic development data (`src/01_fetch_data.py`,
`data/raw/dengue_climate_india.csv`) that was used in the originally submitted
analysis.  Nothing here is simulated, interpolated or temporally reconstructed:
every case count is an observed annual state total released by the Indian
Ministry of Health & Family Welfare (NCVBDC) and archived by OpenDengue.

Provenance
----------
Epidemiology : OpenDengue Spatial extract V1.3, records with
               adm_0_name == INDIA, S_res == Admin1, T_res == Year,
               UUID prefix MOH-IND (National Centre for Vector Borne
               Diseases Control annual state-wise returns), 2015-2024.
Reconciliation: NCVBDC state-wise annual bulletin
               (`data/raw/Dengue data India 2022-2025.xlsx`).
Structural   : NITI Aayog Health Index 2019-20; state GDP per capita;
               NITI State Energy & Climate Index round 1; Census 2011
               population, urban share and density.

Outputs
-------
data/processed/real_state_year_panel.csv   analysis panel
outputs/real/provenance_reconciliation.csv NCVBDC cross-check table
outputs/real/panel_provenance.json         counts, coverage, exclusions
"""

import csv
import io
import json
import os
import re
import zipfile

import numpy as np
import pandas as pd

OD_ZIP = "data/raw/opendengue/Spatial_extract_V1_3.zip"
OD_CACHE = "data/processed/opendengue_india_admin1_year.csv"
NCVBDC_XLSX = "data/raw/Dengue data India 2022-2025.xlsx"
VDIR = "data/raw/data_related"
OUTDIR = "outputs/real"
YEAR_MIN, YEAR_MAX = 2015, 2024

# Name harmonisation: OpenDengue admin-1 labels -> canonical state name.
_FIX = {
    "ORISSA": "ODISHA",
    "PONDICHERRY": "PUDUCHERRY",
    "J AND K": "JAMMU AND KASHMIR",
    "UTTRAKHAND": "UTTARAKHAND",
    "A AND N ISLAND": "ANDAMAN AND NICOBAR",
    "AANDN ISLAND": "ANDAMAN AND NICOBAR",
    "ANDAMAN AND NICOBAR ISLANDS": "ANDAMAN AND NICOBAR",
    "D AND N HAVELI": "DADRA AND NAGAR HAVELI",
    "DANDN HAVELI": "DADRA AND NAGAR HAVELI",
    "CHATTISGARH": "CHHATTISGARH",
    "DADRA AND NAGAR HAVELI AND DAMAN AND DIU": "DADRA AND NAGAR HAVELI",
    "NCT OF DELHI": "DELHI",
}


def canon(s):
    s = str(s).strip().upper().replace("\n", " ")
    s = re.sub(r"\s+", " ", s).replace("&", "AND")
    s = re.sub(r"\s+", " ", s).strip()
    return _FIX.get(s, s)


# --------------------------------------------------------------------------- #
def load_opendengue_admin1():
    """India admin-1 annual rows from the OpenDengue spatial extract.

    The upstream extract is ~500 MB uncompressed and is not redistributed with
    this repository. On first run the India slice is cached to
    `data/processed/opendengue_india_admin1_year.csv` (~40 kB), which IS
    committed, so reviewers can reproduce every result without downloading the
    full archive. Delete the cache to force a rebuild from the source zip.
    """
    if os.path.exists(OD_CACHE):
        d = pd.read_csv(OD_CACHE)
        print(f"[info] using committed India slice: {OD_CACHE} ({len(d)} rows)")
    elif os.path.exists(OD_ZIP):
        z = zipfile.ZipFile(OD_ZIP)
        name = z.namelist()[0]
        rows = []
        with z.open(name) as fh:
            rdr = csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8",
                                                  errors="replace"))
            for r in rdr:
                if (r.get("adm_0_name", "").strip().upper() == "INDIA"
                        and r.get("S_res") == "Admin1" and r.get("T_res") == "Year"):
                    rows.append(r)
        d = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(OD_CACHE), exist_ok=True)
        d.to_csv(OD_CACHE, index=False)
        print(f"[info] extracted India slice from {OD_ZIP} -> {OD_CACHE} "
              f"({len(d)} rows)")
    else:
        raise FileNotFoundError(
            f"Neither the cached India slice ({OD_CACHE}) nor the OpenDengue "
            f"source archive ({OD_ZIP}) is present. Download the Spatial "
            f"extract V1.3 from https://opendengue.org and place it at "
            f"{OD_ZIP}; see SOURCES.md for the expected checksum.")

    d["year"] = d["Year"].astype(int)
    d["cases"] = pd.to_numeric(d["dengue_total"], errors="coerce")
    d["state"] = d["adm_1_name"].map(canon)
    return d


def build_panel():
    raw = load_opendengue_admin1()
    prov = {"opendengue_india_admin1_year_rows": int(len(raw))}

    # Restrict to the official MOH/NCVBDC source and the study window.
    moh = raw[raw["UUID"].str.startswith("MOH-IND")].copy()
    moh = moh[(moh.year >= YEAR_MIN) & (moh.year <= YEAR_MAX)]
    prov["moh_rows_in_window"] = int(len(moh))
    prov["source_uuids"] = sorted(moh["UUID"].unique().tolist())

    # A state-year may appear under more than one MOH release; take the max of
    # duplicate releases (revised returns supersede provisional ones) rather
    # than summing, which would double-count.
    dup = int(moh.duplicated(["state", "year"], keep=False).sum())
    prov["duplicate_state_year_records_resolved"] = dup
    p = moh.groupby(["state", "year"], as_index=False)["cases"].max()

    piv = p.pivot(index="state", columns="year", values="cases")
    complete = piv[piv.notna().all(axis=1)].index.tolist()
    excluded = sorted(set(piv.index) - set(complete))
    prov["states_all_admin1"] = int(len(piv))
    prov["states_complete_2015_2024"] = int(len(complete))
    prov["excluded_states"] = excluded
    prov["exclusion_rule"] = (
        "A state/UT is eligible only if an observed NCVBDC annual total is "
        "present for every one of the 10 study years (2015-2024). No missing "
        "year was imputed, interpolated or carried forward."
    )
    prov["missing_years_by_excluded_state"] = {
        s: int(10 - piv.loc[s].notna().sum()) for s in excluded
    }

    panel = p[p.state.isin(complete)].copy().sort_values(["state", "year"])
    prov["panel_state_years"] = int(len(panel))
    prov["panel_states"] = int(panel.state.nunique())
    prov["zero_count_state_years"] = int((panel.cases == 0).sum())
    return panel, prov


# --------------------------------------------------------------------------- #
def merge_structural(panel):
    def rd(fname, cols):
        d = pd.read_csv(os.path.join(VDIR, fname))
        d["state"] = d["state"].map(canon)
        return d[["state"] + cols]

    hi = rd("health_index_2019_20.csv", ["health_index_2019_20"])
    gdp = rd("gdp_per_capita_state.csv", ["gdp_pc"])
    seci = rd("seci_round1.csv", ["seci_score"])
    pop = rd("population_state.csv", ["pop_2011", "urban_pct_2011", "density_2011"])

    out = (panel.merge(hi, on="state", how="left")
                .merge(gdp, on="state", how="left")
                .merge(seci, on="state", how="left")
                .merge(pop, on="state", how="left"))

    # Explicit missingness - nothing is silently imputed here.
    miss = {}
    for c in ["health_index_2019_20", "gdp_pc", "seci_score", "pop_2011"]:
        miss[c] = sorted(out.loc[out[c].isna(), "state"].unique().tolist())
    out["incidence_per_100k"] = out["cases"] / (out["pop_2011"] / 1e5)
    return out, miss


# --------------------------------------------------------------------------- #
def reconcile_ncvbdc(panel):
    """Cross-check the OpenDengue-derived panel against the NCVBDC bulletin."""
    x = pd.read_excel(NCVBDC_XLSX)
    x.columns = [str(c) for c in x.columns]
    hdr = x.iloc[0]

    # Columns alternate Cases (C) / Deaths (D) beneath each year header.
    year_cols, cur = {}, None
    for c in x.columns:
        if re.fullmatch(r"20\d\d\*?", c.strip()):
            cur = int(c.strip().rstrip("*"))
        if cur and str(hdr[c]).strip().upper() == "C":
            year_cols[cur] = c

    body = x.iloc[1:].copy()
    body["state"] = body["Affected States/UTs"].map(canon)
    recs = []
    for yr, col in sorted(year_cols.items()):
        if not (YEAR_MIN <= yr <= YEAR_MAX):
            continue
        v = pd.to_numeric(body[col], errors="coerce")
        for st, val in zip(body["state"], v):
            if pd.notna(val):
                recs.append(dict(state=st, year=yr, ncvbdc_cases=float(val)))

    nc = pd.DataFrame(recs)
    if nc.empty:
        return pd.DataFrame(), {}
    m = panel.merge(nc, on=["state", "year"], how="inner")
    m["difference"] = m["cases"] - m["ncvbdc_cases"]
    m["pct_difference"] = 100 * m["difference"] / m["ncvbdc_cases"].replace(0, np.nan)
    summary = dict(
        overlapping_state_years=int(len(m)),
        exact_matches=int((m["difference"].abs() < 0.5).sum()),
        pct_exact=float(100 * (m["difference"].abs() < 0.5).mean()) if len(m) else 0.0,
        median_abs_pct_difference=(float(m["pct_difference"].abs().median())
                                   if len(m) else None),
        overlap_years=sorted(int(y) for y in m["year"].unique()),
    )
    return m.sort_values(["year", "state"]), summary


# --------------------------------------------------------------------------- #
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    panel, prov = build_panel()
    panel, miss = merge_structural(panel)
    prov["structural_covariate_missing_states"] = miss

    rec, rsum = reconcile_ncvbdc(panel[["state", "year", "cases"]])
    prov["ncvbdc_reconciliation"] = rsum
    if not rec.empty:
        rec.to_csv(os.path.join(OUTDIR, "provenance_reconciliation.csv"), index=False)

    panel.to_csv("data/processed/real_state_year_panel.csv", index=False)
    with open(os.path.join(OUTDIR, "panel_provenance.json"), "w") as f:
        json.dump(prov, f, indent=2)

    print("=" * 68)
    print("AUTHENTIC STATE-YEAR PANEL")
    print("=" * 68)
    print(f"OpenDengue India admin-1 annual records : {prov['opendengue_india_admin1_year_rows']}")
    print(f"MOH/NCVBDC records {YEAR_MIN}-{YEAR_MAX}       : {prov['moh_rows_in_window']}")
    print(f"States/UTs with complete 10-year series  : {prov['states_complete_2015_2024']}")
    print(f"Analysis panel                           : {prov['panel_state_years']} state-years")
    print(f"Excluded (incomplete series)             : {len(prov['excluded_states'])}")
    print(f"Zero-count state-years                   : {prov['zero_count_state_years']}")
    print()
    print("National annual totals from the panel:")
    print(panel.groupby("year")["cases"].sum().astype(int).to_string())
    print()
    print("NCVBDC reconciliation:", json.dumps(rsum, indent=2))
    print()
    print("Structural covariate gaps:", json.dumps(miss, indent=2))
    print("\nSaved -> data/processed/real_state_year_panel.csv")


if __name__ == "__main__":
    main()
