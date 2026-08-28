# IJDSA Revision Package — Submission ID 9abb84c1-1d65-44de-916a-fc708a733fe8

Prepared 29 August 2026. Deadline 27 October 2026.

## Upload manifest

| Order | File | Springer upload item |
| :--- | :--- | :--- |
| 1 | `Cover_Letter_IJDSA_R1.docx` | Cover letter |
| 2 | `Main_Manuscript_IJDSA_R1_clean.docx` | Manuscript (clean, double-column) |
| 3 | `Main_Manuscript_IJDSA_R1_tracked.docx` | Manuscript (tracked changes) |
| 4 | `Response_to_Reviewers_IJDSA_R1.docx` | Point-by-point response (tabular) |
| 5 | `Supplementary_IJDSA_R1.docx` | Supplementary information |

Figures are embedded in the manuscript and also available individually in
`outputs/figures_real/` at 330 dpi should the journal request separate files.

## What changed, in one paragraph

The originally submitted analysis was run on a **synthetic development dataset**
(`data/raw/dengue_climate_india.csv`, bit-identical to
`create_synthetic_dengue_data()` in `src/01_fetch_data.py` under seed 42) and its
feature matrix contained an **unshifted rolling case mean**, i.e. direct target
leakage. Both reviewers identified this correctly. The reported R² = 0.892 and
AUC = 0.936 are withdrawn. The study has been rebuilt on an authenticated panel
of **350 state-years across 35 states/UTs (2015–2024)** from NCVBDC returns, with
**124/124 overlapping state-years reconciling exactly** against the official
bulletin. Under a leakage-free design no model beats state climatology,
within-state R² is ≤ 0 for every model, and outbreak classification is at chance.
The between-state structural gradient survives and strengthens.

## Reproducing every number

```
python src/20_build_real_panel.py     # panel + NCVBDC reconciliation
python src/21_real_analysis.py        # benchmarks, classification, leakage experiment
python src/22_real_figures.py         # all seven figures
python src/23_build_revision_docx.py  # clean + tracked manuscripts
python src/24_build_response_letter.py
python src/25_build_supplementary.py
python src/26_verify_revision.py      # 67 integrity checks, exits non-zero on failure
```

`src/26_verify_revision.py` cross-checks every headline number in the manuscript
against `outputs/real/real_metrics.json`, confirms the tracked file carries real
Word revisions, and asserts that no withdrawn claim (0.892, 0.936, 1,740
state-months, 74.0% seasonality, the field scorecard, month-ahead framing)
appears anywhere outside the section that explicitly withdraws it.

## Canonical vs superseded

**Canonical for this revision:** `src/20`–`src/26`,
`reports/MANUSCRIPT_IJDSA_R1.md`, `outputs/real/`, `outputs/figures_real/`.

**Superseded — do not cite or reuse:** `src/01`–`src/14`,
`reports/MANUSCRIPT_IJDSA.md`, `reports/MANUSCRIPT_FINAL.md`,
`outputs/models/rigorous_metrics.json`, `outputs/figures/`, and every
`Main_Manuscript_IJMR_*` / `Main_Manuscript_IJDSA_double_column.docx` file. These
rest on the synthetic panel. They are retained only so the audit trail in
Supplementary S6 can be verified.
