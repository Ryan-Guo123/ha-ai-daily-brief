"""Data coordinator for Daily Brief integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_BRIEFING_LENGTH,
    CONF_CONTENT_PACKS,
    CONF_CUSTOM_FEEDS,
    CONF_GENERATION_TIME,
    CONF_INTERESTS,
    CONF_LANGUAGE,
    CONF_LLM_API_KEY,
    CONF_LLM_MODEL,
    CONF_LLM_PROVIDER,
    CONF_TTS_API_KEY,
    CONF_TTS_PROVIDER,
    CONF_TTS_VOICE,
    DEFAULT_BRIEFING_LENGTH,
    DEFAULT_LANGUAGE,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_PROVIDER,
    DEFAULT_TTS_PROVIDER,
    DEFAULT_TTS_VOICE,
    DOMAIN,
    FEED_FETCH_INTERVAL,
    STATUS_IDLE,
)
from .components.orchestrator import BriefingOrchestrator
from .storage.database import Database

_LOGGER = logging.getLogger(__name__)


class DailyBriefCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Daily Brief data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=FEED_FETCH_INTERVAL),
        )
        self.entry = entry
        self.database: Database | None = None
        self.orchestrator: BriefingOrchestrator | None = None
        self._status = STATUS_IDLE
        self._current_briefing: dict[str, Any] | None = None
        self._progress = 0

    @property
    def config(self) -> dict[str, Any]:
        """Get configuration from config entry."""
        return self.entry.data

    @property
    def llm_provider(self) -> str:
        """Get LLM provider."""
        return self.config.get(CONF_LLM_PROVIDER, DEFAULT_LLM_PROVIDER)

    @property
    def llm_api_key(self) -> str | None:
        """Get LLM API key."""
        return self.config.get(CONF_LLM_API_KEY)

    @property
    def llm_model(self) -> str:
        """Get LLM model."""
        return self.config.get(CONF_LLM_MODEL, DEFAULT_LLM_MODEL)

    @property
    def tts_provider(self) -> str:
        """Get TTS provider."""
        return self.config.get(CONF_TTS_PROVIDER, DEFAULT_TTS_PROVIDER)

    @property
    def tts_api_key(self) -> str | None:
        """Get TTS API key."""
        return self.config.get(CONF_TTS_API_KEY)

    @property
    def tts_voice(self) -> str:
        """Get TTS voice."""
        return self.config.get(CONF_TTS_VOICE, DEFAULT_TTS_VOICE)

    @property
    def content_packs(self) -> list[str]:
        """Get enabled content packs."""
        return self.config.get(CONF_CONTENT_PACKS, [])

    @property
    def custom_feeds(self) -> list[dict[str, Any]]:
        """Get custom feeds."""
        return self.config.get(CONF_CUSTOM_FEEDS, [])

    @property
    def interests(self) -> list[str]:
        """Get user interests."""
        return self.config.get(CONF_INTERESTS, [])

    @property
    def briefing_length(self) -> str:
        """Get briefing length preference."""
        return self.config.get(CONF_BRIEFING_LENGTH, DEFAULT_BRIEFING_LENGTH)

    @property
    def language(self) -> str:
        """Get language preference."""
        return self.config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)

    @property
    def generation_time(self) -> str:
        """Get generation time."""
        return self.config.get(CONF_GENERATION_TIME, "06:30:00")

    @property
    def status(self) -> str:
        """Get current status."""
        return self._status

    @property
    def current_briefing(self) -> dict[str, Any] | None:
        """Get current briefing data."""
        return self._current_briefing

    @property
    def progress(self) -> int:
        """Get generation progress percentage."""
        return self._progress

    def set_status(self, status: str) -> None:
        """Set current status."""
        self._status = status
        self.async_set_updated_data(self.data)

    def set_progress(self, progress: int) -> None:
        """Set generation progress."""
        self._progress = min(100, max(0, progress))
        self.async_set_updated_data(self.data)

    def set_current_briefing(self, briefing: dict[str, Any] | None) -> None:
        """Set current briefing."""
        self._current_briefing = briefing
        self.async_set_updated_data(self.data)

    async def async_initialize(self) -> None:
        """Initialize the coordinator."""
        _LOGGER.debug("Initializing Daily Brief coordinator")

        # Initialize database
        self.database = Database(self.hass)
        await self.database.async_initialize()

        # Load or create user config
        await self._async_load_config()

        # Initialize orchestrator
        self.orchestrator = BriefingOrchestrator(
            self.hass,
            self.database,
            self.config,
        )

        # Set status callback
        self.orchestrator.set_status_callback(self._on_status_update)

        _LOGGER.info("Daily Brief coordinator initialized")

    def _on_status_update(self, status: str, progress: int) -> None:
        """Handle status updates from orchestrator."""
        self.set_status(status)
        self.set_progress(progress)

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        _LOGGER.debug("Shutting down Daily Brief coordinator")

        if self.database:
            await self.database.async_close()

        _LOGGER.info("Daily Brief coordinator shutdown complete")

    async def _async_load_config(self) -> None:
        """Load or create user configuration in database."""
        if not self.database:
            return

        # Check if config exists
        config_data = await self.database.get_config()

        if not config_data:
            # Create initial config from config entry
            await self.database.save_config({
                "user_id": self.entry.entry_id,
                "language": self.language,
                "briefing_length": self.briefing_length,
                "interests": self.interests,
                "excluded_topics": [],
            })
            _LOGGER.debug("Created initial database configuration")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint.

        This is called periodically to update cached data.
        For now, it returns current status.
        """
        try:
            return {
                "status": self._status,
                "progress": self._progress,
                "current_briefing": self._current_briefing,
                "last_update": datetime.now().isoformat(),
            }
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
