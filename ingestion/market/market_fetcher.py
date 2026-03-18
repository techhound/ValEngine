import yfinance as yf
import pandas as pd

def fetch_market_data(ticker: str) -> pd.DataFrame:
    t = yf.Ticker(ticker)
    info = t.info

    df = pd.DataFrame([{
        "Ticker": ticker.upper(),
        "CompanyName": info.get("longName"),
        "MarketPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
        "MarketCap": info.get("marketCap"),
        "Volume": info.get("volume"),
        "Exchange": info.get("exchange"),
        "Beta": info.get("beta"),
        "52WeekHigh": info.get("fiftyTwoWeekHigh"),
        "52WeekLow": info.get("fiftyTwoWeekLow"),
        "Sector": info.get("sector"),
        "Industry": info.get("industry"),
        "FloatShares": info.get("floatShares"),
        "SharesOutstanding_Market": info.get("sharesOutstanding")
        
    }])

    return df

