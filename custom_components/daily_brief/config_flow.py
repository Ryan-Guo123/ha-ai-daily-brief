"""Config flow for Daily Brief integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_BRIEFING_LENGTH,
    CONF_CONTENT_PACKS,
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
)
from .feeds import list_content_packs

_LOGGER = logging.getLogger(__name__)


class DailyBriefConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Daily Brief."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize config flow."""
        self.data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - LLM configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_tts()

        # Show LLM configuration form
        data_schema = vol.Schema({
            vol.Required(
                CONF_LLM_PROVIDER, default=DEFAULT_LLM_PROVIDER
            ): vol.In(["openai", "anthropic", "google", "ollama"]),
            vol.Required(CONF_LLM_API_KEY): cv.string,
            vol.Optional(
                CONF_LLM_MODEL, default=DEFAULT_LLM_MODEL
            ): cv.string,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "docs_url": "https://github.com/Ryan-Guo123/ha-ai-daily-brief"
            },
        )

    async def async_step_tts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle TTS configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_content()

        # Show TTS configuration form
        data_schema = vol.Schema({
            vol.Required(
                CONF_TTS_PROVIDER, default=DEFAULT_TTS_PROVIDER
            ): vol.In(["openai", "elevenlabs", "piper"]),
            vol.Optional(CONF_TTS_API_KEY): cv.string,
            vol.Optional(
                CONF_TTS_VOICE, default=DEFAULT_TTS_VOICE
            ): cv.string,
        })

        return self.async_show_form(
            step_id="tts",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_content(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle content selection step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_preferences()

        # Get available content packs
        content_packs = list_content_packs()
        pack_options = {pack["id"]: pack["name"] for pack in content_packs}

        # Show content selection form
        data_schema = vol.Schema({
            vol.Required(CONF_CONTENT_PACKS, default=["tech_en"]): cv.multi_select(
                pack_options
            ),
        })

        return self.async_show_form(
            step_id="content",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_preferences(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user preferences step."""
        if user_input is not None:
            self.data.update(user_input)

            # Create entry
            return self.async_create_entry(
                title="Daily Brief",
                data=self.data,
            )

        # Show preferences form
        data_schema = vol.Schema({
            vol.Optional(CONF_INTERESTS, default=""): cv.string,
            vol.Optional(
                CONF_BRIEFING_LENGTH, default=DEFAULT_BRIEFING_LENGTH
            ): vol.In(["quick", "balanced", "deep"]),
            vol.Optional(
                CONF_LANGUAGE, default=DEFAULT_LANGUAGE
            ): vol.In(["en", "zh-Hans"]),
        })

        return self.async_show_form(
            step_id="preferences",
            data_schema=data_schema,
        )
