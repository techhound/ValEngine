import pandas as pd
from typing import Dict, Any, Optional


def _extract_latest_fact(facts: Dict[str, Any], tag: str, unit: str = "USD") -> Optional[Dict[str, Any]]:
    """
    Extract the most recent fact for a given XBRL tag and unit.
    Returns a dict with value, end date, and form type.
    """
    try:
        entries = facts[tag]["units"][unit]
    except KeyError:
        return None

    # Sort by end date descending
    entries = sorted(entries, key=lambda x: x.get("end", ""), reverse=True)

    for entry in entries:
        # Skip entries missing values
        if "val" not in entry:
            continue
        return {
            "value": entry["val"],
            "end": entry.get("end"),
            "form": entry.get("form")
        }

    return None


def extract_latest_income(companyfacts: Dict[str, Any]) -> pd.DataFrame:
    facts = companyfacts["facts"]["us-gaap"]

    fields = {
        "Revenue": ("Revenues", "USD"),
        "OperatingIncome": ("OperatingIncomeLoss", "USD"),
        "NetIncome": ("NetIncomeLoss", "USD"),
        "EPSBasic": ("EarningsPerShareBasic", "USD/shares"),
        "EPSDiluted": ("EarningsPerShareDiluted", "USD/shares")
    }

    data = {}
    for col, (tag, unit) in fields.items():
        result = _extract_latest_fact(facts, tag, unit)
        data[col] = result["value"] if result else None

    return pd.DataFrame([data])


def extract_latest_balance(companyfacts: Dict[str, Any]) -> pd.DataFrame:
    facts = companyfacts["facts"]["us-gaap"]

    fields = {
        "TotalAssets": ("Assets", "USD"),
        "TotalLiabilities": ("Liabilities", "USD"),
        "ShareholderEquity": ("StockholdersEquity", "USD"),
        "CashAndEquivalents": ("CashAndCashEquivalentsAtCarryingValue", "USD"),
        "ShortTermDebt": ("ShortTermDebt", "USD"),
        "LongTermDebt": ("LongTermDebtNoncurrent", "USD")
    }

    data = {}
    for col, (tag, unit) in fields.items():
        result = _extract_latest_fact(facts, tag, unit)
        data[col] = result["value"] if result else None

    return pd.DataFrame([data])


def extract_latest_cashflow(companyfacts: Dict[str, Any]) -> pd.DataFrame:
    facts = companyfacts["facts"]["us-gaap"]

    fields = {
        "CFO": ("NetCashProvidedByUsedInOperatingActivities", "USD"),
        "CapEx": ("PaymentsToAcquirePropertyPlantAndEquipment", "USD")
    }

    data = {}
    for col, (tag, unit) in fields.items():
        result = _extract_latest_fact(facts, tag, unit)
        data[col] = result["value"] if result else None

    # Derived metric
    if data["CFO"] is not None and data["CapEx"] is not None:
        data["FreeCashFlow"] = data["CFO"] - abs(data["CapEx"])
    else:
        data["FreeCashFlow"] = None

    return pd.DataFrame([data])


def extract_latest_shares(submissions: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract latest shares outstanding from submissions JSON.
    """
    try:
        shares = submissions["filings"]["recent"]["sharesOutstanding"]
        forms = submissions["filings"]["recent"]["form"]
        dates = submissions["filings"]["recent"]["filingDate"]

        # Find the most recent entry with a valid shares value
        for shares_val, form, date in zip(shares, forms, dates):
            if shares_val is not None:
                return pd.DataFrame([{
                    "SharesOutstanding": shares_val,
                    "FilingDate": date,
                    "Form": form
                }])
    except Exception:
        pass

    return pd.DataFrame([{
        "SharesOutstanding": None,
        "FilingDate": None,
        "Form": None
    }])


def extract_metadata(submissions: Dict[str, Any]) -> pd.DataFrame:
    """
    Extract basic metadata about the company.
    """
    data = {
        "CIK": submissions.get("cik"),
        "Name": submissions.get("name"),
        "FiscalYearEnd": submissions.get("fiscalYearEnd"),
        "SIC": submissions.get("sic"),
        "SICDescription": submissions.get("sicDescription")
    }

    return pd.DataFrame([data])
