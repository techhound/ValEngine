import pandas as pd
from ingestion.writer.write_csv import write_csv

# Your local OneDrive/SharePoint sync path
BASE_PATH = r"C:\Users\jjcoc\OneDrive - Data Science Review\Documents\Projects\Power BI\valuation-engine"

def main():
    # Load the tester.csv from the project root
    df = pd.read_csv("tester.csv")

    # Write it to the processed folder using your writer
    output_path = write_csv(df, "tester_output.csv", BASE_PATH)

    print(f"File successfully written to: {output_path}")

if __name__ == "__main__":
    main()
