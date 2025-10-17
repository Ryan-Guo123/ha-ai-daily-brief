"""播放控制组件."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    ATTR_MEDIA_CONTENT_ID,
    ATTR_MEDIA_CONTENT_TYPE,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_PLAY_MEDIA,
)
from homeassistant.core import HomeAssistant

from ..storage import Briefing, Database, Feedback
from ..const import FEEDBACK_COMPLETE, FEEDBACK_SKIP

_LOGGER = logging.getLogger(__name__)


class PlaybackController:
    """简报播放控制器."""

    def __init__(self, hass: HomeAssistant, database: Database) -> None:
        """初始化播放控制器.

        Args:
            hass: Home Assistant实例
            database: 数据库实例

        """
        self.hass = hass
        self.database = database
        self._current_briefing: Briefing | None = None
        self._current_media_player: str | None = None
        self._playback_position: int = 0  # 秒

    async def play_briefing(
        self,
        media_player_entity_id: str,
        briefing_date: str | None = None,
    ) -> bool:
        """播放简报.

        Args:
            media_player_entity_id: 媒体播放器实体ID
            briefing_date: 简报日期 (可选，默认今天)

        Returns:
            是否成功开始播放

        """
        try:
            # 获取简报
            from datetime import datetime

            if not briefing_date:
                briefing_date = datetime.now().strftime("%Y-%m-%d")

            briefing = await self.database.get_briefing(briefing_date)

            if not briefing:
                _LOGGER.error("未找到日期为 %s 的简报", briefing_date)
                return False

            if not briefing.audio_path:
                _LOGGER.error("简报没有音频文件")
                return False

            # 检查音频文件是否存在
            from pathlib import Path

            if not Path(briefing.audio_path).exists():
                _LOGGER.error("音频文件不存在: %s", briefing.audio_path)
                return False

            # 保存当前播放状态
            self._current_briefing = briefing
            self._current_media_player = media_player_entity_id
            self._playback_position = 0

            # 生成媒体URL
            # 假设文件存储在 www/daily_brief/ 下
            # Home Assistant可以通过 /local/ 路径访问
            audio_filename = Path(briefing.audio_path).name
            media_url = f"/local/daily_brief/{audio_filename}"

            _LOGGER.info(
                "在 %s 上播放简报: %s (URL: %s)",
                media_player_entity_id,
                briefing_date,
                media_url,
            )

            # 调用媒体播放器服务
            await self.hass.services.async_call(
                MEDIA_PLAYER_DOMAIN,
                SERVICE_PLAY_MEDIA,
                {
                    "entity_id": media_player_entity_id,
                    ATTR_MEDIA_CONTENT_ID: media_url,
                    ATTR_MEDIA_CONTENT_TYPE: "music",
                },
                blocking=True,
            )

            # 更新播放统计
            if briefing.id:
                await self._update_play_stats(briefing.id)

            return True

        except Exception as err:
            _LOGGER.error("播放简报时出错: %s", err)
            return False

    async def stop_playback(self, media_player_entity_id: str | None = None) -> bool:
        """停止播放.

        Args:
            media_player_entity_id: 媒体播放器实体ID（可选）

        Returns:
            是否成功停止

        """
        try:
            entity_id = media_player_entity_id or self._current_media_player

            if not entity_id:
                _LOGGER.warning("没有正在播放的媒体播放器")
                return False

            _LOGGER.info("停止播放: %s", entity_id)

            # 调用停止服务
            await self.hass.services.async_call(
                MEDIA_PLAYER_DOMAIN,
                "media_stop",
                {"entity_id": entity_id},
                blocking=True,
            )

            # 保存播放反馈
            if self._current_briefing and self._current_briefing.id:
                await self._save_playback_feedback(
                    self._current_briefing.id,
                    self._playback_position,
                    FEEDBACK_COMPLETE
                    if self._playback_position >= (self._current_briefing.duration or 0)
                    else FEEDBACK_SKIP,
                )

            # 清除当前状态
            self._current_briefing = None
            self._current_media_player = None
            self._playback_position = 0

            return True

        except Exception as err:
            _LOGGER.error("停止播放时出错: %s", err)
            return False

    async def skip_story(self) -> bool:
        """跳过当前故事.

        Returns:
            是否成功跳过

        """
        # 这需要知道每个故事在音频中的位置
        # 作为简化实现，我们暂时只记录跳过反馈
        if self._current_briefing and self._current_briefing.id:
            await self._save_playback_feedback(
                self._current_briefing.id, self._playback_position, FEEDBACK_SKIP
            )
            _LOGGER.info("已记录跳过反馈")
            return True

        return False

    async def _update_play_stats(self, briefing_id: int) -> None:
        """更新播放统计.

        Args:
            briefing_id: 简报ID

        """
        try:
            # 这里需要数据库支持更新played_at和play_count
            # 暂时记录日志
            _LOGGER.debug("更新简报 %d 的播放统计", briefing_id)

        except Exception as err:
            _LOGGER.error("更新播放统计失败: %s", err)

    async def _save_playback_feedback(
        self, briefing_id: int, duration: int, feedback_type: str
    ) -> None:
        """保存播放反馈.

        Args:
            briefing_id: 简报ID
            duration: 播放时长（秒）
            feedback_type: 反馈类型

        """
        try:
            feedback = Feedback(
                briefing_id=briefing_id,
                article_id="",  # 整体简报反馈
                feedback_type=feedback_type,
                listen_duration=duration,
            )

            await self.database.save_feedback(feedback)
            _LOGGER.debug("已保存播放反馈: %s", feedback_type)

        except Exception as err:
            _LOGGER.error("保存播放反馈失败: %s", err)

    def get_current_briefing(self) -> Briefing | None:
        """获取当前播放的简报.

        Returns:
            当前简报或None

        """
        return self._current_briefing

    def get_current_media_player(self) -> str | None:
        """获取当前媒体播放器.

        Returns:
            媒体播放器实体ID或None

        """
        return self._current_media_player

    def is_playing(self) -> bool:
        """检查是否正在播放.

        Returns:
            是否正在播放

        """
        return self._current_briefing is not None
