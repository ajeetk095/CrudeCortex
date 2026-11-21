"""PAGE 2 — Problem Formulation & Literature Review (Step 1 + Step 2)."""
import streamlit as st

st.title("📖 Problem Formulation & Literature Review")
st.caption("GWP1 Step 1 (paper review) and Step 2 (group problem formulation, "
           "2–3 pages) — rendered in two views.")

view = st.radio("Explanation mode", ["Plain-English explanation", "Technical explanation"],
                horizontal=True)

if view == "Plain-English explanation":
    st.markdown("""
## Why crude oil matters

Crude oil is the lifeblood of the global economy. It fuels transport, heats homes,
generates backup electricity and feeds the petrochemical industry. When its price
swings sharply, the effects ripple through inflation, transport costs, farm output
and virtually every household budget. That is why economists watch oil prices so
closely — they are one of the most important **barometers of global economic health**.

## Why oil prices are so hard to pin down

Unlike the price of a loaf of bread, the oil price is shaped by a constantly shifting
web of forces acting at the same time:

- **Supply side** — OPEC and non-OPEC producers decide how much to pump; wars,
  sanctions and hurricanes can knock supply out overnight.
- **Demand side** — a booming world economy burns more oil; a pandemic empties
  the roads and skies.
- **Money and markets** — the strength of the US dollar, equity-market sentiment
  and speculative positions all colour the price.
- **Stocks and buffers** — when inventories pile up, prices sag; when they drain,
  prices surge.

No single number explains the oil price. We need a way to study **many variables
that all influence each other at once** — and to be honest about our uncertainty.

## What this research does about it

Instead of trying to squeeze the oil price into a single equation, we take an
inventory-first approach (this is GWP1 — the foundation for later model building):

1. **List the candidate drivers** — macroeconomic, microeconomic, geopolitical
   and financial.
2. **Gather the best available data** from authoritative public sources
   (FRED, EIA, Yahoo Finance).
3. **Clean it ruthlessly and transparently** — document every cap, flag and fill.
4. **Characterise the data statistically** — how volatile are oil returns? Are
   they normally distributed? Do they show volatility clustering?
5. **Sketch the map of relationships** using probabilistic graphical models —
   a technique that draws variables as nodes and statistical dependencies as
   edges, so the "wiring diagram" of the oil market becomes visible.

## Why this matters for decision-makers

A structured picture of *which* variables are conditionally linked to oil —
and *which* only appear linked through third variables — helps analysts, risk
managers and students ask better questions before any forecasting is attempted.
Understanding the plumbing comes before predicting the flow.
""")
else:
    st.markdown("""
## A. Introduction to crude oil markets

Crude oil is the world's most heavily traded commodity and a critical
macroeconomic indicator of industrial growth. Its price is determined in
globally integrated markets balancing supply from OPEC and non-OPEC producers
against demand concentrated in OECD and emerging economies. Price formation is
sensitive to energy-consumption cycles, producer policy, and economic and
geopolitical shocks, generating persistent uncertainty that transmits into
inflation, terms of trade and financial conditions.

## B. The research problem

Crude oil prices are difficult to model because they are the joint outcome of
**multiple interdependent variables**: supply and demand shocks, macroeconomic
developments, political events, currency movements, financial-market uncertainty
and inventory dynamics. These relationships are plausibly **nonlinear and
time-varying**, and many candidate drivers are themselves correlated — creating
multicollinearity that confounds naive regression approaches. A framework that
can represent **conditional dependence and independence** among many variables,
while quantifying uncertainty, is required.

## C. Why probabilistic graphical models (PGMs) are relevant

PGMs encode a joint probability distribution over a set of random variables
using a graph whose nodes are variables and whose edges encode (in)dependence:

- **Directed graphs (Bayesian/belief networks)** factorise the joint as a
  product of conditional distributions, $p(X_1,\\dots,X_n) = \\prod_i p(X_i \\mid \\mathrm{Pa}(X_i))$.
- **Undirected graphs (Markov networks)** represent symmetric affinity through
  clique potentials.
- **Conditional independence** (d-separation in DAGs) makes high-dimensional
  reasoning tractable: each variable depends only on its local neighbourhood.
- The **Markov blanket** of a node — its parents, children and co-parents —
  shields it from the rest of the network.

Applied to oil markets, PGMs offer a disciplined language for asking which
variables remain informative about WTI once other variables are accounted for.

## D. Advantages of the methodology

Visual interpretation; dependency discovery from data; principled multivariate
analysis; probabilistic (not deterministic) reasoning; modular graph structures
that extend naturally; and explicit explanation of conditional relationships —
directly serving risk-management insight.

## E. Research objective and questions

**Primary question.** *"How can macroeconomic, microeconomic, geopolitical and
financial variables be identified, structured and analysed to understand the
factors associated with global crude oil price behaviour, and how can
probabilistic graphical models provide a framework for representing their
relationships?"*

**Supporting questions.**

1. Which variables are relevant to crude oil market analysis?
2. Which reliable data sources provide them?
3. What data-quality challenges arise when combining heterogeneous time series?
4. What statistical characteristics are observable in crude oil returns?
5. How can PGMs represent interdependencies?
6. What can Markov blankets and inferred-causality analysis reveal about
   conditional relationships?

> GWP1 does **not** claim predictive performance. Model development (GWP2) and
> interpretation (GWP3) follow.
""")

st.divider()
st.markdown("## Literature Review — Alvi (2018) and related research")

st.markdown("""
**Alvi, Danish A. (2018). *Application of Probabilistic Graphical Models in
Forecasting Crude Oil Price*. UCL BSc dissertation (arXiv:1804.10869).** — the
primary academic reference for this project.

### 1. Research motivation
The dissertation motivates PGMs as a response to the failure of single-equation
models in a market driven by "a vast amount of macroeconomic factors": OPEC
supply, OECD demand, geopolitical and geoeconomic change. The objective is to use
graphical models both to *understand* relationships among oil-price drivers and
to *forecast* WTI prices.

### 2. Global importance of crude oil
Oil is framed as a pivotal macroeconomic indicator of industrial growth; price
shocks propagate into CPI, industrial production and GDP across economies.

### 3. Difficulties in analysing crude oil prices
High dimensionality, interdependent regressors, regime changes and the mixture
of physical (supply/demand/inventory) and financial (dollar, equities, volatility)
forces — each series at different frequencies.

### 4–8. Variables and their categories
- **Macroeconomic:** industrial production, CPI, GDP growth, interest rates, exchange rates.
- **Microeconomic:** production decisions, consumption, inventories, refinery activity.
- **Geopolitical:** producer-country disruptions, energy policy, conflict risk.
- **Financial:** WTI/Brent spot and futures, equities, VIX, dollar indices.
- **Interdependencies:** these groups are mutually correlated — e.g. the dollar
  moves inversely with oil; demand responds to growth; inventories buffer shocks.

### 9–12. PGM foundations and Bayesian networks
The paper reviews belief (directed) versus Markov (undirected) networks, the role
of conditional-independence tests, skeleton construction, v-structures and Markov
blankets, and the advantage of graphical representations: interpretability,
modularity and uncertainty quantification.

### 13–15. Assumptions, limitations and relevance to GWP1
The methodology assumes stationarity of the transformed series, faithfulness of
the graph to the data-generating distribution, and validity of linear-Gaussian
conditional-independence tests. Inferred directions are statistical, not proven
physical causation. For GWP1 the paper supplies: the variable taxonomy, the
Section 4.1 cleaning methodology (outlier/bad-data/missing-data), and Algorithm 1
(*Inferred Causality*), which this project re-implements as pseudocode and a
simplified executable version.

### Additional references consulted
- Caldara, D. & Iacoviello, M. (2022). "Measuring Geopolitical Risk." *American Economic Review* 112(4).
- U.S. EIA, *Short-Term Energy Outlook* (STEO) data documentation.
- Federal Reserve Bank of St. Louis, FRED database documentation.
- Koller, D. & Friedman, N. (2009). *Probabilistic Graphical Models: Principles and Techniques*. MIT Press.
- Spirtes, P., Glymour, C. & Scheines, R. (2000). *Causation, Prediction, and Search*. MIT Press.
""")

st.markdown("📄 The full GWP1 report is available for download on the **Methodology, Docs & About** page.")
