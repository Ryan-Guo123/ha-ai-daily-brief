"""Binary sensor entities for Daily Brief."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_READY
from .coordinator import DailyBriefCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Daily Brief binary sensor entities."""
    coordinator: DailyBriefCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        DailyBriefReadySensor(coordinator),
    ]

    async_add_entities(entities)


class DailyBriefReadySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor indicating if briefing is ready."""

    def __init__(self, coordinator: DailyBriefCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Daily Brief Ready"
        self._attr_unique_id = f"{DOMAIN}_ready"
        self._attr_icon = "mdi:check-circle"

    @property
    def is_on(self) -> bool:
        """Return true if briefing is ready."""
        return self.coordinator.status == STATUS_READY
