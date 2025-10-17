"""OpenAI provider for LLM and TTS."""
from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI, OpenAIError

from ..llm import LLMProvider
from ..prompts import (
    SCRIPT_SYSTEM_PROMPT,
    SELECTION_SYSTEM_PROMPT,
    get_script_prompt,
    get_selection_prompt,
    get_summary_prompt,
)
from ..tts import TTSProvider

_LOGGER = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider implementation."""

    # Pricing per 1M tokens (as of 2024)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    }

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name to use

        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self._validate_model()

    def _validate_model(self) -> None:
        """Validate model name."""
        if self.model not in self.PRICING:
            _LOGGER.warning(
                "Model %s not in known pricing list, cost estimates may be inaccurate",
                self.model,
            )

    async def select_articles(
        self,
        articles: list[dict[str, Any]],
        user_interests: list[str],
        count: int,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Select top N articles using GPT.

        Args:
            articles: List of article dictionaries
            user_interests: User interests
            count: Number to select
            **kwargs: Additional parameters

        Returns:
            Selection results with article IDs and reasoning

        """
        try:
            # Get liked/disliked topics from kwargs
            liked_topics = kwargs.get("liked_topics", [])
            disliked_topics = kwargs.get("disliked_topics", [])

            # Generate prompt
            user_prompt = get_selection_prompt(
                articles, user_interests, count, liked_topics, disliked_topics
            )

            # Call API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SELECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            # Parse response
            result = json.loads(response.choices[0].message.content)

            _LOGGER.info(
                "Selected %d articles (used %d tokens)",
                len(result.get("selected", [])),
                response.usage.total_tokens if response.usage else 0,
            )

            return result

        except OpenAIError as err:
            _LOGGER.error("OpenAI API error in select_articles: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error in select_articles: %s", err)
            raise

    async def generate_script(
        self,
        articles: list[dict[str, Any]],
        duration: int,
        **kwargs: Any,
    ) -> str:
        """Generate briefing script.

        Args:
            articles: Selected articles
            duration: Target duration in minutes
            **kwargs: Additional parameters

        Returns:
            Generated script

        """
        try:
            # Extract parameters
            detail_level = kwargs.get("detail_level", "balanced")
            tone = kwargs.get("tone", "professional")
            language = kwargs.get("language", "en")
            interests = kwargs.get("interests", [])

            # Generate prompt
            user_prompt = get_script_prompt(
                articles, duration, detail_level, tone, language, interests
            )

            system_prompt = SCRIPT_SYSTEM_PROMPT.format(duration=duration)

            # Call API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
            )

            script = response.choices[0].message.content

            _LOGGER.info(
                "Generated script of ~%d words (used %d tokens)",
                len(script.split()),
                response.usage.total_tokens if response.usage else 0,
            )

            return script

        except OpenAIError as err:
            _LOGGER.error("OpenAI API error in generate_script: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error in generate_script: %s", err)
            raise

    async def summarize_article(
        self,
        title: str,
        content: str,
        **kwargs: Any,
    ) -> str:
        """Summarize an article.

        Args:
            title: Article title
            content: Article content
            **kwargs: Additional parameters

        Returns:
            Summary text

        """
        try:
            prompt = get_summary_prompt(title, content)

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150,
            )

            return response.choices[0].message.content

        except OpenAIError as err:
            _LOGGER.error("OpenAI API error in summarize_article: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error in summarize_article: %s", err)
            raise

    async def test_connection(self) -> bool:
        """Test OpenAI API connection.

        Returns:
            True if successful

        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
            )
            return bool(response.choices)
        except Exception as err:
            _LOGGER.error("OpenAI connection test failed: %s", err)
            return False

    async def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost for API call.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD

        """
        pricing = self.PRICING.get(self.model, {"input": 1.0, "output": 2.0})

        input_cost = (prompt_tokens / 1_000_000) * pricing["input"]
        output_cost = (completion_tokens / 1_000_000) * pricing["output"]

        return input_cost + output_cost


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS provider implementation."""

    # Pricing per 1M characters
    PRICING = {
        "tts-1": 15.00,  # $15 per 1M chars
        "tts-1-hd": 30.00,  # $30 per 1M chars
    }

    VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def __init__(
        self,
        api_key: str,
        model: str = "tts-1",
        voice: str = "alloy",
        speed: float = 1.0,
    ) -> None:
        """Initialize OpenAI TTS provider.

        Args:
            api_key: OpenAI API key
            model: Model name (tts-1 or tts-1-hd)
            voice: Voice name
            speed: Speech speed (0.25-4.0)

        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_voice = voice
        self.speed = max(0.25, min(4.0, speed))

    async def generate_audio(
        self,
        text: str,
        voice: str | None = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate audio from text.

        Args:
            text: Text to convert
            voice: Voice to use (uses default if not specified)
            **kwargs: Additional parameters

        Returns:
            Audio data as bytes (MP3)

        """
        try:
            voice = voice or self.default_voice
            speed = kwargs.get("speed", self.speed)

            _LOGGER.debug(
                "Generating audio: %d chars, voice=%s, speed=%.2f",
                len(text),
                voice,
                speed,
            )

            response = await self.client.audio.speech.create(
                model=self.model,
                voice=voice,
                input=text,
                speed=speed,
            )

            # Get audio bytes
            audio_bytes = b""
            async for chunk in response.iter_bytes():
                audio_bytes += chunk

            _LOGGER.info("Generated audio: %d bytes", len(audio_bytes))
            return audio_bytes

        except OpenAIError as err:
            _LOGGER.error("OpenAI API error in generate_audio: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error in generate_audio: %s", err)
            raise

    async def list_voices(self, language: str | None = None) -> list[dict[str, Any]]:
        """Get available voices.

        Args:
            language: Language filter (not used for OpenAI)

        Returns:
            List of voice dictionaries

        """
        return [
            {
                "id": voice,
                "name": voice.capitalize(),
                "language": "multi",
                "description": f"OpenAI {voice} voice",
            }
            for voice in self.VOICES
        ]

    async def estimate_cost(self, text: str) -> float:
        """Estimate TTS cost.

        Args:
            text: Text to convert

        Returns:
            Estimated cost in USD

        """
        chars = len(text)
        price_per_million = self.PRICING.get(self.model, 15.00)
        return (chars / 1_000_000) * price_per_million

    async def test_connection(self) -> bool:
        """Test OpenAI TTS connection.

        Returns:
            True if successful

        """
        try:
            await self.generate_audio("Test", self.default_voice)
            return True
        except Exception as err:
            _LOGGER.error("OpenAI TTS connection test failed: %s", err)
            return False
