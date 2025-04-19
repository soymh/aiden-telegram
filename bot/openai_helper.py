from __future__ import annotations
import datetime
import logging
import os

import tiktoken

import openai

import json
import httpx
import io
from PIL import Image

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from utils import is_direct_result, encode_image, decode_image
from plugin_manager import PluginManager

#import requests for TogetherAI
import requests

from usage_tracker import UsageTracker

from gpt_all_models import GPT_ALL_MODELS, GPT_3_MODELS, GPT_3_16K_MODELS,\
    GPT_4_MODELS, GPT_4_32K_MODELS, VISION_MODELS, \
    GPT_4_128K_MODELS, GPT_4O_MODELS, O_MODELS, \
    GOOGLE_AI_STUDIO_MODELS

#TogetherAI Models;Put your desired models from TogetherAI models here
GPT_TOGETHERAI_MODELS = ("Qwen/Qwen2.5-Coder-32B-Instruct","meta-llama/Llama-3.3-70B-Instruct-Turbo")


def default_max_tokens(model: str) -> int:
    """
    Gets the default number of max tokens for the given model.
    :param model: The model name
    :return: The default number of max tokens
    """
    base = 1200
    if model in GPT_3_MODELS:
        return base
    elif model in GPT_4_MODELS:
        return base * 2
    elif model in GPT_3_16K_MODELS:
        if model == "gpt-3.5-turbo-1106":
            return 4096
        return base * 4
    elif model in GPT_4_32K_MODELS:
        return base * 8
    elif model in VISION_MODELS:
        return 4096
    elif model in GPT_4_128K_MODELS:
        return 4096
    elif model in GPT_4O_MODELS:
        return 4096
    elif model in O_MODELS:
        return 4096
    else :
        return 4096


def are_functions_available(model: str) -> bool:
    """
    Whether the given model supports functions
    """
    if model in ("gpt-3.5-turbo-0301", "gpt-4-0314", "gpt-4-32k-0314", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-16k-0613"):
        return False
    if model in O_MODELS:
        return False
    return True


# Load translations
parent_dir_path = os.path.join(os.path.dirname(__file__), os.pardir)
translations_file_path = os.path.join(parent_dir_path, 'translations.json')
with open(translations_file_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)


# def localized_text(key, bot_language):
#     """
#     Return translated text for a key in specified bot_language.
#     Keys and translations can be found in the translations.json.
#     """
#     try:
#         return translations[bot_language][key]
#     except KeyError:
#         logging.warning(f"No translation available for bot_language code '{bot_language}' and key '{key}'")
#         # Fallback to English if the translation is not available
#         if key in translations['en']:
#             return translations['en'][key]
#         else:
#             logging.warning(f"No english definition found for key '{key}' in translations.json")
#             # return key as text
#             return key

model = os.environ.get('OPENAI_MODEL', 'gemini-2.0-flash')
functions_available = are_functions_available(model=model)
max_tokens_default = default_max_tokens(model=model)

class OpenAIHelper:
    """
    ChatGPT helper class.
    """
    def __init__(self, plugin_manager: PluginManager):
        """
        Initializes the OpenAI helper class with the given configuration.
        :param config: A dictionary containing the GPT configuration
        :param plugin_manager: The plugin manager
        """
        self.user_id = int()
        self.username = ""
        self.usage = {}
        self.chat_id = int()
        self.usage[self.user_id] = UsageTracker(self.user_id, self.username, self.chat_id)
        self.config =  self.usage[self.user_id].return_configs('openai')
        done, self.channel_id = self.usage[self.user_id].retrieve_config_value('telegram', 'channel_id', True)
        done, self.group_id = self.usage[self.user_id].retrieve_config_value('telegram', 'group_id', True)
        done, self.mod_bot_token = self.usage[self.user_id].retrieve_config_value('telegram', 'mod_bot_token', True)

        http_client = httpx.AsyncClient(proxy=self.config['proxy']) if 'proxy' in self.config else None
        self.client = openai.AsyncOpenAI(api_key=self.config['api_key'], http_client=http_client)

        self.media_client = openai.AsyncOpenAI(api_key=self.config['openai_media_api_key'],base_url=self.config['openai_media_base_url'], http_client=http_client)

        self.plugin_manager = plugin_manager
        self.conversations: dict[int: list] = {}
        self.conversations_vision: dict[int: bool] = {}
        self.last_updated: dict[int: str] = {}

        self.logs_dir = "user_logs"
        self.logger = self.create_user_logger(self.user_id)

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        # Check if the attribute change should trigger the call.
        # For example, you might trigger it for changes to config-related keys.
        if name in {"config", "usage", "conversations", "conversations_vision", "last_updated"}:
            # Ensure user_id exists before calling
            if hasattr(self, "user_id") and self.user_id in self.usage:
                self.usage[self.user_id].save_state()

    def user_update(self, user_id, username, chat_id):
        """
        set the default user id
        """
        self.user_id = user_id
        self.username = username
        self.chat_id = chat_id
        self.logger = self.create_user_logger(self.user_id)
        self.usage[self.user_id] = UsageTracker(self.user_id , self.username, self.chat_id)
        self.config = self.usage[self.user_id].return_configs('openai')
        done, self.channel_id = self.usage[self.user_id].retrieve_config_value('telegram', 'channel_id', True)
        done, self.group_id = self.usage[self.user_id].retrieve_config_value('telegram', 'group_id', True)
        done, self.mod_bot_token = self.usage[self.user_id].retrieve_config_value('telegram', 'mod_bot_token', True)
        self.conversations = self.usage[self.user_id].do_conversations(chat_id=chat_id)
        self.conversations_vision = self.usage[self.user_id].do_vision_conversations()
        self.last_updated = self.usage[self.user_id].do_last_updated()

        http_client = httpx.AsyncClient(proxy=self.config['proxy']) if 'proxy' in self.config else None
        self.client = openai.AsyncOpenAI(api_key=self.config['api_key'], http_client=http_client)

        self.media_client = openai.AsyncOpenAI(api_key=self.config['openai_media_api_key'],base_url=self.config['openai_media_base_url'], http_client=http_client)

    def create_user_logger(self, user_id):
        # Create a logger for the user if it doesn't exist
        logger = logging.getLogger(f"user_{user_id}")
        
        # Check if the logger already has handlers
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Create a file handler for the user's log file
            log_file_path = os.path.join(self.logs_dir, str(user_id),f"user_{user_id}.log")
            handler = logging.FileHandler(log_file_path, mode='a')
            formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")
            handler.setFormatter(formatter)
            
            # Add the handler to the logger
            logger.addHandler(handler)
        
        return logger

    def localized_text(self, key, bot_language):
        """
        Return translated text for a key in specified bot_language.
        Keys and translations can be found in the translations.json.
        """
        try:
            return translations[bot_language][key]
        except KeyError:
            self.logger.warning(f"No translation available for bot_language code '{bot_language}' and key '{key}'")
            # Fallback to English if the translation is not available
            if key in translations['en']:
                return translations['en'][key]
            else:
                self.logger.warning(f"No english definition found for key '{key}' in translations.json")
                # return key as text
                return key
                
    def get_conversation_stats(self, user_id: int, username: str, chat_id: int) -> tuple[int, int]:
        """
        Gets the number of messages and tokens used in the conversation.
        :param chat_id: The chat ID
        :return: A tuple containing the number of messages and tokens used
        """

        self.user_update(user_id,username,chat_id)

        if str(chat_id) not in self.conversations:
            self.reset_chat_history(self.user_id, self.username, chat_id)
        return len(self.conversations[str(chat_id)]), self.__count_tokens(self.conversations[str(chat_id)])

    async def get_chat_response(self, user_id: int, username: str, chat_id: int,role:str, query: str , super_access=False) -> tuple[str, str]:
        """
        Gets a full response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """

        self.user_update(user_id, username, chat_id)

        plugins_used = ()
        response = await self.__common_get_chat_response(self.user_id, self.username, chat_id, role, query)
        if self.config['enable_functions'] and not self.conversations_vision[str(chat_id)]:
            response, plugins_used = await self.__handle_function_call(user_id=self.user_id, username=self.username, chat_id=chat_id, response=response, super_access=super_access)
            if is_direct_result(response):
                return response, '0', '0', '0'

        answer = ''

        if len(response.choices) > 1 and self.config['n_choices'] > 1:
            for index, choice in enumerate(response.choices):
                content = choice.message.content.strip()
                if index == 0:
                    self.add_to_history(self.user_id, self.username, chat_id, role="assistant", content=content)
                answer += f'{index + 1}\u20e3\n'
                answer += content
                answer += '\n\n'
        else:
            if response.choices[0].message.content:
                answer = response.choices[0].message.content.strip()
            else:
                answer = "None"
            self.add_to_history(self.user_id, self.username, chat_id, role="assistant", content=answer)

        bot_language = self.config['bot_language']
        show_plugins_used = len(plugins_used) > 0 and self.config['show_plugins_used']
        plugin_names = tuple(self.plugin_manager.get_plugin_source_name(plugin) for plugin in plugins_used)
        if self.config['show_usage']:
            answer += "\n\n---\n" \
                      f"💰 {str(response.usage.total_tokens)} {self.localized_text('stats_tokens', bot_language)}" \
                      f" ({str(response.usage.prompt_tokens)} {self.localized_text('prompt', bot_language)}," \
                      f" {str(response.usage.completion_tokens)} {self.localized_text('completion', bot_language)})"
            if show_plugins_used:
                answer += f"\n🔌 {', '.join(plugin_names)}"
        elif show_plugins_used:
            answer += f"\n\n---\n🔌 {', '.join(plugin_names)}"

        cached_tokens = getattr(response.usage.prompt_tokens_details, 'cached_tokens', 0)
        completion_tokens = getattr(response.usage, 'completion_tokens', 0)
        prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
        return answer, prompt_tokens, completion_tokens, cached_tokens

    async def get_chat_response_stream(self, user_id: int, username: str, chat_id: int, role:str, query: str,super_access=False):
        """
        Stream response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used, or 'not_finished'
        """
        self.user_update(user_id, username, chat_id)

        plugins_used = ()
        response = await self.__common_get_chat_response(self.user_id, self.username, self.chat_id, role, query, stream=True)
        if self.config['enable_functions'] and not self.conversations_vision[chat_id]:
            response, plugins_used = await self.__handle_function_call(user_id=self.user_id, username=self.username, chat_id=chat_id, response=response, stream=True,super_access=super_access)
            if is_direct_result(response):
                yield response, '0'
                return

        answer = ''
        async for chunk in response:
            if len(chunk.choices) == 0:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                answer += delta.content
                yield answer, 'not_finished'
        answer = answer.strip()
        self.add_to_history(self.user_id, self.username, chat_id, role=role, content=answer)
        tokens_used = str(self.__count_tokens(self.conversations[chat_id]))

        show_plugins_used = len(plugins_used) > 0 and self.config['show_plugins_used']
        plugin_names = tuple(self.plugin_manager.get_plugin_source_name(plugin) for plugin in plugins_used)
        if self.config['show_usage']:
            answer += f"\n\n---\n💰 {tokens_used} {self.localized_text('stats_tokens', self.config['bot_language'])}"
            if show_plugins_used:
                answer += f"\n🔌 {', '.join(plugin_names)}"
        elif show_plugins_used:
            answer += f"\n\n---\n🔌 {', '.join(plugin_names)}"

        yield answer, tokens_used


    @retry(
        reraise=True,
        retry=retry_if_exception_type(openai.RateLimitError),
        wait=wait_fixed(20),
        stop=stop_after_attempt(3)
    )
    async def __common_get_chat_response(self, user_id: int, username: str, chat_id: int, role:str, query: str, stream=False):
        """
        Request a response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        self.user_update(user_id, username, chat_id)

        bot_language = self.config['bot_language']
        try:
            if self.conversations[self.chat_id]==[] or self.__max_age_reached(self.user_id, self.username, self.chat_id):
                self.reset_chat_history(self.user_id, self.username, self.chat_id)

            self.last_updated[self.chat_id] = str(datetime.datetime.now())

            self.add_to_history(self.user_id, self.username, self.chat_id, role=role, content=query)

            # Summarize the chat history if it's too long to avoid excessive token usage
            # token_count = self.__count_tokens(self.conversations[self.chat_id])
            # exceeded_max_tokens = token_count + self.config['max_tokens'] > self.__max_model_tokens()
            exceeded_max_history_size = len(self.conversations[self.chat_id]) > self.config['max_history_size']

            if exceeded_max_history_size:
                self.logger.info(f'Chat history for chat ID {self.chat_id} is too long. Summarising...')
                try:
                    summary = await self.__summarise(self.user_id, self.username, self.conversations[self.chat_id][:-1])
                    self.logger.debug(f'Summary: {summary}')
                    self.reset_chat_history(self.user_id, self.username, self.chat_id, self.conversations[self.chat_id][0]['content'])
                    self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=summary)
                    self.add_to_history(self.user_id, self.username, self.chat_id, role="user", content=query)
                except Exception as e:
                    self.logger.warning(f'Error while summarising chat history: {str(e)}. Popping elements instead...')
                    self.conversations[self.chat_id] = self.conversations[self.chat_id][-self.config['max_history_size']:]

            max_tokens_str = 'max_completion_tokens' if self.config['model'] in O_MODELS else 'max_tokens'
            common_args = {
                'model': self.config['model'] if not self.conversations_vision[str(self.chat_id)] else self.config['vision_model'],
                'messages': self.conversations[self.chat_id],
                'temperature': self.config['temperature'],
                # 'n': self.config['n_choices'],
                # max_tokens_str: self.config['max_tokens'],
                # 'presence_penalty': self.config['presence_penalty'],
                # 'frequency_penalty': self.config['frequency_penalty'],
                # 'stream': stream
            }

            if self.config['enable_functions'] and not self.conversations_vision[str(self.chat_id)]:
                functions = self.plugin_manager.get_functions_specs()
                if len(functions) > 0:
                    common_args['tools'] = self.plugin_manager.get_functions_specs()
                    common_args['tool_choice'] = 'auto'
            return await self.client.chat.completions.create(**common_args)

        except openai.RateLimitError as e:
            raise e

        except openai.BadRequestError as e:
            raise Exception(f"⚠️ _{self.localized_text('openai_invalid', bot_language)}._ ⚠️\n{str(e)}") from e

        except Exception as e:
            raise Exception(f"⚠️ _{self.localized_text('error', bot_language)}._ ⚠️\n{str(e)}") from e

    async def __handle_function_call(self, user_id, username, chat_id, response, stream=False, times=0, plugins_used=(),super_access=False):
        self.user_update(user_id, username, chat_id)

        function_name = ''
        arguments = ''
        if stream:
            async for item in response:
                if len(item.choices) > 0:
                    first_choice = item.choices[0]
                    if first_choice.delta and first_choice.delta.tool_calls:
                        if first_choice.delta.tool_calls.name:
                            function_name += first_choice.delta.tool_calls.name
                        if first_choice.delta.tool_calls.arguments:
                            arguments += first_choice.delta.tool_calls.arguments
                    elif first_choice.finish_reason and first_choice.finish_reason == 'tool_calls':
                        break
                    else:
                        return response, plugins_used
                else:
                    return response, plugins_used
        else:
            first_choice = response.choices[0]
            content = first_choice.message.content
            if len(response.choices) > 0:
                if first_choice.message.tool_calls:
                    if first_choice.message.tool_calls[0].function.name:
                        function_name += first_choice.message.tool_calls[0].function.name
                    if first_choice.message.tool_calls[0].function.arguments:
                        arguments += first_choice.message.tool_calls[0].function.arguments
                else:
                    return response, plugins_used
            else:
                return response, plugins_used
            self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=content if content else "None", function_call={"name": function_name})

            

        if function_name != "telegram_moderator":
            self.logger.info(f'Calling function {function_name} with arguments {arguments}')
            function_response = await self.plugin_manager.call_function(function_name, self, arguments)
        else:
            if super_access:
                    self.logger.info(f'! Super_Acess Call: Bot has called Telegram moderator function: `{function_name}` with arguments {arguments}')
                    arguments = json.loads(arguments)
                    arguments['channel_id'] = self.channel_id
                    arguments['group_id'] = self.group_id
                    arguments['mod_bot_token'] = self.mod_bot_token
                    arguments = json.dumps(arguments)
                    function_response = await self.plugin_manager.call_function(function_name, self, arguments)
            else:
                self.logger.info(f'The bot doesn\'t have access to built-in moderating plugin[s],aborting function call {function_name} with arguments {arguments}')
                function_response = json.dumps({"status": "failed", "details": "You don't have access to this function. Ask the user if they want to moderate telegram ,they have to use '/moderate' command."}, default=str)


        if function_name not in plugins_used:
            plugins_used += (function_name,)

        if is_direct_result(function_response):
            self.__add_function_call_to_history(self.user_id, self.username, chat_id=self.chat_id, function_name=function_name,
                                                content=json.dumps({'result': 'Done, the content has been sent to the user.'}))
            return function_response, plugins_used

        self.__add_function_call_to_history(self.user_id, self.username, chat_id=self.chat_id, function_name=function_name, content=function_response)
        response = await self.client.chat.completions.create(
            model=self.config['model'],
            messages=self.conversations[self.chat_id],
            tools=self.plugin_manager.get_functions_specs(),
            tool_choice='auto' if times < self.config['functions_max_consecutive_calls'] else 'none',
            stream=stream
        )
        return await self.__handle_function_call(user_id=self.user_id, username=self.username, chat_id=self.chat_id, response=response, stream=stream, times=times + 1, plugins_used=plugins_used,super_access=super_access)


    async def generate_image(self, user_id, username, chat_id, prompt: str) -> tuple[str, str]:
        """
        Generates an image from the given prompt using DALL·E model.
        :param prompt: The prompt to send to the model
        :return: The image URL and the image size
        """
        if user_id and username and chat_id:
            self.user_update(user_id, username, chat_id)
        else :
            self.logger.warning(f"Tool called for image generation")
        

        bot_language = self.config['bot_language']
        try:
            response = await self.media_client.images.generate(
                prompt=prompt,
                n=1,
                model=self.config['image_model'],
                quality=self.config['image_quality'],
                style=self.config['image_style'],
                size=self.config['image_size']
            )

            if len(response.data) == 0:
                self.logger.error(f'No response from GPT: {str(response)}')
                raise Exception(
                    f"⚠️ _{self.localized_text('error', bot_language)}._ "
                    f"⚠️\n{self.localized_text('try_again', bot_language)}."
                )

            return response.data[0].url, self.config['image_size']
        except Exception as e:
            raise Exception(f"⚠️ _{self.localized_text('error', bot_language)}._ ⚠️\n{str(e)}") from e

    async def generate_image_flux(self, user_id, username, prompt: str) -> tuple[str, str]:
        """
        Generates an image from the given prompt using FLUX model.
        :param prompt: The prompt to send to the model
        :return: The image URL and the image size
        """
        # self.user_update(user_id,username)

        bot_language = self.config['bot_language']
        flux_base_url = self.config['flux_base_url']
        try:
            # Parse the image_size string to extract width and height
            image_size_parts = self.config['image_size'].split('x')
            if len(image_size_parts) == 2:
                image_width = int(image_size_parts[0])
                image_height = int(image_size_parts[1])
            else:
                raise ValueError("Invalid image_size format. Expected format: 'widthxheight'.")

            # Prepare the request payload
            payload = {
                "model": self.config['image_model'],
                "prompt": prompt,
                "width": image_width,
                "height": image_height,
                "steps": 24,
                "n": 1,
                "response_format": "b64_json"
            }

            # Set the headers
            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }

            # Make the POST request
            response = requests.post(
                flux_base_url,
                headers=headers,
                data=json.dumps(payload)
            )

            # Check if the request was successful
            if response.status_code != 200:
                self.logger.error(f'Error from FLUX API: {response.status_code} - {response.text}')
                raise Exception(
                    f"⚠️ _{self.localized_text('error', bot_language)}._ "
                    f"⚠️\n{self.localized_text('try_again', bot_language)}."
                )

            # Parse the response JSON
            response_data = response.json()
            if 'data' not in response_data or len(response_data['data']) == 0:
                self.logger.error(f'No data in response from FLUX: {response_data}')
                raise Exception(
                    f"⚠️ _{self.localized_text('error', bot_language)}._ "
                    f"⚠️\n{self.localized_text('try_again', bot_language)}."
                )

            # Extract the b64_json data from the response
            b64_json = response_data['data'][0]['b64_json']

            # Return the b64_json data and the image size
            return b64_json, f"{image_width}x{image_height}"
        except Exception as e:
            raise Exception(f"⚠️ _{self.localized_text('error', bot_language)}._ ⚠️\n{str(e)}") from e


    async def generate_speech(self, text: str) -> tuple[any, int]:
        """
        Generates an audio from the given text using TTS model.
        :param prompt: The text to send to the model
        :return: The audio in bytes and the text size
        """
        # self.user_update(user_id,username)

        bot_language = self.config['bot_language']
        try:
            response = await self.media_client.audio.speech.create(
                model=self.config['tts_model'],
                voice=self.config['tts_voice'],
                input=text,
                response_format='opus'
            )

            temp_file = io.BytesIO()
            temp_file.write(response.read())
            temp_file.seek(0)
            return temp_file, len(text)
        except Exception as e:
            raise Exception(f"⚠️ _{self.localized_text('error', bot_language)}._ ⚠️\n{str(e)}") from e

    async def transcribe(self, user_id, username, filename):
        """
        Transcribes the audio file using the Whisper model.
        """
        # self.user_update(user_id,username)

        try:
            with open(filename, "rb") as audio:
                prompt_text = self.config['whisper_prompt']
                result = await self.media_client.audio.transcriptions.create(model="whisper-1", file=audio, prompt=prompt_text)
                return result.text
        except Exception as e:
            self.logger.exception(e)
            raise Exception(f"⚠️ _{self.localized_text('error', self.config['bot_language'])}._ ⚠️\n{str(e)}") from e

    @retry(
        reraise=True,
        retry=retry_if_exception_type(openai.RateLimitError),
        wait=wait_fixed(20),
        stop=stop_after_attempt(3)
    )
    async def __common_get_chat_response_vision(self, user_id: int, username: str, chat_id: int, content: list, stream=False):
        """
        Request a response from the GPT model.
        :param chat_id: The chat ID
        :param query: The query to send to the model
        :return: The answer from the model and the number of tokens used
        """
        self.user_update(user_id,username,chat_id)

        bot_language = self.config['bot_language']
        try:
            if str(self.chat_id) not in self.conversations or self.__max_age_reached(self.user_id, self.username, self.chat_id):
                self.reset_chat_history(self.user_id, self.username, self.chat_id)

            self.last_updated[self.chat_id] = datetime.datetime.now()

            if self.config['enable_vision_follow_up_questions']:
                self.conversations_vision[str(self.chat_id)] = True
                self.add_to_history(self.user_id, self.username, self.chat_id, role="user", content=content)
            else:
                for message in content:
                    if message['type'] == 'text':
                        query = message['text']
                        break
                self.add_to_history(self.user_id, self.username, self.chat_id, role="user", content=query)

            # Summarize the chat history if it's too long to avoid excessive token usage
            token_count = self.__count_tokens(self.conversations[self.chat_id])
            exceeded_max_tokens = token_count + self.config['max_tokens'] > self.__max_model_tokens()
            exceeded_max_history_size = len(self.conversations[self.chat_id]) > self.config['max_history_size']

            if exceeded_max_tokens or exceeded_max_history_size:
                self.logger.info(f'Chat history for chat ID {self.chat_id} is too long. Summarising...')
                try:
                    
                    last = self.conversations[self.chat_id][-1]
                    summary = await self.__summarise(self.user_id, self.username, self.conversations[self.chat_id][:-1])
                    self.logger.debug(f'Summary: {summary}')
                    self.reset_chat_history(self.user_id, self.username, self.chat_id, self.conversations[self.chat_id][0]['content'])
                    self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=summary)
                    self.conversations[self.chat_id] += [last]
                except Exception as e:
                    self.logger.warning(f'Error while summarising chat history: {str(e)}. Popping elements instead...')
                    self.conversations[self.chat_id] = self.conversations[self.chat_id][-self.config['max_history_size']:]

            message = {'role':'user', 'content':content}

            common_args = {
                'model': self.config['vision_model'],
                'messages': self.conversations[self.chat_id][:-1] + [message],
                # 'temperature': self.config['temperature'],
                # 'n': 1, # several choices is not implemented yet
                # 'max_tokens': self.config['vision_max_tokens'],
                # 'presence_penalty': self.config['presence_penalty'],
                # 'frequency_penalty': self.config['frequency_penalty'],
                # 'stream': stream
            }


            # vision model does support functions

            if self.config['enable_functions']:
                functions = self.plugin_manager.get_functions_specs()
                if len(functions) > 0:
                    common_args['tools'] = self.plugin_manager.get_functions_specs()
                    common_args['tool_choice'] = 'auto'
            
            return await self.client.chat.completions.create(**common_args)

        except openai.RateLimitError as e:
            raise e

        except openai.BadRequestError as e:
            raise Exception(f"⚠️ _{self.localized_text('openai_invalid', bot_language)}._ ⚠️\n{str(e)}") from e

        except Exception as e:
            raise Exception(f"⚠️ _{self.localized_text('error', bot_language)}._ ⚠️\n{str(e)}") from e


    async def interpret_image(self, user_id: int, username: str, chat_id, fileobj, prompt=None):
        """
        Interprets a given PNG image file using the Vision model.
        """
        self.user_update(user_id, username, chat_id)

        image = encode_image(fileobj)
        prompt = self.config['vision_prompt'] if prompt is None else prompt

        content = [{'type':'text', 'text':prompt}, {'type':'image_url', \
                    'image_url': {'url':image, 'detail':self.config['vision_detail'] } }]

        response = await self.__common_get_chat_response_vision(self.user_id, self.username, self.chat_id, content)

        

        # functions are not available for this model
        
        # if self.config['enable_functions']:
        #     response, plugins_used = await self.__handle_function_call(self.chat_id, response)
        #     if is_direct_result(response):
        #         return response, '0'

        answer = ''

        if len(response.choices) > 1 and self.config['n_choices'] > 1:
            for index, choice in enumerate(response.choices):
                content = choice.message.content.strip()
                if index == 0:
                    self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=content)
                answer += f'{index + 1}\u20e3\n'
                answer += content
                answer += '\n\n'
        else:
            answer = response.choices[0].message.content.strip()
            self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=answer)

        bot_language = self.config['bot_language']
        # Plugins are not enabled either
        # show_plugins_used = len(plugins_used) > 0 and self.config['show_plugins_used']
        # plugin_names = tuple(self.plugin_manager.get_plugin_source_name(plugin) for plugin in plugins_used)
        if self.config['show_usage']:
            answer += "\n\n---\n" \
                      f"💰 {str(response.usage.total_tokens)} {self.localized_text('stats_tokens', bot_language)}" \
                      f" ({str(response.usage.prompt_tokens)} {self.localized_text('prompt', bot_language)}," \
                      f" {str(response.usage.completion_tokens)} {self.localized_text('completion', bot_language)})"
            # if show_plugins_used:
            #     answer += f"\n🔌 {', '.join(plugin_names)}"
        # elif show_plugins_used:
        #     answer += f"\n\n---\n🔌 {', '.join(plugin_names)}"

        return answer, response.usage.total_tokens

    async def interpret_image_stream(self, user_id, username, chat_id, fileobj, prompt=None):
        """
        Interprets a given PNG image file using the Vision model.
        """
        self.user_update(user_id, username, chat_id)

        image = encode_image(fileobj)
        prompt = self.config['vision_prompt'] if prompt is None else prompt

        content = [{'type':'text', 'text':prompt}, {'type':'image_url', \
                    'image_url': {'url':image, 'detail':self.config['vision_detail'] } }]

        response = await self.__common_get_chat_response_vision(self.user_id, self.username, self.chat_id, content, stream=True)

        

        # if self.config['enable_functions']:
        #     response, plugins_used = await self.__handle_function_call(self.chat_id, response, stream=True)
        #     if is_direct_result(response):
        #         yield response, '0'
        #         return

        answer = ''
        async for chunk in response:
            if len(chunk.choices) == 0:
                continue
            delta = chunk.choices[0].delta
            if delta.content:
                answer += delta.content
                yield answer, 'not_finished'
        answer = answer.strip()
        self.add_to_history(self.user_id, self.username, self.chat_id, role="assistant", content=answer)
        tokens_used = str(self.__count_tokens(self.conversations[self.chat_id]))

        #show_plugins_used = len(plugins_used) > 0 and self.config['show_plugins_used']
        #plugin_names = tuple(self.plugin_manager.get_plugin_source_name(plugin) for plugin in plugins_used)
        if self.config['show_usage']:
            answer += f"\n\n---\n💰 {tokens_used} {self.localized_text('stats_tokens', self.config['bot_language'])}"
        #     if show_plugins_used:
        #         answer += f"\n🔌 {', '.join(plugin_names)}"
        # elif show_plugins_used:
        #     answer += f"\n\n---\n🔌 {', '.join(plugin_names)}"

        yield answer, tokens_used

    def reset_chat_history(self, user_id, username, chat_id, content=''):
        """
        Resets the conversation history.
        """
        self.user_update(user_id, username, chat_id)

        if content == '':
            content = self.config['assistant_prompt']
        # self.conversations[self.chat_id] = [{"role": "assistant" if self.config['model'] in O_MODELS else "system", "content": content}]
        update_value = {"role": "assistant" if self.config['model'] in O_MODELS else "system", "content": content}
        self.usage[user_id].do_conversations( self.chat_id, update_value, reset=True)
        # self.conversations_vision[str(self.chat_id)] = False

    def __max_age_reached(self, user_id, username, chat_id) -> bool:
        """
        Checks if the maximum conversation age has been reached.
        :param chat_id: The chat ID
        :return: A boolean indicating whether the maximum conversation age has been reached
        """
        self.user_update(user_id, username, chat_id)

        if self.chat_id not in self.last_updated:
            return False
        last_updated = self.last_updated[chat_id]
        now = datetime.datetime.now()
        max_age_minutes = self.config['max_conversation_age_minutes']
        return last_updated < now - datetime.timedelta(minutes=max_age_minutes)

    def __add_function_call_to_history(self, user_id, username, chat_id, function_name, content):
        """
        Adds a function call to the conversation history
        """
        self.user_update(user_id, username, chat_id)

        self.usage[self.user_id].do_conversations(chat_id, {"role": "function","name": function_name, "content": content})
    def add_to_history(self, user_id, username, chat_id, role, content, function_call=None):
        """
        Adds a message to the conversation history.
        :param chat_id: The chat ID
        :param role: The role of the message sender
        :param content: The message content
        """
        self.user_update(user_id, username, chat_id)
        if function_call:
            self.usage[self.user_id].do_conversations(self.chat_id, {"role": role, "content": content, "function_call": function_call})
        else:
            self.usage[self.user_id].do_conversations(self.chat_id, {"role": role, "content": content})

    async def __summarise(self, user_id: int, username: str, conversation) -> str:
        """
        Summarises the conversation history.
        :param conversation: The conversation history
        :return: The summary
        """
        # self.user_update(user_id,username)

        messages = [
            {"role": "system", "content": "Summarize this conversation in 700 characters or less"},
            {"role": "user", "content": str(conversation)}
        ]
        response = await self.client.chat.completions.create(
            model=self.config['model'],
            messages=messages,
            temperature=1 if self.config['model'] in O_MODELS else 0.4
        )
        return response.choices[0].message.content

    def __max_model_tokens(self):
        base = 4096
        if self.config['model'] in GPT_3_MODELS:
            return base
        if self.config['model'] in GPT_3_16K_MODELS:
            return base * 4
        if self.config['model'] in GPT_4_MODELS:
            return base * 2
        if self.config['model'] in GPT_4_32K_MODELS:
            return base * 8
        if self.config['model'] in VISION_MODELS:
            return base * 31
        if self.config['model'] in GPT_4_128K_MODELS:
            return base * 31
        if self.config['model'] in GPT_4O_MODELS:
            return base * 31
        #set default max tokens from Together.AI to 64,000 tk;increase if you mind!
        if self.config['model'] in GPT_TOGETHERAI_MODELS:
            return base * 16
        if self.config['model'] in GOOGLE_AI_STUDIO_MODELS:
            return base * 16
        elif self.config['model'] in O_MODELS:
            # https://platform.openai.com/docs/models#o1
            if self.config['model'] == "o1":
                return 100_000
            elif self.config['model'] == "o1-preview":
                return 32_768
            else:
                return 65_536
        raise NotImplementedError(
            f"Max tokens for model {self.config['model']} is not implemented yet."
        )

    # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
    def __count_tokens(self, messages) -> int:
        """
        Counts the number of tokens required to send the given messages.
        :param messages: the messages to send
        :return: the number of tokens required
        """
        model = self.config['model']
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("o200k_base")

        if model in GPT_ALL_MODELS:
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}.""")
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if key == 'content':
                    if isinstance(value, str):
                        num_tokens += len(encoding.encode(value))
                    else:
                        for message1 in value:
                            if message1['type'] == 'image_url':
                                image = decode_image(message1['image_url']['url'])
                                num_tokens += self.__count_tokens_vision(image)
                            else:
                                num_tokens += len(encoding.encode(message1['text']))
                else:
                    num_tokens += len(encoding.encode(value))
                    if key == "name":
                        num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def __count_tokens_vision(self, image_bytes: bytes) -> int:
        """
        Counts the number of tokens for interpreting an image.
        :param image_bytes: image to interpret
        :return: the number of tokens required
        """
        image_file = io.BytesIO(image_bytes)
        image = Image.open(image_file)
        model = self.config['vision_model']
        if model not in VISION_MODELS:
            raise NotImplementedError(f"""count_tokens_vision() is not implemented for model {model}.""")
        
        w, h = image.size
        if w > h: w, h = h, w
        # this computation follows https://platform.openai.com/docs/guides/vision and https://openai.com/pricing#gpt-4-turbo
        base_tokens = 85
        detail = self.config['vision_detail']
        if detail == 'low':
            return base_tokens
        elif detail == 'high' or detail == 'auto': # assuming worst cost for auto
            f = max(w / 768, h / 2048)
            if f > 1:
                w, h = int(w / f), int(h / f)
            tw, th = (w + 511) // 512, (h + 511) // 512
            tiles = tw * th
            num_tokens = base_tokens + tiles * 170
            return num_tokens
        else:
            raise NotImplementedError(f"""unknown parameter detail={detail} for model {model}.""")

    # No longer works as of July 21st 2023, as OpenAI has removed the billing API
    # def get_billing_current_month(self):
    #     """Gets billed usage for current month from OpenAI API.
    #
    #     :return: dollar amount of usage this month
    #     """
    #     headers = {
    #         "Authorization": f"Bearer {openai.api_key}"
    #     }
    #     # calculate first and last day of current month
    #     today = date.today()
    #     first_day = date(today.year, today.month, 1)
    #     _, last_day_of_month = monthrange(today.year, today.month)
    #     last_day = date(today.year, today.month, last_day_of_month)
    #     params = {
    #         "start_date": first_day,
    #         "end_date": last_day
    #     }
    #     response = requests.get("https://api.openai.com/dashboard/billing/usage", headers=headers, params=params)
    #     billing_data = json.loads(response.text)
    #     usage_month = billing_data["total_usage"] / 100  # convert cent amount to dollars
    #     return usage_month
