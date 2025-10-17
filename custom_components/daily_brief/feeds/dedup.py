"""Article deduplication for Daily Brief."""
from __future__ import annotations

import logging
from difflib import SequenceMatcher
from typing import Any

from ..const import DEDUP_SIMILARITY_THRESHOLD
from ..storage.models import Article

_LOGGER = logging.getLogger(__name__)


class Deduplicator:
    """Article deduplication engine."""

    def __init__(self, similarity_threshold: float = DEDUP_SIMILARITY_THRESHOLD) -> None:
        """Initialize deduplicator.

        Args:
            similarity_threshold: Threshold for considering articles as duplicates (0.0-1.0)

        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, articles: list[Article]) -> list[Article]:
        """Remove duplicate articles from list.

        Args:
            articles: List of articles to deduplicate

        Returns:
            List of unique articles

        """
        if not articles:
            return []

        _LOGGER.debug("Deduplicating %d articles", len(articles))

        unique_articles: list[Article] = []
        seen_urls: set[str] = set()

        for article in articles:
            # Skip if exact URL match
            if article.url in seen_urls:
                _LOGGER.debug("Skipping duplicate URL: %s", article.url)
                continue

            # Check similarity with existing articles
            is_duplicate = False
            for existing in unique_articles:
                if self._are_similar(article, existing):
                    _LOGGER.debug(
                        "Found duplicate: '%s' similar to '%s'",
                        article.title[:50],
                        existing.title[:50],
                    )
                    # Keep the one with higher score, or the first one if scores are equal
                    if article.score > existing.score:
                        unique_articles.remove(existing)
                        seen_urls.remove(existing.url)
                    else:
                        is_duplicate = True
                        break

            if not is_duplicate:
                unique_articles.append(article)
                seen_urls.add(article.url)

        removed_count = len(articles) - len(unique_articles)
        if removed_count > 0:
            _LOGGER.info("Removed %d duplicate articles", removed_count)

        return unique_articles

    def _are_similar(self, article1: Article, article2: Article) -> bool:
        """Check if two articles are similar enough to be considered duplicates.

        Args:
            article1: First article
            article2: Second article

        Returns:
            True if articles are similar

        """
        # Must be same language
        if article1.language != article2.language:
            return False

        # Calculate title similarity
        title_similarity = self._calculate_similarity(
            article1.title.lower(), article2.title.lower()
        )

        if title_similarity >= self.similarity_threshold:
            return True

        # If titles are somewhat similar, check content
        if title_similarity >= 0.5:
            content1 = (article1.summary or article1.content)[:500]
            content2 = (article2.summary or article2.content)[:500]

            if content1 and content2:
                content_similarity = self._calculate_similarity(
                    content1.lower(), content2.lower()
                )
                if content_similarity >= self.similarity_threshold:
                    return True

        return False

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity ratio (0.0-1.0)

        """
        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(None, text1, text2).ratio()

    def merge_duplicates(
        self, articles: list[Article], preserve: str = "highest_score"
    ) -> list[Article]:
        """Merge duplicate articles and combine their information.

        Args:
            articles: List of articles
            preserve: Which article to preserve ('first', 'highest_score', 'latest')

        Returns:
            List of merged articles

        """
        if not articles:
            return []

        groups: list[list[Article]] = []

        for article in articles:
            # Find matching group
            matched_group = None
            for group in groups:
                if self._are_similar(article, group[0]):
                    matched_group = group
                    break

            if matched_group:
                matched_group.append(article)
            else:
                groups.append([article])

        # Select best article from each group
        merged_articles = []
        for group in groups:
            if len(group) == 1:
                merged_articles.append(group[0])
            else:
                best_article = self._select_best_article(group, preserve)
                merged_articles.append(best_article)

        return merged_articles

    def _select_best_article(
        self, articles: list[Article], criterion: str = "highest_score"
    ) -> Article:
        """Select the best article from a group of duplicates.

        Args:
            articles: List of duplicate articles
            criterion: Selection criterion

        Returns:
            Best article

        """
        if criterion == "first":
            return articles[0]
        elif criterion == "latest":
            return max(
                articles,
                key=lambda a: a.published_at or datetime.min,
            )
        else:  # highest_score
            return max(articles, key=lambda a: a.score)
