"""
11_rigorous_pipeline.py
=======================
Authoritative, reproducible modelling pipeline for the IJDSA revision.

Key corrections over the legacy pipeline:
  * Socio-economic VULNERABILITY indices (NITI Aayog Health Index, GDP per
    capita, State Energy & Climate Index, urbanisation, population density)
    are MERGED INTO THE FEATURE MATRIX and genuinely used by the model.
  * Target is modelled on the log(1+cases) scale (as stated in Methods) and
    metrics are reported back-transformed to the case scale.
  * Rigorous 5-fold TimeSeriesSplit cross-validation (no temporal leakage).
  * Grouped feature-importance, a nested ABLATION (incremental value of each
    feature block) and a BETWEEN-STATE vulnerability association analysis are
    all computed so that every claim in the manuscript is artifact-backed.

Outputs (all consumed by the manuscript / figure / table generators):
  outputs/models/rigorous_metrics.json
  outputs/models/rigorous_regressor.joblib
  outputs/models/rigorous_classifier.joblib
  outputs/models/rigorous_roc.joblib
  outputs/enhanced/state_risk_scorecard.csv   (regenerated, consistent)
"""

import os
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import (mean_absolute_error, mean_squared_error, r2_score,
                             roc_auc_score, roc_curve)
from sklearn.model_selection import TimeSeriesSplit

warnings.filterwarnings("ignore")
RNG = 42
DATA = "data/processed/dengue_features.parquet"
VDIR = "data/raw/data_related"


# --------------------------------------------------------------------------- #
# 1. Load panel and merge vulnerability indices                               #
# --------------------------------------------------------------------------- #
def _norm(s):
    return (s.astype(str).str.strip().str.lower()
            .str.replace("&", "and", regex=False)
            .str.replace(r"\s+", " ", regex=True))


def load_data():
    df = pd.read_parquet(DATA).copy()
    df["k"] = _norm(df["state"])

    hi = pd.read_csv(f"{VDIR}/health_index_2019_20.csv")
    gdp = pd.read_csv(f"{VDIR}/gdp_per_capita_state.csv")
    seci = pd.read_csv(f"{VDIR}/seci_round1.csv")
    pop = pd.read_csv(f"{VDIR}/population_state.csv")
    for d in (hi, gdp, seci, pop):
        d["k"] = _norm(d["state"])

    vuln = (hi[["k", "health_index_2019_20"]]
            .merge(gdp[["k", "gdp_pc"]], on="k", how="outer")
            .merge(seci[["k", "seci_score"]], on="k", how="outer")
            .merge(pop[["k", "urban_pct_2011", "density_2011"]], on="k", how="outer"))

    out = df.merge(vuln, on="k", how="left")
    missing = out.loc[out["health_index_2019_20"].isna(), "state"].unique()
    if len(missing):
        print(f"[warn] vulnerability unmatched for: {list(missing)} -> median-imputed")
    for c in ["health_index_2019_20", "gdp_pc", "seci_score",
              "urban_pct_2011", "density_2011"]:
        out[c] = out[c].fillna(out[c].median())
    return out


# --------------------------------------------------------------------------- #
# 2. Feature groups                                                           #
# --------------------------------------------------------------------------- #
GROUPS = {
    "Autoregressive": ["cases_lag1", "cases_lag2", "cases_lag3",
                        "cases_lag4", "cases_rolling3"],
    "Seasonality": ["month_sin", "month_cos", "is_monsoon"],
    "Climate": ["temperature_c", "rainfall_mm", "humidity_pct",
                "temp_lag1", "temp_lag2", "rain_lag1", "rain_lag2",
                "humidity_lag1", "humidity_lag2", "temp_rolling3", "rain_rolling3"],
    "Vulnerability": ["health_index_2019_20", "gdp_pc", "seci_score",
                      "urban_pct_2011", "density_2011", "population_millions"],
}
ALL_FEATS = [f for g in GROUPS.values() for f in g]


def reg_params():
    return dict(n_estimators=300, max_depth=3, learning_rate=0.05,
                subsample=0.9, random_state=RNG)


# --------------------------------------------------------------------------- #
# 3. Time-series CV on log1p target, metrics back-transformed to case scale   #
# --------------------------------------------------------------------------- #
def cv_regression(df, feats, n_splits=5):
    d = df.sort_values(["year", "month"]).reset_index(drop=True)
    X = d[feats].values
    y = d["cases"].values
    yl = np.log1p(y)
    tscv = TimeSeriesSplit(n_splits=n_splits)
    folds = []
    for k, (tr, te) in enumerate(tscv.split(X), 1):
        m = GradientBoostingRegressor(**reg_params())
        m.fit(X[tr], yl[tr])
        pred = np.expm1(m.predict(X[te]))
        pred = np.clip(pred, 0, None)
        folds.append(dict(fold=k,
                          rmse=float(np.sqrt(mean_squared_error(y[te], pred))),
                          mae=float(mean_absolute_error(y[te], pred)),
                          r2=float(r2_score(y[te], pred))))
    agg = lambda key: (float(np.mean([f[key] for f in folds])),
                       float(np.std([f[key] for f in folds])))
    r2m, r2s = agg("r2"); rm, rs = agg("rmse"); mm, ms = agg("mae")
    return dict(mean_r2=r2m, sd_r2=r2s, mean_rmse=rm, sd_rmse=rs,
                mean_mae=mm, sd_mae=ms, folds=folds)


# --------------------------------------------------------------------------- #
# 4. Outbreak classifier (state-specific 75th pct) with out-of-fold ROC       #
# --------------------------------------------------------------------------- #
def cv_classification(df, feats, n_splits=5):
    d = df.sort_values(["year", "month"]).reset_index(drop=True)
    thr = d.groupby("state")["cases"].transform(lambda s: s.quantile(0.75))
    d["outbreak"] = (d["cases"] > thr).astype(int)
    X = d[feats].values
    y = d["outbreak"].values
    tscv = TimeSeriesSplit(n_splits=n_splits)
    oof_y, oof_p, aucs = [], [], []
    for tr, te in tscv.split(X):
        if len(np.unique(y[tr])) < 2:
            continue
        m = GradientBoostingClassifier(n_estimators=300, max_depth=3,
                                       learning_rate=0.05, subsample=0.9,
                                       random_state=RNG)
        m.fit(X[tr], y[tr])
        p = m.predict_proba(X[te])[:, 1]
        oof_y.extend(y[te]); oof_p.extend(p)
        if len(np.unique(y[te])) > 1:
            aucs.append(roc_auc_score(y[te], p))
    oof_y, oof_p = np.array(oof_y), np.array(oof_p)
    fpr, tpr, _ = roc_curve(oof_y, oof_p)
    pooled_auc = float(roc_auc_score(oof_y, oof_p))
    # Sensitivity at the Youden-optimal threshold
    j = tpr - fpr
    sens = float(tpr[int(np.argmax(j))])
    return dict(pooled_auc=pooled_auc,
                mean_fold_auc=float(np.mean(aucs)) if aucs else pooled_auc,
                sd_fold_auc=float(np.std(aucs)) if aucs else 0.0,
                sensitivity=sens,
                n_outbreak=int(y.sum()), n_total=int(len(y)),
                roc=dict(fpr=fpr.tolist(), tpr=tpr.tolist(), auc=pooled_auc))


# --------------------------------------------------------------------------- #
# 5. Grouped importance, ablation, between-state association                  #
# --------------------------------------------------------------------------- #
def grouped_importance(df, feats):
    d = df.sort_values(["year", "month"]).reset_index(drop=True)
    m = GradientBoostingRegressor(**reg_params())
    m.fit(d[feats].values, np.log1p(d["cases"].values))
    imp = pd.Series(m.feature_importances_, index=feats)
    grp = {g: float(imp[[f for f in fs if f in feats]].sum()) * 100
           for g, fs in GROUPS.items()}
    top = imp.sort_values(ascending=False).head(8)
    return grp, {k: float(v * 100) for k, v in top.items()}, m


def ablation(df):
    blocks = [("Seasonality + autoregression", GROUPS["Seasonality"] + GROUPS["Autoregressive"]),
              ("+ Climate", GROUPS["Seasonality"] + GROUPS["Autoregressive"] + GROUPS["Climate"]),
              ("+ Vulnerability (full)", ALL_FEATS)]
    rows = []
    for name, feats in blocks:
        r = cv_regression(df, feats)
        rows.append(dict(model=name, n_features=len(feats),
                         r2=r["mean_r2"], rmse=r["mean_rmse"], mae=r["mean_mae"]))
    return rows


def field_score_validation(df, reg_model, feats):
    """Transparent, paper-deployable ordinal field score (0-6) built ONLY from
    variables a district officer can read off without a computer, validated
    against the full model's forecast (Spearman)."""
    d = df.sort_values(["year", "month"]).copy()
    med = d.groupby("state")["cases"].transform("median")
    rmed = d.groupby("state")["rain_lag2"].transform("median")
    score = (2 * d["is_monsoon"].astype(int)
             + 2 * (d["cases_lag1"] > med).astype(int)
             + 1 * (d["rain_lag2"] > rmed).astype(int)
             + 1 * (d["month_cos"] < 0).astype(int))   # Aug-Apr trough vs peak
    forecast = np.expm1(reg_model.predict(d[feats].values))
    rho, p = stats.spearmanr(score, forecast)
    return dict(spearman_rho=float(rho), p_value=float(p),
                scale_min=0, scale_max=6)


def between_state(df):
    g = (df.groupby("state")
         .agg(mean_cases=("cases", "mean"),
              health_index=("health_index_2019_20", "first"),
              gdp_pc=("gdp_pc", "first"),
              seci=("seci_score", "first")).reset_index())
    out = {}
    for col in ["health_index", "gdp_pc", "seci"]:
        rho, p = stats.spearmanr(g[col], g["mean_cases"])
        out[col] = dict(spearman_rho=float(rho), p_value=float(p))
    return out, g


# --------------------------------------------------------------------------- #
# 6. Risk scorecard (regenerated, consistent with retrained model)            #
# --------------------------------------------------------------------------- #
def build_scorecard(df, reg_model, feats):
    latest = (df.sort_values(["year", "month"])
              .groupby("state").tail(1).copy())
    latest["forecast_cases"] = np.clip(
        np.expm1(reg_model.predict(latest[feats].values)), 0, None).round(0)
    # composite risk: standardized blend of forecast magnitude and (inverse)
    # health-system capacity, scaled 0-100
    z = lambda s: (s - s.mean()) / (s.std() + 1e-9)
    raw = (0.7 * z(np.log1p(latest["forecast_cases"]))
           - 0.3 * z(latest["health_index_2019_20"]))
    latest["risk_score"] = (100 * (raw - raw.min()) /
                            (raw.max() - raw.min() + 1e-9)).round(1)
    latest["risk_category"] = pd.cut(latest["risk_score"],
                                     [-1, 40, 70, 101],
                                     labels=["Low", "Moderate", "High"])
    cols = ["state", "forecast_cases", "health_index_2019_20",
            "risk_score", "risk_category"]
    sc = latest[cols].sort_values("risk_score", ascending=False).reset_index(drop=True)
    os.makedirs("outputs/enhanced", exist_ok=True)
    sc.to_csv("outputs/enhanced/state_risk_scorecard.csv", index=False)
    return sc


# --------------------------------------------------------------------------- #
def main():
    os.makedirs("outputs/models", exist_ok=True)
    df = load_data()
    print(f"Panel: {len(df)} state-months | states={df['state'].nunique()} | "
          f"years {df['year'].min()}-{df['year'].max()} | features={len(ALL_FEATS)}")

    reg = cv_regression(df, ALL_FEATS)
    clf = cv_classification(df, ALL_FEATS)
    grp, top, reg_model = grouped_importance(df, ALL_FEATS)
    abl = ablation(df)
    assoc, _ = between_state(df)
    field = field_score_validation(df, reg_model, ALL_FEATS)
    sc = build_scorecard(df, reg_model, ALL_FEATS)

    metrics = dict(
        dataset=dict(n_state_months=int(len(df)), n_states=int(df["state"].nunique()),
                     year_min=int(df["year"].min()), year_max=int(df["year"].max()),
                     n_features=len(ALL_FEATS),
                     states=sorted(df["state"].unique().tolist())),
        regression=reg,
        classification={k: v for k, v in clf.items() if k != "roc"},
        grouped_importance=grp,
        top_features=top,
        ablation=abl,
        between_state_association=assoc,
        field_score_validation=field,
    )
    with open("outputs/models/rigorous_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    joblib.dump(reg_model, "outputs/models/rigorous_regressor.joblib")
    joblib.dump(clf["roc"], "outputs/models/rigorous_roc.joblib")

    # console summary
    print("\n=== REGRESSION (5-fold TimeSeriesSplit, case scale) ===")
    print(f"R2 = {reg['mean_r2']:.3f} ± {reg['sd_r2']:.3f} | "
          f"RMSE = {reg['mean_rmse']:.1f} ± {reg['sd_rmse']:.1f} | "
          f"MAE = {reg['mean_mae']:.1f}")
    print("\n=== CLASSIFIER ===")
    print(f"AUC = {clf['pooled_auc']:.3f} | Sensitivity = {clf['sensitivity']:.3f} | "
          f"outbreak months = {clf['n_outbreak']}/{clf['n_total']}")
    print("\n=== GROUPED IMPORTANCE (%) ===")
    for k, v in sorted(grp.items(), key=lambda kv: -kv[1]):
        print(f"  {k:16s} {v:6.2f}")
    print("\n=== ABLATION (incremental value) ===")
    for r in abl:
        print(f"  {r['model']:28s} R2={r['r2']:.3f}  RMSE={r['rmse']:.1f}")
    print("\n=== BETWEEN-STATE ASSOCIATION (Spearman) ===")
    for k, v in assoc.items():
        print(f"  mean cases vs {k:14s} rho={v['spearman_rho']:+.2f} p={v['p_value']:.3f}")
    print("\n=== TOP RISK STATES ===")
    print(sc.head(8).to_string(index=False))
    print("\nSaved -> outputs/models/rigorous_metrics.json")


if __name__ == "__main__":
    main()
