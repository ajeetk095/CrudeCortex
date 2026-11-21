"""PAGE 3 — Data Sources & Interactive Data Dictionary (Step 3 + Step 4)."""
import sys, os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all, data_dictionary_df, VARIABLE_CATEGORIES

st.title("🗂️ Data Sources & Data Dictionary")
st.caption("GWP1 Step 3 (identify, import, structure, graph) and Step 4 "
           "(data dictionary + summary table).")

@st.cache_data(show_spinner="Loading research dataset…")
def _research():
    return get_all()

rd = _research()
dd = data_dictionary_df()

# Merge computed coverage stats from the raw data
for _, row in dd.iterrows():
    v = row["Variable"]
    if v in rd.raw.columns:
        s = rd.raw[v]
        dd.loc[dd["Variable"] == v, "Start date"] = (
            s.dropna().index.min().strftime("%Y-%m") if s.notna().any() else "—")
        dd.loc[dd["Variable"] == v, "End date"] = (
            s.dropna().index.max().strftime("%Y-%m") if s.notna().any() else "—")
        dd.loc[dd["Variable"] == v, "Observations"] = int(s.notna().sum())
        dd.loc[dd["Variable"] == v, "Missing observations"] = int(s.isna().sum())
        dd.loc[dd["Variable"] == v, "Missing %"] = round(float(s.isna().mean() * 100), 1)
    else:
        dd.loc[dd["Variable"] == v, ["Start date", "End date"]] = "—"
        dd.loc[dd["Variable"] == v, ["Observations", "Missing observations"]] = 0
        dd.loc[dd["Variable"] == v, "Missing %"] = 100.0

# ---------------------------------------------------------------- summary table
st.markdown("## Summary Table (report format)")
summary = dd[["Variable", "Full name", "Economic category", "Series ID / ticker",
              "Units", "Native frequency", "Analytical frequency", "Start date",
              "End date", "Observations", "Data status"]]
st.dataframe(summary, use_container_width=True, hide_index=True, height=430)
st.download_button("⬇️ Download summary table (CSV)",
                   summary.to_csv(index=False).encode(),
                   "gwp1_data_dictionary_summary.csv", "text/csv")

# ---------------------------------------------------------------- interactive
st.markdown("## Interactive Data Catalogue")
f1, f2, f3 = st.columns([2, 2, 2])
q = f1.text_input("🔍 Search variable / description / series ID")
cats = f2.multiselect("Filter by economic category",
                      sorted(dd["Economic category"].unique()))
status_opts = f3.multiselect("Filter by availability",
                             sorted(dd["Data status"].unique()))

view = dd.copy()
if q:
    m = view.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)
    view = view[m]
if cats:
    view = view[view["Economic category"].isin(cats)]
if status_opts:
    view = view[view["Data status"].str.contains("|".join(status_opts))]

st.dataframe(view, use_container_width=True, hide_index=True, height=380)
st.download_button("⬇️ Download full data dictionary (CSV)",
                   view.to_csv(index=False).encode(),
                   "gwp1_data_dictionary.csv", "text/csv")

# ---------------------------------------------------------------- missingness
st.markdown("## Missing-Data Overview (raw dataset)")
miss = rd.raw.isnull().sum()
miss = miss[miss > 0].sort_values(ascending=False)
if len(miss):
    fig = go.Figure(go.Bar(x=miss.index, y=miss.values, marker_color="#C62828"))
    fig.update_layout(title="Missing monthly observations per variable (raw, 2010–2024)",
                      xaxis_title="Variable", yaxis_title="Missing months",
                      height=350)
    st.plotly_chart(fig, use_container_width=True)
    st.warning("NonOECD_Demand and US_Ref_Cap were **completely unavailable** in "
               "the original retrieval (180/180 missing). They were **never "
               "imputed** — fabricating them would corrupt the research. The GPR "
               "(geopolitical risk) series also failed to load and is documented "
               "as unavailable.")
else:
    st.success("No missing values detected in the raw dataset.")

# ---------------------------------------------------------------- per-variable charts
st.markdown("## Variable Time-Series Charts")
plot_vars = [v for v in rd.raw.columns if rd.raw[v].notna().any()]
sel = st.selectbox("Select variable", plot_vars)
cat = VARIABLE_CATEGORIES.get(sel, "—")
unit = dd.loc[dd["Variable"] == sel, "Units"].iloc[0]
sid = dd.loc[dd["Variable"] == sel, "Series ID / ticker"].iloc[0]
src = sid.split("—")[0].strip()

fig = px.line(x=rd.sterilized.index, y=rd.sterilized[sel])
fig.data[0].line.color = "#E8842C"
fig.update_layout(title=f"{sel} — sterilized monthly series",
                  xaxis_title="Month", yaxis_title=unit, height=380)
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Category: **{cat}** · Source: **{sid}** · Units: {unit} · "
           f"After sterilization (3×IQR winsorisation + missing-data treatment). "
           f"Source attribution: {src}.")

# ---------------------------------------------------------------- lineage
st.markdown("## Data Lineage")
st.markdown("""
| Stage | Tool / rule | Output |
|---|---|---|
| Collection | FRED API (fredapi), EIA STEO API v2, yfinance | raw master CSV (180 × 15) |
| Frequency alignment | daily→monthly (last), quarterly→monthly (ffill) | aligned raw |
| Outlier treatment | 3×IQR winsorisation (Student A) | capped values |
| Bad-data checks | negative/duplicate/stale scans (Student B) | flags & event log |
| Missing-data treatment | time-interp → ffill → bfill (Student C) | sterilized CSV |
""")

# Variable inspector — raw vs sterilized
st.markdown("### Variable inspector — raw vs sterilized")
var = st.selectbox("Variable", [v for v in rd.raw.columns if rd.raw[v].notna().any()])
insp = pd.DataFrame({"Raw": rd.raw[var], "Sterilized": rd.sterilized[var]})
changed = insp["Raw"].round(6) != insp["Sterilized"].round(6)
insp["Changed by cleaning"] = changed.map({True: "✔ yes", False: ""})
st.dataframe(insp[insp["Changed by cleaning"] == "✔ yes"].head(50),
             use_container_width=True)
st.caption("Only rows actually modified by cleaning are shown. Raw values are "
           "never overwritten on disk.")
