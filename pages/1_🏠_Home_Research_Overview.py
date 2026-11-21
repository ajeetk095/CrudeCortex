"""PAGE 1 — Research Overview / Home."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import (get_all, descriptive_statistics, correlations_with_wti,
                            inferred_causality)
from theme import ORANGE, NAVY, BLUE

st.title("🛢️ CrudeCortex")
st.markdown("### *Data Engineering | Energy Market Research | Risk Analytics | "
            "Probabilistic Graphical Models*")
st.caption("MScFE 660 Risk Management — Group Work Project 1 (GWP1) · "
           "WorldQuant University · Group 14660")

@st.cache_data(show_spinner="Loading research dataset…")
def _research():
    return get_all()

rd = _research()
desc = descriptive_statistics(rd.returns)
corr = correlations_with_wti(rd.sterilized)

st.info("**What does this research investigate?**  \n"
        "It examines how economic, financial and other relevant variables are "
        "associated with crude oil price behaviour, and explores probabilistic "
        "graphical models (PGMs) as a structured framework for representing "
        "these relationships. This is **GWP1 — problem formulation and data "
        "collection**. Bayesian-network model *development* is GWP2 and "
        "results interpretation is GWP3; neither is claimed as completed here.")

st.markdown("## Research Question")
st.success("**\"How can macroeconomic, microeconomic, geopolitical and financial "
           "variables be identified, structured and analysed to understand the "
           "factors associated with global crude oil price behaviour, and how can "
           "probabilistic graphical models provide a framework for representing "
           "their relationships?\"**")

# ------------------------------------------------------------------ KPI cards
st.markdown("## Dataset at a Glance")
c1, c2, c3, c4, c5 = st.columns(5)
usable = sum(1 for v in rd.raw.columns if rd.raw[v].notna().any())
unavailable = len(rd.raw.columns) - usable
c1.metric("Observations", f"{len(rd.raw)}", "monthly")
c2.metric("Period", "2010-01 → 2024-12", "180 months")
c3.metric("Usable variables", str(usable), "of 15 collected")
c4.metric("Unavailable", str(unavailable), "never imputed")
c5.metric("Ann. volatility", f"{desc['ann_vol_pct']:.1f}%", "WTI monthly")

st.markdown("## Key Descriptive Statistics — WTI Monthly Simple Returns")
d1, d2, d3, d4 = st.columns(4)
d1.metric("Mean", f"{desc['mean_pct']:+.3f}%")
d2.metric("Std deviation", f"{desc['std_pct']:.3f}%")
d3.metric("Skewness", f"{desc['skew']:.4f}", "right tail")
d4.metric("Excess kurtosis", f"{desc['excess_kurtosis']:.3f}", "fat tails")

st.markdown("## Correlation of Key Variables with WTI Spot")
cc1, cc2 = st.columns([3, 2])
with cc1:
    top = corr.head(8).sort_values()
    fig = go.Figure(go.Bar(
        x=top.values, y=top.index, orientation="h",
        marker_color=[ORANGE if v >= 0 else BLUE for v in top.values]))
    fig.update_layout(title="Pearson correlation with WTI_Spot (monthly, sterilized data)",
                      xaxis_title="Correlation coefficient", yaxis_title="Variable",
                      height=380, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)
with cc2:
    st.markdown("**Reading this chart**")
    st.markdown("- Energy CPI co-moves most strongly with oil "
                f"({corr['CPI_Energy']:.3f}).\n"
                f"- The US dollar index is the strongest **negative** associate "
                f"({corr['USD_DXY']:.3f}) — a well-documented inverse relation.\n"
                "- Correlation measures *historical association*, **not causation**.")
    st.caption("Source: FRED, EIA STEO, Yahoo Finance — authors' calculations "
               "on the sterilized dataset.")

# ------------------------------------------------------------------ IC preview
st.markdown("## Inferred-Causality Graph (preview)")
st.caption("Statistically inferred conditional relationships — "
           "**not** proven economic causation. Full interactive explorer on "
           "the *Inferred Causality Explorer* page.")
ic = inferred_causality(rd.sterilized)
fig = go.Figure()
for (a, b) in ic.edges:
    fig.add_trace(go.Scatter(x=[0, 0], y=[0, 0], mode="lines", visible=False,
                             hovertext=f"{a} — {b}", showlegend=False))
st.info(f"Preview: the simplified procedure identifies **{len(ic.edges)} skeleton "
        f"edges** among {len(ic.variables)} variables and a WTI_Spot Markov blanket "
        f"of {{{', '.join(sorted(ic.markov_blankets['WTI_Spot']))}}}. "
        "Open the explorer page for the full interactive graph.")
st.markdown("[🔗 Open graph explorer](/causality-explorer)")

# ------------------------------------------------------------------ stages
st.markdown("## Research Stages (GWP roadmap)")
st.markdown("""
| Stage | Scope | Status in this platform |
|---|---|---|
| **GWP1** | Problem formulation, data collection, data dictionary, cleaning, sterilization, EDA, stylized facts, PGM theory, inferred-causality pseudocode | ✅ **Main scope — implemented & reproducible** |
| **GWP2** | Bayesian-network methodology and model development | 🔜 Next academic stage — described, not claimed complete |
| **GWP3** | Results interpretation and model improvement | 🔜 Later stage — not implemented |
""")

st.markdown("## What can visitors explore?")
e1, e2, e3 = st.columns(3)
with e1:
    st.markdown("- Crude oil price history\n- Macro & financial indicators\n"
                "- Data collection sources\n- Data quality & cleaning")
with e2:
    st.markdown("- Statistical properties of oil returns\n- Variable correlations\n"
                "- Bayesian-network concepts\n- Markov chains & blankets")
with e3:
    st.markdown("- Inferred-causality structure\n- Live market context "
                "(monitoring only)\n- Downloadable datasets & dictionary\n"
                "- Full methodology & documentation")

st.markdown("## Data Sources")
s1, s2, s3 = st.columns(3)
s1.markdown("[**FRED** — Federal Reserve Economic Data](https://fred.stlouisfed.org/)\n\n"
            "Macro & financial series: WTISPLC, INDPRO, CPIENGSL, DTWEXBGS, GDP growth.")
s2.markdown("[**EIA Open Data / STEO**](https://www.eia.gov/opendata/)\n\n"
            "Production, demand and inventory series (OPEC, Non-OPEC, OECD).")
s3.markdown("[**Yahoo Finance**](https://finance.yahoo.com/)\n\n"
            "Futures and market indices: CL=F, BZ=F, ^VIX, ^GSPC.")

st.divider()
st.markdown("### 🧭 Understand this page — Home / Research Overview")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>180 monthly observations:</b> <span style='color:#C2571B;font-weight:700'>2010-01 → 2024-12</span> — every dot is one month of oil-market history, the exact window the group studied.</div>
<div class='insight-num'><b>15 collected → 13 usable variables:</b> <span style='color:#C2571B;font-weight:700'>{usable} usable</span> — two series could never be retrieved (Non-OECD demand, US refinery capacity) and were honestly left out, never faked.</div>
<div class='insight-num'><b>Mean monthly return {desc['mean_pct']:+.2f}%:</b> — in a typical month oil moved up by about half a percent, on average, over 15 years.</div>
<div class='insight-num'><b>Annualised volatility {desc['ann_vol_pct']:.1f}%:</b> — a "typical year" for oil swings by about a third in value — far more than a savings account, roughly 2–3× a stock index.</div>
<div class='insight-num'><b>Skewness {desc['skew']:.2f} / Excess kurtosis {desc['excess_kurtosis']:.1f}:</b> — more upside spikes than downside (skew > 0), but far more extreme months than a normal bell curve would allow (kurtosis ≫ 0).</div>
<div class='insight-num'><b>Skeleton of {len(ic.edges)} edges:</b> — the statistical map connecting oil to its closest companion variables; explored interactively on the Inferred Causality page.</div>

**💡 Key insights**

- Oil's 15-year history is a story of regimes: the 2014–16 supply glut, the 2020 pandemic collapse, the 2022 energy crisis — visible directly in the Home price chart.
- The US dollar is oil's strongest *inverse* companion ({corr['USD_DXY']:.2f}): when the dollar strengthens, oil historically weakens.
- The data show behaviour, not destiny: GWP1 builds the foundation; forecasting is GWP2's job.
- Every figure on this platform is computed live from the bundled dataset — nothing is typed in by hand.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This platform is an interactive atlas of the oil market. It shows what "
    "drives oil prices, how wild the ride has been, and how statisticians map "
    "the relationships between oil, the dollar, production and the economy. It "
    "explains the past and organises the data — it does not predict tomorrow's price."
    "</div>", unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("All values from core/analytics.py: monthly simple returns of FRED "
               "WTISPLC after 3×IQR winsorisation and missing-data treatment; "
               "Pearson correlations on the sterilized panel; skeleton from the "
               "notebook's PC-style procedure (α=0.05, single-variable "
               "conditioning sets). See the Methodology page.")
st.caption("⚠️ This platform presents descriptive research and data analytics. "
           "It does **not** provide forecasts, trading signals or investment advice.")
