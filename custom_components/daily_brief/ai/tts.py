"""TTS provider abstraction for Daily Brief."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TTSProvider(ABC):
    """Base class for TTS providers."""

    @abstractmethod
    async def generate_audio(
        self,
        text: str,
        voice: str,
        **kwargs: Any,
    ) -> bytes:
        """Convert text to audio.

        Args:
            text: Text to convert
            voice: Voice identifier
            **kwargs: Additional provider-specific parameters

        Returns:
            Audio data as bytes

        """

    @abstractmethod
    async def list_voices(self, language: str | None = None) -> list[dict[str, Any]]:
        """Get available voices.

        Args:
            language: Optional language filter

        Returns:
            List of voice dictionaries with id, name, language, etc.

        """

    @abstractmethod
    async def estimate_cost(self, text: str) -> float:
        """Estimate cost for text-to-speech conversion.

        Args:
            text: Text to convert

        Returns:
            Estimated cost in USD

        """

    @abstractmethod
    async def test_connection(self) -> bool:
        """Test API connection and credentials.

        Returns:
            True if connection successful

        """
