"""Button entities for Daily Brief."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import DailyBriefCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Daily Brief button entities."""
    coordinator: DailyBriefCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DailyBriefGenerateButton(coordinator),
    ]

    async_add_entities(entities)


class DailyBriefGenerateButton(CoordinatorEntity, ButtonEntity):
    """Button to generate daily briefing."""

    def __init__(self, coordinator: DailyBriefCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self._attr_name = "Generate Daily Brief"
        self._attr_unique_id = f"{DOMAIN}_generate"
        self._attr_icon = "mdi:play-circle"

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.info("Generate button pressed")
        # TODO: Trigger briefing generation
