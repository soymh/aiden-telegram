import os.path
import pathlib
import json
from datetime import date

def year_month(date_str):
    # extract string of year-month from date, eg: '2023-03'
    return str(date_str)[:7]

model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini-2024-07-18')


class UsageTracker:
    """
    UsageTracker class
    Enables tracking of daily/monthly usage per user.
    User files are stored as JSON in /usage_logs directory.
    JSON example:
    {
        "user_name": "@user_name",
        "current_cost": {
            "day": 0.45,
            "month": 3.23,
            "all_time": 3.23,
            "last_update": "2023-03-14"},
        "usage_history": {
            "chat_tokens": {
                "2023-03-13": 520,
                "2023-03-14": 1532
            },
            "transcription_seconds": {
                "2023-03-13": 125,
                "2023-03-14": 64
            },
            "number_images": {
                "2023-03-12": [0, 2, 3],
                "2023-03-13": [1, 2, 3],
                "2023-03-14": [0, 1, 2]
            }
        }
    }
    """

    def __init__(self, user_id, user_name, default_max_tokens=None, are_functions_available=None, logs_dir="user_logs"):
        """
        Initializes UsageTracker for a user with current date.
        Loads usage data from usage log file.
        :param user_id: Telegram ID of the user
        :param user_name: Telegram user name
        :param logs_dir: path to directory of usage logs, defaults to "usage_logs"
        """
        self.are_functions_available = are_functions_available
        self.default_max_tokens = default_max_tokens
        self.functions_available = self.are_functions_available(model=model) if self.are_functions_available else True
        self.max_tokens_default = self.default_max_tokens(model=model) if self.default_max_tokens else 1200
        self.user_id = user_id
        self.logs_dir = logs_dir
        # path to usage file of given user
        self.user_file = f"{logs_dir}/{user_id}.json"

        self.openai_config = {
            # API Configuration
            'api_key': os.environ['OPENAI_API_KEY'],
            'model': model,
            
            # Proxy Settings
            'proxy': os.environ.get('PROXY', None) or os.environ.get('OPENAI_PROXY', None),
            
            # Conversation Settings
            'assistant_prompt': os.environ.get('ASSISTANT_PROMPT', 'You are a helpful assistant.'),
            'max_tokens': int(os.environ.get('MAX_TOKENS', self.max_tokens_default)),
            'max_history_size': int(os.environ.get('MAX_HISTORY_SIZE', 15)),
            'max_conversation_age_minutes': int(os.environ.get('MAX_CONVERSATION_AGE_MINUTES', 180)),
            'temperature': float(os.environ.get('TEMPERATURE', 1.0)),
            'presence_penalty': float(os.environ.get('PRESENCE_PENALTY', 0.0)),
            'frequency_penalty': float(os.environ.get('FREQUENCY_PENALTY', 0.0)),
            'n_choices': int(os.environ.get('N_CHOICES', 1)),
            'show_usage': os.environ.get('SHOW_USAGE', 'false').lower() == 'true',
            'stream': os.environ.get('STREAM', 'true').lower() == 'true',
            'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
            
            # Image and Vision Configuration
            'image_model': os.environ.get('IMAGE_MODEL', 'dall-e-3'),
            'image_quality': os.environ.get('IMAGE_QUALITY', 'standard'),
            'image_style': os.environ.get('IMAGE_STYLE', 'vivid'),
            'image_size': os.environ.get('IMAGE_SIZE', '1024x1024'),
            'flux_base_url': os.environ.get('FLUX_BASE_URL', 'https://api.together.xyz/v1'),
            'vision_model': os.environ.get('VISION_MODEL', 'gpt-4o'),
            'vision_prompt': os.environ.get('VISION_PROMPT', 'What is in this image'),
            'vision_detail': os.environ.get('VISION_DETAIL', 'auto'),
            'vision_max_tokens': int(os.environ.get('VISION_MAX_TOKENS', '300')),
            'enable_vision_follow_up_questions': os.environ.get('ENABLE_VISION_FOLLOW_UP_QUESTIONS', 'true').lower() == 'true',
            
            # Text-to-Speech (TTS) Configuration
            'tts_model': os.environ.get('TTS_MODEL', 'tts-1'),
            'tts_voice': os.environ.get('TTS_VOICE', 'alloy'),
            
            # Additional (Optional) Settings
            'whisper_prompt': os.environ.get('WHISPER_PROMPT', ''),
            
            # Plugin and Functionality Settings
            'enable_functions': os.environ.get('ENABLE_FUNCTIONS', str(self.functions_available)).lower() == 'true',
            'functions_max_consecutive_calls': int(os.environ.get('FUNCTIONS_MAX_CONSECUTIVE_CALLS', 10)),
            'show_plugins_used': os.environ.get('SHOW_PLUGINS_USED', 'false').lower() == 'true',
        }

        # Telegram configuration re-ordered by sections
        self.telegram_config = {
            # Telegram Bot Configuration
            # 'token': os.environ['TELEGRAM_BOT_TOKEN'],
            'mod_bot_token': os.environ.get("MODRATOR_TOKEN", ""),  # maps to BOT_TOKEN_MODERATOR
            'channel_id': os.environ.get('CHANNEL_ID', ""),
            'group_id': os.environ.get('GROUP_ID', ""),
            
            # User Access Control
            'admin_user_id': os.environ.get('ADMIN_USER_IDS', '-'),
            # 'allowed_user_ids': ','.join(allowed_user_ids_list) if allowed_user_ids_list != [] else os.environ.get('ADMIN_USER_IDS', '-'),
            'is_admin': False,
            'is_allowed': False,


            # Message Keywords and Triggers
            'group_trigger_keyword': os.environ.get('GROUP_TRIGGER_KEYWORD', ''),
            'mod_trigger_keyword': os.environ.get('MOD_TRIGGER_KEYWORD', ''),
            'allow_group_users': os.environ.get('ALLOW_GROUP_USERS','false').lower() == 'true',
            'forward_keyword': 'forward it:',
            
            # Optional Features and Pricing
            'enable_quoting': os.environ.get('ENABLE_QUOTING', 'true').lower() == 'true',
            'enable_image_generation': os.environ.get('ENABLE_IMAGE_GENERATION', 'true').lower() == 'true',
            'enable_transcription': os.environ.get('ENABLE_TRANSCRIPTION', 'true').lower() == 'true',
            'enable_vision': os.environ.get('ENABLE_VISION', 'true').lower() == 'true',
            'enable_tts_generation': os.environ.get('ENABLE_TTS_GENERATION', 'true').lower() == 'true',
            'budget_period': os.environ.get('BUDGET_PERIOD', 'monthly').lower(),
            'user_budgets': os.environ.get('USER_BUDGETS', os.environ.get('MONTHLY_USER_BUDGETS', '*')),
            'guest_budget': float(os.environ.get('GUEST_BUDGET', os.environ.get('MONTHLY_GUEST_BUDGET', '100.0'))),
            'token_price': float(os.environ.get('TOKEN_PRICE', 0.002)),
            'image_prices': [float(i) for i in os.environ.get('IMAGE_PRICES', "0.016,0.018,0.02").split(",")],
            'transcription_price': float(os.environ.get('TRANSCRIPTION_PRICE', 0.006)),
            'vision_token_price': float(os.environ.get('VISION_TOKEN_PRICE', '0.01')),
            'tts_model': os.environ.get('TTS_MODEL', 'tts-1'),
            'tts_prices': [float(i) for i in os.environ.get('TTS_PRICES', "0.015,0.030").split(",")],
            
            # Proxy Settings
            'stream': os.environ.get('STREAM', 'true').lower() == 'true',
            'proxy': os.environ.get('PROXY', None) or os.environ.get('TELEGRAM_PROXY', None),
            
            # Image and Vision Configuration (for message replies)
            'voice_reply_transcript': os.environ.get('VOICE_REPLY_WITH_TRANSCRIPT_ONLY', 'false').lower() == 'true',
            'voice_reply_prompts': os.environ.get('VOICE_REPLY_PROMPTS', '').split(';'),
            'ignore_group_transcriptions': os.environ.get('IGNORE_GROUP_TRANSCRIPTIONS', 'true').lower() == 'true',
            'ignore_group_vision': os.environ.get('IGNORE_GROUP_VISION', 'true').lower() == 'true',
            'image_receive_mode': os.environ.get('IMAGE_FORMAT', "photo"),
            
            # Conversation Settings
            'bot_language': os.environ.get('BOT_LANGUAGE', 'en'),
        }



        if os.path.isfile(self.user_file):
            with open(self.user_file, "r") as file:
                self.usage = json.load(file)
            if 'vision_tokens' not in self.usage['usage_history']:
                self.usage['usage_history']['vision_tokens'] = {}
            if 'tts_characters' not in self.usage['usage_history']:
                self.usage['usage_history']['tts_characters'] = {}
        else:
            # ensure directory exists
            pathlib.Path(logs_dir).mkdir(exist_ok=True)
            # create new dictionary for this user
            self.usage = {
                "user_name": user_name,
                "current_cost": {"day": 0.0, "month": 0.0, "all_time": 0.0, "last_update": str(date.today())},
                "usage_history": {"chat_tokens": {}, "transcription_seconds": {}, "number_images": {}, "tts_characters": {}, "vision_tokens":{}},
                "openai_config": self.openai_config,
                "telegram_config": self.telegram_config
            }
            

    def add_new_user(self):
        """
        Write the new user json file.
        """
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)



    def convert_value(self, new_val_str, current_val):
        """
        Converts new_val_str into the type of current_val.
        """
        try:
            if isinstance(current_val, bool):
                return new_val_str.lower() == 'true'
            elif isinstance(current_val, int):
                return int(new_val_str)
            elif isinstance(current_val, float):
                return float(new_val_str)
            elif isinstance(current_val, list):
                # Assume comma-separated values
                if current_val and isinstance(current_val[0], float):
                    return [float(item.strip()) for item in new_val_str.split(',')]
                elif current_val and isinstance(current_val[0], int):
                    return [int(item.strip()) for item in new_val_str.split(',')]
                else:
                    return [item.strip() for item in new_val_str.split(',')]
            else:
                return new_val_str
        except Exception as e:
            # In case of conversion error, return the raw string
            return new_val_str

    def update_openai_config(self, is_admin:bool, key: str, new_val_str: str) -> bool:
        """
        Updates an OpenAI configuration value if the key is allowed.
        
        Allowed keys:
        assistant_prompt, max_history_size, max_conversation_age_minutes,
        temperature, show_usage, stream, bot_language, image_model, image_quality,
        image_style, flux_base_url, vision_model, vision_prompt, tts_model, tts_voice,
        enable_functions, functions_max_consecutive_calls, show_plugins_used
        
        Returns True if the update was successful, else False.
        """
        admin_allowed_keys = {
            'assistant_prompt', 'max_history_size', 'max_conversation_age_minutes',
            'temperature', 'show_usage', 'stream', 'bot_language', 'image_model',
            'image_quality', 'image_style', 'flux_base_url', 'vision_model', 'vision_prompt',
            'tts_model', 'tts_voice', 'enable_functions', 'functions_max_consecutive_calls',
            'show_plugins_used'
        }

        allowed_keys = {
            'assistant_prompt', 'max_history_size', 'max_conversation_age_minutes',
            'temperature', 'show_usage', 'stream', 'bot_language', 'image_model',
            'image_quality', 'image_style', 'flux_base_url', 'vision_model', 'vision_prompt',
            'tts_model', 'tts_voice', 'enable_functions', 'functions_max_consecutive_calls',
            'show_plugins_used'
        }
        if is_admin:
            if key not in admin_allowed_keys:
                return False
            if key not in self.usage['openai_config']:
                return False
        else:
            if key not in allowed_keys:
                return False
            if key not in self.usage['openai_config']:
                return False
        current_val = self.usage['openai_config'][key]
        new_val = self.convert_value(new_val_str, current_val)
        self.usage['openai_config'][key] = new_val
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)
    def update_telegram_config(self, is_admin:bool, key: str, new_val_str: str) -> bool:
        """
        Updates a Telegram configuration value if the key is allowed.
        
        Allowed keys:
        mod_bot_token, group_trigger_keyword, mod_trigger_keyword,
        allow_group_users, budget_period, user_budgets, bot_language
        
        Returns True if the update was successful, else False.
        """
        allowed_keys = {
            'mod_bot_token', 'group_id' , 'group_trigger_keyword', 'mod_trigger_keyword',
            'allow_group_users', 'budget_period', 'user_budgets', 'bot_language'
        }
        allowed_keys_admin = {
            'mod_bot_token', 'group_id' , 'group_trigger_keyword', 'mod_trigger_keyword',
            'allow_group_users', 'budget_period', 'user_budgets', 'bot_language' , 'is_allowed'
        }
        if is_admin:    
            if key not in allowed_keys_admin:
                return False
            if key not in self.usage['telegram_config']:
                return False
        else:
            if key not in allowed_keys:
                return False
            if key not in self.usage['telegram_config']:
                return False
        current_val = self.usage['telegram_config'][key]
        new_val = self.convert_value(new_val_str, current_val)
        self.usage['telegram_config'][key] = new_val
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def retrieve_config_value(self, config_type: str, key: str):
        """
        Retrieves the configuration value for the given key from either the OpenAI or Telegram configuration.

        Parameters:
            config_type (str): Either "openai" or "telegram" (case-insensitive).
            key (str): The key whose value you wish to retrieve.

        Returns:
            The value corresponding to the key if it exists, or None if the key is not found or the config_type is invalid.
        """
        config_type = config_type.lower()
        if config_type == 'openai':
            config = self.usage.get('openai_config', {})
        elif config_type == 'telegram':
            config = self.usage.get('telegram_config', {})
        else:
            # Invalid configuration type specified.
            return None

        return config.get(key)

    def return_configs(self, config_type: str):
        """
        Return the config file specified for Updating default config whenever a new message received.
        """
        if config_type == 'openai':
            return self.usage['openai_config']
        if config_type == 'telegram':
            return self.usage['telegram_config']
        else:
            return None




    def add_chat_tokens(self, tokens, tokens_price=0.002):
        """Adds used tokens from a request to a users usage history and updates current cost
        :param tokens: total tokens used in last request
        :param tokens_price: price per 1000 tokens, defaults to 0.002
        """
        today = date.today()
        token_cost = round(float(tokens) * tokens_price / 1000, 6)
        self.add_current_costs(token_cost)

        # update usage_history
        if str(today) in self.usage["usage_history"]["chat_tokens"]:
            # add token usage to existing date
            self.usage["usage_history"]["chat_tokens"][str(today)] += tokens
        else:
            # create new entry for current date
            self.usage["usage_history"]["chat_tokens"][str(today)] = tokens

        # write updated token usage to user file
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def get_current_token_usage(self):
        """Get token amounts used for today and this month

        :return: total number of tokens used per day and per month
        """
        today = date.today()
        if str(today) in self.usage["usage_history"]["chat_tokens"]:
            usage_day = self.usage["usage_history"]["chat_tokens"][str(today)]
        else:
            usage_day = 0
        month = str(today)[:7]  # year-month as string
        usage_month = 0
        for today, tokens in self.usage["usage_history"]["chat_tokens"].items():
            if today.startswith(month):
                usage_month += tokens
        return usage_day, usage_month

    # image usage functions:

    def add_image_request(self, image_size, image_prices="0.016,0.018,0.02"):
        """Add image request to users usage history and update current costs.

        :param image_size: requested image size
        :param image_prices: prices for images of sizes ["256x256", "512x512", "1024x1024"],
                             defaults to [0.016, 0.018, 0.02]
        """
        sizes = ["256x256", "512x512", "1024x1024"]
        requested_size = sizes.index(image_size)
        image_cost = image_prices[requested_size]
        today = date.today()
        self.add_current_costs(image_cost)

        # update usage_history
        if str(today) in self.usage["usage_history"]["number_images"]:
            # add token usage to existing date
            self.usage["usage_history"]["number_images"][str(today)][requested_size] += 1
        else:
            # create new entry for current date
            self.usage["usage_history"]["number_images"][str(today)] = [0, 0, 0]
            self.usage["usage_history"]["number_images"][str(today)][requested_size] += 1

        # write updated image number to user file
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def get_current_image_count(self):
        """Get number of images requested for today and this month.

        :return: total number of images requested per day and per month
        """
        today = date.today()
        if str(today) in self.usage["usage_history"]["number_images"]:
            usage_day = sum(self.usage["usage_history"]["number_images"][str(today)])
        else:
            usage_day = 0
        month = str(today)[:7]  # year-month as string
        usage_month = 0
        for today, images in self.usage["usage_history"]["number_images"].items():
            if today.startswith(month):
                usage_month += sum(images)
        return usage_day, usage_month


    # vision usage functions
    def add_vision_tokens(self, tokens, vision_token_price=0.01):
        """
         Adds requested vision tokens to a users usage history and updates current cost.
        :param tokens: total tokens used in last request
        :param vision_token_price: price per 1K tokens transcription, defaults to 0.01
        """
        today = date.today()
        token_price = round(tokens * vision_token_price / 1000, 2)
        self.add_current_costs(token_price)

        # update usage_history
        if str(today) in self.usage["usage_history"]["vision_tokens"]:
            # add requested seconds to existing date
            self.usage["usage_history"]["vision_tokens"][str(today)] += tokens
        else:
            # create new entry for current date
            self.usage["usage_history"]["vision_tokens"][str(today)] = tokens

        # write updated token usage to user file
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def get_current_vision_tokens(self):
        """Get vision tokens for today and this month.

        :return: total amount of vision tokens per day and per month
        """
        today = date.today()
        if str(today) in self.usage["usage_history"]["vision_tokens"]:
            tokens_day = self.usage["usage_history"]["vision_tokens"][str(today)]
        else:
            tokens_day = 0
        month = str(today)[:7]  # year-month as string
        tokens_month = 0
        for today, tokens in self.usage["usage_history"]["vision_tokens"].items():
            if today.startswith(month):
                tokens_month += tokens
        return tokens_day, tokens_month

    # tts usage functions:

    def add_tts_request(self, text_length, tts_model, tts_prices):
        tts_models = ['tts-1', 'tts-1-hd']
        price = tts_prices[tts_models.index(tts_model)]
        today = date.today()
        tts_price = round(text_length * price / 1000, 2)
        self.add_current_costs(tts_price)

        if 'tts_characters' not in self.usage['usage_history']:
            self.usage['usage_history']['tts_characters'] = {}
        
        if tts_model not in self.usage['usage_history']['tts_characters']:
            self.usage['usage_history']['tts_characters'][tts_model] = {}

        # update usage_history
        if str(today) in self.usage["usage_history"]["tts_characters"][tts_model]:
            # add requested text length to existing date
            self.usage["usage_history"]["tts_characters"][tts_model][str(today)] += text_length
        else:
            # create new entry for current date
            self.usage["usage_history"]["tts_characters"][tts_model][str(today)] = text_length

        # write updated token usage to user file
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def get_current_tts_usage(self):
        """Get length of speech generated for today and this month.

        :return: total amount of characters converted to speech per day and per month
        """

        tts_models = ['tts-1', 'tts-1-hd']
        today = date.today()
        characters_day = 0
        for tts_model in tts_models:
            if tts_model in self.usage["usage_history"]["tts_characters"] and \
                str(today) in self.usage["usage_history"]["tts_characters"][tts_model]:
                characters_day += self.usage["usage_history"]["tts_characters"][tts_model][str(today)]

        month = str(today)[:7]  # year-month as string
        characters_month = 0
        for tts_model in tts_models:
            if tts_model in self.usage["usage_history"]["tts_characters"]: 
                for today, characters in self.usage["usage_history"]["tts_characters"][tts_model].items():
                    if today.startswith(month):
                        characters_month += characters
        return int(characters_day), int(characters_month)


    # transcription usage functions:

    def add_transcription_seconds(self, seconds, minute_price=0.006):
        """Adds requested transcription seconds to a users usage history and updates current cost.
        :param seconds: total seconds used in last request
        :param minute_price: price per minute transcription, defaults to 0.006
        """
        today = date.today()
        transcription_price = round(seconds * minute_price / 60, 2)
        self.add_current_costs(transcription_price)

        # update usage_history
        if str(today) in self.usage["usage_history"]["transcription_seconds"]:
            # add requested seconds to existing date
            self.usage["usage_history"]["transcription_seconds"][str(today)] += seconds
        else:
            # create new entry for current date
            self.usage["usage_history"]["transcription_seconds"][str(today)] = seconds

        # write updated token usage to user file
        with open(self.user_file, "w") as outfile:
            json.dump(self.usage, outfile)

    def add_current_costs(self, request_cost):
        """
        Add current cost to all_time, day and month cost and update last_update date.
        """
        today = date.today()
        last_update = date.fromisoformat(self.usage["current_cost"]["last_update"])

        # add to all_time cost, initialize with calculation of total_cost if key doesn't exist
        self.usage["current_cost"]["all_time"] = \
            self.usage["current_cost"].get("all_time", self.initialize_all_time_cost()) + request_cost
        # add current cost, update new day
        if today == last_update:
            self.usage["current_cost"]["day"] += request_cost
            self.usage["current_cost"]["month"] += request_cost
        else:
            if today.month == last_update.month:
                self.usage["current_cost"]["month"] += request_cost
            else:
                self.usage["current_cost"]["month"] = request_cost
            self.usage["current_cost"]["day"] = request_cost
            self.usage["current_cost"]["last_update"] = str(today)

    def get_current_transcription_duration(self):
        """Get minutes and seconds of audio transcribed for today and this month.

        :return: total amount of time transcribed per day and per month (4 values)
        """
        today = date.today()
        if str(today) in self.usage["usage_history"]["transcription_seconds"]:
            seconds_day = self.usage["usage_history"]["transcription_seconds"][str(today)]
        else:
            seconds_day = 0
        month = str(today)[:7]  # year-month as string
        seconds_month = 0
        for today, seconds in self.usage["usage_history"]["transcription_seconds"].items():
            if today.startswith(month):
                seconds_month += seconds
        minutes_day, seconds_day = divmod(seconds_day, 60)
        minutes_month, seconds_month = divmod(seconds_month, 60)
        return int(minutes_day), round(seconds_day, 2), int(minutes_month), round(seconds_month, 2)

    # general functions
    def get_current_cost(self):
        """Get total USD amount of all requests of the current day and month

        :return: cost of current day and month
        """
        today = date.today()
        last_update = date.fromisoformat(self.usage["current_cost"]["last_update"])
        if today == last_update:
            cost_day = self.usage["current_cost"]["day"]
            cost_month = self.usage["current_cost"]["month"]
        else:
            cost_day = 0.0
            if today.month == last_update.month:
                cost_month = self.usage["current_cost"]["month"]
            else:
                cost_month = 0.0
        # add to all_time cost, initialize with calculation of total_cost if key doesn't exist
        cost_all_time = self.usage["current_cost"].get("all_time", self.initialize_all_time_cost())
        return {"cost_today": cost_day, "cost_month": cost_month, "cost_all_time": cost_all_time}

    def initialize_all_time_cost(self, tokens_price=0.002, image_prices="0.016,0.018,0.02", minute_price=0.006, vision_token_price=0.01, tts_prices='0.015,0.030'):
        """Get total USD amount of all requests in history
        
        :param tokens_price: price per 1000 tokens, defaults to 0.002
        :param image_prices: prices for images of sizes ["256x256", "512x512", "1024x1024"],
            defaults to [0.016, 0.018, 0.02]
        :param minute_price: price per minute transcription, defaults to 0.006
        :param vision_token_price: price per 1K vision token interpretation, defaults to 0.01
        :param tts_prices: price per 1K characters tts per model ['tts-1', 'tts-1-hd'], defaults to [0.015, 0.030]
        :return: total cost of all requests
        """
        total_tokens = sum(self.usage['usage_history']['chat_tokens'].values())
        token_cost = round(total_tokens * tokens_price / 1000, 6)

        total_images = [sum(values) for values in zip(*self.usage['usage_history']['number_images'].values())]
        image_prices_list = [float(x) for x in image_prices.split(',')]
        image_cost = sum([count * price for count, price in zip(total_images, image_prices_list)])

        total_transcription_seconds = sum(self.usage['usage_history']['transcription_seconds'].values())
        transcription_cost = round(total_transcription_seconds * minute_price / 60, 2)

        total_vision_tokens = sum(self.usage['usage_history']['vision_tokens'].values())
        vision_cost = round(total_vision_tokens * vision_token_price / 1000, 2)

        total_characters = [sum(tts_model.values()) for tts_model in self.usage['usage_history']['tts_characters'].values()]
        tts_prices_list = [float(x) for x in tts_prices.split(',')]
        tts_cost = round(sum([count * price / 1000 for count, price in zip(total_characters, tts_prices_list)]), 2)

        all_time_cost = token_cost + transcription_cost + image_cost + vision_cost + tts_cost
        return all_time_cost
