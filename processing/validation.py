import logging

logger = logging.getLogger("ScraperLogger")

def validate_record(record: dict) -> bool:
    """Validates record integrity against business rules."""
    # 1. Must have recognizable source
    if record.get("source") not in ["Books to Scrape", "Quotes to Scrape"]:
        logger.warning(f"Validation failed: Invalid source '{record.get('source')}'")
        return False

    # 2. Must have title/name
    if not record.get("name_or_title"):
        logger.warning("Validation failed: Missing name_or_title.")
        return False

    # 3. Valid URL check
    if not record.get("source_url") or not record["source_url"].startswith("http"):
        logger.warning(f"Validation failed: Invalid URL '{record.get('source_url')}'")
        return False

    # 4. Price check for books
    if record["source"] == "Books to Scrape" and record.get("price", 0) < 0:
        logger.warning(f"Validation failed: Negative price for book '{record.get('name_or_title')}'")
        return False

    # 5. Rating range check
    if not (0 <= record.get("rating", 0) <= 5):
        logger.warning(f"Validation failed: Rating out of bounds for '{record.get('name_or_title')}'")
        return False

    return True