"""音频生成和处理组件."""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
from pydub import AudioSegment

from ..ai.tts import TTSProvider
from ..const import AUDIO_FORMAT, AUDIO_SAMPLE_RATE, STORAGE_DIR

_LOGGER = logging.getLogger(__name__)


class AudioProcessor:
    """音频生成和处理器."""

    def __init__(self, tts_provider: TTSProvider, storage_path: Path) -> None:
        """初始化音频处理器.

        Args:
            tts_provider: TTS提供商实例
            storage_path: 存储路径

        """
        self.tts_provider = tts_provider
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

    async def generate_briefing_audio(
        self,
        script: str,
        date: str,
        briefing_type: str = "morning",
        **kwargs: Any,
    ) -> tuple[str, int]:
        """生成简报音频文件.

        Args:
            script: 脚本文本
            date: 日期 (YYYY-MM-DD)
            briefing_type: 简报类型
            **kwargs: 额外参数

        Returns:
            元组 (音频文件路径, 时长秒数)

        """
        _LOGGER.info("开始生成音频简报: %s", date)

        try:
            # 处理暂停标签
            audio_segments = []
            script_parts = script.split("<pause>")

            for idx, part in enumerate(script_parts):
                part = part.strip()
                if not part:
                    continue

                _LOGGER.debug("生成音频片段 %d/%d", idx + 1, len(script_parts))

                # 使用TTS生成音频
                audio_bytes = await self.tts_provider.generate_audio(
                    part,
                    voice=kwargs.get("voice"),
                    speed=kwargs.get("speed", 1.0),
                )

                # 将字节转换为AudioSegment
                audio_segment = self._bytes_to_audio_segment(audio_bytes)
                audio_segments.append(audio_segment)

                # 在片段之间添加暂停（除了最后一个）
                if idx < len(script_parts) - 1:
                    pause_duration = kwargs.get("pause_duration", 1000)  # 毫秒
                    silence = AudioSegment.silent(duration=pause_duration)
                    audio_segments.append(silence)

            # 合并所有音频片段
            if not audio_segments:
                raise ValueError("没有生成任何音频片段")

            combined_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                combined_audio += segment

            # 音频后处理
            processed_audio = self._post_process_audio(combined_audio, **kwargs)

            # 生成文件名和路径
            filename = f"{date}_{briefing_type}.{AUDIO_FORMAT}"
            audio_path = self.storage_path / filename

            # 导出为MP3
            processed_audio.export(
                str(audio_path),
                format=AUDIO_FORMAT,
                bitrate="128k",
                parameters=["-ar", str(AUDIO_SAMPLE_RATE)],
            )

            # 添加元数据
            self._add_metadata(
                audio_path,
                title=f"每日简报 - {date}",
                artist="Daily Brief",
                album=datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m"),
                date=date,
            )

            duration_seconds = int(len(processed_audio) / 1000)

            _LOGGER.info(
                "音频生成完成: %s (时长: %d秒, 大小: %d KB)",
                audio_path,
                duration_seconds,
                audio_path.stat().st_size / 1024,
            )

            return str(audio_path), duration_seconds

        except Exception as err:
            _LOGGER.error("生成音频时出错: %s", err)
            raise

    def _bytes_to_audio_segment(self, audio_bytes: bytes) -> AudioSegment:
        """将音频字节转换为AudioSegment.

        Args:
            audio_bytes: 音频字节数据

        Returns:
            AudioSegment对象

        """
        # 创建临时文件
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        try:
            # 从临时文件加载
            audio_segment = AudioSegment.from_mp3(tmp_path)
            return audio_segment
        finally:
            # 清理临时文件
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    def _post_process_audio(
        self, audio: AudioSegment, **kwargs: Any
    ) -> AudioSegment:
        """音频后处理.

        Args:
            audio: 原始音频
            **kwargs: 处理参数

        Returns:
            处理后的音频

        """
        processed = audio

        # 音量标准化
        if kwargs.get("normalize_volume", True):
            processed = self._normalize_volume(processed)

        # 速度调整
        speed = kwargs.get("playback_speed", 1.0)
        if speed != 1.0:
            processed = self._change_speed(processed, speed)

        # 添加开场音乐（如果提供）
        intro_music_path = kwargs.get("intro_music_path")
        if intro_music_path and Path(intro_music_path).exists():
            processed = self._add_intro_music(processed, intro_music_path)

        # 添加结束音乐（如果提供）
        outro_music_path = kwargs.get("outro_music_path")
        if outro_music_path and Path(outro_music_path).exists():
            processed = self._add_outro_music(processed, outro_music_path)

        return processed

    def _normalize_volume(self, audio: AudioSegment) -> AudioSegment:
        """标准化音量.

        Args:
            audio: 输入音频

        Returns:
            音量标准化后的音频

        """
        # 目标音量（dBFS）
        target_dBFS = -20.0

        # 计算增益变化
        change_in_dBFS = target_dBFS - audio.dBFS

        # 应用增益
        return audio.apply_gain(change_in_dBFS)

    def _change_speed(self, audio: AudioSegment, speed: float) -> AudioSegment:
        """改变播放速度.

        Args:
            audio: 输入音频
            speed: 速度倍数 (0.5-2.0)

        Returns:
            调速后的音频

        """
        # 使用frame_rate来改变速度
        # 注意：这会改变音调，实际应用中可能需要使用更复杂的算法
        new_frame_rate = int(audio.frame_rate * speed)
        return audio._spawn(audio.raw_data, overrides={"frame_rate": new_frame_rate})

    def _add_intro_music(
        self, audio: AudioSegment, intro_path: str
    ) -> AudioSegment:
        """添加开场音乐.

        Args:
            audio: 主音频
            intro_path: 开场音乐路径

        Returns:
            添加开场音乐后的音频

        """
        try:
            intro = AudioSegment.from_file(intro_path)

            # 淡出开场音乐
            intro = intro.fade_out(1000)  # 1秒淡出

            # 降低开场音乐音量
            intro = intro - 10  # 降低10dB

            # 限制开场音乐长度
            max_intro_length = 5000  # 5秒
            if len(intro) > max_intro_length:
                intro = intro[:max_intro_length]

            # 合并音频
            return intro + audio

        except Exception as err:
            _LOGGER.warning("添加开场音乐失败: %s", err)
            return audio

    def _add_outro_music(
        self, audio: AudioSegment, outro_path: str
    ) -> AudioSegment:
        """添加结束音乐.

        Args:
            audio: 主音频
            outro_path: 结束音乐路径

        Returns:
            添加结束音乐后的音频

        """
        try:
            outro = AudioSegment.from_file(outro_path)

            # 淡入结束音乐
            outro = outro.fade_in(1000)  # 1秒淡入

            # 降低结束音乐音量
            outro = outro - 10  # 降低10dB

            # 限制结束音乐长度
            max_outro_length = 5000  # 5秒
            if len(outro) > max_outro_length:
                outro = outro[:max_outro_length]

            # 合并音频
            return audio + outro

        except Exception as err:
            _LOGGER.warning("添加结束音乐失败: %s", err)
            return audio

    def _add_metadata(
        self,
        audio_path: Path,
        title: str,
        artist: str,
        album: str,
        date: str,
    ) -> None:
        """添加MP3元数据.

        Args:
            audio_path: 音频文件路径
            title: 标题
            artist: 艺术家
            album: 专辑
            date: 日期

        """
        try:
            # 添加基本元数据
            audio = EasyID3(str(audio_path))
            audio["title"] = title
            audio["artist"] = artist
            audio["album"] = album
            audio["date"] = date
            audio.save()

            _LOGGER.debug("已添加元数据到: %s", audio_path)

        except Exception as err:
            _LOGGER.warning("添加元数据失败: %s", err)

    async def cleanup_old_files(self, days: int = 7) -> int:
        """清理旧的音频文件.

        Args:
            days: 保留天数

        Returns:
            删除的文件数量

        """
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)

        try:
            for file_path in self.storage_path.glob(f"*.{AUDIO_FORMAT}"):
                if file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
                    _LOGGER.debug("已删除旧文件: %s", file_path)

            if deleted_count > 0:
                _LOGGER.info("清理了 %d 个旧音频文件", deleted_count)

        except Exception as err:
            _LOGGER.error("清理旧文件时出错: %s", err)

        return deleted_count

    def get_audio_info(self, audio_path: str) -> dict[str, Any]:
        """获取音频文件信息.

        Args:
            audio_path: 音频文件路径

        Returns:
            音频信息字典

        """
        try:
            audio = MP3(audio_path)

            return {
                "duration": int(audio.info.length),
                "bitrate": audio.info.bitrate,
                "sample_rate": audio.info.sample_rate,
                "channels": audio.info.channels,
                "file_size": Path(audio_path).stat().st_size,
            }

        except Exception as err:
            _LOGGER.error("获取音频信息失败: %s", err)
            return {}
