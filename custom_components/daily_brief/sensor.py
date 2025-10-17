"""Sensor entities for Daily Brief."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
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
    """Set up Daily Brief sensor entities."""
    coordinator: DailyBriefCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DailyBriefStatusSensor(coordinator),
        DailyBriefProgressSensor(coordinator),
    ]

    async_add_entities(entities)


class DailyBriefStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Daily Brief status."""

    def __init__(self, coordinator: DailyBriefCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Daily Brief Status"
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:newspaper-variant"

    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        return self.coordinator.status

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        briefing = self.coordinator.current_briefing

        attrs = {
            "status": self.coordinator.status,
            "progress": self.coordinator.progress,
        }

        if briefing:
            attrs.update({
                "last_generated": briefing.get("generated_at"),
                "article_count": len(briefing.get("article_ids", [])),
                "duration": briefing.get("duration"),
                "audio_url": briefing.get("audio_path"),
            })

        return attrs


class DailyBriefProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Daily Brief generation progress."""

    def __init__(self, coordinator: DailyBriefCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Daily Brief Progress"
        self._attr_unique_id = f"{DOMAIN}_progress"
        self._attr_icon = "mdi:progress-clock"
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return self.coordinator.progress

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "status": self.coordinator.status,
            "progress": self.coordinator.progress,
        }
