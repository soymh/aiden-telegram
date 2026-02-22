# Vision Capabilities Guide

Aiden Telegram Bot supports advanced vision capabilities for analyzing and interpreting images using state-of-the-art AI models.

## Overview

The bot can:
- Analyze single or multiple images
- Answer questions about image content
- Extract text from images (OCR)
- Describe scenes, objects, and people
- Interpret charts, graphs, and diagrams
- Read documents and screenshots

## Supported Vision Models

### GPT-4o (OpenAI)

**Best for:** General purpose vision tasks

```env
VISION_MODEL=gpt-4o
VISION_DETAIL=auto
VISION_MAX_TOKENS=300
```

**Capabilities:**
- High accuracy image analysis
- Context understanding
- Multi-image comparison
- Text extraction (OCR)
- Chart/graph interpretation

### Gemini 2.0 Flash (Google)

**Best for:** Fast vision processing, Google ecosystem

```env
VISION_MODEL=gemini-2.0-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

**Capabilities:**
- Ultra-fast processing
- Excellent OCR
- Multimodal understanding
- Cost-effective

## Configuration

### Basic Setup

```env
# Enable vision features
ENABLE_VISION=true

# Vision model selection
VISION_MODEL=gpt-4o

# Image analysis detail level
VISION_DETAIL=auto  # Options: low, high, auto

# Maximum tokens for vision responses
VISION_MAX_TOKENS=300

# Default prompt for image interpretation
VISION_PROMPT=What is in this image?

# Enable follow-up questions
ENABLE_VISION_FOLLOW_UP_QUESTIONS=true

# Ignore vision in group chats
IGNORE_GROUP_VISION=true
```

### Detail Levels

#### Low Detail
- Faster processing
- Lower cost (~85 tokens per image)
- Suitable for simple images

#### High Detail
- More accurate analysis
- Higher cost (~85 + tiles × 170 tokens)
- Better for complex images

#### Auto (Recommended)
- Automatically chooses based on image complexity
- Balances cost and quality

## Usage Methods

### Method 1: Send Image Directly

1. Open chat with bot
2. Attach image (no caption needed)
3. Bot analyzes automatically

**Example:**
```
User: [Sends photo of sunset]
Bot: This image shows a beautiful sunset over a mountain landscape...
```

### Method 2: Image with Caption

Send image with question/instruction:

```
User: [Sends chart image] "What trends do you see in this chart?"
Bot: The chart shows three key trends...
```

### Method 3: Vision Command

Use `/vision` command with optional model specification:

```bash
/vision Analyze this image in detail
```

Or specify model:

```bash
/vision gpt-4o Describe this image
```

### Method 4: Multiple Images

Send multiple images in one message:

```
User: [Sends 3 photos of different dishes] "Which dish looks most appetizing?"
Bot: Based on the images...
```

## Vision Prompt Configuration

### Default Prompt

Set global default prompt:

```env
VISION_PROMPT=What is in this image?
```

### Custom Prompts

Use specific prompts for different tasks:

**For OCR:**
```
VISION_PROMPT=Extract all text from this image
```

**For Charts:**
```
VISION_PROMPT=Analyze this chart and describe the key insights
```

**For Code Screenshots:**
```
VISION_PROMPT=Read the code in this screenshot and explain what it does
```

**For Product Photos:**
```
VISION_PROMPT=Describe this product's features and design
```

## Follow-Up Questions

When enabled, you can have conversations about images:

```env
ENABLE_VISION_FOLLOW_UP_QUESTIONS=true
```

**Example Conversation:**
```
User: [Sends image of a building]
Bot: This is the Eiffel Tower in Paris, France...

User: When was it built?
Bot: The Eiffel Tower was completed in 1889...

User: How tall is it?
Bot: The Eiffel Tower is 330 meters (1,083 feet) tall...
```

Without follow-up enabled:
```
User: [Sends image]
Bot: [Analyzes image]

User: When was it built?
Bot: [Treats as new conversation, no image context]
```

## Use Cases

### 1. Document Analysis

**Upload:** PDF pages, scanned documents, receipts

**Prompt Examples:**
- "Summarize this document"
- "Extract the total amount from this receipt"
- "What are the key terms in this contract?"

### 2. Screenshot Interpretation

**Upload:** App screenshots, error messages, web pages

**Prompt Examples:**
- "What error is shown here?"
- "Explain this user interface"
- "What information is on this webpage?"

### 3. Photo Description

**Upload:** Personal photos, nature shots, events

**Prompt Examples:**
- "Describe what's happening in this photo"
- "What emotions do the people show?"
- "Identify the location based on landmarks"

### 4. Chart & Graph Analysis

**Upload:** Business charts, data visualizations, graphs

**Prompt Examples:**
- "What trends are visible in this graph?"
- "Compare the data points"
- "What conclusions can be drawn?"

### 5. OCR (Text Extraction)

**Upload:** Signs, handwritten notes, printed text

**Prompt Examples:**
- "Transcribe all text in this image"
- "Translate the text to Spanish"
- "What does this sign say?"

### 6. Code Review

**Upload:** Code screenshots, error logs

**Prompt Examples:**
- "What programming language is this?"
- "Find bugs in this code"
- "Explain what this function does"

### 7. Educational Content

**Upload:** Textbook pages, diagrams, equations

**Prompt Examples:**
- "Explain this concept"
- "Solve this math problem"
- "Label the parts in this diagram"

### 8. Product Identification

**Upload:** Product photos, packaging, labels

**Prompt Examples:**
- "What product is this?"
- "List the ingredients"
- "Is this product eco-friendly?"

## Token Costs

### Calculation Formula

**GPT-4o Vision Pricing:**

Low Detail:
```
Base: 85 tokens per image
```

High Detail:
```
Base: 85 tokens
+ (Number of 512px tiles × 170 tokens)
```

**Example Calculations:**

1. **Low Detail, 1 image:**
   - 85 tokens
   - Cost: ~$0.00085 (at $0.01/1K tokens)

2. **High Detail, 1024×1024 image:**
   - Tiles: (1024/512) × (1024/512) = 4 tiles
   - Tokens: 85 + (4 × 170) = 765 tokens
   - Cost: ~$0.00765

3. **High Detail, 2048×2048 image:**
   - After downscaling: fits in 2×2 grid
   - Tiles: 4
   - Tokens: 85 + (4 × 170) = 765 tokens

### Cost Optimization

**Tips to Reduce Costs:**

1. **Use Low Detail** when high precision not needed
2. **Crop Images** to focus on relevant areas
3. **Resize Large Images** before sending
4. **Use Auto Detail** for automatic optimization
5. **Limit Follow-Ups** to save conversation tokens

## Advanced Features

### Multi-Image Analysis

Send up to 10 images in one message:

```
User: [Sends 5 photos of vacation spots] "Which location looks best for a family vacation?"
Bot: Based on the images provided...
```

**Use Cases:**
- Compare products
- Choose between options
- Analyze sequences
- Before/after comparisons

### Image + Text Combination

Combine image analysis with other queries:

```
User: [Sends restaurant menu photo]
      "Recommend dishes for someone who likes spicy food"
Bot: Based on the menu, I recommend...
```

### Vision + Plugins

Vision can work with plugins:

```
User: [Sends book cover photo] "Find reviews for this book"
Bot: [Uses vision to identify book, then web search plugin for reviews]
```

## Integration with Other Features

### Vision + TTS

Get audio descriptions:

```env
PLUGINS=auto_tts,vision
```

```
User: [Sends image]
Bot: [Analyzes image] → [Converts response to speech]
```

### Vision + Translation

Analyze and translate:

```
User: [Sends foreign language sign] "Translate this"
Bot: [Extracts text via vision] → [Translates via DeepL plugin]
```

### Vision + Image Generation

Compare generated images:

```
User: "/image a cat"
Bot: [Generates image]
User: [Sends own cat photo] "Which looks more realistic?"
Bot: [Compares both images]
```

## Troubleshooting

### Vision Not Working

**Issue:** Bot doesn't analyze images

**Solutions:**
1. Check `ENABLE_VISION=true`
2. Verify `VISION_MODEL` is vision-capable
3. Ensure image format is supported
4. Check file size (< 20 MB)
5. Review logs for errors

### Poor Analysis Quality

**Issue:** Inaccurate or vague descriptions

**Solutions:**
1. Increase `VISION_DETAIL` to `high`
2. Provide more specific prompts
3. Ensure image is clear and well-lit
4. Crop to focus on subject
5. Try different vision model

### High Costs

**Issue:** Vision usage too expensive

**Solutions:**
1. Use `VISION_DETAIL=low`
2. Switch to `gemini-2.0-flash` (cheaper)
3. Limit images per day
4. Set budget alerts
5. Disable `ENABLE_VISION_FOLLOW_UP_QUESTIONS`

### Timeout Errors

**Issue:** Vision requests timing out

**Solutions:**
1. Reduce image size
2. Use low detail mode
3. Check network connectivity
4. Retry with smaller batch
5. Increase timeout settings

### Format Issues

**Issue:** Image format not supported

**Supported Formats:**
- JPEG/JPG
- PNG
- WebP
- GIF (non-animated)

**Solutions:**
1. Convert to PNG or JPEG
2. Remove animation from GIFs
3. Check file extension matches format

## Best Practices

### Image Quality

1. **Resolution:** 512×512 to 2048×2048 optimal
2. **Lighting:** Well-lit images work better
3. **Focus:** Sharp, clear images preferred
4. **Orientation:** Correct rotation before sending

### Prompt Engineering

1. **Be Specific:** "Count the people" vs "What's here?"
2. **Provide Context:** "This is a medical scan..."
3. **Ask Clear Questions:** One question at a time
4. **Guide Detail Level:** "Brief description" vs "Detailed analysis"

### Cost Management

1. **Monitor Usage:** Check `/stats` regularly
2. **Set Budgets:** Use budget limits
3. **Choose Right Model:** Balance cost vs quality
4. **Optimize Detail:** Use lowest acceptable detail
5. **Cache Results:** Don't re-analyze same images

### Privacy & Security

1. **Avoid Sensitive Data:** Don't share personal info in images
2. **Blur Private Info:** Redact sensitive content
3. **Consider Storage:** Images may be logged
4. **Group Chat Caution:** `IGNORE_GROUP_VISION=true` for privacy

## API Reference

### Programmatic Usage

For developers:

```python
# In code
async def analyze_image(image_bytes, prompt):
    result, tokens = await helper.interpret_image(
        user_id=user_id,
        username=username,
        chat_id=chat_id,
        fileobjs=[image_bytes],
        prompt=prompt
    )
    return result
```

### Vision Plugin

Create custom vision workflows:

```python
from plugins.vision_plugin import VisionPlugin

class CustomVisionPlugin(VisionPlugin):
    async def execute(self, function_name, helper, **kwargs):
        # Custom vision logic
        pass
```

## Future Enhancements

Planned vision features:
- [ ] Video analysis support
- [ ] Real-time object detection
- [ ] Face recognition (with consent)
- [ ] Handwriting recognition improvement
- [ ] 3D image understanding
- [ ] Augmented reality integration

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 🎨 Explore [Image Generation](image_generation.md)
