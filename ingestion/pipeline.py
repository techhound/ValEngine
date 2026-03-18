from ingestion.writer.write_csv import write_csv
from config.settings import settings

def run_pipeline(ticker):
    # fetch SEC, yfinance, FRED, normalize...
    write_csv(financials_df, "financials.csv", settings.sharepoint_sync_path)
