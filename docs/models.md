# Model Support Guide

Aiden Telegram Bot supports a wide range of AI models from multiple providers.

## Supported Models

### OpenAI Models

#### GPT-3.5 Series
- `gpt-3.5-turbo` - Fast and efficient
- `gpt-3.5-turbo-0301` - Legacy version
- `gpt-3.5-turbo-0613` - Legacy with functions
- `gpt-3.5-turbo-16k` - Extended context (16K tokens)
- `gpt-3.5-turbo-1106` - Updated version
- `gpt-3.5-turbo-0125` - Latest 3.5 version

**Best for:** Quick responses, simple tasks, cost-effective usage

#### GPT-4 Series
- `gpt-4` - Standard GPT-4
- `gpt-4-0314` - Legacy version
- `gpt-4-0613` - Legacy with functions
- `gpt-4-32k` - Extended context (32K tokens)
- `gpt-4-turbo-preview` - Faster GPT-4
- `gpt-4-turbo` - Optimized version
- `gpt-4-1106-preview` - Preview with improvements
- `gpt-4-0125-preview` - Latest preview

**Best for:** Complex reasoning, detailed analysis, high-quality outputs

#### GPT-4o Series (Omni)
- `gpt-4o` - Multimodal model (text, image, audio)
- `gpt-4o-mini` - Efficient variant
- `gpt-4o-mini-2024-07-18` - Dated version
- `chatgpt-4o-latest` - Cutting-edge version

**Best for:** Vision tasks, multimodal interactions, balanced performance

#### O1 Series (Reasoning)
- `o1` - Advanced reasoning model
- `o1-mini` - Efficient reasoning variant
- `o1-preview` - Preview version

**Best for:** Complex problem-solving, mathematical reasoning, scientific analysis

**Note:** O1 models don't support function calling

### Google Models (via AI Studio/OpenAI-compatible API)

#### Gemini Series
- `gemini-2.0-flash` - Fast multimodal model
- `gemini-2.0-flash-exp` - Experimental version
- `gemini-2.5-pro-exp-03-25` - Pro experimental
- `gemini-2.5-flash` - Latest flash model
- `gemini-2.5-flash-preview-04-17` - Preview version

**Best for:** Vision tasks, fast responses, Google ecosystem integration

**Configuration:**
```env
OPENAI_MODEL=gemini-2.0-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
OPENAI_API_KEY=your-google-api-key
```

### TogetherAI Models

#### Llama Series
- `meta-llama/Llama-3.3-70B-Instruct-Turbo` - Powerful open model

#### Qwen Series
- `Qwen/Qwen2.5-Coder-32B-Instruct` - Code-specialized model

**Configuration:**
```env
OPENAI_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=your-together-api-key
```

## Model Capabilities

### Function Calling Support

| Model Series | Functions Support | Notes |
|--------------|-------------------|-------|
| GPT-3.5 (recent) | ✅ Yes | Versions after 0301 |
| GPT-4 (recent) | ✅ Yes | Versions after 0314 |
| GPT-4o | ✅ Yes | Full function support |
| O1 Series | ❌ No | Reasoning-only models |
| Gemini | ⚠️ Limited | Depends on API version |
| TogetherAI | ⚠️ Varies | Check specific model |

### Vision Capabilities

| Model | Vision Support | Detail Levels |
|-------|----------------|---------------|
| `gpt-4o` | ✅ Yes | low, high, auto |
| `gpt-4o-mini` | ✅ Yes | low, high, auto |
| `gemini-2.0-flash` | ✅ Yes | Automatic |
| `gpt-4-turbo` | ✅ Yes | low, high |
| Other models | ❌ No | Text-only |

**Vision Configuration:**
```env
VISION_MODEL=gpt-4o
VISION_DETAIL=auto
VISION_MAX_TOKENS=300
ENABLE_VISION_FOLLOW_UP_QUESTIONS=true
```

### Context Window Sizes

| Model | Max Context Tokens |
|-------|-------------------|
| GPT-3.5 | 4,096 - 16,384 |
| GPT-3.5-16k | 16,384 |
| GPT-4 | 8,192 |
| GPT-4-32k | 32,768 |
| GPT-4 Turbo | 128,000 |
| GPT-4o | 128,000 |
| O1 | 32,768 - 100,000 |
| Gemini 2.0 | 1,000,000+ |
| Llama 3.3 70B | 128,000 |

## Selecting the Right Model

### For Chat & Conversation

**Recommended:** `gpt-4o`, `gemini-2.0-flash`

```env
OPENAI_MODEL=gpt-4o
MAX_TOKENS=1200
TEMPERATURE=0.7
```

### For Complex Reasoning

**Recommended:** `o1`, `o1-preview`, `gpt-4-turbo`

```env
OPENAI_MODEL=o1
MAX_TOKENS=4096
TEMPERATURE=1.0  # O1 uses fixed temperature
```

### For Vision Tasks

**Recommended:** `gpt-4o`, `gemini-2.0-flash`

```env
OPENAI_MODEL=gpt-4o
VISION_MODEL=gpt-4o
ENABLE_VISION=true
```

### For Cost-Effective Usage

**Recommended:** `gpt-3.5-turbo`, `gpt-4o-mini`

```env
OPENAI_MODEL=gpt-3.5-turbo
MAX_TOKENS=800
```

### For Code Generation

**Recommended:** `gpt-4-turbo`, `Qwen/Qwen2.5-Coder-32B-Instruct`

```env
OPENAI_MODEL=gpt-4-turbo
MAX_TOKENS=2400
```

### For Creative Writing

**Recommended:** `gpt-4`, `claude` (via compatible API)

```env
OPENAI_MODEL=gpt-4
TEMPERATURE=0.8
PRESENCE_PENALTY=0.5
```

## Model-Specific Configurations

### GPT-4o Configuration

```env
OPENAI_MODEL=gpt-4o
MAX_TOKENS=4096
VISION_MODEL=gpt-4o
VISION_MAX_TOKENS=300
ENABLE_FUNCTIONS=true
```

### O1 Series Configuration

```env
OPENAI_MODEL=o1
MAX_TOKENS=4096
ENABLE_FUNCTIONS=false  # O1 doesn't support functions
TEMPERATURE=1.0  # Fixed for O1
```

**Note:** O1 models require special handling:
- Use `max_completion_tokens` instead of `max_tokens`
- System messages use "assistant" role instead of "system"
- Higher latency but better reasoning

### Gemini Configuration

```env
OPENAI_MODEL=gemini-2.0-flash
OPENAI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
MAX_TOKENS=8192
VISION_MODEL=gemini-2.0-flash
```

### TogetherAI Configuration

```env
OPENAI_MODEL=meta-llama/Llama-3.3-70B-Instruct-Turbo
OPENAI_BASE_URL=https://api.together.xyz/v1
MAX_TOKENS=4096
```

## Performance Comparison

### Speed (Responses per Minute)

1. **Fastest:** `gpt-3.5-turbo`, `gpt-4o-mini`, `gemini-2.0-flash`
2. **Medium:** `gpt-4o`, `gpt-4-turbo`
3. **Slowest:** `o1`, `o1-preview`, `gpt-4-32k`

### Quality (Subjective)

1. **Highest:** `o1`, `gpt-4-turbo`, `gpt-4o`
2. **High:** `gpt-4`, `gemini-2.5-pro`
3. **Good:** `gpt-3.5-turbo`, `gpt-4o-mini`

### Cost Efficiency

1. **Most Affordable:** `gpt-3.5-turbo`, `gpt-4o-mini`
2. **Moderate:** `gpt-4o`, `gpt-4-turbo`
3. **Premium:** `o1`, `gpt-4-32k`

## Pricing (Approximate)

### OpenAI Models (per 1K tokens)

| Model | Input | Output |
|-------|-------|--------|
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| gpt-4o-mini | $0.00015 | $0.0006 |
| gpt-4o | $0.005 | $0.015 |
| gpt-4-turbo | $0.01 | $0.03 |
| o1 | $0.005 | $0.015 |
| o1-preview | $0.015 | $0.06 |

### Vision Costs

- **GPT-4o Vision:** 
  - Low detail: ~85 tokens per image
  - High detail: ~85 + tiles × 170 tokens

### TTS Costs

| Model | Price per 1K characters |
|-------|------------------------|
| tts-1 | $0.015 |
| tts-1-hd | $0.030 |

### Image Generation

| Model | Size | Price |
|-------|------|-------|
| DALL-E 3 | 1024×1024 | $0.040 (HD: $0.080) |
| DALL-E 2 | 1024×1024 | $0.020 |
| DALL-E 2 | 512×512 | $0.018 |
| DALL-E 2 | 256×256 | $0.016 |

## Model Switching

### Via Configuration

Change in `.env`:
```env
OPENAI_MODEL=gpt-4o
```

Restart bot to apply changes.

### Via Command (Future Feature)

```bash
/model gpt-4-turbo
```

### Per-Request Model Selection

For vision:
```bash
/vision gpt-4o Analyze this image
```

## Automatic Model Fallbacks

If a model is unavailable, the bot can fallback to alternatives:

```python
# In code (automatic)
fallback_models = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
```

Configure fallback behavior:
```env
FALLBACK_ENABLED=true
FALLBACK_MODELS=gpt-4o,gpt-4-turbo,gpt-3.5-turbo
```

## Monitoring Model Usage

Track which models you're using:

```bash
/stats
```

Shows:
- Tokens used per model
- Costs breakdown
- Most used models

## Best Practices

### 1. Start Simple
Begin with `gpt-3.5-turbo` or `gpt-4o-mini` for testing

### 2. Upgrade as Needed
Move to more capable models for complex tasks

### 3. Monitor Costs
Use budgets and track usage regularly

### 4. Test Different Models
Experiment to find best fit for your use case

### 5. Consider Latency
O1 models are slower but more accurate

### 6. Use Right Tool for Job
- Chat: GPT-4o
- Reasoning: O1
- Vision: GPT-4o or Gemini
- Code: GPT-4 Turbo or Qwen

### 7. Optimize Prompts
Better prompts reduce need for expensive models

### 8. Cache Results
Avoid repeated calls for same queries

## Troubleshooting

### Model Not Available

**Error:** "Model not found" or "Invalid model"

**Solutions:**
1. Check model name spelling
2. Verify API access for that model
3. Ensure model is not deprecated
4. Check API endpoint configuration

### Function Calling Issues

**Error:** "Functions not supported"

**Solutions:**
1. Use models that support functions
2. Avoid O1 series for function calls
3. Check `ENABLE_FUNCTIONS=true`

### Vision Not Working

**Error:** "Vision not available"

**Solutions:**
1. Set `VISION_MODEL` to vision-capable model
2. Enable `ENABLE_VISION=true`
3. Check image format and size

### Context Too Long

**Error:** "Maximum context length exceeded"

**Solutions:**
1. Use model with larger context window
2. Reduce `MAX_HISTORY_SIZE`
3. Enable conversation summarization
4. Use `/reset` to clear history

## Next Steps

- 📚 Learn about [Commands](commands.md)
- ⚙️ Configure in [Configuration Guide](configuration.md)
- 💰 Track costs in [Usage Tracking](usage_tracking.md)
