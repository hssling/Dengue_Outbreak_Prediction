"""
21_real_analysis.py
===================
Leakage-free analysis of the authentic Indian state-year dengue panel.

Every design decision here responds to a specific reviewer requirement:

  R1-3, R1-4, R2-5   Strict forecast origin. Predictors for target year t are
                     built ONLY from information observable up to 31 Dec t-1.
                     No unshifted rolling statistic, no contemporaneous
                     covariate.
  R2-3               A full benchmark suite: persistence, state climatology,
                     global-year mean, and a negative-binomial GLM, evaluated
                     on identical expanding-window splits.
  R2-4               Spatial confounding addressed with a state-mean-only
                     baseline, within-state (demeaned) R2, and per-state
                     performance.
  R2-3, R2-5         Classification reported as AUC-ROC, AUPRC against
                     prevalence, Brier score and a calibration curve, with
                     outbreak thresholds AND decision cut-offs derived inside
                     the training window (expanding), never from the full panel.
  R1-6, R2-6         Out-of-fold permutation importance replaces impurity
                     ("Gini") importance.
  R1-C1, R2-6        Between-state associations use incidence, report bootstrap
                     CIs, and are adjusted for a surveillance-capacity proxy.
  R1-5, R1-10        A formal leakage experiment quantifies exactly how much
                     the two defects in the original submission inflate
                     apparent performance.

Outputs -> outputs/real/real_metrics.json (+ CSV companions)
"""

import json
import os
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             mean_absolute_error, r2_score, roc_auc_score,
                             roc_curve)
from sklearn.model_selection import KFold

warnings.filterwarnings("ignore")

PANEL = "data/processed/real_state_year_panel.csv"
OUTDIR = "outputs/real"
RNG = 42
FIRST_TEST_YEAR = 2018          # expanding-window origins 2018..2024
STRUCT = ["health_index_2019_20", "gdp_pc", "seci_score",
          "log_pop", "urban_pct_2011", "density_2011"]
AR = ["log_lag1", "log_lag2", "growth", "prior_mean_log", "prior_max_log"]
FULL = AR + STRUCT
GROUPS = {"Epidemiological history": AR, "Structural vulnerability": STRUCT}

GB = dict(n_estimators=300, max_depth=2, learning_rate=0.05,
          subsample=0.9, random_state=RNG)


# --------------------------------------------------------------------------- #
# Feature construction - strictly backward-looking                            #
# --------------------------------------------------------------------------- #
def build_features(d):
    """All predictors for target year t use only observations up to t-1."""
    d = d.sort_values(["state", "year"]).copy()
    g = d.groupby("state")["cases"]
    d["lag1"] = g.shift(1)
    d["lag2"] = g.shift(2)
    d["log_lag1"] = np.log1p(d["lag1"])
    d["log_lag2"] = np.log1p(d["lag2"])
    d["growth"] = d["log_lag1"] - d["log_lag2"]
    # Expanding summaries of the *past only* (shift(1) before expanding).
    past = g.shift(1)
    d["prior_mean_log"] = np.log1p(
        past.groupby(d["state"]).expanding(min_periods=1).mean()
            .reset_index(level=0, drop=True))
    d["prior_max_log"] = np.log1p(
        past.groupby(d["state"]).expanding(min_periods=1).max()
            .reset_index(level=0, drop=True))

    # Structural covariates are time-invariant; median-impute the few UT gaps
    # and flag them so the imputation is auditable rather than silent.
    d["structural_imputed"] = d[STRUCT[:3]].isna().any(axis=1).astype(int)
    d["log_pop"] = np.log(d["pop_2011"])
    for c in STRUCT:
        d[c] = d[c].fillna(d[c].median())
    return d


# --------------------------------------------------------------------------- #
# Benchmark suite, expanding window                                           #
# --------------------------------------------------------------------------- #
def _nb_glm(tr, te, feats):
    """Negative-binomial GLM with a log-population offset (R2-3)."""
    import statsmodels.api as sm
    Xtr = sm.add_constant(tr[feats], has_constant="add")
    Xte = sm.add_constant(te[feats], has_constant="add")
    Xte = Xte.reindex(columns=Xtr.columns, fill_value=0.0)
    # `log_pop` is the imputation-complete population column; the raw
    # `pop_2011` still carries the UT gaps and would produce a NaN offset.
    off_tr = tr["log_pop"].values
    off_te = te["log_pop"].values
    m = sm.GLM(tr["cases"].values, Xtr.values,
               family=sm.families.NegativeBinomial(alpha=1.0),
               offset=off_tr).fit(maxiter=200)
    mu = m.predict(Xte.values, offset=off_te)
    return np.log1p(np.clip(mu, 0, None))


def forecast_benchmarks(d):
    """One-year-ahead forecasts from every model on identical splits."""
    recs, preds = [], []
    for ty in range(FIRST_TEST_YEAR, d.year.max() + 1):
        tr = d[(d.year < ty) & d[FULL].notna().all(axis=1)]
        te = d[(d.year == ty) & d[FULL].notna().all(axis=1)]
        if len(tr) < 20 or len(te) == 0:
            continue
        y = np.log1p(te["cases"].values)

        # Training-window state climatology (the "state mean only" baseline).
        smean = tr.groupby("state")["cases"].mean()
        gmean = tr["cases"].mean()

        P = {}
        P["Persistence (previous year)"] = te["log_lag1"].values
        P["State climatology (training mean)"] = np.log1p(
            te["state"].map(smean).fillna(gmean).values)
        P["Global annual mean"] = np.full(len(te), np.log1p(gmean))
        P["Negative-binomial GLM (history)"] = _nb_glm(tr, te, ["log_lag1", "log_lag2"])
        P["Negative-binomial GLM (full)"] = _nb_glm(tr, te, ["log_lag1", "log_lag2"] + STRUCT)

        m1 = GradientBoostingRegressor(**GB).fit(tr[AR].values, np.log1p(tr["cases"].values))
        P["Gradient boosting (history only)"] = m1.predict(te[AR].values)
        m2 = GradientBoostingRegressor(**GB).fit(tr[FULL].values, np.log1p(tr["cases"].values))
        P["Gradient boosting (multi-modal)"] = m2.predict(te[FULL].values)

        for name, p in P.items():
            p = np.nan_to_num(p, nan=np.log1p(gmean), posinf=np.log1p(gmean), neginf=0.0)
            recs.append(dict(year=ty, model=name, n=len(te),
                             y=y.tolist(), pred=p.tolist(),
                             state=te["state"].tolist(),
                             smean_log=np.log1p(te["state"].map(smean)
                                                .fillna(gmean).values).tolist()))
            preds.append(pd.DataFrame(dict(year=ty, model=name,
                                           state=te["state"].values,
                                           y_log=y, pred_log=p,
                                           cases=te["cases"].values)))
    return recs, pd.concat(preds, ignore_index=True)


def score_pooled(recs):
    """Pooled metrics plus the within-state (demeaned) R2 that R2-4 asks for."""
    out = {}
    for model in sorted({r["model"] for r in recs}):
        rs = [r for r in recs if r["model"] == model]
        y = np.concatenate([r["y"] for r in rs])
        p = np.concatenate([r["pred"] for r in rs])
        sm = np.concatenate([r["smean_log"] for r in rs])
        cases = np.expm1(y)
        pcase = np.clip(np.expm1(p), 0, None)
        per_year = [float(r2_score(np.array(r["y"]), np.array(r["pred"])))
                    for r in rs if len(set(r["y"])) > 1]
        out[model] = dict(
            r2_log=float(r2_score(y, p)),
            r2_log_within_state=float(r2_score(y - sm, p - sm)),
            mae_log=float(mean_absolute_error(y, p)),
            mae_cases=float(mean_absolute_error(cases, pcase)),
            rmse_cases=float(np.sqrt(np.mean((cases - pcase) ** 2))),
            mean_per_year_r2=float(np.mean(per_year)) if per_year else None,
            sd_per_year_r2=float(np.std(per_year)) if per_year else None,
            n_forecasts=int(len(y)),
        )
    return out


# --------------------------------------------------------------------------- #
# Outbreak-year classification, everything estimated inside the training window
# --------------------------------------------------------------------------- #
def classification(d, lookahead_threshold=False):
    oy, op, rows = [], [], []
    full_thr = d.groupby("state")["cases"].quantile(0.75)   # look-ahead variant
    cuts = []
    for ty in range(FIRST_TEST_YEAR, d.year.max() + 1):
        tr = d[(d.year < ty) & d[FULL].notna().all(axis=1)].copy()
        te = d[(d.year == ty) & d[FULL].notna().all(axis=1)].copy()
        if len(tr) < 20 or len(te) == 0:
            continue
        thr = full_thr if lookahead_threshold else tr.groupby("state")["cases"].quantile(0.75)
        gthr = (d if lookahead_threshold else tr)["cases"].quantile(0.75)
        tr["ob"] = (tr["cases"] > tr["state"].map(thr).fillna(gthr)).astype(int)
        te["ob"] = (te["cases"] > te["state"].map(thr).fillna(gthr)).astype(int)
        if tr["ob"].nunique() < 2:
            continue
        clf = GradientBoostingClassifier(**GB).fit(tr[FULL].values, tr["ob"].values)

        # Decision cut-off chosen on the TRAINING data only (R2-5).
        ptr = clf.predict_proba(tr[FULL].values)[:, 1]
        fpr, tpr, thrs = roc_curve(tr["ob"].values, ptr)
        cut = float(thrs[int(np.argmax(tpr - fpr))])
        cuts.append(cut)

        pte = clf.predict_proba(te[FULL].values)[:, 1]
        oy.extend(te["ob"].tolist()); op.extend(pte.tolist())
        rows.append(pd.DataFrame(dict(year=ty, state=te["state"].values,
                                      y=te["ob"].values, p=pte, cut=cut)))
    oy, op = np.array(oy), np.array(op)
    R = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    if len(np.unique(oy)) < 2:
        return dict(error="single class"), R

    yhat = (R["p"].values >= R["cut"].values).astype(int)
    tp = int(((yhat == 1) & (oy == 1)).sum()); fp = int(((yhat == 1) & (oy == 0)).sum())
    fn = int(((yhat == 0) & (oy == 1)).sum()); tn = int(((yhat == 0) & (oy == 0)).sum())
    prev = float(oy.mean())

    # Calibration curve (quantile bins, so each bin is populated).
    qs = pd.qcut(op, 5, duplicates="drop")
    cal = (pd.DataFrame(dict(p=op, y=oy, b=qs)).groupby("b", observed=True)
           .agg(mean_pred=("p", "mean"), obs_freq=("y", "mean"), n=("y", "size")))
    fpr, tpr, _ = roc_curve(oy, op)
    return dict(
        auc_roc=float(roc_auc_score(oy, op)),
        auprc=float(average_precision_score(oy, op)),
        auprc_baseline_prevalence=prev,
        brier=float(brier_score_loss(oy, op)),
        brier_baseline=float(np.mean((prev - oy) ** 2)),
        sensitivity=float(tp / (tp + fn)) if tp + fn else None,
        specificity=float(tn / (tn + fp)) if tn + fp else None,
        ppv=float(tp / (tp + fp)) if tp + fp else None,
        n=int(len(oy)), n_outbreak=int(oy.sum()),
        mean_training_cutoff=float(np.mean(cuts)),
        calibration=[dict(mean_pred=float(r.mean_pred), obs_freq=float(r.obs_freq),
                          n=int(r.n)) for r in cal.itertuples()],
        roc=dict(fpr=fpr.tolist(), tpr=tpr.tolist()),
    ), R


# --------------------------------------------------------------------------- #
# Out-of-fold permutation importance (R1-6, R2-6)                             #
# --------------------------------------------------------------------------- #
def oof_permutation_importance(d, n_repeats=30):
    rng = np.random.default_rng(RNG)
    base_err, feat_err = [], {f: [] for f in FULL}
    for ty in range(FIRST_TEST_YEAR, d.year.max() + 1):
        tr = d[(d.year < ty) & d[FULL].notna().all(axis=1)]
        te = d[(d.year == ty) & d[FULL].notna().all(axis=1)]
        if len(tr) < 20 or len(te) == 0:
            continue
        m = GradientBoostingRegressor(**GB).fit(tr[FULL].values, np.log1p(tr["cases"].values))
        y = np.log1p(te["cases"].values)
        X = te[FULL].values.copy()
        base = mean_absolute_error(y, m.predict(X))
        base_err.append(base)
        for j, f in enumerate(FULL):
            errs = []
            for _ in range(n_repeats):
                Xp = X.copy()
                Xp[:, j] = rng.permutation(Xp[:, j])
                errs.append(mean_absolute_error(y, m.predict(Xp)))
            feat_err[f].append(np.mean(errs) - base)
    imp = {f: float(np.mean(v)) for f, v in feat_err.items()}
    tot = sum(max(v, 0) for v in imp.values()) or 1.0
    grouped = {g: float(100 * sum(max(imp[f], 0) for f in fs) / tot)
               for g, fs in GROUPS.items()}
    return dict(baseline_mae_log=float(np.mean(base_err)),
                per_feature_mae_increase=imp,
                grouped_percent=grouped)


# --------------------------------------------------------------------------- #
# Between-state structural associations (R1-C1, R2-6)                         #
# --------------------------------------------------------------------------- #
def _boot_spearman(x, y, n=4000):
    rng = np.random.default_rng(RNG)
    idx = np.arange(len(x))
    rs = []
    for _ in range(n):
        s = rng.choice(idx, len(idx), replace=True)
        if len(np.unique(x[s])) < 3 or len(np.unique(y[s])) < 3:
            continue
        rs.append(stats.spearmanr(x[s], y[s]).statistic)
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def _partial_spearman(x, y, z):
    """Spearman of x,y adjusting for z, via residuals of rank regression."""
    rx, ry, rz = (stats.rankdata(v) for v in (x, y, z))
    Z = np.column_stack([np.ones_like(rz), rz])
    bx = np.linalg.lstsq(Z, rx, rcond=None)[0]
    by = np.linalg.lstsq(Z, ry, rcond=None)[0]
    ex, ey = rx - Z @ bx, ry - Z @ by
    r, p = stats.pearsonr(ex, ey)
    return float(r), float(p)


def between_state(d):
    g = (d.groupby("state")
         .agg(mean_cases=("cases", "mean"),
              cumulative_cases=("cases", "sum"),
              mean_incidence=("incidence_per_100k", "mean"),
              health_index=("health_index_2019_20", "first"),
              gdp_pc=("gdp_pc", "first"),
              seci=("seci_score", "first"),
              urban_pct=("urban_pct_2011", "first"),
              density=("density_2011", "first"),
              imputed=("structural_imputed", "max"))
         .reset_index())
    g = g[g["imputed"] == 0]                     # observed covariates only
    out = {}
    for outcome in ["mean_incidence", "mean_cases", "cumulative_cases"]:
        res = {}
        for cov in ["health_index", "gdp_pc", "seci", "urban_pct", "density"]:
            sub = g.dropna(subset=[cov, outcome])
            r, p = stats.spearmanr(sub[cov], sub[outcome])
            lo, hi = _boot_spearman(sub[cov].values, sub[outcome].values)
            res[cov] = dict(rho=float(r), p=float(p), ci_low=lo, ci_high=hi, n=int(len(sub)))
        out[outcome] = res

    # Surveillance-intensity adjustment: the Health Index is the best available
    # proxy for a state's detection/reporting capacity (R2-6).
    sub = g.dropna(subset=["gdp_pc", "mean_incidence", "health_index"])
    r_adj, p_adj = _partial_spearman(sub["gdp_pc"].values,
                                     sub["mean_incidence"].values,
                                     sub["health_index"].values)
    out["gdp_incidence_adjusted_for_health_index"] = dict(
        partial_rho=r_adj, p=p_adj, n=int(len(sub)),
        note="Health Index used as a proxy for surveillance/detection capacity.")
    return out, g


# --------------------------------------------------------------------------- #
# Formal leakage experiment (R1-3, R1-5, R1-10)                               #
# --------------------------------------------------------------------------- #
def leakage_experiment(d):
    """Quantify, on identical real data, how much each defect inflates R2."""
    res = {}

    # (a) Corrected design - the paper's primary specification.
    recs, _ = forecast_benchmarks(d)
    res["a_leakage_free_year_ahead"] = score_pooled(recs)["Gradient boosting (multi-modal)"]["r2_log"]

    # (b) Direct target leakage: a 3-year rolling mean that INCLUDES year t,
    #     reproducing `cases_rolling3` from the original submission.
    dl = d.copy()
    dl["roll3_incl_t"] = np.log1p(
        dl.groupby("state")["cases"].rolling(3, min_periods=1).mean()
          .reset_index(level=0, drop=True))
    feats = FULL + ["roll3_incl_t"]
    ys, ps = [], []
    for ty in range(FIRST_TEST_YEAR, dl.year.max() + 1):
        tr = dl[(dl.year < ty) & dl[feats].notna().all(axis=1)]
        te = dl[(dl.year == ty) & dl[feats].notna().all(axis=1)]
        if len(tr) < 20 or len(te) == 0:
            continue
        m = GradientBoostingRegressor(**GB).fit(tr[feats].values, np.log1p(tr["cases"].values))
        ys.append(np.log1p(te["cases"].values)); ps.append(m.predict(te[feats].values))
    res["b_unshifted_rolling_mean"] = float(r2_score(np.concatenate(ys), np.concatenate(ps)))

    # (c) Non-temporal random-split CV on the same features (no time ordering).
    dd = d[d[FULL].notna().all(axis=1)]
    X, y = dd[FULL].values, np.log1p(dd["cases"].values)
    kf, ys, ps = KFold(5, shuffle=True, random_state=RNG), [], []
    for tr, te in kf.split(X):
        m = GradientBoostingRegressor(**GB).fit(X[tr], y[tr])
        ys.append(y[te]); ps.append(m.predict(X[te]))
    res["c_random_split_cv"] = float(r2_score(np.concatenate(ys), np.concatenate(ps)))

    # (d) Look-ahead outbreak threshold vs expanding threshold.
    hon, _ = classification(d, lookahead_threshold=False)
    look, _ = classification(d, lookahead_threshold=True)
    res["d_outbreak_auc_expanding_threshold"] = hon.get("auc_roc")
    res["d_outbreak_auc_lookahead_threshold"] = look.get("auc_roc")
    return res


# --------------------------------------------------------------------------- #
def main():
    os.makedirs(OUTDIR, exist_ok=True)
    d = build_features(pd.read_csv(PANEL))

    recs, preds = forecast_benchmarks(d)
    scores = score_pooled(recs)
    clf, cR = classification(d)
    perm = oof_permutation_importance(d)
    assoc, gstate = between_state(d)
    leak = leakage_experiment(d)

    # Per-state performance for the best model and the climatology baseline.
    best = "Gradient boosting (multi-modal)"
    ps = preds[preds.model.isin([best, "State climatology (training mean)",
                                 "Persistence (previous year)"])]
    per_state = (ps.groupby(["model", "state"])
                 .apply(lambda t: pd.Series(dict(
                     mae_log=float(mean_absolute_error(t.y_log, t.pred_log)),
                     n=int(len(t)))), include_groups=False)
                 .reset_index())
    per_state.to_csv(f"{OUTDIR}/per_state_performance.csv", index=False)
    preds.to_csv(f"{OUTDIR}/forecasts_out_of_sample.csv", index=False)
    gstate.to_csv(f"{OUTDIR}/between_state_summary.csv", index=False)
    if not cR.empty:
        cR.to_csv(f"{OUTDIR}/outbreak_predictions.csv", index=False)

    prov = json.load(open(f"{OUTDIR}/panel_provenance.json"))
    metrics = dict(
        dataset=dict(state_years=int(len(d)), states=int(d.state.nunique()),
                     year_min=int(d.year.min()), year_max=int(d.year.max()),
                     modelling_rows=int(d[FULL].notna().all(axis=1).sum()),
                     forecast_origins=list(range(FIRST_TEST_YEAR, int(d.year.max()) + 1)),
                     provenance=prov["ncvbdc_reconciliation"]),
        forecasting=scores,
        classification={k: v for k, v in clf.items() if k != "roc"},
        classification_roc=clf.get("roc"),
        permutation_importance=perm,
        between_state=assoc,
        leakage_experiment=leak,
    )
    with open(f"{OUTDIR}/real_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    # ------------------------------ report ------------------------------- #
    print("=" * 74)
    print(f"ONE-YEAR-AHEAD FORECASTING  |  {metrics['dataset']['states']} states, "
          f"origins {FIRST_TEST_YEAR}-{d.year.max()}")
    print("=" * 74)
    tab = (pd.DataFrame(scores).T
           .sort_values("r2_log", ascending=False)
           [["r2_log", "r2_log_within_state", "mae_log", "mae_cases", "rmse_cases", "n_forecasts"]])
    print(tab.round(3).to_string())
    print("\n=== OUTBREAK-YEAR CLASSIFICATION (expanding thresholds) ===")
    for k in ["auc_roc", "auprc", "auprc_baseline_prevalence", "brier",
              "brier_baseline", "sensitivity", "specificity", "ppv", "n", "n_outbreak"]:
        print(f"  {k:28s} {clf.get(k)}")
    print("\n=== OUT-OF-FOLD PERMUTATION IMPORTANCE (grouped, %) ===")
    for k, v in sorted(perm["grouped_percent"].items(), key=lambda kv: -kv[1]):
        print(f"  {k:26s} {v:6.1f}")
    print("\n=== BETWEEN-STATE ASSOCIATIONS (mean incidence per 100k) ===")
    for k, v in assoc["mean_incidence"].items():
        print(f"  {k:14s} rho={v['rho']:+.3f}  95% CI [{v['ci_low']:+.2f},{v['ci_high']:+.2f}]  p={v['p']:.4f}  n={v['n']}")
    a = assoc["gdp_incidence_adjusted_for_health_index"]
    print(f"  GDP adjusted for Health Index: partial rho={a['partial_rho']:+.3f} p={a['p']:.4f}")
    print("\n=== LEAKAGE EXPERIMENT (R2, log scale) ===")
    for k, v in leak.items():
        print(f"  {k:42s} {v}")
    print(f"\nSaved -> {OUTDIR}/real_metrics.json")


if __name__ == "__main__":
    main()
