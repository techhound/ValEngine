import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

from ingestion.sec.cik_lookup import lookup_cik
from ingestion.sec.sec_fetcher import fetch_submissions, fetch_company_facts
from ingestion.sec.normalizer import (
    extract_latest_income,
    extract_latest_balance,
    extract_latest_cashflow,
    extract_latest_shares,
    extract_metadata
)
from valuation.engine import build_combined_table
from ingestion.writer.write_processed import save_combined_table
from ingestion.market.market_fetcher import fetch_market_data


# Base directory for SharePoint-synced project folder
BASE_DIR = r"C:\Users\jjcoc\OneDrive - Data Science Review\Documents\Projects\Power BI\valuation-engine"
CACHE_DIR = os.path.join(BASE_DIR, "raw")

st.set_page_config(page_title="Valuation Engine – Fundamentals Extractor", layout="centered")

st.title("📊 Valuation Engine – Latest Fundamentals Extractor")
st.write("Enter a ticker to pull SEC data, normalize it, run valuation models, and save a combined snapshot.")


ticker = st.text_input("Ticker symbol", placeholder="AAPL, MSFT, TSLA...")


if st.button("Run Extraction"):
    if not ticker.strip():
        st.error("Please enter a ticker.")
    else:
        try:
            # Step 1 — Resolve CIK
            cik = lookup_cik(ticker, CACHE_DIR)

            if not cik:
                st.warning(f"Ticker **{ticker.upper()}** not found in SEC ticker file.")
            else:
                st.success(f"Resolved CIK for **{ticker.upper()}** → **{cik}**")

                # Step 2 — Fetch SEC JSON
                with st.spinner("Fetching SEC submissions…"):
                    submissions = fetch_submissions(cik)

                with st.spinner("Fetching SEC company facts…"):
                    companyfacts = fetch_company_facts(cik)

                # Step 3 — Normalize to latest-only valuation fields
                with st.spinner("Extracting latest fundamentals…"):
                    income = extract_latest_income(companyfacts)
                    balance = extract_latest_balance(companyfacts)
                    cashflow = extract_latest_cashflow(companyfacts)
                    shares = extract_latest_shares(submissions)
                    metadata = extract_metadata(submissions)

                with st.spinner("Fetching market data…"):
                    market = fetch_market_data(ticker)


                st.subheader("Latest Income Statement")
                st.dataframe(income)

                st.subheader("Latest Balance Sheet")
                st.dataframe(balance)

                st.subheader("Latest Cash Flow")
                st.dataframe(cashflow)

                st.subheader("Latest Shares Outstanding")
                st.dataframe(shares)

                st.subheader("Company Metadata")
                st.dataframe(metadata)

                # Step 4 — Build combined valuation snapshot
                with st.spinner("Building combined valuation snapshot…"):
                    combined = build_combined_table(
                        ticker,
                        income,
                        balance,
                        cashflow,
                        shares,
                        metadata,
                        market
                    )

                st.subheader("Combined Fundamentals + Valuation")
                st.dataframe(combined)

                # Step 5 — Save combined CSV to SharePoint
                with st.spinner("Saving valuation snapshot…"):
                    save_path = save_combined_table(
                        ticker,
                        combined,
                        base_dir=BASE_DIR
                    )

                st.success("Valuation snapshot saved successfully.")
                st.write(f"📄 File saved at: `{save_path}`")

        except Exception as e:
            st.error(f"An error occurred: {e}")


st.divider()

st.subheader("Ticker Cache Status")
cache_path = os.path.join(CACHE_DIR, "ticker.txt")

if os.path.exists(cache_path):
    st.write(f"📄 Cache file found at: `{cache_path}`")
    st.write(f"🕒 Last updated: {os.path.getmtime(cache_path)}")
else:
    st.write("⚠️ No ticker cache found yet. It will be downloaded automatically on first lookup.")
