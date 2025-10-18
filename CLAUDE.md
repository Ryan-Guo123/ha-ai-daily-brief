# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Daily Brief for Home Assistant** - An AI-powered custom integration that generates personalized daily news briefings from RSS feeds, news APIs, and social media. The system uses LLMs to select important stories, generate natural audio scripts, and deliver them via Home Assistant media players.

**Status:** MVP foundation complete - Core content aggregation, AI selection, and script generation implemented. Audio processing and full playback integration in progress.

## Architecture

### High-Level Data Flow

```
RSS Feeds → Aggregator → Deduplication → Article Scoring → AI Selection → Script Generation → TTS → Audio Processing → Media Player
                                                ↓
                                         SQLite Database (6 tables)
```

### Core Components (Implemented)

```
custom_components/daily_brief/
├── __init__.py              # Integration entry point
├── const.py                 # Constants and configuration schemas
├── coordinator.py           # Data update coordinator
├── config_flow.py           # UI configuration wizard (4 steps)
├── services.py              # 7 services (generate, play, stop, etc.)
├── sensor.py                # Status sensors
├── binary_sensor.py         # Ready state sensor
├── button.py                # Generate button entity
├── media_player.py          # Media player entity
├── components/
│   ├── aggregator.py        # ✅ RSS content fetching (parallel)
│   ├── selector.py          # ✅ AI article scoring & selection
│   ├── generator.py         # ✅ LLM script generation
│   ├── audio.py             # 🚧 TTS & audio processing
│   ├── player.py            # 🚧 Media player integration
│   └── orchestrator.py      # ✅ Main generation coordinator
├── ai/
│   ├── llm.py               # ✅ LLM provider base interface
│   ├── tts.py               # ✅ TTS provider base interface
│   ├── prompts.py           # ✅ Prompt templates
│   └── providers/
│       └── openai.py        # ✅ OpenAI LLM & TTS implementation
├── feeds/
│   ├── parser.py            # ✅ RSS/Atom parsing with HTML cleaning
│   ├── dedup.py             # ✅ Similarity-based deduplication
│   └── content_packs.py     # ✅ 7 pre-configured feed collections
├── storage/
│   ├── database.py          # ✅ SQLite operations (async)
│   ├── models.py            # ✅ Data classes (Article, Briefing, etc.)
│   └── cache.py             # ✅ In-memory TTL cache
└── translations/
    └── en.json              # English UI strings
```

### Technology Stack

- **Language:** Python 3.11+
- **Platform:** Home Assistant 2024.10+
- **Key Libraries:**
  - `aiohttp` - Async HTTP
  - `feedparser`, `beautifulsoup4`, `lxml` - RSS parsing
  - `openai`, `anthropic`, `google-generativeai` - LLMs
  - `elevenlabs` - Premium TTS
  - `pydub`, `mutagen` - Audio processing
  - `langdetect`, `nltk` - NLP
- **External Tools:**
  - FFmpeg (audio processing)
  - RSSHub (feed aggregation)

### Data Flow

1. **Content Aggregation:** Fetch from RSS feeds (RSSHub routes + custom URLs) every 30-60 min → Parse & extract → Deduplicate → Language detection
2. **AI Selection:** Score articles (importance 40pts, relevance 30pts, freshness 20pts, quality 10pts) → LLM ranking (top 50→10) → Balance diversity
3. **Script Generation:** LLM generates conversational audio script (opening → stories with transitions → closing) targeting 150 words/min
4. **Audio Generation:** TTS (ElevenLabs/OpenAI/Piper) → Post-processing (normalize, music, pauses) → Save MP3 with metadata
5. **Delivery:** Auto-play on schedule OR manual trigger → Collect feedback → Update user preferences

### Database Schema (SQLite)

```sql
-- Core tables
config          # User preferences, interests, excluded topics
sources         # RSS/API sources with weights and categories
articles        # Cached articles with scores and topics
briefings       # Generated briefings with metadata and status
feedback        # User feedback (like/dislike/skip) for learning
user_profile    # Learned topic/source preferences (auto-updated)
```

## Development Commands

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_dev.txt

# Setup pre-commit hooks
pre-commit install
```

### Development Workflow

```bash
# Link to Home Assistant for local testing
ln -s $(pwd)/custom_components/daily_brief ~/.homeassistant/custom_components/daily_brief

# Restart Home Assistant
ha core restart

# Watch logs (filter for daily_brief)
tail -f ~/.homeassistant/home-assistant.log | grep daily_brief
```

### Testing

```bash
# Run all tests (when test suite is created)
pytest tests/

# Run with coverage
pytest --cov=custom_components/daily_brief tests/

# Run specific test file
pytest tests/test_aggregator.py

# Run integration tests
pytest tests/test_integration.py -v
```

### Code Quality

```bash
# Format code
black custom_components/
isort custom_components/

# Lint
pylint custom_components/daily_brief/
flake8 custom_components/

# Type checking
mypy custom_components/daily_brief/
```

### Development Workflow

```bash
# Link to HA config for local testing
ln -s $(pwd)/custom_components/daily_brief ~/.homeassistant/custom_components/

# Restart Home Assistant
ha core restart

# Watch logs
tail -f ~/.homeassistant/home-assistant.log | grep daily_brief
```

## Key Implementation Details

### Component Architecture

**BriefingOrchestrator** (`components/orchestrator.py`) - Coordinates entire pipeline:
1. Fetch articles via `ContentAggregator`
2. Select top articles via `ArticleSelector` (scoring + LLM)
3. Generate script via `ScriptGenerator` (LLM)
4. Generate audio via `AudioProcessor` (TTS + FFmpeg)
5. Save briefing metadata to database
6. Update progress throughout process

**Article Selection** (`components/selector.py`) - Hybrid approach:
- **Step 1**: Fast algorithmic scoring of all articles (0-100 points)
  - Importance (40%): Breaking news, source authority
  - Relevance (30%): User interest matching, keyword alignment
  - Freshness (20%): Time-based decay from publish date
  - Quality (10%): Content length, readability
- **Step 2**: LLM selects final N articles from top 50 candidates
- **Step 3**: Ensure topic diversity (max 3 per category)

**Script Generation** (`components/generator.py`):
- Target: 150 words/minute reading pace
- Structure: Opening (date + preview) → Stories (with transitions) → Closing
- LLM-generated natural scripts with fallback to templates
- Includes `<pause>` tags for natural pacing

### AI Provider Abstraction

All LLM and TTS providers implement base interfaces in `ai/llm.py` and `ai/tts.py`:
- Easy provider switching (just change `provider: openai` to `provider: anthropic` in config)
- Automatic fallback on errors
- Cost estimation via `estimate_cost()` method
- Currently implemented: OpenAI (GPT-4o-mini + OpenAI TTS)
- Planned: Anthropic, Google, Ollama, ElevenLabs, Piper

### Cost Management

Estimated costs per briefing (based on ~10 articles, 15-min audio):
- **Budget**: GPT-4o-mini + OpenAI TTS (~$0.18/briefing or ~$5.40/month for daily)
- **Premium**: GPT-4o + ElevenLabs (~$0.45/briefing or ~$13.50/month)
- **Free**: Ollama (local LLM) + Piper (local TTS) - $0 (planned, not yet implemented)

Target: <$0.50 per briefing (configurable cost limits with automatic fallback)

### Content Packs

7 pre-configured content packs in `feeds/content_packs.py`:
- **tech_en**: Hacker News, TechCrunch, The Verge, Ars Technica, Wired
- **tech_zh**: 36氪, 少数派, 爱范儿, V2EX, InfoQ中文
- **world_news_en**: BBC, Reuters, Al Jazeera, The Guardian, AP News
- **news_zh**: 知乎热榜, 澎湃新闻, 财新网, FT中文网
- **business**: WSJ, Bloomberg, Financial Times, The Economist
- **science**: Nature, Science Daily, New Scientist, 果壳网
- **dev**: GitHub Trending, Dev.to, Lobsters, Reddit r/programming

Each pack includes feed URLs, weights (importance multipliers), and associated topics.

### Services (Home Assistant)

7 services implemented in `services.py`:

```yaml
# Generate new briefing
daily_brief.generate:
  briefing_type: morning  # morning, evening, on_demand
  article_count: 10
  force_refresh: false

# Play briefing on media player
daily_brief.play:
  media_player: media_player.bedroom_speaker
  briefing_date: "2025-10-17"  # Optional, defaults to today

# Stop playback
daily_brief.stop:
  media_player: media_player.bedroom_speaker

# Skip current story
daily_brief.skip_story:
  feedback: dislike  # Optional: like, dislike, neutral

# Provide feedback on article
daily_brief.feedback:
  article_id: "abc123"
  feedback_type: like  # like, dislike, skip

# Add custom RSS feed
daily_brief.add_source:
  name: "My Blog"
  url: "https://example.com/feed.xml"
  category: "Technology"

# Regenerate briefing with new script/audio
daily_brief.regenerate:
  keep_articles: true  # Use same articles, regenerate script
```

### Personalization & Learning

- Initial: User selects 3-5 interest categories + optional keywords
- Feedback loop: Listened completely (+10), Skipped (-5), Liked (+20), Disliked (-30)
- Weekly profile update: Adjust topic/source scores, decay old preferences over 30 days

### Audio Processing Pipeline

1. Generate script with `<pause>` tags for natural pacing
2. TTS conversion (chunked for long scripts)
3. Post-processing: Normalize volume → Add intro/outro music → Insert pauses → Speed adjustment
4. Save as MP3 with metadata (title, artist, album art) to `/config/www/daily_brief/`

## Configuration Files

### Home Assistant Config

```yaml
# configuration.yaml
daily_brief:
  llm:
    provider: openai  # openai, anthropic, google, ollama
    api_key: !secret openai_key
    model: gpt-4o-mini
  tts:
    provider: elevenlabs  # elevenlabs, openai, google, azure, piper
    api_key: !secret elevenlabs_key
    voice_id: "21m00Tcm4TlvDq8ikWAM"
  content:
    packs:
      - tech_en
      - business
    custom_feeds:
      - url: https://example.com/feed.xml
        weight: 1.0
  schedule:
    generation_time: "06:30:00"
    auto_play: true
    auto_play_time: "07:00:00"
    media_player: media_player.bedroom_speaker
```

### Manifest

```json
{
  "domain": "daily_brief",
  "name": "Daily Brief",
  "version": "0.1.0",
  "documentation": "https://github.com/Ryan-Guo123/ha-ai-daily-brief",
  "dependencies": [],
  "codeowners": ["@Ryan-Guo123"],
  "requirements": [
    "aiohttp>=3.9.0",
    "feedparser>=6.0.10",
    "beautifulsoup4>=4.12.0",
    "openai>=1.0.0",
    "elevenlabs>=0.2.0",
    "pydub>=0.25.0",
    "langdetect>=1.0.9"
  ],
  "iot_class": "cloud_polling",
  "config_flow": true
}
```

## Development Guidelines

### Adding New AI Providers

1. Create new file in `ai/providers/` (e.g., `anthropic.py`)
2. Implement `LLMProvider` and/or `TTSProvider` base interfaces from `ai/llm.py` and `ai/tts.py`
3. Add provider configuration options in `const.py`
4. Update `config_flow.py` to include new provider in setup wizard
5. Update provider factory methods in `orchestrator.py`

Example provider implementation:
```python
# ai/providers/anthropic.py
from ..llm import LLMProvider

class AnthropicLLMProvider(LLMProvider):
    async def select_articles(self, articles, user_interests, count):
        # Call Anthropic API for article selection
        pass

    async def generate_script(self, articles, style, duration, language):
        # Call Anthropic API for script generation
        pass

    async def estimate_cost(self, operation, **kwargs):
        # Return cost estimate in USD
        pass
```

### Adding New Content Packs

Edit `feeds/content_packs.py` and add to the `CONTENT_PACKS` dictionary:
```python
"my_pack_id": {
    "id": "my_pack_id",
    "name": "My Content Pack",
    "language": "en",
    "category": "technology",
    "icon": "mdi:newspaper",
    "feeds": [
        {
            "name": "Example Source",
            "url": "https://example.com/feed.xml",
            "weight": 1.0,  # Importance multiplier (0.5-2.0)
            "language": "en"
        }
    ],
    "topics": ["Topic1", "Topic2"]
}
```

### Extending the Scoring Algorithm

Modify `components/selector.py` → `ArticleSelector.calculate_score()`:
- Each scoring factor allocates points (must total 100)
- Returns score 0-100 for each article
- Higher scores = more likely to be selected by LLM

## Testing Strategy

When creating tests (no test suite currently exists):

**Unit Tests** - Test individual components:
- `tests/test_aggregator.py` - Feed fetching and parsing
- `tests/test_selector.py` - Article scoring and selection logic
- `tests/test_generator.py` - Script generation
- `tests/test_dedup.py` - Deduplication algorithm

**Integration Tests** - Test full pipeline:
- `tests/test_integration.py` - End-to-end briefing generation
- `tests/test_services.py` - Home Assistant service calls

**Fixtures** - Mock data for tests:
- `tests/fixtures/sample_feeds.xml` - Mock RSS feeds
- `tests/fixtures/sample_articles.json` - Pre-parsed articles
- `tests/fixtures/mock_api_responses/` - LLM/TTS API mocks

## Known Limitations (Current Implementation)

1. **Audio Processing**: TTS generation and FFmpeg processing partially implemented
2. **Playback Control**: Basic media player entity exists, needs full state management
3. **Scheduling**: No automated generation scheduling yet (manual trigger only)
4. **Tests**: No test suite created (high priority for v0.1.0 completion)
5. **Provider Coverage**: Only OpenAI implemented; Anthropic/Google/Ollama/ElevenLabs pending
6. **Feedback Loop**: Feedback collection works, but learning/profile updates not fully implemented

## Development Roadmap

**Current (MVP v0.1.0 in progress):**
- ✅ RSS aggregation with 7 content packs
- ✅ AI article selection (OpenAI GPT-4o-mini)
- ✅ Script generation with LLM
- 🚧 Audio processing (TTS + FFmpeg)
- 🚧 Media player integration
- ⏳ Test suite creation
- ⏳ Documentation completion

**Beta (v0.2.0):** Scheduled automation, multiple AI providers, feedback learning, 10+ content packs

**v1.0.0:** Local LLM (Ollama), advanced personalization, podcast feed, comprehensive tests

**Future:** Social media integration, voice cloning, conversational mode, multi-user profiles

## Common Development Tasks

### Debug Briefing Generation

1. Check logs: `tail -f ~/.homeassistant/home-assistant.log | grep daily_brief`
2. Inspect database: `sqlite3 ~/.homeassistant/daily_brief.db`
3. Verify article fetch: `SELECT COUNT(*) FROM articles WHERE fetched_at > datetime('now', '-1 day');`
4. Test generation: Call `daily_brief.generate` service with `force_refresh: true`

### Add Support for New Language

1. Create content pack for target language in `feeds/content_packs.py`
2. Add UI translations in `translations/{lang_code}.json`
3. Update language detection in `feeds/parser.py` if needed
4. Test with multi-language briefing generation

### Troubleshoot API Costs

- Check cost estimates: Each provider implements `estimate_cost()` method
- Review `const.py` for `MAX_COST_PER_BRIEFING` default (currently $0.50)
- Monitor actual costs via OpenAI/ElevenLabs dashboards
- Consider fallback to cheaper models or local options

## Important Files to Review

**Before Making Major Changes:**
- `const.py` - All constants, defaults, and configuration schemas
- `storage/models.py` - Core data structure definitions
- `coordinator.py` - State management and entity updates
- `components/orchestrator.py` - Main generation pipeline coordinator

**Configuration & Setup:**
- `manifest.json` - Integration metadata, dependencies, version
- `config_flow.py` - UI configuration wizard (4-step flow)
- `strings.json` / `translations/en.json` - All user-facing text

**External Documentation:**
- `README.md` - User-facing documentation and installation guide
- `DEVELOPMENT.md` - Implementation status summary
- `PRD-Home Assistant Daily Brief.md` - Original product requirements and design

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io)
- [HACS Documentation](https://hacs.xyz)
- [PRD Document](./PRD-Home%20Assistant%20Daily%20Brief.md) - Complete product requirements
- [Development Summary](./DEVELOPMENT.md) - Current implementation status
