"""Caching layer for Daily Brief."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any

_LOGGER = logging.getLogger(__name__)


class Cache:
    """Simple in-memory cache with expiration."""

    def __init__(self, default_ttl: int = 3600) -> None:
        """Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds

        """
        self._cache: dict[str, dict[str, Any]] = {}
        self._default_ttl = default_ttl

    def _generate_key(self, *args: Any) -> str:
        """Generate cache key from arguments."""
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, *args: Any) -> Any | None:
        """Get value from cache.

        Args:
            *args: Arguments to generate cache key

        Returns:
            Cached value or None if not found or expired

        """
        key = self._generate_key(*args)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        if datetime.now() > entry["expires_at"]:
            # Expired, remove from cache
            del self._cache[key]
            return None

        return entry["value"]

    def set(self, *args: Any, value: Any, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            *args: Arguments to generate cache key (last arg is the value)
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if not specified)

        """
        key = self._generate_key(*args[:-1])  # Exclude value from key
        ttl = ttl or self._default_ttl

        self._cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
        }

    def invalidate(self, *args: Any) -> None:
        """Invalidate cache entry.

        Args:
            *args: Arguments to generate cache key

        """
        key = self._generate_key(*args)
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        _LOGGER.debug("Cache cleared")

    def cleanup_expired(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed

        """
        now = datetime.now()
        expired_keys = [
            key
            for key, entry in self._cache.items()
            if now > entry["expires_at"]
        ]

        for key in expired_keys:
            del self._cache[key]

        if expired_keys:
            _LOGGER.debug("Removed %d expired cache entries", len(expired_keys))

        return len(expired_keys)

    def stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats

        """
        now = datetime.now()
        valid_entries = sum(
            1 for entry in self._cache.values() if now <= entry["expires_at"]
        )
        expired_entries = len(self._cache) - valid_entries

        return {
            "total_entries": len(self._cache),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
        }
