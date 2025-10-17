"""简报生成编排器 - 协调整个生成流程."""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from ..ai.providers.openai import OpenAILLMProvider, OpenAITTSProvider
from ..const import (
    BRIEFING_CONFIGS,
    DEFAULT_ARTICLE_COUNT,
    STATUS_ERROR,
    STATUS_FETCHING,
    STATUS_GENERATING,
    STATUS_READY,
    STATUS_SELECTING,
    STORAGE_DIR,
)
from ..storage import Briefing, Database
from .aggregator import ContentAggregator
from .audio import AudioProcessor
from .generator import ScriptGenerator
from .player import PlaybackController
from .selector import ArticleSelector

_LOGGER = logging.getLogger(__name__)


class BriefingOrchestrator:
    """简报生成编排器 - 协调所有组件."""

    def __init__(
        self,
        hass: HomeAssistant,
        database: Database,
        config: dict[str, Any],
    ) -> None:
        """初始化编排器.

        Args:
            hass: Home Assistant实例
            database: 数据库实例
            config: 配置字典

        """
        self.hass = hass
        self.database = database
        self.config = config

        # 初始化AI提供商
        self.llm_provider = self._create_llm_provider()
        self.tts_provider = self._create_tts_provider()

        # 初始化组件
        self.aggregator = ContentAggregator(database)
        self.selector = ArticleSelector(self.llm_provider)
        self.generator = ScriptGenerator(self.llm_provider)

        storage_path = Path(hass.config.path(STORAGE_DIR))
        self.audio_processor = AudioProcessor(self.tts_provider, storage_path)
        self.player = PlaybackController(hass, database)

        # 生成状态
        self._is_generating = False
        self._current_progress = 0
        self._status_callback = None

    def _create_llm_provider(self) -> OpenAILLMProvider:
        """创建LLM提供商.

        Returns:
            LLM提供商实例

        """
        provider = self.config.get("llm_provider", "openai")
        api_key = self.config.get("llm_api_key")
        model = self.config.get("llm_model", "gpt-4o-mini")

        if provider == "openai":
            return OpenAILLMProvider(api_key=api_key, model=model)
        else:
            # 其他提供商的实现
            raise ValueError(f"不支持的LLM提供商: {provider}")

    def _create_tts_provider(self) -> OpenAITTSProvider:
        """创建TTS提供商.

        Returns:
            TTS提供商实例

        """
        provider = self.config.get("tts_provider", "openai")
        api_key = self.config.get("tts_api_key") or self.config.get("llm_api_key")
        voice = self.config.get("tts_voice", "alloy")

        if provider == "openai":
            return OpenAITTSProvider(api_key=api_key, voice=voice)
        else:
            # 其他提供商的实现
            raise ValueError(f"不支持的TTS提供商: {provider}")

    def set_status_callback(self, callback) -> None:
        """设置状态回调函数.

        Args:
            callback: 回调函数，接收(status, progress)参数

        """
        self._status_callback = callback

    def _update_status(self, status: str, progress: int) -> None:
        """更新状态.

        Args:
            status: 状态字符串
            progress: 进度百分比

        """
        self._current_progress = progress

        if self._status_callback:
            self._status_callback(status, progress)

        _LOGGER.debug("状态更新: %s (%d%%)", status, progress)

    async def generate_briefing(
        self,
        briefing_type: str = "morning",
        force_refresh: bool = False,
        **kwargs: Any,
    ) -> Briefing | None:
        """生成完整的简报.

        Args:
            briefing_type: 简报类型
            force_refresh: 是否强制刷新内容
            **kwargs: 额外参数

        Returns:
            生成的简报对象或None

        """
        if self._is_generating:
            _LOGGER.warning("已经有简报正在生成中")
            return None

        self._is_generating = True

        try:
            _LOGGER.info("开始生成简报: 类型=%s", briefing_type)
            self._update_status(STATUS_FETCHING, 0)

            # 步骤1: 获取内容 (0-20%)
            articles = await self._fetch_content(force_refresh)
            if not articles:
                _LOGGER.error("未获取到任何文章")
                self._update_status(STATUS_ERROR, 0)
                return None

            self._update_status(STATUS_SELECTING, 20)

            # 步骤2: 选择文章 (20-40%)
            selected_articles = await self._select_articles(articles, **kwargs)
            if not selected_articles:
                _LOGGER.error("未选择到任何文章")
                self._update_status(STATUS_ERROR, 0)
                return None

            self._update_status(STATUS_GENERATING, 40)

            # 步骤3: 生成脚本 (40-60%)
            script = await self._generate_script(selected_articles, **kwargs)
            if not script:
                _LOGGER.error("脚本生成失败")
                self._update_status(STATUS_ERROR, 0)
                return None

            self._update_status(STATUS_GENERATING, 60)

            # 步骤4: 生成音频 (60-90%)
            audio_path, duration = await self._generate_audio(script, **kwargs)
            if not audio_path:
                _LOGGER.error("音频生成失败")
                self._update_status(STATUS_ERROR, 0)
                return None

            self._update_status(STATUS_GENERATING, 90)

            # 步骤5: 保存简报 (90-100%)
            briefing = await self._save_briefing(
                briefing_type=briefing_type,
                articles=selected_articles,
                script=script,
                audio_path=audio_path,
                duration=duration,
            )

            self._update_status(STATUS_READY, 100)

            _LOGGER.info("简报生成完成: %s 篇文章, 时长 %d 秒", len(selected_articles), duration)

            return briefing

        except Exception as err:
            _LOGGER.error("生成简报时出错: %s", err, exc_info=True)
            self._update_status(STATUS_ERROR, 0)
            return None

        finally:
            self._is_generating = False

    async def _fetch_content(self, force_refresh: bool = False) -> list:
        """获取内容.

        Args:
            force_refresh: 是否强制刷新

        Returns:
            文章列表

        """
        _LOGGER.info("开始获取内容...")

        # 获取配置的内容包和自定义源
        content_packs = self.config.get("content_packs", [])
        custom_feeds = self.config.get("custom_feeds", [])

        articles = await self.aggregator.fetch_all_sources(
            content_packs=content_packs,
            custom_feeds=custom_feeds,
        )

        _LOGGER.info("获取到 %d 篇文章", len(articles))

        return articles

    async def _select_articles(self, articles: list, **kwargs: Any) -> list:
        """选择文章.

        Args:
            articles: 候选文章列表
            **kwargs: 额外参数

        Returns:
            选择的文章列表

        """
        # 获取用户兴趣
        interests = self.config.get("interests", [])
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(",") if i.strip()]

        # 确定文章数量
        briefing_length = self.config.get("briefing_length", "balanced")
        config = BRIEFING_CONFIGS.get(briefing_length, BRIEFING_CONFIGS["balanced"])
        article_count = kwargs.get("article_count", config["count"])

        _LOGGER.info("选择 %d 篇文章，基于兴趣: %s", article_count, interests)

        selected = await self.selector.select_articles(
            articles=articles,
            count=article_count,
            interests=interests,
            **kwargs,
        )

        _LOGGER.info("选择了 %d 篇文章", len(selected))

        return selected

    async def _generate_script(self, articles: list, **kwargs: Any) -> str:
        """生成脚本.

        Args:
            articles: 文章列表
            **kwargs: 额外参数

        Returns:
            脚本文本

        """
        briefing_length = self.config.get("briefing_length", "balanced")
        language = self.config.get("language", "en")
        interests = self.config.get("interests", [])

        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(",") if i.strip()]

        _LOGGER.info("生成脚本，长度: %s, 语言: %s", briefing_length, language)

        script = await self.generator.generate_briefing_script(
            articles=articles,
            briefing_length=briefing_length,
            language=language,
            interests=interests,
            **kwargs,
        )

        # 估算时长
        estimated_duration = self.generator.estimate_duration(script)
        _LOGGER.info("脚本生成完成，预估时长: %d 秒", estimated_duration)

        return script

    async def _generate_audio(self, script: str, **kwargs: Any) -> tuple[str, int]:
        """生成音频.

        Args:
            script: 脚本文本
            **kwargs: 额外参数

        Returns:
            (音频文件路径, 时长秒数)

        """
        date = datetime.now().strftime("%Y-%m-%d")
        briefing_type = kwargs.get("briefing_type", "morning")
        voice = self.config.get("tts_voice", "alloy")

        _LOGGER.info("生成音频，日期: %s, 语音: %s", date, voice)

        audio_path, duration = await self.audio_processor.generate_briefing_audio(
            script=script,
            date=date,
            briefing_type=briefing_type,
            voice=voice,
            **kwargs,
        )

        return audio_path, duration

    async def _save_briefing(
        self,
        briefing_type: str,
        articles: list,
        script: str,
        audio_path: str,
        duration: int,
    ) -> Briefing:
        """保存简报到数据库.

        Args:
            briefing_type: 简报类型
            articles: 文章列表
            script: 脚本
            audio_path: 音频路径
            duration: 时长

        Returns:
            简报对象

        """
        date = datetime.now().strftime("%Y-%m-%d")

        briefing = Briefing(
            date=date,
            type=briefing_type,
            article_ids=[article.id for article in articles],
            script=script,
            audio_path=audio_path,
            duration=duration,
            status="ready",
            generated_at=datetime.now(),
        )

        briefing_id = await self.database.save_briefing(briefing)
        briefing.id = briefing_id

        _LOGGER.info("简报已保存到数据库，ID: %d", briefing_id)

        return briefing

    async def play_briefing(
        self, media_player: str, briefing_date: str | None = None
    ) -> bool:
        """播放简报.

        Args:
            media_player: 媒体播放器实体ID
            briefing_date: 简报日期（可选）

        Returns:
            是否成功开始播放

        """
        return await self.player.play_briefing(media_player, briefing_date)

    async def stop_playback(self, media_player: str | None = None) -> bool:
        """停止播放.

        Args:
            media_player: 媒体播放器实体ID（可选）

        Returns:
            是否成功停止

        """
        return await self.player.stop_playback(media_player)

    def is_generating(self) -> bool:
        """检查是否正在生成.

        Returns:
            是否正在生成

        """
        return self._is_generating

    def get_progress(self) -> int:
        """获取当前进度.

        Returns:
            进度百分比

        """
        return self._current_progress
