import logging
import os
import requests

logger = logging.getLogger(__name__)

SEC_TICKER_URL = "https://www.sec.gov/include/ticker.txt"

# SEC requires a descriptive User-Agent
HEADERS = {
    "User-Agent": "ValuationEngine/1.0 (James@DataAnalyticsHelper.com)"
}


def download_ticker_file(destination_path: str) -> str:
    """
    Download the SEC ticker.txt file and save it to the given path.

    Args:
        destination_path: Full path where ticker.txt should be saved.

    Returns:
        The destination path.

    Raises:
        OSError: If the file cannot be written.
        requests.RequestException: If the download fails.
    """
    try:
        logger.info("Downloading SEC ticker file from %s", SEC_TICKER_URL)
        response = requests.get(SEC_TICKER_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        with open(destination_path, "wb") as f:
            f.write(response.content)

        logger.info("Saved ticker.txt to %s", destination_path)
        return destination_path

    except requests.RequestException as e:
        logger.exception("Failed to download ticker.txt from SEC")
        raise

    except OSError as e:
        logger.exception("Failed to write ticker.txt to %s", destination_path)
        raise
