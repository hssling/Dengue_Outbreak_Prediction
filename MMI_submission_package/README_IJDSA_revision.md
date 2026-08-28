# IJDSA Revision — Submission Package

**Manuscript:** Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India
**Journal:** International Journal of Data Science and Analytics (Springer Nature)
**Manuscript ID:** 9abb84c1-1d65-44de-916a-fc708a733fe8

## Deliverables in this folder
| File | Purpose |
| :--- | :--- |
| `Main_Manuscript_IJDSA_double_column.docx` | **Primary** — editable two-column Word manuscript (full-width title/abstract banner, two-column body, full-width tables/figures). |
| `Main_Manuscript_IJDSA_twocolumn.pdf` | Typeset two-column PDF (reference rendering). |
| `Main_Manuscript_IJDSA_twocolumn.tex` | LaTeX source for the PDF. |
| `Response_to_Editor_IJDSA.docx` / `.md` | Cover note: addresses the double-column requirement and declares the rigour enhancements. |
| `Supplementary_IJDSA.docx` / `.md` | Full feature set, fold-level CV metrics, ablation, between-state association, sensitivity analyses. |

## What changed in this revision
1. **Formatting:** single-column → two-column layout (the editor's requirement).
2. **Genuine multi-modal model:** structural vulnerability indices (NITI Health Index, GDP per capita, SECI, urbanisation, density) are now model features.
3. **Reconciled, leakage-controlled metrics:** one 5-fold blocked TimeSeriesSplit pipeline — R² = 0.892 ± 0.028; outbreak AUC = 0.936 (temporal OOF).
4. **Honest driver decomposition + ablation** (new Table 2) and a between-state vulnerability analysis (GDP ρ = 0.51).
5. **Reference, figure and table indexing** audited: sequential first-appearance citation order; DOIs added; ≤6 authors then *et al.*; access dates on web sources.

## Reproducing every number, figure and table
```bash
python src/11_rigorous_pipeline.py        # retrain + metrics  -> outputs/models/rigorous_metrics.json
python src/12_generate_figures.py         # all figures        -> outputs/figures/*.png
python src/13_build_double_column_docx.py # two-column .docx
python src/14_build_latex_pdf.py          # two-column .tex + .pdf (pandoc + xelatex)
```
Source manuscript text: `reports/MANUSCRIPT_IJDSA.md`.
