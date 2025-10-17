# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Daily Brief for Home Assistant** - An AI-powered custom integration that generates personalized daily news briefings from RSS feeds, news APIs, and social media. The system uses LLMs to select important stories, generate natural audio scripts, and deliver them via Home Assistant media players.

**Status:** Planning phase - PRD complete, implementation pending

## Architecture

### Core Components (To Be Implemented)

```
custom_components/daily_brief/
├── components/
│   ├── aggregator.py      # RSS/API content fetching & deduplication
│   ├── selector.py         # AI-powered article scoring & selection
│   ├── generator.py        # LLM script generation
│   ├── audio.py           # TTS & audio processing (FFmpeg)
│   └── player.py          # Media player integration
├── ai/
│   ├── llm.py             # LLM abstraction layer
│   ├── tts.py             # TTS abstraction layer
│   ├── prompts.py         # Prompt templates
│   └── providers/         # OpenAI, Anthropic, Google, Ollama, ElevenLabs, Piper
├── feeds/
│   ├── parser.py          # RSS/Atom parsing (feedparser, BeautifulSoup)
│   ├── dedup.py           # Content deduplication
│   └── content_packs.py   # Pre-configured feed collections
├── storage/
│   ├── database.py        # SQLite operations
│   └── models.py          # Data models
└── frontend/
    └── daily_brief_card.js # Lovelace dashboard card
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

### Testing

```bash
# Run all tests
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

### AI Provider Abstraction

All LLM and TTS providers implement base interfaces (`LLMProvider`, `TTSProvider`) allowing:
- Easy provider switching (OpenAI ↔ Anthropic ↔ Google ↔ Ollama)
- Automatic fallback on errors
- Cost estimation and limits

### Cost Management

- Target: <$0.50 per briefing (configurable limits)
- Free option: Ollama (local LLM) + Piper (local TTS)
- Premium: GPT-4 + ElevenLabs (~$0.45/briefing)
- Budget: GPT-4o-mini + OpenAI TTS (~$0.18/briefing)

### Content Packs

Pre-configured feed collections in YAML format:
- Technology (English/Chinese)
- World News
- Business & Finance
- Science & Health
- Developer News
- Community packs supported

### Services (Home Assistant)

```yaml
# Generate briefing
daily_brief.generate:
  briefing_type: morning  # morning, evening, on_demand
  force_refresh: false
  article_count: 10

# Play briefing
daily_brief.play:
  media_player: media_player.bedroom_speaker
  briefing_date: "2025-10-13"

# Provide feedback
daily_brief.feedback:
  article_id: "abc123"
  feedback_type: "like"  # like, dislike, skip
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
  "documentation": "https://github.com/Ryan-Guo123/ha-daily-brief",
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

## Important Notes

### Privacy & Security

- All user data stored locally in Home Assistant (SQLite)
- Optional anonymous telemetry (opt-in only, no personal data)
- API keys stored in Home Assistant secrets
- No data uploaded to cloud except API calls to LLM/TTS providers

### Performance Targets

- Generation time: <5 minutes for complete briefing
- Memory usage: <500MB during generation
- Concurrent generations: Support 3+ simultaneous
- Storage: Auto-cleanup old briefings (configurable retention 1-30 days)

### Error Handling

- API failures: Automatic retry with exponential backoff, fallback to alternative provider
- Network issues: Cache feeds for 1 hour, use cached data if fresh fetch fails
- Rate limits: Respect provider limits, queue requests if needed
- User feedback: Clear error messages in UI, log details for debugging

## Development Roadmap

**MVP (v0.1.0):** RSS aggregation, basic AI selection (OpenAI), script generation, OpenAI TTS, manual trigger, dashboard card

**Beta (v0.2.0):** Scheduled automation, multiple TTS providers, feedback system, 10+ content packs, multi-language

**v1.0.0:** Local LLM (Ollama), advanced personalization, mobile app integration, podcast feed, comprehensive tests

**Future:** Social media integration, voice cloning, conversational mode, multi-user profiles, enterprise features

## Testing Strategy

### Coverage Requirements

- Unit tests: >80% coverage
- Integration tests: Full briefing generation flow
- Performance tests: Generation time <5min, cost <$0.50, memory <500MB
- User acceptance: Manual testing of complete user workflows

### Test Data

Use fixture files in `tests/fixtures/`:
- `sample_feeds.xml` - Mock RSS feeds
- `sample_articles.json` - Pre-parsed articles
- `mock_api_responses/` - LLM/TTS API mocks

## References

- [Home Assistant Developer Docs](https://developers.home-assistant.io)
- [HACS Documentation](https://hacs.xyz)
- [PRD Document](./PRD-Home%20Assistant%20Daily%20Brief.md) - Complete product requirements
