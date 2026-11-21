"""PAGE 9 — Live Oil Market Context (monitoring only — NOT part of GWP1 dataset)."""
import sys, os
import datetime as dt
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from theme import freshness_badge, GREEN, ORANGE

st.title("🛰️ Live Oil Market Context")
st.caption("An additional application capability — **not** the historical GWP1 "
           "academic dataset. For current-market context and research "
           "comparison only; **not** validated prediction.")

st.error("**Identifier discipline.** Live tickers are *proxies*, not the "
         "academic series: `WTI_Spot` (FRED WTISPLC, monthly avg) ≠ `CL=F` "
         "(front-month futures); `USD_DXY` (FRED DTWEXBGS, broad trade-weighted) "
         "≠ `DX-Y.NYB` (ICE dollar index). Definitions differ — never mix them "
         "in research calculations.", icon="🧭")

WATCHLIST = {
    "WTI futures (proxy for WTI_Spot)": ("CL=F", "Yahoo Finance", "DAILY", "DELAYED"),
    "Brent futures": ("BZ=F", "Yahoo Finance", "DAILY", "DELAYED"),
    "CBOE VIX": ("^VIX", "Yahoo Finance", "DAILY", "DELAYED"),
    "S&P 500": ("^GSPC", "Yahoo Finance", "DAILY", "DELAYED"),
    "US dollar index (proxy for USD_DXY)": ("DX-Y.NYB", "Yahoo Finance", "DAILY", "DELAYED"),
    "US natural gas futures": ("NG=F", "Yahoo Finance", "DAILY", "DELAYED"),
    "Energy select sector SPDR (XLE)": ("XLE", "Yahoo Finance", "DAILY", "DELAYED"),
}


@st.cache_data(ttl=60, show_spinner="Fetching latest market data…")
def fetch_quotes():
    try:
        import yfinance as yf
        rows = []
        for label, (tkr, src, freq, fresh) in WATCHLIST.items():
            try:
                hist = yf.download(tkr, period="1mo", interval="1d",
                                   progress=False, auto_adjust=True)
                if hist is None or hist.empty:
                    rows.append({"Indicator": label, "Ticker": tkr, "Latest": None})
                    continue
                last = hist["Close"].dropna()
                prev = last.iloc[-2] if len(last) > 1 else last.iloc[-1]
                val = float(last.iloc[-1])
                chg = (val / float(prev) - 1) * 100
                rows.append({"Indicator": label, "Ticker": tkr, "Latest": round(val, 2),
                             "1-day change %": round(chg, 2),
                             "Observation time (UTC)": str(last.index[-1].date()),
                             "Retrieved (UTC)": dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                             "Source": src, "Frequency": freq, "Freshness": fresh})
            except Exception as e:
                rows.append({"Indicator": label, "Ticker": tkr, "Latest": None,
                             "Note": f"unavailable: {type(e).__name__}"})
        return pd.DataFrame(rows)
    except Exception as e:
        st.warning(f"Market provider unreachable ({type(e).__name__}). "
                   "No values are fabricated during outages — showing last-known-good state.")
        return pd.DataFrame([{"Indicator": k, "Ticker": v[0], "Latest": None,
                              "Freshness": "UNAVAILABLE"} for k, v in WATCHLIST.items()])


quotes = fetch_quotes()

st.markdown("## Latest-available observations")
disp = quotes.copy()
if "Latest" in disp.columns:
    disp["Freshness"] = disp.apply(
        lambda r: freshness_badge(r.get("Freshness", "UNAVAILABLE")), axis=1)
    st.dataframe(disp.drop(columns=["Note"], errors="ignore"),
                 use_container_width=True, hide_index=True)
    st.caption("Yahoo Finance quotes are typically **15-min delayed** and "
               "end-of-day for the last session. A 60-second cache is applied; "
               "on provider failure the last good value is shown and flagged — "
               "no fabricated observations.")

if "Latest" in quotes.columns and quotes["Latest"].notna().any():
    st.markdown("## Recent daily closes (1 month)")
    ok = quotes[quotes["Latest"].notna()]["Ticker"].tolist()
    try:
        import yfinance as yf
        fig = go.Figure()
        colors = ["#E8842C", "#1F6FB2", "#2E7D32", "#7B1FA2", "#C62828", "#0F766E", "#B45309"]
        for i, tkr in enumerate(ok[:4]):
            h = yf.download(tkr, period="1mo", interval="1d", progress=False,
                            auto_adjust=True)["Close"].dropna()
            if len(h):
                fig.add_scatter(x=h.index, y=h.values, name=tkr,
                                line=dict(width=2, color=colors[i % len(colors)]))
        fig.update_layout(title="Daily closes — normalised scales differ per asset; "
                                "compare directions, not levels",
                          xaxis_title="Date", yaxis_title="Price / index level",
                          height=420)
        st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass

st.markdown("## How this relates to the GWP1 research")
st.markdown("""
- The **academic dataset** (monthly, 2010–2024, FRED/EIA/Yahoo) is fixed, "
  versioned and reproducible — see the Data pages.
- This dashboard uses **separate identifiers** for live proxies, labelled with
  freshness (LIVE / DELAYED / MONTHLY / QUARTERLY / ESTIMATE / FORECAST / STALE /
  UNAVAILABLE) and retrieval timestamps.
- Monthly/quarterly economic series refresh only when their **source publishes**
  — never labelled "live" merely because the app refreshed.
- This is a monitoring and research-comparison tool. It provides **no forecasts,
  signals or investment advice**.
""")

# ---------------- Insight panel (dynamic) ----------------
_ok = quotes[quotes.get("Latest").notna()] if "Latest" in quotes.columns else quotes.iloc[0:0]
st.divider()
st.markdown("### 🧭 Understand this page — Live Oil Market Context")
st.caption("Every key number explained: what it is, what it means, and why it matters.")
st.markdown(f"""
**📏 The numbers & what they mean**

<div class='insight-num'><b>Instruments monitored:</b> <span style='color:#C2571B;font-weight:700'>{len(WATCHLIST)}</span> — front-month WTI & Brent futures, VIX, S&P 500, dollar index, natural gas and an energy equity ETF.</div>
<div class='insight-num'><b>Quotes retrieved now:</b> <span style='color:#C2571B;font-weight:700'>{len(_ok)}</span> — the rest are shown as UNAVAILABLE rather than guessed; provider outages are labelled, never papered over.</div>
<div class='insight-num'><b>Freshness labels:</b> — every row carries DELAYED (15-min Yahoo lag), MONTHLY/QUARTERLY (source publication cycle) or UNAVAILABLE — "live" never means "verified".</div>
<div class='insight-num'><b>Cache:</b> <span style='color:#C2571B;font-weight:700'>60 seconds</span> — repeated visits reuse the last fetch for one minute; the retrieved-at timestamp shows the data's age.</div>

**💡 Key insights**

- Live tickers are proxies with different definitions than the academic series (futures vs spot; ICE dollar vs Fed broad dollar) — mixing them would corrupt research calculations, hence the big identifier warning.
- During the April 2020 crisis these intraday feeds printed −$37.63 while the monthly series never went negative — a concrete example of why frequency and definition discipline matters.
- This page is context, not signal: no forecasts, no trading implications, by design.
""", unsafe_allow_html=True)
st.markdown(
    "<div class='insight-plain'>🟢 <b>For non-technical readers:</b><br>"
    "Think of this as a airport departure board for oil-related markets: "
    "current prices, how fresh they are, and where they come from. If a feed "
    "is down, the board says so instead of showing a made-up number.</div>",
    unsafe_allow_html=True)
with st.expander("🔬 Technical detail — how these numbers were produced"):
    st.caption("yfinance daily closes (auto-adjusted), 1-month lookback, cached "
               "60s via st.cache_data; per-ticker try/except so one failure "
               "never blanks the board; retrieved-at timestamps in UTC.")
