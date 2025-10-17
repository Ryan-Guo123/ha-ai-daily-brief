"""LLM provider abstraction for Daily Brief."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    async def select_articles(
        self,
        articles: list[dict[str, Any]],
        user_interests: list[str],
        count: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Select top N articles from candidates.

        Args:
            articles: List of article dictionaries
            user_interests: List of user interest topics
            count: Number of articles to select
            **kwargs: Additional provider-specific parameters

        Returns:
            Dictionary with selected article IDs and reasoning

        """

    @abstractmethod
    async def generate_script(
        self,
        articles: list[dict[str, Any]],
        duration: int,
        **kwargs: Any,
    ) -> str:
        """Generate briefing script from articles.

        Args:
            articles: List of selected articles
            duration: Target duration in minutes
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated script text

        """

    @abstractmethod
    async def summarize_article(
        self,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> str:
        """Generate summary for an article.

        Args:
            title: Article title
            content: Article content
            **kwargs: Additional provider-specific parameters

        Returns:
            Summary text

        """

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test API connection and credentials.

        Returns:
            True if connection successful

        """

    @abstractmethod
    async def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for API call.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD

        """
