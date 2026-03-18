from ingestion.sec.sec_fetcher import fetch_submissions, fetch_company_facts
from ingestion.sec.cik_lookup import lookup_cik

CACHE_DIR = r"C:\Users\jjcoc\OneDrive - Data Science Review\Documents\Projects\Power BI\valuation-engine\raw"

def main():
    cik = lookup_cik("AAPL", CACHE_DIR)
    print("CIK:", cik)

    subs = fetch_submissions(cik)
    print("Submissions keys:", subs.keys())

    facts = fetch_company_facts(cik)
    print("Company facts keys:", facts.keys())

if __name__ == "__main__":
    main()
