"""PAGE 4 — Data Collection & Cleaning (Step 5 + Step 6)."""
import sys, os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all

st.title("🧹 Data Collection & Cleaning")
st.caption("GWP1 Step 5 (three cleaning responsibilities on ALL data) and "
           "Step 6 (the combined sterilized dataset).")

@st.cache_data(show_spinner="Loading research dataset…")
def _research():
    return get_all()

rd = _research()

# ---------------------------------------------------------------- responsibilities
st.markdown("## Who cleaned what — and how")
a, b, c = st.columns(3)
with a:
    st.markdown("#### 👤 Student A — Extreme outliers")
    st.markdown("3×IQR **winsorisation** following Section 4.1 of Alvi (2018): "
                "values beyond Q1 − 3·IQR or Q3 + 3·IQR are **capped, not deleted**. "
                "Genuine oil-market shocks (COVID-19 crash, 2014–16 supply surge) "
                "are economically meaningful and must be retained.")
with b:
    st.markdown("#### 👤 Student B — Bad data")
    st.markdown("Negative prices where economically invalid, duplicate timestamps, "
                "invalid timestamps, stale runs, unit inconsistencies and abrupt "
                "price movements. Large moves are **flagged as events, not removed**.")
with c:
    st.markdown("#### 👤 Student C — Missing values")
    st.markdown("Sequence: **time interpolation → forward-fill → back-fill**. "
                "Series that were *entirely unavailable* are never imputed. "
                "Quarterly→monthly forward-fill (GDP) is a frequency-conversion "
                "consequence, not an imputation.")

# ---------------------------------------------------------------- outliers
st.markdown("## Student A — 3×IQR Winsorisation Log")
if len(rd.outlier_log):
    st.dataframe(rd.outlier_log, use_container_width=True, hide_index=True)
    st.caption("Fences: Q1 − 3·IQR and Q3 + 3·IQR. Capped values touched the "
               "fence; the raw observations are preserved in `raw_data.csv`.")
    st.warning("**Reproducibility note.** The submitted notebook also reported "
               "capped values for VIX (2), IndustrialProd (2), OPEC_Prod (1) "
               "and OECD_Demand (2). Those outputs were produced in an earlier "
               "data-collection session (with 26 missing futures months); on "
               "the canonical saved CSV those series fall **inside** the 3×IQR "
               "fences. This is execution-session drift in the source data, "
               "disclosed here for transparency — the GDP_Growth cap (9) "
               "reproduces exactly.")
else:
    st.info("No values beyond the 3×IQR fences.")

sel_o = st.selectbox("Inspect before/after distribution for a winsorised variable",
                     rd.outlier_log["Variable"].tolist() if len(rd.outlier_log) else [])
if sel_o:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Before winsorisation",
                                                        "After winsorisation"))
    fig.add_trace(go.Histogram(x=rd.raw[sel_o], marker_color="#6B7280",
                               name="Before"), 1, 1)
    fig.add_trace(go.Histogram(x=rd.winsorised[sel_o], marker_color="#E8842C",
                               name="After"), 1, 2)
    fig.update_layout(title=f"{sel_o} — distribution before vs after capping",
                      showlegend=False, height=380,
                      xaxis_title="Value", yaxis_title="Months")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------- bad data
st.markdown("## Student B — Bad-Data Report")
bad = rd.bad_data
k1, k2, k3 = st.columns(3)
k1.metric("Duplicate timestamps", bad["duplicate_timestamps"])
neg_total = sum(bad["negative_price_counts"].values())
k2.metric("Negative monthly prices", neg_total,
          "none in monthly data (the −$37.63 CL=F print of 2020-04-20 is an "
          "intraday event; monthly closes bottom at $18.84)" if neg_total == 0 else "")
k3.metric("Large-move months (3σ)", len(bad["large_moves"]),
          f"threshold ±{bad['large_move_threshold_pct']}%")
if bad["large_moves"]:
    lm = pd.DataFrame(bad["large_moves"])
    st.dataframe(lm, use_container_width=True, hide_index=True)
    st.info("These are the COVID-19 demand collapse and rebound (Mar–Jun 2020). "
            "Decision: **retained** — a major market movement is not automatically "
            "bad data; these prints are corroborated by market history.")
if bad["stale_runs"]:
    st.markdown("**Stale-run check (5+ identical consecutive months):**")
    st.dataframe(pd.DataFrame(bad["stale_runs"]), use_container_width=True,
                 hide_index=True)
    st.caption("GDP_Growth shows 6-month runs of identical values — the expected "
               "signature of quarterly→monthly forward-fill, **not** a data-feed fault.")

# ---------------------------------------------------------------- missing
st.markdown("## Student C — Missing-Data Treatment Report")
st.dataframe(rd.missing_report, use_container_width=True, hide_index=True)
st.warning("Entirely-unavailable series (NonOECD_Demand, US_Ref_Cap) show 180 "
           "missing before **and after** treatment — we refuse to interpolate "
           "variables that were never retrieved. GPR is likewise documented as "
           "unavailable.")

# ---------------------------------------------------------------- sterilized
st.markdown("## Step 6 — The Sterilized Dataset")
m1, m2, m3 = st.columns(3)
m1.metric("Shape", f"{rd.sterilized.shape[0]} × {rd.sterilized.shape[1]}")
m2.metric("Period", "2010-01 → 2024-12")
m3.metric("Missing after treatment",
          int(rd.sterilized.isnull().sum().sum() -
              rd.sterilized[["NonOECD_Demand", "US_Ref_Cap"]].isnull().sum().sum()),
          "excl. never-retrieved series")

st.markdown("**Key documented decisions**")
st.markdown("""
- 3×IQR winsorisation caps extremes **without deletion** → shocks stay in-sample.
- April 2020 WTI crash ($16.55 monthly avg) **retained** — legitimate COVID demand shock.
- 2014–2016 OPEC supply surge / price collapse **retained**.
- 2022 Russia–Ukraine energy-crisis data **retained**.
- Short gaps (<3 months) in EIA series: linear time interpolation.
- Series with different start dates: boundary-only back-fill.
- Quarterly GDP forward-filled to monthly — labelled as filled, never presented as true monthly data.
""")

st.download_button("⬇️ Download sterilized_data.csv",
                   rd.sterilized.to_csv().encode(), "sterilized_data.csv", "text/csv")
st.download_button("⬇️ Download raw_data.csv (unmodified)",
                   rd.raw.to_csv().encode(), "raw_data.csv", "text/csv")

st.markdown("### Cleaning log (per-transformation register)")
log = rd.outlier_log.rename(columns={"N capped": "Action"}) if len(rd.outlier_log) else pd.DataFrame()
if len(log):
    log = log.assign(Reason="3×IQR winsorisation (Alvi 2018 §4.1)",
                     Responsible="Student A — extreme outliers",
                     Evidence="Quantile fences on 180 monthly observations")
    st.dataframe(log, use_container_width=True, hide_index=True)
    st.download_button("⬇️ Download cleaning_log.csv", log.to_csv(index=False).encode(),
                       "cleaning_log.csv", "text/csv")

st.markdown("### Variable inspector — raw vs sterilized")
var = st.selectbox("Variable", [v for v in rd.raw.columns if rd.raw[v].notna().any()])
insp = pd.DataFrame({"Raw": rd.raw[var], "Sterilized": rd.sterilized[var]})
changed = insp["Raw"].round(6) != insp["Sterilized"].round(6)
insp["Changed by cleaning"] = changed.map({True: "✔ yes", False: ""})
st.dataframe(insp[insp["Changed by cleaning"] == "✔ yes"].head(50),
             use_container_width=True)
st.caption("Only rows actually modified by cleaning are shown. Raw values are "
           "never overwritten on disk.")

# ---------------- Insight panel (dynamic) ----------------
n_capped_total = int(rd.outlier_log["N capped"].sum()) if len(rd.outlier_log) else 0
n_missing_fixed = int(rd.missing_report["Missing after"].sum() -
                      rd.missing_report.loc[rd.missing_report["Method"].str.contains("never"),
                                            "Missing after"].sum())
st.divider()
st.markdown("### 🧭 Understand this page — Data Collection & Cleaning")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Values capped by 3×IQR winsorisation:</b> <span style='color:#C2571B;font-weight:700'>{n_capped_total}</span> — extreme values that sat beyond the statistical fences; they were pulled back to the fence line, never deleted.</div>
<div class='insight-num'><b>GDP_Growth capped values:</b> <span style='color:#C2571B;font-weight:700'>9</span> — the only series on the canonical dataset needing caps; its quarterly-to-monthly fill creates fat tails the fences catch.</div>
<div class='insight-num'><b>Large-move months flagged (3σ):</b> <span style='color:#C2571B;font-weight:700'>{len(rd.bad_data['large_moves'])}</span> — the COVID crash and rebound of 2020; flagged as events and deliberately RETAINED because they really happened.</div>
<div class='insight-num'><b>Missing observations after treatment:</b> <span style='color:#C2571B;font-weight:700'>{n_missing_fixed}</span> (excluding never-retrieved series) — every retrievable gap was filled by time interpolation, never by guessing.</div>
<div class='insight-num'><b>2 series never imputed:</b> <span style='color:#C2571B;font-weight:700'>NonOECD_Demand, US_Ref_Cap</span> — no data ever arrived for them; fabricating them would poison the research.</div>

**💡 Key insights**

- "Winsorise, don't delete": oil crashes are real economics — removing them would understate risk exactly when it matters most.
- Every cleaning action is logged (variable, count, fences, reason, responsible student) and exportable as `cleaning_log.csv` — the audit trail reviewers ask for.
- Raw data on disk is never modified: the sterilized dataset is always regenerable from `raw_data.csv` with one script.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This page is the app's quality-control lab. Imagine proof-reading 15 "
    "spreadsheets: capping obvious typos, flagging unbelievable numbers, and "
    "filling small gaps sensibly — while keeping a note of every change so "
    "anyone can check the work.</div>", unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("3×IQR fences per series on 180 monthly obs (Alvi 2018 §4.1); "
               "large-move flag = |pct-change| > 3σ of WTI monthly changes; "
               "missing-data sequence time→ffill→bfill; all-NaN columns "
               "protected. See core/analytics.py: winsorise_3iqr, "
               "bad_data_checks, impute_missing.")
