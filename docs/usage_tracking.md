# Usage Tracking & Budget Management

Aiden Telegram Bot includes comprehensive usage tracking and budget management features to help you monitor and control costs.

## Overview

The bot tracks:
- **Token Usage**: Input, output, and cached tokens for chat
- **Image Generation**: DALL-E and FLUX image costs
- **Text-to-Speech**: Character counts and TTS model costs
- **Vision API**: Image analysis token usage
- **Transcription**: Audio/video transcription minutes
- **Plugin Usage**: Costs from external API calls

## Configuration

### Budget Period

Set the time frame for budget tracking:

```env
BUDGET_PERIOD=monthly  # Options: daily, monthly, all-time
```

- **daily**: Resets at midnight UTC
- **monthly**: Resets on the 1st of each month
- **all-time**: Never resets (cumulative tracking)

### User Budgets

Set spending limits per user:

```env
# Single budget for all users
USER_BUDGETS=10.0

# Different budgets per user (matches ALLOWED_TELEGRAM_USER_IDS order)
USER_BUDGETS=5.0,10.0,20.0

# No limits (default)
USER_BUDGETS=*
```

### Guest Budgets

Limit spending for group chat guests (users not in `ALLOWED_TELEGRAM_USER_IDS`):

```env
GUEST_BUDGET=5.0
```

Guests are users in group chats who haven't been explicitly allowed.

### Pricing Configuration

Set custom prices if needed (defaults use OpenAI pricing):

```env
# Chat Token Prices (per 1K tokens)
INPUT_TOKEN_PRICE=0.00015
OUTPUT_TOKEN_PRICE=0.0006
CACHED_TOKEN_PRICE=0.000075

# Image Generation Prices (by size)
IMAGE_PRICES=0.016,0.018,0.02  # 256x256, 512x512, 1024x1024

# Transcription Price (per minute)
TRANSCRIPTION_PRICE=0.006

# Vision Token Price (per 1K tokens)
VISION_TOKEN_PRICE=0.01

# TTS Prices (per 1K characters)
TTS_PRICES=0.015,0.030  # tts-1, tts-1-hd

# KokoroTTS Price (per request)
KOKORO_TTS_PRICE=0.015
```

## Viewing Usage Statistics

### Personal Stats

Use the `/stats` command to view your usage:

```
/stats
```

**Example Output:**
```
📊 Your Usage Statistics

💰 Total spent: $3.45

Today:
- Chat tokens: 1,234 ($0.12)
- Images: 2 ($0.04)
- TTS: 500 chars ($0.01)
- Vision: 450 tokens ($0.005)
Total today: $0.175

This Month:
- Chat tokens: 45,678 ($3.20)
- Images: 10 ($0.20)
- TTS: 2,500 chars ($0.05)
Total this month: $3.45

Budget: $10.00
Remaining: $6.55
```

### Admin Stats

Admins can view all users' stats:

```
/users
```

**Example Output:**
```
👥 All Users

User ID: 123456789 (@john)
- Spent this month: $3.45
- Budget: $10.00
- Status: Active

User ID: 987654321 (@jane)
- Spent this month: $8.90
- Budget: $10.00
- Status: Active

Total users: 2
Total spent: $12.35
```

## Budget Alerts

### Budget Reached

When a user reaches their budget limit:

```
⚠️ Budget Reached

You've reached your budget limit of $10.00 for this period.

Your usage will be restricted until:
- Budget resets (next month)
- Admin increases your budget
- You're granted admin status

Contact an admin if you need assistance.
```

### Near Budget Limit

The bot can warn when approaching budget limits (configurable threshold):

```
⚠️ Budget Warning

You've used 80% of your monthly budget ($8.00 of $10.00).

Current usage: $8.00
Remaining: $2.00
```

## Detailed Cost Breakdown

### Chat Token Usage

Tracked separately for input and output:

```
Chat Usage:
- Input tokens: 12,345 ($0.185)
- Output tokens: 8,765 ($0.526)
- Cached tokens: 2,345 ($0.018)
Total chat cost: $0.729
```

### Image Generation

Track by model and size:

```
Image Generation:
- DALL-E 3 (1024x1024): 5 images ($0.20)
- DALL-E 3 HD (1024x1024): 2 images ($0.16)
- FLUX: 3 images (free)
Total image cost: $0.36
```

### Text-to-Speech

Track by model and character count:

```
TTS Usage:
- OpenAI tts-1: 3,500 chars ($0.053)
- OpenAI tts-1-hd: 1,200 chars ($0.036)
- KokoroTTS: 5 requests ($0.075)
Total TTS cost: $0.164
```

### Vision API

Track image analysis:

```
Vision Usage:
- Images analyzed: 15
- Tokens used: 4,500
- Cost: $0.045
```

### Transcription

Track audio/video transcription:

```
Transcription:
- Minutes transcribed: 12.5
- Cost: $0.075
```

## Resetting Usage

### User Reset (Admin Only)

Admins can reset a user's stats:

```
/reset_stats @username
```

Or reset all users:

```
/reset_stats all
```

### Self Reset

Users cannot reset their own stats (prevents budget bypass).

### Automatic Reset

Stats automatically reset based on `BUDGET_PERIOD`:
- **daily**: At 00:00 UTC
- **monthly**: On the 1st at 00:00 UTC
- **all-time**: Never auto-resets

## Usage Logs

### Log Files

Detailed usage logs are stored per user:

```
user_logs/<user_id>/user_<user_id>.log
```

**Log Entry Example:**
```
2024-01-15 14:30:25 [INFO] user_123456789 - Chat completion: 
  Model: gpt-4o
  Input tokens: 150
  Output tokens: 85
  Cost: $0.0015
  Total month: $3.45
```

### Viewing Logs

```bash
# View your logs
cat user_logs/123456789/user_123456789.log

# Follow logs in real-time
tail -f user_logs/123456789/user_123456789.log

# Search logs
grep "Image" user_logs/*/user_*.log
```

## Budget Management Commands

### Check Budget

```
/budget
```

Shows remaining budget for current period.

### Usage History

```
/usage
```

Shows detailed usage breakdown.

### Admin: Set User Budget

```
/config set USER_BUDGETS 5.0,10.0,20.0
```

### Admin: View All Usage

```
/admin_stats
```

Shows comprehensive usage across all users.

## Cost Optimization Tips

### 1. Use Appropriate Models

Choose cost-effective models for simple tasks:

```env
OPENAI_MODEL=gpt-3.5-turbo  # For simple chat
# vs
OPENAI_MODEL=gpt-4o  # For complex tasks
```

### 2. Limit Response Length

```env
MAX_TOKENS=800  # Instead of default 1200
```

### 3. Reduce Conversation History

```env
MAX_HISTORY_SIZE=10  # Instead of default 15
```

### 4. Disable Expensive Features

```env
ENABLE_IMAGE_GENERATION=false  # If not needed
ENABLE_VISION=false  # If not needed
```

### 5. Use Free Alternatives

- Use FLUX for free image generation
- Use free plugins (weather, web search) instead of paid ones

### 6. Enable Caching

Some APIs support caching for reduced costs:

```env
ENABLE_CACHING=true
```

### 7. Monitor Regularly

Check `/stats` frequently to catch unexpected usage spikes.

### 8. Set Conservative Budgets

Start with low budgets and increase as needed:

```env
USER_BUDGETS=5.0  # Start low
GUEST_BUDGET=2.0
```

## Advanced Usage Tracking

### Per-Chat Tracking

Usage is tracked separately for each chat:

```python
# In code
chat_id_1_usage = tracker.get_chat_usage(chat_id_1)
chat_id_2_usage = tracker.get_chat_usage(chat_id_2)
```

### Time-Based Analysis

View usage trends over time:

```bash
# Usage by day
grep "2024-01" user_logs/*/user_*.log | wc -l

# Most active users
cat user_logs/*/user_*.log | grep "Total month" | sort -t'$' -k2 -n -r
```

### Export Usage Data

Export usage data for analysis:

```bash
# Export to CSV
python scripts/export_usage.py > usage.csv
```

### Custom Reports

Create custom usage reports:

```python
# Example script
from usage_tracker import UsageTracker

tracker = UsageTracker(user_id, username, chat_id)
report = tracker.generate_report(period='monthly')
print(report)
```

## Troubleshooting

### Budget Not Resetting

**Issue:** Budget should have reset but didn't

**Solutions:**
1. Check `BUDGET_PERIOD` setting
2. Verify system timezone (resets at UTC midnight)
3. Manually trigger reset: `/reset_stats`
4. Check logs for errors

### Incorrect Cost Calculation

**Issue:** Costs don't match expected values

**Solutions:**
1. Verify pricing configuration
2. Check if using correct model prices
3. Review token counting accuracy
4. Compare with provider's dashboard

### Stats Not Updating

**Issue:** Usage not being tracked

**Solutions:**
1. Check file permissions on `user_logs/` directory
2. Verify disk space available
3. Check logs for write errors
4. Restart bot to reload tracker

### Budget Too Restrictive

**Issue:** Users hitting budget too quickly

**Solutions:**
1. Increase `USER_BUDGETS`
2. Optimize model selection
3. Reduce `MAX_TOKENS`
4. Disable expensive features

## API Reference

### UsageTracker Class

For developers wanting to extend tracking:

```python
from usage_tracker import UsageTracker

# Initialize
tracker = UsageTracker(user_id, username, chat_id)

# Add chat usage
tracker.add_chat_usage(input_tokens, output_tokens, cached_tokens, model)

# Add image usage
tracker.add_image_request(image_size, image_model)

# Add TTS usage
tracker.add_tts_request(char_count, tts_model)

# Add vision usage
tracker.add_vision_usage(token_count)

# Get stats
stats = tracker.get_stats()

# Save state
tracker.save_state()
```

### Database Schema

Usage data stored in JSON format:

```json
{
  "user_id": 123456789,
  "username": "@john",
  "period": "monthly",
  "current_period_start": "2024-01-01T00:00:00Z",
  "usage": {
    "chat": {
      "input_tokens": 12345,
      "output_tokens": 8765,
      "cached_tokens": 2345,
      "cost": 3.20
    },
    "image": {
      "count": 10,
      "cost": 0.20
    },
    "tts": {
      "char_count": 2500,
      "cost": 0.05
    }
  },
  "budget": 10.0,
  "remaining": 6.55
}
```

## Best Practices

### For Users

1. **Monitor Regularly**: Check `/stats` weekly
2. **Set Alerts**: Note when you reach 50%, 75%, 90%
3. **Optimize Prompts**: Be concise to save tokens
4. **Use Reset Wisely**: Don't abuse `/reset` to bypass budgets

### For Admins

1. **Review Usage**: Check `/users` regularly
2. **Adjust Budgets**: Based on actual usage patterns
3. **Communicate Limits**: Inform users of budget policies
4. **Monitor Trends**: Look for unusual spikes
5. **Document Policies**: Create guidelines for budget allocation

### For Developers

1. **Atomic Writes**: Ensure usage saves are atomic
2. **Error Handling**: Handle disk full, permission errors
3. **Performance**: Minimize I/O operations
4. **Testing**: Test tracking accuracy thoroughly

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 🔌 Explore [Plugins](plugins.md)
