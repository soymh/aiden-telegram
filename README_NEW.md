# Aiden Telegram Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: GPL 2.0](https://img.shields.io/badge/License-GPL%202.0-brightgreen.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

**A powerful, feature-rich AI Telegram bot with multi-model support, advanced plugins, and comprehensive administration tools.**

🌟 **Forked from** [n3d1117/chatgpt-telegram-bot](https://github.com/n3d1117/chatgpt-telegram-bot)  
📍 **Maintained at** [soymh/aiden-telegram](https://github.com/soymh/aiden-telegram)

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/soymh/aiden-telegram.git
cd aiden-telegram
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python bot/main.py
```

Or use Docker:
```bash
docker compose up -d
```

## ✨ Key Features

### 🤖 Multi-Model AI Support
- **OpenAI**: GPT-3.5, GPT-4, GPT-4o, GPT-4 Turbo, O1, O1-mini
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Pro/Flash
- **TogetherAI**: Llama 3.3, Qwen 2.5 Coder
- **Vision Models**: GPT-4o, Gemini 2.0 Flash for image analysis
- **Image Generation**: DALL-E 2/3, FLUX.1 (free alternative)

### 🔌 Extensive Plugin System (30+ Built-in + MCP Support)
- **Search & Information**: Web search (DuckDuckGo), Weather, WolframAlpha, ArXiv papers
- **Media Tools**: YouTube downloader, Reddit helper, Web extractor, PDF processor
- **Text Processing**: DeepL translation, Multiple TTS engines (OpenAI, Kokoro, Google)
- **Utilities**: Whois lookup, IP location, World time, Web screenshots, LaTeX rendering
- **Telegram Integration**: Message extraction, Group moderation, Media relay
- **MCP Plugins**: Dynamic plugin loading via [MCPO](https://github.com/open-webui/mcpo) server

### 💬 Advanced Conversation Management
- Automatic conversation summarization to save tokens
- Configurable history size and timeout
- Per-chat conversation tracking
- Vision follow-up questions (continue discussing images)
- Custom prompt templates

### 📊 Comprehensive Usage Tracking
- Per-user and per-chat token tracking
- Multi-service cost calculation (chat, images, TTS, transcription, vision)
- Flexible budget periods: daily, monthly, all-time
- Guest budgets for group chats
- Detailed statistics via `/stats` command

### 🎨 Rich Media Capabilities
- **Image Generation**: DALL-E 3 (HD quality), FLUX (free)
- **Text-to-Speech**: OpenAI TTS (6 voices), KokoroTTS (advanced), Google TTS
- **Voice Transcription**: Whisper model with custom prompts
- **Vision Analysis**: Multi-image support, OCR, chart interpretation

### 👥 Group Chat & Admin Features
- Trigger keywords for group responses
- Advanced moderation tools with separate moderator bot
- Channel integration and membership requirements
- Broadcast messaging to all users
- User management (allow/disallow)
- Configuration management via commands
- Per-user logging system

### 🌍 Localization
- 20+ supported languages
- AI-powered JSON translation tool
- Community-contributed translations
- RTL language support

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting_started.md) | Installation and setup guide |
| [Configuration Guide](docs/configuration.md) | All configuration options explained |
| [Available Commands](docs/commands.md) | Complete command reference |
| [Plugin System](docs/plugins.md) | Built-in and MCP plugins guide |
| [Model Support](docs/models.md) | Supported AI models and selection |
| [Usage Tracking](docs/usage_tracking.md) | Budget management and monitoring |
| [TTS Guide](docs/tts_guide.md) | Text-to-speech features |
| [Vision Guide](docs/vision_guide.md) | Image analysis capabilities |
| [Image Generation](docs/image_generation.md) | DALL-E and FLUX usage |
| [Advanced Features](docs/advanced_features.md) | Admin tools and power features |
| [Translation Tools](docs/translation_tools.md) | Localization guide |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

## 🎯 What Can It Do?

### Chat & Assist
- Answer questions on any topic
- Help with writing, coding, analysis
- Multi-turn conversations with context
- Voice message transcription and response

### Media Creation
```bash
/image a sunset over mountains --provider dalle
/tts Hello world --voice nova
/vision Analyze this image
```

### Information & Research
```bash
/arxiv quantum computing
/extract https://example.com/article
/whois google.com
/ip 8.8.8.8
```

### Productivity
- Translate text to 50+ languages
- Extract audio from YouTube videos
- Summarize PDF documents
- Take website screenshots
- Get weather forecasts worldwide

### Group Management
- Auto-moderate inappropriate content
- Require channel membership
- Forward messages to channels
- Broadcast announcements

## ⚙️ Configuration Highlights

### Required Settings
```env
OPENAI_API_KEY=sk-your-key-here
TELEGRAM_BOT_TOKEN=your-bot-token
OPENAI_MODEL=gemini-2.0-flash
ADMIN_USER_IDS=your-telegram-id
ALLOWED_TELEGRAM_USER_IDS=your-telegram-id
```

### Popular Options
```env
# Budgets
BUDGET_PERIOD=monthly
USER_BUDGETS=10.0
GUEST_BUDGET=5.0

# Features
ENABLE_IMAGE_GENERATION=true
ENABLE_TTS_GENERATION=true
ENABLE_VISION=true
ENABLE_FUNCTIONS=true

# Plugins
PLUGINS=weather,ddg_web_search,youtube_downloader,kokoro_tts,arxiv_search

# MCPO Integration
MCPO_BASE_URL=http://localhost:8000
MCPO_API_KEY=top-secret
```

See [`.env.example`](.env.example) for all options and [Configuration Guide](docs/configuration.md) for detailed explanations.

## 🔌 Available Plugins

### Communication & Search
- `ddg_web_search` - DuckDuckGo web search
- `ddg_image_search` - Image and GIF search
- `weather` - Current weather and 7-day forecast
- `wolfram` - WolframAlpha computational engine

### Media & Content
- `youtube_downloader` - Download videos or extract audio
- `reddit_helper` - Reddit post and comment extraction
- `arxiv_search` / `arxiv_extract` - Academic paper search and summaries
- `web_extract` - Smart webpage content extraction
- `pdf_extract` - PDF document processing

### Text & Translation
- `deepl_translate` - Professional translation service
- `auto_tts` - OpenAI text-to-speech
- `kokoro_tts` - Advanced TTS with custom voices
- `gtts_text_to_speech` - Google TTS

### Utilities
- `dice` - Roll dice (Telegram native)
- `whois` - Domain name lookup
- `iplocation` - IP geolocation
- `worldtimeapi` - World time queries
- `webshot` - Website screenshots
- `latex_to_image` - Render LaTeX equations

### Telegram Integration
- `telegram_moderator` - Advanced group moderation
- `telegram_extract` - Message and media extraction
- `media_relay` - Cross-chat media forwarding
- `image_gen` - DALL-E and FLUX image generation
- `vision_plugin` - Image analysis with vision models

### MCP Plugins
Dynamic plugins loaded from MCPO servers - add new capabilities without code changes!

## 📊 Model Comparison

| Model | Best For | Speed | Cost |
|-------|----------|-------|------|
| `gpt-4o` | All-around performance | Fast | Medium |
| `gemini-2.0-flash` | Vision tasks, speed | Very Fast | Low |
| `o1` | Complex reasoning | Slow | High |
| `gpt-3.5-turbo` | Cost-effective chat | Very Fast | Very Low |
| `gpt-4o-mini` | Balanced performance | Fast | Low |

See [Model Support Guide](docs/models.md) for complete list and details.

## 💰 Cost Management

The bot includes comprehensive cost tracking and budget controls:

- **Per-user budgets**: Set individual spending limits
- **Period-based tracking**: Daily, monthly, or all-time
- **Multi-service costs**: Track chat, images, TTS, vision separately
- **Guest limits**: Control costs in group chats
- **Real-time stats**: `/stats` command shows usage breakdown

Example costs (OpenAI):
- Chat (GPT-4o): ~$0.005 per 1K tokens
- Image (DALL-E 3): $0.040-0.080 per image
- TTS: $0.015 per 1K characters
- FLUX images: Free!

## 🛠️ Installation Options

### From Source
```bash
git clone https://github.com/soymh/aiden-telegram.git
cd aiden-telegram
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python bot/main.py
```

### Docker Compose
```bash
docker compose up -d
docker compose logs -f  # View logs
```

### Docker Manual
```bash
docker build -t aiden-telegram .
docker run -it --env-file .env aiden-telegram
```

### Pre-built Images
```bash
# Docker Hub
docker pull soymh/aiden-telegram:latest
docker run -it --env-file .env soymh/aiden-telegram

# Or GitHub Container Registry
docker pull ghcr.io/soymh/aiden-telegram:latest
```

## 🔧 MCPO Integration

Aiden Bot supports [MCPO (Model Context Protocol OpenAPI)](https://github.com/open-webui/mcpo) for dynamic plugin loading:

### Setup MCPO Server
```bash
# Install and run MCPO
uvx mcpo --port 8000 --api-key "top-secret" -- your_mcp_command

# Example: Memory server
uvx mcpo --port 8000 --api-key "secret" -- npx -y @modelcontextprotocol/server-memory
```

### Configure Bot
```env
MCPO_BASE_URL=http://localhost:8000
MCPO_API_KEY=top-secret
```

The bot automatically discovers and loads MCP plugins!

## 📈 What's New (vs Original)

### Enhanced Model Support
- 40+ models from OpenAI, Google, TogetherAI
- Automatic capability detection
- Model-specific optimizations

### Advanced Plugin Architecture
- MCP plugin loader for dynamic integrations
- 10+ new built-in plugins
- Plugin cost tracking

### Improved Vision
- Multiple vision models (GPT-4o, Gemini)
- Follow-up question support
- Multi-image processing

### Multiple TTS Engines
- OpenAI TTS, KokoroTTS, Google TTS
- Voice customization
- Character-based pricing

### Enhanced Administration
- Broadcast messaging
- Channel integration
- Advanced moderation tools
- Per-user logging

### Better Cost Control
- Multi-service tracking
- Flexible budget periods
- Detailed usage reports

### Translation Tools
- AI-powered JSON translation
- 20+ languages supported
- Progressive translation with state saving

## 🤝 Contributing

Contributions are welcome! Areas of interest:

- **Translations**: Help localize the bot to more languages
- **Plugins**: Create new integrations
- **Features**: Implement requested enhancements
- **Bug Fixes**: Squash bugs and improve stability
- **Documentation**: Improve guides and examples

See [GitHub Issues](https://github.com/soymh/aiden-telegram/issues) for open tasks.

## 📖 Additional Resources

- **Original Project**: [n3d1117/chatgpt-telegram-bot](https://github.com/n3d1117/chatgpt-telegram-bot)
- **OpenAI API**: [Documentation](https://platform.openai.com/docs)
- **Telegram Bot API**: [Documentation](https://core.telegram.org/bots/api)
- **MCPO**: [GitHub Repository](https://github.com/open-webui/mcpo)
- **Budget Manual**: [Discussion Thread](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184)
- **Translation Guide**: [Contribute Translations](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219)

## ⚠️ Disclaimer

This is a community-maintained project and is not affiliated with OpenAI, Telegram, or Google. Use at your own risk.

## 📄 License

This project is released under the GPL 2.0 license. See the [LICENSE](LICENSE) file for details.

## 💡 Quick Tips

1. **Start Simple**: Begin with `gpt-3.5-turbo` or `gpt-4o-mini` for testing
2. **Set Budgets**: Configure spending limits before deploying
3. **Enable Plugins Gradually**: Add plugins as needed to avoid complexity
4. **Monitor Usage**: Check `/stats` regularly
5. **Use FLUX for Testing**: Free image generation for experimentation
6. **Join Community**: Ask questions in Discussions

---

**Ready to get started?** Check out the [Getting Started Guide](docs/getting_started.md)!

**Need help?** Browse the [Documentation](docs/README.md) or ask in [Discussions](https://github.com/soymh/aiden-telegram/discussions).
