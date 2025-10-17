"""Article selection component with AI and scoring."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from ..ai.llm import LLMProvider
from ..const import (
    FRESHNESS_EXCELLENT,
    FRESHNESS_FAIR,
    FRESHNESS_GOOD,
    QUALITY_IDEAL_LENGTH,
    QUALITY_MAX_LENGTH,
    QUALITY_MIN_LENGTH,
    SCORE_FRESHNESS_WEIGHT,
    SCORE_IMPORTANCE_WEIGHT,
    SCORE_QUALITY_WEIGHT,
    SCORE_RELEVANCE_WEIGHT,
)
from ..storage.models import Article

_LOGGER = logging.getLogger(__name__)


class ArticleSelector:
    """Select and score articles for briefing."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        """Initialize selector.

        Args:
            llm_provider: LLM provider for AI selection

        """
        self.llm_provider = llm_provider

    async def select_articles(
        self,
        articles: list[Article],
        count: int,
        interests: list[str] | None = None,
        **kwargs: Any,
    ) -> list[Article]:
        """Select top articles for briefing.

        Args:
            articles: List of candidate articles
            count: Number of articles to select
            interests: User interests
            **kwargs: Additional parameters

        Returns:
            List of selected articles

        """
        _LOGGER.info("Selecting %d articles from %d candidates", count, len(articles))

        if not articles:
            return []

        # Step 1: Score all articles
        scored_articles = self._score_articles(articles, interests or [])

        # Step 2: Initial filter - keep top 50 or 5x target count
        initial_count = max(50, count * 5)
        top_candidates = sorted(scored_articles, key=lambda a: a.score, reverse=True)[
            :initial_count
        ]

        _LOGGER.debug("Filtered to top %d candidates", len(top_candidates))

        # Step 3: Use LLM to select final articles
        try:
            selected = await self._llm_select(
                top_candidates, count, interests or [], **kwargs
            )
        except Exception as err:
            _LOGGER.error("LLM selection failed: %s, using fallback", err)
            # Fallback to score-based selection
            selected = self._fallback_select(top_candidates, count)

        # Step 4: Ensure diversity
        final_selection = self._ensure_diversity(selected, count)

        _LOGGER.info("Final selection: %d articles", len(final_selection))
        return final_selection

    def _score_articles(
        self, articles: list[Article], interests: list[str]
    ) -> list[Article]:
        """Score all articles based on multiple factors.

        Args:
            articles: Articles to score
            interests: User interests

        Returns:
            Articles with updated scores

        """
        for article in articles:
            importance_score = self._calculate_importance(article)
            relevance_score = self._calculate_relevance(article, interests)
            freshness_score = self._calculate_freshness(article)
            quality_score = self._calculate_quality(article)

            # Weighted total score (0-100)
            article.score = (
                importance_score * SCORE_IMPORTANCE_WEIGHT / 100
                + relevance_score * SCORE_RELEVANCE_WEIGHT / 100
                + freshness_score * SCORE_FRESHNESS_WEIGHT / 100
                + quality_score * SCORE_QUALITY_WEIGHT / 100
            )

            _LOGGER.debug(
                "Scored article '%s': %.1f (I:%.1f R:%.1f F:%.1f Q:%.1f)",
                article.title[:50],
                article.score,
                importance_score,
                relevance_score,
                freshness_score,
                quality_score,
            )

        return articles

    def _calculate_importance(self, article: Article) -> float:
        """Calculate importance score (0-100).

        Args:
            article: Article to score

        Returns:
            Importance score

        """
        score = 0.0

        # Source authority (from article.score which contains source weight)
        # Source weight ranges from 0.5 to 2.0, normalize to 0-10
        source_score = min(10, max(0, (article.score - 0.5) * 10 / 1.5))
        score += source_score

        # Placeholder for other importance factors
        # In a full implementation, these could include:
        # - Breaking news detection (+20)
        # - Social engagement metrics (+10)
        # - Impact prediction via AI (+0 to +40)

        # For now, give a base importance based on presence of content
        if article.content:
            score += 10  # Has full content
        if article.topics:
            score += 5  # Has topic tags

        return min(100, score)

    def _calculate_relevance(self, article: Article, interests: list[str]) -> float:
        """Calculate relevance score based on user interests (0-100).

        Args:
            article: Article to score
            interests: User interests

        Returns:
            Relevance score

        """
        if not interests:
            return 50  # Neutral score if no interests

        score = 0.0

        # Check title and content for interest keywords
        text = (article.title + " " + article.summary).lower()
        interests_lower = [i.lower() for i in interests]

        matches = sum(1 for interest in interests_lower if interest in text)

        if matches > 0:
            score += min(30, matches * 15)  # +15 per match, max 30

        # Check topic alignment
        if article.topics:
            topics_lower = [t.lower() for t in article.topics]
            topic_matches = sum(
                1 for interest in interests_lower if any(interest in t for t in topics_lower)
            )
            if topic_matches > 0:
                score += min(20, topic_matches * 10)  # +10 per match, max 20

        # If no matches, give a small base score
        if score == 0:
            score = 20

        return min(100, score)

    def _calculate_freshness(self, article: Article) -> float:
        """Calculate freshness score based on publish date (0-100).

        Args:
            article: Article to score

        Returns:
            Freshness score

        """
        if not article.published_at:
            return 50  # Unknown date gets neutral score

        now = datetime.now()
        age_hours = (now - article.published_at).total_seconds() / 3600

        if age_hours < FRESHNESS_EXCELLENT:
            return 100  # <2 hours: +20 points
        elif age_hours < FRESHNESS_GOOD:
            return 75  # <12 hours: +15 points
        elif age_hours < FRESHNESS_FAIR:
            return 50  # <24 hours: +10 points
        else:
            # Decay after 24 hours
            days_old = age_hours / 24
            return max(0, 50 - (days_old * 10))

    def _calculate_quality(self, article: Article) -> float:
        """Calculate quality score based on content characteristics (0-100).

        Args:
            article: Article to score

        Returns:
            Quality score

        """
        score = 50.0  # Base score

        # Content length
        content_words = len((article.content or article.summary).split())

        if QUALITY_MIN_LENGTH <= content_words <= QUALITY_MAX_LENGTH:
            # Within ideal range
            if abs(content_words - QUALITY_IDEAL_LENGTH) < 200:
                score += 20  # Near ideal length
            else:
                score += 10  # Good length
        elif content_words < QUALITY_MIN_LENGTH:
            score -= 10  # Too short
        else:
            score -= 5  # Too long

        # Has summary
        if article.summary and len(article.summary) > 50:
            score += 10

        # Has author
        if article.author:
            score += 5

        # Readability (simple heuristic)
        if article.summary:
            avg_word_length = sum(len(w) for w in article.summary.split()) / max(
                1, len(article.summary.split())
            )
            if 4 <= avg_word_length <= 7:  # Readable range
                score += 10

        return min(100, max(0, score))

    async def _llm_select(
        self,
        articles: list[Article],
        count: int,
        interests: list[str],
        **kwargs: Any,
    ) -> list[Article]:
        """Use LLM to select articles.

        Args:
            articles: Candidate articles
            count: Number to select
            interests: User interests
            **kwargs: Additional parameters

        Returns:
            Selected articles

        """
        # Convert articles to dict format for LLM
        article_dicts = [article.to_dict() for article in articles]

        # Call LLM
        result = await self.llm_provider.select_articles(
            article_dicts, interests, count, **kwargs
        )

        # Extract selected article IDs
        selected_ids = [item["id"] for item in result.get("selected", [])]

        # Find corresponding Article objects
        article_map = {article.id: article for article in articles}
        selected = [article_map[aid] for aid in selected_ids if aid in article_map]

        return selected

    def _fallback_select(self, articles: list[Article], count: int) -> list[Article]:
        """Fallback selection based on scores only.

        Args:
            articles: Articles to select from
            count: Number to select

        Returns:
            Selected articles

        """
        return sorted(articles, key=lambda a: a.score, reverse=True)[:count]

    def _ensure_diversity(
        self, articles: list[Article], target_count: int
    ) -> list[Article]:
        """Ensure topic diversity in selection.

        Args:
            articles: Selected articles
            target_count: Target number of articles

        Returns:
            Diverse selection

        """
        if len(articles) <= target_count:
            return articles

        # Group by language
        by_language: dict[str, list[Article]] = {}
        for article in articles:
            lang = article.language
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(article)

        # Ensure at least one from each language represented
        diverse_selection: list[Article] = []
        seen_topics: set[str] = set()

        # First pass: one per language
        for articles_in_lang in by_language.values():
            if articles_in_lang:
                diverse_selection.append(articles_in_lang[0])

        # Second pass: fill remaining slots with highest scores
        # avoiding topic duplication
        remaining = [a for a in articles if a not in diverse_selection]

        for article in sorted(remaining, key=lambda a: a.score, reverse=True):
            if len(diverse_selection) >= target_count:
                break

            # Check topic diversity
            article_topics = set(article.topics)
            if not article_topics or not article_topics.intersection(seen_topics):
                diverse_selection.append(article)
                seen_topics.update(article_topics)

        # If still not enough, add remaining by score
        if len(diverse_selection) < target_count:
            remaining = [a for a in articles if a not in diverse_selection]
            diverse_selection.extend(
                sorted(remaining, key=lambda a: a.score, reverse=True)[
                    : target_count - len(diverse_selection)
                ]
            )

        return diverse_selection[:target_count]
