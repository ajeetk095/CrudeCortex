"""
CRUDECORTEX — The brain behind the barrel.
Crude oil research, forecasting & investment insights — MScFE 660 GWP1
Research: Application of Probabilistic Graphical Models in Forecasting Crude Oil Prices

Streamlit entry point. Run:  streamlit run app.py
"""
import sys, os
import streamlit as st
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.ui_components import inject_css

st.set_page_config(
    page_title="CrudeCortex — The brain behind the barrel · MScFE 660 GWP1",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

HOME = st.Page(
    "pages/1_🏠_Home_Research_Overview.py",
    title="Home — Research Overview", icon="🏠", url_path="home", default=True,
)
PROBLEM = st.Page(
    "pages/2_📖_Problem_&_Literature.py",
    title="Problem Formulation & Literature", icon="📖", url_path="problem-literature",
)
DICTIONARY = st.Page(
    "pages/3_🗂️_Data_Sources_&_Dictionary.py",
    title="Data Sources & Data Dictionary", icon="🗂️", url_path="data-dictionary",
)
CLEANING = st.Page(
    "pages/4_🧹_Data_Collection_&_Cleaning.py",
    title="Data Collection & Cleaning", icon="🧹", url_path="data-cleaning",
)
EDA = st.Page(
    "pages/5_📈_Exploratory_Data_Analysis.py",
    title="Exploratory Data Analysis", icon="📈", url_path="exploratory-analysis",
)
STYLIZED = st.Page(
    "pages/6_📊_Stylized_Facts_&_Risk.py",
    title="Stylized Facts & Risk", icon="📊", url_path="stylized-facts-risk",
)
PGM = st.Page(
    "pages/7_🕸️_PGM_Learning_Centre.py",
    title="Probabilistic Graphical Models", icon="🕸️", url_path="pgm-learning",
)
CAUSAL = st.Page(
    "pages/8_🔗_Inferred_Causality_Explorer.py",
    title="Inferred Causality Graph Explorer", icon="🔗", url_path="causality-explorer",
)
LIVE = st.Page(
    "pages/9_🛰️_Live_Oil_Market_Context.py",
    title="Live Oil Market Context", icon="🛰️", url_path="live-market",
)
FORECAST = st.Page(
    "pages/11_🔮_Forecasting_&_Investment_Insights.py",
    title="Forecasting & Investment Insights", icon="🔮", url_path="forecasting-insights",
)
ABOUT = st.Page(
    "pages/10_👤_Methodology_&_About.py",
    title="Methodology, Docs & About", icon="👤", url_path="methodology-about",
)

pg = st.navigation([
    HOME, PROBLEM, DICTIONARY, CLEANING, EDA,
    STYLIZED, PGM, CAUSAL, LIVE, FORECAST, ABOUT,
])

with st.sidebar:
    st.markdown(
        "<div style='padding:4px 4px 0 4px'>"
        "<span style='font-size:1.6em'>🧠🛢️</span> "
        "<span style='font-size:1.15em;font-weight:900;color:#C2571B'>"
        "CRUDECORTEX</span><br>"
        "<span style='font-size:.8em;font-style:italic;color:#6B7280'>"
        "The brain behind the barrel.</span></div>",
        unsafe_allow_html=True,
    )
    st.caption("Data Engineering · Energy Market Research · Risk Analytics · "
               "Probabilistic Graphical Models · Forecasting")
    st.divider()
    st.caption("**MScFE 660 — Risk Management**  \nGroup Work Project 1  \n"
               "Group 14660 — Ajeet Kumar · Frank Osei · Nha Van Tran")
    st.caption("Dataset: monthly, 2010-01 → 2024-12 · FRED · EIA · Yahoo Finance")
    st.caption("🔮 **New:** Forecasting & Investment Insights — scenario "
               "projections with confidence bands and mechanical signals "
               "(not financial advice).")
    with st.expander("📚 Quick help"):
        st.markdown("""
**New here?** Start at **Home**, then follow the pages top-to-bottom — they
follow the research journey.

- Every analytical page ends with an **🧭 Understand this page** panel that
  explains the numbers in plain language.
- Charts have hover tooltips and a **camera icon** to download as PNG.
- Use the **📅 date-range sliders** on the analysis pages to zoom in.

Full walkthrough: `USER_GUIDE.md` in the repository, or the
**Methodology, Docs & About** page.
""")

pg.run()
