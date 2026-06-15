"""
12_generate_figures.py
======================
Regenerate ALL publication figures from the rigorous artifacts so every figure
is numerically consistent with outputs/models/rigorous_metrics.json.

Figures produced (outputs/figures/):
  roc_curve.png              ROC of the temporal out-of-fold classifier
  feature_importance.png     Grouped driver hierarchy (true values)
  ablation.png               Incremental value of each feature block
  validation_scatter.png     Predicted vs observed (temporal holdout)
  risk_vs_vulnerability.png  State risk score vs NITI Health Index
  india_risk_map.png         Choropleth of state-level risk
"""
import json
import os
import warnings

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import importlib.util
spec = importlib.util.spec_from_file_location("rp", "src/11_rigorous_pipeline.py")
rp = importlib.util.module_from_spec(spec); spec.loader.exec_module(rp)

warnings.filterwarnings("ignore")
plt.style.use("seaborn-v0_8-whitegrid")
FIG = "outputs/figures"
os.makedirs(FIG, exist_ok=True)
M = json.load(open("outputs/models/rigorous_metrics.json"))
GCOL = {"Seasonality": "#2ecc71", "Autoregressive": "#9b59b6",
        "Climate": "#3498db", "Vulnerability": "#e74c3c"}


def fig_roc():
    roc = joblib.load("outputs/models/rigorous_roc.joblib")
    plt.figure(figsize=(7, 6))
    plt.plot(roc["fpr"], roc["tpr"], color="#e67e22", lw=2.2,
             label=f"ROC (AUC = {roc['auc']:.3f})")
    plt.plot([0, 1], [0, 1], "--", color="navy", lw=1.5)
    plt.xlim(0, 1); plt.ylim(0, 1.02)
    plt.xlabel("False Positive Rate (1 - Specificity)")
    plt.ylabel("True Positive Rate (Sensitivity)")
    plt.title("Outbreak Detection - Temporal Out-of-Fold ROC", fontsize=13)
    plt.legend(loc="lower right"); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(f"{FIG}/roc_curve.png", dpi=300); plt.close()
    print("  roc_curve.png")


def fig_importance():
    g = M["grouped_importance"]
    df = (pd.DataFrame({"Driver": list(g), "Impact (%)": list(g.values())})
          .sort_values("Impact (%)", ascending=False))
    plt.figure(figsize=(9, 5))
    sns.barplot(data=df, x="Impact (%)", y="Driver",
                palette=[GCOL[d] for d in df["Driver"]])
    for i, v in enumerate(df["Impact (%)"]):
        plt.text(v + 1, i, f"{v:.1f}%", va="center", fontweight="bold")
    plt.xlim(0, 100)
    plt.title("Hierarchy of Dengue Drivers (Gradient Boosting, grouped Gini importance)",
              fontsize=12)
    plt.xlabel("Relative contribution to model (%)"); plt.ylabel("")
    plt.tight_layout(); plt.savefig(f"{FIG}/feature_importance.png", dpi=300); plt.close()
    print("  feature_importance.png")


def fig_ablation():
    ab = pd.DataFrame(M["ablation"])
    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = np.arange(len(ab))
    ax1.bar(x - 0.2, ab["r2"], 0.4, color="#2c7fb8", label="R$^2$")
    ax1.set_ylabel("Cross-validated R$^2$", color="#2c7fb8")
    ax1.set_ylim(0.8, 0.95)
    ax2 = ax1.twinx()
    ax2.plot(x, ab["rmse"], "o-", color="#d95f0e", label="RMSE")
    ax2.set_ylabel("RMSE (cases)", color="#d95f0e")
    ax1.set_xticks(x); ax1.set_xticklabels(ab["model"], rotation=12, ha="right")
    plt.title("Ablation: Incremental Value of Each Feature Block "
              "(5-fold TimeSeriesSplit)", fontsize=12)
    fig.tight_layout(); plt.savefig(f"{FIG}/ablation.png", dpi=300); plt.close()
    print("  ablation.png")


def fig_validation():
    """Predicted vs observed on a temporal holdout (last 20% by date)."""
    df = rp.load_data().sort_values(["year", "month"]).reset_index(drop=True)
    n = len(df); cut = int(n * 0.8)
    from sklearn.ensemble import GradientBoostingRegressor
    m = GradientBoostingRegressor(**rp.reg_params())
    m.fit(df[rp.ALL_FEATS].values[:cut], np.log1p(df["cases"].values[:cut]))
    obs = df["cases"].values[cut:]
    pred = np.clip(np.expm1(m.predict(df[rp.ALL_FEATS].values[cut:])), 0, None)
    r2 = rp.r2_score(obs, pred)
    plt.figure(figsize=(7, 6))
    plt.scatter(obs, pred, s=28, alpha=0.5, color="#16a085", edgecolor="w")
    lim = max(obs.max(), pred.max()) * 1.05
    plt.plot([0, lim], [0, lim], "--", color="grey")
    plt.xlim(0, lim); plt.ylim(0, lim)
    plt.xlabel("Observed cases"); plt.ylabel("Predicted cases")
    plt.title(f"Temporal Holdout Calibration (R$^2$ = {r2:.2f})", fontsize=13)
    plt.tight_layout(); plt.savefig(f"{FIG}/validation_scatter.png", dpi=300); plt.close()
    print("  validation_scatter.png")


def fig_risk_vuln():
    sc = pd.read_csv("outputs/enhanced/state_risk_scorecard.csv")
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=sc, x="health_index_2019_20", y="risk_score",
                    hue="risk_category", s=130,
                    palette={"High": "#c0392b", "Moderate": "#e67e22", "Low": "#27ae60"})
    for _, r in sc.iterrows():
        plt.annotate(r["state"], (r["health_index_2019_20"], r["risk_score"]),
                     fontsize=7, alpha=0.7, xytext=(3, 3), textcoords="offset points")
    plt.xlabel("NITI Aayog Health Index 2019-20 (higher = stronger system)")
    plt.ylabel("Composite Outbreak Risk Score (0-100)")
    plt.title("Between-State Vulnerability vs Forecast Risk", fontsize=12)
    plt.tight_layout(); plt.savefig(f"{FIG}/risk_vs_vulnerability.png", dpi=300); plt.close()
    print("  risk_vs_vulnerability.png")


def fig_map():
    try:
        import geopandas as gpd
        sc = pd.read_csv("outputs/enhanced/state_risk_scorecard.csv")
        shp = gpd.read_file("data/raw/data_related/ne_10m_admin_1_states_provinces/"
                            "ne_10m_admin_1_states_provinces.shp")
        india = shp[shp["admin"] == "India"].copy()
        norm = lambda s: s.str.strip().str.lower().str.replace("&", "and", regex=False)
        india["k"] = norm(india["name"])
        sc["k"] = norm(sc["state"])
        india = india.merge(sc[["k", "risk_score"]], on="k", how="left")
        fig, ax = plt.subplots(figsize=(8, 9))
        india.plot(column="risk_score", cmap="OrRd", linewidth=0.4, edgecolor="grey",
                   legend=True, missing_kwds={"color": "#f0f0f0", "label": "No data"},
                   ax=ax)
        ax.set_title("National Dengue Outbreak Risk (state-level composite)", fontsize=13)
        ax.axis("off"); plt.tight_layout()
        plt.savefig(f"{FIG}/india_risk_map.png", dpi=300); plt.close()
        print("  india_risk_map.png")
    except Exception as e:
        print(f"  [skip] india_risk_map.png ({e})")


if __name__ == "__main__":
    print("Generating figures from rigorous artifacts...")
    fig_roc(); fig_importance(); fig_ablation()
    fig_validation(); fig_risk_vuln(); fig_map()
    print("Done.")
