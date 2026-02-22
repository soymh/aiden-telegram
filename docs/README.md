# Aiden Telegram Bot Documentation

Welcome to the comprehensive documentation for **Aiden Telegram Bot** - an advanced AI-powered Telegram bot forked from [n3d1117/chatgpt-telegram-bot](https://github.com/n3d1117/chatgpt-telegram-bot) and enhanced with additional features.

**Repository**: [github.com/soymh/aiden-telegram](https://github.com/soymh/aiden-telegram)

## Table of Contents

1. [Getting Started](getting_started.md) - Quick setup guide
2. [Configuration Guide](configuration.md) - Detailed configuration options
3. [Available Commands](commands.md) - All bot commands
4. [Plugin System](plugins.md) - Built-in and MCP plugins
5. [Model Support](models.md) - Supported AI models
6. [Usage Tracking & Budgets](usage_tracking.md) - Cost management
7. [Text-to-Speech Guide](tts_guide.md) - TTS features
8. [Vision Capabilities](vision_guide.md) - Image analysis
9. [Image Generation](image_generation.md) - DALL-E and FLUX
10. [Advanced Features](advanced_features.md) - Admin tools, moderation
11. [Translation Tools](translation_tools.md) - Localization features
12. [Troubleshooting](troubleshooting.md) - Common issues

## What is Aiden Telegram Bot?

Aiden Telegram Bot is a powerful, feature-rich Telegram bot that integrates with multiple AI services to provide:

### Core AI Services

- **Chat Completion**: GPT-3.5, GPT-4, GPT-4o, O1 series, Gemini, and more
- **Vision Models**: Image analysis with GPT-4o and Gemini 2.0 Flash
- **Image Generation**: DALL-E 2/3 and FLUX models
- **Text-to-Speech**: OpenAI TTS, KokoroTTS, Google TTS
- **Audio Transcription**: Whisper model for voice messages
- **Plugin System**: 30+ built-in plugins + MCP (Model Context Protocol) support

### Enhanced Features (Beyond Original)

- **Multi-Provider Support**: OpenAI, Google AI Studio, TogetherAI, Flux
- **Advanced Plugin Architecture**: MCP plugin loader for dynamic integrations
- **Enhanced Vision**: Multiple vision models with follow-up questions
- **Multiple TTS Engines**: OpenAI, Kokoro, Google with voice customization
- **PDF Processing**: Extract and summarize PDF content
- **Media Relay**: Forward and process media across chats
- **Telegram Moderation**: Advanced group moderation tools
- **Message Templates**: Custom prompt templates
- **Broadcast System**: Admin broadcast messaging
- **Channel Integration**: Channel posting and management
- **Enhanced Logging**: Per-user logging system

## Quick Start

### Prerequisites

- Python 3.9+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key (or compatible API)

### Installation

```bash
# Clone the repository
git clone https://github.com/soymh/aiden-telegram.git
cd aiden-telegram

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run the bot
python bot/main.py
```

### Docker Deployment

```bash
# Using Docker Compose
docker compose up -d

# Or using Docker directly
docker pull soymh/aiden-telegram:latest
docker run -it --env-file .env soymh/aiden-telegram
```

## Key Features Overview

### 🤖 Multi-Model Support

Support for 40+ AI models across different providers:

- **OpenAI**: GPT-3.5, GPT-4, GPT-4o, GPT-4 Turbo, O1, O1-mini
- **Google**: Gemini 2.0 Flash, Gemini 2.5 Pro, Gemini 2.5 Flash
- **TogetherAI**: Llama 3.3, Qwen 2.5 Coder
- **Vision**: GPT-4o, Gemini 2.0 Flash
- **Image Gen**: DALL-E 2/3, FLUX.1

### 🔌 Extensive Plugin System

**Built-in Plugins** (30+):
- Web Search (DuckDuckGo)
- Weather Forecasting
- YouTube Downloader
- Reddit Helper
- ArXiv Paper Search
- Image Generation
- Text-to-Speech (Multiple engines)
- Translation (DeepL, Google)
- Whois Domain Lookup
- IP Location
- LaTeX Rendering
- Web Screenshot
- Dice Roller
- And more...

**MCP Plugins**:
- Dynamic plugin loading via Model Context Protocol
- Custom integrations via OpenAPI specs
- Automatic function discovery

### 💬 Conversation Management

- Automatic conversation summarization to save tokens
- Configurable history size (default: 15 messages)
- Conversation age limits (default: 180 minutes)
- Per-chat conversation tracking
- Vision follow-up questions

### 📊 Usage Tracking & Budgets

- **Per-User Tracking**: Track token usage per user
- **Per-Service Costs**: Separate tracking for chat, images, TTS, transcription
- **Budget Periods**: Daily, monthly, or all-time budgets
- **Guest Budgets**: Separate limits for group chat guests
- **Statistics Commands**: `/stats`, `/budget`, `/usage`
- **Admin Controls**: Reset stats, manage user budgets

### 🎨 Image Generation

- **DALL-E 3**: High-quality images with style options
- **FLUX**: Free alternative via TogetherAI
- **Multiple Sizes**: 256x256 to 1024x1024
- **Quality Options**: Standard and HD
- **Style Selection**: Vivid or Natural

### 🗣️ Text-to-Speech

- **OpenAI TTS**: 6 voices (alloy, echo, fable, onyx, nova, shimmer)
- **KokoroTTS**: Advanced local TTS with custom voices
- **Google TTS**: Via gTTS plugin
- **Multiple Formats**: MP3, Opus
- **Character-Based Pricing**: Track costs per character

### 👁️ Vision Capabilities

- **Multiple Models**: GPT-4o, Gemini 2.0 Flash
- **Image Analysis**: Describe, interpret, analyze images
- **Follow-Up Questions**: Continue conversations about images
- **Multi-Image Support**: Process multiple images in one message
- **Detail Levels**: Low, high, or auto

### 🎯 Advanced Features

- **Group Chat Support**: Trigger keywords, ignore transcriptions/vision
- **Inline Queries**: Use bot in any chat via @mention
- **Admin Commands**: Broadcast, user management, config updates
- **Moderation Tools**: Telegram moderator plugin
- **Channel Integration**: Post to channels, forward messages
- **Custom Prompts**: Create, delete, and manage prompt templates
- **Localization**: 20+ languages supported
- **Proxy Support**: Separate proxies for OpenAI and Telegram

## Documentation Navigation

### For End Users
- [Getting Started](getting_started.md) - Setup and basic usage
- [Available Commands](commands.md) - Command reference
- [Usage Tracking](usage_tracking.md) - Monitor your usage

### For Administrators
- [Configuration Guide](configuration.md) - Full configuration options
- [Plugin System](plugins.md) - Enable and configure plugins
- [Advanced Features](advanced_features.md) - Admin tools and moderation

### For Developers
- [Models](models.md) - Model integration details
- [Translation Tools](translation_tools.md) - Add new languages
- [Troubleshooting](troubleshooting.md) - Debug common issues

## Support & Community

- **GitHub Issues**: [Report bugs](https://github.com/soymh/aiden-telegram/issues)
- **Discussions**: [Ask questions](https://github.com/soymh/aiden-telegram/discussions)
- **Original Project**: [n3d1117/chatgpt-telegram-bot](https://github.com/n3d1117/chatgpt-telegram-bot)

## License

This project is released under the GPL 2.0 license. See [LICENSE](../LICENSE) for details.

---

**Ready to get started?** Check out the [Getting Started Guide](getting_started.md)!
