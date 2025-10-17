"""RSS feed parser for Daily Brief."""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from langdetect import LangDetectException, detect

from ..const import API_TIMEOUT
from ..storage.models import Article

_LOGGER = logging.getLogger(__name__)


class FeedParser:
    """RSS/Atom feed parser."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize parser."""
        self._session = session
        self._should_close_session = session is None

    async def __aenter__(self) -> FeedParser:
        """Async context manager entry."""
        if not self._session:
            self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        if self._should_close_session and self._session:
            await self._session.close()

    async def fetch_feed(self, url: str, source_id: int | None = None) -> list[Article]:
        """Fetch and parse RSS feed.

        Args:
            url: Feed URL
            source_id: Optional source ID for tracking

        Returns:
            List of Article objects

        """
        try:
            _LOGGER.debug("Fetching feed: %s", url)

            if not self._session:
                self._session = aiohttp.ClientSession()

            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as response:
                if response.status != 200:
                    _LOGGER.warning("Failed to fetch feed %s: HTTP %d", url, response.status)
                    return []

                content = await response.text()

            # Parse feed
            feed = feedparser.parse(content)

            if feed.bozo:
                _LOGGER.warning("Feed %s has malformed XML: %s", url, feed.bozo_exception)

            articles = []
            for entry in feed.entries:
                article = self._parse_entry(entry, source_id)
                if article:
                    articles.append(article)

            _LOGGER.info("Parsed %d articles from %s", len(articles), url)
            return articles

        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching feed %s: %s", url, err)
            return []
        except Exception as err:
            _LOGGER.error("Error parsing feed %s: %s", url, err)
            return []

    def _parse_entry(self, entry: Any, source_id: int | None = None) -> Article | None:
        """Parse a single feed entry into an Article.

        Args:
            entry: Feed entry from feedparser
            source_id: Optional source ID

        Returns:
            Article object or None if parsing fails

        """
        try:
            # Extract URL (required)
            url = entry.get("link", "")
            if not url:
                _LOGGER.debug("Skipping entry without URL")
                return None

            # Generate article ID from URL
            article_id = hashlib.md5(url.encode()).hexdigest()

            # Extract title (required)
            title = entry.get("title", "").strip()
            if not title:
                _LOGGER.debug("Skipping entry without title: %s", url)
                return None

            # Extract summary/description
            summary = ""
            if "summary" in entry:
                summary = self._clean_html(entry.summary)
            elif "description" in entry:
                summary = self._clean_html(entry.description)

            # Extract content
            content = ""
            if "content" in entry and entry.content:
                content = self._clean_html(entry.content[0].value)
            elif summary:
                content = summary

            # Extract author
            author = entry.get("author", "")

            # Extract published date
            published_at = None
            if "published_parsed" in entry and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except (TypeError, ValueError):
                    pass

            if not published_at and "updated_parsed" in entry and entry.updated_parsed:
                try:
                    published_at = datetime(*entry.updated_parsed[:6])
                except (TypeError, ValueError):
                    pass

            # Detect language
            language = self._detect_language(title + " " + summary)

            # Extract topics/tags
            topics = []
            if "tags" in entry:
                topics = [tag.term for tag in entry.tags if hasattr(tag, "term")]

            # Create article
            article = Article(
                id=article_id,
                source_id=source_id,
                title=title,
                summary=summary,
                content=content,
                url=url,
                author=author,
                published_at=published_at,
                fetched_at=datetime.now(),
                language=language,
                topics=topics,
                score=0.0,  # Will be calculated later
            )

            return article

        except Exception as err:
            _LOGGER.error("Error parsing entry: %s", err)
            return None

    def _clean_html(self, html_content: str) -> str:
        """Clean HTML tags and return plain text.

        Args:
            html_content: HTML content

        Returns:
            Plain text

        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            # Get text
            text = soup.get_text(separator=" ", strip=True)
            # Clean up whitespace
            text = " ".join(text.split())
            return text
        except Exception as err:
            _LOGGER.debug("Error cleaning HTML: %s", err)
            return html_content

    def _detect_language(self, text: str) -> str:
        """Detect language of text.

        Args:
            text: Text to analyze

        Returns:
            Language code (ISO 639-1)

        """
        try:
            if not text or len(text) < 10:
                return "en"

            lang = detect(text)
            return lang
        except LangDetectException:
            return "en"
        except Exception as err:
            _LOGGER.debug("Error detecting language: %s", err)
            return "en"
