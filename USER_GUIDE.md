# 📖 User Guide — CrudeCortex

> **The brain behind the barrel.** — Crude oil research, forecasting & investment insights.

*Everything you need to run, navigate and understand the GWP1 research platform — written for technical and non-technical readers.*

---

## 1. What this app is

An interactive research platform built for **MScFE 660 Risk Management — Group Work Project 1**. It walks through the complete GWP1 journey:

> **Research Problem → Literature Review → Data Identification → Data Collection → Data Dictionary → Data Cleaning → Sterilized Dataset → Exploratory Data Analysis → Stylized Facts → PGM Theory → Inferred Causality.**

**What it tells you (in one paragraph):** how major economic, financial and
market variables relate to crude oil prices over 2010–2024, how that data was
sourced and cleaned, what statistical character oil returns have (extreme
spikes, volatility clustering, fat tails), and how probabilistic graphical
models give a structured way to map those relationships — with an
inferred-causality graph you can explore yourself.

**What it does NOT do:** no price forecasts, no trading signals, no investment
advice. Model development is GWP2; interpretation is GWP3. The app is careful
to never claim those as complete.

---

## 2. Running the app

### Option A — Streamlit Cloud (recommended, no install)
1. Repo is on GitHub → [share.streamlit.io](https://share.streamlit.io) → sign in with GitHub.
2. **Create app → Deploy a public app from GitHub** → pick repo, branch `main`.
3. Main file path: `app.py` · Advanced settings → Python **3.14** → **Deploy**.
4. Live at `https://<your-app-name>.streamlit.app` — every push to `main` auto-redeploys.

### Option B — Run locally
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py             # opens http://localhost:8501
```
No API keys needed — the research dataset ships with the repo (`data/raw_data.csv`).

### Option C — Docker
```bash
docker build -t gwp1-oil-research .
docker run -p 8501:8501 gwp1-oil-research
```

---

## 3. Page-by-page walkthrough

| Page | What you'll find | How to use it |
|---|---|---|
| 🏠 **Home** | Research question, dataset KPIs, headline statistics, correlation chart, GWP roadmap | Start here. Use the 📅 date slider to recompute everything on any window. |
| 📖 **Problem & Literature** | The problem Alvi (2018) tackles, why Bayesian networks fit, and a full literature review | Switch between **Plain-English** and **Technical** explanations with the radio button. |
| 🗂️ **Data Sources & Dictionary** | All 15 variables with sources, units, frequencies, availability; missing-data chart; per-variable time series | Use the search box and filters to find a variable; click rows in the interactive dictionary; download the dictionary as CSV. |
| 🧹 **Data Collection & Cleaning** | What each student cleaned: outlier capping, bad-data flags, missing-value treatment; before/after charts | Inspect any winsorised variable's distribution; read the reproducibility note about execution-session drift; download the cleaning log. |
| 📈 **Exploratory Data Analysis** | Three tabs — distributions (A), time series (B), multivariate (C) | Every tab has selectors; the scatter explorer lets you pick any X/Y pair with an OLS trend line; correlation heatmap is hover-to-read; download any chart's data as CSV. |
| 📊 **Stylized Facts & Risk** | The four official Step-8 questions answered with tests, charts and risk metrics | Choose **simple vs log returns** and a date range — every statistic, test and chart recomputes. VaR/CVaR/Sharpe/MaxDD are dynamic. |
| 🕸️ **PGM Learning Centre** | Three student theory summaries with diagrams | Read tab by tab; diagrams are generated live; the blanket shown is computed on the real data. |
| 🔗 **Inferred Causality Explorer** | The causal-map drawing: skeleton, v-structures, Markov blankets, pseudocode | Switch between the group pseudocode view and the notebook implementation; **click any node** in the explorer to see its blanket, neighbours and interpretation. |
| 🛰️ **Live Market Context** | Current-market monitoring with freshness labels | Read-only monitoring with 60-s cache; note the identifier warnings (CL=F ≠ WTI_Spot). |
| 🔮 **Forecasting & Investment Insights** | Scenario projections (1/3/6/12 months) with 80%/95% confidence bands, bull/base/bear paths, walk-forward backtest and mechanical investment signals | Set the bull/bear drift sliders and the anchor (historical vs live-blend); read the backtest metrics first, then the projection table and the composite stance. **Not financial advice.** |
| 👤 **Methodology, Docs & About** | Ten-step methodology, known limitations, security practices, document downloads, developer profile & hire-me form | Download the report PDF; use the mail form to contact the developer. |

---

## 4. The "🧭 Understand this page" panels

Every analytical page ends with a standard explainer panel:

- **📏 The numbers & what they mean** — each key figure with a one-line
  explanation, pulled live from the computed data (never hardcoded).
- **💡 Key insights** — the three or four takeaways the page demonstrates.
- **🟢 For non-technical readers** — the same story in everyday language.
- **🔬 Technical detail** (expander) — exact formulas, libraries and
  conventions used, for reviewers and graders.

If you read only one thing per page, read the green box.

---

## 5. Interactive features cheat-sheet

| Feature | Where | What it does |
|---|---|---|
| 📅 Date-range slider | Home, EDA, Stylized Facts | Filters every statistic and chart on the page |
| Return-basis switch | Stylized Facts | Simple vs log returns |
| Variable multi-select | EDA → Student A | Pick which distributions to plot |
| X/Y scatter explorer | EDA → Student C | Any pair + trend line + CSV download |
| Node click-explorer | Causality page | Blanket, neighbours and meaning per node |
| Search & filters | Data Dictionary | Find variables by name, category or status |
| Download buttons | Most pages | Sterilized/raw/filtered CSV, dictionary, cleaning log, correlation matrix |
| Chart camera icon | All Plotly charts | Download any chart as PNG |
| Plain/Technical toggle | Problem page | Same content, two audiences |

---

## 6. Glossary (plain language)

| Term | Meaning |
|---|---|
| **WTI / Brent** | Benchmark crude oils; WTI is US-centric, Brent is global |
| **Winsorisation** | Capping extreme values at statistical fences instead of deleting them |
| **VaR (Value at Risk)** | The loss threshold you exceed in only the worst X% of months |
| **CVaR / Expected Shortfall** | The *average* loss in those worst months |
| **Skewness** | Whether the ups or downs have longer tails (>0 = bigger up-spikes) |
| **Excess kurtosis** | How much more often extremes happen than a bell curve predicts |
| **Volatility clustering** | Stormy months arriving in runs, calm months in runs |
| **Autocorrelation** | Whether a month resembles the previous month(s) |
| **Ljung–Box test** | A statistical check for whether autocorrelation is real |
| **Probabilistic Graphical Model** | A graph (nodes + edges) that also carries probabilities |
| **Bayesian network** | A directed PGM: arrows show direct influence |
| **Conditional independence** | "Once I know Z, X tells me nothing more about Y" |
| **Markov blanket** | The minimal set of nodes that makes a variable independent of all the rest |
| **V-structure / collider** | Two arrows pointing into the same node; a pattern that reveals direction |
| **Skeleton** | The undirected version of the learned graph |
| **STEO** | EIA's Short-Term Energy Outlook — partly estimates, hence flagged |

---

## 7. The 🔮 Forecasting & Investment Insights page (platform extension)

**Honest answer to "does the app forecast?"** The original GWP1 research did
not — forecasting is GWP2 scope. This page is a clearly-labelled *platform
extension* added on top, so visitors can see transparent statistical
extrapolations of the same historical data.

### Method (nothing hardcoded — all values computed at render time)

| Component | What runs | What you see |
|---|---|---|
| **Primary model** | Damped-trend Holt exponential smoothing (`statsmodels.ExponentialSmoothing`, trend='add', damped, optimized MLE) on monthly WTI (FRED WTISPLC, optionally anchored to the latest CL=F close) | Base path for 1, 3, 6, 12 months ahead |
| **Baseline model** | OLS linear trend on the time index | Dashed comparison path |
| **Confidence bands** | base ± z·σ_resid·√h, z = 1.2816 / 1.96, σ from in-sample residuals | 80% and 95% shaded bands that widen with horizon |
| **Scenarios** | Base path compounded at user-set bull/bear annual drift (defaults +10%/−10%) | Green/red dotted storylines with sliders |
| **Backtest** | Walk-forward: fit through month *T−12*, score the held-out year | MAPE (%) and directional hit-rate for both models, plotted against actuals |
| **Signals** | Four mechanical rules: 12-month projected slope (±2% band), 6-month momentum (±3% band), 12m-vs-36m monthly-average crossover, 12m annualised volatility vs its typical level | Per-signal stance + reasoning, composite score, and a stance for crude exposure (futures, USO/BNO ETFs, energy equities) with caveats |
| **Risk override** | If volatility > 1.25× its full-sample median, the composite is capped at *Hold* | "Volatility modifier — applied" note |

### How to read it (non-technical)
The orange line is the "most likely" path if the recent pattern simply
continues; the shaded band is the range of realistic outcomes (wider further
out = more uncertainty); green/red dotted lines are rosier/gloomier storylines
you control. Signals are rule-of-thumb condition checks — they describe the
tape, they don't know the future.

### Limitations (read before using)
1. **Univariate extrapolation** — the model knows oil's own history only; it
cannot anticipate OPEC decisions, wars, sanctions or recessions.
2. **Monthly granularity** — intra-month dynamics are invisible to it.
3. **No parameter uncertainty** — bands cover residual noise, not model risk.
4. **Roll costs** — any futures/ETF implementation adds costs the forecast
doesn't include (contango drag on USO-style ETFs).
5. **Backtests are past-looking** — a good held-out MAPE does not guarantee
future accuracy; regime changes can invalidate any model.
6. **Not financial advice** — signals are mechanical rules for education;
consult a licensed advisor before investing.

---

## 8. Troubleshooting

| Problem | Fix |
|---|---|
| App blank / "Please wait" forever | First build compiles deps — wait 3–5 min on Streamlit Cloud |
| `ModuleNotFoundError` | `pip install -r requirements.txt` inside your activated venv |
| Charts not showing | Check the date slider isn't narrowed to < 5 months |
| Live page empty | Yahoo/FRED outage — rows show UNAVAILABLE; retry after a minute |
| Need API keys? | Not for the app; only for `scripts/collect_data.py` (see `.env.example`) |
| Tests | `python -m pytest tests/ -v` — expect 32 passed |

---

## 9. For graders & reviewers

- Reproduce every reported number: `python scripts/reproduce_notebook.py` → all checks ✅.
- The single analytical source of truth is `core/analytics.py`; the app and scripts share it.
- Known issues (autocorrelation wording, 50-obs Shapiro–Wilk, execution-session winsorisation drift) are disclosed on-page and in the Methodology tab.
- Scope discipline: GWP1 only — GWP2/GWP3 are described, never claimed.
