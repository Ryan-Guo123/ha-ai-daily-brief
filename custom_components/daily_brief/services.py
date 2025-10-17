"""服务处理程序 for Daily Brief - 已更新版本."""
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
from .storage import ContentSource

_LOGGER = logging.getLogger(__name__)

# 服务schema定义
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
    """设置Daily Brief服务."""

    async def handle_generate(call: ServiceCall) -> None:
        """处理生成服务调用."""
        _LOGGER.info("生成服务被调用: %s", call.data)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            _LOGGER.error("未配置Daily Brief集成")
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.orchestrator:
            _LOGGER.error("编排器未初始化")
            return

        # 提取参数
        briefing_type = call.data.get(ATTR_BRIEFING_TYPE, BRIEFING_TYPE_MORNING)
        force_refresh = call.data.get(ATTR_FORCE_REFRESH, False)
        article_count = call.data.get(ATTR_ARTICLE_COUNT)

        try:
            _LOGGER.info("开始生成简报...")

            # 生成简报
            briefing = await coordinator.orchestrator.generate_briefing(
                briefing_type=briefing_type,
                force_refresh=force_refresh,
                article_count=article_count,
            )

            if briefing:
                _LOGGER.info("简报生成成功: %d秒, 音频: %s", briefing.duration, briefing.audio_path)
                coordinator.set_current_briefing(briefing.to_dict())
            else:
                _LOGGER.error("简报生成失败")

        except Exception as err:
            _LOGGER.error("生成简报时出错: %s", err, exc_info=True)

    async def handle_play(call: ServiceCall) -> None:
        """处理播放服务调用."""
        _LOGGER.info("播放服务被调用: %s", call.data)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.orchestrator:
            _LOGGER.error("编排器未初始化")
            return

        media_player = call.data[ATTR_MEDIA_PLAYER]
        briefing_date = call.data.get(ATTR_BRIEFING_DATE)

        try:
            success = await coordinator.orchestrator.play_briefing(
                media_player=media_player,
                briefing_date=briefing_date,
            )

            if success:
                _LOGGER.info("开始在 %s 上播放简报", media_player)
            else:
                _LOGGER.error("播放简报失败")

        except Exception as err:
            _LOGGER.error("播放简报时出错: %s", err, exc_info=True)

    async def handle_stop(call: ServiceCall) -> None:
        """处理停止服务调用."""
        _LOGGER.info("停止服务被调用")

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.orchestrator:
            return

        try:
            await coordinator.orchestrator.stop_playback()
            _LOGGER.info("播放已停止")
        except Exception as err:
            _LOGGER.error("停止播放时出错: %s", err)

    async def handle_skip_story(call: ServiceCall) -> None:
        """处理跳过故事服务调用."""
        _LOGGER.info("跳过故事服务被调用")

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.orchestrator:
            return

        try:
            player = coordinator.orchestrator.player
            await player.skip_story()
            _LOGGER.info("已跳过当前故事")
        except Exception as err:
            _LOGGER.error("跳过故事时出错: %s", err)

    async def handle_feedback(call: ServiceCall) -> None:
        """处理反馈服务调用."""
        article_id = call.data[ATTR_ARTICLE_ID]
        feedback_type = call.data[ATTR_FEEDBACK_TYPE]

        _LOGGER.info("收到反馈: %s for article %s", feedback_type, article_id)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.database:
            return

        try:
            from .storage import Feedback

            feedback = Feedback(
                article_id=article_id,
                feedback_type=feedback_type,
            )

            await coordinator.database.save_feedback(feedback)
            _LOGGER.info("反馈已保存")

        except Exception as err:
            _LOGGER.error("保存反馈时出错: %s", err)

    async def handle_add_source(call: ServiceCall) -> None:
        """处理添加源服务调用."""
        name = call.data[ATTR_SOURCE_NAME]
        url = call.data[ATTR_SOURCE_URL]
        category = call.data.get(ATTR_SOURCE_CATEGORY, "general")

        _LOGGER.info("添加新源: %s (%s)", name, url)

        coordinators = hass.data.get(DOMAIN, {})
        if not coordinators:
            return

        coordinator = next(iter(coordinators.values()))

        if not coordinator.database:
            return

        try:
            source = ContentSource(
                name=name,
                url=url,
                category=category,
                type="rss",
                enabled=True,
            )

            source_id = await coordinator.database.add_source(source)
            _LOGGER.info("源已添加，ID: %d", source_id)

        except Exception as err:
            _LOGGER.error("添加源时出错: %s", err)

    async def handle_regenerate(call: ServiceCall) -> None:
        """处理重新生成服务调用."""
        keep_articles = call.data[ATTR_KEEP_ARTICLES]

        _LOGGER.info("重新生成服务被调用 (保留文章=%s)", keep_articles)

        # 如果保留文章，可以从数据库加载上次的文章列表
        # 否则重新抓取
        # 这里简化实现，直接调用generate
        await handle_generate(ServiceCall(DOMAIN, SERVICE_GENERATE, {}))

    # 注册服务
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

    _LOGGER.info("Daily Brief服务已注册")
