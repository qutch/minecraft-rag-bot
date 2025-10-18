import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import time

BASE_URL = "https://minecraft.wiki"
CATEGORY_URLS = {
    "blocks": "https://minecraft.wiki/w/Category:Blocks",
    "items": "https://minecraft.wiki/w/Category:Items",
    "entities": "https://minecraft.wiki/w/Category:Entities",
    "mobs": "https://minecraft.wiki/w/Category:Mobs",
    "biomes": "https://minecraft.wiki/w/Category:Biomes",
    "gameplay": "https://minecraft.wiki/w/Category:Gameplay"
}

BLACKLIST = ["Category:", "Template:", "File:", "Talk:", "User:", "Help:", "Module:"]

def get_soup(url):
    """Fetch a page and return a BeautifulSoup object."""
    time.sleep(0.5)
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def crawl_category(url, visited):
    """Recursively collect article links from a category page."""
    if url in visited:
        return set()
    visited.add(url)
    
    print(f"Crawling: {url}")
    # time.sleep(0.5)  # small delay to be polite

    soup = get_soup(url)
    if not soup:
        return set()

    links = set()

    # Article links inside this category
    for a in soup.select(".mw-category-group a"):
        href = a.get("href")
        if not href:
            continue
        full_url = urljoin(BASE_URL, href)
        if any(b in full_url for b in BLACKLIST):
            continue
        links.add(full_url)

    # Follow subcategories
    for a in soup.select(".CategoryTreeItem a"):
        subcat = urljoin(BASE_URL, a.get("href"))
        links |= crawl_category(subcat, visited)

    # Handle pagination
    next_link = soup.find("a", string="next page")
    if next_link:
        next_url = urljoin(BASE_URL, next_link["href"])
        links |= crawl_category(next_url, visited)

    return links


def main():
    results = {}

    for category, url in CATEGORY_URLS.items():
        print(f"\nCrawling category: {category}")
        visited = set()
        links = crawl_category(url, visited)
        results[category] = sorted(list(links))
        print(f"{category}: {len(links)} pages found")

    # Save to JSON
    with open("minecraft_main_features.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nSaved all results to minecraft_main_features.json")


if __name__ == "__main__":
    main()
