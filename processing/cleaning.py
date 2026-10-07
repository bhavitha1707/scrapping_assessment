import re
from datetime import datetime
from urllib.parse import urljoin

def clean_text(text: str) -> str:
    """Removes extra whitespace, non-breaking spaces, and newlines."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def parse_price(price_str: str) -> float:
    """Extracts numeric float value from currency strings like '£51.77'."""
    if not price_str:
        return 0.0
    cleaned = re.sub(r'[^\d.]', '', price_str)
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def parse_rating(rating_str: str) -> int:
    """Converts textual ratings ('Three') to integers (3)."""
    rating_map = {
        'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
    }
    if not rating_str:
        return 0
    return rating_map.get(rating_str.strip().title(), 0)

def normalize_url(base_url: str, relative_url: str) -> str:
    """Resolves relative URLs against base domain."""
    if not relative_url:
        return ""
    return urljoin(base_url, relative_url)

def standardize_record(raw_data: dict, source_name: str, base_url: str) -> dict:
    """Maps raw source data into the unified schema."""
    return {
        "source": source_name,
        "source_url": normalize_url(base_url, raw_data.get("source_url", "")),
        "name_or_title": clean_text(raw_data.get("name_or_title", "")),
        "category": clean_text(raw_data.get("category", "")),
        "price": parse_price(raw_data.get("price", "0")),
        "rating": parse_rating(raw_data.get("rating", "0")),
        "author": clean_text(raw_data.get("author", "")),
        "tags": clean_text(raw_data.get("tags", "")),
        "description": clean_text(raw_data.get("description", "")),
        "scraped_at": datetime.utcnow().isoformat()
    }