from ingestion.market.market_fetcher import fetch_market_data

def test_market_module(ticker: str):
    print(f"\n=== Testing Market Data Fetch for {ticker.upper()} ===\n")

    try:
        df = fetch_market_data(ticker)
        print(df.to_string(index=False))
        print("\nTest completed successfully.\n")

    except Exception as e:
        print(f"Error fetching market data for {ticker}: {e}")


if __name__ == "__main__":
    test_market_module("MSFT")

