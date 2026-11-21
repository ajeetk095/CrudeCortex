"""PAGE 5 — Exploratory Data Analysis (Step 7)."""
import sys, os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all, rolling_stats

st.title("📈 Exploratory Data Analysis")
st.caption("GWP1 Step 7 — distributional (Student A), time-series (Student B) "
           "and multivariate (Student C) analysis. Each student covers ALL data.")

@st.cache_data(show_spinner="Loading research dataset…")
def _research():
    return get_all()

rd = _research()
import copy as _copy
st.markdown("#### 🎛️ Global filters — every chart below respects these")
f1c, f2c = st.columns([2, 1])
dmin, dmax = rd.sterilized.index.min().date(), rd.sterilized.index.max().date()
drange = f1c.slider("📅 Date range", value=(dmin, dmax), min_value=dmin, max_value=dmax)
_m = (rd.sterilized.index >= pd.Timestamp(drange[0])) & (rd.sterilized.index <= pd.Timestamp(drange[1]))
rd = _copy.copy(rd)
rd.sterilized = rd.sterilized.loc[_m].copy()
rd.returns = rd.returns[(rd.returns.index >= pd.Timestamp(drange[0])) &
                        (rd.returns.index <= pd.Timestamp(drange[1]) + pd.offsets.MonthEnd(0))]
rd.log_returns = rd.log_returns[(rd.log_returns.index >= pd.Timestamp(drange[0])) &
                                (rd.log_returns.index <= pd.Timestamp(drange[1]) + pd.offsets.MonthEnd(0))]
ster = rd.sterilized
f2c.metric("Months in view", f"{len(ster)}")
if len(ster) < 5:
    st.warning("Selected range is too short for meaningful statistics — full period restored.")
    rd = _research()
    ster = rd.sterilized
ster_r = ster.copy()
ster_r["WTI_Return"] = ster["WTI_Spot"].pct_change()

tab_a, tab_b, tab_c = st.tabs(["🔴 Student A — Distributional",
                               "🔵 Student B — Time series",
                               "🟣 Student C — Multivariate"])

with tab_a:
    st.markdown("### Distributions of key variables")
    dist_vars = st.multiselect("Variables", [v for v in ster.columns if ster[v].notna().any()],
                               default=["WTI_Spot", "VIX", "CPI_Energy", "GDP_Growth"])
    if not dist_vars:
        st.info("👆 Select at least one variable above to display distributional charts.")
    for v in dist_vars:
        fig = make_subplots(rows=1, cols=2, column_widths=[2, 1],
                            specs=[[{"type": "xy"}, {"type": "box"}]])
        fig.add_trace(go.Histogram(x=ster[v].dropna(), nbinsx=30, name=v,
                                   marker_color="#E8842C", showlegend=False), 1, 1)
        fig.add_trace(go.Box(y=ster[v].dropna(), name="", marker_color="#1F6FB2",
                             showlegend=False), 1, 2)
        fig.update_layout(title=f"{v} — histogram & boxplot", height=300,
                          xaxis_title=v, yaxis_title="Months")
        st.plotly_chart(fig, use_container_width=True)
    if dist_vars:
        st.markdown("### Descriptive statistics")
        st.dataframe(ster[dist_vars].describe().round(3), use_container_width=True)

    st.markdown("### Return distribution (WTI monthly simple returns)")
    ret = rd.returns
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=ret * 100, nbinsx=40, histnorm="probability density",
                               name="Observed", marker_color="#E8842C", opacity=0.75))
    xs = np.linspace(ret.min() * 100 - 5, ret.max() * 100 + 5, 300)
    from scipy import stats as sstats
    fig.add_scatter(x=xs, y=sstats.norm.pdf(xs, ret.mean() * 100, ret.std() * 100),
                    name="Normal fit", line=dict(color="#1A2733", width=2))
    fig.update_layout(title="WTI monthly simple returns vs fitted normal — "
                            "right-skewed with pronounced fat tails",
                      xaxis_title="Return (%)", yaxis_title="Density", height=380)
    st.plotly_chart(fig, use_container_width=True)

with tab_b:
    st.markdown("### Price history")
    fig = go.Figure()
    fig.add_scatter(x=ster.index, y=ster["WTI_Spot"], name="WTI Spot (FRED WTISPLC)",
                    line=dict(color="#E8842C", width=2))
    if "Brent" in ster.columns:
        fig.add_scatter(x=ster.index, y=ster["Brent"], name="Brent (BZ=F)",
                        line=dict(color="#1F6FB2", width=1.5))
    if "WTI_Futures" in ster.columns:
        fig.add_scatter(x=ster.index, y=ster["WTI_Futures"], name="WTI Futures (CL=F)",
                        line=dict(color="#2E7D32", width=1, dash="dot"))
    fig.update_layout(title="Crude oil prices, monthly 2010–2024 (USD/bbl)",
                      xaxis_title="Month", yaxis_title="USD per barrel", height=400)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Visible regimes: 2014–16 OPEC supply surge & price collapse; "
               "Apr-2020 COVID demand collapse; 2022 Russia–Ukraine energy crisis. "
               "Source: FRED, Yahoo Finance (EIA).")

    st.markdown("### Returns & rolling statistics")
    rs = rolling_stats(rd.returns, 12)
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("WTI monthly simple return (%)",
                                        "Rolling 12-month volatility (annualised)"),
                        vertical_spacing=0.12)
    fig.add_trace(go.Bar(x=rd.returns.index, y=rd.returns * 100, name="Return",
                         marker_color=["#C62828" if v < 0 else "#2E7D32"
                                       for v in rd.returns], showlegend=False), 1, 1)
    fig.add_trace(go.Scatter(x=rs.index, y=rs["Rolling std (ann.)"] * 100,
                             name="12m rolling vol", line=dict(color="#1F6FB2", width=2),
                             showlegend=False), 2, 1)
    fig.update_layout(height=520)
    fig.update_yaxes(title_text="%", row=1, col=1)
    fig.update_yaxes(title_text="%", row=2, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Supply, demand & inventory (EIA STEO)")
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("OPEC production (Mb/d)", "Non-OPEC production (Mb/d)",
                                        "OECD demand (Mb/d)", "OECD inventories (million bbl)"))
    for (v, r, c) in [("OPEC_Prod", 1, 1), ("NonOPEC_Prod", 1, 2),
                      ("OECD_Demand", 2, 1), ("OECD_Inventory", 2, 2)]:
        fig.add_trace(go.Scatter(x=ster.index, y=ster[v], name=v,
                                 line=dict(color="#E8842C", width=1.8), showlegend=False),
                      r, c)
    fig.update_layout(height=600, title="Global oil balances — partly STEO estimates")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Macroeconomic drivers")
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("CPI Energy (1982-84=100)", "Industrial production (2017=100)",
                                        "USD trade-weighted index", "US real GDP growth (%, q)"))
    for (v, r, c) in [("CPI_Energy", 1, 1), ("IndustrialProd", 1, 2),
                      ("USD_DXY", 2, 1), ("GDP_Growth", 2, 2)]:
        fig.add_trace(go.Scatter(x=ster.index, y=ster[v], name=v,
                                 line=dict(color="#1F6FB2", width=1.8), showlegend=False),
                      r, c)
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("GDP_Growth is quarterly data forward-filled to monthly — steps, "
               "not genuine monthly variation. Source: FRED.")

with tab_c:
    num = [v for v in ster.columns if ster[v].notna().sum() > 60 and v not in
           ("NonOECD_Demand", "US_Ref_Cap", "GDP_Growth")]
    st.markdown("### Correlation heatmap")
    fig = px.imshow(ster[num + ["GDP_Growth"]].corr().round(2),
                    color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                    aspect="auto", text_auto=True)
    fig.update_layout(height=640, title="Pearson correlation matrix — sterilized monthly data")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Scatter explorer")
    c1, c2 = st.columns(2)
    xvar = c1.selectbox("X variable", num, index=6)
    yvar = c2.selectbox("Y variable", num, index=0)
    df2 = ster[[xvar, yvar]].dropna()
    if len(df2) < 5:
        st.info("Not enough observations in the selected date range for this pair — "
                "widen the 📅 slider above.")
    else:
        fig = px.scatter(df2, x=xvar, y=yvar, trendline="ols",
                         color_discrete_sequence=["#E8842C"])
        r_val = df2.corr().iloc[0, 1]
        fig.update_layout(title=f"{yvar} vs {xvar} — Pearson r = {r_val:.3f}",
                          height=430)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("⬇️ Download this pair (CSV)",
                           df2.to_csv().encode(), f"scatter_{xvar}_{yvar}.csv", "text/csv")
    st.caption("Association ≠ causation. Trendline is descriptive OLS.")

    st.markdown("### Pairplot (key variables)")
    keys = ["WTI_Spot", "CPI_Energy", "USD_DXY", "VIX", "SP500"]
    fig = px.scatter_matrix(ster[keys].dropna(), dimensions=keys, height=640)
    fig.update_traces(marker=dict(size=3, color="#E8842C"), diagonal_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    d1b, d2b = st.columns(2)
    d1b.download_button("⬇️ Download filtered dataset (CSV)",
                        ster.to_csv().encode(), "gwp1_filtered_dataset.csv", "text/csv")
    d2b.download_button("⬇️ Download correlation matrix (CSV)",
                        ster[num + ["GDP_Growth"]].corr().round(4).to_csv().encode(),
                        "gwp1_correlation_matrix.csv", "text/csv")

# ---------------- Insight panel (dynamic) ----------------
_corr_full = ster[[c for c in ster.columns if ster[c].notna().sum() > 60
                   and c not in ("NonOECD_Demand", "US_Ref_Cap", "GDP_Growth")]].corr()
_pair = _corr_full["WTI_Spot"].drop("WTI_Spot").abs().idxmax()
_r_val = _corr_full.loc[_pair, "WTI_Spot"]
_ann_vol_now = float(rd.returns.std() * np.sqrt(12) * 100) if len(rd.returns) > 2 else float("nan")
st.divider()
st.markdown("### 🧭 Understand this page — Exploratory Data Analysis")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Months in view:</b> <span style='color:#C2571B;font-weight:700'>{len(ster)}</span> — controlled by the 📅 slider above; every chart on this page recomputes instantly on the filtered window.</div>
<div class='insight-num'><b>Strongest absolute correlation with WTI:</b> <span style='color:#C2571B;font-weight:700'>{_pair} (r = {_r_val:+.2f})</span> — the variable that historically moves most closely (positively or negatively) with oil in your selected window.</div>
<div class='insight-num'><b>Annualised volatility in view:</b> <span style='color:#C2571B;font-weight:700'>{_ann_vol_now:.1f}%</span> — how wildly oil swung per year within the selected range.</div>
<div class='insight-num'><b>Correlation heatmap:</b> — red cells = move together, blue = move oppositely; it is the one-glance summary of all inter-relationships.</div>

**💡 Key insights**

- Students A, B and C each analyse ALL the data, just through different lenses: shapes (distributions), journeys (time series) and relationships (multivariate).
- The scatter explorer lets you test any pair yourself — with a downloadable CSV of exactly what you see.
- Correlation heatmaps are symmetric and unit-free: perfect for spotting surprises (e.g. the dollar-oil inverse link) before any modelling.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This is the photo album of the data: what each variable looks like on "
    "its own, how it moved over time, and how it dances with the others. "
    "Move the date slider and watch every chart re-draw — you are doing your "
    "own exploration, no coding needed.</div>", unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("Histograms/boxplots on the sterilized panel; ACF via unbiased "
               "estimator with 1.96/√n bands; OLS trendlines via Plotly statsmodels "
               "bridge; Pearson correlations on complete cases of the filtered window.")
