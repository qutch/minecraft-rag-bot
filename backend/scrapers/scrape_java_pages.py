import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://minecraft.wiki"
START_URL = "https://minecraft.wiki/w/Category:Java_Edition"

visited = set()
pages = set()

BLACKLIST = ["Category:", "Template:", "File:", "Talk:", "User:", "Help:", "Module:"]

def crawl_category(url):
    """Recursively crawl category pages for Java Edition."""
    if url in visited:
        return
    visited.add(url)

    print(f"Crawling: {url}")
    time.sleep(0.5)  # small delay to be polite

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(res.text, "html.parser")

    # Collect article links
    for a in soup.select(".mw-category-group a"):
        href = a.get("href")
        if not href:
            continue
        full_url = urljoin(BASE_URL, href)
        # Skip blacklisted namespaces
        if any(b in full_url for b in BLACKLIST):
            continue
        pages.add(full_url)

    # Follow subcategories
    for a in soup.select(".CategoryTreeItem a"):
        subcat = urljoin(BASE_URL, a.get("href"))
        crawl_category(subcat)

    # Follow pagination
    next_link = soup.find("a", string="next page")
    if next_link:
        next_url = urljoin(BASE_URL, next_link["href"])
        crawl_category(next_url)


def main():
    print("Starting crawl from:", START_URL)
    crawl_category(START_URL)

    # Save results
    pages_list = sorted(pages)
    with open("java_pages.json", "w", encoding="utf-8") as f:
        json.dump(pages_list, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Collected {len(pages_list)} pages.")
    print("Saved to java_pages.json")


if __name__ == "__main__":
    main()
