import logging
import requests
import time

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "ValuationEngine/1.0 (James@DataAnalyticsHelper.com)"
}

BASE_URL = "https://data.sec.gov"


def _get_json(url: str, retries: int = 3, delay: float = 0.5):
    """
    Internal helper to GET JSON from the SEC with retry logic.

    Args:
        url: Full SEC endpoint URL.
        retries: Number of retry attempts.
        delay: Delay between retries in seconds.

    Returns:
        Parsed JSON dict.

    Raises:
        requests.RequestException if all retries fail.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info("Fetching SEC URL: %s", url)
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logger.warning("Attempt %s failed for %s: %s", attempt, url, e)
            if attempt == retries:
                logger.exception("All retries failed for %s", url)
                raise
            time.sleep(delay)


def fetch_submissions(cik: str) -> dict:
    """
    Fetch the SEC submissions JSON for a company.

    Args:
        cik: 10-digit zero-padded CIK string.

    Returns:
        JSON dict of submissions.
    """
    url = f"{BASE_URL}/submissions/CIK{cik}.json"
    return _get_json(url)


def fetch_company_facts(cik: str) -> dict:
    """
    Fetch the SEC companyfacts JSON (XBRL financials).

    Args:
        cik: 10-digit zero-padded CIK string.

    Returns:
        JSON dict of company facts.
    """
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
    return _get_json(url)


def fetch_filings(cik: str) -> dict:
    """
    Fetch the SEC filings list JSON.

    Args:
        cik: 10-digit zero-padded CIK string.

    Returns:
        JSON dict of filings.
    """
    url = f"{BASE_URL}/api/xbrl/filings/CIK{cik}.json"
    return _get_json(url)
