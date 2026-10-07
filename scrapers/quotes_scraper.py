import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger("ScraperLogger")

class QuotesScraper:
    BASE_URL = "https://quotes.toscrape.com/"

    def __init__(self, delay: float = 1.0):
        self.session = requests.Session()
        self.delay = delay

    def scrape_catalog(self) -> list[dict]:
        records = []
        current_url = self.BASE_URL
        page_num = 1

        while current_url:
            logger.info(f"[Quotes] Scraping page {page_num}: {current_url}")
            try:
                response = self.session.get(current_url, timeout=10)
                if response.status_code != 200:
                    logger.error(f"[Quotes] HTTP {response.status_code} encountered at {current_url}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                quotes = soup.find_all('div', class_='quote')

                for quote in quotes:
                    try:
                        text = quote.find('span', class_='text').text
                        author = quote.find('small', class_='author').text
                        
                        # Author detail link
                        author_relative_url = quote.find('a')['href']
                        author_url = f"{self.BASE_URL.rstrip('/')}{author_relative_url}"

                        tag_elements = quote.find_all('a', class_='tag')
                        tags = ", ".join([tag.text for tag in tag_elements])

                        records.append({
                            "source": "Quotes to Scrape",
                            "source_url": current_url,
                            "name_or_title": text,
                            "category": "",
                            "price": "0",
                            "rating": "",
                            "author": author,
                            "tags": tags,
                            "description": f"Tags: {tags}"
                        })
                    except Exception as e:
                        logger.warning(f"[Quotes] Error parsing quote item: {e}")

                # Pagination check
                next_btn = soup.find('li', class_='next')
                if next_btn and next_btn.a:
                    next_page_relative = next_btn.a['href']
                    current_url = f"{self.BASE_URL.rstrip('/')}{next_page_relative}"
                    page_num += 1
                    time.sleep(self.delay)
                else:
                    current_url = None

            except requests.RequestException as e:
                logger.error(f"[Quotes] Request failed at {current_url}: {e}")
                break

        return records