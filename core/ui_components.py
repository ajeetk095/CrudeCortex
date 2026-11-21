"""Reusable UI components: colourful KPI cards, section headers and the
plain-language INSIGHT PANEL used at the bottom of every analytical page.
All values are passed in DYNAMICALLY from computed data — never hardcoded."""
import streamlit as st


def inject_css() -> None:
    st.markdown("""
<style>
    /* ---------- global look & feel ---------- */
    .stApp { background: linear-gradient(180deg,#FBF9F5 0%,#F4F1EC 60%,#EEF3F7 100%); }
    h1 { background: linear-gradient(90deg,#E8842C,#C2571B);
         -webkit-background-clip: text; -webkit-text-fill-color: transparent;
         font-weight: 900 !important; padding-bottom: 4px; }
    [data-testid="stMetric"] {
        background: linear-gradient(135deg,#FFFFFF 0%,#FDF3E7 100%);
        border: 1px solid #EAD9C3; border-radius: 14px; padding: 14px 16px;
        box-shadow: 0 2px 8px rgba(26,39,51,.06); }
    [data-testid="stMetricLabel"] p { font-size: .82rem !important; color:#5B6470 !important; }
    [data-testid="stMetricValue"] { font-weight: 800 !important; color:#1A2733 !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #EFE9DF; border-radius: 10px 10px 0 0; padding: 8px 18px; }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg,#E8842C,#F0A050); color: white; }
    .stDownloadButton > button, div.stButton > button {
        border-radius: 10px; border: 1.5px solid #E8842C; color: #B35A10; font-weight: 600; }
    div.stButton > button:hover, .stDownloadButton > button:hover {
        background: #E8842C; color: white; }
    .insight-card {
        background: linear-gradient(135deg,#FFF8F0 0%,#FDF0E0 100%);
        border: 1.5px solid #F0C896; border-radius: 16px; padding: 18px 22px; }
    .insight-plain {
        background: linear-gradient(90deg,#EAF7EC 0%,#F2FBF3 100%);
        border-left: 5px solid #2E7D32; border-radius: 10px; padding: 14px 18px;
        margin-top: 12px; }
    .insight-num {
        background: #FFFFFF; border: 1px solid #EAD9C3; border-radius: 12px;
        padding: 10px 14px; margin: 4px 0; }
    .insight-num b { color: #C2571B; }
</style>""", unsafe_allow_html=True)


def kpi_row(items):
    """items: list of (label, value, delta|None, help|None)."""
    cols = st.columns(len(items))
    for c, it in zip(cols, items):
        label, value = it[0], it[1]
        delta = it[2] if len(it) > 2 else None
        help_txt = it[3] if len(it) > 3 else None
        c.metric(label=label, value=value, delta=delta,
                 delta_color="off" if delta and str(delta).startswith(("≈", " ", "~")) else "normal",
                 help=help_txt)


def insight_panel(page, numbers, insights, plain, technical):
    """Bottom-of-page explainer rendered on every insightful page.

    page      : short page name shown in the panel title
    numbers   : list of (figure label, value, what it means) — dynamic values
    insights  : list of insight bullets
    plain     : one-paragraph summary for non-technical readers
    technical : technical details shown inside an expander
    """
    st.divider()
    st.markdown("### 🧭 Understand this page — " + page)
    st.caption("Every key number explained: what it is, what it means, and why it matters.")

    st.markdown("**📏 The numbers & what they mean**")
    for label, value, meaning in numbers:
        st.markdown(
            f"<div class='insight-num'><b>{label}:</b> <span style='color:#C2571B;"
            f"font-weight:700'>{value}</span> &nbsp;—&nbsp; {meaning}</div>",
            unsafe_allow_html=True)

    st.markdown("**💡 Key insights**")
    for i in insights:
        st.markdown(f"- {i}")

    st.markdown(
        "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>" + plain +
        "</div>", unsafe_allow_html=True)

    with st.expander("🔬 Technical detail — how these numbers were produced"):
        st.caption(technical)
