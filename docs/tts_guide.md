# Text-to-Speech (TTS) Guide

Aiden Telegram Bot supports multiple TTS engines for converting text to natural-sounding speech.

## Overview

The bot supports three TTS providers:

1. **OpenAI TTS** - High-quality voices, fast generation
2. **KokoroTTS** - Advanced local deployment, custom voices
3. **Google TTS (gTTS)** - Free alternative via Google Translate

## OpenAI TTS

### Configuration

```env
# Enable TTS generation
ENABLE_TTS_GENERATION=true

# TTS Model: tts-1 or tts-1-hd
TTS_MODEL=tts-1

# Voice selection: alloy, echo, fable, onyx, nova, shimmer
TTS_VOICE=alloy

# Pricing (per 1K characters)
TTS_PRICES=0.015,0.030  # tts-1, tts-1-hd
```

### Available Voices

| Voice | Gender | Characteristics |
|-------|--------|----------------|
| `alloy` | Neutral | Balanced, clear, versatile |
| `echo` | Male | Warm, deep, authoritative |
| `fable` | Female | Expressive, storytelling |
| `onyx` | Male | Deep, resonant, professional |
| `nova` | Female | Bright, energetic, friendly |
| `shimmer` | Female | Soft, gentle, soothing |

### Usage

#### Command Line

```bash
/tts Hello, this is a test of the text-to-speech system.
```

#### With Voice Selection

```bash
/tts Hello --voice nova
```

#### Automatic TTS

Some plugins can automatically generate TTS responses:

```env
# Auto TTS plugin
PLUGINS=auto_tts
```

### Quality Settings

- **tts-1**: Standard quality, faster, cheaper ($0.015/1K chars)
- **tts-1-hd**: High definition quality, slower, more expensive ($0.030/1K chars)

### Example

```
User: /tts Welcome to Aiden Bot!
Bot: [Sends voice message with audio]
```

## KokoroTTS

### What is KokoroTTS?

KokoroTTS is an advanced open-source TTS engine that offers:
- Higher quality voices
- Local deployment options
- Custom voice training
- Multiple languages
- Better prosody and emotion

### Configuration

```env
# KokoroTTS API Configuration
KOKORO_TTS_BASE_URL=http://127.0.0.1:3000/api/v1
KOKORO_TTS_API_KEY=your-kokoro-api-key

# Voice and Model
KOKORO_TTS_VOICE=af_heart
KOKORO_TTS_MODEL=model_q8f16

# Pricing
KOKORO_TTS_PRICE=0.015
```

### Available Voices

Popular voices:
- `af_heart`: Warm, emotional female
- `af_bella`: Clear, professional female
- `am_adam`: Deep, authoritative male
- `am_michael`: Friendly, casual male

### Setting Up KokoroTTS Server

#### Option 1: Self-Hosted (Recommended)

```bash
# Clone KokoroTTS repository
git clone https://github.com/kokoro-tts/kokoro-tts.git
cd kokoro-tts

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py --port 3000
```

#### Option 2: Docker

```bash
docker run -p 3000:3000 kokorotts/kokoro-tts:latest
```

#### Option 3: Cloud Service

Use a hosted KokoroTTS service and set the base URL accordingly.

### Usage

#### Command with KokoroTTS

```bash
/tts Hello from KokoroTTS! --engine kokoro --voice af_heart
```

#### Default KokoroTTS

Set as default in config:

```env
DEFAULT_TTS_ENGINE=kokoro
KOKORO_TTS_VOICE=af_heart
```

### Advantages Over OpenAI TTS

1. **Cost**: Free if self-hosted
2. **Privacy**: Runs locally, no data sent externally
3. **Customization**: Train custom voices
4. **Quality**: Comparable or better than OpenAI
5. **Control**: Full control over parameters

## Google TTS (gTTS)

### Configuration

```env
# Enable gTTS plugin
PLUGINS=gtts_text_to_speech
```

No API key required (uses Google Translate APIs).

### Usage

```bash
/tts Hello from Google TTS! --engine google
```

### Limitations

- Lower quality than OpenAI/Kokoro
- Rate limits from Google
- No voice customization
- Requires internet connection

### Advantages

- Completely free
- No setup required
- Multiple languages auto-detected

## TTS Commands

### Basic TTS Command

```bash
/tts <text>
```

### Advanced Options

```bash
/tts <text> --voice <voice_name> --engine <engine_name>
```

**Parameters:**
- `text`: The text to convert to speech
- `--voice`: Voice to use (varies by engine)
- `--engine`: TTS engine (`openai`, `kokoro`, `google`)

### Examples

```bash
# OpenAI TTS with default voice
/tts Hello world!

# OpenAI TTS with specific voice
/tts Welcome to our channel! --voice nova

# KokoroTTS with custom voice
/tts This is a high-quality voice --engine kokoro --voice af_bella

# Google TTS
/tts Free TTS from Google --engine google
```

## Voice Message Handling

### Transcription vs TTS Response

Configure how the bot handles voice messages:

```env
# Reply with transcript only (no ChatGPT response)
VOICE_REPLY_WITH_TRANSCRIPT_ONLY=true

# Trigger phrases that bypass transcript-only mode
VOICE_REPLY_PROMPTS=Hi bot;Hey bot;Hi chat;Hey chat
```

### Behavior

**With `VOICE_REPLY_WITH_TRANSCRIPT_ONLY=true`:**
- Voice message → Transcript shown
- No ChatGPT response
- Saves tokens

**With trigger phrase:**
- "Hi bot, what's the weather?" → Full ChatGPT response
- Bypasses transcript-only mode

## TTS in Plugins

### Auto TTS Plugin

Automatically generates TTS for all responses:

```env
PLUGINS=auto_tts
```

**Usage:**
- Bot responds with both text and audio
- Useful for accessibility
- Increases costs

### KokoroTTS Plugin

Advanced TTS with more options:

```env
PLUGINS=kokoro_tts
```

**Features:**
- Multiple voice options
- Emotion control
- Speed/pitch adjustment

### GTTS Plugin

Free TTS option:

```env
PLUGINS=gtts_text_to_speech
```

## Cost Tracking

### OpenAI TTS Costs

Tracked per character:

```
TTS Usage:
- Characters: 3,500
- Model: tts-1
- Cost: $0.053
```

### KokoroTTS Costs

If using cloud service:
```
TTS Usage:
- Requests: 5
- Model: model_q8f16
- Cost: $0.075
```

If self-hosted:
```
TTS Usage:
- Requests: 5
- Cost: $0.00 (self-hosted)
```

### View TTS Stats

```bash
/stats
```

Shows TTS usage breakdown.

## Advanced Features

### Multi-Language Support

All TTS engines support multiple languages:

```bash
# English
/tts Hello, how are you? --lang en

# Spanish
/tts Hola, ¿cómo estás? --lang es

# French
/tts Bonjour, comment allez-vous? --lang fr

# Japanese
/tts こんにちは、お元気ですか？ --lang ja
```

### SSML Support (KokoroTTS)

Advanced control with Speech Synthesis Markup Language:

```bash
/tts <speak>Hello <break time="1s"/>world!</speak> --engine kokoro
```

### Batch TTS

Generate multiple audio files:

```bash
/tts_batch "Hello";"World";"Test" --voice alloy
```

### Audio Format

Configure output format:

```env
# Opus (default, smaller size)
TTS_FORMAT=opus

# MP3 (more compatible)
TTS_FORMAT=mp3

# WAV (highest quality)
TTS_FORMAT=wav
```

## Performance Optimization

### Caching

Cache frequently used TTS responses:

```env
ENABLE_TTS_CACHING=true
TTS_CACHE_TTL=3600  # Cache for 1 hour
```

### Async Generation

TTS generation happens asynchronously to avoid blocking:

```python
# In code
audio = await helper.generate_speech(text)
```

### Size Limits

Telegram has file size limits:
- **Voice messages**: Up to 20 MB
- **Audio files**: Up to 50 MB

For long texts, consider:
- Splitting into multiple messages
- Using lower quality settings
- Truncating text

## Troubleshooting

### TTS Not Working

**Issue:** No audio generated

**Solutions:**
1. Check `ENABLE_TTS_GENERATION=true`
2. Verify API keys are valid
3. Check KokoroTTS server is running
4. Review logs for errors

### Poor Audio Quality

**Issue:** Audio sounds robotic or unclear

**Solutions:**
1. Try different voice
2. Use `tts-1-hd` instead of `tts-1`
3. Switch to KokoroTTS for better quality
4. Check text formatting (remove special chars)

### Slow Generation

**Issue:** TTS takes too long

**Solutions:**
1. Use standard quality (`tts-1`)
2. Reduce text length
3. Check network connectivity
4. Consider self-hosting KokoroTTS

### Voice Not Available

**Issue:** Selected voice not working

**Solutions:**
1. Verify voice name spelling
2. Check engine supports that voice
3. Try alternative voice
4. Update KokoroTTS if self-hosted

### API Errors

**Issue:** OpenAI API errors

**Solutions:**
1. Check API key validity
2. Verify sufficient credits
3. Check rate limits
4. Review OpenAI status page

## Best Practices

### 1. Choose Right Engine

- **Production**: OpenAI TTS or KokoroTTS
- **Testing**: Google TTS (free)
- **Privacy**: Self-hosted KokoroTTS
- **Cost-sensitive**: Self-hosted KokoroTTS

### 2. Optimize Text

- Keep messages concise
- Remove unnecessary punctuation
- Use proper capitalization
- Avoid special characters

### 3. Voice Selection

- Match voice to content type
- Use consistent voice for branding
- Test multiple voices
- Consider audience preferences

### 4. Monitor Costs

- Track TTS usage regularly
- Set budgets for TTS
- Cache common responses
- Use free alternatives when possible

### 5. Accessibility

- Provide text alternatives
- Allow users to disable TTS
- Offer voice choices
- Consider hearing-impaired users

## Integration Examples

### Podcast Generation

```bash
# Generate podcast intro
/tts "Welcome to Tech Talk, your daily tech news podcast!" --voice nova
```

### Audiobook Creation

```bash
# Chapter narration
/tts "Chapter 1: The Beginning..." --voice echo --engine kokoro
```

### Notification System

```bash
# Alert message
/tts "Attention: New message received!" --voice shimmer
```

### Language Learning

```bash
# Pronunciation guide
/tts "Bonjour" --lang fr --voice af_bella
```

## Future Features

Planned TTS enhancements:
- [ ] Real-time voice cloning
- [ ] Emotion detection and expression
- [ ] Multi-speaker dialogues
- [ ] Background music integration
- [ ] Voice morphing
- [ ] Offline mode

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 🔌 Explore [Plugins](plugins.md)
