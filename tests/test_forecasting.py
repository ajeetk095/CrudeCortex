"""Tests for the forecasting & signals engine (v3)."""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analytics import get_all
from core.forecasting import (prepare_series, fit_forecasts, backtest,
                              investment_signals, HORIZONS)


@pytest.fixture(scope="module")
def s():
    return prepare_series(get_all().sterilized)


def test_series_shape(s):
    assert len(s) == 180
    assert not s.isna().any()


def test_forecast_horizons(s):
    fr = fit_forecasts(s)
    assert len(fr.base) == max(HORIZONS)
    assert np.isfinite(fr.base).all()
    assert np.isfinite(fr.bull).all() and np.isfinite(fr.bear).all()
    # bands widen with horizon
    assert fr.band95[-1] > fr.band95[0] > 0


def test_backtest_passes(s):
    bt = backtest(s, 12)
    assert bt["holt_mape"] < 20.0, f"Holt MAPE too high: {bt['holt_mape']}"
    assert bt["linear_mape"] < 30.0
    assert bt["holt_dir_hit"] > 0


def test_scenarios_bracket_base(s):
    fr = fit_forecasts(s, bull_ann=0.10, bear_ann=-0.10)
    assert (fr.bear < fr.base).all()
    assert (fr.bull > fr.base).all()


def test_signals_wellformed(s):
    fr = fit_forecasts(s)
    book = investment_signals(s, fr)
    assert book.composite_stance in ("Accumulate / bullish tilt", "Hold / neutral",
                                     "Reduce / cautious")
    assert len(book.signals) >= 4
    for sg in book.signals:
        assert sg["stance"] and sg["reason"] and sg["reading"]
