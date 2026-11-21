"""Reproduce every reported notebook baseline and print a verification table.
Run:  python scripts/reproduce_notebook.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics import get_all, descriptive_statistics, normality_tests, risk_metrics, ljung_box, inferred_causality

EXPECTED = {
    "n_returns": 179, "mean_pct": 0.505, "std_pct": 10.714,
    "skew": 1.0796, "excess_kurtosis": 13.379,
    "VaR95": -12.99, "CVaR95": -22.86, "VaR99": -26.27, "CVaR99": -42.77,
    "Sharpe": 0.1633, "MaxDD": -84.96, "JB": 1289.786,
    "n_edges": 7,
}
TOL = {"mean_pct": 0.02, "std_pct": 0.05, "skew": 0.02, "excess_kurtosis": 0.1,
       "JB": 3.0, "VaR95": 0.3, "CVaR95": 0.5, "VaR99": 0.5, "CVaR99": 0.8,
       "Sharpe": 0.01, "MaxDD": 1.0, "n_returns": 0, "n_edges": 0}


def main() -> None:
    rd = get_all()
    d = descriptive_statistics(rd.returns)
    n = normality_tests(rd.returns)
    r = risk_metrics(rd.returns)
    ic = inferred_causality(rd.sterilized)

    got = {
        "n_returns": d["n"], "mean_pct": d["mean_pct"], "std_pct": d["std_pct"],
        "skew": d["skew"], "excess_kurtosis": d["excess_kurtosis"],
        "VaR95": r["VaR95"], "CVaR95": r["CVaR95"], "VaR99": r["VaR99"],
        "CVaR99": r["CVaR99"], "Sharpe": r["Sharpe"], "MaxDD": r["MaxDD"],
        "JB": n["Jarque-Bera"]["stat"], "n_edges": len(ic.edges),
    }
    print(f"{'Metric':<16}{'Expected':>12}{'Got':>12}  Status")
    ok_all = True
    for k, exp in EXPECTED.items():
        g = got[k]
        ok = abs(g - exp) <= max(TOL.get(k, 0), 1e-9) if TOL.get(k) else g == exp
        ok_all &= ok
        print(f"{k:<16}{exp:>12}{g:>12.4f}  {'✅' if ok else '❌'}")

    mb = sorted(ic.markov_blankets["WTI_Spot"])
    ok_mb = mb == ["CPI_Energy", "NonOPEC_Prod", "USD_DXY"]
    print(f"{'WTI blanket':<16}{'CPI/NONOP/DXY':>12}{'/'.join(mb)[:30]:>12}  {'✅' if ok_mb else '❌'}")
    ok_v = any({"WTI_Spot"} == {k} and {a, b} == {"CPI_Energy", "USD_DXY"}
               for a, k, b in ic.v_structures)
    print(f"{'v-structure':<16}{'DXY→WTI←CPI':>12}{'present':>12}  {'✅' if ok_v else '❌'}")
    print("\nREPRODUCTION:", "ALL CHECKS PASSED ✅" if ok_all and ok_mb and ok_v
          else "SOME CHECKS FAILED — see table ❌")
    sys.exit(0 if (ok_all and ok_mb and ok_v) else 1)


if __name__ == "__main__":
    main()
