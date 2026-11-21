"""Reproduction + security tests for the GWP1 research platform.
Run:  python -m pytest tests/ -v
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics import (build_research_data, descriptive_statistics,
                            normality_tests, risk_metrics, ljung_box,
                            inferred_causality, winsorise_3iqr, impute_missing)


@pytest.fixture(scope="module")
def rd():
    return build_research_data()


# ------------------------------------------------------- reproduction tests
def test_shape_180_rows(rd):
    assert rd.raw.shape == (180, 15)


def test_period(rd):
    assert str(rd.raw.index[0].date()) == "2010-01-01"
    assert str(rd.raw.index[-1].date()) == "2024-12-01"


def test_unavailable_series_never_imputed(rd):
    for col in ("NonOECD_Demand", "US_Ref_Cap"):
        assert rd.raw[col].isna().all()
        assert rd.sterilized[col].isna().all()


def test_thirteen_usable_variables(rd):
    usable = [c for c in rd.raw.columns if rd.raw[c].notna().any()]
    assert len(usable) == 13


def test_return_statistics(rd):
    d = descriptive_statistics(rd.returns)
    assert d["n"] == 179
    assert abs(d["mean_pct"] - 0.505) < 0.02
    assert abs(d["std_pct"] - 10.714) < 0.05
    assert abs(d["ann_vol_pct"] - 37.11) < 0.1
    assert abs(d["skew"] - 1.0796) < 0.02
    assert abs(d["excess_kurtosis"] - 13.379) < 0.1
    assert abs(d["min_pct"] - (-43.34)) < 0.1
    assert abs(d["max_pct"] - 72.57) < 0.1


def test_jarque_bera(rd):
    n = normality_tests(rd.returns)
    assert abs(n["Jarque-Bera"]["stat"] - 1289.786) < 3.0
    assert n["Jarque-Bera"]["p"] < 1e-4


def test_risk_metrics(rd):
    r = risk_metrics(rd.returns)
    for key, exp, tol in [("VaR95", -12.99, 0.3), ("CVaR95", -22.86, 0.5),
                          ("VaR99", -26.27, 0.5), ("CVaR99", -42.77, 0.8),
                          ("Sharpe", 0.1633, 0.01), ("MaxDD", -84.96, 1.0)]:
        assert abs(r[key] - exp) < tol, key


def test_ljung_box_rejects(rd):
    lb = ljung_box(rd.returns)
    assert (lb["returns"]["lb_pvalue"] < 0.05).all()
    assert (lb["squared"]["lb_pvalue"] < 1e-4).all()


def test_inferred_causality_structure(rd):
    ic = inferred_causality(rd.sterilized)
    assert len(ic.edges) == 7
    assert sorted(ic.markov_blankets["WTI_Spot"]) == \
        ["CPI_Energy", "NonOPEC_Prod", "USD_DXY"]
    # reported v-structure DXY → WTI ← CPI present
    assert any({"WTI_Spot"} == {k} and {a, b} == {"CPI_Energy", "USD_DXY"}
               for a, k, b in ic.v_structures)
    for (a, b) in [("CPI_Energy", "NonOPEC_Prod"), ("CPI_Energy", "WTI_Spot"),
                   ("NonOPEC_Prod", "USD_DXY"), ("NonOPEC_Prod", "WTI_Spot"),
                   ("OECD_Demand", "OPEC_Prod"), ("OPEC_Prod", "VIX"),
                   ("USD_DXY", "WTI_Spot")]:
        assert (a, b) in [tuple(e) for e in ic.edges] or \
               (b, a) in [tuple(e) for e in ic.edges], (a, b)


# ------------------------------------------------------- unit tests
def test_winsorisation_counts(rd):
    """Verify caps against the canonical raw CSV.

    GDP_Growth: 9 capped values — matches the notebook baseline exactly
    (fences ≈ notebook's reported [-4.12, 9.35] on the canonical quartiles).
    VIX / IndustrialProd / OPEC_Prod / OECD_Demand caps reported in the
    notebook correspond to an EARLIER collection session (26 missing
    futures months); on the canonical CSV those series fall inside the
    3×IQR fences. Documented as execution-session drift — see Page 4.
    """
    _, log = winsorise_3iqr(rd.raw)
    got = dict(zip(log["Variable"], log["N capped"]))
    assert got.get("GDP_Growth") == 9
    for var in ("VIX", "IndustrialProd", "OPEC_Prod", "OECD_Demand"):
        assert got.get(var, 0) == 0  # inside fences on the canonical CSV


def test_winsorisation_preserves_raw(rd):
    raw_copy = rd.raw.copy()
    wins, _ = winsorise_3iqr(rd.raw)
    pd.testing.assert_frame_equal(rd.raw, raw_copy)   # raw untouched
    assert not wins.equals(rd.raw)                    # winsorised differs


def test_large_move_events(rd):
    months = {m["Month"] for m in rd.bad_data["large_moves"]}
    assert {"2020-03", "2020-04", "2020-05", "2020-06"} <= months


def test_no_duplicate_timestamps(rd):
    assert rd.bad_data["duplicate_timestamps"] == 0


def test_correlation_usd(rd):
    corr = rd.sterilized[["WTI_Spot", "USD_DXY"]].corr().iloc[0, 1]
    assert abs(corr - (-0.519)) < 0.03


# ------------------------------------------------------- security tests
def test_no_secrets_in_repo():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in
                       (".git", "__pycache__", ".venv", "venv", "node_modules")]
        for fn in filenames:
            if fn in (".env", "secrets.toml"):
                hits.append(fn)
            if fn.endswith((".py", ".md", ".toml", ".txt")) and not fn.endswith(".example") \
                    and fn != "test_reproduction.py" and fn != "SECURITY.md":
                with open(os.path.join(dirpath, fn), errors="ignore") as f:
                    t = f.read().lower()
                for pat in ("api_key=kv", "password=", "sk-live", "secret_token="):
                    if pat in t:
                        hits.append(f"{fn}:{pat}")
    assert not hits, hits


def test_no_dangerous_calls():
    import subprocess
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = subprocess.run(
        ["grep", "-rn", "--exclude-dir=.venv", "--exclude-dir=.git",
         "-E", r"eval\(|exec\(|pickle\.loads|shell=True", "."],
        cwd=root, capture_output=True, text=True).stdout
    out = "\n".join(l for l in out.splitlines()
                    if "test_" not in l and "SECURITY.md" not in l)
    assert out.strip() == "", out
