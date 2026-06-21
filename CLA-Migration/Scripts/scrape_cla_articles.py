import csv
import time
import re
from urllib.parse import urljoin

import requests
# pyrefly: ignore [missing-import]
from bs4 import BeautifulSoup

BASE_URL = "https://www.corporatelawacademy.net"
START_URL = "https://www.corporatelawacademy.net/case-studies"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_soup(url):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def extract_listing_articles(page_url):
    soup = get_soup(page_url)
    articles = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        title = link.get_text(" ", strip=True)

        if "/post/" not in href:
            continue

        if not title or len(title) < 10:
            continue

        full_url = urljoin(BASE_URL, href)
        slug = full_url.rstrip("/").split("/")[-1]

        articles.append({
            "title": title,
            "url": full_url,
            "slug": slug,
        })

    seen = set()
    clean_articles = []

    for article in articles:
        if article["url"] not in seen:
            clean_articles.append(article)
            seen.add(article["url"])

    return clean_articles


def extract_article_body(article_url):
    soup = get_soup(article_url)

    title_tag = soup.find("h1")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""

    stop_phrases = [
        "let's talk",
        "facebook",
        "linkedin",
        "instagram",
        "© 2026 by corporate law academy",
        "scrivi un commento",
        "commenti",
    ]

    ignored_exact = [
        "Home",
        "People",
        "Events",
        "Articles",
        "Moot Courts",
        "Join Us!",
        "Search",
        "All Posts",
    ]

    text_blocks = []

    for tag in soup.find_all(["h2", "h3", "h4", "h5", "h6", "p", "li"]):
        text = tag.get_text(" ", strip=True)

        if not text:
            continue

        lower = text.lower()

        if any(phrase in lower for phrase in stop_phrases):
            break

        if text in ignored_exact:
            continue

        text_blocks.append(text)

    content = "\n\n".join(text_blocks)

    return {
        "title": title,
        "content": content,
    }


def main():
    all_articles = []
    listing_articles = extract_listing_articles(START_URL)

    print(f"Found {len(listing_articles)} article links")

    for article in listing_articles:
        print(f"Scraping: {article['title']}")

        try:
            article_data = extract_article_body(article["url"])

            if not article_data["content"].strip():
                print(f"EMPTY CONTENT: {article['url']}")

            all_articles.append({
                "title": article_data["title"] or article["title"],
                "slug": article["slug"],
                "old_url": article["url"],
                "content": article_data["content"],
                "author": "",
                "published_at": "",
                "cover_image_url": "",
                "status": "draft",
                "source": "wix_public_scrape",
            })

            time.sleep(1)

        except Exception as error:
            print(f"ERROR: {article['url']}")
            print(error)

    output_file = "CLA-Migration/Scripts/wix_articles_scraped_sample.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "title",
                "slug",
                "old_url",
                "content",
                "author",
                "published_at",
                "cover_image_url",
                "status",
                "source",
            ],
        )

        writer.writeheader()
        writer.writerows(all_articles)

    print(f"Done. Scraped {len(all_articles)} articles.")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()