# ChatGPT Telegram Bot
![python-version](https://img.shields.io/badge/python-3.9-blue.svg)
[![openai-version](https://img.shields.io/badge/openai-1.58.1-orange.svg)](https://openai.com/)
[![license](https://img.shields.io/badge/License-GPL%202.0-brightgreen.svg)](LICENSE)
[![Publish Docker image](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml/badge.svg)](https://github.com/n3d1117/chatgpt-telegram-bot/actions/workflows/publish.yaml)

A [Telegram bot](https://core.telegram.org/bots/api) that integrates with OpenAI's _official_ [ChatGPT](https://openai.com/blog/chatgpt/), [DALL·E](https://openai.com/product/dall-e-2) and [Whisper](https://openai.com/research/whisper) APIs to provide answers. Ready to use with minimal configuration required.

## Screenshots

### Demo
![demo](https://user-images.githubusercontent.com/11541888/225114786-0d639854-b3e1-4214-b49a-e51ce8c40387.png)

### Plugins
![plugins](https://github.com/n3d1117/chatgpt-telegram-bot/assets/11541888/83d5e0cd-e09a-463d-a292-722f919e929f)

## Features
- [x] Support markdown in answers
- [x] Reset conversation with the `/reset` command
- [x] Typing indicator while generating a response
- [x] Access can be restricted by specifying a list of allowed users
- [x] Docker and Proxy support
- [x] Image generation using DALL·E via the `/image` command
- [x] Transcribe audio and video messages using Whisper (may require [ffmpeg](https://ffmpeg.org))
- [x] Automatic conversation summary to avoid excessive token usage
- [x] Track token usage per user - by [@AlexHTW](https://github.com/AlexHTW)
- [x] Get personal token usage statistics via the `/stats` command - by [@AlexHTW](https://github.com/AlexHTW)
- [x] User budgets and guest budgets - by [@AlexHTW](https://github.com/AlexHTW)
- [x] Stream support
- [x] GPT-4 support
  - If you have access to the GPT-4 API, simply change the `OPENAI_MODEL` parameter to `gpt-4`
- [x] Localized bot language
  - Available languages :brazil: :cn: :finland: :de: :indonesia: :iran: :it: :malaysia: :netherlands: :poland: :ru: :saudi_arabia: :es: :taiwan: :tr: :ukraine: :gb: :uzbekistan: :vietnam: :israel:
- [x] Improved inline queries support for group and private chats - by [@bugfloyd](https://github.com/bugfloyd)
  - To use this feature, enable inline queries for your bot in BotFather via the `/setinline` [command](https://core.telegram.org/bots/inline)
- [x] Support *new models* [announced on June 13, 2023](https://openai.com/blog/function-calling-and-other-api-updates)
- [x] Support *functions* (plugins) to extend the bot's functionality with 3rd party services
  - Weather, Spotify, Web search, text-to-speech and more. See [here](#available-plugins) for a list of available plugins
- [x] Support unofficial OpenAI-compatible APIs - by [@kristaller486](https://github.com/kristaller486)
- [x] (NEW!) Support GPT-4 Turbo and DALL·E 3 [announced on November 6, 2023](https://openai.com/blog/new-models-and-developer-products-announced-at-devday) - by [@AlexHTW](https://github.com/AlexHTW)
- [x] (NEW!) Text-to-speech support [announced on November 6, 2023](https://platform.openai.com/docs/guides/text-to-speech) - by [@gilcu3](https://github.com/gilcu3)
- [x] (NEW!) Vision support [announced on November 6, 2023](https://platform.openai.com/docs/guides/vision) - by [@gilcu3](https://github.com/gilcu3)
- [x] (NEW!) GPT-4o model support [announced on May 12, 2024](https://openai.com/index/hello-gpt-4o/) - by [@err09r](https://github.com/err09r)
- [x] (NEW!) o1 and o1-mini model preliminary support
- [x] (NEW!) Advanced Plugin System with ML-powered integrations:
  - ArXiv Search & Extract - Search and summarize academic papers
  - YouTube Video/Audio Tools - Download and extract audio from videos
  - Image Generation with multiple providers (DALL-E, Flux)
  - KokoroTTS Integration - Advanced text-to-speech capabilities
  - IP Location Tracking - Get geographical info for IP addresses
  - LaTeX to Image Conversion - Render LaTeX equations
  - Reddit Content Helper - Interact with Reddit content
  - Telegram Integration - Message extraction and moderation
  - Web Content Extraction - Smart webpage parsing
- [x] (NEW!) Enhanced Vision Capabilities:
  - Support for multiple vision models (GPT-4o, Gemini)
  - Automatic image analysis and captioning
  - Vision-based conversation context
  - Multi-image processing support
- [x] (NEW!) Advanced Text-to-Speech:
  - Multiple TTS providers (OpenAI, Google, Kokoro)
  - Voice customization options
  - Multi-language support
  - Character-based pricing
- [x] (NEW!) Improved Usage Tracking:
  - Per-user and per-chat tracking
  - Multi-service cost calculation
  - Budget management system
  - Usage statistics and reporting
- [x] (BETA!) Translation Tools for Bot Localization:
  - Automated JSON-based translation system
  - Support for multiple language targets
  - AI-powered professional translations
  - Maintains placeholder integrity
  - Command-line interface for easy use
  - Progressive translation with state saving
  - Skips existing translations to save costs

## Additional features - help needed!
If you'd like to help, check out the [issues](https://github.com/n3d1117/chatgpt-telegram-bot/issues) section and contribute!  
If you want to help with translations, check out the [Translations Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219)

PRs are always welcome!

## Prerequisites
- Python 3.9+
- A [Telegram bot](https://core.telegram.org/bots#6-botfather) and its token (see [tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))
- An [OpenAI](https://openai.com) account (see [configuration](#configuration) section)

## Getting started

### Configuration
Customize the configuration by copying `.env.example` and renaming it to `.env`, then editing the required parameters as desired:

| Parameter                   | Description                                                                                                                                                                                                                   |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `OPENAI_API_KEY`            | Your OpenAI API key, you can get it from [here](https://platform.openai.com/account/api-keys)                                                                                                                                 |
| `TELEGRAM_BOT_TOKEN`        | Your Telegram bot's token, obtained using [BotFather](http://t.me/botfather) (see [tutorial](https://core.telegram.org/bots/tutorial#obtain-your-bot-token))                                                                  |
| `ADMIN_USER_IDS`            | Telegram user IDs of admins. These users have access to special admin commands, information and no budget restrictions. Admin IDs don't have to be added to `ALLOWED_TELEGRAM_USER_IDS`. **Note**: by default, no admin (`-`) |
| `ALLOWED_TELEGRAM_USER_IDS` | A comma-separated list of Telegram user IDs that are allowed to interact with the bot (use [getidsbot](https://t.me/getidsbot) to find your user ID). **Note**: by default, *everyone* is allowed (`*`)                       |

### Optional configuration
The following parameters are optional and can be set in the `.env` file:

#### Budgets
| Parameter             | Description                                                                                                                                                                                                                                                                                                                                                                               | Default value      |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| `BUDGET_PERIOD`       | Determines the time frame all budgets are applied to. Available periods: `daily` *(resets budget every day)*, `monthly` *(resets budgets on the first of each month)*, `all-time` *(never resets budget)*. See the [Budget Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184) for more information                                                                  | `monthly`          |
| `USER_BUDGETS`        | A comma-separated list of $-amounts per user from list `ALLOWED_TELEGRAM_USER_IDS` to set custom usage limit of OpenAI API costs for each. For `*`- user lists the first `USER_BUDGETS` value is given to every user. **Note**: by default, *no limits* for any user (`*`). See the [Budget Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184) for more information | `*`                |
| `GUEST_BUDGET`        | $-amount as usage limit for all guest users. Guest users are users in group chats that are not in the `ALLOWED_TELEGRAM_USER_IDS` list. Value is ignored if no usage limits are set in user budgets (`USER_BUDGETS`=`*`). See the [Budget Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184) for more information                                                   | `100.0`            |
| `TOKEN_PRICE`         | $-price per 1000 tokens used to compute cost information in usage statistics. Source: https://openai.com/pricing                                                                                                                                                                                                                                                                          | `0.002`            |
| `IMAGE_PRICES`        | A comma-separated list with 3 elements of prices for the different image sizes: `256x256`, `512x512` and `1024x1024`. Source: https://openai.com/pricing                                                                                                                                                                                                                                  | `0.016,0.018,0.02` |
| `TRANSCRIPTION_PRICE` | USD-price for one minute of audio transcription. Source: https://openai.com/pricing                                                                                                                                                                                                                                                                                                       | `0.006`            |
| `VISION_TOKEN_PRICE`  | USD-price per 1K tokens of image interpretation. Source: https://openai.com/pricing                                                                                                                                                                                                                                                                                                       | `0.01`             |
| `TTS_PRICES`          | A comma-separated list with prices for the tts models: `tts-1`, `tts-1-hd`. Source: https://openai.com/pricing                                                                                                                                                                                                                                                                            | `0.015,0.030`      |

Check out the [Budget Manual](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/184) for possible budget configurations.

#### Additional optional configuration options
| Parameter                           | Description                                                                                                                                                                                                                                                                             | Default value                      |
|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| `ENABLE_QUOTING`                    | Whether to enable message quoting in private chats                                                                                                                                                                                                                                      | `true`                             |
| `ENABLE_IMAGE_GENERATION`           | Whether to enable image generation via the `/image` command                                                                                                                                                                                                                             | `true`                             |
| `ENABLE_TRANSCRIPTION`              | Whether to enable transcriptions of audio and video messages                                                                                                                                                                                                                            | `true`                             |
| `ENABLE_TTS_GENERATION`             | Whether to enable text to speech generation via the `/tts`                                                                                                                                                                                                                              | `true`                             |
| `ENABLE_VISION`                     | Whether to enable vision capabilities in supported models                                                                                                                                                                                                                               | `true`                             |
| `PROXY`                             | Proxy to be used for OpenAI and Telegram bot (e.g. `http://localhost:8080`)                                                                                                                                                                                                             | -                                  |
| `OPENAI_PROXY`                      | Proxy to be used only for OpenAI (e.g. `http://localhost:8080`)                                                                                                                                                                                                                         | -                                  |
| `TELEGRAM_PROXY`                    | Proxy to be used only for Telegram bot (e.g. `http://localhost:8080`)                                                                                                                                                                                                                   | -                                  |
| `OPENAI_MODEL`                      | The OpenAI model to use for generating responses. You can find all available models [here](https://platform.openai.com/docs/models/)                                                                                                                                                    | `gpt-4o`                           |
| `OPENAI_BASE_URL`                   | Endpoint URL for unofficial OpenAI-compatible APIs (e.g., LocalAI or text-generation-webui)                                                                                                                                                                                             | Default OpenAI API URL             |
| `ASSISTANT_PROMPT`                  | A system message that sets the tone and controls the behavior of the assistant                                                                                                                                                                                                          | `You are a helpful assistant.`     |
| `SHOW_USAGE`                        | Whether to show OpenAI token usage information after each response                                                                                                                                                                                                                      | `false`                            |
| `STREAM`                            | Whether to stream responses. **Note**: incompatible, if enabled, with `N_CHOICES` higher than 1                                                                                                                                                                                         | `true`                             |
| `MAX_TOKENS`                        | Upper bound on how many tokens the ChatGPT API will return                                                                                                                                                                                                                              | `1200` for GPT-3, `2400` for GPT-4 |
| `VISION_MAX_TOKENS`                 | Upper bound on how many tokens vision models will return                                                                                                                                                                                                                                | `300` for gpt-4o                   |
| `VISION_MODEL`                      | The Vision to Speech model to use. Allowed values: `gpt-4o`                                                                                                                                                                                                                             | `gpt-4o`                           |
| `ENABLE_VISION_FOLLOW_UP_QUESTIONS` | If true, once you send an image to the bot, it uses the configured VISION_MODEL until the conversation ends. Otherwise, it uses the OPENAI_MODEL to follow the conversation. Allowed values: `true` or `false`                                                                          | `true`                             |
| `MAX_HISTORY_SIZE`                  | Max number of messages to keep in memory, after which the conversation will be summarised to avoid excessive token usage                                                                                                                                                                | `15`                               |
| `MAX_CONVERSATION_AGE_MINUTES`      | Maximum number of minutes a conversation should live since the last message, after which the conversation will be reset                                                                                                                                                                 | `180`                              |
| `VOICE_REPLY_WITH_TRANSCRIPT_ONLY`  | Whether to answer to voice messages with the transcript only or with a ChatGPT response of the transcript                                                                                                                                                                               | `false`                            |
| `VOICE_REPLY_PROMPTS`               | A semicolon separated list of phrases (i.e. `Hi bot;Hello chat`). If the transcript starts with any of them, it will be treated as a prompt even if `VOICE_REPLY_WITH_TRANSCRIPT_ONLY` is set to `true`                                                                                 | -                                  |
| `VISION_PROMPT`                     | A phrase (i.e. `What is in this image`). The vision models use it as prompt to interpret a given image. If there is caption in the image sent to the bot, that supersedes this parameter                                                                                                | `What is in this image`            |
| `N_CHOICES`                         | Number of answers to generate for each input message. **Note**: setting this to a number higher than 1 will not work properly if `STREAM` is enabled                                                                                                                                    | `1`                                |
| `TEMPERATURE`                       | Number between 0 and 2. Higher values will make the output more random                                                                                                                                                                                                                  | `1.0`                              |
| `PRESENCE_PENALTY`                  | Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far                                                                                                                                                                        | `0.0`                              |
| `FREQUENCY_PENALTY`                 | Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far                                                                                                                                                                   | `0.0`                              |
| `IMAGE_FORMAT`                      | The Telegram image receive mode. Allowed values: `document` or `photo`                                                                                                                                                                                                                  | `photo`                            |
| `IMAGE_MODEL`                       | The DALL·E model to be used. Available models: `dall-e-2` and `dall-e-3`, find current available models [here](https://platform.openai.com/docs/models/dall-e)                                                                                                                          | `dall-e-2`                         |
| `IMAGE_QUALITY`                     | Quality of DALL·E images, only available for `dall-e-3`-model. Possible options: `standard` or `hd`, beware of [pricing differences](https://openai.com/pricing#image-models).                                                                                                          | `standard`                         |
| `IMAGE_STYLE`                       | Style for DALL·E image generation, only available for `dall-e-3`-model. Possible options: `vivid` or `natural`. Check availbe styles [here](https://platform.openai.com/docs/api-reference/images/create).                                                                              | `vivid`                            |
| `IMAGE_SIZE`                        | The DALL·E generated image size. Must be `256x256`, `512x512`, or `1024x1024` for dall-e-2. Must be `1024x1024` for dall-e-3 models.                                                                                                                                                    | `512x512`                          |
| `VISION_DETAIL`                     | The detail parameter for vision models, explained [Vision Guide](https://platform.openai.com/docs/guides/vision). Allowed values: `low` or `high`                                                                                                                                       | `auto`                             |
| `GROUP_TRIGGER_KEYWORD`             | If set, the bot in group chats will only respond to messages that start with this keyword                                                                                                                                                                                               | -                                  |
| `IGNORE_GROUP_TRANSCRIPTIONS`       | If set to true, the bot will not process transcriptions in group chats                                                                                                                                                                                                                  | `true`                             |
| `IGNORE_GROUP_VISION`               | If set to true, the bot will not process vision queries in group chats                                                                                                                                                                                                                  | `true`                             |
| `BOT_LANGUAGE`                      | Language of general bot messages. Currently available: `en`, `de`, `ru`, `tr`, `it`, `fi`, `es`, `id`, `nl`, `zh-cn`, `zh-tw`, `vi`, `fa`, `pt-br`, `uk`, `ms`, `uz`, `ar`.  [Contribute with additional translations](https://github.com/n3d1117/chatgpt-telegram-bot/discussions/219) | `en`                               |
| `WHISPER_PROMPT`                    | To improve the accuracy of Whisper's transcription service, especially for specific names or terms, you can set up a custom message.  [Speech to text - Prompting](https://platform.openai.com/docs/guides/speech-to-text/prompting)                                                    | `-`                                |
| `TTS_VOICE`                         | The Text to Speech voice to use. Allowed values: `alloy`, `echo`, `fable`, `onyx`, `nova`, or `shimmer`                                                                                                                                                                                 | `alloy`                            |
| `TTS_MODEL`                         | The Text to Speech model to use. Allowed values: `tts-1` or `tts-1-hd`                                                                                                                                                                                                                  | `tts-1`                            |

Check out the [official API reference](https://platform.openai.com/docs/api-reference/chat) for more details.

#### Functions
| Parameter                         | Description                                                                                                                                      | Default value                       |
|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|
| `ENABLE_FUNCTIONS`                | Whether to use functions (aka plugins). You can read more about functions [here](https://openai.com/blog/function-calling-and-other-api-updates) | `true` (if available for the model) |
| `FUNCTIONS_MAX_CONSECUTIVE_CALLS` | Maximum number of back-to-back function calls to be made by the model in a single response, before displaying a user-facing message              | `10`                                |
| `PLUGINS`                         | List of plugins to enable (see below for a full list), e.g: `PLUGINS=wolfram,weather`                                                            | -                                   |
| `SHOW_PLUGINS_USED`               | Whether to show which plugins were used for a response                                                                                           | `false`                             |

#### Available plugins
| Name                      | Description                                                                                                                                         | Required environment variable(s)                                     | Dependency          |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|---------------------|
| `weather`                 | Daily weather and 7-day forecast for any location (powered by [Open-Meteo](https://open-meteo.com))                                                 | -                                                                    |                     |
| `wolfram`                 | WolframAlpha queries (powered by [WolframAlpha](https://www.wolframalpha.com))                                                                      | `WOLFRAM_APP_ID`                                                     | `wolframalpha`      |
| `ddg_web_search`          | Web search (powered by [DuckDuckGo](https://duckduckgo.com))                                                                                        | -                                                                    | `duckduckgo_search` |
| `ddg_image_search`        | Search image or GIF (powered by [DuckDuckGo](https://duckduckgo.com))                                                                               | -                                                                    | `duckduckgo_search` |
| `crypto`                  | Live cryptocurrencies rate (powered by [CoinCap](https://coincap.io)) - by [@stumpyfr](https://github.com/stumpyfr)                                 | -                                                                    |                     |
| `spotify`                 | Spotify top tracks/artists, currently playing song and content search (powered by [Spotify](https://spotify.com)). Requires one-time authorization. | `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI` | `spotipy`           |
| `worldtimeapi`            | Get latest world time (powered by [WorldTimeAPI](https://worldtimeapi.org/)) - by [@noriellecruz](https://github.com/noriellecruz)                  | `WORLDTIME_DEFAULT_TIMEZONE`                                         |                     |
| `dice`                    | Send a dice in the chat!                                                                                                                            | -                                                                    |                     |
| `youtube_audio_extractor` | Extract audio from YouTube videos                                                                                                                   | -                                                                    | `pytube`            |
| `deepl_translate`         | Translate text to any language (powered by [DeepL](https://deepl.com)) - by [@LedyBacer](https://github.com/LedyBacer)                              | `DEEPL_API_KEY`                                                      |                     |
| `gtts_text_to_speech`     | Text to speech (powered by Google Translate APIs)                                                                                                   | -                                                                    | `gtts`              |
| `whois`                   | Query the whois domain database - by [@jnaskali](https://github.com/jnaskali)                                                                       | -                                                                    | `whois`             |
| `webshot`                 | Screenshot a website from a given url or domain name - by [@noriellecruz](https://github.com/noriellecruz)                                          | -                                                                    |                     |
| `auto_tts`                | Text to speech using OpenAI APIs - by [@Jipok](https://github.com/Jipok)                                                                            | -                                                                    |                     |
| `arxiv_extract`            | Extract and summarize academic papers from arXiv                                                                                                        | -                                                                    | `arxiv`            |
| `arxiv_search`             | Search academic papers on arXiv with advanced filtering                                                                                                 | -                                                                    | `arxiv`            |
| `kokoro_tts`              | Advanced text-to-speech using KokoroTTS engine                                                                                                         | `KOKORO_TTS_API_KEY`, `KOKORO_TTS_BASE_URL`                         | -                  |
| `iplocation`              | Get detailed geographical information for IP addresses                                                                                                  | -                                                                    | `requests`         |
| `latex_to_image`          | Convert LaTeX equations to images                                                                                                                      | -                                                                    | `matplotlib`       |
| `reddit_helper`           | Interact with Reddit content (posts, comments, subreddits)                                                                                             | `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`                           | `praw`             |
| `telegram_extract`        | Extract and process Telegram messages and media                                                                                                        | -                                                                    | -                  |
| `telegram_moderator`      | Advanced moderation tools for Telegram groups                                                                                                          | `BOT_TOKEN_MODERATOR`                                                | -                  |
| `web_extract`            | Smart extraction of content from web pages                                                                                                             | -                                                                    | `beautifulsoup4`   |
| `youtube_downloader`     | Download YouTube videos in various formats                                                                                                             | -                                                                    | `yt-dlp`           |

#### Environment variables
| Variable                          | Description                                                                                                                                                                                     | Default value                       |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------|
| `WOLFRAM_APP_ID`                  | Wolfram Alpha APP ID (required only for the `wolfram` plugin, you can get one [here](https://products.wolframalpha.com/simple-api/documentation))                                               | -                                   |
| `SPOTIFY_CLIENT_ID`               | Spotify app Client ID (required only for the `spotify` plugin, you can find it on the [dashboard](https://developer.spotify.com/dashboard/))                                                    | -                                   |
| `SPOTIFY_CLIENT_SECRET`           | Spotify app Client Secret (required only for the `spotify` plugin, you can find it on the [dashboard](https://developer.spotify.com/dashboard/))                                                | -                                   |
| `SPOTIFY_REDIRECT_URI`            | Spotify app Redirect URI (required only for the `spotify` plugin, you can find it on the [dashboard](https://developer.spotify.com/dashboard/))                                                 | -                                   |
| `WORLDTIME_DEFAULT_TIMEZONE`      | Default timezone to use, i.e. `Europe/Rome` (required only for the `worldtimeapi` plugin, you can get TZ Identifiers from [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)) | -                                   |
| `DUCKDUCKGO_SAFESEARCH`           | DuckDuckGo safe search (`on`, `off` or `moderate`) (optional, applies to `ddg_web_search` and `ddg_image_search`)                                                                               | `moderate`                          |
| `DEEPL_API_KEY`                   | DeepL API key (required for the `deepl` plugin, you can get one [here](https://www.deepl.com/pro-api?cta=header-pro-api))                                                                       | -                                   |
| `KOKORO_TTS_API_KEY`            | API key for KokoroTTS service                                                                                                                                                                  | -                                   |
| `KOKORO_TTS_BASE_URL`           | Base URL for KokoroTTS API                                                                                                                                                                     | `http://127.0.0.1:3000/api/v1`     |
| `REDDIT_CLIENT_ID`              | Reddit API client ID for reddit_helper plugin                                                                                                                                                   | -                                   |
| `REDDIT_CLIENT_SECRET`          | Reddit API client secret for reddit_helper plugin                                                                                                                                               | -                                   |
| `BOT_TOKEN_MODERATOR`           | Secondary bot token for moderation features                                                                                                                                                     | -                                   |
| `FLUX_API_KEY`                  | API key for Flux image generation service                                                                                                                                                       | -                                   |
| `FLUX_BASE_URL`                 | Base URL for Flux API                                                                                                                                                                           | Default Flux API URL                |
| `FLUX_IMAGE_MODEL`              | Model to use for Flux image generation                                                                                                                                                          | `black-forest-labs/FLUX.1-schnell-Free` |

### Installing
Clone the repository and navigate to the project directory:

```shell
git clone https://github.com/n3d1117/chatgpt-telegram-bot.git
cd chatgpt-telegram-bot
```

#### From Source
1. Create a virtual environment:
```shell
python -m venv venv
```

2. Activate the virtual environment:
```shell
# For Linux or macOS:
source venv/bin/activate

# For Windows:
venv\Scripts\activate
```

3. Install the dependencies using `requirements.txt` file:
```shell
pip install -r requirements.txt
```

4. Use the following command to start the bot:
```
python bot/main.py
```

#### Using Docker Compose

Run the following command to build and run the Docker image:
```shell
docker compose up
```

#### Ready-to-use Docker images
You can also use the Docker image from [Docker Hub](https://hub.docker.com/r/n3d1117/chatgpt-telegram-bot):
```shell
docker pull n3d1117/chatgpt-telegram-bot:latest
docker run -it --env-file .env n3d1117/chatgpt-telegram-bot
```

or using the [GitHub Container Registry](https://github.com/n3d1117/chatgpt-telegram-bot/pkgs/container/chatgpt-telegram-bot/):

```shell
docker pull ghcr.io/n3d1117/chatgpt-telegram-bot:latest
docker run -it --env-file .env ghcr.io/n3d1117/chatgpt-telegram-bot
```

#### Docker manual build
```shell
docker build -t chatgpt-telegram-bot .
docker run -it --env-file .env chatgpt-telegram-bot
```

#### Heroku
Here is an example of `Procfile` for deploying using Heroku (thanks [err09r](https://github.com/err09r)!):
```
worker: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python bot/main.py
```

## Changelog

### Infrastructure & Configuration Updates
#### Docker Configuration
- Added `.dockerignore` file to optimize Docker builds:
  - Excludes non-essential files: .env, .github, configuration files
  - Improves build performance and security
- Updated Dockerfile with optimizations:
  - Base image: Python 3.9-alpine for minimal footprint
  - Includes ffmpeg for audio/video processing
  - Configured Python environment variables for optimal performance:
    - PYTHONFAULTHANDLER=1 for better error tracking
    - PYTHONUNBUFFERED=1 for immediate log output
    - PYTHONDONTWRITEBYTECODE=1 to reduce image size
    - PIP_DISABLE_PIP_VERSION_CHECK=on for faster builds

#### Environment Configuration
- Added comprehensive `.env.example` with detailed configuration sections:
  - API Configuration (OpenAI, Model selection)
  - Telegram Bot Configuration (Bot tokens, channel/group IDs)
  - User Access Control (Admin and allowed user management)
  - Message Keywords and Triggers
  - Optional Features and Pricing
  - Proxy Settings
  - Image and Vision Configuration
  - Text-to-Speech Configuration
  - Conversation Settings
  - Plugin Configuration

#### Version Control
- Added `.gitignore` to exclude sensitive and generated files:
  - Python cache files (__pycache__)
  - Environment files (.env)
  - IDE files (.idea)
  - System files (.DS_Store)
  - Log directories (usage_logs)
  - Virtual environment (venv)
  - Cache directories (.cache)

### Model Support & AI Integration
#### New Model Integration
- Enhanced model support in `gpt_all_models.py`:
  - GPT-3.5 Models:
    - Base model: gpt-3.5-turbo
    - Legacy versions: 0301, 0613
    - Extended context versions: 16k variants
    
  - GPT-4 Models:
    - Standard versions: gpt-4, gpt-4-0314, gpt-4-0613
    - Extended context: 32k variants
    - Latest versions: turbo-preview, 0125-preview
    - Context window variants: 128K models
    
  - Vision-capable Models:
    - OpenAI: gpt-4o with vision capabilities
    - Google: gemini-2.0-flash for multimodal interactions
    
  - GPT-4o Specialized Models:
    - gpt-4o-mini for efficient processing
    - chatgpt-4o-latest for cutting-edge features
    - Specialized variants like gpt-4o-mini-2024-07-18
    
  - O1 Series Models:
    - Base model: o1
    - Efficient variant: o1-mini
    - Preview version: o1-preview
    
  - Third-party Models:
    - TogetherAI integrations:
      - Qwen2.5-Coder-32B-Instruct
      - Llama-3.3-70B-Instruct-Turbo
    - Google AI Studio models:
      - Gemini 2.0/2.5 variants
      - Flash and preview versions

### Core Functionality Updates
#### Server Integration
- Added Flask server integration in `main.py`:
  - Keep-alive endpoint implementation
  - Automatic health checks every 5 minutes
  - Threading support for concurrent operations
  - Configurable port settings
  - Error handling and logging

#### OpenAI Helper Enhancements
- Enhanced OpenAI helper with comprehensive features:
  - Dynamic model support with automatic capability detection
  - Smart token limit management:
    - Model-specific default limits
    - Automatic adjustment based on model capabilities
  - Function/plugin availability checking:
    - Model compatibility verification
    - Automatic fallback handling
  - Improved error handling and retry logic
  - Support for new API endpoints and features

### Environment Variable Updates
#### Deprecation Notices
- Updated environment variable naming conventions:
  - MONTHLY_USER_BUDGETS → USER_BUDGETS with BUDGET_PERIOD
    - More flexible budget period management
    - Support for daily, monthly, and all-time tracking
  - MONTHLY_GUEST_BUDGET → GUEST_BUDGET with BUDGET_PERIOD
    - Consistent with new budget system
    - Enhanced guest access control

#### New Configuration Options
- Added support for new environment variables:
  - Model-specific configurations
  - Vision and audio processing settings
  - Enhanced security options
  - Expanded plugin support
  - Performance tuning parameters

### Core Usage Tracking System Overhaul
#### Usage Tracker Module Enhancements (`usage_tracker.py`)
- Complete architectural redesign of the usage tracking system:
  - Advanced JSON-based persistent storage
  - Atomic file operations for improved data integrity
  - Enhanced error handling and logging
  - Thread-safe operations

#### Configuration Management
- Implemented dynamic configuration system:
  - Separated OpenAI and Telegram configurations
  - Role-based access control for config updates
  - Configuration validation and type conversion
  - Automatic config synchronization
  - Default value fallbacks

#### Usage Tracking Features
- Enhanced token tracking:
  - Separate tracking for input, output, and cached tokens
  - Model-specific token pricing
  - Improved cost calculation accuracy
  - Token usage statistics per conversation

- Comprehensive cost tracking:
  - Multi-period budget tracking (daily/monthly/all-time)
  - Detailed cost breakdowns by service:
    - Chat token usage
    - Image generation
    - Audio transcription
    - Vision API usage
    - Text-to-speech services
    - KokoroTTS integration

- Conversation management:
  - Multi-chat support with separate histories
  - Vision conversation tracking
  - Automatic conversation cleanup
  - Timestamp-based conversation management

#### New Tracking Capabilities
- Vision API usage tracking:
  - Token counting for vision models
  - Cost tracking per vision request
  - Vision conversation state management

- Text-to-Speech tracking:
  - Character count tracking
  - Multiple TTS model support (tts-1, tts-1-hd)
  - KokoroTTS integration with separate pricing
  - Usage statistics per TTS model

- Broadcast message handling:
  - Pending broadcast storage
  - Automatic broadcast expiration
  - Recipient counting and tracking
  - Broadcast message persistence

#### Performance Optimizations
- File I/O improvements:
  - Atomic write operations
  - Cached file reading
  - Efficient JSON handling
  - Reduced disk operations

- Memory management:
  - Optimized data structures
  - Efficient conversation storage
  - Automatic cleanup of expired data

#### Administrative Features
- Enhanced admin controls:
  - Detailed usage statistics
  - Configuration management
  - User budget control
  - System monitoring capabilities

- Reporting capabilities:
  - Detailed usage reports
  - Cost analysis tools
  - Usage trend tracking
  - Budget monitoring

## New Features Usage Guide

### JSON Translation Tool (Beta)
The bot includes a powerful JSON translation tool that helps in localizing bot responses and messages.

#### Usage:
```bash
python bot/translate_json.py <target_language> <language_code>
```
Example:
```bash
python bot/translate_json.py "Persian (Farsi)" "fa"
```

Features:
- Automatically translates missing entries while preserving existing ones
- Maintains JSON structure and placeholders
- Professional-quality translations using AI
- Progress tracking and state saving
- Cost-efficient by skipping existing translations

### Vision Features Usage
Send images to the bot in several ways:
1. Direct image upload
2. Image with caption
3. Multiple images in one message
4. Reply to image with follow-up questions

Commands:
- `/vision <model>` - Switch between vision models
- Vision models available:
  - `gpt-4o` - OpenAI's vision model
  - `gemini-2.0-flash` - Google's vision model

### Advanced TTS Features
Multiple TTS providers with different capabilities:

1. OpenAI TTS:
```
/tts <text> --voice alloy
```
Available voices: alloy, echo, fable, onyx, nova, shimmer

2. KokoroTTS:
```
/tts <text> --engine kokoro --voice af_heart
```
Features:
- Multiple voice options
- Local deployment support
- Custom voice training

3. Google TTS:
```
/tts <text> --engine google
```

### Plugin System
New plugins can be enabled in your .env file:

1. ArXiv Integration:
```
/arxiv <query> - Search papers
/paper <paper_id> - Get paper summary
```

2. YouTube Tools:
```
/ytdl <url> - Download video
/ytaudio <url> - Extract audio
```

3. Advanced Image Generation:
```
/image <prompt> [--provider dalle|flux]
```

4. LaTeX Rendering:
```
/latex <equation>
```

5. IP Location:
```
/ip <address>
```

6. Reddit Integration:
```
/reddit <url>
```

7. Web Extraction:
```
/extract <url>
```

### Usage Tracking
Monitor your usage with enhanced commands:
- `/stats` - View detailed usage statistics
- `/budget` - Check remaining budget
- `/usage` - See current period usage
- `/reset_stats` - Reset usage statistics (admin only)

### Installation
For new plugins, additional dependencies may be required:
```bash
pip install arxiv youtube_dl beautifulsoup4 praw latex2mathml
```

## Credits
- [ChatGPT](https://chat.openai.com/chat) from [OpenAI](https://openai.com)
- [python-telegram-bot](https://python-telegram-bot.org)
- [jiaaro/pydub](https://github.com/jiaaro/pydub)

## Disclaimer
This is a personal project and is not affiliated with OpenAI in any way.

## License
This project is released under the terms of the GPL 2.0 license. For more information, see the [LICENSE](LICENSE) file included in the repository.
