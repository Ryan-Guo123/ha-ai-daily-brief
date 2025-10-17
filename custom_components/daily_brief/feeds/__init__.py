"""Feeds module for Daily Brief."""
from .content_packs import (
    CONTENT_PACKS,
    get_content_pack,
    get_feeds_from_packs,
    list_content_packs,
)
from .dedup import Deduplicator
from .parser import FeedParser

__all__ = [
    "FeedParser",
    "Deduplicator",
    "CONTENT_PACKS",
    "get_content_pack",
    "list_content_packs",
    "get_feeds_from_packs",
]
