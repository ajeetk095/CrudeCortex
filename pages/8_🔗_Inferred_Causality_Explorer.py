"""PAGE 8 — Inferred Causality Graph Explorer (Step 10)."""
import sys, os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.analytics import get_all, inferred_causality

st.title("🔗 Inferred Causality Graph Explorer")
st.caption("GWP1 Step 10 — the group's own version of Algorithm 1 "
           "(Inferred Causality), reproduced from the actual notebook "
           "implementation on the sterilized dataset.")

st.error("**These are statistically inferred conditional relationships under the "
         "chosen assumptions. Directed graph orientations do not independently "
         "establish real-world economic causation.**", icon="⚠️")

@st.cache_data(show_spinner="Running inferred-causality algorithm…")
def _run():
    rd = get_all()
    return rd, inferred_causality(rd.sterilized)

rd, ic = _run()

mode = st.radio("Representation", ["② Simplified algorithm implemented in the notebook",
                                   "① General algorithmic methodology (pseudocode)"],
                horizontal=True)

# ------------------------------------------------------------------ layouts
POS = {
    "WTI_Spot": (0.5, 0.5), "CPI_Energy": (0.18, 0.82),
    "USD_DXY": (0.15, 0.18), "NonOPEC_Prod": (0.82, 0.75),
    "OPEC_Prod": (0.85, 0.25), "OECD_Demand": (0.55, 0.06),
    "VIX": (0.88, 0.5),
}
MB_COLOR = {"WTI_Spot": "#1F6FB2", "CPI_Energy": "#2E7D32",
            "NonOPEC_Prod": "#2E7D32", "USD_DXY": "#2E7D32"}
DEFAULT_COLOR = "#9CA3AF"

def draw(edges, arrows=False, title=""):
    fig = go.Figure()
    for (a, b) in edges:
        x0, y0 = POS[a]; x1, y1 = POS[b]
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0,
                           xref="x", yref="y", axref="x", ayref="y",
                           showarrow=True, arrowhead=2 if arrows else 0,
                           arrowsize=1.2, arrowwidth=2.2,
                           arrowcolor="#E8842C", standoff=14)
    for v, (x, y) in POS.items():
        color = MB_COLOR.get(v, DEFAULT_COLOR)
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            text=[v.replace("_", " ")], textposition="bottom center",
            marker=dict(size=46 if v == "WTI_Spot" else 36, color=color,
                        opacity=0.9, line=dict(width=2, color="white")),
            textfont=dict(size=11, color="#1A2733"), hovertext=v,
            showlegend=False))
    fig.update_layout(title=title, height=520,
                      xaxis=dict(visible=False, range=[0, 1]),
                      yaxis=dict(visible=False, range=[-0.05, 1]),
                      margin=dict(t=60))
    return fig

if mode.startswith("②"):
    st.markdown(f"""
**Notebook implementation — exactly as executed** (α = {ic.alpha}):

- **Phase 1 — Markov blankets:** pairwise marginal-independence (Pearson) tests;
  variables with p < α become neighbours.
- **Phase 2 — Skeleton:** for each adjacent pair, test conditional independence
  given **single-variable conditioning sets only** (drawn from the union of the
  pair's blankets). An edge survives if no single separator is found.
- **Phase 3 — v-structures:** for non-adjacent pairs sharing a neighbour,
  orient a collider when the shared node is not in the separating set.

Result: **{len(ic.edges)} skeleton edges**, **{len(ic.v_structures)} v-structures**.
""")
    st.plotly_chart(draw(ic.edges, title="Skeleton inferred from the sterilized monthly data — "
                                        "green nodes form the WTI_Spot Markov blanket"),
                    use_container_width=True)

    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Skeleton edges**")
        st.markdown("\n".join(f"- {a} — {b}" for a, b in sorted(ic.edges)))
    with m2:
        st.markdown("**V-structures**")
        st.markdown("\n".join(f"- {a} → {k} ← {b}" for a, k, b in ic.v_structures))

    st.markdown("**Markov blankets (from Phase 1)**")
    mbdf = pd.DataFrame({"Variable": list(ic.markov_blankets),
                         "Markov blanket": [", ".join(sorted(v)) if v else "—"
                                            for v in ic.markov_blankets.values()]})
    st.dataframe(mbdf, use_container_width=True, hide_index=True)

    # separation sets
    if ic.sep_sets:
        with st.expander("Separation sets found in Phase 2"):
            st.dataframe(pd.DataFrame(
                [{"Pair": f"{a} ⊥ {b}", "Separating set": ", ".join(sorted(s)) or "∅ (marginally independent)"}
                 for (a, b), s in ic.sep_sets.items()]),
                use_container_width=True, hide_index=True)
else:
    st.markdown("""
**General algorithmic methodology** — the group's full pseudocode (below) is
more extensive than the executed notebook version: it searches conditioning
subsets of **all sizes** up to a bound, applies symmetric Markov-blanket
handling, and applies full PC orientation rules (colliders first, then
Meek's rules). The notebook implements a **simplified** version
(single-variable conditioning sets only). The distinction matters: results
shown on the other tab come from the simplified implementation.
""")
    st.plotly_chart(draw(ic.edges, title="Same dataset — the simplified implementation's output (for reference)"),
                    use_container_width=True)
    with st.expander("📜 Pseudocode — Algorithm 1: Inferred Causality (group version)"):
        st.code("""
ALGORITHM 1: INFERRED CAUSALITY
INPUT : data matrix D over variables V = {X1,...,Xn}
        significance level alpha (e.g. 0.05)
        maximum conditioning-set size L
OUTPUT: DAG G = (V, E) with statistically inferred orientations

# ---------- PHASE 1: Markov blanket identification ----------
1  for each ordered pair (Xi, Xj), i != j:
2      r, p <- partial_correlation(Xi, Xj, conditioning set = {})
3      if p < alpha: add Xi to neighbourhood(Xj) and vice versa
4  for each Xi:
5      MB(Xi) <- neighbourhood(Xi)
6      # symmetric refinement (full version):
7      for each Y in MB(Xi):
8          if Y not in MB of any Z in MB(Xi) considering (Xi, Z):
9              apply blanket-symmetry correction
10 FORBIDDEN  <- V \\ ({Xi} ∪ MB(Xi))          # shielded variables

# ---------- PHASE 2: skeleton construction ----------
11 E <- all pairs found adjacent in Phase 1
12 for each edge (Xi, Xj) in E:
13     for k = 0 .. min(L, |MB(Xi) ∪ MB(Xj)| - 2):
14         for each conditioning set S of size k, S ⊆ MB(Xi) ∪ MB(Xj) \\ {Xi, Xj}:
15             r, p <- partial_correlation(Xi, Xj, S)
16             if p >= alpha:                  # independence found
17                 remove (Xi, Xj) from E
18                 sep_set(Xi, Xj) <- S        # record separating set
19                 break to next edge
20 # NOTE: the executed notebook restricts S to SINGLE variables (k ≤ 1).

# ---------- PHASE 3: edge orientation (v-structures) ----------
21 for each collider candidate Xk with non-adjacent parents Xi, Xj:
22     if Xi—Xk and Xk—Xj in E and (Xi, Xj) not adjacent:
23         if Xk ∉ sep_set(Xi, Xj):
24             orient Xi -> Xk <- Xj           # collider / v-structure

# ---------- PHASE 4: final graphical representation ----------
25 apply Meek's orientation rules to orient remaining edges without
   creating new colliders or cycles
26 return G

INTERPRETATION LIMIT: arrows encode statistical conditional structure,
not demonstrated economic causation.
""", language="text")
    st.info("**Theory ↔ implementation map.** Phases 1, 2 (restricted to "
            "single-variable conditioning sets) and 3 (collider step only) are "
            "implemented in the notebook. Symmetric blanket refinement "
            "(lines 7–9), multi-variable conditioning sets (line 13–14 loop at "
            "k > 1) and Meek's rules (Phase 4) belong to the general algorithm "
            "and were **not** implemented.")

# ------------------------------------------------------------------ explorer
st.markdown("## Interactive node explorer")
sel = st.selectbox("Click a node to inspect it", ic.variables, index=0)
mb_sel = sorted(ic.markov_blankets.get(sel, []))
nbrs = sorted({b for a, b in ic.edges if a == sel} | {a for a, b in ic.edges if b == sel})
c1, c2, c3 = st.columns(3)
c1.metric("Markov blanket", ", ".join(mb_sel) if mb_sel else "— (no blanket)")
c2.metric("Direct skeleton neighbours", ", ".join(nbrs) if nbrs else "—")
c3.metric("Blanket size", len(mb_sel))
st.caption(f"Once {mb_sel or 'its blanket'} is known, the remaining variables add "
           "no information about " + sel + " under this inferred structure — "
           "the Markov blanket property.")

st.markdown("## Purpose & limitations of inferred causality")
st.markdown(f"""
**Purpose.** Move beyond raw correlations: identify which variables remain
conditionally informative about WTI_Spot, and propose a directed structure —
grounded in the Step 9 theory (Markov blankets, conditional independence,
separation sets, v-structures).

**Inputs:** the sterilized monthly panel (7 core variables), α = {ic.alpha},
Pearson-based partial correlations. **Method:** the simplified PC-style
procedure described above.

**Limitations.** Linear-Gaussian tests only; single-variable conditioning sets;
monthly frequency hides intramonth dynamics; possible unobserved common drivers;
faithfulness and stationarity assumed; directions are statistically inferred and
**must not** be read as physical or economic causation.
""")

# ---------------- Insight panel (dynamic) ----------------
st.divider()
st.markdown("### 🧭 Understand this page — Inferred Causality Explorer")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Skeleton edges:</b> <span style='color:#C2571B;font-weight:700'>{len(ic.edges)}</span> — direct statistical connections that survived the independence tests; the market's "wiring" under this method.</div>
<div class='insight-num'><b>V-structures:</b> <span style='color:#C2571B;font-weight:700'>{len(ic.v_structures)}</span> — special collider patterns (two causes pointing at one effect) that let the algorithm suggest arrow directions.</div>
<div class='insight-num'><b>Significance level α:</b> <span style='color:#C2571B;font-weight:700'>{ic.alpha}</span> — the strictness dial for "are these two variables independent?"; lower α = fewer, stronger edges.</div>
<div class='insight-num'><b>WTI's blanket:</b> <span style='color:#C2571B;font-weight:700'>{', '.join(sorted(ic.markov_blankets['WTI_Spot']))}</span> — once these are known, every other variable adds nothing about oil *under this inferred structure*.</div>

**💡 Key insights**

- Two representations are provided: the general pseudocode the group wrote, and the simplified version actually executed in the notebook — the map shows exactly which phases were implemented.
- The dollar appears as a hub in the skeleton (links to non-OPEC supply, energy CPI and WTI) — a good example of a common driver connecting otherwise distant variables.
- Arrows here are statistical suggestions, not economic proof: with linear-Gaussian tests and monthly data, direction is an inference under assumptions, always labelled as such.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "This page draws a suspects-and-connections map for oil prices. Lines mean "
    "'two things genuinely move together after accounting for others'; arrows are "
    "best guesses about direction. Click any circle to see its inner circle of "
    "influences. It is detective work with statistics — not a claim that one "
    "thing physically causes another.</div>", unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("Simplified PC-style procedure on the sterilized panel: Phase 1 "
               "pairwise marginal tests → blankets; Phase 2 single-variable "
               "conditioning for separation; Phase 3 collider orientation via "
               "separation sets. Pearson-based partial correlations (OLS residuals), "
               "complete cases, n=179 return months.")
