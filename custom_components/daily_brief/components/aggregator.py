"""Content aggregation component for Daily Brief."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

import aiohttp

from ..const import MAX_CONCURRENT_FETCHES
from ..feeds import Deduplicator, FeedParser, get_feeds_from_packs
from ..storage import ContentSource, Database
from ..storage.models import Article

_LOGGER = logging.getLogger(__name__)


class ContentAggregator:
    """Aggregate content from multiple sources."""

    def __init__(self, database: Database) -> None:
        """Initialize aggregator.

        Args:
            database: Database instance

        """
        self.database = database
        self.parser = FeedParser()
        self.deduplicator = Deduplicator()

    async def fetch_all_sources(
        self,
        content_packs: list[str] | None = None,
        custom_feeds: list[dict[str, Any]] | None = None,
    ) -> list[Article]:
        """Fetch articles from all enabled sources.

        Args:
            content_packs: List of content pack IDs to use
            custom_feeds: List of custom feed dictionaries

        Returns:
            List of unique Article objects

        """
        _LOGGER.info("Starting content aggregation")

        # Get sources from content packs
        sources = []

        if content_packs:
            pack_feeds = get_feeds_from_packs(content_packs)
            for feed in pack_feeds:
                sources.append(
                    ContentSource(
                        name=feed["name"],
                        url=feed["url"],
                        type="rss",
                        category=feed["category"],
                        language=feed["language"],
                        weight=feed.get("weight", 1.0),
                        enabled=True,
                    )
                )

        # Add custom feeds
        if custom_feeds:
            for feed in custom_feeds:
                sources.append(
                    ContentSource(
                        name=feed.get("name", "Custom Feed"),
                        url=feed["url"],
                        type="rss",
                        category=feed.get("category", "general"),
                        language=feed.get("language", "en"),
                        weight=feed.get("weight", 1.0),
                        enabled=True,
                    )
                )

        # Also get sources from database
        db_sources = await self.database.get_sources(enabled_only=True)
        sources.extend(db_sources)

        if not sources:
            _LOGGER.warning("No content sources configured")
            return []

        _LOGGER.info("Fetching from %d sources", len(sources))

        # Fetch articles from all sources in parallel
        all_articles = await self._fetch_parallel(sources)

        _LOGGER.info("Fetched %d total articles", len(all_articles))

        # Deduplicate articles
        unique_articles = self.deduplicator.deduplicate(all_articles)

        _LOGGER.info("After deduplication: %d unique articles", len(unique_articles))

        # Save articles to database
        await self._save_articles(unique_articles)

        return unique_articles

    async def _fetch_parallel(self, sources: list[ContentSource]) -> list[Article]:
        """Fetch articles from multiple sources in parallel.

        Args:
            sources: List of content sources

        Returns:
            Combined list of all articles

        """
        async with aiohttp.ClientSession() as session:
            parser = FeedParser(session)

            # Create tasks with semaphore to limit concurrency
            semaphore = asyncio.Semaphore(MAX_CONCURRENT_FETCHES)

            async def fetch_with_semaphore(source: ContentSource) -> list[Article]:
                async with semaphore:
                    return await self._fetch_source(parser, source)

            tasks = [fetch_with_semaphore(source) for source in sources]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Flatten results and filter out errors
            all_articles: list[Article] = []
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    _LOGGER.error("Error fetching source: %s", result)

            return all_articles

    async def _fetch_source(
        self, parser: FeedParser, source: ContentSource
    ) -> list[Article]:
        """Fetch articles from a single source.

        Args:
            parser: Feed parser instance
            source: Content source

        Returns:
            List of articles

        """
        try:
            _LOGGER.debug("Fetching source: %s (%s)", source.name, source.url)

            # Fetch and parse feed
            articles = await parser.fetch_feed(source.url, source.id)

            # Apply source weight to articles
            for article in articles:
                article.score = source.weight

            # Update source fetch time in database
            if source.id:
                await self.database.update_source_fetch_time(source.id)

            return articles

        except Exception as err:
            _LOGGER.error("Error fetching source %s: %s", source.name, err)
            return []

    async def _save_articles(self, articles: list[Article]) -> None:
        """Save articles to database.

        Args:
            articles: List of articles to save

        """
        for article in articles:
            try:
                await self.database.save_article(article)
            except Exception as err:
                _LOGGER.error("Error saving article %s: %s", article.id, err)

    async def get_recent_articles(
        self, limit: int | None = None, min_score: float = 0.0
    ) -> list[Article]:
        """Get recent articles from database.

        Args:
            limit: Maximum number of articles to return
            min_score: Minimum score threshold

        Returns:
            List of articles

        """
        return await self.database.get_articles(limit=limit, min_score=min_score)

    async def cleanup_old_articles(self, days: int = 7) -> None:
        """Clean up articles older than specified days.

        Args:
            days: Number of days to keep

        """
        await self.database.cleanup_old_articles(days)
        _LOGGER.info("Cleaned up articles older than %d days", days)
