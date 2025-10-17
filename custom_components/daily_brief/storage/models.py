"""Data models for Daily Brief storage."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserConfig:
    """User configuration model."""

    user_id: str
    language: str = "en"
    briefing_length: str = "balanced"
    interests: list[str] = field(default_factory=list)
    excluded_topics: list[str] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class ContentSource:
    """Content source model."""

    id: int | None = None
    name: str = ""
    url: str = ""
    type: str = "rss"  # rss, api, social
    category: str = ""
    language: str = "en"
    enabled: bool = True
    weight: float = 1.0
    last_fetched: datetime | None = None
    error_count: int = 0


@dataclass
class Article:
    """Article model."""

    id: str  # hash of URL
    source_id: int | None = None
    title: str = ""
    summary: str = ""
    content: str = ""
    url: str = ""
    author: str = ""
    published_at: datetime | None = None
    fetched_at: datetime | None = None
    language: str = "en"
    topics: list[str] = field(default_factory=list)
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "url": self.url,
            "author": self.author,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
            "language": self.language,
            "topics": self.topics,
            "score": self.score,
        }


@dataclass
class Briefing:
    """Briefing model."""

    id: int | None = None
    date: str = ""  # YYYY-MM-DD
    type: str = "morning"
    article_ids: list[str] = field(default_factory=list)
    script: str = ""
    audio_path: str = ""
    duration: int = 0  # seconds
    status: str = "generating"
    generated_at: datetime | None = None
    played_at: datetime | None = None
    play_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "date": self.date,
            "type": self.type,
            "article_ids": self.article_ids,
            "script": self.script,
            "audio_path": self.audio_path,
            "duration": self.duration,
            "status": self.status,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "played_at": self.played_at.isoformat() if self.played_at else None,
            "play_count": self.play_count,
        }


@dataclass
class Feedback:
    """Feedback model."""

    id: int | None = None
    briefing_id: int | None = None
    article_id: str = ""
    feedback_type: str = "like"
    listen_duration: int = 0  # seconds
    timestamp: datetime | None = None


@dataclass
class UserProfile:
    """User profile model for learned preferences."""

    id: int | None = None
    topic: str = ""
    score: float = 0.0
    source: str = ""
    updated_at: datetime | None = None
