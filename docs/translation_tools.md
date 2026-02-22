# Translation Tools Guide (Beta)

Aiden Telegram Bot includes a powerful JSON-based translation system for localizing bot responses.

## Overview

The translation tool helps you:
- Translate bot messages to any language
- Maintain JSON structure integrity
- Preserve placeholders and variables
- Track translation progress
- Save costs by skipping existing translations

## Usage

### Basic Translation Command

```bash
python bot/translate_json.py "<target_language>" "<language_code>"
```

**Example:**
```bash
python bot/translate_json.py "Persian (Farsi)" "fa"
```

### Parameters

- `target_language`: Full language name (e.g., "Spanish", "German")
- `language_code`: ISO language code (e.g., "es", "de")

## Features

### Progressive Translation

Translates missing entries while preserving existing ones:

```json
// Before
{
  "en": {
    "help": "How can I help you?",
    "stats": "Your statistics"
  },
  "es": {
    // Empty - will be translated
  }
}

// After running: python translate_json.py "Spanish" "es"
{
  "en": {
    "help": "How can I help you?",
    "stats": "Your statistics"
  },
  "es": {
    "help": "¿Cómo puedo ayudarte?",
    "stats": "Tus estadísticas"
  }
}
```

### Placeholder Preservation

Maintains variables and placeholders:

```json
// English
{
  "welcome": "Hello {username}, welcome!",
  "tokens_used": "Used {count} tokens"
}

// Spanish (placeholders preserved)
{
  "welcome": "Hola {username}, ¡bienvenido!",
  "tokens_used": "Usaste {count} tokens"
}
```

### State Saving

Tracks progress and can resume if interrupted:

```
Translation progress saved to: translations_fa_progress.json
Resuming from last checkpoint...
```

### Cost Efficiency

Skips already translated keys:

```
Found 50 existing translations
Skipping already translated keys...
Translating 15 new keys only
Cost saved: $0.35
```

## Supported Languages

Currently supported (20+ languages):

| Code | Language | Native Name |
|------|----------|-------------|
| `en` | English | English |
| `de` | German | Deutsch |
| `ru` | Russian | Русский |
| `tr` | Turkish | Türkçe |
| `it` | Italian | Italiano |
| `fi` | Finnish | Suomi |
| `es` | Spanish | Español |
| `id` | Indonesian | Bahasa Indonesia |
| `nl` | Dutch | Nederlands |
| `zh-cn` | Chinese (Simplified) | 简体中文 |
| `zh-tw` | Chinese (Traditional) | 繁體中文 |
| `vi` | Vietnamese | Tiếng Việt |
| `fa` | Persian (Farsi) | فارسی |
| `pt-br` | Portuguese (Brazil) | Português (Brasil) |
| `uk` | Ukrainian | Українська |
| `ms` | Malay | Bahasa Melayu |
| `uz` | Uzbek | O'zbekcha |
| `ar` | Arabic | العربية |
| `he` | Hebrew | עברית |
| `pl` | Polish | Polski |

## Adding New Language

### Step 1: Run Translation Tool

```bash
python bot/translate_json.py "French" "fr"
```

### Step 2: Review Translations

Check `translations.json` for accuracy:

```json
{
  "fr": {
    "help": "Comment puis-je vous aider?",
    "stats": "Vos statistiques"
  }
}
```

### Step 3: Update Bot Configuration

Add language to available options in code:

```python
# In telegram_bot.py or config
AVAILABLE_LANGUAGES = ['en', 'de', 'ru', 'tr', 'fr', ...]
```

### Step 4: Test

Set bot language and test:

```env
BOT_LANGUAGE=fr
```

## Translation Quality

### AI-Powered Translations

Uses AI for professional-quality translations:
- Context-aware
- Natural phrasing
- Technical accuracy
- Cultural adaptation

### Manual Review Recommended

Always review translations for:
- Accuracy
- Cultural sensitivity
- Technical terms
- Idioms and expressions

### Improving Translations

Edit `translations.json` manually if needed:

```json
{
  "de": {
    "help": "Wie kann ich Ihnen helfen?"  // Corrected manually
  }
}
```

## Batch Translation

### Multiple Languages

Translate to multiple languages:

```bash
# Sequential translation
python translate_json.py "Spanish" "es"
python translate_json.py "French" "fr"
python translate_json.py "German" "de"
```

### Parallel Translation

Run multiple instances (different sessions):

```bash
# Terminal 1
python translate_json.py "Spanish" "es"

# Terminal 2
python translate_json.py "French" "fr"
```

## Cost Management

### Pricing

Translation costs depend on:
- Number of keys
- Text length
- Target language
- AI model used

**Estimated Costs:**
- Small language (50 keys): ~$0.10-0.30
- Medium language (150 keys): ~$0.30-0.80
- Large language (300+ keys): ~$0.80-2.00

### Reduce Costs

1. **Skip Existing**: Tool automatically skips translated keys
2. **Batch Updates**: Add multiple keys before translating
3. **Review First**: Check if existing translations are adequate
4. **Use Free Tier**: Some AI providers offer free translation tiers

## Troubleshooting

### Translation Fails

**Issue:** Error during translation

**Solutions:**
1. Check API key is valid
2. Verify internet connection
3. Ensure sufficient credits
4. Check language code format
5. Review error logs

### Placeholders Broken

**Issue:** Variables not preserved

**Solutions:**
1. Use consistent placeholder format `{variable}`
2. Don't translate variable names
3. Review translation output
4. Manually fix if needed

### Encoding Issues

**Issue:** Special characters display incorrectly

**Solutions:**
1. Ensure UTF-8 encoding
2. Use proper escape sequences
3. Check file encoding in editor
4. Validate JSON syntax

### Progress Not Saved

**Issue:** Translation doesn't resume

**Solutions:**
1. Check write permissions
2. Verify progress file exists
3. Ensure disk space available
4. Review file path

## Best Practices

### 1. Start with Major Languages

Prioritize most-used languages first:
- English (base)
- Spanish, Chinese, Hindi (most speakers)
- Languages matching your user base

### 2. Community Contributions

Invite native speakers to review:
- Post in community forums
- Create GitHub issues for review
- Credit contributors

### 3. Regular Updates

Update translations when:
- Adding new features
- Changing existing messages
- Receiving user feedback

### 4. Test Thoroughly

Test each language:
- All commands work
- Messages display correctly
- No broken placeholders
- Proper text direction (RTL languages)

### 5. Document Changes

Keep changelog:
```markdown
## 2024-01-15
- Added French translations
- Updated German translations
- Fixed Spanish placeholder issue
```

## Contributing Translations

### Submit New Language

1. Fork repository
2. Run translation tool
3. Review and edit translations
4. Test thoroughly
5. Submit pull request

### Improve Existing

1. Find errors in translations
2. Edit `translations.json`
3. Document changes
4. Submit pull request

### Translation Guidelines

- Keep tone consistent
- Preserve formality levels
- Adapt cultural references
- Test with native speakers
- Document special cases

## API Reference

### Programmatic Usage

For developers:

```python
from translate_json import translate_language

# Translate specific language
result = translate_language(
    target_language="Spanish",
    language_code="es",
    input_file="translations.json",
    output_file="translations.json"
)

print(f"Translated {result['count']} keys")
print(f"Cost: ${result['cost']}")
```

### Custom Translation Function

Integrate with other AI providers:

```python
def custom_translate(text, target_lang):
    # Use your preferred translation API
    pass
```

## Future Enhancements

Planned features:
- [ ] Web interface for translations
- [ ] Community voting on translations
- [ ] Automatic quality checks
- [ ] Translation memory
- [ ] Glossary support
- [ ] Context-aware translations
- [ ] Screenshot-based UI translation

## Resources

- **ISO Language Codes**: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
- **Translation Best Practices**: https://www.w3.org/International/questions/qa-international-multilingual
- **Unicode & Characters**: https://unicode.org/

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 🔧 Read [Troubleshooting](troubleshooting.md)
