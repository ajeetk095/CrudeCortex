"""Forecasting & signal engine for the GWP1 platform (extension beyond GWP1 scope).

Real statistical models only — every number is computed from the historical
monthly series (and optionally a live anchor), nothing is hardcoded:
  • Damped-trend Holt (exponential smoothing) — primary model
  • Linear-trend OLS baseline — comparison model
  • Backtest: walk-forward MAPE on a held-out period
  • Confidence bands from in-sample residual dispersion
  • Rule-based investment signals (trend, momentum, MA cross, volatility regime)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

HORIZONS = [1, 3, 6, 12]


# ------------------------------------------------------------------ data prep
def prepare_series(sterilized: pd.DataFrame) -> pd.Series:
    """Monthly WTI spot series, index sorted, no gaps."""
    s = sterilized["WTI_Spot"].dropna().copy()
    s.index = pd.to_datetime(s.index)
    return s.sort_index()


def blend_live_anchor(s: pd.Series) -> tuple[pd.Series, dict]:
    """Optionally anchor the series to the latest CL=F close (proxy).
    Returns (series, info). Never raises — falls back to historical only."""
    info = {"live_anchor": None, "note": "Historical monthly series only."}
    try:
        import yfinance as yf
        h = yf.download("CL=F", period="5d", interval="1d", progress=False,
                        auto_adjust=True)
        if h is not None and not h.empty:
            last = float(h["Close"].dropna().iloc[-1])
            t = h.index[-1]
            out = s.copy()
            out.loc[pd.Timestamp(t).to_period("M").to_timestamp()] = last
            out = out.sort_index()
            info = {"live_anchor": (str(t.date()), last),
                    "note": f"Anchored to CL=F close {last:.2f} ({t.date()}) — proxy for spot."}
            return out, info
    except Exception:
        pass
    return s, info


# ------------------------------------------------------------------ models
@dataclass
class ForecastResult:
    history: pd.Series
    future_index: pd.DatetimeIndex
    base: np.ndarray            # Holt damped point forecast
    linear: np.ndarray          # OLS trend baseline
    band80: np.ndarray          # ± half-width, base path
    band95: np.ndarray
    bull: np.ndarray            # scenario paths (user drift assumptions)
    bear: np.ndarray
    bull_ann: float
    bear_ann: float
    resid_sigma: float
    last_value: float


def fit_forecasts(s: pd.Series, bull_ann: float = 0.10,
                  bear_ann: float = -0.10) -> ForecastResult:
    h_max = max(HORIZONS)
    model = ExponentialSmoothing(s.values, trend="add", damped_trend=True)
    fit = model.fit(optimized=True)
    base = np.asarray(fit.forecast(h_max))
    resid = s.values - fit.fittedvalues
    sigma = float(np.std(resid, ddof=1))

    t = np.arange(len(s))
    slope, intercept = np.polyfit(t, s.values, 1)
    t_fut = np.arange(len(s), len(s) + h_max)
    linear = intercept + slope * t_fut

    last_date = s.index[-1]
    fut_idx = pd.date_range(last_date + pd.offsets.MonthBegin(1), periods=h_max,
                            freq="MS")
    h = np.arange(1, h_max + 1)
    band95 = 1.96 * sigma * np.sqrt(h)
    band80 = 1.2816 * sigma * np.sqrt(h)
    bull = base * (1 + bull_ann / 12.0) ** h
    bear = base * (1 + bear_ann / 12.0) ** h
    return ForecastResult(s, fut_idx, base, linear, band80, band95,
                          bull, bear, bull_ann, bear_ann, sigma,
                          float(s.iloc[-1]))


def backtest(s: pd.Series, horizon: int = 12) -> dict:
    """Walk-forward backtest: fit on s[:-h], evaluate on the held-out h months."""
    train, test = s.iloc[:-horizon], s.iloc[-horizon:]

    holt = ExponentialSmoothing(train.values, trend="add", damped_trend=True).fit()
    f_holt = np.asarray(holt.forecast(horizon))

    t = np.arange(len(train))
    slope, intercept = np.polyfit(t, train.values, 1)
    f_lin = intercept + slope * np.arange(len(train), len(train) + horizon)

    def mape(a, f):
        return float(np.mean(np.abs((a - f) / a)) * 100)

    def hit_rate(a, f):
        a_dir = np.sign(np.diff(np.concatenate([[train.iloc[-1]], a])))
        f_dir = np.sign(np.diff(np.concatenate([[train.iloc[-1]], f])))
        return float(np.mean(a_dir == f_dir) * 100)

    return {
        "horizon": horizon,
        "train_months": len(train), "test_months": len(test),
        "train_end": str(train.index[-1].date()),
        "test_start": str(test.index[0].date()), "test_end": str(test.index[-1].date()),
        "holt_mape": mape(test.values, f_holt),
        "linear_mape": mape(test.values, f_lin),
        "holt_dir_hit": hit_rate(test.values, f_holt),
        "linear_dir_hit": hit_rate(test.values, f_lin),
        "actual": test, "holt_fc": f_holt, "linear_fc": f_lin,
        "train": train,
    }


# ------------------------------------------------------------------ signals
@dataclass
class SignalBook:
    signals: list = field(default_factory=list)
    composite_stance: str = ""
    composite_score: int = 0


def investment_signals(s: pd.Series, fr: ForecastResult,
                       vol_full_median: float | None = None) -> SignalBook:
    book = SignalBook()
    last = float(s.iloc[-1])

    # 1 — forecast slope (12-month projected move)
    slope_pct = (fr.base[HORIZONS.index(12)] / last - 1) * 100
    stance1 = "Bullish" if slope_pct > 2 else ("Bearish" if slope_pct < -2 else "Neutral")
    book.signals.append({
        "name": "Forecast trend (12-month slope)",
        "reading": f"{slope_pct:+.1f}% projected over 12 months",
        "stance": stance1,
        "reason": ("The damped-trend model projects prices to rise beyond a ±2% band, "
                   "so the trend component alone supports a constructive view."
                   if stance1 == "Bullish" else
                   "The damped-trend model projects prices to fall beyond a ±2% band, "
                   "so the trend component alone argues for caution."
                   if stance1 == "Bearish" else
                   "The model's 12-month path stays within a ±2% band — trend "
                   "evidence is inconclusive by itself."),
    })

    # 2 — momentum (6-month historical return)
    mom6 = float(s.pct_change(6).iloc[-1] * 100)
    stance2 = "Bullish" if mom6 > 3 else ("Bearish" if mom6 < -3 else "Neutral")
    book.signals.append({
        "name": "Momentum (6-month return)",
        "reading": f"{mom6:+.1f}% over the last 6 months",
        "stance": stance2,
        "reason": ("Positive 6-month momentum has historically persisted at "
                   "1-month horizons in commodity markets (documented momentum "
                   "effect), supporting a constructive tilt."
                   if stance2 == "Bullish" else
                   "Negative 6-month momentum historically persists short-term; "
                   "suggests caution on adding exposure."
                   if stance2 == "Bearish" else
                   "Momentum over the past half-year is inside a ±3% "
                   "no-signal band."),
    })

    # 3 — moving-average crossover (12m vs 36m monthly averages)
    ma12 = float(s.rolling(12).mean().iloc[-1])
    ma36 = float(s.rolling(36).mean().iloc[-1])
    golden = ma12 > ma36
    book.signals.append({
        "name": "Moving-average crossover (12m vs 36m)",
        "reading": f"12m avg {ma12:.2f} {'above' if golden else 'below'} 36m avg {ma36:.2f}",
        "stance": "Bullish" if golden else "Bearish",
        "reason": ("The 12-month average trading above the 36-month average is the "
                   "monthly analogue of a golden cross — medium-term trend up."
                   if golden else
                   "The 12-month average trading below the 36-month average is the "
                   "monthly analogue of a death cross — medium-term trend down."),
    })

    # 4 — volatility regime
    vol_now = float(s.pct_change().rolling(12).std().iloc[-1] * np.sqrt(12) * 100)
    if vol_full_median is None:
        vol_full_median = float(s.pct_change().rolling(12).std().median() * np.sqrt(12) * 100)
    elevated = vol_now > vol_full_median * 1.25
    book.signals.append({
        "name": "Volatility regime (12m annualised)",
        "reading": f"{vol_now:.1f}% now vs {vol_full_median:.1f}% typical",
        "stance": "Caution" if elevated else "Neutral",
        "reason": ("Volatility is well above its typical level — position sizing "
                   "should shrink in high-vol regimes regardless of direction view."
                   if elevated else
                   "Volatility is near its normal regime — no extra position-size "
                   "penalty implied."),
    })

    score = sum({"Bullish": 1, "Neutral": 0, "Bearish": -1}.get(x["stance"], 0)
                for x in book.signals[:3])
    book.composite_score = score
    if elevated:
        score = min(score, 1)
        book.signals.append({
            "name": "Volatility modifier",
            "reading": "composite capped at Hold",
            "stance": "Applied",
            "reason": "Elevated volatility caps the composite at Hold — risk control overrides trend signals.",
        })
    book.composite_stance = ("Accumulate / bullish tilt" if score >= 2 else
                             "Hold / neutral" if score >= 1 else
                             "Reduce / cautious")
    return book


INSTRUMENT_MAP = [
    ("WTI front-month futures (CL)", "Direct crude exposure; highest volatility and roll-cost sensitivity.", "Suitable for the stated horizon only with strict position sizing."),
    ("WTI ETFs (USO, BNO)", "Futures-based ETFs; roll yield can erode returns in contango.", "Check the term structure before acting on any bullish view."),
    ("Brent ETFs (BNO) / Brent futures (BZ)", "Global-benchmark exposure; tracks the WTI-Brent spread.", "Spread vs WTI is an additional risk factor."),
    ("Energy equities (XLE and peers)", "Equity beta + oil beta; dividends cushion drawdowns.", "Signals apply with weaker conviction — equities add market risk."),
]
