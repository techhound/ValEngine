import os
import pandas as pd


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_csv(df: pd.DataFrame, path: str) -> None:
    ensure_dir(os.path.dirname(path))
    df.to_csv(path, index=False, encoding="utf-8")


def save_combined_table(ticker: str, combined_df: pd.DataFrame, base_dir: str) -> str:
    # ticker = ticker.upper()
    # out_dir = os.path.join(base_dir, "processed", ticker)
    # path = os.path.join(out_dir, "valuation_snapshot.csv")
    filename = f"{ticker.upper()}_valuation_snapshot.csv"
    path = os.path.join(base_dir, "processed", filename)


    write_csv(combined_df, path)
    return path
