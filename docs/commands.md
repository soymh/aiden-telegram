# Available Commands

This document lists all available commands for Aiden Telegram Bot.

## Basic Commands

### Chat & Interaction

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Start the bot and show welcome message | `/start` |
| `/help` | Show help message with all commands | `/help` |
| `/reset` | Reset conversation history | `/reset` |
| `/resend` | Resend last response (if failed) | `/resend` |

### Information & Statistics

| Command | Description | Example |
|---------|-------------|---------|
| `/stats` | View your usage statistics and costs | `/stats` |
| `/budget` | Check remaining budget | `/budget` |

### Media Generation

| Command | Description | Example |
|---------|-------------|---------|
| `/image` | Generate an image from text prompt | `/image a sunset over mountains` |
| `/tts` | Convert text to speech | `/tts Hello world` |
| `/vision` | Analyze/interpret an image | Send image with `/vision` caption |

## Admin Commands

These commands are only available to users listed in `ADMIN_USER_IDS`.

### User Management

| Command | Description | Example |
|---------|-------------|---------|
| `/config` | View and modify bot configuration | `/config get USER_BUDGETS` |
| `/users` | List all users and their status | `/users` |
| `/allow @username` | Grant bot access to a user | `/allow @john` |
| `/disallow @username` | Revoke bot access from a user | `/disallow @john` |

### Broadcasting

| Command | Description | Example |
|---------|-------------|---------|
| `/broadcast` | Send message to all users | `/broadcast Maintenance tonight` |

### Moderation

| Command | Description | Example |
|---------|-------------|---------|
| `/moderate` | Enable moderation mode for group | `/moderate` |
| `/dmadmin` | Send content privately to admins | Reply with `/dmadmin` to message |

### Prompt Management

| Command | Description | Example |
|---------|-------------|---------|
| `/newprompt` | Create a new prompt template | `/newprompt` |
| `/delprompt` | Delete a prompt template | `/delprompt` |
| `/getprompts` | List all saved prompt templates | `/getprompts` |

## Plugin-Specific Commands

Some plugins add their own commands. These vary based on enabled plugins.

### Weather Plugin (`weather`)
- No specific commands - triggered automatically when discussing weather

### Web Search (`ddg_web_search`)
- No specific commands - triggered automatically for search queries

### YouTube Downloader (`youtube_downloader`)
- Triggered by sending YouTube links
- Can use `/ytdl <url>` for video download
- Can use `/ytaudio <url>` for audio extraction

### ArXiv Search (`arxiv_search`)
- `/arxiv <query>` - Search academic papers
- `/paper <id>` - Get paper summary

### Image Generation (`image_gen`)
- `/image <prompt>` - Generate image with DALL-E or FLUX

### Text-to-Speech

#### Auto TTS (`auto_tts`)
- Automatic TTS for responses

#### KokoroTTS (`kokoro_tts`)
- Enhanced TTS with multiple voices
- Configure via `/config` command

### Reddit Helper (`reddit_helper`)
- Triggered by Reddit links
- Extracts post content and comments

### Web Extractor (`web_extract`)
- `/extract <url>` - Extract content from webpage

### Whois Plugin (`whois`)
- `/whois <domain>` - Lookup domain information

### IP Location (`iplocation`)
- `/ip <address>` - Get geographical info for IP

### LaTeX Renderer (`latex_to_image`)
- `/latex <equation>` - Render LaTeX equation as image

### Web Screenshot (`webshot`)
- `/screenshot <url>` - Take screenshot of website

### Dice Roller (`dice`)
- `/dice` - Roll a dice (Telegram native)

### World Time (`worldtimeapi`)
- `/time <location>` - Get current time anywhere

### DeepL Translate (`deepl_translate`)
- `/translate <text>` - Translate text
- Or auto-detect translation requests

### PDF Processor (`pdf_extract`)
- Send PDF file to extract and summarize content

## Inline Mode Commands

Use the bot in any chat by typing `@yourbotname <query>`.

### Inline Query Examples

1. **General Query**:
   ```
   @yourbotname What is quantum computing?
   ```

2. **Image Generation**:
   ```
   @yourbotname /image a cute cat
   ```

3. **Web Search**:
   ```
   @yourbotname Latest AI news
   ```

## Voice Message Commands

Send voice messages with optional trigger phrases:

### Default Behavior
- Voice messages are transcribed automatically
- Bot responds to the transcription

### With Transcript Only
If `VOICE_REPLY_WITH_TRANSCRIPT_ONLY=true`:
- Bot only shows transcription
- No ChatGPT response

### Override with Trigger Phrases
Start voice message with any phrase from `VOICE_REPLY_PROMPTS`:
- "Hi bot, what's the weather?"
- "Hey chat, tell me a joke"
- "Hi bot, explain quantum physics"

## Group Chat Commands

In group chats, additional behaviors apply:

### Trigger Keyword Mode
If `GROUP_TRIGGER_KEYWORD` is set:
```
!bot What's the weather today?
```

### Moderator Commands
When moderation is enabled:
- Auto-moderate inappropriate content
- Manage user permissions
- Log violations

## Message Triggers

The bot also responds to certain message types without commands:

### Automatic Triggers

1. **Text Messages**: Processed as chat prompts
2. **Images**: Analyzed with vision model (if enabled)
3. **Voice Messages**: Transcribed (if enabled)
4. **YouTube Links**: Offer download options
5. **Reddit Links**: Extract content
6. **Web URLs**: Offer to extract content
7. **PDF Files**: Summarize content

### Bypass Triggers

To send a message without triggering bot response:
- Start with `/ignore` (if implemented)
- Use in chats where bot is not allowed

## Command Syntax

### Arguments

Commands can accept arguments:

```
/command arg1 arg2 arg3
```

### Flags

Some commands support flags:

```
/tts Hello --voice alloy
/image Sunset --provider flux
/vision Analyze this --model gemini
```

### Multi-word Arguments

Use quotes for multi-word arguments:

```
/image "A beautiful sunset over mountain range"
```

## Response Formats

### Text Responses
- Markdown formatting supported
- Code blocks with syntax highlighting
- Links and inline elements

### Image Responses
- Sent as photo (default)
- Or as document (if `IMAGE_FORMAT=document`)

### Audio Responses
- TTS sent as voice message
- Format: MP3 or Opus

### File Responses
- Documents sent with captions
- Size limits apply (Telegram: 50MB max)

## Rate Limits

### User Rate Limits
- Configurable per user
- Default: Based on budget settings

### Admin DM Rate Limit
- Controlled by `ADMIN_DM_RATELIMIT`
- Default: 5 hours between DMs

### Global Rate Limits
- API rate limits from providers
- Bot-level throttling if needed

## Error Responses

Common error messages:

| Error | Meaning | Solution |
|-------|---------|----------|
| "Budget reached" | Usage limit exceeded | Wait for reset or increase budget |
| "Not allowed" | User not in allowed list | Admin must grant access |
| "Invalid command" | Unknown command | Check `/help` for valid commands |
| "API error" | External service issue | Try again later |
| "Timeout" | Request took too long | Simplify query or retry |

## Tips & Tricks

### 1. Quick Stats
Use `/stats` frequently to monitor usage

### 2. Reset Conversations
Use `/reset` to start fresh and save tokens

### 3. Efficient Prompts
Be specific in your requests for better results

### 4. Plugin Combinations
Combine plugins for powerful workflows:
- Search → Extract → Summarize
- Image → Vision → Describe

### 5. Voice Efficiency
Use trigger phrases to get full responses to voice messages

### 6. Group Chat Etiquette
Set `GROUP_TRIGGER_KEYWORD` to avoid spam in groups

### 7. Admin Broadcasts
Use `/broadcast` sparingly and for important announcements only

### 8. Custom Prompts
Create reusable prompt templates with `/newprompt`

## Command Permissions

| Command Type | Regular Users | Admins |
|--------------|---------------|--------|
| Basic Commands | ✅ | ✅ |
| Stats/Budget | ✅ | ✅ |
| Media Generation | ✅ (if enabled) | ✅ |
| User Management | ❌ | ✅ |
| Broadcasting | ❌ | ✅ |
| Configuration | ❌ | ✅ |
| Moderation | ❌ | ✅ |

## Keyboard Shortcuts

Telegram supports command shortcuts:

1. Type `/` to see all available commands
2. Tap command to insert it
3. Add arguments and send

## Next Steps

- ⚙️ Learn about [Configuration](configuration.md)
- 🔌 Explore [Plugins](plugins.md)
- 💰 Understand [Usage Tracking](usage_tracking.md)
