"""Service handlers for Daily Brief."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    ATTR_ARTICLE_COUNT,
    ATTR_ARTICLE_ID,
    ATTR_BRIEFING_DATE,
    ATTR_BRIEFING_TYPE,
    ATTR_FEEDBACK_TYPE,
    ATTR_FORCE_REFRESH,
    ATTR_KEEP_ARTICLES,
    ATTR_MEDIA_PLAYER,
    ATTR_SOURCE_CATEGORY,
    ATTR_SOURCE_NAME,
    ATTR_SOURCE_URL,
    ATTR_TARGET_DURATION,
    BRIEFING_TYPE_MORNING,
    BRIEFING_TYPE_ON_DEMAND,
    DOMAIN,
    FEEDBACK_DISLIKE,
    FEEDBACK_LIKE,
    FEEDBACK_SKIP,
    SERVICE_ADD_SOURCE,
    SERVICE_FEEDBACK,
    SERVICE_GENERATE,
    SERVICE_PLAY,
    SERVICE_REGENERATE,
    SERVICE_SKIP_STORY,
    SERVICE_STOP,
)

_LOGGER = logging.getLogger(__name__)

# Service schemas
SERVICE_GENERATE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_BRIEFING_TYPE, default=BRIEFING_TYPE_MORNING): cv.string,
    vol.Optional(ATTR_FORCE_REFRESH, default=False): cv.boolean,
    vol.Optional(ATTR_ARTICLE_COUNT): cv.positive_int,
    vol.Optional(ATTR_TARGET_DURATION): cv.positive_int,
})

SERVICE_PLAY_SCHEMA = vol.Schema({
    vol.Required(ATTR_MEDIA_PLAYER): cv.entity_id,
    vol.Optional(ATTR_BRIEFING_DATE): cv.string,
})

SERVICE_FEEDBACK_SCHEMA = vol.Schema({
    vol.Required(ATTR_ARTICLE_ID): cv.string,
    vol.Required(ATTR_FEEDBACK_TYPE): vol.In([FEEDBACK_LIKE, FEEDBACK_DISLIKE, FEEDBACK_SKIP]),
})

SERVICE_ADD_SOURCE_SCHEMA = vol.Schema({
    vol.Required(ATTR_SOURCE_NAME): cv.string,
    vol.Required(ATTR_SOURCE_URL): cv.url,
    vol.Optional(ATTR_SOURCE_CATEGORY): cv.string,
})

SERVICE_REGENERATE_SCHEMA = vol.Schema({
    vol.Optional(ATTR_KEEP_ARTICLES, default=False): cv.boolean,
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up Daily Brief services."""

    async def handle_generate(call: ServiceCall) -> None:
        """Handle generate service call."""
        _LOGGER.info("Generate service called: %s", call.data)

        # Get coordinator from first configured entry
        # In a real implementation, you'd select the right one
        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            _LOGGER.error("No Daily Brief integration configured")
            return

        coordinator = next(iter(coordinators.values()))

        # TODO: Implement actual generation logic
        _LOGGER.info("Briefing generation not yet implemented")

    async def handle_play(call: ServiceCall) -> None:
        """Handle play service call."""
        _LOGGER.info("Play service called: %s", call.data)

        media_player = call.data[ATTR_MEDIA_PLAYER]
        briefing_date = call.data.get(ATTR_BRIEFING_DATE)

        # TODO: Implement playback logic
        _LOGGER.info(
            "Playing briefing on %s (date: %s) not yet implemented",
            media_player,
            briefing_date,
        )

    async def handle_stop(call: ServiceCall) -> None:
        """Handle stop service call."""
        _LOGGER.info("Stop service called")
        # TODO: Implement stop logic

    async def handle_skip_story(call: ServiceCall) -> None:
        """Handle skip story service call."""
        _LOGGER.info("Skip story service called")
        # TODO: Implement skip logic

    async def handle_feedback(call: ServiceCall) -> None:
        """Handle feedback service call."""
        article_id = call.data[ATTR_ARTICLE_ID]
        feedback_type = call.data[ATTR_FEEDBACK_TYPE]

        _LOGGER.info("Feedback: %s for article %s", feedback_type, article_id)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        # TODO: Save feedback to database
        _LOGGER.info("Feedback storage not yet implemented")

    async def handle_add_source(call: ServiceCall) -> None:
        """Handle add source service call."""
        name = call.data[ATTR_SOURCE_NAME]
        url = call.data[ATTR_SOURCE_URL]
        category = call.data.get(ATTR_SOURCE_CATEGORY, "general")

        _LOGGER.info("Adding source: %s (%s)", name, url)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        # TODO: Add source to database
        _LOGGER.info("Source addition not yet implemented")

    async def handle_regenerate(call: ServiceCall) -> None:
        """Handle regenerate service call."""
        keep_articles = call.data[ATTR_KEEP_ARTICLES]

        _LOGGER.info("Regenerate service called (keep_articles=%s)", keep_articles)

        # TODO: Implement regeneration logic
        _LOGGER.info("Regeneration not yet implemented")

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_GENERATE, handle_generate, schema=SERVICE_GENERATE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_PLAY, handle_play, schema=SERVICE_PLAY_SCHEMA
    )

    hass.services.async_register(DOMAIN, SERVICE_STOP, handle_stop)

    hass.services.async_register(DOMAIN, SERVICE_SKIP_STORY, handle_skip_story)

    hass.services.async_register(
        DOMAIN, SERVICE_FEEDBACK, handle_feedback, schema=SERVICE_FEEDBACK_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_SOURCE, handle_add_source, schema=SERVICE_ADD_SOURCE_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_REGENERATE, handle_regenerate, schema=SERVICE_REGENERATE_SCHEMA
    )

    _LOGGER.info("Daily Brief services registered")
