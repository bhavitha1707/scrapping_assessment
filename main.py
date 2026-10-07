import os
import time
import json
import logging
import pandas as pd
from datetime import datetime

from scrapers.books_scrapers import BooksScraper
from scrapers.quotes_scraper import QuotesScraper
from processing.cleaning import standardize_record
from processing.validation import validate_record
from processing.deduplication import deduplicate_records

# Setup Logging
os.makedirs("logs", exist_ok=True)
os.makedirs("output", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ScraperLogger")

def main():
    start_time = time.time()
    logger.info("=== Starting Web Scraping & Consolidation Pipeline ===")

    raw_records = []

    # 1. Scrape Books
    try:
        books_scraper = BooksScraper(delay=0.5)
        books_raw = books_scraper.scrape_catalog()
        logger.info(f"Collected {len(books_raw)} raw records from Books to Scrape.")
        for item in books_raw:
            raw_records.append(standardize_record(item, "Books to Scrape", BooksScraper.BASE_URL))
    except Exception as e:
        logger.error(f"Books scraping failed: {e}")

    # 2. Scrape Quotes
    try:
        quotes_scraper = QuotesScraper(delay=0.5)
        quotes_raw = quotes_scraper.scrape_catalog()
        logger.info(f"Collected {len(quotes_raw)} raw records from Quotes to Scrape.")
        for item in quotes_raw:
            raw_records.append(standardize_record(item, "Quotes to Scrape", QuotesScraper.BASE_URL))
    except Exception as e:
        logger.error(f"Quotes scraping failed: {e}")

    total_collected = len(raw_records)
    logger.info(f"Total raw records collected across all sources: {total_collected}")

    # 3. Validation
    valid_records = []
    rejected_count = 0
    for record in raw_records:
        if validate_record(record):
            valid_records.append(record)
        else:
            rejected_count += 1

    logger.info(f"Records passed validation: {len(valid_records)}, Rejected: {rejected_count}")

    # 4. Deduplication
    unique_records, duplicate_count = deduplicate_records(valid_records)
    logger.info(f"Duplicates detected and removed: {duplicate_count}")
    logger.info(f"Final unique records count: {len(unique_records)}")

    # 5. Output Generation
    df_final = pd.DataFrame(unique_records)
    csv_path = "output/final_dataset.csv"
    df_final.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"Final dataset successfully written to {csv_path}")

    execution_time = round(time.time() - start_time, 2)

    # 6. Summary Report
    summary = {
        "execution_timestamp": datetime.utcnow().isoformat(),
        "execution_time_seconds": execution_time,
        "total_records_collected": total_collected,
        "records_rejected_validation": rejected_count,
        "duplicates_removed": duplicate_count,
        "final_record_count": len(unique_records),
        "breakdown_by_source": df_final['source'].value_counts().to_dict() if not df_final.empty else {}
    }

    json_path = "output/summary_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=4)
    logger.info(f"Summary report written to {json_path}")
    logger.info("=== Pipeline Execution Complete ===")

if __name__ == "__main__":
    main()