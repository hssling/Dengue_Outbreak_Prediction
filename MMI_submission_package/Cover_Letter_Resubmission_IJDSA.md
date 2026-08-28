**Dr Siddalingaiah H S**
Professor, Department of Community Medicine
Shridevi Institute of Medical Sciences and Research Hospital
Tumkur 572106, Karnataka, India
E-mail: hssling@yahoo.com · Tel.: +91-8941087719 · ORCID: 0000-0002-4771-8285

15 June 2026

Ms Pavithra K
Editorial Office
**International Journal of Data Science and Analytics**
Springer Nature

**Re: Resubmission of Manuscript ID 9abb84c1-1d65-44de-916a-fc708a733fe8 (v1.0)**
**"Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India"**

Dear Ms Pavithra K,

Thank you for the technical check of our manuscript and for the opportunity to revise it. We are pleased to resubmit the manuscript and confirm that we have addressed the formatting requirement. In the same revision, and in the interest of scientific rigour, we have also strengthened the methodological reporting; we declare both sets of changes openly below so that the editorial office and reviewers have a complete and transparent record.

**1. Required formatting change.** As requested ("the manuscript should be provided in double-formatted column"), the manuscript has been reformatted into a **two-column layout**, with a full-width title and abstract banner and a two-column body. We enclose it as an editable Microsoft Word file and, for reference, as a typeset two-column PDF with its LaTeX source.

**2. Methodological strengthening (declared).** While preparing the revision we identified and corrected internal inconsistencies and added analyses that materially improve the work:

- The socio-economic vulnerability indicators (NITI Aayog Health Index, GDP per capita, State Energy & Climate Index, urbanisation and population density) are now genuine model features, and their true contribution is reported.
- All performance metrics now derive from a single, leakage-controlled 5-fold blocked TimeSeriesSplit pipeline and are mutually consistent throughout: regression R² = 0.892 ± 0.028 (RMSE = 232 cases); outbreak-detection AUC = 0.936 (temporal out-of-fold).
- A transparent driver decomposition and a nested ablation (new table) honestly attribute predictive power to seasonality and case momentum, and locate the role of structural vulnerability at the between-state level (cumulative burden vs GDP per capita, Spearman ρ = 0.51).
- The Methods section has been expanded to report study design, data provenance, the full 25-feature specification, model configuration, validation, software and reproducibility; all code and the processed data are openly available.
- The dataset is now described precisely as 1,740 state-months across 15 major dengue-endemic states (May 2015–December 2024); the single missing Health Index value (West Bengal) is disclosed as median-imputed, with a sensitivity analysis confirming it is non-influential (ΔR² = 0.003).
- Citations, figures and tables have been re-indexed in sequential order of first appearance; reference metadata, DOIs and access dates have been verified.

These changes make every reported statistic reproducible from the released pipeline. Should the editorial office prefer a formatting-only revision, we would be glad to restore the prior Methods text; we judged that transparent strengthening best serves the journal and its readers.

**Declarations.** This work is original, has not been published elsewhere, and is not under consideration by another journal. All authors have approved the manuscript and this resubmission, and declare no competing interests. The study used only aggregated, anonymised, publicly available data and did not require ethics approval.

**Enclosures.** Two-column main manuscript (Word + PDF/LaTeX); Supplementary Material; this cover letter.

We thank you and the reviewers for your time and look forward to your decision.

Yours sincerely,

**Dr Siddalingaiah H S**
On behalf of the authors (Siddalingaiah H S, Sowjanya D, Rangaswamy H V)
