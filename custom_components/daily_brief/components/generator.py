"""Script generation component for Daily Brief."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from ..ai.llm import LLMProvider
from ..const import AUDIO_READING_SPEED, BRIEFING_CONFIGS
from ..storage.models import Article

_LOGGER = logging.getLogger(__name__)


class ScriptGenerator:
    """Generate audio briefing scripts from articles."""

    def __init__(self, llm_provider: LLMProvider) -> None:
        """Initialize generator.

        Args:
            llm_provider: LLM provider for script generation

        """
        self.llm_provider = llm_provider

    async def generate_briefing_script(
        self,
        articles: list[Article],
        briefing_length: str = "balanced",
        **kwargs: Any,
    ) -> str:
        """Generate complete briefing script.

        Args:
            articles: Selected articles
            briefing_length: Briefing length preference
            **kwargs: Additional parameters

        Returns:
            Generated script text

        """
        if not articles:
            return self._generate_empty_briefing()

        # Get duration from briefing length config
        config = BRIEFING_CONFIGS.get(briefing_length, BRIEFING_CONFIGS["balanced"])
        duration = config["duration"]

        _LOGGER.info(
            "Generating %d-minute script from %d articles", duration, len(articles)
        )

        # Prepare article data for LLM
        article_dicts = []
        for article in articles:
            article_dicts.append({
                "title": article.title,
                "summary": article.summary or article.content[:500],
                "source": "Unknown",  # TODO: Get source name from database
                "url": article.url,
                "topics": article.topics,
            })

        # Generate script using LLM
        try:
            script = await self.llm_provider.generate_script(
                article_dicts,
                duration,
                detail_level=kwargs.get("detail_level", "balanced"),
                tone=kwargs.get("tone", "professional"),
                language=kwargs.get("language", "en"),
                interests=kwargs.get("interests", []),
            )

            # Add opening and closing if not present
            script = self._ensure_structure(script, duration)

            # Validate script length
            word_count = len(script.split())
            expected_words = duration * AUDIO_READING_SPEED
            actual_duration = word_count / AUDIO_READING_SPEED

            _LOGGER.info(
                "Generated script: %d words (%.1f minutes at %d wpm)",
                word_count,
                actual_duration,
                AUDIO_READING_SPEED,
            )

            return script

        except Exception as err:
            _LOGGER.error("Error generating script: %s", err)
            # Fallback to template-based generation
            return self._generate_fallback_script(articles, duration)

    def _ensure_structure(self, script: str, duration: int) -> str:
        """Ensure script has proper structure.

        Args:
            script: Generated script
            duration: Target duration

        Returns:
            Script with ensured structure

        """
        # Check if script has opening
        if not any(
            greeting in script[:100].lower()
            for greeting in ["good morning", "hello", "welcome", "good day"]
        ):
            date_str = datetime.now().strftime("%A, %B %d, %Y")
            opening = f"Good morning! It's {date_str}. Here are today's top stories.\n\n<pause>\n\n"
            script = opening + script

        # Check if script has closing
        if not any(
            closing in script[-200:].lower()
            for closing in ["that's all", "that's it", "thank you", "have a great"]
        ):
            closing = "\n\n<pause>\n\nThat's all for today's briefing. Have a great day!"
            script = script + closing

        return script

    def _generate_fallback_script(
        self, articles: list[Article], duration: int
    ) -> str:
        """Generate fallback script without LLM.

        Args:
            articles: Articles to include
            duration: Target duration

        Returns:
            Template-based script

        """
        _LOGGER.info("Using fallback script generation")

        date_str = datetime.now().strftime("%A, %B %d, %Y")

        script_parts = [
            f"Good morning! It's {date_str}. Here are today's top {len(articles)} stories.",
            "",
            "<pause>",
            "",
        ]

        for idx, article in enumerate(articles, 1):
            script_parts.append(f"Story {idx}: {article.title}")
            script_parts.append("")

            summary = article.summary or article.content[:300]
            if summary:
                script_parts.append(summary)
                script_parts.append("")

            script_parts.append("<pause>")
            script_parts.append("")

        script_parts.append("That's all for today's briefing. Have a great day!")

        return "\n".join(script_parts)

    def _generate_empty_briefing(self) -> str:
        """Generate script for when no articles are available.

        Returns:
            Empty briefing script

        """
        date_str = datetime.now().strftime("%A, %B %d, %Y")

        return f"""Good morning! It's {date_str}.

<pause>

I don't have any new stories to share with you today. This might be because your news sources haven't been updated, or there are no articles matching your interests.

<pause>

Please check your Daily Brief configuration to ensure your content sources are set up correctly.

Have a great day!"""

    def estimate_duration(self, script: str) -> int:
        """Estimate duration of script in seconds.

        Args:
            script: Script text

        Returns:
            Duration in seconds

        """
        # Remove pause tags for word count
        text_without_pauses = script.replace("<pause>", "")

        word_count = len(text_without_pauses.split())

        # Add pause durations (assume 2 seconds per pause)
        pause_count = script.count("<pause>")
        pause_duration = pause_count * 2

        # Calculate reading time
        reading_time = (word_count / AUDIO_READING_SPEED) * 60

        total_duration = int(reading_time + pause_duration)

        return total_duration
