"""Collect fresh source data into data/raw_data.csv (requires API keys in env).
Run:  python scripts/collect_data.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from core.analytics import RAW_CSV, START, END


def main() -> None:
    from fredapi import Fred
    import yfinance as yf
    import requests

    fred_key = os.environ.get("FRED_API_KEY", "")
    eia_key = os.environ.get("EIA_API_KEY", "")
    if not fred_key:
        sys.exit("Set FRED_API_KEY in your environment first (see .env.example).")
    fred = Fred(api_key=fred_key)

    def to_monthly(s):
        s = s.dropna()
        s.index = pd.to_datetime(s.index)
        return s.resample("MS").last().ffill()

    def fetch_eia_steo(series_id):
        url = "https://api.eia.gov/v2/steo/data/"
        params = {
            "api_key": eia_key, "frequency": "monthly", "data[0]": "value",
            "facets[seriesId][]": series_id, "start": START[:7], "end": END[:7],
            "sort[0][column]": "period", "sort[0][direction]": "asc",
            "length": 500, "offset": 0,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        rows = r.json()["response"]["data"]
        if not rows:
            print(f"  WARNING — no data for {series_id}; skipped")
            return None
        return pd.Series({pd.Timestamp(r_["period"] + "-01"): float(r_["value"])
                          for r_ in rows}, name=series_id)

    def fetch_yf(ticker):
        raw = yf.download(ticker, start=START, end=END, interval="1mo",
                          progress=False, auto_adjust=True)
        s = raw["Close"].squeeze().dropna()
        s.index = pd.to_datetime(s.index).to_period("M").to_timestamp()
        return s

    print("Collecting FRED series…")
    series = {
        "WTI_Spot": to_monthly(fred.get_series("WTISPLC", observation_start=START, observation_end=END)),
        "IndustrialProd": to_monthly(fred.get_series("INDPRO", observation_start=START, observation_end=END)),
        "CPI_Energy": to_monthly(fred.get_series("CPIENGSL", observation_start=START, observation_end=END)),
        "USD_DXY": to_monthly(fred.get_series("DTWEXBGS", observation_start=START, observation_end=END)),
        "GDP_Growth": to_monthly(fred.get_series("A191RL1Q225SBEA", observation_start=START, observation_end=END)),
        "WTI_Futures": fetch_yf("CL=F"),
        "Brent": fetch_yf("BZ=F"),
        "VIX": fetch_yf("^VIX"),
        "SP500": fetch_yf("^GSPC"),
    }
    if eia_key:
        print("Collecting EIA STEO series…")
        for sid, name in [("PAPR_OPEC", "OPEC_Prod"), ("PAPR_NONOPEC", "NonOPEC_Prod"),
                          ("PATC_OECD", "OECD_Demand"), ("PASC_OECD_T3", "OECD_Inventory"),
                          ("PATC_NONOECD", "NonOECD_Demand"), ("PARC_USA", "US_Ref_Cap")]:
            s = fetch_eia_steo(sid)
            if s is not None:
                series[name] = s

    idx = pd.date_range(START, END, freq="MS")
    df = pd.DataFrame(index=idx)
    for name, s in series.items():
        df[name] = s.reindex(idx)
    df.index.name = "date"
    os.makedirs(os.path.dirname(RAW_CSV), exist_ok=True)
    df.to_csv(RAW_CSV)
    print(f"Saved {df.shape} → {RAW_CSV}")


if __name__ == "__main__":
    main()
