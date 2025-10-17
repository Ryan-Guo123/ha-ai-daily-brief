"""Constants for the Daily Brief integration."""
from typing import Final

# Integration domain
DOMAIN: Final = "daily_brief"

# Configuration keys
CONF_LLM_PROVIDER: Final = "llm_provider"
CONF_LLM_API_KEY: Final = "llm_api_key"
CONF_LLM_MODEL: Final = "llm_model"
CONF_TTS_PROVIDER: Final = "tts_provider"
CONF_TTS_API_KEY: Final = "tts_api_key"
CONF_TTS_VOICE: Final = "tts_voice"
CONF_CONTENT_PACKS: Final = "content_packs"
CONF_CUSTOM_FEEDS: Final = "custom_feeds"
CONF_INTERESTS: Final = "interests"
CONF_BRIEFING_LENGTH: Final = "briefing_length"
CONF_LANGUAGE: Final = "language"
CONF_GENERATION_TIME: Final = "generation_time"
CONF_AUTO_PLAY: Final = "auto_play"
CONF_AUTO_PLAY_TIME: Final = "auto_play_time"
CONF_MEDIA_PLAYER: Final = "media_player"

# Default values
DEFAULT_LLM_PROVIDER: Final = "openai"
DEFAULT_LLM_MODEL: Final = "gpt-4o-mini"
DEFAULT_TTS_PROVIDER: Final = "openai"
DEFAULT_TTS_VOICE: Final = "alloy"
DEFAULT_BRIEFING_LENGTH: Final = "balanced"
DEFAULT_LANGUAGE: Final = "en"
DEFAULT_GENERATION_TIME: Final = "06:30:00"
DEFAULT_AUTO_PLAY_TIME: Final = "07:00:00"
DEFAULT_ARTICLE_COUNT: Final = 10
DEFAULT_TARGET_DURATION: Final = 15  # minutes

# Briefing types
BRIEFING_TYPE_MORNING: Final = "morning"
BRIEFING_TYPE_EVENING: Final = "evening"
BRIEFING_TYPE_ON_DEMAND: Final = "on_demand"

# Briefing lengths
BRIEFING_LENGTH_QUICK: Final = "quick"  # 5-10 min, 5 stories
BRIEFING_LENGTH_BALANCED: Final = "balanced"  # 10-20 min, 10 stories
BRIEFING_LENGTH_DEEP: Final = "deep"  # 20-30 min, 15 stories

# Briefing length configurations
BRIEFING_CONFIGS: Final = {
    BRIEFING_LENGTH_QUICK: {"duration": 7, "count": 5},
    BRIEFING_LENGTH_BALANCED: {"duration": 15, "count": 10},
    BRIEFING_LENGTH_DEEP: {"duration": 25, "count": 15},
}

# Scoring weights
SCORE_IMPORTANCE_WEIGHT: Final = 40
SCORE_RELEVANCE_WEIGHT: Final = 30
SCORE_FRESHNESS_WEIGHT: Final = 20
SCORE_QUALITY_WEIGHT: Final = 10

# Freshness decay (hours)
FRESHNESS_EXCELLENT: Final = 2  # +20 points
FRESHNESS_GOOD: Final = 12  # +15 points
FRESHNESS_FAIR: Final = 24  # +10 points

# Quality thresholds
QUALITY_MIN_LENGTH: Final = 500  # words
QUALITY_MAX_LENGTH: Final = 3000  # words
QUALITY_IDEAL_LENGTH: Final = 1500  # words

# Deduplication threshold
DEDUP_SIMILARITY_THRESHOLD: Final = 0.8

# Services
SERVICE_GENERATE: Final = "generate"
SERVICE_PLAY: Final = "play"
SERVICE_STOP: Final = "stop"
SERVICE_SKIP_STORY: Final = "skip_story"
SERVICE_FEEDBACK: Final = "feedback"
SERVICE_ADD_SOURCE: Final = "add_source"
SERVICE_REGENERATE: Final = "regenerate"

# Feedback types
FEEDBACK_LIKE: Final = "like"
FEEDBACK_DISLIKE: Final = "dislike"
FEEDBACK_SKIP: Final = "skip"
FEEDBACK_COMPLETE: Final = "complete"

# Feedback scores
FEEDBACK_SCORES: Final = {
    FEEDBACK_LIKE: 20,
    FEEDBACK_DISLIKE: -30,
    FEEDBACK_SKIP: -5,
    FEEDBACK_COMPLETE: 10,
}

# Status values
STATUS_IDLE: Final = "idle"
STATUS_FETCHING: Final = "fetching"
STATUS_SELECTING: Final = "selecting"
STATUS_GENERATING: Final = "generating"
STATUS_READY: Final = "ready"
STATUS_PLAYING: Final = "playing"
STATUS_ERROR: Final = "error"

# Storage paths
STORAGE_DIR: Final = "www/daily_brief"
DATABASE_NAME: Final = "daily_brief.db"

# Audio settings
AUDIO_FORMAT: Final = "mp3"
AUDIO_SAMPLE_RATE: Final = 22050
AUDIO_READING_SPEED: Final = 150  # words per minute

# API limits and timeouts
API_TIMEOUT: Final = 60  # seconds
MAX_RETRIES: Final = 3
RETRY_DELAY: Final = 2  # seconds
MAX_CONCURRENT_FETCHES: Final = 10

# Cache settings
CACHE_DURATION: Final = 3600  # 1 hour in seconds
FEED_FETCH_INTERVAL: Final = 1800  # 30 minutes

# Cost limits (USD)
MAX_COST_PER_BRIEFING: Final = 0.50

# Retention settings
MIN_RETENTION_DAYS: Final = 1
MAX_RETENTION_DAYS: Final = 30
DEFAULT_RETENTION_DAYS: Final = 7

# Supported languages
SUPPORTED_LANGUAGES: Final = ["en", "zh-Hans", "zh-Hant", "es", "fr", "de", "ja", "ko"]

# LLM providers
LLM_PROVIDER_OPENAI: Final = "openai"
LLM_PROVIDER_ANTHROPIC: Final = "anthropic"
LLM_PROVIDER_GOOGLE: Final = "google"
LLM_PROVIDER_OLLAMA: Final = "ollama"

# TTS providers
TTS_PROVIDER_OPENAI: Final = "openai"
TTS_PROVIDER_ELEVENLABS: Final = "elevenlabs"
TTS_PROVIDER_GOOGLE: Final = "google"
TTS_PROVIDER_AZURE: Final = "azure"
TTS_PROVIDER_PIPER: Final = "piper"
TTS_PROVIDER_HA: Final = "ha"

# Entity names
SENSOR_STATUS: Final = "sensor.daily_brief_status"
SENSOR_PROGRESS: Final = "sensor.daily_brief_progress"
SENSOR_ARTICLES: Final = "sensor.daily_brief_articles"
SENSOR_STATS: Final = "sensor.daily_brief_stats"
BINARY_SENSOR_READY: Final = "binary_sensor.daily_brief_ready"
BINARY_SENSOR_PLAYING: Final = "binary_sensor.daily_brief_playing"
BINARY_SENSOR_NEW_CONTENT: Final = "binary_sensor.daily_brief_new_content"
BUTTON_GENERATE: Final = "button.daily_brief_generate"
BUTTON_PLAY: Final = "button.daily_brief_play"
BUTTON_REGENERATE: Final = "button.daily_brief_regenerate"
MEDIA_PLAYER_BRIEF: Final = "media_player.daily_brief"

# Attributes
ATTR_ARTICLE_ID: Final = "article_id"
ATTR_BRIEFING_TYPE: Final = "briefing_type"
ATTR_BRIEFING_DATE: Final = "briefing_date"
ATTR_ARTICLE_COUNT: Final = "article_count"
ATTR_TARGET_DURATION: Final = "target_duration"
ATTR_FORCE_REFRESH: Final = "force_refresh"
ATTR_FEEDBACK_TYPE: Final = "feedback_type"
ATTR_KEEP_ARTICLES: Final = "keep_articles"
ATTR_SOURCE_NAME: Final = "name"
ATTR_SOURCE_URL: Final = "url"
ATTR_SOURCE_CATEGORY: Final = "category"
ATTR_MEDIA_PLAYER: Final = "media_player"
ATTR_SHUFFLE: Final = "shuffle"
