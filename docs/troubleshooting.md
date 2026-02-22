# Troubleshooting Guide

Common issues and solutions for Aiden Telegram Bot.

## Installation Issues

### Python Version Error

**Error:** `Python 3.9+ required`

**Solution:**
```bash
# Check Python version
python --version

# If outdated, install Python 3.9+
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.9 python3.9-venv

# macOS:
brew install python@3.9

# Windows: Download from python.org
```

### Dependency Installation Fails

**Error:** `Could not find a version that satisfies the requirement...`

**Solutions:**
1. Upgrade pip:
```bash
pip install --upgrade pip
```

2. Clear cache:
```bash
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

3. Install system dependencies:
```bash
# For ffmpeg (audio/video processing)
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS

# For build tools
sudo apt install build-essential  # Linux
xcode-select --install          # macOS
```

### Virtual Environment Issues

**Error:** `ModuleNotFoundError`

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

## Configuration Issues

### Bot Doesn't Start

**Symptoms:** No response, silent failure

**Checklist:**
1. Verify `.env` file exists:
```bash
ls -la .env
```

2. Check required variables:
```bash
grep -E "^(OPENAI_API_KEY|TELEGRAM_BOT_TOKEN)=" .env
```

3. Validate `.env` format:
```env
# Correct:
OPENAI_API_KEY=sk-xxx

# Wrong (spaces around =):
OPENAI_API_KEY = sk-xxx

# Wrong (quotes issues):
OPENAI_API_KEY="sk-xxx  # Missing closing quote
```

4. Check logs:
```bash
tail -50 logs.log
```

### Invalid API Key

**Error:** `Invalid API key` or `Authentication failed`

**Solutions:**
1. Verify API key in OpenAI dashboard: https://platform.openai.com/api-keys
2. Check for typos (no spaces, correct characters)
3. Ensure key has sufficient credits
4. Test key with curl:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Bot Token Invalid

**Error:** `Unauthorized` or `Invalid bot token`

**Solutions:**
1. Get new token from @BotFather
2. Update `TELEGRAM_BOT_TOKEN` in `.env`
3. Restart bot
4. Test with simple request:
```bash
curl "https://api.telegram.org/botYOUR_TOKEN/getMe"
```

## Runtime Issues

### Bot Doesn't Respond to Messages

**Possible Causes & Solutions:**

1. **User Not Allowed:**
```env
# Add your user ID
ALLOWED_TELEGRAM_USER_IDS=your_user_id
```

Find your ID: Message @getidsbot

2. **Budget Reached:**
```bash
/stats  # Check remaining budget
```

3. **Plugin Errors:**
```bash
# Disable all plugins temporarily
PLUGINS=
# Restart bot
```

4. **Network Issues:**
```bash
# Test connectivity
ping api.openai.com
ping api.telegram.org
```

5. **Check Logs:**
```bash
tail -f logs.log
```

### Slow Responses

**Causes & Solutions:**

1. **Model Too Slow:**
```env
# Switch to faster model
OPENAI_MODEL=gpt-3.5-turbo
# or
OPENAI_MODEL=gpt-4o-mini
```

2. **Large Context:**
```env
# Reduce history size
MAX_HISTORY_SIZE=10
```

3. **Network Latency:**
```env
# Use proxy if needed
PROXY=http://your-proxy:8080
```

4. **High Token Count:**
```env
# Limit response length
MAX_TOKENS=800
```

5. **Server Load:**
- Wait and retry
- Check OpenAI status: https://status.openai.com

### API Rate Limit Errors

**Error:** `Rate limit reached` or `429 Too Many Requests`

**Solutions:**

1. **Wait and Retry:**
- Bot automatically retries after 20 seconds
- Maximum 3 attempts

2. **Reduce Frequency:**
```env
# Space out requests
REQUEST_DELAY=2  # Seconds between requests
```

3. **Upgrade Plan:**
- Check OpenAI tier limits
- Consider upgrading to higher tier

4. **Distribute Load:**
- Use multiple API keys (future feature)
- Implement queuing system

### Memory Issues

**Error:** `MemoryError` or bot crashes

**Solutions:**

1. **Reduce History:**
```env
MAX_HISTORY_SIZE=10
MAX_CONVERSATION_AGE_MINUTES=60
```

2. **Clear Cache:**
```bash
# Remove cached data
rm -rf .cache/
```

3. **Increase System Resources:**
- Close other applications
- Add swap space (Linux)
- Restart system

4. **Optimize Images:**
```env
# Use smaller image sizes
IMAGE_SIZE=512x512
```

## Feature-Specific Issues

### Image Generation Fails

**Errors & Solutions:**

1. **"Content policy violation":**
   - Revise prompt to avoid restricted content
   - Remove violent/adult themes
   - Avoid copyrighted characters

2. **"Image generation failed":**
```bash
# Check configuration
/config get IMAGE_MODEL
/config get IMAGE_QUALITY

# Try DALL-E 2 instead of DALL-E 3
IMAGE_MODEL=dall-e-2
```

3. **Timeout:**
```env
# Reduce image size
IMAGE_SIZE=512x512
```

4. **Cost Too High:**
```env
# Use FLUX (free)
FLUX_GEN=true
/image prompt --provider flux
```

### Vision Not Working

**Issues & Solutions:**

1. **Vision Disabled:**
```env
ENABLE_VISION=true
VISION_MODEL=gpt-4o
```

2. **Unsupported Model:**
```env
# Use vision-capable model
VISION_MODEL=gpt-4o
# or
VISION_MODEL=gemini-2.0-flash
```

3. **Image Format:**
- Convert to JPEG or PNG
- Ensure file size < 20 MB
- Remove animated GIFs

4. **Group Chat Ignored:**
```env
IGNORE_GROUP_VISION=false  # Enable in groups
```

### TTS Not Working

**Problems & Fixes:**

1. **TTS Disabled:**
```env
ENABLE_TTS_GENERATION=true
```

2. **No Audio Sent:**
- Check file size limits
- Verify media API endpoint
- Test with short text first

3. **Voice Not Available:**
```env
# Use available voices
TTS_VOICE=alloy  # Options: alloy, echo, fable, onyx, nova, shimmer
```

4. **KokoroTTS Connection Failed:**
```bash
# Check Kokoro server
curl http://localhost:3000/api/v1

# Restart Kokoro server
systemctl restart kokoro-tts  # If using systemd
```

### Transcription Fails

**Issues:**

1. **ffmpeg Missing:**
```bash
# Install ffmpeg
sudo apt install ffmpeg  # Linux
brew install ffmpeg      # macOS
choco install ffmpeg     # Windows
```

2. **File Too Large:**
- Split audio into smaller parts
- Compress audio file
- Use shorter messages

3. **Unsupported Format:**
- Convert to MP3 or WAV
- Use Telegram voice message format

4. **Language Issues:**
```env
# Set language hint
WHISPER_PROMPT=This conversation is in Spanish
```

### Plugin Issues

**Common Problems:**

1. **Plugin Not Loading:**
```bash
# Check plugin name spelling
/config get PLUGINS

# Verify dependencies
pip list | grep plugin_name

# Check logs for errors
grep "plugin" logs.log
```

2. **Plugin Function Not Called:**
```env
# Ensure functions enabled
ENABLE_FUNCTIONS=true
```

3. **API Key Missing:**
```env
# Set required keys
WOLFRAM_APP_ID=xxx
DEEPL_API_KEY=xxx
REDDIT_CLIENT_ID=xxx
```

4. **MCP Plugins Not Discovered:**
```bash
# Test MCPO server
curl http://localhost:8000/docs

# Check MCPO configuration
/config get MCPO_BASE_URL
/config get MCPO_API_KEY
```

## Budget & Usage Issues

### Budget Not Resetting

**Problem:** Budget should reset but doesn't

**Solutions:**

1. **Check Period Setting:**
```env
BUDGET_PERIOD=monthly  # or daily, all-time
```

2. **Timezone Issue:**
- Resets happen at UTC midnight
- Check system timezone:
```bash
timedatectl  # Linux
date         # macOS/Linux
```

3. **Manual Reset:**
```bash
# Admin reset user
/reset_stats @username

# Reset all users
/reset_stats all
```

### Incorrect Cost Calculation

**Problem:** Costs don't match expectations

**Debug Steps:**

1. **Check Pricing Config:**
```env
INPUT_TOKEN_PRICE=0.00015
OUTPUT_TOKEN_PRICE=0.0006
```

2. **Verify Model:**
```bash
/config get OPENAI_MODEL
```

3. **Compare with Provider:**
- Check OpenAI usage dashboard
- Compare token counts
- Verify pricing tier

4. **Review Logs:**
```bash
grep "cost" user_logs/*/user_*.log
```

### Stats Not Updating

**Problem:** Usage not being tracked

**Solutions:**

1. **Check Permissions:**
```bash
# Ensure write access
chmod -R 755 user_logs/
```

2. **Disk Space:**
```bash
df -h  # Check available space
```

3. **Corrupted State:**
```bash
# Backup and reset
cp usage_logs.json usage_logs.json.bak
rm usage_logs.json
# Restart bot to create fresh file
```

## Group Chat Issues

### Bot Doesn't Respond in Groups

**Causes & Fixes:**

1. **Not Added to Group:**
- Add bot to group
- Grant necessary permissions

2. **Privacy Mode Enabled:**
- In BotFather: `/setprivacy`
- Disable privacy mode for your bot

3. **Trigger Keyword Required:**
```env
GROUP_TRIGGER_KEYWORD=!bot
# Then use: !bot your message
```

4. **Guest Access Blocked:**
```env
ALLOW_GROUP_USERS=true
GUEST_BUDGET=5.0
```

### Moderation Not Working

**Problem:** Moderator plugin fails

**Solutions:**

1. **Missing Moderator Bot:**
```env
BOT_TOKEN_MODERATOR=moderator_bot_token
```

2. **Wrong Group ID:**
```bash
# Get group ID via @getidsbot
GROUP_ID=-1001234567890
```

3. **Plugin Not Enabled:**
```env
PLUGINS=telegram_moderator
```

## Database & Storage Issues

### Usage File Corrupted

**Error:** JSON decode errors

**Solution:**
```bash
# Backup corrupted file
cp usage_logs.json usage_logs.json.corrupt

# Create new file from backup or reset
echo '{}' > usage_logs.json

# Restart bot
```

### Log Files Too Large

**Problem:** Logs consuming disk space

**Solutions:**

1. **Rotate Logs:**
```bash
# Manual rotation
mv logs.log logs.log.old
touch logs.log
```

2. **Reduce Logging:**
```python
# In code, change log level
logger.setLevel(logging.WARNING)  # Instead of INFO
```

3. **Automated Cleanup:**
```bash
# Cron job to clean old logs
0 0 * * * find /path/to/logs -name "*.log" -mtime +7 -delete
```

## Network & Proxy Issues

### Connection Timeouts

**Error:** `Connection timed out` or `Request timeout`

**Solutions:**

1. **Use Proxy:**
```env
PROXY=http://proxy-server:8080
# Or separate proxies
OPENAI_PROXY=http://openai-proxy:8080
TELEGRAM_PROXY=http://telegram-proxy:8080
```

2. **Increase Timeout:**
```python
# In code
timeout = httpx.Timeout(60.0)  # Increase from default
```

3. **Check Firewall:**
```bash
# Allow required ports
sudo ufw allow out 443/tcp  # HTTPS
```

4. **DNS Issues:**
```bash
# Use public DNS
# Edit /etc/resolv.conf
nameserver 8.8.8.8
nameserver 1.1.1.1
```

### SSL/Certificate Errors

**Error:** `SSL certificate verify failed`

**Solutions:**

1. **Update Certificates:**
```bash
# Ubuntu/Debian
sudo apt install --reinstall ca-certificates

# macOS
pip install --upgrade certifi
```

2. **Disable Verification (NOT RECOMMENDED):**
```python
# Only for testing
verify_ssl=False
```

## Docker Issues

### Container Won't Start

**Error:** Container exits immediately

**Solutions:**

1. **Check Logs:**
```bash
docker compose logs
```

2. **Verify .env:**
```bash
docker compose config  # Validate configuration
```

3. **Rebuild:**
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Volume Mount Issues

**Problem:** Data not persisting

**Solutions:**

1. **Check Paths:**
```yaml
# docker-compose.yml
volumes:
  - ./usage_logs:/app/usage_logs
  - ./user_logs:/app/user_logs
```

2. **Permissions:**
```bash
sudo chown -R 1000:1000 usage_logs user_logs
```

3. **SELinux/AppArmor:**
```bash
# Temporarily disable for testing
sudo setenforce 0  # SELinux
```

## Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Review logs for errors
3. ✅ Verify configuration
4. ✅ Test with minimal setup
5. ✅ Document steps to reproduce

### Information to Provide

When reporting issues:

1. **System Info:**
   - OS and version
   - Python version
   - Bot version/commit

2. **Configuration:**
   - Relevant `.env` settings (hide secrets)
   - Enabled plugins

3. **Logs:**
   - Error messages
   - Last 50 lines of logs

4. **Steps Taken:**
   - What you tried
   - What worked/didn't work

### Where to Get Help

1. **GitHub Issues:** https://github.com/soymh/aiden-telegram/issues
2. **Discussions:** https://github.com/soymh/aiden-telegram/discussions
3. **Original Project:** https://github.com/n3d1117/chatgpt-telegram-bot

## Debugging Tools

### Enable Debug Mode

```env
LOG_LEVEL=DEBUG
```

### Test Commands

```bash
# Test OpenAI connection
python test_api.py

# Test Telegram bot
curl "https://api.telegram.org/botTOKEN/getMe"

# Check configuration
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('OPENAI_API_KEY', 'Not set'))"
```

### Monitor in Real-Time

```bash
# Follow logs
tail -f logs.log

# Monitor resource usage
watch -n 1 'ps aux | grep python'

# Network monitoring
iftop  # Requires installation
```

## Next Steps

- 📚 Review [Configuration Guide](configuration.md)
- 🔧 Check [Commands Reference](commands.md)
- 💬 Ask in [Discussions](https://github.com/soymh/aiden-telegram/discussions)
