"""Media player entity for Daily Brief."""
from __future__ import annotations

import logging

from homeassistant.components.media_player import MediaPlayerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import DailyBriefCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Daily Brief media player entity."""
    coordinator: DailyBriefCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DailyBriefMediaPlayer(coordinator),
    ]

    async_add_entities(entities)


class DailyBriefMediaPlayer(MediaPlayerEntity):
    """Media player for Daily Brief playback control."""

    def __init__(self, coordinator: DailyBriefCoordinator) -> None:
        """Initialize the media player."""
        self.coordinator = coordinator
        self._attr_name = "Daily Brief"
        self._attr_unique_id = f"{DOMAIN}_media_player"
        self._attr_icon = "mdi:radio"

    # Minimal implementation for MVP
    # Full media player controls would be implemented in later versions
