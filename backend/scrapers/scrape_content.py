import json
import requests
from bs4 import BeautifulSoup
import time
import os

FEATURES_FILE = "minecraft_main_features.json"  # your JSON with blocks, items, etc.
OUTPUT_FILE = "documents.json"
BASE_URL = "https://minecraft.wiki"

def clean_text(s):
    """Clean and normalize text."""
    return " ".join(s.replace("\n", " ").split())

def extract_main_content(url):
    """Extract title and main text from a wiki page."""
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"⚠️ Failed to fetch {url}: {e}")
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    title_tag = soup.find("h1", id="firstHeading")
    title = title_tag.text.strip() if title_tag else "Unknown Title"

    content_div = soup.find("div", class_="mw-parser-output")
    if not content_div:
        return None

    # Remove non-essential sections like tables, infoboxes, etc.
    for tag in content_div.select(
        ".infobox, .navbox, .hatnote, .toc, .thumb, .mw-editsection, table, .metadata"
    ):
        tag.decompose()

    text = clean_text(content_div.get_text(" "))

    return {
        "title": title,
        "url": url,
        "content": text
    }

def load_json(filename):
    """Safely load a JSON file or return empty dict/list if not found."""
    if not os.path.exists(filename):
        if filename.endswith(".json"):
            return {} if "features" in filename else []
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    # Load features JSON (with categories like blocks, items, etc.)
    features = load_json(FEATURES_FILE)
    if not features:
        print(f"⚠️ Could not load {FEATURES_FILE} or it's empty.")
        return

    # Load existing scraped data
    documents = load_json(OUTPUT_FILE)
    existing_urls = {doc["url"] for doc in documents}
    print(f"📘 Loaded {len(documents)} existing documents.")

    new_docs = []

    # Iterate over categories and URLs
    for category, urls in features.items():
        print(f"\n🔹 Category: {category} ({len(urls)} URLs)")
        for i, url in enumerate(urls, 1):
            if url in existing_urls:
                print(f"   [{i}] ⏩ Skipping (already exists): {url}")
                continue

            print(f"   [{i}] 🧱 Scraping: {url}")
            doc = extract_main_content(url)
            if doc:
                doc["category"] = category  # tag the source type (block, item, etc.)
                new_docs.append(doc)
                existing_urls.add(url)
            time.sleep(0.5)  # polite delay

    # Merge and save
    all_docs = documents + new_docs
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_docs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done! Added {len(new_docs)} new documents.")
    print(f"💾 Total saved in {OUTPUT_FILE}: {len(all_docs)}")

if __name__ == "__main__":
    main()
