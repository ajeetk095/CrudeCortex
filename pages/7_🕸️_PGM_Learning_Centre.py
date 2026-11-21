"""PAGE 7 — Probabilistic Graphical Model Learning Centre (Step 9)."""
import sys, os
import streamlit as st
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.title("🕸️ Probabilistic Graphical Model Learning Centre")
st.caption("GWP1 Step 9 — three two-page theoretical summaries "
           "(Student A / B / C), with oil-market examples throughout.")

tab_a, tab_b, tab_c = st.tabs(["🎓 Student A — PGMs",
                               "🎓 Student B — Parameter vs Structure learning",
                               "🎓 Student C — Markov chains & blankets"])


def _edge(fig, x0, y0, x1, y1, color="#6B7280", dash=None, width=2):
    fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines",
                             line=dict(color=color, width=width, dash=dash),
                             hoverinfo="skip", showlegend=False))


def _node(fig, x, y, label, color="#E8842C", size=26):
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="text+markers",
                             text=[label], textposition="bottom center",
                             marker=dict(size=size * 2, color=color, opacity=0.85),
                             textfont=dict(size=12, color="#1A2733"),
                             showlegend=False))


with tab_a:
    st.markdown("""
## Probabilistic Graphical Models — big picture

A **probabilistic graphical model (PGM)** marries probability theory with graph
theory. **Nodes** are random variables (e.g. WTI_Spot, USD_DXY); **edges** express
what does — and does not — directly influence what. The graph encodes the
*structure* of a joint probability distribution, so that high-dimensional
reasoning factorises into local pieces.

$$p(X_1,\\dots,X_n) = \\prod_{i=1}^{n} p\\big(X_i \\mid \\mathrm{Parents}(X_i)\\big) \\quad \\text{(directed case)}$$

**Directed vs undirected models**

| | Belief / Bayesian network (directed) | Markov network (undirected) |
|---|---|---|
| Edges mean | direct (parent→child) influence | symmetric affinity |
| Factorisation | product of conditional probabilities | product of clique potentials |
| Natural when | causal/temporal ordering plausible | symmetric constraints (e.g. spatial) |
| Independence | d-separation | graph separation |

**Conditional dependence & independence.** Two nodes connected by an edge are
conditionally dependent; if an edge is absent there is a conditioning context
that renders them independent. Conditional independence
($X \\perp Y \\mid Z$) is the workhorse: it is what conditional-independence
tests probe during structure learning, and it lets a variable's information be
summarised by its neighbourhood.

**Oil-market relevance.** Treat WTI_Spot, OPEC production, the dollar index and
VIX as nodes. A belief network can express "dollar strength → lower oil price,
*all else equal*", while the graph structure keeps us honest about which
relationships are direct and which are mediated by third variables — exactly
the conditional structure GWP1's inferred-causality analysis later probes.
""")

with tab_b:
    st.markdown("""
## Parameter learning vs Structure learning

Two distinct questions, often confused:

- **Parameter learning** — *"the graph is given; estimate the numbers."*
  For a fixed DAG, estimate each conditional distribution
  $p(X_i \\mid \\mathrm{Pa}(X_i))$. For continuous data a common choice is a
  linear-Gaussian CPD, $X_i = \\beta_0 + \\boldsymbol{\\beta}^{\\!\\top}\\mathrm{Pa}(X_i) + \\varepsilon_i$,
  with $(\\beta_0, \\boldsymbol{\\beta}, \\sigma^2)$ estimated by maximum
  likelihood / least squares per node — conceptually one regression per family.

- **Structure learning** — *"the graph itself is unknown; discover the edges."*
  Search or test for the skeleton and orientations:
  **constraint-based** methods (PC-style) run conditional-independence tests
  and keep an edge only if no conditioning set severs the dependence;
  **score-based** methods (e.g. hill-climbing with BIC) score whole graphs.

**Why both matter.** The graph determines *which* parameters exist; the
parameters determine *what the graph says numerically*. Getting structure wrong
invalidates every conditional probability read from the model; getting
parameters wrong weakens otherwise-correct structure.

**Interactive intuition.** In the mini-diagram below, solid edges are a
*hypothesised structure*; learning means (1) testing whether each solid edge
survives conditional-independence tests, and (2) fitting the conditional
distributions on the surviving graph.
""")
    fig = go.Figure()
    _edge(fig, 0.2, 0.75, 0.5, 0.5, "#2E7D32")
    _edge(fig, 0.8, 0.75, 0.5, 0.5, "#2E7D32")
    _edge(fig, 0.5, 0.5, 0.5, 0.15, "#C62828", dash="dash")
    _node(fig, 0.2, 0.75, "USD_DXY")
    _node(fig, 0.8, 0.75, "CPI_Energy")
    _node(fig, 0.5, 0.5, "WTI_Spot", "#1F6FB2")
    _node(fig, 0.5, 0.15, "VIX (edge under test)", "#9CA3AF", 20)
    fig.update_layout(title="Structure learning decides the edges; parameter learning fills in the CPDs",
                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                      height=380, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("GWP1 stops at the theory: no complete forecasting model is "
               "developed here — that belongs to GWP2.")

with tab_c:
    st.markdown("""
## Markov chains and Markov blankets

**The Markov property.** The future is independent of the past given the
present: $p(X_{t+1} \\mid X_t, X_{t-1}, \\dots) = p(X_{t+1} \\mid X_t)$.

**Markov chains.** A stochastic process with states and **transition
probabilities** $P_{ij} = p(X_{t+1}=j \\mid X_t=i)$. An oil-market illustration:
classify each month as *Bull / Bear / Sideways* and estimate the 3×3 transition
matrix from history — the chain answers "given this month's regime, what is the
chance of a switch next month?" without consulting earlier months.

**Markov blankets.** Inside a Bayesian network, the **Markov blanket** of a node
is its **parents ∪ children ∪ co-parents (spouses)**. It is the *minimal* set
that shields the node from everything else:

$$p(X \\mid \\mathrm{MB}(X), \\text{rest}) = p(X \\mid \\mathrm{MB}(X))$$

**Why it matters for WTI_Spot.** If the network is learned from the data, the
blanket of WTI_Spot identifies the *shortlist* of variables that carry all
conditioned information about oil prices — every other variable is redundant
once the blanket is known. That is precisely what the
Inferred-Causality Explorer computes for this project's variables: it found
{CPI_Energy, NonOPEC_Prod, USD_DXY} as WTI's blanket under the notebook's
assumptions (α = 0.05).
""")
    fig = go.Figure()
    # WTI blanket diagram: parents top, children bottom, spouse side
    _edge(fig, 0.5, 0.85, 0.5, 0.5, "#2E7D32", width=3)      # parent
    _edge(fig, 0.15, 0.85, 0.5, 0.5, "#2E7D32", width=3)     # spouse->child
    _edge(fig, 0.15, 0.85, 0.85, 0.5, "#7B1FA2", dash="dot", width=2)  # spouse co-parent
    _edge(fig, 0.5, 0.5, 0.5, 0.15, "#E8842C", width=3)      # child
    _edge(fig, 0.85, 0.5, 0.5, 0.15, "#9CA3AF", width=1.5)
    _node(fig, 0.5, 0.85, "CPI_Energy (parent)", "#2E7D32", 22)
    _node(fig, 0.15, 0.85, "USD_DXY (spouse)", "#7B1FA2", 22)
    _node(fig, 0.5, 0.5, "WTI_Spot", "#1F6FB2", 30)
    _node(fig, 0.85, 0.5, "SP500 (child)", "#E8842C", 22)
    _node(fig, 0.5, 0.15, "VIX (outside blanket)", "#9CA3AF", 18)
    fig.update_layout(title="The Markov blanket of WTI_Spot (illustrative)",
                      xaxis=dict(visible=False), yaxis=dict(visible=False),
                      height=420, margin=dict(t=60))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Green = parent edge, purple dotted = co-parent link, orange = "
               "child edge. Everything not touching the node is redundant given "
               "the blanket.")

st.markdown("[🔗 Next: see Markov blankets computed on the real data →](/causality-explorer)")

# ---------------- Insight panel (dynamic) ----------------
import sys as _s, os as _o
_s.path.insert(0, _o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))))
from core.analytics import inferred_causality, get_all as _ga
_ic7 = inferred_causality(_ga().sterilized)
_mb_wti = ", ".join(sorted(_ic7.markov_blankets["WTI_Spot"]))
st.divider()
st.markdown("### 🧭 Understand this page — PGM Learning Centre")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Variables in the causal map:</b> <span style='color:#C2571B;font-weight:700'>{len(_ic7.variables)}</span> — the core oil-market set (spot price, OPEC & non-OPEC supply, OECD demand, energy CPI, VIX, dollar).</div>
<div class='insight-num'><b>WTI's Markov blanket on real data:</b> <span style='color:#C2571B;font-weight:700'>{_mb_wti}</span> — computed on page 8; the minimal "inner circle" that summarises everything else for oil.</div>
<div class='insight-num'><b>3 theory summaries:</b> — Student A (what PGMs are), Student B (learning the graph vs learning the numbers), Student C (Markov chains & blankets) — each with oil-market examples and a diagram.</div>

**💡 Key insights**

- A PGM is a wiring diagram + a probability manual: structure says who influences whom; parameters say how strongly.
- Conditional independence is the knife that separates real connections from coincidental overlap — the same idea behind "all else equal" in economics.
- Markov blankets give risk managers a practical shortlist: monitor the blanket, ignore the rest (given the model).
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This page teaches, in pictures and small words, how statisticians draw a "
    "map of influences: circles for quantities (oil price, dollar, supply), "
    "lines for real connections, and a special trick — the 'Markov blanket' — "
    "that finds the few influences that truly matter for oil.</div>",
    unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("Theory summaries follow Koller & Friedman (2009) and Alvi (2018) "
               "§9-12; the blanket shown is computed live by the same simplified "
               "PC-style procedure as page 8 (α=0.05, single-variable conditioning).")
