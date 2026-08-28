"""
22_real_figures.py
==================
Publication figures for the IJDSA revision, generated exclusively from
outputs/real/real_metrics.json so that every plotted number is traceable to
the leakage-free pipeline in 21_real_analysis.py.

Figures (outputs/figures_real/):
  fig1_panel_provenance.png    observed national trend + NCVBDC reconciliation
  fig2_forecast_benchmarks.png pooled vs within-state skill of every model
  fig3_leakage_experiment.png  how much each design defect inflates R2
  fig4_classification.png      ROC, precision-recall and calibration
  fig5_between_state.png       structural gradient in observed incidence
  fig6_incidence_map.png       descriptive choropleth of observed incidence
  fig7_permutation_importance.png out-of-fold permutation importance
"""

import json
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9,
                     "axes.titlesize": 10, "axes.titleweight": "bold",
                     "savefig.bbox": "tight"})

FIG = "outputs/figures_real"
REAL = "outputs/real"
os.makedirs(FIG, exist_ok=True)
M = json.load(open(f"{REAL}/real_metrics.json"))
PANEL = pd.read_csv("data/processed/real_state_year_panel.csv")

C_OBS, C_MODEL, C_BASE, C_BAD = "#1b6ca8", "#e07b39", "#7f8c8d", "#c0392b"


# --------------------------------------------------------------------------- #
def fig1_provenance():
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6))
    nat = PANEL.groupby("year")["cases"].sum()
    ax[0].plot(nat.index, nat.values / 1000, "o-", color=C_OBS, lw=2, ms=5)
    ax[0].annotate("COVID-19 disruption\n(2020)", xy=(2020, nat.loc[2020] / 1000),
                   xytext=(2020.2, 130), fontsize=8, color=C_BAD,
                   arrowprops=dict(arrowstyle="->", color=C_BAD, lw=1.1))
    ax[0].set_xlabel("Year"); ax[0].set_ylabel("Reported cases (thousands)")
    ax[0].set_title("A  Observed national dengue burden, 35 states/UTs")

    rec = pd.read_csv(f"{REAL}/provenance_reconciliation.csv")
    ax[1].scatter(rec["ncvbdc_cases"] / 1000, rec["cases"] / 1000, s=18,
                  color=C_OBS, alpha=.75, edgecolor="white", linewidth=.4)
    lim = max(rec["ncvbdc_cases"].max(), rec["cases"].max()) / 1000 * 1.05
    ax[1].plot([0, lim], [0, lim], "--", color=C_BASE, lw=1)
    p = M["dataset"]["provenance"]
    ax[1].set_xlim(0, lim); ax[1].set_ylim(0, lim)
    ax[1].set_xlabel("NCVBDC bulletin (thousands)")
    ax[1].set_ylabel("Analysis panel (thousands)")
    ax[1].set_title(f"B  Independent reconciliation\n"
                    f"{p['exact_matches']}/{p['overlapping_state_years']} state-years exact "
                    f"({p['pct_exact']:.0f}%)")
    plt.tight_layout(); plt.savefig(f"{FIG}/fig1_panel_provenance.png", dpi=330); plt.close()
    print("  fig1_panel_provenance.png")


# --------------------------------------------------------------------------- #
def fig2_benchmarks():
    f = M["forecasting"]
    order = sorted(f, key=lambda k: -f[k]["r2_log"])
    pooled = [f[k]["r2_log"] for k in order]
    within = [f[k]["r2_log_within_state"] for k in order]
    y = np.arange(len(order))
    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    ax.barh(y - .2, pooled, .38, label="Pooled (between + within state)",
            color=[C_MODEL if "boosting" in k or "GLM" in k else C_BASE for k in order])
    ax.barh(y + .2, within, .38, label="Within-state (state mean removed)",
            color="#b8c6d1", edgecolor="#5b6b78", linewidth=.5)
    ax.axvline(0, color="black", lw=.9)
    ax.set_yticks(y); ax.set_yticklabels(order, fontsize=8.5)
    ax.invert_yaxis()
    ax.set_xlabel("R² (log₁₊ case scale), 245 out-of-sample state-year forecasts")
    ax.set_title("One-year-ahead forecasting skill: no model beats state climatology,\n"
                 "and no model explains within-state variation")
    ax.legend(loc="upper left", fontsize=8, framealpha=.95)
    plt.tight_layout(); plt.savefig(f"{FIG}/fig2_forecast_benchmarks.png", dpi=330); plt.close()
    print("  fig2_forecast_benchmarks.png")


# --------------------------------------------------------------------------- #
def fig3_leakage():
    L = M["leakage_experiment"]
    labs = ["Leakage-free\nyear-ahead\n(this study)",
            "Non-temporal\nrandom-split CV",
            "Unshifted 3-year\nrolling mean\n(target leakage)"]
    vals = [L["a_leakage_free_year_ahead"], L["c_random_split_cv"],
            L["b_unshifted_rolling_mean"]]
    cols = [C_OBS, "#e0a339", C_BAD]
    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.7))
    b = ax[0].bar(labs, vals, color=cols, width=.62)
    ax[0].axhline(vals[0], ls=":", color=C_OBS, lw=1.2)
    for i, (r, v) in enumerate(zip(b, vals)):
        x = r.get_x() + r.get_width() / 2
        ax[0].text(x, v + .04, f"{v:.3f}", ha="center", fontsize=9.5, fontweight="bold")
        if i:
            ax[0].text(x, v + .012, f"+{v - vals[0]:.3f}", color=C_BAD,
                       fontsize=8.5, ha="center")
    ax[0].set_ylabel("R² (log₁₊ scale)"); ax[0].set_ylim(0, .88)
    ax[0].set_title("A  Regression: inflation from design defects")
    ax[0].tick_params(axis="x", labelsize=8)

    a1, a2 = L["d_outbreak_auc_expanding_threshold"], L["d_outbreak_auc_lookahead_threshold"]
    b2 = ax[1].bar(["Expanding-window\nthreshold\n(this study)",
                    "Full-panel threshold\n(look-ahead)"], [a1, a2],
                   color=[C_OBS, C_BAD], width=.5)
    for r, v in zip(b2, [a1, a2]):
        ax[1].text(r.get_x() + r.get_width() / 2, v + .006, f"{v:.3f}",
                   ha="center", fontsize=9, fontweight="bold")
    ax[1].axhline(.5, ls="--", color=C_BASE, lw=1)
    ax[1].text(1.42, .505, "chance", fontsize=8, color=C_BASE, ha="right")
    ax[1].set_ylim(.45, .60); ax[1].set_ylabel("Outbreak-year AUC")
    ax[1].set_title("B  Classification: look-ahead thresholds")
    ax[1].tick_params(axis="x", labelsize=8)
    plt.tight_layout(); plt.savefig(f"{FIG}/fig3_leakage_experiment.png", dpi=330); plt.close()
    print("  fig3_leakage_experiment.png")


# --------------------------------------------------------------------------- #
def fig4_classification():
    C, roc = M["classification"], M["classification_roc"]
    pred = pd.read_csv(f"{REAL}/outbreak_predictions.csv")
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.5))

    ax[0].plot(roc["fpr"], roc["tpr"], color=C_MODEL, lw=2)
    ax[0].plot([0, 1], [0, 1], "--", color=C_BASE, lw=1)
    ax[0].set_xlabel("1 − specificity"); ax[0].set_ylabel("Sensitivity")
    ax[0].set_title(f"A  ROC — AUC = {C['auc_roc']:.3f}")

    from sklearn.metrics import precision_recall_curve
    pr, rc, _ = precision_recall_curve(pred["y"], pred["p"])
    ax[1].plot(rc, pr, color=C_MODEL, lw=2)
    ax[1].axhline(C["auprc_baseline_prevalence"], ls="--", color=C_BASE, lw=1)
    ax[1].text(.98, .04, f"prevalence = {C['auprc_baseline_prevalence']:.3f}",
               fontsize=8, color=C_BASE, ha="right")
    ax[1].set_ylim(0, 1.05)
    ax[1].set_xlabel("Recall"); ax[1].set_ylabel("Precision")
    ax[1].set_title(f"B  Precision–recall — AP = {C['auprc']:.3f}")

    cal = pd.DataFrame(C["calibration"])
    ax[2].plot([0, 1], [0, 1], "--", color=C_BASE, lw=1, label="Perfect")
    ax[2].plot(cal["mean_pred"], cal["obs_freq"], "o-", color=C_BAD, lw=1.8, ms=6,
               label="Observed")
    ax[2].set_xlabel("Mean predicted probability")
    ax[2].set_ylabel("Observed outbreak frequency")
    ax[2].set_title(f"C  Calibration — Brier = {C['brier']:.3f}\n"
                    f"(non-informative baseline {C['brier_baseline']:.3f})")
    ax[2].legend(fontsize=8, loc="upper left")
    for a in ax:
        a.set_xlim(-.02, 1.02)
    plt.tight_layout(); plt.savefig(f"{FIG}/fig4_classification.png", dpi=330); plt.close()
    print("  fig4_classification.png")


# --------------------------------------------------------------------------- #
def fig5_between_state():
    g = pd.read_csv(f"{REAL}/between_state_summary.csv")
    A = M["between_state"]["mean_incidence"]
    specs = [("urban_pct", "Urban population share, 2011 (%)", "A"),
             ("gdp_pc", "GDP per capita (₹)", "B"),
             ("health_index", "NITI Aayog Health Index 2019-20", "C")]
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.5))
    for k, (cov, xlab, tag) in enumerate(specs):
        s = g.dropna(subset=[cov, "mean_incidence"])
        ax[k].scatter(s[cov], s["mean_incidence"], s=34, color=C_OBS,
                      alpha=.8, edgecolor="white", linewidth=.5)
        sl, ic = np.polyfit(stats.rankdata(s[cov]), stats.rankdata(s["mean_incidence"]), 1)
        xr = np.linspace(s[cov].min(), s[cov].max(), 50)
        rk = np.interp(xr, np.sort(s[cov]), np.sort(stats.rankdata(s[cov])))
        yr = np.interp(sl * rk + ic, np.sort(stats.rankdata(s["mean_incidence"])),
                       np.sort(s["mean_incidence"]))
        ax[k].plot(xr, yr, color=C_MODEL, lw=1.8)
        a = A[cov]
        sig = "" if a["p"] >= .05 else " *"
        ax[k].set_xlabel(xlab); ax[k].set_yscale("log")
        ax[k].set_title(f"{tag}  ρ = {a['rho']:+.3f}{sig}\n95% CI [{a['ci_low']:+.2f}, "
                        f"{a['ci_high']:+.2f}], p = {a['p']:.4f}", fontsize=9)
        if k == 0:
            ax[k].set_ylabel("Mean annual incidence\nper 100 000 (log scale)")
    plt.tight_layout(); plt.savefig(f"{FIG}/fig5_between_state.png", dpi=330); plt.close()
    print("  fig5_between_state.png")


# --------------------------------------------------------------------------- #
def fig6_map():
    try:
        import geopandas as gpd
        shp = ("data/raw/data_related/ne_10m_admin_1_states_provinces/"
               "ne_10m_admin_1_states_provinces.shp")
        w = gpd.read_file(shp)
        ind = w[w["admin"] == "India"].copy()
        g = pd.read_csv(f"{REAL}/between_state_summary.csv")

        def canon(s):
            import re
            s = str(s).strip().upper().replace("&", "AND")
            s = re.sub(r"\s+", " ", s)
            return {"ORISSA": "ODISHA", "PONDICHERRY": "PUDUCHERRY",
                    "NCT OF DELHI": "DELHI", "UTTARANCHAL": "UTTARAKHAND",
                    "JAMMU AND KASHMIR": "JAMMU AND KASHMIR"}.get(s, s)

        ind["key"] = ind["name"].map(canon)
        g["key"] = g["state"].map(canon)
        m = ind.merge(g[["key", "mean_incidence"]], on="key", how="left")
        fig, ax = plt.subplots(figsize=(6.2, 6.8))
        m.plot(column="mean_incidence", cmap="YlOrRd", linewidth=.35,
               edgecolor="#666666", legend=True, ax=ax,
               missing_kwds={"color": "#eeeeee", "edgecolor": "#999999",
                             "hatch": "///", "label": "Not in panel"},
               legend_kwds={"label": "Mean annual incidence per 100 000 (2015–2024)",
                            "shrink": .55})
        ax.set_axis_off()
        ax.set_title("Observed mean annual dengue incidence, 2015–2024\n"
                     "(descriptive; not a forecast)", fontsize=10, fontweight="bold")
        plt.tight_layout(); plt.savefig(f"{FIG}/fig6_incidence_map.png", dpi=330); plt.close()
        print("  fig6_incidence_map.png")
    except Exception as e:
        print(f"  [skip] fig6_incidence_map.png ({e})")


# --------------------------------------------------------------------------- #
def fig7_importance():
    P = M["permutation_importance"]
    per = pd.Series(P["per_feature_mae_increase"]).sort_values()
    lbl = {"log_lag1": "Cases, previous year (log)",
           "log_lag2": "Cases, two years prior (log)",
           "growth": "Year-on-year growth",
           "prior_mean_log": "Mean of all prior years (log)",
           "prior_max_log": "Maximum of all prior years (log)",
           "health_index_2019_20": "NITI Health Index",
           "gdp_pc": "GDP per capita", "seci_score": "State Energy & Climate Index",
           "log_pop": "Population (log)", "urban_pct_2011": "Urban share",
           "density_2011": "Population density"}
    hist = set(["log_lag1", "log_lag2", "growth", "prior_mean_log", "prior_max_log"])
    fig, ax = plt.subplots(1, 2, figsize=(9.6, 3.8))
    ax[0].barh([lbl.get(i, i) for i in per.index], per.values,
               color=[C_MODEL if i in hist else "#5b8fb9" for i in per.index])
    ax[0].axvline(0, color="black", lw=.9)
    ax[0].set_xlabel("Increase in out-of-fold MAE (log scale) when permuted")
    ax[0].set_title("A  Out-of-fold permutation importance")
    ax[0].tick_params(axis="y", labelsize=8)

    G = P["grouped_percent"]
    ks = sorted(G, key=lambda k: -G[k])
    ax[1].bar(ks, [G[k] for k in ks], color=[C_MODEL, "#5b8fb9"], width=.5)
    for i, k in enumerate(ks):
        ax[1].text(i, G[k] + 1.2, f"{G[k]:.1f}%", ha="center", fontweight="bold", fontsize=9)
    ax[1].set_ylabel("Share of total permutation importance (%)")
    ax[1].set_ylim(0, max(G.values()) * 1.25)
    ax[1].set_title("B  Grouped predictive importance")
    ax[1].tick_params(axis="x", labelsize=8.5)
    plt.tight_layout(); plt.savefig(f"{FIG}/fig7_permutation_importance.png", dpi=330); plt.close()
    print("  fig7_permutation_importance.png")


if __name__ == "__main__":
    print("Generating figures from outputs/real/real_metrics.json ...")
    fig1_provenance(); fig2_benchmarks(); fig3_leakage()
    fig4_classification(); fig5_between_state(); fig6_map(); fig7_importance()
    print("Done ->", FIG)
