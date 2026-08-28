# IJDSA Revision (R1) — Upload Folder

**Submission ID 9abb84c1-1d65-44de-916a-fc708a733fe8 · Deadline 27 October 2026**

Everything in this folder — and **nothing outside it** — goes to the Springer portal.
The parent directory holds superseded IJMR/MMI drafts built on the withdrawn synthetic
panel; do not upload from there.

## Upload manifest

| # | File | Springer upload item |
| :--- | :--- | :--- |
| 1 | `Cover_Letter_IJDSA_R1.docx` | Cover letter |
| 2 | `Main_Manuscript_IJDSA_R1_clean.docx` | Manuscript — **main document** |
| 3 | `Main_Manuscript_IJDSA_R1_tracked.docx` | Manuscript — marked-up / tracked-changes copy |
| 4 | `Response_to_Reviewers_IJDSA_R1.docx` | Response to reviewers (point-by-point, 25 items) |
| 5 | `Supplementary_IJDSA_R1.docx` | Supplementary information (Tables S1–S6) |

Designate **#2** as the main manuscript, not #3. Both carry identical text; #3
additionally contains 88 insertions and 65 deletions as genuine Word revisions
(`w:ins` / `w:del`), so the editor can use Review → Accept/Reject normally.

**Not for upload:** this README, and `Response_to_Reviewers_IJDSA_R1.md` (a Markdown
mirror of #4 kept for version control).

## Optional alternative formats

The journal accepts Word or LaTeX. The Word file above is the primary submission; these
are provided in case they are requested.

| File | Purpose |
| :--- | :--- |
| `Main_Manuscript_IJDSA_R1.pdf` | Reading copy, rendered **from the clean .docx via Word**, so it is the exact layout the editor opens. Attach only if a PDF is asked for. |
| `Main_Manuscript_IJDSA_R1.tex` | Two-column LaTeX source, generated with pandoc. |
| `figures/Figure1.png` … `Figure7.png` | Figures for the LaTeX build, renamed to match manuscript numbering and referenced by **relative** path, so the bundle compiles anywhere. |

If submitting LaTeX, upload the `.tex` together with the whole `figures/` folder. No
LaTeX engine is installed in this project, so the `.tex` has not been compiled here; it
is provided as source and should be checked once before use. The PDF above is authoritative.

Figures are embedded in both manuscript files. If the journal later requests separate
figure files, they are in `outputs/figures_real/` at 330 dpi. Filenames do **not** match
figure numbers, because numbering follows order of first mention as the journal requires:

| Manuscript | Source file |
| :--- | :--- |
| Figure 1 | `fig1_panel_provenance.png` |
| Figure 2 | `fig2_forecast_benchmarks.png` |
| Figure 3 | `fig4_classification.png` |
| Figure 4 | `fig7_permutation_importance.png` |
| Figure 5 | `fig5_between_state.png` |
| Figure 6 | `fig6_incidence_map.png` |
| Figure 7 | `fig3_leakage_experiment.png` |

## What changed, in one paragraph

The originally submitted analysis was run on a **synthetic development dataset**
(`data/raw/dengue_climate_india.csv`, bit-identical to `create_synthetic_dengue_data()`
in `src/01_fetch_data.py` under seed 42) and its feature matrix contained an **unshifted
rolling case mean**, i.e. direct target leakage. Both reviewers identified this
correctly. The reported R² = 0.892 and AUC = 0.936 are withdrawn. The study is rebuilt
on an authenticated panel of **350 state-years across 35 states/UTs (2015–2024)** from
NCVBDC returns, with **124/124 overlapping state-years reconciling exactly** against the
official bulletin. Under a leakage-free design no model beats state climatology,
within-state R² is ≤ 0 for every model, and outbreak classification is at chance. The
between-state structural gradient survives and strengthens.

## Regenerating these five files

Run from the repository root:

```
python src/20_build_real_panel.py       # panel + NCVBDC reconciliation
python src/21_real_analysis.py          # benchmarks, classification, leakage experiment
python src/22_real_figures.py           # all seven figures
python src/23_build_revision_docx.py    # -> #2 and #3
python src/24_build_response_letter.py  # -> #4
python src/25_build_supplementary.py    # -> #5 and #1
python src/26_verify_revision.py        # 67 integrity checks
python src/27_audit_revision.py         # 37 adversarial checks
```

Both verification suites exit non-zero on failure. `26` cross-checks every headline
number in the manuscript against `outputs/real/real_metrics.json`, confirms the tracked
file carries real Word revisions, and asserts that no withdrawn claim (0.892, 0.936,
1,740 state-months, 74.0% seasonality, the field scorecard, month-ahead framing) appears
anywhere outside the section that explicitly withdraws it. `27` adds a
**future-information test** — it corrupts every observation at or after the target year
and asserts that no predictor changes — plus citation, sequential-numbering and
cross-document consistency checks.

## Canonical vs superseded

**Canonical:** `src/20`–`src/28`, `reports/MANUSCRIPT_IJDSA_R1.md`, `outputs/real/`,
`outputs/figures_real/`, this folder.

**Superseded — do not cite or reuse:** `src/01`–`src/14`, `reports/MANUSCRIPT_FINAL.md`,
`reports/MANUSCRIPT_IJDSA.md`, `outputs/models/`, `outputs/figures/`, `outputs/enhanced/`,
and every `Main_Manuscript_IJMR_*` / `*_MMI_*` /
`Main_Manuscript_IJDSA_double_column.docx` file in the parent directory. These rest on
the synthetic panel and are retained only so the audit trail in Supplementary Table S6
can be verified.
