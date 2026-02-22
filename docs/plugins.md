# Plugin System Guide

Aiden Telegram Bot features a powerful plugin system that extends its functionality with third-party services and custom tools.

## Overview

The bot supports two types of plugins:

1. **Built-in Plugins**: Hardcoded Python plugins included in the repository
2. **MCP Plugins**: Dynamically loaded via Model Context Protocol OpenAPI (MCPO)

## Plugin Architecture

### Built-in Plugins

Located in `bot/plugins/` directory, each plugin is a Python class that inherits from the base `Plugin` class.

**Structure:**
```python
from .plugin import Plugin

class MyPlugin(Plugin):
    def get_source_name(self) -> str:
        return "My Plugin"
    
    def get_spec(self) -> [Dict]:
        return [{
            "name": "my_function",
            "description": "What this function does",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "Description"}
                },
                "required": ["param1"]
            }
        }]
    
    async def execute(self, function_name, helper, **kwargs) -> Dict:
        # Implementation here
        return {"result": "Function result"}
```

### MCP Plugins

Dynamically loaded from MCPO servers. The bot:
1. Connects to MCPO server at startup
2. Fetches OpenAPI schema
3. Converts to OpenAI function format
4. Makes functions available to the model

## Available Built-in Plugins

### Communication & Search

#### 1. DuckDuckGo Web Search (`ddg_web_search`)
Search the web using DuckDuckGo.

**Requirements:** None  
**Functions:** `ddg_web_search`  
**Usage:** Ask questions that require web search

**Example:**
```
User: What's the latest news about AI?
Bot: [Uses ddg_web_search to find recent AI news]
```

#### 2. DuckDuckGo Image Search (`ddg_image_search`)
Search for images and GIFs.

**Requirements:** None  
**Functions:** `ddg_image_search`  
**Usage:** Request image searches

**Example:**
```
User: Find pictures of sunsets
Bot: [Returns image search results]
```

#### 3. Weather (`weather`)
Get current weather and 7-day forecast.

**Requirements:** None (uses Open-Meteo API)  
**Functions:** `get_weather`, `get_forecast`  
**Usage:** Ask about weather anywhere

**Example:**
```
User: What's the weather in Tokyo?
Bot: Current weather in Tokyo: 22°C, Partly cloudy...
```

#### 4. WolframAlpha (`wolfram`)
Computational knowledge engine for math, science, and more.

**Requirements:** `WOLFRAM_APP_ID`  
**Functions:** `wolfram_query`  
**Usage:** Complex calculations, scientific queries

**Example:**
```
User: Solve x^2 + 2x - 8 = 0
Bot: [Uses WolframAlpha to solve equation]
```

### Media & Content

#### 5. YouTube Downloader (`youtube_downloader`)
Download YouTube videos or extract audio.

**Requirements:** `pytube` or `yt-dlp`  
**Functions:** `download_video`, `extract_audio`  
**Usage:** Send YouTube links or use commands

**Commands:**
- `/ytdl <url>` - Download video
- `/ytaudio <url>` - Extract audio

**Example:**
```
User: https://youtube.com/watch?v=example
Bot: Would you like to download video or extract audio?
```

#### 6. YouTube Audio Extractor (`youtube_audio_extractor`)
Extract audio from YouTube videos.

**Requirements:** `pytube`  
**Functions:** `extract_youtube_audio`  
**Usage:** Similar to youtube_downloader

#### 7. Reddit Helper (`reddit_helper`)
Interact with Reddit content.

**Requirements:** `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `praw`  
**Functions:** `get_post`, `search_subreddit`, `get_comments`  
**Usage:** Share Reddit links or query Reddit

**Example:**
```
User: [Sends Reddit post link]
Bot: [Extracts post title, content, and top comments]
```

#### 8. ArXiv Search (`arxiv_search`)
Search academic papers on arXiv.

**Requirements:** `arxiv` package  
**Functions:** `search_arxiv`  
**Usage:** Research paper queries

**Commands:**
- `/arxiv <query>` - Search papers
- `/paper <id>` - Get specific paper

**Example:**
```
User: /arxiv transformer attention mechanism
Bot: Found 5 papers related to transformer attention...
```

#### 9. ArXiv Extract (`arxiv_extract`)
Extract and summarize arXiv papers.

**Requirements:** `arxiv` package  
**Functions:** `summarize_paper`  
**Usage:** Get paper summaries

#### 10. Web Extractor (`web_extract`)
Smart extraction of webpage content.

**Requirements:** `beautifulsoup4`  
**Functions:** `extract_webpage`  
**Usage:** Extract main content from URLs

**Commands:**
- `/extract <url>` - Extract content

**Example:**
```
User: /extract https://example.com/article
Bot: [Extracts and summarizes article content]
```

#### 11. PDF Processor (`pdf_extract`)
Extract and summarize PDF content.

**Requirements:** PDF processing libraries  
**Functions:** `process_pdf`, `summarize_pdf`  
**Usage:** Send PDF files to bot

**Example:**
```
User: [Sends PDF file]
Bot: [Extracts text and provides summary]
```

#### 12. Telegram Extract (`telegram_extract`)
Extract and process Telegram messages and media.

**Requirements:** None  
**Functions:** `extract_telegram_message`  
**Usage:** Forward messages for processing

#### 13. Media Relay (`media_relay`)
Forward and process media across chats.

**Requirements:** None  
**Functions:** `relay_media`  
**Usage:** Forward media with processing

### Text Processing & Translation

#### 14. DeepL Translate (`deepl_translate`)
Professional translation service.

**Requirements:** `DEEPL_API_KEY`  
**Functions:** `translate_text`  
**Usage:** Translate between languages

**Example:**
```
User: Translate "Hello world" to Spanish
Bot: "Hola mundo"
```

#### 15. Google TTS (`gtts_text_to_speech`)
Text-to-speech using Google Translate.

**Requirements:** `gtts` package  
**Functions:** `google_tts`  
**Usage:** Alternative TTS option

#### 16. Auto TTS (`auto_tts`)
OpenAI TTS integration.

**Requirements:** OpenAI API key  
**Functions:** `openai_tts`  
**Usage:** High-quality TTS

#### 17. KokoroTTS (`kokoro_tts`)
Advanced TTS with multiple voices.

**Requirements:** `KOKORO_TTS_BASE_URL`, `KOKORO_TTS_API_KEY`  
**Functions:** `kokoro_tts`  
**Voices:** Multiple options (af_heart, etc.)  
**Usage:** Premium TTS quality

**Configuration:**
```env
KOKORO_TTS_BASE_URL=http://localhost:3000/api/v1
KOKORO_TTS_API_KEY=your-api-key
KOKORO_TTS_VOICE=af_heart
```

### Utilities

#### 18. Dice (`dice`)
Roll dice using Telegram's native dice emoji.

**Requirements:** None  
**Functions:** `roll_dice`  
**Usage:** Fun/games in chat

**Command:**
- `/dice` - Roll dice

#### 19. Whois (`whois`)
Domain name lookup.

**Requirements:** `whois` package  
**Functions:** `whois_lookup`  
**Usage:** Check domain registration info

**Command:**
- `/whois example.com`

**Example:**
```
User: /whois google.com
Bot: Domain: google.com
     Registrar: MarkMonitor Inc.
     Created: 1997-09-15
     ...
```

#### 20. IP Location (`iplocation`)
Geographical information for IP addresses.

**Requirements:** `requests`  
**Functions:** `get_ip_location`  
**Usage:** Lookup IP geolocation

**Command:**
- `/ip 8.8.8.8`

**Example:**
```
User: /ip 8.8.8.8
Bot: IP: 8.8.8.8
     Country: United States
     City: Mountain View
     ISP: Google LLC
```

#### 21. WorldTimeAPI (`worldtimeapi`)
Get current time worldwide.

**Requirements:** None  
**Functions:** `get_world_time`  
**Usage:** Check time in different timezones

**Command:**
- `/time Tokyo`

**Configuration:**
```env
WORLDTIME_DEFAULT_TIMEZONE=America/New_York
```

#### 22. Web Screenshot (`webshot`)
Take screenshots of websites.

**Requirements:** None  
**Functions:** `take_screenshot`  
**Usage:** Capture webpage appearance

**Command:**
- `/screenshot https://example.com`

**Example:**
```
User: /screenshot https://github.com
Bot: [Sends screenshot image]
```

#### 23. LaTeX to Image (`latex_to_image`)
Render LaTeX equations as images.

**Requirements:** `matplotlib`  
**Functions:** `render_latex`  
**Usage:** Display mathematical equations

**Command:**
- `/latex \int_0^\infty e^{-x} dx`

**Example:**
```
User: /latex E = mc^2
Bot: [Sends rendered equation image]
```

### Image Generation

#### 24. Image Generator (`image_gen`)
Generate images using DALL-E or FLUX.

**Requirements:** OpenAI API key (DALL-E) or Flux API key  
**Functions:** `generate_image_dalle`, `generate_image_flux`  
**Usage:** Create images from text descriptions

**Command:**
- `/image a sunset over mountains`

**Configuration:**
```env
IMAGE_MODEL=dall-e-3
IMAGE_QUALITY=hd
IMAGE_STYLE=vivid
FLUX_GEN=true  # Enable FLUX as alternative
```

### Vision & Analysis

#### 25. Vision Plugin (`vision_plugin`)
Analyze images using vision models.

**Requirements:** Vision-capable model configured  
**Functions:** `interpret_telegram_image`  
**Usage:** Describe and analyze images

**Usage:**
- Send image with optional caption
- Use `/vision` command

**Example:**
```
User: [Sends image] "What's in this picture?"
Bot: This image shows a beautiful landscape with...
```

### Moderation & Management

#### 26. Telegram Moderator (`telegram_moderator`)
Advanced moderation for Telegram groups.

**Requirements:** `BOT_TOKEN_MODERATOR`  
**Functions:** `moderate_message`, `ban_user`, `warn_user`, `delete_message`  
**Usage:** Automate group moderation

**Command:**
- `/moderate` - Enable moderation mode

**Features:**
- Auto-detect inappropriate content
- User warnings and bans
- Message deletion
- Logging violations

#### 27. Message Plugin (`message_sender`)
Send templated messages.

**Requirements:** None  
**Functions:** `send_message`  
**Usage:** Custom message delivery

## Enabling Plugins

### Method 1: Environment Variable

Edit `.env` file:
```env
PLUGINS=weather,ddg_web_search,dice,youtube_downloader,kokoro_tts
```

Restart the bot after changes.

### Method 2: Configuration Command (Admin Only)

```bash
/config set PLUGINS weather,ddg_web_search,dice
```

### Plugin Dependencies

Some plugins require additional Python packages:

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install specific plugin dependencies
pip install wolframalpha  # For wolfram plugin
pip install spotipy       # For spotify plugin
pip install arxiv         # For arxiv plugins
pip install praw          # For reddit plugin
pip install beautifulsoup4  # For web_extract
pip install yt-dlp        # For youtube_downloader
pip install matplotlib    # For latex_to_image
```

## MCP Plugin Integration

### What are MCP Plugins?

MCP (Model Context Protocol) plugins are dynamically loaded from MCPO servers. They allow you to:
- Add new tools without code changes
- Use community-built integrations
- Hot-reload plugins

### Setting Up MCPO

1. **Install MCPO Server:**
```bash
uvx mcpo --port 8000 --api-key "top-secret" -- your_mcp_command
```

2. **Configure Bot:**
```env
MCPO_BASE_URL=http://localhost:8000
MCPO_API_KEY=top-secret
```

3. **Available MCP Servers:**
- Memory servers
- Time/date servers
- File system servers
- Database servers
- Custom API servers

### Example: Memory MCP Server

```bash
# Start memory server
uvx mcpo --port 8000 --api-key "secret" -- npx -y @modelcontextprotocol/server-memory

# Bot automatically discovers and uses it
```

**Usage:**
```
User: Remember that I like pizza
Bot: [Stores in memory via MCP]
User: What do I like?
Bot: You mentioned you like pizza
```

## Creating Custom Plugins

### Basic Plugin Template

Create `bot/plugins/my_custom_plugin.py`:

```python
import logging
from typing import Dict
from .plugin import Plugin

logger = logging.getLogger(__name__)

class MyCustomPlugin(Plugin):
    """
    Custom plugin description
    """
    
    def get_source_name(self) -> str:
        return "My Custom Plugin"
    
    def get_spec(self) -> [Dict]:
        return [{
            "name": "my_custom_function",
            "description": "Description of what this function does",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_param": {
                        "type": "string",
                        "description": "Description of parameter"
                    }
                },
                "required": ["input_param"]
            }
        }]
    
    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            # Access user info
            user_id = helper.user_id
            username = helper.username
            
            # Get parameters
            input_param = kwargs.get("input_param")
            
            # Your implementation here
            result = await self.do_something(input_param)
            
            return {"result": result}
            
        except Exception as e:
            logger.exception(f"Error in my_custom_function: {e}")
            return {"error": str(e)}
    
    async def do_something(self, param):
        # Your custom logic here
        return f"Processed: {param}"
```

### Registering Your Plugin

Add to `bot/plugin_manager.py`:

```python
from plugins.my_custom_plugin import MyCustomPlugin

# In __init__ method:
plugin_mapping = {
    # ... existing plugins ...
    'my_custom_plugin': MyCustomPlugin,
}
```

Then enable in `.env`:
```env
PLUGINS=my_custom_plugin
```

### Plugin Development Tips

1. **Error Handling:** Always wrap code in try-except blocks
2. **Logging:** Use logger for debugging and monitoring
3. **Async:** Use async/await for I/O operations
4. **Validation:** Validate all input parameters
5. **Rate Limiting:** Implement rate limiting if calling external APIs
6. **Security:** Never expose sensitive data in logs or responses

## Plugin Best Practices

### 1. Minimal Permissions
Only request necessary API permissions

### 2. Error Messages
Provide clear, user-friendly error messages

### 3. Rate Limiting
Respect API rate limits and implement backoff

### 4. Caching
Cache results when appropriate to reduce API calls

### 5. Cost Awareness
Track and report costs for paid APIs

### 6. Documentation
Document all functions and parameters clearly

### 7. Testing
Test plugins thoroughly before deployment

### 8. Monitoring
Log usage and errors for debugging

## Troubleshooting Plugins

### Plugin Not Loading

**Check:**
1. Plugin name in `PLUGINS` variable
2. Required dependencies installed
3. Required environment variables set
4. No syntax errors in plugin code

**Logs:**
```bash
grep "plugin" logs.log
```

### Function Not Called

**Check:**
1. Function spec is correct
2. Model has access to functions (`ENABLE_FUNCTIONS=true`)
3. Function name matches spec
4. Parameters are properly defined

### MCP Plugins Not Discovered

**Check:**
1. MCPO server is running
2. `MCPO_BASE_URL` and `MCPO_API_KEY` correct
3. Test endpoint: `curl http://localhost:8000/docs`
4. Check MCPO server logs

## Plugin Costs & Budgets

Plugins that use external APIs may incur costs:

| Plugin | Cost Factor | Tracking |
|--------|-------------|----------|
| WolframAlpha | API calls | Included in budget |
| DeepL | Characters translated | Included in budget |
| DALL-E | Images generated | Tracked separately |
| TTS | Characters/Audio length | Tracked separately |
| Web Search | API calls (free) | No cost |
| Weather | API calls (free) | No cost |

Monitor usage with `/stats` command.

## Next Steps

- 📚 Read about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 💰 Track usage in [Usage Tracking](usage_tracking.md)
