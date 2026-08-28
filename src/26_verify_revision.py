"""
26_verify_revision.py
=====================
Integrity check for the IJDSA revision package.

Confirms that (a) every headline number asserted in the manuscript matches the
artefact produced by the pipeline, (b) the deliverables exist and are readable,
and (c) no withdrawn claim from the original submission survives anywhere in the
revised text. Exits non-zero if any check fails.
"""

import json
import os
import re
import sys

from docx import Document

MD = "reports/MANUSCRIPT_IJDSA_R1.md"
REAL = "outputs/real"
PKG = "MMI_submission_package"

M = json.load(open(f"{REAL}/real_metrics.json"))
P = json.load(open(f"{REAL}/panel_provenance.json"))
TEXT = open(MD, encoding="utf-8").read()

ok, fail = [], []


def check(label, condition, detail=""):
    (ok if condition else fail).append(f"{label}{(' — ' + detail) if detail else ''}")


def near(a, b, tol=0.0006):
    return abs(a - b) <= tol


# --------------------------- headline numbers ---------------------------- #
F = M["forecasting"]
C = M["classification"]
B = M["between_state"]["mean_incidence"]
L = M["leakage_experiment"]

claims = [
    ("state climatology pooled R2 0.637", F["State climatology (training mean)"]["r2_log"], 0.637),
    ("NB GLM full pooled R2 0.607", F["Negative-binomial GLM (full)"]["r2_log"], 0.607),
    ("GBM multi-modal pooled R2 0.551", F["Gradient boosting (multi-modal)"]["r2_log"], 0.551),
    ("persistence pooled R2 0.550", F["Persistence (previous year)"]["r2_log"], 0.550),
    ("GBM history pooled R2 0.488", F["Gradient boosting (history only)"]["r2_log"], 0.488),
    ("climatology within-state R2 -0.002",
     F["State climatology (training mean)"]["r2_log_within_state"], -0.002),
    ("GBM within-state R2 -0.239",
     F["Gradient boosting (multi-modal)"]["r2_log_within_state"], -0.239),
    ("outbreak AUC 0.522", C["auc_roc"], 0.522),
    ("average precision 0.468", C["auprc"], 0.468),
    ("prevalence 0.452", C["auprc_baseline_prevalence"], 0.452),
    ("Brier 0.326", C["brier"], 0.326),
    ("Brier baseline 0.248", C["brier_baseline"], 0.248),
    ("urbanisation rho 0.635", B["urban_pct"]["rho"], 0.635),
    ("GDP rho 0.609", B["gdp_pc"]["rho"], 0.609),
    ("health index rho 0.159", B["health_index"]["rho"], 0.159),
    ("leakage-free R2 0.551", L["a_leakage_free_year_ahead"], 0.551),
    ("rolling-mean leaked R2 0.759", L["b_unshifted_rolling_mean"], 0.759),
    ("random-split R2 0.626", L["c_random_split_cv"], 0.626),
]
for label, actual, stated in claims:
    check(f"artefact matches manuscript: {label}", near(round(actual, 3), stated),
          f"artefact={actual:.4f} manuscript={stated}")
    check(f"manuscript text contains {stated}", f"{abs(stated):.3f}".lstrip("0") in TEXT
          or f"{stated:.3f}" in TEXT or f"{abs(stated):.3f}" in TEXT,
          f"looked for {stated:.3f}")

# --------------------------- panel facts --------------------------------- #
check("panel is 350 state-years", P["panel_state_years"] == 350 and "350 state-years" in TEXT)
check("panel is 35 states", P["states_complete_2015_2024"] == 35 and "35 states" in TEXT)
check("reconciliation 124/124 exact",
      M["dataset"]["provenance"]["exact_matches"] == 124
      and M["dataset"]["provenance"]["overlapping_state_years"] == 124
      and "124" in TEXT)
check("245 out-of-sample forecasts",
      F["Gradient boosting (multi-modal)"]["n_forecasts"] == 245 and "245" in TEXT)
check("West Bengal named as the excluded state",
      P["excluded_states"] == ["WEST BENGAL"] and "West Bengal" in TEXT)

# --------------------- withdrawn claims must not recur -------------------- #
# These may appear ONLY in Section 4.6, where they are explicitly withdrawn.
withdrawn_section = TEXT.split("### 4.6")[1] if "### 4.6" in TEXT else ""
body_without_withdrawal = TEXT.replace(withdrawn_section, "")
for bad, why in [
    ("0.892", "old synthetic R2"),
    ("0.936", "old synthetic AUC"),
    ("1,740", "old synthetic state-months"),
    ("74.0%", "old circular seasonality figure"),
    ("Field Scorecard", "withdrawn field tool"),
    ("month-ahead", "withdrawn monthly horizon claim"),
    ("four weeks of lead", "withdrawn lead-time claim"),
]:
    check(f"withdrawn claim absent from body: {why}", bad not in body_without_withdrawal,
          f"found '{bad}' outside Section 4.6")

# ---------------------------- deliverables -------------------------------- #
expected = [
    "Main_Manuscript_IJDSA_R1_clean.docx",
    "Main_Manuscript_IJDSA_R1_tracked.docx",
    "Response_to_Reviewers_IJDSA_R1.docx",
    "Supplementary_IJDSA_R1.docx",
    "Cover_Letter_IJDSA_R1.docx",
]
for f in expected:
    p = os.path.join(PKG, f)
    exists = os.path.exists(p) and os.path.getsize(p) > 8000
    check(f"deliverable present: {f}", exists)
    if exists:
        try:
            d = Document(p)
            check(f"deliverable opens: {f}", len(d.paragraphs) > 5)
        except Exception as e:
            check(f"deliverable opens: {f}", False, str(e))

# tracked changes really are tracked
import zipfile
tp = os.path.join(PKG, "Main_Manuscript_IJDSA_R1_tracked.docx")
if os.path.exists(tp):
    x = zipfile.ZipFile(tp).read("word/document.xml").decode("utf-8")
    n_ins, n_del = len(re.findall(r"<w:ins ", x)), len(re.findall(r"<w:del ", x))
    check("tracked file carries Word revisions", n_ins > 20 and n_del > 20,
          f"{n_ins} insertions, {n_del} deletions")
    check("deleted runs use w:delText",
          len(re.findall(r"<w:del [^>]*>(?:(?!</w:del>).)*?<w:t[ >]", x, re.S)) == 0)

# figures referenced by the manuscript exist
for n in range(1, 8):
    check(f"figure {n} rendered",
          any(f.startswith(f"fig{n}_") for f in os.listdir("outputs/figures_real")))

# --------------------------------- report --------------------------------- #
print(f"PASSED {len(ok)}")
print(f"FAILED {len(fail)}")
if fail:
    print("\nFailures:")
    for f in fail:
        print("  -", f)
    sys.exit(1)
print("\nAll integrity checks passed.")
