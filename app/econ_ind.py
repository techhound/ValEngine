



BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

import os
import pandas as pd
from datetime import datetime
from fredapi import Fred

FRED_API_KEY = "{YOUR_FRED_API_KEY}"

fred = Fred(api_key=FRED_API_KEY)


def fetch_series(series_id: str):
    """Fetch a FRED series as a pandas Series with datetime index."""
    try:
        s = fred.get_series(series_id)
        s = s.dropna()
        return s
    except Exception:
        return None


def latest_value(series):
    if series is None or len(series) == 0:
        return None
    return float(series.iloc[-1])


def yoy(series):
    if series is None or len(series) < 13:
        return None
    latest = series.iloc[-1]
    prev_year = series.iloc[-13]
    return float((latest - prev_year) / prev_year * 100)


def build_macro_snapshot():
    # Interest rates
    dgs10 = fetch_series("DGS10")
    fedfunds = fetch_series("FEDFUNDS")

    # Inflation
    cpi = fetch_series("CPIAUCSL")
    ppi = fetch_series("PPIACO")
    t5yie = fetch_series("T5YIE")

    # Growth
    gdp = fetch_series("GDP")
    ism_mfg = fetch_series("NAPM")      # fredapi CAN fetch this
    ism_srv = fetch_series("NAPMS")     # fredapi CAN fetch this
    corp_profits = fetch_series("CP")

    # Risk appetite
    vix = fetch_series("VIXCLS")
    baa10y = fetch_series("BAA10Y")

    df = pd.DataFrame([{
        "AsOfDate": datetime.today().strftime("%Y-%m-%d"),

        # Interest rates
        "TenYearYield": latest_value(dgs10),
        "FedFundsRate": latest_value(fedfunds),

        # Inflation
        "CPI_YoY": yoy(cpi),
        "PPI_YoY": yoy(ppi),
        "InflationExpectations_5Y": latest_value(t5yie),

        # Growth
        "GDP_YoY": yoy(gdp),
        "ISM_Manufacturing": latest_value(ism_mfg),
        "ISM_Services": latest_value(ism_srv),
        "CorporateProfits_YoY": yoy(corp_profits),

        # Risk appetite
        "VIX": latest_value(vix),
        "CreditSpread_BBB": latest_value(baa10y),
    }])

    return df


def save_macro_snapshot(base_dir: str):
    df = build_macro_snapshot()
    out_path = os.path.join(base_dir, "economy", "macro_snapshot.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    return out_path
