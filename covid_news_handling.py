"""Fetch COVID-related news headlines from NewsAPI (https://newsapi.org)."""

import logging

import requests

NEWS_API_URL = "https://newsapi.org/v2/everything"
DEFAULT_TERMS = "Covid COVID-19 coronavirus"


class NewsStore:
    """Holds the current headlines and remembers any the user has dismissed."""

    def __init__(self, api_key: str = "", search_terms: str = DEFAULT_TERMS,
                 max_articles: int = 5):
        self.api_key = api_key
        self.search_terms = search_terms
        self.max_articles = max_articles
        self.articles = []
        self.removed_titles = set()

    def update_news(self, update_name: str = "") -> list:
        """Fetch fresh headlines, leaving out any the user has dismissed."""
        fetched = news_API_request(self.search_terms, self.api_key)
        if fetched:
            self.articles = fetched
        logging.info("News update %r returned %d articles", update_name, len(fetched))
        return self.visible()

    def remove(self, title: str) -> None:
        """Dismiss an article so it won't come back on later updates."""
        self.removed_titles.add(title)

    def visible(self) -> list:
        """Return the articles to show on the dashboard."""
        shown = [a for a in self.articles if a["title"] not in self.removed_titles]
        return shown[: self.max_articles]


def news_API_request(covid_terms: str = DEFAULT_TERMS, api_key: str = "",
                     session=None) -> list:
    """Return a list of {title, content, url} dicts for articles matching any term.

    Returns an empty list (and logs why) if there is no API key or the
    request fails, so the dashboard keeps working without news.
    """
    if not api_key:
        logging.warning("No NewsAPI key configured; skipping news request")
        return []

    query = " OR ".join(covid_terms.split())
    http = session or requests
    try:
        response = http.get(
            NEWS_API_URL,
            params={"q": query, "language": "en", "sortBy": "publishedAt",
                    "pageSize": 20},
            headers={"X-Api-Key": api_key},
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        logging.error("NewsAPI request failed: %s", error)
        return []

    articles = []
    for item in payload.get("articles", []):
        title = item.get("title")
        if not title or title == "[Removed]":
            continue
        articles.append({
            "title": title,
            "content": item.get("description") or "",
            "url": item.get("url") or "",
        })
    return articles
