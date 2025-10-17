# Daily Brief for Home Assistant

An AI-powered custom integration that generates personalized daily news briefings from RSS feeds and delivers them via Home Assistant media players.

## ✨ Features

- **AI-Powered Selection**: Uses LLMs (GPT-4o-mini, Claude, etc.) to intelligently select the most important and relevant stories
- **Natural Audio Generation**: Text-to-speech with premium voices (ElevenLabs, OpenAI TTS, or free local Piper)
- **Personalized**: Learns from your feedback to improve story selection over time
- **Multi-Language**: Supports English, Chinese, and other languages
- **Content Packs**: Pre-configured feed collections for Technology, News, Business, Science, and more
- **Privacy-First**: All data stored locally in Home Assistant
- **Flexible Delivery**: Auto-play on schedule, manual trigger, voice commands, or mobile notifications

## 📋 Requirements

- Home Assistant 2024.10.0 or newer
- Python 3.11 or newer
- OpenAI API key (or alternative LLM/TTS provider)
- FFmpeg (for audio processing)

## 🚀 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots (top right) → "Custom repositories"
4. Add repository URL: `https://github.com/yourusername/ha-daily-brief`
5. Category: "Integration"
6. Click "Add"
7. Search for "Daily Brief"
8. Click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Extract to `config/custom_components/daily_brief/`
3. Restart Home Assistant

## ⚙️ Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "Daily Brief"
4. Follow the setup wizard:
   - Select content packs (Technology, News, Business, etc.)
   - Set your interests and preferences
   - Configure AI providers (OpenAI, Anthropic, etc.)
   - Set up TTS provider (OpenAI, ElevenLabs, Piper)
   - Configure schedule and auto-play settings

## 📖 Usage

### Automatic Daily Briefing

Once configured, your briefing will be automatically generated each morning and can optionally auto-play at your specified time.

### Manual Generation

```yaml
# Generate a briefing on demand
service: daily_brief.generate
data:
  briefing_type: on_demand
  article_count: 10
```

### Play Briefing

```yaml
# Play latest briefing
service: daily_brief.play
data:
  media_player: media_player.bedroom_speaker
```

### Automation Example

```yaml
automation:
  - alias: "Morning News Briefing"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.workday
        state: "on"
    action:
      - service: daily_brief.generate_and_play
        data:
          media_player: media_player.kitchen_speaker
          briefing_type: morning
```

## 💰 Cost Estimates

### Budget Configuration
- LLM: GPT-4o-mini (~$0.02/briefing)
- TTS: OpenAI TTS (~$0.15/briefing)
- **Total: ~$0.18/briefing** or **~$5.40/month** (30 briefings)

### Premium Configuration
- LLM: GPT-4o (~$0.15/briefing)
- TTS: ElevenLabs (~$0.30/briefing)
- **Total: ~$0.45/briefing** or **~$13.50/month** (30 briefings)

### Free Configuration
- LLM: Ollama (local, free)
- TTS: Piper (local, free)
- **Total: $0** (only electricity costs)

## 📊 Available Services

- `daily_brief.generate` - Generate a new briefing
- `daily_brief.play` - Play a briefing
- `daily_brief.stop` - Stop playback
- `daily_brief.feedback` - Provide feedback (like/dislike)
- `daily_brief.add_source` - Add custom RSS feed
- `daily_brief.regenerate` - Regenerate with new script/audio

## 🎯 Content Packs

Pre-configured content collections:

- **Technology (English)**: Hacker News, TechCrunch, The Verge, Ars Technica, Wired
- **Technology (Chinese)**: 36氪, 少数派, 爱范儿, V2EX
- **World News**: BBC, Reuters, Al Jazeera, The Guardian
- **Business & Finance**: WSJ, Bloomberg, Financial Times
- **Science & Health**: Nature, Science Daily, New Scientist
- **Developer News**: GitHub Trending, Dev.to, Lobsters

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/ha-daily-brief
cd ha-daily-brief

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Project Structure

```
custom_components/daily_brief/
├── __init__.py              # Integration entry point
├── manifest.json            # Integration metadata
├── const.py                 # Constants
├── coordinator.py           # Data coordinator
├── services.py              # Service handlers
├── components/
│   ├── aggregator.py        # Content fetching
│   ├── selector.py          # AI article selection
│   ├── generator.py         # Script generation
│   └── audio.py             # TTS & audio processing
├── ai/
│   ├── llm.py               # LLM abstraction
│   ├── tts.py               # TTS abstraction
│   ├── prompts.py           # Prompt templates
│   └── providers/           # OpenAI, Anthropic, etc.
├── feeds/
│   ├── parser.py            # RSS parsing
│   ├── dedup.py             # Deduplication
│   └── content_packs.py     # Pre-configured feeds
└── storage/
    ├── database.py          # SQLite operations
    ├── models.py            # Data models
    └── cache.py             # Caching layer
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Home Assistant community for the amazing platform
- RSSHub for aggregating RSS feeds
- OpenAI, ElevenLabs for AI services
- All contributors to this project

## 📞 Support

- **GitHub Issues**: https://github.com/yourusername/ha-daily-brief/issues
- **Home Assistant Forum**: [Discussion Thread]
- **Discord**: [Server Link]

## 🗺️ Roadmap

**v0.1.0 (MVP)** - ✅ Core functionality
- RSS aggregation, AI selection, basic TTS

**v0.2.0 (Beta)** - 🚧 In Progress
- Multiple TTS providers, feedback system, more content packs

**v1.0.0 (Stable)** - 📅 Planned
- Local LLM support (Ollama), mobile app integration, podcast feed

**Future**
- Social media integration, voice cloning, conversational mode, multi-user profiles

## 📸 Screenshots

_Coming soon..._

---

**Made with ❤️ for the Home Assistant community**
