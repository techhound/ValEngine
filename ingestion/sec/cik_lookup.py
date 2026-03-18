import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from ingestion.sec.fetch_ticker_file import download_ticker_file

logger = logging.getLogger(__name__)

CACHE_FILENAME = "ticker.txt"
CACHE_MAX_AGE_HOURS = 24


def _is_cache_stale(path: str) -> bool:
    """Return True if the ticker.txt cache is missing or older than CACHE_MAX_AGE_HOURS."""
    if not os.path.exists(path):
        return True

    modified_time = datetime.fromtimestamp(os.path.getmtime(path))
    age = datetime.now() - modified_time
    return age > timedelta(hours=CACHE_MAX_AGE_HOURS)


def load_ticker_cache(cache_dir: str) -> pd.DataFrame:
    """
    Load ticker.txt from cache, refreshing if needed.

    Returns:
        DataFrame with columns ['ticker', 'cik']
    """
    cache_path = os.path.join(cache_dir, CACHE_FILENAME)

    try:
        if _is_cache_stale(cache_path):
            logger.info("Ticker cache missing or stale. Downloading fresh copy.")
            download_ticker_file(cache_path)

        df = pd.read_csv(cache_path, sep="\t", header=None, names=["ticker", "cik"])
        df["ticker"] = df["ticker"].str.upper()
        df["cik"] = df["cik"].astype(str).str.zfill(10)
        return df

    except Exception:
        logger.exception("Failed to load or parse ticker.txt")
        raise


def lookup_cik(ticker: str, cache_dir: str) -> str | None:
    """
    Look up a CIK for a given ticker symbol.

    Args:
        ticker: Stock ticker (case-insensitive)
        cache_dir: Directory where ticker.txt is stored

    Returns:
        Zero-padded 10-digit CIK string, or None if not found.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("ticker must be a non-empty string")

    ticker = ticker.upper().strip()

    try:
        df = load_ticker_cache(cache_dir)
        match = df.loc[df["ticker"] == ticker]

        if match.empty:
            logger.warning("Ticker %s not found in cache.", ticker)
            return None

        return match.iloc[0]["cik"]

    except Exception:
        logger.exception("Error during CIK lookup for ticker %s", ticker)
        raise
