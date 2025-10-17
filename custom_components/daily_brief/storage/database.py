"""Database operations for Daily Brief."""
from __future__ import annotations

import aiosqlite
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from ..const import DATABASE_NAME, STORAGE_DIR
from .models import Article, Briefing, ContentSource, Feedback, UserConfig, UserProfile

_LOGGER = logging.getLogger(__name__)


class Database:
    """Database manager for Daily Brief."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize database."""
        self.hass = hass
        self._db_path = Path(hass.config.path(STORAGE_DIR)) / DATABASE_NAME
        self._connection: aiosqlite.Connection | None = None

    async def async_initialize(self) -> None:
        """Initialize database connection and create tables."""
        _LOGGER.debug("Initializing database at %s", self._db_path)

        self._connection = await aiosqlite.connect(str(self._db_path))
        self._connection.row_factory = aiosqlite.Row

        await self._create_tables()
        _LOGGER.info("Database initialized successfully")

    async def async_close(self) -> None:
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            _LOGGER.debug("Database connection closed")

    async def _create_tables(self) -> None:
        """Create database tables."""
        if not self._connection:
            return

        # User configuration table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                language TEXT DEFAULT 'en',
                briefing_length TEXT DEFAULT 'balanced',
                interests TEXT,
                excluded_topics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Content sources table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                type TEXT DEFAULT 'rss',
                category TEXT,
                language TEXT DEFAULT 'en',
                enabled BOOLEAN DEFAULT 1,
                weight REAL DEFAULT 1.0,
                last_fetched TIMESTAMP,
                error_count INTEGER DEFAULT 0
            )
        """)

        # Articles cache table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                source_id INTEGER,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                url TEXT NOT NULL,
                author TEXT,
                published_at TIMESTAMP,
                fetched_at TIMESTAMP,
                language TEXT,
                topics TEXT,
                score REAL DEFAULT 0,
                FOREIGN KEY (source_id) REFERENCES sources(id)
            )
        """)

        # Briefings table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS briefings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                type TEXT DEFAULT 'morning',
                article_ids TEXT,
                script TEXT,
                audio_path TEXT,
                duration INTEGER DEFAULT 0,
                status TEXT DEFAULT 'generating',
                generated_at TIMESTAMP,
                played_at TIMESTAMP,
                play_count INTEGER DEFAULT 0
            )
        """)

        # Feedback table
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                briefing_id INTEGER,
                article_id TEXT,
                feedback_type TEXT,
                listen_duration INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (briefing_id) REFERENCES briefings(id)
            )
        """)

        # User profile table (learned preferences)
        await self._connection.execute("""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL UNIQUE,
                score REAL DEFAULT 0,
                source TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_articles_score ON articles(score DESC)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_briefings_date ON briefings(date DESC)"
        )
        await self._connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_feedback_timestamp ON feedback(timestamp DESC)"
        )

        await self._connection.commit()

    # Config operations
    async def get_config(self) -> dict[str, Any] | None:
        """Get user configuration."""
        if not self._connection:
            return None

        cursor = await self._connection.execute("SELECT * FROM config LIMIT 1")
        row = await cursor.fetchone()

        if not row:
            return None

        return {
            "user_id": row["user_id"],
            "language": row["language"],
            "briefing_length": row["briefing_length"],
            "interests": json.loads(row["interests"]) if row["interests"] else [],
            "excluded_topics": json.loads(row["excluded_topics"]) if row["excluded_topics"] else [],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    async def save_config(self, config: dict[str, Any]) -> None:
        """Save user configuration."""
        if not self._connection:
            return

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO config
            (user_id, language, briefing_length, interests, excluded_topics, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                config["user_id"],
                config["language"],
                config["briefing_length"],
                json.dumps(config.get("interests", [])),
                json.dumps(config.get("excluded_topics", [])),
            ),
        )
        await self._connection.commit()

    # Source operations
    async def add_source(self, source: ContentSource) -> int:
        """Add a content source."""
        if not self._connection:
            return -1

        cursor = await self._connection.execute(
            """
            INSERT INTO sources (name, url, type, category, language, enabled, weight)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source.name,
                source.url,
                source.type,
                source.category,
                source.language,
                source.enabled,
                source.weight,
            ),
        )
        await self._connection.commit()
        return cursor.lastrowid or -1

    async def get_sources(self, enabled_only: bool = True) -> list[ContentSource]:
        """Get all content sources."""
        if not self._connection:
            return []

        query = "SELECT * FROM sources"
        if enabled_only:
            query += " WHERE enabled = 1"

        cursor = await self._connection.execute(query)
        rows = await cursor.fetchall()

        sources = []
        for row in rows:
            sources.append(
                ContentSource(
                    id=row["id"],
                    name=row["name"],
                    url=row["url"],
                    type=row["type"],
                    category=row["category"],
                    language=row["language"],
                    enabled=bool(row["enabled"]),
                    weight=row["weight"],
                    last_fetched=datetime.fromisoformat(row["last_fetched"])
                    if row["last_fetched"]
                    else None,
                    error_count=row["error_count"],
                )
            )

        return sources

    async def update_source_fetch_time(self, source_id: int) -> None:
        """Update source last fetch time."""
        if not self._connection:
            return

        await self._connection.execute(
            "UPDATE sources SET last_fetched = CURRENT_TIMESTAMP WHERE id = ?",
            (source_id,),
        )
        await self._connection.commit()

    # Article operations
    async def save_article(self, article: Article) -> None:
        """Save an article."""
        if not self._connection:
            return

        await self._connection.execute(
            """
            INSERT OR REPLACE INTO articles
            (id, source_id, title, summary, content, url, author, published_at,
             fetched_at, language, topics, score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                article.id,
                article.source_id,
                article.title,
                article.summary,
                article.content,
                article.url,
                article.author,
                article.published_at,
                article.fetched_at,
                article.language,
                json.dumps(article.topics),
                article.score,
            ),
        )
        await self._connection.commit()

    async def get_articles(
        self, limit: int | None = None, min_score: float = 0.0
    ) -> list[Article]:
        """Get articles, optionally filtered by score."""
        if not self._connection:
            return []

        query = "SELECT * FROM articles WHERE score >= ? ORDER BY score DESC, published_at DESC"
        params: tuple[Any, ...] = (min_score,)

        if limit:
            query += " LIMIT ?"
            params = (*params, limit)

        cursor = await self._connection.execute(query, params)
        rows = await cursor.fetchall()

        articles = []
        for row in rows:
            articles.append(
                Article(
                    id=row["id"],
                    source_id=row["source_id"],
                    title=row["title"],
                    summary=row["summary"],
                    content=row["content"],
                    url=row["url"],
                    author=row["author"],
                    published_at=datetime.fromisoformat(row["published_at"])
                    if row["published_at"]
                    else None,
                    fetched_at=datetime.fromisoformat(row["fetched_at"])
                    if row["fetched_at"]
                    else None,
                    language=row["language"],
                    topics=json.loads(row["topics"]) if row["topics"] else [],
                    score=row["score"],
                )
            )

        return articles

    # Briefing operations
    async def save_briefing(self, briefing: Briefing) -> int:
        """Save a briefing."""
        if not self._connection:
            return -1

        cursor = await self._connection.execute(
            """
            INSERT INTO briefings
            (date, type, article_ids, script, audio_path, duration, status, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                briefing.date,
                briefing.type,
                json.dumps(briefing.article_ids),
                briefing.script,
                briefing.audio_path,
                briefing.duration,
                briefing.status,
                briefing.generated_at,
            ),
        )
        await self._connection.commit()
        return cursor.lastrowid or -1

    async def get_briefing(self, date: str) -> Briefing | None:
        """Get briefing by date."""
        if not self._connection:
            return None

        cursor = await self._connection.execute(
            "SELECT * FROM briefings WHERE date = ? ORDER BY generated_at DESC LIMIT 1",
            (date,),
        )
        row = await cursor.fetchone()

        if not row:
            return None

        return Briefing(
            id=row["id"],
            date=row["date"],
            type=row["type"],
            article_ids=json.loads(row["article_ids"]) if row["article_ids"] else [],
            script=row["script"],
            audio_path=row["audio_path"],
            duration=row["duration"],
            status=row["status"],
            generated_at=datetime.fromisoformat(row["generated_at"])
            if row["generated_at"]
            else None,
            played_at=datetime.fromisoformat(row["played_at"]) if row["played_at"] else None,
            play_count=row["play_count"],
        )

    async def update_briefing_status(self, briefing_id: int, status: str) -> None:
        """Update briefing status."""
        if not self._connection:
            return

        await self._connection.execute(
            "UPDATE briefings SET status = ? WHERE id = ?", (status, briefing_id)
        )
        await self._connection.commit()

    # Feedback operations
    async def save_feedback(self, feedback: Feedback) -> None:
        """Save user feedback."""
        if not self._connection:
            return

        await self._connection.execute(
            """
            INSERT INTO feedback (briefing_id, article_id, feedback_type, listen_duration)
            VALUES (?, ?, ?, ?)
            """,
            (
                feedback.briefing_id,
                feedback.article_id,
                feedback.feedback_type,
                feedback.listen_duration,
            ),
        )
        await self._connection.commit()

    async def get_feedback_stats(self) -> dict[str, Any]:
        """Get feedback statistics."""
        if not self._connection:
            return {}

        cursor = await self._connection.execute(
            """
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN feedback_type = 'like' THEN 1 ELSE 0 END) as likes,
                SUM(CASE WHEN feedback_type = 'dislike' THEN 1 ELSE 0 END) as dislikes,
                SUM(CASE WHEN feedback_type = 'skip' THEN 1 ELSE 0 END) as skips
            FROM feedback
            """
        )
        row = await cursor.fetchone()

        return {
            "total": row["total"] if row else 0,
            "likes": row["likes"] if row else 0,
            "dislikes": row["dislikes"] if row else 0,
            "skips": row["skips"] if row else 0,
        }

    # Cleanup operations
    async def cleanup_old_articles(self, days: int = 7) -> None:
        """Delete articles older than specified days."""
        if not self._connection:
            return

        await self._connection.execute(
            "DELETE FROM articles WHERE fetched_at < datetime('now', '-' || ? || ' days')",
            (days,),
        )
        await self._connection.commit()
        _LOGGER.debug("Cleaned up articles older than %d days", days)

    async def cleanup_old_briefings(self, days: int = 7) -> None:
        """Delete briefings older than specified days."""
        if not self._connection:
            return

        await self._connection.execute(
            "DELETE FROM briefings WHERE date < date('now', '-' || ? || ' days')",
            (days,),
        )
        await self._connection.commit()
        _LOGGER.debug("Cleaned up briefings older than %d days", days)
