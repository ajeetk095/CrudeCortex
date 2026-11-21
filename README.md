# 🧠🛢️ CrudeCortex

> **The brain behind the barrel.** — Crude oil research, forecasting & investment insights, powered by probabilistic graphical models.

**MScFE 660 Risk Management — Group Work Project 1 (GWP1) · WorldQuant University**
*Research: Application of Probabilistic Graphical Models in Forecasting Crude Oil Prices*
*Primary reference: Alvi, Danish A. (2018), UCL dissertation — [arXiv:1804.10869](https://arxiv.org/abs/1804.10869)*

An interactive Streamlit research platform covering the full GWP1 journey:
**Research Problem → Literature Review → Data Identification → Data Collection →
Data Dictionary → Data Cleaning → Sterilized Dataset → Exploratory Data Analysis →
Stylized Facts → PGM Theory → Inferred Causality.**

> **Scope.** This is GWP1 (problem formulation & data collection). GWP2
> (model development) and GWP3 (interpretation) are future stages and are
> never claimed as complete. No forecasts, trading signals or investment advice.

---

## ✨ Pages

| # | Page | GWP1 step |
|---|---|---|
| 1 | 🏠 Home — Research Overview | — (summary, KPIs, correlation preview) |
| 2 | 📖 Problem Formulation & Literature | Steps 1–2 (plain-English + technical views) |
| 3 | 🗂️ Data Sources & Data Dictionary | Steps 3–4 (searchable catalogue, charts, lineage) |
| 4 | 🧹 Data Collection & Cleaning | Steps 5–6 (outliers / bad data / missing values) |
| 5 | 📈 Exploratory Data Analysis | Step 7 (distributional, time-series, multivariate) |
| 6 | 📊 Stylized Facts & Risk | Step 8 (4 official questions, tests, VaR/CVaR) |
| 7 | 🕸️ PGM Learning Centre | Step 9 (Students A/B/C theory) |
| 8 | 🔗 Inferred Causality Explorer | Step 10 (interactive graph + pseudocode) |
| 9 | 🛰️ Live Oil Market Context | extra (monitoring only, separate identifiers) |
| 10 | 👤 Methodology, Docs & About | documentation, security, developer profile |

## 🧭 Understand-this-page panels

Every analytical page ends with a dynamic explainer panel — the key numbers
with one-line meanings, the insights, a green **for non-technical readers**
summary and a **technical detail** expander. All values are computed live from
the dataset, never hardcoded.

## 📊 Research ground truth (reproduced by `core/analytics.py`)

Monthly data 2010-01 → 2024-12, 180 observations, 15 collected columns,
13 usable (NonOECD_Demand & US_Ref_Cap never retrieved — **never imputed**).

| Metric | Value |
|---|---|
| Mean monthly simple return | +0.505% |
| Std dev / annualised vol | 10.714% / 37.11% |
| Skewness / excess kurtosis | 1.0796 / 13.379 |
| Jarque-Bera | 1289.786 (p ≈ 0) |
| VaR95 / CVaR95 | −12.99% / −22.86% |
| VaR99 / CVaR99 | −26.27% / −42.77% |
| Sharpe (ann., rf=0) / Max drawdown | 0.1633 / −84.96% |
| Inferred-causality skeleton | 7 edges, WTI blanket {CPI_Energy, NonOPEC_Prod, USD_DXY}, v-structures USD_DXY→WTI←CPI_Energy etc. |

## 🚀 Quick start

See **[USER_GUIDE.md](USER_GUIDE.md)** for the full walkthrough: how to run,
every page explained, interactive-features cheat-sheet, plain-language glossary
and troubleshooting.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Python **3.14 is fully supported** (also runs on 3.10–3.13). All dependencies
are pinned with `>=` to recent releases that ship 3.14 wheels.

## 🗂️ Repository layout

```text
├── app.py                  # Streamlit multipage entry point
├── core/analytics.py       # single analytical source of truth (cleaning, tests, risk, PGM)
├── pages/                  # the ten application pages
├── data/raw_data.csv       # unmodified raw master dataset (180 × 15)
├── documents/              # assignment, group report, Alvi (2018) PDFs
├── notebooks/              # original executed notebook (+ HTML export)
├── scripts/                # collect / sterilize / reproduce utilities
├── tests/                  # reproduction tests vs notebook baseline
├── .streamlit/config.toml  # theme, XSRF, telemetry-off
├── requirements.txt · Dockerfile · .env.example · SECURITY.md · LICENSE
```

## 🔗 Data sources

- [FRED — Federal Reserve Economic Data](https://fred.stlouisfed.org/) — WTISPLC, INDPRO, CPIENGSL, DTWEXBGS, A191RL1Q225SBEA
- [EIA Open Data / STEO](https://www.eia.gov/opendata/) — PAPR_OPEC, PAPR_NONOPEC, PATC_OECD, PASC_OECD_T3
- [Yahoo Finance](https://finance.yahoo.com/) — CL=F, BZ=F, ^VIX, ^GSPC
- [SEDAR](https://www.sedar.com/) · [Data.World oil datasets](https://data.world/datasets/oil)

The historical master dataset is bundled at `data/raw_data.csv` (and can be
re-downloaded from the notebook's public Google Drive source).

## 🔐 Environment variables

No keys are required to run the app (the historical dataset ships with it).
For live collection scripts, copy `.env.example` → `.env` and fill in:
`FRED_API_KEY`, `EIA_API_KEY`. On Streamlit Cloud, put them in
**Settings → Secrets** instead. Never commit `.env`.

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

Reproduction tests verify the notebook baselines above against the sterilized
dataset, plus unit tests for cleaning, returns, risk metrics, Markov blankets
and exports.

## 🐳 Docker (optional)

```bash
docker build -t gwp1-oil-research .
docker run -p 8501:8501 gwp1-oil-research
```

## 👨‍💻 About the developer

**Ajeet Kumar — Quantitative Finance & AI Professional** — *"Bridging code & capital."*
M.Sc. Financial Engineering · B.Tech IT · Python, C++, SQL, ML.
🥇 1st Place, IIT Kanpur ML Hackathon · 🏅 Felicitated by the President of India ·
AI systems at Algo8.ai and Amul. Seeking full-time Quant Research / Financial
Engineering roles.
[LinkedIn](https://www.linkedin.com/in/ajeek095/) ·
[GitHub](https://github.com/ajeetk095) ·
[ajeetk095@gmail.com](mailto:ajeetk095@gmail.com)

## 📄 License & credits

MIT License — see `LICENSE`. Academic content © the GWP1 group (Group 14660).
Data © their providers (FRED, EIA, Yahoo Finance) under their terms.
