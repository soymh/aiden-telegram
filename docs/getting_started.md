# Getting Started with Aiden Telegram Bot

This guide will walk you through setting up and running your own AI-powered Telegram bot.

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.9 or higher** installed on your system
2. A **Telegram account**
3. An **OpenAI API key** (or compatible API provider)
4. **Git** (for cloning the repository)

## Step 1: Obtain Required API Keys

### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow the prompts to name your bot and choose a username
4. BotFather will give you a **bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. **Save this token** - you'll need it in the configuration

### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. **Copy and save the key** - it will only be shown once
5. Ensure you have API credits available

### Optional: Additional API Keys

Depending on which features you want to enable:

- **WolframAlpha**: For math and science queries ([Get App ID](https://products.wolframalpha.com/simple-api/documentation))
- **Spotify**: For music integration ([Get Credentials](https://developer.spotify.com/dashboard/))
- **DeepL**: For translations ([Get API Key](https://www.deepl.com/pro-api?cta=header-pro-api))
- **KokoroTTS**: For advanced TTS (self-hosted or API service)
- **Reddit**: For Reddit integration ([Get Credentials](https://www.reddit.com/prefs/apps))
- **Flux API**: For alternative image generation

## Step 2: Install the Bot

### Option A: From Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/soymh/aiden-telegram.git
cd aiden-telegram

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Option B: Using Docker (Recommended for Production)

```bash
# Clone the repository
git clone https://github.com/soymh/aiden-telegram.git
cd aiden-telegram

# Build and run with Docker Compose
docker compose up -d

# Or pull pre-built image
docker pull soymh/aiden-telegram:latest
docker run -it --env-file .env soymh/aiden-telegram
```

## Step 3: Configure the Bot

### Create Configuration File

```bash
# Copy the example configuration
cp .env.example .env
```

### Edit Configuration

Open `.env` in a text editor and configure the required parameters:

#### Required Configuration

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gemini-2.0-flash

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# User Access Control
ADMIN_USER_IDS=your_telegram_user_id
ALLOWED_TELEGRAM_USER_IDS=your_telegram_user_id
```

**Finding Your Telegram User ID:**
- Message [@getidsbot](https://t.me/getidsbot) on Telegram
- It will reply with your user ID (a number like: 123456789)

#### Optional but Recommended

```env
# Bot Language
BOT_LANGUAGE=en

# Enable Features
ENABLE_QUOTING=true
ENABLE_IMAGE_GENERATION=true
ENABLE_TTS_GENERATION=true
ENABLE_TRANSCRIPTION=true
ENABLE_VISION=true
ENABLE_FUNCTIONS=true

# Budget Management
BUDGET_PERIOD=monthly
USER_BUDGETS=*
GUEST_BUDGET=100.0

# Conversation Settings
MAX_HISTORY_SIZE=15
MAX_CONVERSATION_AGE_MINUTES=180
STREAM=true

# Plugins (comma-separated list)
PLUGINS=ddg_web_search,weather,dice,youtube_audio_extractor
```

## Step 4: Run the Bot

### From Source

```bash
# Make sure you're in the project directory
cd aiden-telegram

# Activate virtual environment if not already active
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Start the bot
python bot/main.py
```

### Using Docker

```bash
# If using docker-compose
docker compose up -d

# View logs
docker compose logs -f

# If using docker directly
docker run -it --env-file .env soymh/aiden-telegram
```

## Step 5: Test the Bot

1. **Open Telegram** and search for your bot by username
2. **Start a chat** and send `/start` or `/help`
3. **Test basic functionality**:
   - Send a text message: "Hello, how are you?"
   - Try a command: `/stats`
   - Test image generation: `/image a cute cat`
   - Test web search: "What's the weather in Tokyo?"

## Step 6: Verify Everything Works

### Check Bot Responses

✅ **Chat Response**: Send "Hello" - should get a friendly response  
✅ **Stats Command**: Send `/stats` - should show usage statistics  
✅ **Help Command**: Send `/help` - should show available commands  

### Check Logs

```bash
# If running from source, check the terminal output
# Look for messages like:
# - "Initialized built-in plugin: weather"
# - "Starting bot polling..."

# If using Docker:
docker compose logs -f
```

### Check Log Files

User-specific logs are stored in:
```
user_logs/<user_id>/user_<user_id>.log
```

Main bot logs:
```
logs.log
bot/logs.log
```

## Common First Steps

### 1. Set Up Admin Access

Add your user ID to `ADMIN_USER_IDS` in `.env`:
```env
ADMIN_USER_IDS=123456789
```

Admins have access to special commands:
- `/broadcast` - Send messages to all users
- `/dmadmin` - DM admins with content
- `/config` - View and modify configuration
- `/moderate` - Moderate group chats

### 2. Enable Desired Plugins

Edit the `PLUGINS` variable in `.env`:
```env
PLUGINS=weather,ddg_web_search,dice,youtube_downloader,arxiv_search,kokoro_tts
```

Restart the bot after changing plugins.

### 3. Configure Budgets (Optional)

Set spending limits to control costs:
```env
BUDGET_PERIOD=monthly
USER_BUDGETS=10.0,20.0,5.0  # Different limits per user
GUEST_BUDGET=5.0            # Limit for group chat guests
```

See [Usage Tracking Guide](usage_tracking.md) for details.

### 4. Customize Bot Behavior

Adjust conversation settings:
```env
ASSISTANT_PROMPT=You are Aiden, a helpful AI assistant.
MAX_HISTORY_SIZE=20
TEMPERATURE=0.7
```

## Troubleshooting

### Bot Doesn't Respond

1. Check if bot is running (look at logs)
2. Verify `TELEGRAM_BOT_TOKEN` is correct
3. Ensure your user ID is in `ALLOWED_TELEGRAM_USER_IDS`
4. Check network connectivity

### API Errors

1. Verify `OPENAI_API_KEY` is correct and has credits
2. Check if model name is valid
3. Review rate limits on your API plan
4. Look at error messages in logs

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Permission Errors

```bash
# On Linux/macOS, ensure proper permissions
chmod +x bot/main.py
```

## Next Steps

- 📚 Read the [Configuration Guide](configuration.md) for detailed options
- 🎮 Explore [Available Commands](commands.md)
- 🔌 Learn about the [Plugin System](plugins.md)
- 💰 Understand [Usage Tracking](usage_tracking.md)

## Getting Help

- **Documentation**: Browse other docs in this folder
- **GitHub Issues**: [Report bugs](https://github.com/soymh/aiden-telegram/issues)
- **Discussions**: [Ask questions](https://github.com/soymh/aiden-telegram/discussions)

---

**Congratulations!** Your Aiden Telegram Bot is now running! 🎉
