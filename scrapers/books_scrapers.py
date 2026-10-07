import requests
from bs4 import BeautifulSoup
import logging
import time

logger = logging.getLogger("ScraperLogger")

class BooksScraper:
    BASE_URL = "https://books.toscrape.com/"

    def __init__(self, delay: float = 1.0):
        self.session = requests.Session()
        self.delay = delay

    def scrape_catalog(self) -> list[dict]:
        records = []
        current_url = url = f"{self.BASE_URL}catalogue/page-1.html"
        page_num = 1

        while current_url:
            logger.info(f"[Books] Scraping page {page_num}: {current_url}")
            try:
                response = self.session.get(current_url, timeout=10)
                if response.status_code != 200:
                    logger.error(f"[Books] HTTP {response.status_code} encountered at {current_url}")
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                books = soup.find_all('article', class_='product_pod')

                for book in books:
                    try:
                        title = book.h3.a['title']
                        price_str = book.find('p', class_='price_color').text
                        rating_elem = book.find('p', class_='star-rating')
                        rating_str = rating_elem['class'][1] if rating_elem else ""
                        detail_url = book.h3.a['href']
                        full_detail_url = f"{self.BASE_URL}catalogue/{detail_url}"

                        # Fetch detail page for description & category
                        category, description = self._scrape_book_details(full_detail_url)

                        records.append({
                            "source": "Books to Scrape",
                            "source_url": full_detail_url,
                            "name_or_title": title,
                            "category": category,
                            "price": price_str,
                            "rating": rating_str,
                            "author": "",
                            "tags": category,
                            "description": description
                        })
                    except Exception as e:
                        logger.warning(f"[Books] Error parsing individual book item: {e}")

                # Pagination check
                next_btn = soup.find('li', class_='next')
                if next_btn and next_btn.a:
                    next_page_relative = next_btn.a['href']
                    # Handle relative path resolution for pagination
                    if 'catalogue/' in current_url:
                        base_catalog = current_url.rsplit('/', 1)[0] + '/'
                        current_url = base_catalog + next_page_relative
                    else:
                        current_url = f"{self.BASE_URL}catalogue/{next_page_relative}"
                    page_num += 1
                    time.sleep(self.delay)
                else:
                    current_url = None

            except requests.RequestException as e:
                logger.error(f"[Books] Request failed at {current_url}: {e}")
                break

        return records

    def _scrape_book_details(self, detail_url: str) -> tuple[str, str]:
        try:
            res = self.session.get(detail_url, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                # Category is in breadcrumbs
                breadcrumb = soup.find('ul', class_='breadcrumb')
                category = breadcrumb.find_all('li')[2].text.strip() if breadcrumb and len(breadcrumb.find_all('li')) > 2 else ""
                
                # Description
                desc_p = soup.find('div', id='product_description')
                description = desc_p.find_next_sibling('p').text.strip() if desc_p and desc_p.find_next_sibling('p') else ""
                return category, description
        except Exception as e:
            logger.debug(f"[Books] Could not fetch details for {detail_url}: {e}")
        return "", ""