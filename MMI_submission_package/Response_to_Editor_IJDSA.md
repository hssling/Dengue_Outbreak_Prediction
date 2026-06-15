# Response to the Editorial Office

**International Journal of Data Science and Analytics**

**Manuscript ID:** 9abb84c1-1d65-44de-916a-fc708a733fe8 (v1.0)
**Title:** Multi-Modal Machine Learning Framework for State-Level Dengue Outbreak Prediction in India

---

Dear Ms Pavithra K and the Editorial Team,

Thank you for the technical check and for the opportunity to revise our submission. We have addressed the required formatting point and, in the interest of scientific rigour, have also corrected and strengthened the methodological reporting. Both sets of changes are summarised below for full transparency.

## 1. Required formatting change

**Point raised:** *"As per the recent update in the journal, the manuscript should be provided in double-formatted column."*

**Action:** The manuscript has been reformatted into a **two-column layout**. We provide it in two compatible forms so the editorial office may use whichever is preferred:

- `Main_Manuscript_IJDSA_double_column.docx` — editable Microsoft Word file with a full-width title/abstract banner and a two-column body (tables and figures set full width for legibility).
- `Main_Manuscript_IJDSA_twocolumn.pdf` (with source `.tex`) — a typeset two-column PDF for reference.

No change was made to the scientific structure, section order, author list, or declarations.

## 2. Rigour enhancements (declared)

While preparing the revision we identified and corrected internal inconsistencies in the previous version and added analyses that materially strengthen the methods. We declare these candidly rather than silently incorporate them:

1. **Genuine integration of vulnerability indicators.** The structural indices (NITI Aayog Health Index, GDP per capita, SECI, urbanisation, density) are now included as model features and their true contribution is reported, rather than referenced only qualitatively.
2. **Corrected and reconciled performance.** All metrics now derive from a single, leakage-controlled 5-fold blocked TimeSeriesSplit pipeline and are mutually consistent across the abstract, results and tables: regression R² = 0.892 ± 0.028 (RMSE = 232 cases); outbreak-detection AUC = 0.936 (temporal out-of-fold).
3. **Transparent driver decomposition and ablation (new Table 3).** Grouped feature importance and a nested ablation now honestly attribute predictive power to seasonality (74%) and case momentum (21%), and locate the role of structural vulnerability at the between-state level (cumulative burden vs GDP per capita, Spearman ρ = 0.51).
4. **Expanded Methods.** Study design, data provenance, the full 25-feature specification, model configuration, validation procedure, software and reproducibility are now reported in full, with all code and the processed dataset openly available.
5. **Accurate dataset description.** The panel is now reported precisely as 1,740 state-months across 15 major dengue-endemic states (2015–2024); one missing Health Index value (West Bengal) is disclosed as median-imputed.

These changes make every reported statistic regenerable from the released pipeline and remove the inconsistencies that could have arisen at peer review. We would of course be glad to revert any of Section 2 to the prior text should the editorial office prefer a formatting-only revision; we judged that transparent strengthening best serves the journal and readers.

We confirm the work is original, not under consideration elsewhere, and approved by all authors. Thank you for your consideration.

Yours sincerely,

**Dr Siddalingaiah H S** (on behalf of all authors)
Professor, Department of Community Medicine,
Shridevi Institute of Medical Sciences and Research Hospital, Tumkur, Karnataka, India
E-mail: hssling@yahoo.com · ORCID: 0000-0002-4771-8285
