"""
GWP1 — Single source of truth for all research analytics.
CrudeCortex — MScFE 660 GWP1.

Reproduces the exact methodology of the original notebook
(GWP1_14660_SRC.ipynb) on the sterilized monthly dataset:
2010-01 → 2024-12, 180 observations, 13 usable variables.
"""
from __future__ import annotations

import io
import os
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import jarque_bera, shapiro, kstest, anderson
from statsmodels.stats.diagnostic import acorr_ljungbox

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_CSV = os.path.join(PROJECT_ROOT, "data", "raw_data.csv")
MASTER_URL = ("https://drive.google.com/uc?export=download&id="
              "1_d0GM6SMHELNhH6cZv2zvaF4hEweDxQR")

START, END = "2010-01-01", "2024-12-31"
IC_VARS = ["WTI_Spot", "OPEC_Prod", "NonOPEC_Prod", "OECD_Demand",
           "CPI_Energy", "VIX", "USD_DXY"]

# ---------------------------------------------------------------- metadata
DATA_DICTIONARY = [
    # variable, full name, category, series id, units, native freq, analytical freq, publication delay, status
    ("WTI_Spot", "WTI Crude Oil Spot Price (monthly average)", "Financial", "FRED — WTISPLC", "USD/bbl", "Monthly", "Monthly", "~2 weeks", "Available"),
    ("WTI_Futures", "WTI Crude Oil Futures (front-month)", "Financial", "Yahoo Finance — CL=F", "USD/bbl", "Daily→Monthly", "Monthly", "Daily", "Available (26 short-gap months interpolated)"),
    ("Brent", "Brent Crude Oil Futures Price", "Financial", "Yahoo Finance — BZ=F", "USD/bbl", "Daily→Monthly", "Monthly", "Daily", "Available (26 short-gap months interpolated)"),
    ("VIX", "CBOE Volatility Index", "Financial", "Yahoo Finance — ^VIX", "Index", "Daily→Monthly", "Monthly", "Daily", "Available"),
    ("SP500", "S&P 500 Equity Index", "Financial", "Yahoo Finance — ^GSPC", "Index", "Daily→Monthly", "Monthly", "Daily", "Available"),
    ("IndustrialProd", "US Industrial Production Index", "Macroeconomic", "FRED — INDPRO", "Index (2017=100)", "Monthly", "Monthly", "~2 weeks", "Available"),
    ("CPI_Energy", "US CPI — Energy Sub-Index", "Macroeconomic", "FRED — CPIENGSL", "Index (1982-84=100)", "Monthly", "Monthly", "~2 weeks", "Available"),
    ("USD_DXY", "US Dollar Trade-Weighted Broad Index", "Macroeconomic", "FRED — DTWEXBGS", "Index (Jan 2006=100)", "Daily→Monthly", "Monthly", "Daily", "Available"),
    ("GDP_Growth", "US Real GDP Growth Rate", "Macroeconomic/Geopolitical", "FRED — A191RL1Q225SBEA", "% (annualised q/q)", "Quarterly→Monthly (ffill)", "Monthly (filled)", "~1 month", "Available — forward-filled, not true monthly data"),
    ("OPEC_Prod", "OPEC Crude Oil Production", "Microeconomic", "EIA STEO — PAPR_OPEC", "Million bbl/day", "Monthly (STEO)", "Monthly", "STEO cycle", "Available — partly STEO estimate"),
    ("NonOPEC_Prod", "Non-OPEC Crude Oil Production", "Microeconomic", "EIA STEO — PAPR_NONOPEC", "Million bbl/day", "Monthly (STEO)", "Monthly", "STEO cycle", "Available — partly STEO estimate"),
    ("OECD_Demand", "OECD Petroleum Consumption", "Microeconomic", "EIA STEO — PATC_OECD", "Million bbl/day", "Monthly (STEO)", "Monthly", "STEO cycle", "Available — partly STEO estimate"),
    ("OECD_Inventory", "OECD Commercial Crude Oil Inventories", "Microeconomic", "EIA STEO — PASC_OECD_T3", "Million bbl", "Monthly (STEO)", "Monthly", "STEO cycle", "Available — partly STEO estimate"),
    ("NonOECD_Demand", "Non-OECD Petroleum Consumption", "Microeconomic", "EIA STEO — PATC_NONOECD", "Million bbl/day", "Monthly", "—", "—", "UNAVAILABLE — retrieval failed; NOT imputed"),
    ("US_Ref_Cap", "US Petroleum Refinery Capacity Utilisation", "Microeconomic", "EIA STEO — PARC_USA", "%", "Monthly", "—", "—", "UNAVAILABLE — retrieval failed; NOT imputed"),
    ("GPR", "Geopolitical Risk Index (Caldara & Iacoviello)", "Geopolitical", "FRED — GPRICEN", "Index", "Monthly", "—", "—", "UNAVAILABLE — load failed in original retrieval; NOT imputed"),
]

VARIABLE_CATEGORIES = {
    "WTI_Spot": "Financial", "WTI_Futures": "Financial", "Brent": "Financial",
    "VIX": "Financial", "SP500": "Financial",
    "IndustrialProd": "Macroeconomic", "CPI_Energy": "Macroeconomic",
    "USD_DXY": "Macroeconomic", "GDP_Growth": "Macroeconomic/Geopolitical",
    "OPEC_Prod": "Microeconomic", "NonOPEC_Prod": "Microeconomic",
    "OECD_Demand": "Microeconomic", "OECD_Inventory": "Microeconomic",
    "NonOECD_Demand": "Microeconomic (unavailable)", "US_Ref_Cap": "Microeconomic (unavailable)",
}


def data_dictionary_df() -> pd.DataFrame:
    rows = []
    for v, full, cat, sid, units, nfreq, afreq, delay, status in DATA_DICTIONARY:
        rows.append({
            "Variable": v, "Full name": full, "Economic category": cat,
            "Series ID / ticker": sid, "Units": units,
            "Native frequency": nfreq, "Analytical frequency": afreq,
            "Publication delay": delay, "Data status": status,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- loading
def load_raw(refresh: bool = False) -> pd.DataFrame:
    """Load the raw master dataset (local CSV, else re-download from the
    notebook's public Google Drive source). Never modified in place."""
    if os.path.exists(RAW_CSV) and not refresh:
        return pd.read_csv(RAW_CSV, index_col=0, parse_dates=True)
    try:
        import requests
        r = requests.get(MASTER_URL, timeout=60)
        r.raise_for_status()
        df = pd.read_csv(io.BytesIO(r.content), index_col=0, parse_dates=True)
        os.makedirs(os.path.dirname(RAW_CSV), exist_ok=True)
        df.to_csv(RAW_CSV)
        return df
    except Exception:
        if os.path.exists(RAW_CSV):
            return pd.read_csv(RAW_CSV, index_col=0, parse_dates=True)
        raise


# ---------------------------------------------------------------- cleaning
def winsorise_3iqr(df_raw: pd.DataFrame):
    """Student A — extreme outlier treatment: 3×IQR winsorisation
    (Section 4.1 methodology of Alvi 2018). Values beyond the fences are
    CAPPED, never deleted: genuine oil-market shocks are retained."""
    df = df_raw.copy()
    log = []
    for col in df.columns:
        s = df[col].dropna()
        if s.empty:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        lo, hi = q1 - 3 * iqr, q3 + 3 * iqr
        mask = (df[col] < lo) | (df[col] > hi)
        n = int(mask.sum())
        if n > 0:
            df[col] = df[col].clip(lo, hi)
            log.append({"Variable": col, "N capped": n,
                        "Lower fence": round(float(lo), 3),
                        "Upper fence": round(float(hi), 3)})
    return df, pd.DataFrame(log)


def bad_data_checks(df_raw: pd.DataFrame) -> dict:
    """Student B — bad-data identification."""
    df, _ = winsorise_3iqr(df_raw)
    out = {"duplicate_timestamps": int(df.index.duplicated().sum()),
           "negative_price_counts": {}, "large_moves": []}
    for col in ["WTI_Spot", "WTI_Futures", "Brent"]:
        if col in df.columns:
            out["negative_price_counts"][col] = int((df[col] < 0).sum())
    chg = df["WTI_Spot"].pct_change().dropna()
    thr = chg.std() * 3
    out["large_move_threshold_pct"] = round(float(thr * 100), 1)
    for dt, val in chg[chg.abs() > thr].items():
        out["large_moves"].append({"Month": dt.strftime("%Y-%m"),
                                   "Return": round(float(val) * 100, 1)})
    # stale runs (quarterly→monthly forward-fill shows up here)
    stale = []
    for col in df.columns:
        s = df[col].dropna()
        run = (s != s.shift()).cumsum()
        rl = run.map(run.value_counts())
        for st in s[(rl >= 5) & (s != s.shift())].index:
            stale.append({"Variable": col, "Run length": int(rl[st]),
                          "Start": str(st.date())})
    out["stale_runs"] = stale
    return out


def impute_missing(df_winsorised: pd.DataFrame):
    """Student C — missing-data treatment:
    time interpolation → forward-fill → back-fill.
    Entirely-unavailable series (all NaN) are NEVER imputed."""
    df = df_winsorised.copy()
    before = df.isnull().sum().copy()
    df = df.interpolate(method="time", limit_direction="both")
    df = df.ffill().bfill()
    after = df.isnull().sum()
    # keep all-NaN columns all-NaN (interpolation cannot fill them and
    # we must not fabricate them)
    for col in df.columns:
        if before[col] == len(df):
            df[col] = np.nan
    rep = pd.DataFrame({"Missing before": before, "Missing after": after})
    rep["Method"] = ["time-interp + ffill/bfill" if b < len(df) and b > 0
                     else ("never imputed (fully unavailable)" if b == len(df)
                           else "none needed") for b in before]
    return df, rep


@dataclass
class ResearchData:
    raw: pd.DataFrame
    winsorised: pd.DataFrame
    sterilized: pd.DataFrame
    outlier_log: pd.DataFrame
    missing_report: pd.DataFrame
    bad_data: dict
    returns: pd.Series
    log_returns: pd.Series


def build_research_data(refresh: bool = False) -> ResearchData:
    raw = load_raw(refresh)
    wins, olog = winsorise_3iqr(raw)
    ster, mrep = impute_missing(wins)
    bad = bad_data_checks(raw)
    ret = ster["WTI_Spot"].pct_change().dropna()
    lret = np.log(ster["WTI_Spot"] / ster["WTI_Spot"].shift(1)).dropna()
    return ResearchData(raw, wins, ster, olog, mrep, bad, ret, lret)


# ---------------------------------------------------------------- statistics
def descriptive_statistics(ret: pd.Series) -> dict:
    return {
        "n": int(ret.size),
        "mean_pct": float(ret.mean() * 100),
        "std_pct": float(ret.std() * 100),
        "ann_vol_pct": float(ret.std() * np.sqrt(12) * 100),
        "skew": float(ret.skew()),
        "excess_kurtosis": float(ret.kurtosis()),
        "min_pct": float(ret.min() * 100),
        "max_pct": float(ret.max() * 100),
    }


def normality_tests(ret: pd.Series) -> dict:
    jb_s, jb_p = jarque_bera(ret.values)
    sw_s, sw_p = shapiro(ret.values[:50])            # original convention (n≤50)
    sw_full_s, sw_full_p = shapiro(ret.values)       # full-sample reassessment
    ks_s, ks_p = kstest((ret.values - ret.mean()) / ret.std(), "norm")
    ad = anderson(ret.values, dist="norm")
    ad_cv5 = float(ad.critical_values[2])
    return {
        "Jarque-Bera": {"stat": float(jb_s), "p": float(jb_p)},
        "Shapiro-Wilk (first 50, original)": {"stat": float(sw_s), "p": float(sw_p)},
        "Shapiro-Wilk (full sample, n=%d)" % ret.size: {"stat": float(sw_full_s), "p": float(sw_full_p)},
        "Kolmogorov-Smirnov": {"stat": float(ks_s), "p": float(ks_p)},
        "Anderson-Darling": {"stat": float(ad.statistic), "cv5": ad_cv5},
    }


def risk_metrics(ret: pd.Series) -> dict:
    var95 = float(np.percentile(ret, 5))
    cvar95 = float(ret[ret <= var95].mean())
    var99 = float(np.percentile(ret, 1))
    cvar99 = float(ret[ret <= var99].mean())
    cum = (1 + ret).cumprod()
    mdd = float(((cum - cum.cummax()) / cum.cummax()).min()) * 100
    sharpe = float((ret.mean() / ret.std()) * np.sqrt(12))
    return {"VaR95": var95 * 100, "CVaR95": cvar95 * 100,
            "VaR99": var99 * 100, "CVaR99": cvar99 * 100,
            "Sharpe": sharpe, "MaxDD": mdd}


def ljung_box(ret: pd.Series) -> dict:
    lb_r = acorr_ljungbox(ret, lags=[1, 6, 12, 24], return_df=True)
    lb_sq = acorr_ljungbox(ret ** 2, lags=[1, 6, 12, 24], return_df=True)
    return {"returns": lb_r, "squared": lb_sq}


def correlations_with_wti(ster: pd.DataFrame) -> pd.Series:
    cand = ["CPI_Energy", "OECD_Demand", "IndustrialProd", "VIX",
            "OPEC_Prod", "USD_DXY", "SP500", "GDP_Growth",
            "NonOPEC_Prod", "OECD_Inventory", "WTI_Futures", "Brent"]
    out = {}
    for c in cand:
        if c in ster.columns:
            out[c] = float(ster[["WTI_Spot", c]].corr().iloc[0, 1])
    return pd.Series(out).sort_values(key=abs, ascending=False)


def rolling_stats(ret: pd.Series, window: int = 12) -> pd.DataFrame:
    return pd.DataFrame({
        "Rolling mean": ret.rolling(window).mean(),
        "Rolling std (ann.)": ret.rolling(window).std() * np.sqrt(12),
    })


# ---------------------------------------------------------------- inferred causality
def partial_corr(x_var: str, y_var: str, cond_set, data: pd.DataFrame):
    """Partial correlation via OLS residuals (identical to notebook)."""
    cols = [x_var, y_var] + list(cond_set)
    sub = data[cols].dropna()
    if len(sub) < 15:
        return 0.0, 1.0
    if len(cond_set) == 0:
        r, p = stats.pearsonr(sub[x_var].values, sub[y_var].values)
        return float(r), float(p)
    from numpy.linalg import lstsq
    Z = np.column_stack([sub[z].values for z in cond_set] + [np.ones(len(sub))])
    rx = sub[x_var].values - Z @ lstsq(Z, sub[x_var].values, rcond=None)[0]
    ry = sub[y_var].values - Z @ lstsq(Z, sub[y_var].values, rcond=None)[0]
    if rx.std() < 1e-12 or ry.std() < 1e-12:
        return 0.0, 1.0
    r, p = stats.pearsonr(rx, ry)
    return float(r), float(p)


@dataclass
class CausalResult:
    variables: list
    markov_blankets: dict
    edges: list                 # frozenset pairs → sorted tuples
    sep_sets: dict
    v_structures: list          # unique (a, k, b)
    alpha: float


def inferred_causality(data: pd.DataFrame, variables=None, alpha: float = 0.05) -> CausalResult:
    """Simplified PC-style constraint-based structure learning — the exact
    procedure implemented in the original notebook:
      Phase 1 — Markov blankets via pairwise marginal independence tests
      Phase 2 — skeleton with SINGLE-variable conditioning sets only
      Phase 3 — v-structure orientation"""
    variables = variables or [v for v in IC_VARS if v in data.columns]
    adj = {v: set() for v in variables}
    for i, vi in enumerate(variables):
        for j, vj in enumerate(variables):
            if i >= j:
                continue
            _, p = partial_corr(vi, vj, [], data)
            if p < alpha:
                adj[vi].add(vj); adj[vj].add(vi)
    mb = {v: set(adj[v]) for v in variables}

    edges, sep_sets = set(), {}
    for i, vi in enumerate(variables):
        for j, vj in enumerate(variables):
            if i >= j:
                continue
            _, p0 = partial_corr(vi, vj, [], data)
            if p0 >= alpha:
                sep_sets[frozenset([vi, vj])] = set()
                continue
            found = False
            for vk in (mb[vi] | mb[vj]) - {vi, vj}:
                _, pc = partial_corr(vi, vj, [vk], data)
                if pc >= alpha:
                    found = True
                    sep_sets[frozenset([vi, vj])] = {vk}
                    break
            if not found:
                edges.add(frozenset([vi, vj]))

    raw_vs = []
    for vk in variables:
        nb = [e for e in edges if vk in e]
        for ea in nb:
            for eb in nb:
                if ea == eb:
                    continue
                vi_n = (set(ea) - {vk}).pop()
                vj_n = (set(eb) - {vk}).pop()
                if frozenset([vi_n, vj_n]) not in edges:
                    ss = sep_sets.get(frozenset([vi_n, vj_n]), set())
                    if vk not in ss:
                        raw_vs.append((vi_n, vk, vj_n))
    # de-duplicate reversed repetitions of the same v-structure
    uniq, seen = [], set()
    for a, k, b in raw_vs:
        key = frozenset([a, b]) | {k}
        if key not in seen:
            seen.add(key); uniq.append((a, k, b))

    return CausalResult(variables, mb, [tuple(sorted(e)) for e in edges],
                        {tuple(sorted(k)): v for k, v in sep_sets.items()},
                        uniq, alpha)


# ---------------------------------------------------------------- one-call cache
def get_all(refresh: bool = False) -> ResearchData:
    return build_research_data(refresh)
