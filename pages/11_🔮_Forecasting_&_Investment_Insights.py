"""PAGE 11 — Forecasting & Investment Insights (platform extension beyond GWP1)."""
import sys, os
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all, descriptive_statistics
from core.forecasting import (prepare_series, blend_live_anchor, fit_forecasts,
                              backtest, investment_signals, INSTRUMENT_MAP, HORIZONS)

st.title("🔮 Forecasting & Investment Insights")
st.caption("Platform extension beyond the GWP1 academic scope — transparent "
           "statistical scenario projections and rule-based signals.")

st.error("## ⚠️ Not financial advice\n"
         "**Everything on this page is a statistical extrapolation of past data "
         "under explicit assumptions.** Models extrapolate history; they cannot "
         "anticipate wars, OPEC decisions, recessions or supply shocks. Projections "
         "are *scenarios*, not predictions. Signals are mechanical rules, not "
         "recommendations. Do your own research and consult a licensed advisor "
         "before investing.", icon="🚨")

@st.cache_data(show_spinner="Preparing series and fitting models…")
def _prep():
    rd = get_all()
    return rd, prepare_series(rd.sterilized)

rd, s_hist = _prep()
s, live_info = blend_live_anchor(s_hist)

# ------------------------------------------------------------------ controls
c1, c2, c3 = st.columns([2, 2, 2])
bull_ann = c1.slider("🐂 Bull scenario — added annual drift", -30, 30, 10,
                     format="+%d%%", help="Applied on top of the model path, compounding monthly.") / 100
bear_ann = c2.slider("🐻 Bear scenario — subtracted annual drift", -30, 30, 10,
                     format="−%d%%", help="Subtracted from the model path, compounding monthly.") / 100
anchor = c3.radio("Series anchor", ["Historical monthly (FRED)",
                                    "Blend with latest CL=F close (proxy)"],
                  horizontal=True)
if anchor.startswith("Blend"):
    s_use, info = blend_live_anchor(s_hist)
else:
    s_use, info = s_hist, {"note": "Historical monthly series only."}
st.caption(info["note"])

fr = fit_forecasts(s_use, bull_ann, -abs(bear_ann) if bear_ann > 0 else bear_ann)
bt = backtest(s_use, 12)
book = investment_signals(s_use, fr)

# ------------------------------------------------------------------ backtest
st.markdown("## 1️⃣ Model validation — walk-forward backtest")
st.caption(f"Both models were fitted on data through {bt['train_end']} and asked "
           f"to forecast the held-out period ({bt['test_start']} → {bt['test_end']}) "
           "before ever seeing it. Error is scored on that unseen window.")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Holt damped-trend MAPE", f"{bt['holt_mape']:.1f}%",
          f"direction hit {bt['holt_dir_hit']:.0f}%")
m2.metric("Linear-trend MAPE", f"{bt['linear_mape']:.1f}%",
          f"direction hit {bt['linear_dir_hit']:.0f}%")
m3.metric("Better model", "Holt" if bt["holt_mape"] < bt["linear_mape"] else "Linear",
          "on held-out error")
m4.metric("Residual σ (monthly)", f"${fr.resid_sigma:.2f}", "drives the bands")

fig = make_subplots(rows=1, cols=1)
fig.add_scatter(x=bt["train"].index, y=bt["train"].values, name="Training data",
                line=dict(color="#1F6FB2", width=1.6))
fig.add_scatter(x=bt["actual"].index, y=bt["actual"].values, name="Actual (held out)",
                line=dict(color="#1A2733", width=2.4))
fig.add_scatter(x=bt["actual"].index, y=bt["holt_fc"], name="Holt forecast",
                line=dict(color="#E8842C", width=2, dash="dash"))
fig.add_scatter(x=bt["actual"].index, y=bt["linear_fc"], name="Linear forecast",
                line=dict(color="#7B1FA2", width=1.6, dash="dot"))
fig.update_layout(title=f"Backtest — out-of-sample forecast vs actual "
                        f"({bt['test_start']} → {bt['test_end']})",
                  xaxis_title="Month", yaxis_title="USD per barrel", height=400)
st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------------ projections
st.markdown("## 2️⃣ Scenario projections — 1, 3, 6 and 12 months ahead")
show_anchor = anchor.startswith("Blend")
hist_tail = s_use.iloc[-36:] if show_anchor else s_hist.iloc[-36:]
hist_color_name = "FRED monthly + CL=F anchor" if show_anchor else "FRED monthly average"

fig = go.Figure()
fig.add_scatter(x=hist_tail.index, y=hist_tail.values, name=f"History ({hist_color_name})",
                line=dict(color="#1F6FB2", width=2.2))
x_f = fr.future_index
fig.add_trace(go.Scatter(x=x_f, y=fr.base + fr.band95, name="95% band (upper)",
                         line=dict(width=0), hoverinfo="skip"))
fig.add_trace(go.Scatter(x=x_f, y=fr.base - fr.band95, name="95% band (lower)",
                         fill="tonexty", fillcolor="rgba(232,132,44,0.12)",
                         line=dict(width=0), hoverinfo="skip"))
fig.add_trace(go.Scatter(x=x_f, y=fr.base + fr.band80, name="80% band (upper)",
                         line=dict(width=0), hoverinfo="skip"))
fig.add_trace(go.Scatter(x=x_f, y=fr.base - fr.band80, name="80% band (lower)",
                         fill="tonexty", fillcolor="rgba(232,132,44,0.18)",
                         line=dict(width=0), hoverinfo="skip"))
fig.add_scatter(x=x_f, y=fr.bull, name=f"🐂 Bull ({bull_ann:+.0%}/yr)",
                line=dict(color="#2E7D32", width=1.8, dash="dot"))
fig.add_scatter(x=x_f, y=fr.base, name="Base (Holt damped)",
                line=dict(color="#E8842C", width=3))
fig.add_scatter(x=x_f, y=fr.bear, name=f"🐻 Bear (−{abs(bear_ann):.0%}/yr)",
                line=dict(color="#C62828", width=1.8, dash="dot"))
fig.add_scatter(x=x_f, y=fr.linear, name="Linear-trend baseline",
                line=dict(color="#7B1FA2", width=1.4, dash="dash"))
fig.update_layout(title="WTI scenario projection with confidence bands",
                  xaxis_title="Month", yaxis_title="USD per barrel", height=480)
st.plotly_chart(fig, use_container_width=True)

rows = []
for i, h in enumerate(HORIZONS):
    rows.append({
        "Horizon": f"{h} month" + ("s" if h > 1 else ""),
        "Base": f"${fr.base[i]:.2f}",
        "80% band": f"${fr.base[i]-fr.band80[i]:.2f} – ${fr.base[i]+fr.band80[i]:.2f}",
        "95% band": f"${fr.base[i]-fr.band95[i]:.2f} – ${fr.base[i]+fr.band95[i]:.2f}",
        f"Bull ({bull_ann:+.0%}/yr)": f"${fr.bull[i]:.2f}",
        f"Bear (−{abs(bear_ann):.0%}/yr)": f"${fr.bear[i]:.2f}",
        "Base vs last": f"{(fr.base[i]/fr.last_value-1)*100:+.1f}%",
    })
tbl = pd.DataFrame(rows)
st.dataframe(tbl, use_container_width=True, hide_index=True)
st.download_button("⬇️ Download projection table (CSV)", tbl.to_csv(index=False).encode(),
                   "wti_projections.csv", "text/csv")

# ------------------------------------------------------------------ signals
st.markdown("## 3️⃣ Investment insights — mechanical signals")
comp_col = {"Accumulate / bullish tilt": "#2E7D32", "Hold / neutral": "#B45309",
            "Reduce / cautious": "#C62828"}.get(book.composite_stance, "#6B7280")
st.markdown(f"""
<div style='background:linear-gradient(135deg,#FFF8F0,#FDF0E0);border:2px solid {comp_col};
border-radius:16px;padding:18px 22px;margin:8px 0'>
<span style='font-size:1.05em;color:{comp_col};font-weight:800'>
🧭 Composite stance for crude-oil exposure: {book.composite_stance}</span>
<br><span style='font-size:.9em'>Trend/momentum/MA score: {book.composite_score:+d} ·
{"⚠ volatility modifier applied" if any(s['stance']=='Applied' for s in book.signals) else "no volatility override"}</span>
</div>""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
sig = book.signals
s1.metric("📈 Trend (12m proj.)", sig[0]["stance"], sig[0]["reading"].split(" projected")[0])
s2.metric("⚡ Momentum (6m)", sig[1]["stance"], sig[1]["reading"].split(" over")[0])
s3.metric("📐 MA crossover", sig[2]["stance"], "12m vs 36m avg")
s4.metric("🌊 Volatility regime", sig[3]["stance"], f"{float(sig[3]['reading'].split('%')[0]):.0f}% ann.")

st.markdown("**Why each signal reads this way**")
for sg in book.signals:
    with st.expander(f"{sg['name']} — {sg['stance']} · {sg['reading']}"):
        st.markdown(sg["reason"])

st.markdown("### What this would mean for common crude-oil instruments")
st.dataframe(pd.DataFrame(INSTRUMENT_MAP,
                          columns=["Instrument", "Character", "Caveat under this stance"]),
             use_container_width=True, hide_index=True)

st.markdown("""
<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>
Think of this page as a weather forecast for oil prices. The orange line is
the "most likely" path if the recent pattern simply continues; the shaded band
is the range of realistic outcomes (wider = more uncertainty further out); the
green and red dotted lines are rosier and gloomier storylines you control with
the sliders. The signals are simple rule-of-thumb checks a analyst might run —
they describe conditions, they don't know the future.</div>""", unsafe_allow_html=True)

with st.expander("🔬 Technical detail — how every number here is produced"):
    st.caption("""
Models: (1) damped-trend Holt exponential smoothing (statsmodels
ExponentialSmoothing, trend='add', damped_trend=True, optimized MLE) —
primary; (2) OLS linear trend on the time index — baseline. Bands: base ±
z·σ_resid·√h with z = 1.2816 (80%) and 1.96 (95%), σ from in-sample residuals.
Scenarios: base compounded at the user's bull/bear annual drift
(+10%/−10% defaults). Backtest: fit on all data before the last 12 months,
score MAPE and directional hit-rate on the held-out year. Signals: 12m
projected slope (>±2% band), 6m momentum (>±3% band), 12m-vs-36m monthly
average crossover, 12m annualised volatility vs full-sample median
(>1.25× → position-size penalty caps the composite at Hold). Series: FRED
WTISPLC monthly, optionally anchored to the latest CL=F close. All computed
live — nothing hardcoded.""")

st.divider()
st.caption("🚨 Reminder: statistical extrapolations under assumptions — not "
           "predictions, not advice. Markets can and do break any model.")
