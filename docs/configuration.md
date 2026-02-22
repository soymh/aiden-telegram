# Configuration Guide

This guide covers all configuration options for Aiden Telegram Bot. The bot uses environment variables stored in a `.env` file for configuration.

## Configuration File Setup

1. Copy the example configuration:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings

## Required Configuration

### API Keys

```env
# OpenAI API Key (required)
# Get from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=sk-your-api-key-here

# Telegram Bot Token (required)
# Get from @BotFather on Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Model Selection
# Options: gpt-4o, gemini-2.0-flash, gpt-4-turbo, o1, etc.
OPENAI_MODEL=gemini-2.0-flash
```

### User Access Control

```env
# Admin User IDs (comma-separated)
# These users have special privileges and no budget restrictions
# Find your ID via @getidsbot on Telegram
ADMIN_USER_IDS=123456789,987654321

# Allowed User IDs (comma-separated)
# Users who can interact with the bot
# Use * to allow everyone (default)
ALLOWED_TELEGRAM_USER_IDS=123456789,111222333
```

## Optional Configuration Sections

### Budget Management

Control spending with flexible budget periods:

```env
# Budget Period: daily, monthly, or all-time
BUDGET_PERIOD=monthly

# User Budgets (comma-separated, matches ALLOWED_TELEGRAM_USER_IDS order)
# Use * for no limits
USER_BUDGETS=10.0,20.0,5.0

# Guest Budget (for group chat users not in allowed list)
GUEST_BUDGET=5.0

# Pricing Configuration
INPUT_TOKEN_PRICE=0.00015      # Per 1K tokens
OUTPUT_TOKEN_PRICE=0.0006      # Per 1K tokens
CACHED_TOKEN_PRICE=0.000075    # Per 1K tokens
IMAGE_PRICES=0.016,0.018,0.02  # For 256x256, 512x512, 1024x1024
TRANSCRIPTION_PRICE=0.006      # Per minute
VISION_TOKEN_PRICE=0.01        # Per 1K tokens
TTS_PRICES=0.015,0.030         # For tts-1, tts-1-hd
KOKORO_TTS_PRICE=0.015         # Per request
```

### Feature Toggles

Enable/disable specific bot capabilities:

```env
ENABLE_QUOTING=true                    # Enable message quoting
ENABLE_IMAGE_GENERATION=true           # Enable /image command
ENABLE_TTS_GENERATION=true            # Enable /tts command
ENABLE_TRANSCRIPTION=true              # Enable voice message transcription
ENABLE_VISION=true                     # Enable image analysis
ENABLE_FUNCTIONS=true                  # Enable plugin/function calls
SHOW_PLUGINS_USED=false                # Show which plugins were used
SHOW_USAGE=false                       # Show token usage after responses
```

### Conversation Settings

```env
# Assistant personality/prompt
ASSISTANT_PROMPT=You are Aiden, a helpful AI assistant.

# Maximum tokens in response
MAX_TOKENS=1200

# Maximum messages to keep in history
MAX_HISTORY_SIZE=15

# Conversation timeout in minutes
MAX_CONVERSATION_AGE_MINUTES=180

# Temperature (0.0-2.0): Higher = more random
TEMPERATURE=1.0

# Penalties (-2.0 to 2.0)
PRESENCE_PENALTY=0.0
FREQUENCY_PENALTY=0.0

# Number of response choices (1 for single response)
N_CHOICES=1

# Stream responses in real-time
STREAM=true
```

### Image Generation

#### DALL-E Configuration

```env
# DALL-E Model: dall-e-2 or dall-e-3
IMAGE_MODEL=dall-e-3

# Image Quality (dall-e-3 only): standard or hd
IMAGE_QUALITY=hd

# Image Style (dall-e-3 only): vivid or natural
IMAGE_STYLE=vivid

# Image Size
# DALL-E 2: 256x256, 512x512, 1024x1024
# DALL-E 3: 1024x1024 only
IMAGE_SIZE=1024x1024

# Image Format in Telegram: photo or document
IMAGE_FORMAT=photo

# OpenAI Media API (if using separate endpoint)
OPENAI_MEDIA_BASE_URL=https://api.openai.com/v1
OPENAI_MEDIA_API_KEY=your-media-api-key
```

#### FLUX Configuration (Alternative Image Generator)

```env
# Enable FLUX image generation
FLUX_GEN=false

# FLUX API Configuration
FLUX_API_KEY=your-flux-api-key
FLUX_BASE_URL=https://api.together.xyz/v1/images/generations
FLUX_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell-Free
```

### Vision Configuration

```env
# Vision Model: gpt-4o or gemini-2.0-flash
VISION_MODEL=gpt-4o

# Vision Detail Level: low, high, or auto
VISION_DETAIL=low

# Maximum tokens for vision responses
VISION_MAX_TOKENS=300

# Default prompt for image interpretation
VISION_PROMPT=What is in this image?

# Enable follow-up questions about images
ENABLE_VISION_FOLLOW_UP_QUESTIONS=true

# Ignore vision requests in group chats
IGNORE_GROUP_VISION=true
```

### Text-to-Speech Configuration

#### OpenAI TTS

```env
# TTS Model: tts-1 or tts-1-hd
TTS_MODEL=tts-1

# Voice: alloy, echo, fable, onyx, nova, shimmer
TTS_VOICE=alloy
```

#### KokoroTTS (Advanced TTS)

```env
# KokoroTTS API Configuration
KOKORO_TTS_BASE_URL=http://127.0.0.1:3000/api/v1
KOKORO_TTS_API_KEY=your-kokoro-api-key

# Kokoro Voice Options
KOKORO_TTS_VOICE=af_heart

# Kokoro Model
KOKORO_TTS_MODEL=model_q8f16
```

#### Voice Message Handling

```env
# Reply with transcript only (no ChatGPT response)
VOICE_REPLY_WITH_TRANSCRIPT_ONLY=true

# Trigger phrases that bypass transcript-only mode
# Separate multiple phrases with semicolons
VOICE_REPLY_PROMPTS=Hi bot;Hey bot;Hi chat;Hey chat
```

### Whisper Transcription

```env
# Custom prompt to improve transcription accuracy
# Useful for specific names, technical terms, etc.
WHISPER_PROMPT=This is a conversation about technology and AI.
```

### Plugin Configuration

```env
# Enable specific plugins (comma-separated)
# Available: weather, wolfram, ddg_web_search, ddg_image_search, 
# dice, youtube_audio_extractor, deepl_translate, gtts_text_to_speech,
# auto_tts, kokoro_tts, whois, webshot, iplocation, telegram_moderator,
# web_extract, arxiv_search, arxiv_extract, telegram_extract,
# image_gen, reddit_helper, youtube_downloader, media_relay,
# message_sender, vision, pdf_extract

PLUGINS=ddg_web_search,weather,dice,youtube_downloader,kokoro_tts

# Maximum consecutive function calls
FUNCTIONS_MAX_CONSECUTIVE_CALLS=10
```

#### Plugin-Specific Environment Variables

```env
# WolframAlpha
WOLFRAM_APP_ID=your-wolfram-app-id

# DeepL Translation
DEEPL_API_KEY=your-deepl-api-key

# WorldTimeAPI
WORLDTIME_DEFAULT_TIMEZONE=America/New_York

# Reddit Integration
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret

# Telegram Moderator
BOT_TOKEN_MODERATOR=your-moderator-bot-token

# MCPO Server (for dynamic plugins)
MCPO_BASE_URL=http://localhost:8000
MCPO_API_KEY=top-secret
```

### Group Chat Configuration

```env
# Only respond to messages starting with this keyword
GROUP_TRIGGER_KEYWORD=!bot

# Ignore transcriptions in group chats
IGNORE_GROUP_TRANSCRIPTIONS=true

# Allow users to join channel before using bot
ALLOW_GROUP_USERS=false

# Require channel membership
REQUIRED_CHANNEL_ID=@your_channel
```

### Channel & Moderation

```env
# Channel ID for posting
CHANNEL_ID=@your_channel_username

# Group ID for moderation
GROUP_ID=-1001234567890

# Moderator bot token (separate bot for moderation)
BOT_TOKEN_MODERATOR=moderator-bot-token

# Moderator trigger keyword
MODERATOR_TRIGGER_KEYWORD=/moderate
```

### Proxy Configuration

```env
# Single proxy for both OpenAI and Telegram
PROXY=http://localhost:8080

# Or separate proxies
OPENAI_PROXY=http://openai-proxy:8080
TELEGRAM_PROXY=http://telegram-proxy:8080
```

### Localization

```env
# Bot Language
# Available: en, de, ru, tr, it, fi, es, id, nl, zh-cn, zh-tw, 
# vi, fa, pt-br, uk, ms, uz, ar, he
BOT_LANGUAGE=en

# Custom bot signature
BOT_SIGNATURE=By AidenBot
```

### Logging & Debugging

```env
# Rate limit for admin DMs (in hours)
ADMIN_DM_RATELIMIT=5
```

## MCPO Server Configuration

The bot integrates with [MCPO](https://github.com/open-webui/mcpo) to dynamically load plugins from MCP servers.

### What is MCPO?

MCPO (Model Context Protocol OpenAPI) exposes MCP tools as OpenAPI-compatible HTTP servers, allowing the bot to:
- Dynamically discover available functions
- Auto-generate function specifications
- Call remote tools via HTTP

### Setting Up MCPO

1. **Install MCPO**:
```bash
# Using uv (recommended)
uvx mcpo --port 8000 --api-key "top-secret" -- your_mcp_server_command

# Or via pip
pip install mcpo
mcpo --port 8000 --api-key "top-secret" -- your_mcp_server_command

# Or via Docker
docker run -p 8000:8000 ghcr.io/open-webui/mcpo:main --api-key "top-secret" -- your_mcp_server_command
```

2. **Example MCP Servers**:
```bash
# Time server
uvx mcpo --port 8000 --api-key "top-secret" -- uvx mcp-server-time --local-timezone=America/New_York

# Memory server
uvx mcpo --port 8001 --api-key "top-secret" -- npx -y @modelcontextprotocol/server-memory

# Multiple servers via config file
mcpo --config config.json --hot-reload
```

3. **MCPO Config File** (`config.json`):
```json
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"]
    },
    "mcp_sse": {
      "type": "sse",
      "url": "http://127.0.0.1:8001/sse",
      "headers": {
        "Authorization": "Bearer token"
      }
    }
  }
}
```

4. **Configure Bot for MCPO**:
```env
# MCPO Server URL
MCPO_BASE_URL=http://localhost:8000

# MCPO API Key (must match MCPO server)
MCPO_API_KEY=top-secret
```

### How MCPO Integration Works

1. **Discovery**: Bot connects to MCPO server at startup
2. **Schema Fetch**: Retrieves OpenAPI schema for all available tools
3. **Function Registration**: Converts OpenAPI specs to OpenAI function format
4. **Dynamic Calling**: When model requests a function, bot calls MCPO endpoint
5. **Result Processing**: Returns results back to the model

### Benefits of MCPO

- **No Code Changes**: Add new tools without modifying bot code
- **Standard Protocol**: Uses OpenAPI, widely supported
- **Hot Reload**: Update tools without restarting bot
- **Secure**: API key authentication, isolated execution
- **Scalable**: Run tools on separate servers/machines

## Advanced Configuration

### Custom API Endpoints

Use compatible APIs instead of OpenAI:

```env
# Custom OpenAI-compatible API
OPENAI_BASE_URL=https://your-api.com/v1
OPENAI_API_KEY=your-custom-api-key
```

### TogetherAI Models

```env
# Use TogetherAI models
OPENAI_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
OPENAI_BASE_URL=https://api.together.xyz/v1
```

### Google AI Studio

```env
# Use Google Gemini models
OPENAI_MODEL=gemini-2.0-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

## Configuration Validation

After editing `.env`, validate your configuration:

```bash
# Check if all required variables are set
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OPENAI_API_KEY:', '✓' if os.getenv('OPENAI_API_KEY') else '✗'); print('TELEGRAM_BOT_TOKEN:', '✓' if os.getenv('TELEGRAM_BOT_TOKEN') else '✗')"
```

## Environment Variable Precedence

Environment variables are loaded in this order:
1. System environment variables
2. `.env` file in project root
3. Default values in code

System environment variables take precedence over `.env` file values.

## Troubleshooting Configuration

### Common Issues

**Bot doesn't start:**
- Check `.env` file exists and is properly formatted
- Verify no spaces around `=` signs
- Ensure quotes are properly closed

**Plugins not loading:**
- Verify plugin name spelling in `PLUGINS` variable
- Check required API keys for specific plugins
- Review logs for initialization errors

**Budget not working:**
- Ensure `BUDGET_PERIOD` is set correctly
- Verify `USER_BUDGETS` matches user count
- Check usage tracker logs

**MCPO plugins not discovered:**
- Verify MCPO server is running
- Check `MCPO_BASE_URL` and `MCPO_API_KEY`
- Test MCPO endpoint: `curl http://localhost:8000/docs`

## Next Steps

- 📖 Read about [Available Commands](commands.md)
- 🔌 Explore the [Plugin System](plugins.md)
- 💰 Learn about [Usage Tracking](usage_tracking.md)
