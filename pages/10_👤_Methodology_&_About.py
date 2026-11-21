"""PAGE 10 — Methodology, Documentation & About the Developer."""
import sys, os
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.title("👤 Methodology, Documentation & About")
st.caption("GWP1 Step 10 supporting material, project documentation, "
           "security practices and the developer profile.")

tab_m, tab_d, tab_s, tab_a = st.tabs(["🧪 Methodology & limitations",
                                      "📄 Documents & downloads",
                                      "🔒 Security practices",
                                      "👨‍💻 About the developer"])

with tab_m:
    st.markdown("""
## Research methodology (ten official steps)

| Step | What was done | Where to see it |
|---|---|---|
| 1 | Individual review of Alvi (2018) + structured literature review | Problem & Literature |
| 2 | Group problem formulation (2–3 pages, Questions A–C) | Problem & Literature |
| 3 | Macro / micro / geopolitical / financial data identified, imported, structured, graphed | Data Sources & Dictionary |
| 4 | Full data dictionary + report summary table | Data Sources & Dictionary |
| 5 | Student A/B/C cleaning: outliers, bad data, missing values — on ALL data | Data Collection & Cleaning |
| 6 | Combined sterilized dataset with documented decisions | Data Collection & Cleaning |
| 7 | Distributional, time-series and multivariate EDA | Exploratory Data Analysis |
| 8 | The four stylized-fact questions with tests | Stylized Facts & Risk |
| 9 | Three two-page PGM theory summaries | PGM Learning Centre |
| 10 | Group pseudocode for Algorithm 1: Inferred Causality + reproduction | Inferred Causality Explorer |

**Reproducibility.** The app reuses one analytical core (`core/analytics.py`)
for the notebook and the platform; the raw master CSV is preserved untouched and
the sterilized dataset is regenerated from it deterministically.

## Known limitations (disclosed)
1. **Return autocorrelation** — Ljung–Box rejects no-autocorrelation at all
   tested lags; "near-zero autocorrelation" is a magnitude statement, and the
   platform presents the corrected interpretation.
2. **Normality tests** — the original Shapiro–Wilk used only 50 observations
   and did not reject; both the original and full-sample results are shown.
3. **April 2020 negative print** — the −$37.63 intraday CL=F event does not
   appear in monthly data (monthly futures minimum $18.84). No fabricated
   negative monthly price is introduced.
4. **Return labels** — all headline statistics use **simple** returns; log
   returns are computed separately and labelled as such.
5. **Pseudocode vs implementation** — the executed algorithm restricts
   conditioning sets to single variables; the general pseudocode's extra
   phases are documented, not claimed as implemented.
6. **Untested stylized facts** — seasonality, leverage effects and
   contango/backwardation are labelled untested literature observations.
7. **EIA estimates** — STEO series partly contain estimates/forecasts;
   freshness labels disclose this.
8. **Unavailable variables** — NonOECD_Demand, US_Ref_Cap and GPR were never
   retrieved and were **never imputed**.
""")

with tab_d:
    st.markdown("## Project documents")
    c1, c2, c3 = st.columns(3)
    c1.markdown("📄 **Official GWP1 assignment**  \n  `documents/MScFE_660_Risk_Management_Group_Work_Project_1.pdf`")
    c2.markdown("📄 **Group report**  \n  `documents/MScFE 660_GWP1_14660_Report.pdf`")
    c3.markdown("📄 **Alvi (2018) dissertation**  \n  `documents/Alvi_2018_PGM_Crude_Oil.pdf`")
    try:
        with open("documents/MScFE 660_GWP1_14660_Report.pdf", "rb") as f:
            st.download_button("⬇️ Download the full group report",
                               f.read(), "MScFE 660_GWP1_14660_Report.pdf",
                               "application/pdf")
    except Exception:
        st.info("Original report file not bundled in this build.")
    st.markdown("""
## Project architecture
```text
CrudeCortex-GWP1/
├── app.py                      # Streamlit entry point (10-page navigation)
├── core/analytics.py           # single analytical source of truth
├── pages/                      # the ten application pages
├── data/raw_data.csv           # unmodified raw master dataset (180 × 15)
├── documents/                  # assignment, report, dissertation PDFs
├── notebooks/                  # original executed notebook + HTML export
├── scripts/                    # collect / sterilize / reproduce utilities
├── tests/                      # reproduction & unit tests
├── requirements.txt            # Python 3.14-ready dependencies
├── .streamlit/config.toml      # theme & server settings
├── README.md · LICENSE · SECURITY.md · Dockerfile · .env.example
```

## User instructions
1. Start at **Home** for the research question and headline statistics.
2. Read the **Problem & Literature** page in *Plain-English* first, then *Technical*.
3. Inspect data provenance in the **Data Dictionary**, then the cleaning trail.
4. Study **EDA** and **Stylized Facts** — every number shows formula, meaning and limitation.
5. Learn PGM theory, then explore the **Inferred Causality** graph interactively.
6. Check current conditions in **Live Market Context** (monitoring only).
""")

with tab_s:
    st.markdown("""
## Security assessment & production safety

No application can honestly be guaranteed hack-proof; the objective is to
minimise risk, test implemented controls and document residual weaknesses.

**Implemented controls**
- **Input protection** — widget-constrained parameters, strict types, bounded
  date ranges, no free-form SQL (pandas only), rejection of unexpected fields.
- **Secret management** — API keys via environment variables / `st.secrets`
  only; `.env.example` documents every variable; no credentials in the repo;
  nothing secret reaches the client bundle.
- **File protection** — documents served from a whitelisted `documents/`
  directory only; no path traversal; no user file upload; no code execution
  from user input; no pickle deserialisation.
- **Notebook protection** — the bundled notebook is a *static, pre-executed
  export*; opening it in the viewer never executes code.
- **Network** — HTTPS enforced by the host (Streamlit Cloud); XSRF protection
  enabled; usage telemetry disabled.
- **Logging & errors** — safe, generic error messages; no stack traces or
  secrets surfaced to visitors.
- **Dependency hygiene** — pinned-compatible versions; run `pip-audit`,
  `bandit -r .`, `ruff check .` and `npm audit` (no JS frontend in this build)
  before each release.
- **Container** (optional Docker path) — non-root user, single exposed port.

**Residual limitations.** Public dashboards can be scraped; Yahoo/FRED
availability depends on third parties; Streamlit's execution model re-runs
scripts per session (kept stateless by design); no authentication — the app
contains public research data only.

See `SECURITY.md` in the repository for the checklist and threat model.
""")

with tab_a:
    # ------------------------------------------------------ developer profile
    st.markdown("## About the developer")
    h1, h2 = st.columns([2, 1])
    with h1:
        st.markdown("### Ajeet Kumar — Quantitative Finance & AI Professional")
        st.markdown("*\"Bridging code & capital.\"*")
        st.markdown("""
Quantitative finance specialist with an **M.Sc. in Financial Engineering** and a
**B.Tech in IT**. Turns complex data into alpha using **Python, C++, SQL and
ML** — from **Markowitz MVO** and **Black-Litterman** to **Monte Carlo**
simulation and **deep learning**.
""")
        st.markdown("**Highlights**")
        st.markdown("""
- 🥇 **1st Place, IIT Kanpur ML Hackathon**
- 🏅 **Felicitated by the President of India**
- 🤖 **AI systems built at Algo8.ai and Amul**
- 🎯 Seeking **full-time Quant Research / Financial Engineering** roles
""")
    with h2:
        st.markdown("### Connect")
        st.link_button("🔗 Connect on LinkedIn",
                       "https://www.linkedin.com/in/ajeek095/", use_container_width=True)
        st.link_button("🐙 Explore GitHub",
                       "https://github.com/ajeetk095", use_container_width=True)
        st.link_button("✉️ Email me directly",
                       "mailto:ajeetk095@gmail.com", use_container_width=True)

    st.divider()
    st.markdown("### ✉️ Hire me — send a message")
    st.caption("Completing this form opens your own email client with the "
               "recipient, subject and message pre-filled — press *Send* there "
               "to deliver it. Nothing is stored by this app.")
    with st.form("hire_me"):
        fe1, fe2 = st.columns(2)
        email = fe1.text_input("Your email", placeholder="you@example.com")
        name = fe2.text_input("Your name / organisation")
        subject = st.text_input("Subject",
                                value="Opportunity for Ajeet Kumar — Quant Research / FinEng",
                                max_chars=120)
        message = st.text_area("Message", height=160,
                               placeholder="Tell me about the role, team and team focus…")
        csend, clink = st.columns(2)
        sent = csend.form_submit_button("📨 Send message", type="primary", use_container_width=True)
        if sent:
            if not message.strip() or not email.strip():
                st.error("Please provide at least your email and a message.")
            else:
                body = (f"From: {name or '(not provided)'} <{email}>\n\n{message}\n\n"
                        f"— Sent via the GWP1 CrudeCortex platform")
                import urllib.parse
                mailto = ("mailto:ajeetk095@gmail.com?subject="
                          + urllib.parse.quote(subject)
                          + "&body=" + urllib.parse.quote(body))
                st.link_button("📤 Open & send in your email client", mailto,
                               use_container_width=True, type="primary")
                st.code(f"To: ajeetk095@gmail.com\nSubject: {subject}\n\n{body}",
                        language=None)
                st.button("📋 Copy blocked? Select the text above and paste into your mail app.")

    st.divider()
    st.caption("This platform presents GWP1 academic research. It makes no "
               "trading or forecasting claims: GWP2 (model development) and "
               "GWP3 (interpretation) are future stages.")
