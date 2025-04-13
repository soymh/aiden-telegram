# Models can be found here: https://platform.openai.com/docs/models/overview
# Models gpt-3.5-turbo-0613 and  gpt-3.5-turbo-16k-0613 will be deprecated on June 13, 2024
GPT_3_MODELS = ("gpt-3.5-turbo", "gpt-3.5-turbo-0301", "gpt-3.5-turbo-0613")
GPT_3_16K_MODELS = ("gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-0125")
GPT_4_MODELS = ("gpt-4", "gpt-4-0314", "gpt-4-0613", "gpt-4-turbo-preview")
GPT_4_32K_MODELS = ("gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-0613")
GPT_4_VISION_MODELS = ("gpt-4o",)
GPT_4_128K_MODELS = ("gpt-4-1106-preview", "gpt-4-0125-preview", "gpt-4-turbo-preview", "gpt-4-turbo", "gpt-4-turbo-2024-04-09")
GPT_4O_MODELS = ("gpt-4o", "gpt-4o-mini", "gpt-4o-mini-2024-07-18", "chatgpt-4o-latest")
O_MODELS = ("o1", "o1-mini", "o1-preview")

#TogetherAI Models;Put your desired models from TogetherAI models here
GPT_TOGETHERAI_MODELS = ("Qwen/Qwen2.5-Coder-32B-Instruct","meta-llama/Llama-3.3-70B-Instruct-Turbo")

GPT_OPENROUTER_MODELS = ("google/gemini-2.0-flash-exp:free","google/gemini-2.5-pro-exp-03-25:free")

GPT_ALL_MODELS = GPT_3_MODELS + GPT_3_16K_MODELS + GPT_4_MODELS \
    + GPT_4_32K_MODELS + GPT_4_VISION_MODELS + GPT_4_128K_MODELS \
    + GPT_4O_MODELS + O_MODELS + GPT_TOGETHERAI_MODELS + GPT_OPENROUTER_MODELS
