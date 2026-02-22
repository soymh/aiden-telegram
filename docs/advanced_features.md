# Advanced Features Guide

Aiden Telegram Bot includes powerful advanced features for administrators and power users.

## Admin Controls

### Admin Configuration

Admins are specified in `.env`:

```env
ADMIN_USER_IDS=123456789,987654321
```

**Admin Privileges:**
- No budget restrictions
- Access to admin commands
- Can modify bot configuration
- Can manage users
- Can broadcast messages
- Can moderate groups

### Admin Commands

#### Configuration Management

```bash
# View all configs
/config

# Get specific config
/config get OPENAI_MODEL

# Set config value
/config set MAX_TOKENS 2000

# Reset to default
/config reset ASSISTANT_PROMPT
```

#### User Management

```bash
# List all users
/users

# Allow user
/allow @username

# Disallow user
/disallow @username

# View user stats
/userstats @username
```

#### Broadcasting

```bash
# Send message to all users
/broadcast Your message here

# With confirmation
/broadcast Please confirm maintenance tonight
```

## Moderation System

### Telegram Moderator Plugin

Advanced moderation for group chats.

**Configuration:**
```env
PLUGINS=telegram_moderator
BOT_TOKEN_MODERATOR=your-moderator-bot-token
GROUP_ID=-1001234567890
```

**Features:**
- Auto-moderate inappropriate content
- Ban/warn users
- Delete messages
- Log violations
- Custom rules

**Commands:**
```bash
# Enable moderation
/moderate

# Ban user
/ban @username reason

# Warn user
/warn @username reason

# Delete message
/delete (reply to message)

# View logs
/modlogs
```

### Super Access Mode

For built-in moderation functions:

```python
# In code, super_access=True allows moderator plugin
await helper.get_chat_response(..., super_access=True)
```

Enables moderator bot to:
- Access channel/group IDs
- Use moderator bot token
- Perform admin actions

## Channel Integration

### Channel Posting

Post messages to Telegram channels:

**Configuration:**
```env
CHANNEL_ID=@your_channel
```

**Usage:**
```bash
# Forward to channel
forward it : <message>

# Or via command
/send_to_channel <message>
```

### Channel Membership Requirement

Require users to join channel before using bot:

```env
REQUIRED_CHANNEL_ID=@your_channel
ALLOW_GROUP_USERS=false
```

**Flow:**
1. User sends message
2. Bot checks channel membership
3. If not member → Show join request
4. After joining → Allow bot usage

### Join Request Handling

```python
# Callback for join requests
async def join_request_callback(update, context):
    # Process join request
    pass
```

## Prompt Templates

Create reusable prompt templates.

### Managing Prompts

```bash
# Create new prompt
/newprompt

# Delete prompt
/delprompt <name>

# List all prompts
/getprompts
```

### Using Prompts

```bash
# Use saved prompt
/useprompt <name> <input>

# Example
/useprompt translator Hello world
```

### Prompt Variables

Templates support variables:
- `{input}` - User input
- `{username}` - User's name
- `{date}` - Current date

**Example Template:**
```
Name: translator
Template: Translate this from English to Spanish: {input}
```

## Group Chat Features

### Trigger Keywords

Only respond to messages starting with keyword:

```env
GROUP_TRIGGER_KEYWORD=!bot
```

**Usage:**
```
!bot What's the weather?
!bot /image a cat
```

### Ignore Settings

Disable specific features in groups:

```env
IGNORE_GROUP_TRANSCRIPTIONS=true
IGNORE_GROUP_VISION=true
```

### Guest Users

Users not in `ALLOWED_TELEGRAM_USER_IDS` are guests:

```env
GUEST_BUDGET=5.0  # Limit for guests
ALLOW_GROUP_USERS=false  # Block guests entirely
```

## Inline Mode

Use bot in any chat via `@mention`.

### Setup

Enable in BotFather:
```
/setinline @yourbot
```

### Usage

```
@yourbot What is AI?
@yourbot /image a cat
@yourbot Translate "hello" to French
```

### Inline Results

Bot returns inline results that can be sent to any chat.

## Message Relay

Forward and process messages across chats.

### Media Relay Plugin

```env
PLUGINS=media_relay
```

**Features:**
- Forward media with processing
- Cross-chat communication
- Media transformation

### Message Sender Plugin

Send templated messages:

```env
PLUGINS=message_sender
```

**Usage:**
```bash
/send_message template_name arg1 arg2
```

## Rate Limiting

### Admin DM Rate Limit

Limit how often admins can be DM'd:

```env
ADMIN_DM_RATELIMIT=5  # Hours
```

### User Rate Limits

Control request frequency per user:

```python
# In code
rate_limit = {
    'user_id': user_id,
    'requests_per_minute': 10,
    'requests_per_hour': 100
}
```

### API Rate Limiting

Handle provider rate limits:

```python
# Automatic retry with backoff
@retry(
    reraise=True,
    retry=retry_if_exception_type(openai.RateLimitError),
    wait=wait_fixed(20),
    stop=stop_after_attempt(3)
)
```

## Logging System

### Per-User Logs

Each user has dedicated log file:

```
user_logs/<user_id>/user_<user_id>.log
```

**Log Contents:**
- All user interactions
- Token usage
- Errors and exceptions
- Plugin executions

### Main Bot Logs

```
logs.log
bot/logs.log
```

**Contents:**
- System events
- Plugin initialization
- Global errors
- Startup/shutdown

### Log Levels

Configure logging verbosity:

```python
logger.setLevel(logging.INFO)  # Options: DEBUG, INFO, WARNING, ERROR
```

### Log Analysis

```bash
# View recent errors
grep "ERROR" logs.log | tail -20

# User activity
cat user_logs/*/user_*.log | wc -l

# Plugin usage
grep "plugin" logs.log | sort | uniq -c
```

## Broadcast System

Send announcements to all users.

### Text Broadcast

```bash
/broadcast Maintenance scheduled for tonight at 2 AM UTC
```

**Process:**
1. Admin sends `/broadcast`
2. Bot asks for confirmation
3. Admin confirms
4. Message sent to all users

### Media Broadcast

Send media to all users:

```bash
# Reply to media with /broadcast
[Attach image] → /broadcast Check out our new feature!
```

### Broadcast Scheduling

Schedule future broadcasts:

```bash
/schedule_broadcast 2024-01-15 14:00 "New year special!"
```

### Broadcast Stats

View broadcast statistics:

```bash
/broadcast_stats
```

Shows:
- Messages sent
- Delivery rate
- Failed sends

## Custom Configurations

### Model Switching

Change models dynamically:

```bash
# For current chat
/model gpt-4-turbo

# For specific task
/model_for_task vision gemini-2.0-flash
```

### Budget Overrides

Set custom budgets per user:

```bash
/set_budget @username 20.0
```

### Feature Toggles

Enable/disable features per chat:

```bash
/toggle vision  # Enable/disable vision in current chat
/toggle image_gen
/toggle tts
```

## Webhook Integration

### Flask Server

Bot runs Flask server for webhooks:

```python
# In main.py
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # Process webhook
    pass
```

### Keep-Alive

Automatic health checks:

```python
# Ping endpoint every 5 minutes
def keep_alive():
    while True:
        requests.get('http://localhost:5000/health')
        time.sleep(300)
```

### API Endpoints

Custom API routes:

```
GET  /health       - Health check
POST /send_message - Send message via API
GET  /stats        - Get bot statistics
```

## Data Export

### Export User Data

```bash
/export_data @username
```

Exports:
- Conversation history
- Usage statistics
- Preferences

### Backup System

Automated backups:

```bash
# Backup to file
/backup create

# Restore from backup
/backup restore filename.json
```

## Security Features

### API Key Encryption

Encrypt sensitive data:

```python
from cryptography.fernet import Fernet

cipher = Fernet(encryption_key)
encrypted = cipher.encrypt(api_key.encode())
```

### Access Control

Fine-grained permissions:

```python
permissions = {
    'use_bot': True,
    'use_image_gen': admin_only,
    'use_broadcast': admin_only,
    'moderate': moderator_only
}
```

### Audit Logging

Track admin actions:

```python
log_admin_action(admin_id, action, target, details)
```

## Performance Optimization

### Caching

Cache frequently accessed data:

```env
ENABLE_CACHING=true
CACHE_TTL=3600  # 1 hour
```

### Async Operations

All I/O operations are async:

```python
async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### Connection Pooling

Reuse connections:

```python
http_client = httpx.AsyncClient(
    limits=httpx.Limits(max_keepalive_connections=10)
)
```

## Monitoring & Alerts

### Health Checks

Monitor bot status:

```bash
/health
```

Returns:
- Uptime
- Response time
- Error rate
- Active users

### Alert Configuration

Set up alerts:

```env
ALERT_ON_ERROR=true
ALERT_THRESHOLD=5  # Alert after 5 errors
ALERT_CHAT_ID=123456789  # Where to send alerts
```

### Metrics Collection

Track key metrics:
- Requests per minute
- Average response time
- Error rates
- Token usage trends

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 💰 Track usage in [Usage Tracking](usage_tracking.md)
