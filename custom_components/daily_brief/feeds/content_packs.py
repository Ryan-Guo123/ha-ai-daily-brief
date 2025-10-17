"""Pre-configured content packs for Daily Brief."""
from __future__ import annotations

from typing import Any

# Content packs are collections of pre-configured RSS feeds
# organized by topic and language

CONTENT_PACKS: dict[str, dict[str, Any]] = {
    "tech_en": {
        "id": "tech_en",
        "name": "Technology (English)",
        "description": "Top technology news in English",
        "language": "en",
        "category": "technology",
        "icon": "mdi:laptop",
        "feeds": [
            {
                "name": "Hacker News",
                "url": "https://hnrss.org/frontpage",
                "weight": 1.2,
            },
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com/feed/",
                "weight": 1.0,
            },
            {
                "name": "The Verge",
                "url": "https://www.theverge.com/rss/index.xml",
                "weight": 1.0,
            },
            {
                "name": "Ars Technica",
                "url": "https://feeds.arstechnica.com/arstechnica/index",
                "weight": 0.9,
            },
            {
                "name": "Wired",
                "url": "https://www.wired.com/feed/rss",
                "weight": 0.9,
            },
        ],
        "topics": ["AI", "Startups", "Consumer Tech", "Software", "Hardware"],
    },
    "tech_zh": {
        "id": "tech_zh",
        "name": "科技新闻 (Chinese)",
        "description": "Top technology news in Chinese",
        "language": "zh",
        "category": "technology",
        "icon": "mdi:laptop",
        "feeds": [
            {
                "name": "36氪",
                "url": "https://rsshub.app/36kr/newsflashes",
                "weight": 1.1,
            },
            {
                "name": "少数派",
                "url": "https://rsshub.app/sspai/index",
                "weight": 1.0,
            },
            {
                "name": "爱范儿",
                "url": "https://rsshub.app/ifanr/app",
                "weight": 1.0,
            },
            {
                "name": "V2EX",
                "url": "https://rsshub.app/v2ex/topics/hot",
                "weight": 0.9,
            },
        ],
        "topics": ["人工智能", "创业公司", "消费电子", "软件开发", "互联网"],
    },
    "world_news_en": {
        "id": "world_news_en",
        "name": "World News (English)",
        "description": "International news coverage",
        "language": "en",
        "category": "news",
        "icon": "mdi:earth",
        "feeds": [
            {
                "name": "BBC World",
                "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
                "weight": 1.2,
            },
            {
                "name": "Reuters",
                "url": "https://www.reutersagency.com/feed/",
                "weight": 1.2,
            },
            {
                "name": "Al Jazeera",
                "url": "https://www.aljazeera.com/xml/rss/all.xml",
                "weight": 1.0,
            },
            {
                "name": "The Guardian",
                "url": "https://www.theguardian.com/world/rss",
                "weight": 1.0,
            },
        ],
        "topics": ["World Politics", "International Relations", "Global Events"],
    },
    "news_zh": {
        "id": "news_zh",
        "name": "中文新闻 (Chinese News)",
        "description": "Chinese language news",
        "language": "zh",
        "category": "news",
        "icon": "mdi:earth",
        "feeds": [
            {
                "name": "知乎热榜",
                "url": "https://rsshub.app/zhihu/hotlist",
                "weight": 1.0,
            },
            {
                "name": "澎湃新闻",
                "url": "https://rsshub.app/thepaper/featured",
                "weight": 1.1,
            },
        ],
        "topics": ["时事", "社会", "经济"],
    },
    "business": {
        "id": "business",
        "name": "Business & Finance",
        "description": "Business and financial news",
        "language": "en",
        "category": "business",
        "icon": "mdi:currency-usd",
        "feeds": [
            {
                "name": "Wall Street Journal",
                "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
                "weight": 1.2,
            },
            {
                "name": "Bloomberg",
                "url": "https://feeds.bloomberg.com/markets/news.rss",
                "weight": 1.2,
            },
            {
                "name": "Financial Times",
                "url": "https://www.ft.com/?format=rss",
                "weight": 1.1,
            },
        ],
        "topics": ["Markets", "Economy", "Corporate", "Finance"],
    },
    "science": {
        "id": "science",
        "name": "Science & Health",
        "description": "Scientific discoveries and health news",
        "language": "en",
        "category": "science",
        "icon": "mdi:flask",
        "feeds": [
            {
                "name": "Science Daily",
                "url": "https://www.sciencedaily.com/rss/all.xml",
                "weight": 1.0,
            },
            {
                "name": "Nature News",
                "url": "https://www.nature.com/nature.rss",
                "weight": 1.2,
            },
            {
                "name": "New Scientist",
                "url": "https://www.newscientist.com/feed/home",
                "weight": 1.0,
            },
        ],
        "topics": ["Research", "Health", "Medicine", "Biology", "Physics"],
    },
    "dev": {
        "id": "dev",
        "name": "Developer News",
        "description": "Programming and software development",
        "language": "en",
        "category": "technology",
        "icon": "mdi:code-braces",
        "feeds": [
            {
                "name": "GitHub Trending",
                "url": "https://rsshub.app/github/trending/daily",
                "weight": 1.1,
            },
            {
                "name": "Dev.to",
                "url": "https://dev.to/feed",
                "weight": 0.9,
            },
            {
                "name": "Lobsters",
                "url": "https://lobste.rs/rss",
                "weight": 1.0,
            },
        ],
        "topics": ["Programming", "Open Source", "Web Development", "DevOps"],
    },
}


def get_content_pack(pack_id: str) -> dict[str, Any] | None:
    """Get content pack by ID.

    Args:
        pack_id: Content pack ID

    Returns:
        Content pack dictionary or None if not found

    """
    return CONTENT_PACKS.get(pack_id)


def list_content_packs() -> list[dict[str, Any]]:
    """Get list of all available content packs.

    Returns:
        List of content pack dictionaries

    """
    return list(CONTENT_PACKS.values())


def get_feeds_from_packs(pack_ids: list[str]) -> list[dict[str, Any]]:
    """Get all feeds from specified content packs.

    Args:
        pack_ids: List of content pack IDs

    Returns:
        List of feed dictionaries with metadata

    """
    feeds = []

    for pack_id in pack_ids:
        pack = get_content_pack(pack_id)
        if not pack:
            continue

        for feed in pack["feeds"]:
            feeds.append({
                "name": feed["name"],
                "url": feed["url"],
                "weight": feed.get("weight", 1.0),
                "category": pack["category"],
                "language": pack["language"],
                "pack_id": pack_id,
            })

    return feeds
