# Image Generation Guide

Aiden Telegram Bot supports multiple image generation engines including DALL-E 2/3 and FLUX.

## Overview

Generate images from text descriptions using:

1. **DALL-E 3** (OpenAI) - High-quality, detailed images
2. **DALL-E 2** (OpenAI) - Faster, more affordable
3. **FLUX** (TogetherAI) - Free alternative, fast generation

## Configuration

### DALL-E Configuration

```env
# Enable image generation
ENABLE_IMAGE_GENERATION=true

# Model selection: dall-e-2 or dall-e-3
IMAGE_MODEL=dall-e-3

# Image quality (dall-e-3 only): standard or hd
IMAGE_QUALITY=standard

# Image style (dall-e-3 only): vivid or natural
IMAGE_STYLE=vivid

# Image size
# DALL-E 2: 256x256, 512x512, 1024x1024
# DALL-E 3: 1024x1024 only
IMAGE_SIZE=1024x1024

# Format in Telegram: photo or document
IMAGE_FORMAT=photo

# OpenAI Media API (if using separate endpoint)
OPENAI_MEDIA_BASE_URL=https://api.openai.com/v1
OPENAI_MEDIA_API_KEY=your-media-api-key
```

### FLUX Configuration

```env
# Enable FLUX generation
FLUX_GEN=true

# FLUX API settings
FLUX_API_KEY=your-flux-api-key
FLUX_BASE_URL=https://api.together.xyz/v1/images/generations
FLUX_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell-Free
```

## Usage Commands

### Basic Image Generation

```bash
/image a sunset over mountains
```

### With Specific Provider

```bash
# Use DALL-E 3
/image a cyberpunk city --provider dalle

# Use FLUX (free)
/image a fantasy castle --provider flux
```

### Advanced Options

```bash
/image a portrait --size 1024x1024 --quality hd --style vivid
```

## DALL-E 3 Features

### Image Quality

**Standard Quality:**
```env
IMAGE_QUALITY=standard
```
- Faster generation
- Lower cost ($0.040 per image)
- Good for most use cases

**HD Quality:**
```env
IMAGE_QUALITY=hd
```
- Higher detail and quality
- Slower generation
- Higher cost ($0.080 per image)

### Image Styles

**Vivid Style:**
```env
IMAGE_STYLE=vivid
```
- Enhanced colors
- More dramatic lighting
- Artistic enhancement
- Best for: Fantasy, art, creative concepts

**Natural Style:**
```env
IMAGE_STYLE=natural
```
- Realistic appearance
- Natural lighting
- Photographic quality
- Best for: Products, portraits, realistic scenes

### Size Options

**DALL-E 3:**
- Only `1024x1024` supported

**DALL-E 2:**
- `256x256` - $0.016
- `512x512` - $0.018
- `1024x1024` - $0.020

## FLUX Image Generation

### What is FLUX?

FLUX.1 is a free, open-source image generation model available via TogetherAI.

**Advantages:**
- ✅ Free to use
- ✅ Fast generation
- ✅ Good quality
- ✅ No per-image costs

**Limitations:**
- Lower resolution than DALL-E 3
- Less detailed for complex prompts
- Limited style options

### Setup FLUX

1. **Get TogetherAI API Key:**
   - Visit: https://together.ai
   - Create account
   - Get API key

2. **Configure:**
```env
FLUX_GEN=true
FLUX_API_KEY=your-api-key
FLUX_BASE_URL=https://api.together.xyz/v1/images/generations
FLUX_IMAGE_MODEL=black-forest-labs/FLUX.1-schnell-Free
```

3. **Use:**
```bash
/image a beautiful landscape --provider flux
```

## Prompt Engineering

### Basic Structure

Good prompt formula:
```
[Subject] + [Action/Context] + [Style/Medium] + [Lighting/Color] + [Composition]
```

**Example:**
```
"A majestic lion standing on a rocky cliff at sunset, 
photorealistic, golden hour lighting, dramatic composition"
```

### Style Keywords

**Artistic Styles:**
- `oil painting`
- `watercolor`
- `digital art`
- `pencil sketch`
- `anime style`
- `cyberpunk`
- `steampunk`

**Photography Styles:**
- `photorealistic`
- `portrait photography`
- `landscape photography`
- `macro photography`
- `aerial view`
- `wide angle`

**Lighting:**
- `golden hour`
- `blue hour`
- `dramatic lighting`
- `soft lighting`
- `neon lights`
- `cinematic lighting`

### Negative Prompts (Implicit)

Avoid these in your prompts:
- Vague descriptions
- Too many elements
- Conflicting styles
- Overly complex scenes

### Example Prompts

**Portrait:**
```
"Professional headshot of a young woman with curly hair, 
studio lighting, neutral background, high detail, 8k"
```

**Landscape:**
```
"Misty mountain landscape at dawn, pine trees in foreground, 
lake reflection, serene atmosphere, photorealistic"
```

**Fantasy:**
```
"Ancient dragon guarding treasure hoard in cave, 
fantasy art, dramatic lighting, highly detailed, epic composition"
```

**Sci-Fi:**
```
"Futuristic city with flying cars, neon signs, 
cyberpunk style, night scene, rain-slicked streets"
```

**Product:**
```
"Minimalist product photography of smartwatch, 
white background, soft shadows, professional lighting"
```

## Cost Tracking

### DALL-E Pricing

| Model | Size | Quality | Price |
|-------|------|---------|-------|
| DALL-E 3 | 1024×1024 | Standard | $0.040 |
| DALL-E 3 | 1024×1024 | HD | $0.080 |
| DALL-E 2 | 1024×1024 | - | $0.020 |
| DALL-E 2 | 512×512 | - | $0.018 |
| DALL-E 2 | 256×256 | - | $0.016 |

### FLUX Pricing

| Model | Size | Price |
|-------|------|-------|
| FLUX.1 Schnell | 1024×1024 | Free |

### View Image Costs

```bash
/stats
```

Shows:
- Number of images generated
- Total cost
- Cost breakdown by model

## Advanced Features

### Multiple Images

Generate variations:

```bash
/image a cat
```

**Note:** Requires `N_CHOICES` configuration.

### Image Editing (Future)

Planned features:
- Edit existing images
- Inpainting/outpainting
- Style transfer
- Upscaling

### Batch Generation

Generate multiple prompts:

```bash
/batch_image "a cat";"a dog";"a bird"
```

## Integration with Other Features

### Vision + Image Generation

Compare generated images:

```
User: "/image a sunset"
Bot: [Generates image]
User: [Sends own sunset photo] "Which looks better?"
Bot: [Uses vision to compare]
```

### TTS Descriptions

Describe generated images via audio:

```env
PLUGINS=auto_tts,image_gen
```

```
User: "/image a forest"
Bot: [Generates image] → [Describes in audio]
```

### Web Search Inspiration

Find ideas for image generation:

```
User: "Search for fantasy landscape ideas"
Bot: [Uses web search] → "Try generating: [suggestion]"
User: "/image [suggestion]"
```

## Troubleshooting

### Image Not Generating

**Issue:** Error when generating image

**Solutions:**
1. Check `ENABLE_IMAGE_GENERATION=true`
2. Verify API key is valid
3. Ensure sufficient credits
4. Check prompt doesn't violate policies
5. Review logs for specific error

### Poor Image Quality

**Issue:** Images look blurry or distorted

**Solutions:**
1. Use DALL-E 3 instead of DALL-E 2
2. Increase quality to `hd`
3. Improve prompt detail
4. Specify desired style
5. Try different seed/model

### Policy Violations

**Issue:** "Content policy violation"

**Restricted Content:**
- Adult/NSFW content
- Violence or gore
- Hate symbols
- Celebrity likenesses
- Copyrighted characters

**Solutions:**
1. Revise prompt to avoid restricted content
2. Use more abstract descriptions
3. Focus on original concepts
4. Check OpenAI usage policies

### Slow Generation

**Issue:** Images take too long

**Solutions:**
1. Use DALL-E 2 for faster generation
2. Try FLUX for instant results
3. Reduce image quality setting
4. Check network connectivity
5. Avoid peak hours

### Cost Too High

**Issue:** Image generation expensive

**Solutions:**
1. Switch to FLUX (free)
2. Use DALL-E 2 instead of DALL-E 3
3. Reduce quality to `standard`
4. Limit images per day
5. Set budget alerts

## Best Practices

### 1. Start Simple

Begin with basic prompts, then add detail:
```
"a cat" → "a fluffy orange cat" → "a fluffy orange cat sleeping on windowsill"
```

### 2. Be Specific

Vague: "a building"  
Specific: "Victorian mansion with turret, brick facade, wraparound porch"

### 3. Reference Styles

Use known artists or movements:
- "in the style of Van Gogh"
- "Art Nouveau poster"
- "Bauhaus design"

### 4. Control Composition

Specify framing:
- "close-up portrait"
- "wide landscape view"
- "bird's eye view"
- "rule of thirds"

### 5. Iterate

First result not perfect? Refine prompt:
- Add/remove details
- Change style keywords
- Adjust lighting description

### 6. Use FLUX for Testing

Test prompts with free FLUX before using paid DALL-E

### 7. Save Good Prompts

Keep library of successful prompts for reuse

### 8. Monitor Costs

Track image generation in `/stats`

## Creative Applications

### 1. Story Illustration

Generate scenes from your stories:
```
/image medieval knight facing dragon, fantasy book illustration
```

### 2. Concept Art

Visualize ideas for projects:
```
/image futuristic kitchen design, concept art, clean lines
```

### 3. Social Media Content

Create unique visuals:
```
/image inspirational quote background, abstract art
```

### 4. Product Mockups

Preview product ideas:
```
/image eco-friendly water bottle design, minimalist
```

### 5. Character Design

Create character concepts:
```
/image steampunk inventor character, goggles, leather apron
```

### 6. Album Art

Design music artwork:
```
/image psychedelic album cover, swirling colors, 1960s style
```

### 7. Educational Materials

Create teaching aids:
```
/image diagram of human heart, medical illustration style
```

## Legal & Ethical Considerations

### Copyright

- Generated images may have usage restrictions
- Check OpenAI terms of service
- Be cautious with commercial use
- Avoid generating copyrighted characters

### Attribution

Some uses may require:
- "Generated by DALL-E 3"
- Disclosure of AI generation
- Compliance with platform rules

### Ethical Use

Consider:
- Misinformation potential
- Deepfake concerns
- Cultural sensitivity
- Representation issues

## Future Features

Planned enhancements:
- [ ] Image editing/inpainting
- [ ] Video generation
- [ ] 3D model generation
- [ ] Style transfer
- [ ] Higher resolutions
- [ ] Custom model training

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 👁️ Explore [Vision Capabilities](vision_guide.md)
