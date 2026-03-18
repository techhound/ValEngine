import pandas as pd
import numpy as np
from typing import Optional, Dict


def _safe(val):
    try:
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return None
        return float(val)
    except Exception:
        return None


# -----------------------------
# Valuation Models
# -----------------------------

def dcf_valuation(
    fcf: float,
    growth_rate: float = 0.05,
    discount_rate: float = 0.10,
    terminal_growth: float = 0.02,
    years: int = 5
) -> Optional[float]:
    fcf = _safe(fcf)
    if fcf is None:
        return None

    cashflows = []
    current_fcf = fcf

    for _ in range(years):
        current_fcf *= (1 + growth_rate)
        cashflows.append(current_fcf)

    discounted = [cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cashflows)]

    terminal_value = cashflows[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    terminal_discounted = terminal_value / ((1 + discount_rate) ** years)

    return sum(discounted) + terminal_discounted


def fcf_yield_valuation(fcf: float, shares: float, required_yield: float = 0.08) -> Optional[float]:
    fcf = _safe(fcf)
    shares = _safe(shares)

    if fcf is None or shares is None or shares == 0:
        return None

    intrinsic_market_cap = fcf / required_yield
    return intrinsic_market_cap / shares


def graham_valuation(eps: float, growth_rate: float = 0.05, aaabond_yield: float = 0.04) -> Optional[float]:
    eps = _safe(eps)
    if eps is None:
        return None

    return eps * (8.5 + 2 * (growth_rate * 100)) * (4.4 / (aaabond_yield * 100))


def multiples_valuation(
    earnings: float,
    revenue: float,
    ebitda: Optional[float],
    shares: float,
    pe_multiple: float = 15,
    ps_multiple: float = 3,
    ev_ebitda_multiple: float = 10
) -> Dict[str, Optional[float]]:
    earnings = _safe(earnings)
    revenue = _safe(revenue)
    ebitda = _safe(ebitda)
    shares = _safe(shares)

    results = {}

    results["PE_Value"] = (earnings * pe_multiple) / shares if earnings and shares else None
    results["PS_Value"] = (revenue * ps_multiple) / shares if revenue and shares else None

    if ebitda and shares:
        ev = ebitda * ev_ebitda_multiple
        results["EV_EBITDA_Value"] = ev / shares
    else:
        results["EV_EBITDA_Value"] = None

    return results


# -----------------------------
# Unified Valuation + Fundamentals Table
# -----------------------------

def build_combined_table(
    ticker: str,
    income_df: pd.DataFrame,
    balance_df: pd.DataFrame,
    cashflow_df: pd.DataFrame,
    shares_df: pd.DataFrame,
    metadata_df: pd.DataFrame,
    market_df: pd.DataFrame
) -> pd.DataFrame:

    # Drop duplicates if they sneak in
    if "SharesOutstanding" in market_df.columns:
        market_df = market_df.drop(columns=["SharesOutstanding"])

    # Extract fundamentals
    fcf = _safe(cashflow_df["FreeCashFlow"].iloc[0])
    eps = _safe(income_df["EPSDiluted"].iloc[0] or income_df["EPSBasic"].iloc[0])
    net_income = _safe(income_df["NetIncome"].iloc[0])
    revenue = _safe(income_df["Revenue"].iloc[0])
    shares = _safe(shares_df["SharesOutstanding"].iloc[0])

    # Valuation models
    dcf_val = dcf_valuation(fcf)
    fcf_yield_val = fcf_yield_valuation(fcf, shares)
    graham_val = graham_valuation(eps)
    multiples = multiples_valuation(
        earnings=net_income,
        revenue=revenue,
        ebitda=None,
        shares=shares
    )

    # Merge fundamentals + metadata + market data
    combined = pd.concat(
        [income_df, balance_df, cashflow_df, shares_df, metadata_df, market_df],
        axis=1
    )

    # Add ticker
    combined["Ticker"] = ticker.upper()

    # Add valuation outputs
    combined["DCF_Value"] = dcf_val
    combined["FCF_Yield_Value"] = fcf_yield_val
    combined["Graham_Value"] = graham_val
    combined["PE_Value"] = multiples["PE_Value"]
    combined["PS_Value"] = multiples["PS_Value"]
    combined["EV_EBITDA_Value"] = multiples["EV_EBITDA_Value"]

    return combined

