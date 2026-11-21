"""PAGE 6 — Stylized Facts & Risk Characteristics (Step 8)."""
import sys, os
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats as sstats

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all, descriptive_statistics, normality_tests, risk_metrics, ljung_box

st.title("📊 Stylized Facts & Risk Characteristics")
st.caption("GWP1 Step 8 — the four official questions, answered on the cleaned "
           "data with supporting statistics. All figures are descriptive "
           "historical estimates, not strategy results.")

@st.cache_data(show_spinner="Loading research dataset…")
def _research():
    return get_all()

rd = _research()
import copy as _copy
b1, b2 = st.columns([2, 3])
basis = b1.radio("Return basis", ["Simple returns (headline basis)", "Log returns"],
                 horizontal=True)
dmin, dmax = rd.returns.index.min().date(), rd.returns.index.max().date()
dr = b2.slider("📅 Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
src_ret = rd.log_returns if basis.startswith("Log") else rd.returns
ret = src_ret[(src_ret.index >= pd.Timestamp(dr[0])) &
              (src_ret.index <= pd.Timestamp(dr[1]) + pd.offsets.MonthEnd(0))]
rd = _copy.copy(rd)
rd.returns = ret
desc = descriptive_statistics(ret)
norm = normality_tests(ret)
risk = risk_metrics(ret)
lb = ljung_box(ret)
st.caption(f"Basis: **{basis.split(' (')[0]}** · Months in view: **{len(ret)}** · "
           "all panels below recompute on these inputs.")

qa, qb, qc, qd = st.tabs(["Q(a) What makes oil different?",
                          "Q(b) Return distributions",
                          "Q(c) Autocorrelation",
                          "Q(d) Other stylized facts"])

with qa:
    st.markdown("""
### What makes oil prices look different from other asset prices?

**Observed in this dataset:**
- **Extreme spikes** — monthly simple returns reached **−43.3% (Apr 2020)** and
  **+72.6% (May 2020)**; no major equity index shows monthly moves of this
  magnitude in the same window.
- **Volatility clustering** — calm and turbulent months arrive in runs
  (see the rolling-volatility chart); Ljung–Box on squared returns confirms it.
- **Event-driven regimes** — the 2014–16 OPEC supply surge, the 2020 COVID
  demand collapse and the 2022 Russia–Ukraine crisis each dominate a distinct
  price regime.
- **Physical anchor** — unlike equities, oil is priced by physical balances
  (production, demand, inventories) *and* financial flows, with storage costs
  producing term-structure effects (contango/backwardation).

**Possible economic explanations (interpretation, not proof):** supply/demand
shocks, inventory buffering, geopolitical disruptions and the dollar's inverse
channel all plausibly contribute — the data show the behaviour, the economics
explains it.
""")
    rs = ret.rolling(12).std() * np.sqrt(12) * 100
    fig = go.Figure()
    fig.add_scatter(x=ret.index, y=ret * 100, name="Monthly return (%)",
                    line=dict(width=0.8, color="#9CA3AF"))
    fig.add_scatter(x=rs.index, y=rs, name="12m rolling vol (ann. %)",
                    line=dict(width=2.5, color="#C62828"))
    fig.update_layout(title="Volatility clustering in WTI — regime structure is visible",
                      xaxis_title="Month", yaxis_title="%", height=380)
    st.plotly_chart(fig, use_container_width=True)

with qb:
    st.markdown("### Distribution of WTI monthly simple returns")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Mean", f"{desc['mean_pct']:+.3f}%")
    m2.metric("Std dev", f"{desc['std_pct']:.3f}%")
    m3.metric("Skewness", f"{desc['skew']:.4f}")
    m4.metric("Excess kurtosis", f"{desc['excess_kurtosis']:.3f}")
    st.markdown(f"Range: **{desc['min_pct']:.2f}% → {desc['max_pct']:.2f}%** "
                f"over {desc['n']} returns.")

    xs = np.linspace(ret.min() * 100 - 8, ret.max() * 100 + 8, 400)
    params_t = sstats.t.fit(ret.values)
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=ret * 100, histnorm="probability density",
                               nbinsx=40, name="Observed", marker_color="#E8842C",
                               opacity=0.7))
    fig.add_scatter(x=xs, y=sstats.norm.pdf(xs, ret.mean() * 100, ret.std() * 100),
                    name="Normal", line=dict(color="#1A2733", width=2))
    fig.add_scatter(x=xs, y=sstats.t.pdf(xs, params_t[0], loc=params_t[1],
                                         scale=params_t[2]),
                    name=f"Student-t (df={params_t[0]:.1f})",
                    line=dict(color="#7B1FA2", width=2, dash="dash"))
    fig.update_layout(title="Fat tails: the Student-t fit dominates the normal",
                      xaxis_title="Return (%)", yaxis_title="Density", height=380)
    st.plotly_chart(fig, use_container_width=True)

    qq_x, qq_y = sstats.probplot(ret.values, dist="norm")
    fig = go.Figure()
    fig.add_scatter(x=qq_x[0], y=qq_x[1], mode="markers", name="Sample quantiles",
                    marker=dict(color="#E8842C", size=5))
    fig.add_scatter(x=qq_x[0], y=qq_x[0] * qq_x[1][1] + qq_x[1][0], mode="lines",
                    name="Theoretical normal", line=dict(color="#1A2733"))
    fig.update_layout(title="Q–Q plot vs normal — tail departure is severe",
                      xaxis_title="Theoretical quantiles",
                      yaxis_title="Sample quantiles (return)", height=380)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Normality tests")
    rows = []
    for k, v in norm.items():
        p = v.get("p")
        rows.append({"Test": k, "Statistic": round(v["stat"], 4),
                     "p-value": ("—" if p is None else
                                 ("< 0.0001" if p < 1e-4 else f"{p:.4f}")),
                     "Decision (5%)": "Reject normality" if (p is None and v["stat"] > v.get("cv5", 1e9))
                                      or (p is not None and p < 0.05) else "Fail to reject"})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.error("**Interpretation.** Jarque-Bera, Kolmogorov–Smirnov and "
             "Anderson–Darling reject normality — driven by skewness and huge "
             "excess kurtosis. **Known-issue disclosure:** the original notebook's "
             "Shapiro–Wilk used only the first 50 observations and did *not* "
             "reject; that result is preserved above alongside the full-sample "
             "reassessment. A normal distribution is **not** an adequate model "
             "for monthly oil returns; heavy-tailed (Student-t) assumptions are "
             "preferable for risk work.")

with qc:
    st.markdown("### Autocorrelation structure")
    lags = np.arange(1, 25)
    def acf(x, k):
        xm = x - x.mean()
        return float(np.sum(xm[k:] * xm[:-k]) / np.sum(xm * xm))
    acf_r = [acf(ret.values, k) for k in lags]
    acf_sq = [acf((ret ** 2).values, k) for k in lags]
    n = len(ret)
    ci = 1.96 / np.sqrt(n)
    fig = make_subplots(rows=1, cols=2, subplot_titles=("ACF of returns",
                                                        "ACF of squared returns"))
    fig.add_trace(go.Bar(x=list(lags), y=acf_r, marker_color="#1F6FB2",
                         showlegend=False), 1, 1)
    fig.add_trace(go.Bar(x=list(lags), y=acf_sq, marker_color="#C62828",
                         showlegend=False), 1, 2)
    for col in (1, 2):
        fig.add_hline(y=ci, line_dash="dot", line_color="#6B7280", row=1, col=col)
        fig.add_hline(y=-ci, line_dash="dot", line_color="#6B7280", row=1, col=col)
    fig.update_layout(height=380, title="Returns show weak serial dependence; "
                                         "squared returns show strong dependence")
    fig.update_xaxes(title_text="Lag (months)", row=1, col=1)
    fig.update_xaxes(title_text="Lag (months)", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Ljung–Box tests")
    t1, t2 = st.columns(2)
    lb_r = lb["returns"][["lb_stat", "lb_pvalue"]].round(6).reset_index()
    lb_r.columns = ["Lag", "Statistic", "p-value"]
    lb_sq = lb["squared"][["lb_stat", "lb_pvalue"]].round(6).reset_index()
    lb_sq.columns = ["Lag", "Statistic", "p-value"]
    t1.markdown("**On returns**"); t1.dataframe(lb_r, hide_index=True, use_container_width=True)
    t2.markdown("**On squared returns**"); t2.dataframe(lb_sq, hide_index=True, use_container_width=True)
    st.warning("**Corrected interpretation (known issue #1).** The original "
               "narrative said returns have 'near-zero autocorrelation', but the "
               "Ljung–Box results reject the no-autocorrelation null at all "
               "listed lag groups (e.g. lag-1 p≈0.0046). The correct reading: "
               "individual ACF coefficients are small in magnitude, yet "
               "collectively significant — while **squared returns** are far "
               "more strongly dependent, the classic volatility-clustering "
               "signature. Statistical significance here does not establish "
               "practical predictive value.")

with qd:
    st.markdown("### Additional stylized facts")
    st.markdown("""
| Candidate fact | Evidence status in GWP1 |
|---|---|
| **Volatility clustering** | ✅ Demonstrated — Ljung–Box on squared returns rejects at all lags; rolling vol shows regimes |
| **Fat tails / heavy-tailed returns** | ✅ Demonstrated — excess kurtosis ≈ 13.4; JB rejection |
| **Right-skew at monthly horizon** | ✅ Demonstrated — skew ≈ +1.08, driven by 2020 rebound |
| **Seasonality** | ⚠️ Untested literature observation — no formal test in GWP1 |
| **Leverage effects** | ⚠️ Untested literature observation — not tested in GWP1 |
| **Contango / backwardation** | ⚠️ Untested — requires futures term-structure data beyond the monthly panel |
| **Dollar inverse relation** | ✅ Documented — correlation with USD_DXY ≈ −0.52 (association, not causation) |
| **Structural breaks** | ✅ Descriptively visible (2014–16, 2020, 2022 regimes); no formal break test in GWP1 |
""")
    st.markdown("### Historical risk summary (descriptive)")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("VaR 95% (monthly)", f"{risk['VaR95']:.2f}%")
    r2.metric("CVaR 95%", f"{risk['CVaR95']:.2f}%")
    r3.metric("VaR 99%", f"{risk['VaR99']:.2f}%")
    r4.metric("CVaR 99%", f"{risk['CVaR99']:.2f}%")
    r5, r6 = st.columns(2)
    r5.metric("Sharpe ratio (ann., rf=0)", f"{risk['Sharpe']:.4f}")
    r6.metric("Maximum drawdown (price path)", f"{risk['MaxDD']:.2f}%")
    st.caption("""
- **VaR95** = 5th percentile of monthly returns; **CVaR95** = mean return in the worst 5% of months.
- **Sharpe** = (mean μ/σ)·√12 with a zero risk-free convention — descriptive only.
- **Max drawdown** = peak-to-trough on the cumulative-return path (−84.96% reflects the 2014→2016 and 2018→2020 declines).
- **Limitations:** historical, single-sample, zero-risk-free-rate convention, no parameter uncertainty; these are *not* forecasts and imply no trading strategy.
""")

st.divider()
st.caption("Source: authors' calculations on the sterilized GWP1 dataset "
           "(FRED · EIA STEO · Yahoo Finance). Methods follow the original "
           "notebook conventions (monthly simple returns).")

# ---------------- Insight panel (dynamic) ----------------
lb1 = float(lb["returns"]["lb_pvalue"].iloc[0])
lbsq = float(lb["squared"]["lb_pvalue"].iloc[0])
st.divider()
st.markdown("### 🧭 Understand this page — Stylized Facts & Risk")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Mean monthly return:</b> <span style='color:#C2571B;font-weight:700'>{desc['mean_pct']:+.2f}%</span> — the average month's move; small positive drift over the selected window.</div>
<div class='insight-num'><b>Annualised volatility:</b> <span style='color:#C2571B;font-weight:700'>{desc['ann_vol_pct']:.1f}%</span> — the "typical" yearly swing; oil is a rough ride by any asset's standard.</div>
<div class='insight-num'><b>Skewness {desc['skew']:.2f}:</b> — positive means a longer right tail: occasional huge up-months (the 2020 rebound).</div>
<div class='insight-num'><b>Excess kurtosis {desc['excess_kurtosis']:.1f}:</b> — how much more often extreme months occur than a bell curve predicts; anything above ~1 is "fat tails", oil sits near {desc['excess_kurtosis']:.0f}.</div>
<div class='insight-num'><b>VaR 95% / CVaR 95%:</b> <span style='color:#C2571B;font-weight:700'>{risk['VaR95']:.1f}% / {risk['CVaR95']:.1f}%</span> — in the worst 5% of months you lose at least {abs(risk['VaR95']):.0f}%, and when you land in that zone the average loss is about {abs(risk['CVaR95']):.0f}%.</div>
<div class='insight-num'><b>Maximum drawdown:</b> <span style='color:#C2571B;font-weight:700'>{risk['MaxDD']:.1f}%</span> — the deepest peak-to-trough fall an investor would have endured (2014→2016 and 2018→2020 declines).</div>
<div class='insight-num'><b>Ljung-Box p-values (lag 1):</b> <span style='color:#C2571B;font-weight:700'>{lb1:.4f} (returns) · {lbsq:.2g} (squared)</span> — squared returns' tiny p-value is the statistical fingerprint of volatility clustering.</div>

**💡 Key insights**

- Q(a): oil differs from other assets through extreme spikes, volatility clustering and event-driven regimes — all demonstrated in the charts above.
- Q(b): monthly oil returns are right-skewed and heavily fat-tailed; a normal bell curve is rejected by Jarque-Bera, KS and Anderson-Darling.
- Q(c): autocorrelation in returns is small in magnitude but collectively significant (disclosed correction of the notebook's wording), while squared returns show strong dependence — volatility predicts volatility, not direction.
- Q(d): seasonality, leverage effects and contango/backwardation remain untested literature observations — honestly labelled, not claimed.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This page answers four plain questions with numbers instead of opinions: "
    "Is oil wilder than other investments? Yes — crashes and spikes far beyond "
    "a bell curve. Do calm and stormy months cluster? Yes. Can last month "
    "predict next month's direction? Barely. What could you lose in a bad "
    "stretch? The VaR and drawdown figures say it directly. These are risk "
    "descriptions of the past — not predictions.</div>", unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("Monthly simple/log returns per selected basis; JB, SW (first-50 "
               "original convention + full sample), KS on standardised returns, "
               "AD with 5% critical value; VaR/CVaR empirical percentiles; Sharpe "
               "= (μ/σ)·√12 with rf=0 (descriptive only); Ljung-Box via statsmodels "
               "on returns and squared returns.")
