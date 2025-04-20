from __future__ import annotations

import asyncio
import logging
import os
import io
from io import BytesIO
import json
import base64

from uuid import uuid4
from telegram import BotCommandScopeAllGroupChats, Update, constants , InputMediaPhoto
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle
from telegram import InputTextMessageContent, BotCommand
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.error import RetryAfter, TimedOut, BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, InlineQueryHandler, CallbackQueryHandler, Application, ContextTypes, CallbackContext

import uuid

from pydub import AudioSegment
from PIL import Image

from utils import is_group_chat, get_thread_id, message_text, wrap_with_indicator, split_into_chunks, \
    edit_message_with_retry, get_stream_cutoff_values, is_allowed, get_remaining_budget, is_admin, is_within_budget, \
    get_reply_to_message_id, add_chat_request_to_usage_tracker, error_handler, is_direct_result, handle_direct_result, \
    cleanup_intermediate_files , is_forbidden
from openai_helper import OpenAIHelper, default_max_tokens, are_functions_available #, localized_text
from usage_tracker import UsageTracker

#Load the .env file
from dotenv import load_dotenv

load_dotenv()

# Load translations
parent_dir_path = os.path.join(os.path.dirname(__file__), os.pardir)
translations_file_path = os.path.join(parent_dir_path, 'translations.json')
with open(translations_file_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)


class ChatGPTTelegramBot:
    """
    Class representing a ChatGPT Telegram Bot.
    """

    def __init__(self, openai: OpenAIHelper):
        """
        Initializes the bot with the given configuration and GPT bot object.
        :param openai: OpenAIHelper object
        """
        first_admin = os.environ.get('ADMIN_USER_IDS','0').split(',')[0]
        # user_ids_list = [
        #     filename[:-5] for filename in os.listdir(users_directory)
        #     if os.path.isfile(os.path.join(users_directory, filename)) and filename.lower().endswith('.json')
        # ]
        self.user_id = int()
        self.username = ""
        self.chat_id = int()
        self.usage = {}
        self.conversations: dict[int: list] = {}
        self.usage[self.user_id] = UsageTracker(self.user_id , self.username, self.chat_id)
        # self.usage[self.user_id].save_state()

        self.logs_dir = "user_logs"

        self.config = self.usage[self.user_id].return_configs('telegram')

        self.openai = openai
        dummy, bot_language = self.usage[self.user_id].retrieve_config_value('telegram','bot_language')
        self.commands = [
            BotCommand(command='help', description=self.localized_text('help_description', bot_language)),
            BotCommand(command='reset', description=self.localized_text('reset_description', bot_language)),
            BotCommand(command='stats', description=self.localized_text('stats_description', bot_language)),
            BotCommand(command='resend', description=self.localized_text('resend_description', bot_language)),
            BotCommand(command='setconfig', description=self.localized_text('setconfig_description', bot_language))

        ]
        # If imaging is enabled, add the "image" command to the list
        if self.config.get('enable_image_generation', False):
            self.commands.append(BotCommand(command='image', description=self.localized_text('image_description', bot_language)))

        if self.config.get('enable_tts_generation', False):
            self.commands.append(BotCommand(command='tts', description=self.localized_text('tts_description', bot_language)))

        self.group_commands = [BotCommand(
            command='chat', description=self.localized_text('chat_description', bot_language)
        ),
        BotCommand(
            command='moderate', description=self.localized_text('moderate_description', bot_language)
        )] + self.commands
        self.disallowed_message = "Sorry...\n You are not allowed to perform this action."
        self.budget_limit_message = self.localized_text('budget_limit', bot_language)
        self.last_message = {}
        self.inline_queries_cache = {}

        self.logger = self.create_user_logger(self.user_id)
    def extract_chat_id(self,update):
        if update.inline_query:
            chat_id = update.inline_query.id
        elif update.effective_chat:
            chat_id = update.effective_chat.id
        else :
            chat_id = update.callback_query.from_user.id
        return chat_id


    async def user_update(self, update:Update, context:ContextTypes.DEFAULT_TYPE, is_inline=False):
        """
        set the default user id
        """

        user = update.effective_user
        chat_id = self.extract_chat_id(update)
        self.user_id = user.id
        self.username = user.name
        self.chat_id = chat_id
        self.usage[self.user_id] = UsageTracker(self.user_id , self.username, self.chat_id)
        self.logger = self.create_user_logger(self.user_id)
        self.config = self.usage[self.user_id].return_configs('telegram')
        self.usage[self.user_id].save_state()
        self.conversations = self.usage[self.user_id].do_conversations(chat_id=chat_id)
        dummy, self.bot_language = self.usage[self.user_id].retrieve_config_value('telegram','bot_language')

    def create_user_logger(self, user_id):
        # Create a logger for the user if it doesn't exist
        logger = logging.getLogger(f"user_{user_id}")
        
        # Check if the logger already has handlers
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Create a file handler for the user's log file
            log_file_path = os.path.join(self.logs_dir, str(user_id), f"user_{user_id}.log")
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
                
    async def help(self, update: Update, _: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Shows the help menu.
        """
        commands = self.group_commands if is_group_chat(update) else self.commands
        commands_description = [f'/{command.command} - {command.description}' for command in commands]
        bot_language = self.config['bot_language']
        help_text = (
                self.localized_text('help_text', bot_language)[0] +
                '\n\n' +
                '\n'.join(commands_description) +
                '\n\n' +
                self.localized_text('help_text', bot_language)[1] +
                '\n\n' +
                self.localized_text('help_text', bot_language)[2]
        )
        await update.message.reply_text(help_text, disable_web_page_preview=True)

    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Returns token usage statistics for current day and month.
        """
        await self.user_update(update,context)

        if not await is_allowed(self.config, update, context):
            self.logger.warning(f'User {update.message.from_user.name} (id: {update.message.from_user.id}) '
                            'is not allowed to request their usage statistics')
            await self.send_disallowed_markup(update, context)
            return

        self.logger.info(f'User {update.message.from_user.name} (id: {update.message.from_user.id}) '
                     'requested their usage statistics')

        user_id = update.message.from_user.id
        if user_id not in self.usage:
            self.usage[self.user_id] = UsageTracker(user_id, update.message.from_user.name)

        tokens_today, tokens_month = self.usage[self.user_id].get_current_token_usage()
        images_today, images_month = self.usage[self.user_id].get_current_image_count()
        (transcribe_minutes_today, transcribe_seconds_today, transcribe_minutes_month,
         transcribe_seconds_month) = self.usage[self.user_id].get_current_transcription_duration()
        vision_today, vision_month = self.usage[self.user_id].get_current_vision_tokens()
        characters_today, characters_month = self.usage[self.user_id].get_current_tts_usage()
        current_cost = self.usage[self.user_id].get_current_cost()

        chat_id = update.effective_chat.id
        chat_messages, chat_token_length = self.openai.get_conversation_stats(self.user_id, self.username, chat_id)
        remaining_budget = get_remaining_budget(self.config, self.usage, update)
        bot_language = self.config['bot_language']
        
        text_current_conversation = (
            f"*{self.localized_text('stats_conversation', bot_language)[0]}*:\n"
            f"{chat_messages} {self.localized_text('stats_conversation', bot_language)[1]}\n"
            f"{chat_token_length} {self.localized_text('stats_conversation', bot_language)[2]}\n"
            "----------------------------\n"
        )
        
        # Check if image generation is enabled and, if so, generate the image statistics for today
        text_today_images = ""
        if self.config.get('enable_image_generation', False):
            text_today_images = f"{images_today} {self.localized_text('stats_images', bot_language)}\n"

        text_today_vision = ""
        if self.config.get('enable_vision', False):
            text_today_vision = f"{vision_today} {self.localized_text('stats_vision', bot_language)}\n"

        text_today_tts = ""
        if self.config.get('enable_tts_generation', False):
            text_today_tts = f"{characters_today} {self.localized_text('stats_tts', bot_language)}\n"
        
        text_today = (
            f"*{self.localized_text('usage_today', bot_language)}:*\n"
            f"{tokens_today} {self.localized_text('stats_tokens', bot_language)}\n"
            f"{text_today_images}"  # Include the image statistics for today if applicable
            f"{text_today_vision}"
            f"{text_today_tts}"
            f"{transcribe_minutes_today} {self.localized_text('stats_transcribe', bot_language)[0]} "
            f"{transcribe_seconds_today} {self.localized_text('stats_transcribe', bot_language)[1]}\n"
            f"{self.localized_text('stats_total', bot_language)}{current_cost['cost_today']:.2f}\n"
            "----------------------------\n"
        )
        
        text_month_images = ""
        if self.config.get('enable_image_generation', False):
            text_month_images = f"{images_month} {self.localized_text('stats_images', bot_language)}\n"

        text_month_vision = ""
        if self.config.get('enable_vision', False):
            text_month_vision = f"{vision_month} {self.localized_text('stats_vision', bot_language)}\n"

        text_month_tts = ""
        if self.config.get('enable_tts_generation', False):
            text_month_tts = f"{characters_month} {self.localized_text('stats_tts', bot_language)}\n"
        
        # Check if image generation is enabled and, if so, generate the image statistics for the month
        text_month = (
            f"*{self.localized_text('usage_month', bot_language)}:*\n"
            f"{tokens_month} {self.localized_text('stats_tokens', bot_language)}\n"
            f"{text_month_images}"  # Include the image statistics for the month if applicable
            f"{text_month_vision}"
            f"{text_month_tts}"
            f"{transcribe_minutes_month} {self.localized_text('stats_transcribe', bot_language)[0]} "
            f"{transcribe_seconds_month} {self.localized_text('stats_transcribe', bot_language)[1]}\n"
            f"{self.localized_text('stats_total', bot_language)}{current_cost['cost_month']:.2f}"
        )

        # text_budget filled with conditional content
        text_budget = "\n\n"
        budget_period = self.config['budget_period']
        if remaining_budget < float('inf'):
            text_budget += (
                f"{self.localized_text('stats_budget', bot_language)}"
                f"{self.localized_text(budget_period, bot_language)}: "
                f"${remaining_budget:.2f}.\n"
            )
        # No longer works as of July 21st 2023, as OpenAI has removed the billing API
        # add OpenAI account information for admin request
        # if is_admin(self.config, user_id):
        #     text_budget += (
        #         f"{self.localized_text('stats_openai', bot_language)}"
        #         f"{self.openai.get_billing_current_month():.2f}"
        #     )

        usage_text = text_current_conversation + text_today + text_month + text_budget
        await update.message.reply_text(usage_text, parse_mode=constants.ParseMode.MARKDOWN)

    async def resend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Resend the last request
        """
        if not await is_allowed(self.config, update, context):
            self.logger.warning(f'User {update.message.from_user.name}  (id: {update.message.from_user.id})'
                            ' is not allowed to resend the message')
            await self.send_disallowed_markup(update, context)
            return

        chat_id = update.effective_chat.id
        if chat_id not in self.last_message:
            self.logger.warning(f'User {update.message.from_user.name} (id: {update.message.from_user.id})'
                            ' does not have anything to resend')
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.localized_text('resend_failed', self.config['bot_language'])
            )
            return

        # Update message text, clear self.last_message and send the request to prompt
        self.logger.info(f'Resending the last prompt from user: {update.message.from_user.name} '
                     f'(id: {update.message.from_user.id})')
        with update.message._unfrozen() as message:
            message.text = self.last_message.pop(chat_id)

        await self.prompt(update=update, context=context)

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Resets the conversation.
        """
        await self.user_update(update,context)

        if not await is_allowed(self.config, update, context):
            self.logger.warning(f'User {update.message.from_user.name} (id: {update.message.from_user.id}) '
                            'is not allowed to reset the conversation')
            await self.send_disallowed_markup(update, context)
            return

        self.logger.info(f'Resetting the conversation for user {update.message.from_user.name} '
                     f'(id: {update.message.from_user.id})...')

        chat_id = update.effective_chat.id
        reset_content = message_text(update.message)
        self.openai.reset_chat_history(self.user_id, self.username, chat_id=chat_id, content=reset_content)
        await update.effective_message.reply_text(
            message_thread_id=get_thread_id(update),
            text=self.localized_text('reset_done', self.config['bot_language'])
        )

    async def image(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Generates an image for the given prompt using either OpenAI or FLUX APIs based on the openai_api_url configuration
        """
        await self.user_update(update,context)

        if not self.config['enable_image_generation'] \
        or not await self.check_allowed_and_within_budget(update, context):
            return

        image_query = message_text(update.message)
        if image_query == '':
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.localized_text('image_no_prompt', self.config['bot_language'])
            )
            return

        self.logger.info(f'New image generation request received from user {update.message.from_user.name} '
                    f'(id: {update.message.from_user.id})')

        async def _generate():
            try:
                if os.getenv("FLUX_GEN",'false') == 'true':
                    # Use FLUX API
                    b64_json, image_size = await self.openai.generate_image_flux(self.user_id, self.username, self.chat_id, prompt=image_query)
                    # Decode the base64 JSON to get the image data
                    image_data = base64.b64decode(b64_json)
                    image_bytes = BytesIO(image_data)
                    image_bytes.name = 'generated_image.png'  # Set a name for the file

                    if self.config['image_receive_mode'] == 'photo':
                        await update.effective_message.reply_photo(
                            reply_to_message_id=get_reply_to_message_id(self.config, update),
                            photo=image_bytes
                        )
                    elif self.config['image_receive_mode'] == 'document':
                        await update.effective_message.reply_document(
                            reply_to_message_id=get_reply_to_message_id(self.config, update),
                            document=image_bytes
                        )
                    else:
                        raise Exception(f"env variable IMAGE_RECEIVE_MODE has invalid value {self.config['image_receive_mode']}")
                else:
                    # Use OpenAI API
                    image_url, image_size = await self.openai.generate_image(self.user_id, self.username, self.chat_id, prompt=image_query)
                    if self.config['image_receive_mode'] == 'photo':
                        await update.effective_message.reply_photo(
                            reply_to_message_id=get_reply_to_message_id(self.config, update),
                            photo=image_url
                        )
                    elif self.config['image_receive_mode'] == 'document':
                        await update.effective_message.reply_document(
                            reply_to_message_id=get_reply_to_message_id(self.config, update),
                            document=image_url
                        )
                    else:
                        raise Exception(f"env variable IMAGE_RECEIVE_MODE has invalid value {self.config['image_receive_mode']}")

                # Add image request to users usage tracker
                # user_id = update.message.from_user.id
                self.usage[self.user_id].add_image_request(image_size, self.config['image_prices'])

                # Add guest chat request to guest usage tracker
                if str(self.user_id) not in self.config['user_ids_list'].split(',') and 'guests' in self.usage:
                    self.usage["guests"].add_image_request(image_size, self.config['image_prices'])

            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=f"{self.localized_text('image_fail', self.config['bot_language'])}: {str(e)}",
                    parse_mode=constants.ParseMode.MARKDOWN
                )

        await wrap_with_indicator(update, context, _generate, constants.ChatAction.UPLOAD_PHOTO)

    async def tts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Generates an speech for the given input using TTS APIs
        """
        await self.user_update(update,context)

        if not self.config['enable_tts_generation'] \
                or not await self.check_allowed_and_within_budget(update, context):
            return

        tts_query = message_text(update.message)
        if tts_query == '':
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.localized_text('tts_no_prompt', self.config['bot_language'])
            )
            return

        self.logger.info(f'New speech generation request received from user {update.message.from_user.name} '
                     f'(id: {update.message.from_user.id})')

        async def _generate():
            try:
                speech_file, text_length = await self.openai.generate_speech(self.user_id, self.username, text=tts_query)

                await update.effective_message.reply_voice(
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    voice=speech_file
                )
                speech_file.close()
                # add image request to users usage tracker
                # user_id = update.message.from_user.id
                self.usage[self.user_id].add_tts_request(text_length, self.config['tts_model'], self.config['tts_prices'])
                # add guest chat request to guest usage tracker
                if str(self.user_id) not in self.config['user_ids_list'].split(',') and 'guests' in self.usage:
                    self.usage["guests"].add_tts_request(text_length, self.config['tts_model'], self.config['tts_prices'])

            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=f"{self.localized_text('tts_fail', self.config['bot_language'])}: {str(e)}",
                    parse_mode=constants.ParseMode.MARKDOWN
                )

        await wrap_with_indicator(update, context, _generate, constants.ChatAction.UPLOAD_VOICE)

    async def transcribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Transcribe audio messages.
        """
        await self.user_update(update,context)

        if not self.config['enable_transcription'] or not await self.check_allowed_and_within_budget(update, context):
            return

        if is_group_chat(update) and self.config['ignore_group_transcriptions']:
            self.logger.info('Transcription coming from group chat, ignoring...')
            return

        chat_id = update.effective_chat.id
        filename = update.message.effective_attachment.file_unique_id

        async def _execute():
            filename_mp3 = f'{filename}.mp3'
            bot_language = self.config['bot_language']
            try:
                media_file = await context.bot.get_file(update.message.effective_attachment.file_id)
                await media_file.download_to_drive(filename)
            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=(
                        f"{self.localized_text('media_download_fail', bot_language)[0]}: "
                        f"{str(e)}. {self.localized_text('media_download_fail', bot_language)[1]}"
                    ),
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                return

            try:
                audio_track = AudioSegment.from_file(filename)
                audio_track.export(filename_mp3, format="mp3")
                self.logger.info(f'New transcribe request received from user {update.message.from_user.name} '
                             f'(id: {update.message.from_user.id})')

            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=self.localized_text('media_type_fail', bot_language)
                )
                if os.path.exists(filename):
                    os.remove(filename)
                return

            # user_id = update.message.from_user.id
            # username =update.message.from_user.name
            # if user_id not in self.usage:
            #     self.usage[self.user_id] = UsageTracker(self.user_id, self.username)

            try:
                transcript = await self.openai.transcribe(self.user_id, self.username, filename_mp3)

                transcription_price = self.config['transcription_price']
                self.usage[self.user_id].add_transcription_seconds(audio_track.duration_seconds, transcription_price)

                user_ids_list = self.config['user_ids_list'].split(',')
                if str(self.user_id) not in user_ids_list and 'guests' in self.usage:
                    self.usage["guests"].add_transcription_seconds(audio_track.duration_seconds, transcription_price)

                # check if transcript starts with any of the prefixes
                response_to_transcription = any(transcript.lower().startswith(prefix.lower()) if prefix else False
                                                for prefix in self.config['voice_reply_prompts'])

                if self.config['voice_reply_transcript'] and not response_to_transcription:

                    # Split into chunks of 4096 characters (Telegram's message limit)
                    transcript_output = f"_{self.localized_text('transcript', bot_language)}:_\n\"{transcript}\""
                    chunks = split_into_chunks(transcript_output)

                    for index, transcript_chunk in enumerate(chunks):
                        await update.effective_message.reply_text(
                            message_thread_id=get_thread_id(update),
                            reply_to_message_id=get_reply_to_message_id(self.config, update) if index == 0 else None,
                            text=transcript_chunk,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                else:
                    # Get the response of the transcript
                    response, input_tokens, output_tokens, cached_tokens  = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=chat_id, role="user", query=transcript)
                    if is_direct_result(response):
                        direct_caption_prompt = "Previous Function ran successfully, Give a follow-up caption based on the previous function you called, consice and clear."
                        direct_caption, direct_input_tokens, direct_output_tokens, direct_cached_tokens = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=chat_id, role="user", query=direct_caption_prompt)
                        # self.usage[self.user_id].add_chat_tokens(output_tokens=direct_tokens)
                        # self.logger.info(f"direct caption is : {direct_caption} and direct token: {direct_tokens}")
                        add_chat_request_to_usage_tracker(self.usage, self.config, update.message.from_user.id, direct_input_tokens, direct_output_tokens, direct_cached_tokens)
                        return await handle_direct_result(self.config, update, response , direct_caption)
                    
                    # self.usage[self.user_id].add_chat_tokens(input_tokens=input_tokens, output_tokens=output_tokens, cached_tokens=cached_tokens)

                    if str(self.user_id) not in user_ids_list and 'guests' in self.usage:
                        self.usage["guests"].add_chat_tokens(output_tokens=output_tokens)

                    # Split into chunks of 4096 characters (Telegram's message limit)
                    transcript_output = (
                        f"_{self.localized_text('transcript', bot_language)}:_\n\"{transcript}\"\n\n"
                        f"_{self.localized_text('answer', bot_language)}:_\n{response}"
                    )
                    chunks = split_into_chunks(transcript_output)

                    for index, transcript_chunk in enumerate(chunks):
                        await update.effective_message.reply_text(
                            message_thread_id=get_thread_id(update),
                            reply_to_message_id=get_reply_to_message_id(self.config, update) if index == 0 else None,
                            text=transcript_chunk,
                            parse_mode=constants.ParseMode.HTML
                        )

            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=f"{self.localized_text('transcribe_fail', bot_language)}: {str(e)}",
                    parse_mode=constants.ParseMode.MARKDOWN
                )
            finally:
                if os.path.exists(filename_mp3):
                    os.remove(filename_mp3)
                if os.path.exists(filename):
                    os.remove(filename)

        await wrap_with_indicator(update, context, _execute, constants.ChatAction.TYPING)

    async def vision(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Interpret image using vision model.
        """
        await self.user_update(update,context)

        if not self.config['enable_vision'] or not await self.check_allowed_and_within_budget(update, context):
            return

        chat_id = update.effective_chat.id
        prompt = update.message.caption

        if is_group_chat(update):
            if self.config['ignore_group_vision']:
                self.logger.info('Vision coming from group chat, ignoring...')
                return
            else:
                gp_trigger_keyword = self.config['group_trigger_keyword']
                if (prompt is None and gp_trigger_keyword != '') or \
                   (prompt is not None and not prompt.lower().startswith(gp_trigger_keyword.lower())):
                    self.logger.info('Vision coming from group chat with wrong keyword, ignoring...')
                    return
        
        image = update.message.effective_attachment[-1]
        

        async def _execute():
            bot_language = self.config['bot_language']
            try:
                media_file = await context.bot.get_file(image.file_id)
                temp_file = io.BytesIO(await media_file.download_as_bytearray())
            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=(
                        f"{self.localized_text('media_download_fail', bot_language)[0]}: "
                        f"{str(e)}. {self.localized_text('media_download_fail', bot_language)[1]}"
                    ),
                    parse_mode=constants.ParseMode.MARKDOWN
                )
                return
            
            # convert jpg from telegram to png as understood by openai

            temp_file_png = io.BytesIO()

            try:
                original_image = Image.open(temp_file)
                
                original_image.save(temp_file_png, format='PNG')
                self.logger.info(f'New vision request received from user {update.message.from_user.name} '
                             f'(id: {update.message.from_user.id})')

            except Exception as e:
                self.logger.exception(e)
                await update.effective_message.reply_text(
                    message_thread_id=get_thread_id(update),
                    reply_to_message_id=get_reply_to_message_id(self.config, update),
                    text=self.localized_text('media_type_fail', bot_language)
                )
            
            

            # user_id = update.message.from_user.id
            # if user_id not in self.usage:
            #     self.usage[user_id] = UsageTracker(user_id, update.message.from_user.name)

            if self.config['stream']:

                stream_response = self.openai.interpret_image_stream(self.user_id, self.username, chat_id=chat_id, fileobj=temp_file_png, prompt=prompt)
                i = 0
                prev = ''
                sent_message = None
                backoff = 0
                stream_chunk = 0

                async for content, tokens in stream_response:
                    if is_direct_result(content):
                        return await handle_direct_result(self.config, update, content)

                    if len(content.strip()) == 0:
                        continue

                    stream_chunks = split_into_chunks(content)
                    if len(stream_chunks) > 1:
                        content = stream_chunks[-1]
                        if stream_chunk != len(stream_chunks) - 1:
                            stream_chunk += 1
                            try:
                                await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                              stream_chunks[-2])
                            except:
                                pass
                            try:
                                sent_message = await update.effective_message.reply_text(
                                    message_thread_id=get_thread_id(update),
                                    text=content if len(content) > 0 else "..."
                                )
                            except:
                                pass
                            continue

                    cutoff = get_stream_cutoff_values(update, content)
                    cutoff += backoff

                    if i == 0:
                        try:
                            if sent_message is not None:
                                await context.bot.delete_message(chat_id=sent_message.chat_id,
                                                                 message_id=sent_message.message_id)
                            sent_message = await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(self.config, update),
                                text=content,
                            )
                        except:
                            continue

                    elif abs(len(content) - len(prev)) > cutoff or tokens != 'not_finished':
                        prev = content

                        try:
                            use_markdown = tokens != 'not_finished'
                            await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                          text=content, markdown=use_markdown)

                        except RetryAfter as e:
                            backoff += 5
                            await asyncio.sleep(e.retry_after)
                            continue

                        except TimedOut:
                            backoff += 5
                            await asyncio.sleep(0.5)
                            continue

                        except Exception:
                            backoff += 5
                            continue

                        await asyncio.sleep(0.01)

                    i += 1
                    if tokens != 'not_finished':
                        output_tokens = int(tokens)

                
            else:

                try:
                    interpretation, output_tokens = await self.openai.interpret_image(self.user_id, self.username, chat_id, temp_file_png, prompt=prompt)


                    try:
                        await update.effective_message.reply_text(
                            message_thread_id=get_thread_id(update),
                            reply_to_message_id=get_reply_to_message_id(self.config, update),
                            text=interpretation,
                            parse_mode=constants.ParseMode.MARKDOWN
                        )
                    except BadRequest:
                        try:
                            await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(self.config, update),
                                text=interpretation
                            )
                        except Exception as e:
                            self.logger.exception(e)
                            await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(self.config, update),
                                text=f"{self.localized_text('vision_fail', bot_language)}: {str(e)}",
                                parse_mode=constants.ParseMode.MARKDOWN
                            )
                except Exception as e:
                    self.logger.exception(e)
                    await update.effective_message.reply_text(
                        message_thread_id=get_thread_id(update),
                        reply_to_message_id=get_reply_to_message_id(self.config, update),
                        text=f"{self.localized_text('vision_fail', bot_language)}: {str(e)}",
                        parse_mode=constants.ParseMode.MARKDOWN
                    )
            vision_token_price = self.config['vision_token_price']
            self.usage[self.user_id].add_vision_tokens(output_tokens, vision_token_price)

            user_ids_list = self.config['user_ids_list'].split(',')
            if str(self.user_id) not in user_ids_list and 'guests' in self.usage:
                self.usage["guests"].add_vision_tokens(output_tokens, vision_token_price)

        await wrap_with_indicator(update, context, _execute, constants.ChatAction.TYPING)

    async def process_openai_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt, chat_id, role:str, super_access=False):
        input_tokens = output_tokens = cached_tokens = 0
        await self.user_update(update,context)

        try:
            # Handle streaming response
            if self.config['stream']:
                await update.effective_message.reply_chat_action(
                    action=constants.ChatAction.TYPING,
                    message_thread_id=get_thread_id(update)
                )

                stream_response = self.openai.get_chat_response_stream(user_id=self.user_id, username=self.username, chat_id=chat_id, role=role, query=prompt, super_access=super_access)
                i = 0
                prev = ''
                sent_message = None
                backoff = 0
                stream_chunk = 0

                async for content, tokens in stream_response:
                    if is_direct_result(content):
                        direct_caption_prompt = "Previous Function ran successfully, Give a follow-up caption based on the previous function you called, consice and clear."
                        direct_caption, direct_input_tokens, direct_output_tokens, direct_cached_tokens = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=chat_id, role="user", query=direct_caption_prompt)
                        add_chat_request_to_usage_tracker(self.usage, self.config, update.message.from_user.id, direct_input_tokens, direct_output_tokens, direct_cached_tokens)
                        return await handle_direct_result(self.config, update, content , direct_caption)

                    if len(content.strip()) == 0:
                        continue

                    stream_chunks = split_into_chunks(content)
                    if len(stream_chunks) > 1:
                        content = stream_chunks[-1]
                        if stream_chunk != len(stream_chunks) - 1:
                            stream_chunk += 1
                            try:
                                await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                            stream_chunks[-2])
                            except:
                                pass
                            try:
                                sent_message = await update.effective_message.reply_text(
                                    message_thread_id=get_thread_id(update),
                                    text=content if len(content) > 0 else "..."
                                )
                            except:
                                pass
                            continue

                    cutoff = get_stream_cutoff_values(update, content)
                    cutoff += backoff

                    if i == 0:
                        try:
                            if sent_message is not None:
                                await context.bot.delete_message(chat_id=sent_message.chat_id,
                                                                message_id=sent_message.message_id)
                            sent_message = await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(self.config, update),
                                text=content,
                            )
                        except:
                            continue

                    elif abs(len(content) - len(prev)) > cutoff or tokens != 'not_finished':
                        prev = content

                        try:
                            use_markdown = tokens != 'not_finished'
                            await edit_message_with_retry(context, chat_id, str(sent_message.message_id),
                                                        text=content, markdown=use_markdown)

                        except RetryAfter as e:
                            backoff += 5
                            await asyncio.sleep(e.retry_after)
                            continue

                        except TimedOut:
                            backoff += 5
                            await asyncio.sleep(0.5)
                            continue

                        except Exception:
                            backoff += 5
                            continue

                        await asyncio.sleep(0.01)

                    i += 1
                    if tokens != 'not_finished':
                        output_tokens = int(tokens)

            # Handle non-streaming response
            else:
                async def _reply():
                    nonlocal input_tokens, output_tokens, cached_tokens
                    response, input_tokens, output_tokens, cached_tokens = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=chat_id, role=role, query=prompt, super_access=super_access)
                    if is_direct_result(response):
                        direct_caption_prompt = "Previous Function ran successfully, Give a follow-up caption based on the previous function you called, consice and clear."
                        direct_caption, direct_input_tokens, direct_output_tokens, direct_cached_tokens = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=chat_id, role="user", query=direct_caption_prompt)
                        # self.usage[self.user_id].add_chat_tokens(output_tokens=direct_tokens)
                        self.logger.info(f"direct output tokens are : {direct_output_tokens}, output tokens are : {output_tokens}")
                        output_tokens = int(output_tokens)
                        output_tokens += int(direct_output_tokens)
                        add_chat_request_to_usage_tracker(self.usage, self.config, update.message.from_user.id, direct_input_tokens, direct_output_tokens, direct_cached_tokens)
                        return await handle_direct_result(self.config, update, response , direct_caption)

                    # Split into chunks of 4096 characters (Telegram's message limit)
                    chunks = split_into_chunks(response)

                    for index, chunk in enumerate(chunks):
                        try:
                            await update.effective_message.reply_text(
                                message_thread_id=get_thread_id(update),
                                reply_to_message_id=get_reply_to_message_id(self.config,
                                                                            update) if index == 0 else None,
                                text=chunk,
                                parse_mode=constants.ParseMode.MARKDOWN
                            )
                        except Exception:
                            try:
                                await update.effective_message.reply_text(
                                    message_thread_id=get_thread_id(update),
                                    reply_to_message_id=get_reply_to_message_id(self.config,
                                                                                update) if index == 0 else None,
                                    text=chunk
                                )
                            except Exception as exception:
                                raise exception

                await wrap_with_indicator(update, context, _reply, constants.ChatAction.TYPING)

            add_chat_request_to_usage_tracker(self.usage, self.config, update.message.from_user.id, input_tokens, output_tokens, cached_tokens)

        except Exception as e:
            self.logger.exception(e)
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                reply_to_message_id=get_reply_to_message_id(self.config, update),
                text=f"{self.localized_text('chat_fail', self.config['bot_language'])} {str(e)}",
                parse_mode=constants.ParseMode.MARKDOWN
            )

   
    async def handle_channel_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, chat_id: int):
        """
        Handles channel-related commands: forwarding or sending messages based on keywords.
        """
        user = update.effective_user
        await self.user_update(update,context)
        forward_keyword = self.config["forward_keyword"]
        channel_id = self.config["channel_id"]

        if prompt.lower().startswith(forward_keyword.lower()):
            if (channel_id or forward_keyword) in [""]  :
                missing_response = "The message hasn't been sent to their channel,"  
                "channel_id or forward_keyword in the config is missing."
                self.openai.add_to_history(self.user_id, self.username, chat_id, "system", missing_response)
                await self.process_openai_response(update, context, "what happended?", chat_id,role="suer")
                return
            # Extract the part of the prompt after the forward keyword and strip spaces.
            user_input_after_keyword = prompt[len(forward_keyword):].strip()
            # If no extra content is provided, forward the replied-to message.
            if not user_input_after_keyword:
                await context.bot.forward_message(
                    chat_id=channel_id,
                    from_chat_id=update.message.chat.id,
                    message_id=update.effective_message.reply_to_message.message_id
                )
            else:
                await context.bot.forward_message(
                    chat_id=channel_id,
                    from_chat_id=update.message.chat.id,
                    message_id=update.message.message_id
                )
            self.logger.info(
                f"Forwarded message to the channel {channel_id}: %s", 
                update.effective_message.reply_to_message.text
            )
            forward_response = "The message has been forwarded to the channel successfully."
            self.openai.add_to_history(self.user_id, self.username, chat_id, "system", forward_response)
            await self.process_openai_response(update, context, "what happened?", chat_id,role="user")

        return


    async def handle_moderation_request(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, chat_id: int, message_thread_id: int, group_id: int
    ):
        """Handles moderation requests in group chats."""
        self.logger.info(
            f"User requested for `Indirect` Group/Channel moderation with message_thread_id:{message_thread_id} and group_id={group_id}"
        )
        
        # Call the common reply-checking logic.
        # Note: process_reply_logic returns the updated prompt and a flag (handled) if processing was already done.
        prompt, handled = await self.process_reply_logic(
            update, context, prompt, chat_id, original_prompt=prompt, is_group=True, super_access=True
        )
        if handled:
            return

        # If there was no reply, remove the mod trigger keyword and add moderation info.
        if update.effective_message.reply_to_message is None:
            prompt = prompt[len(self.config["mod_trigger_keyword"]) :].strip()
            self.logger.info(f"With the prompt: {prompt}")
            system_prompt = (
                f"User asked for channel/group moderation. Using these information : "
                f"`message_thread_id={message_thread_id} group_id={group_id}`, Answer their request.NOTHING MORE!"
            )
        else:
            # A reply exists but process_reply_logic did not handle it.
            reply = update.effective_message.reply_to_message
            if reply.text:
                self.logger.info(f"by replying to the text: {reply.text}")
                system_prompt = (
                    f'"User replied to the text :`{reply.text}" and asked for channel/group moderation. '
                    f"Using these information : 'replied_message_id={reply.message_id} message_thread_id={message_thread_id} and group_id={group_id}', "
                    f"Answer their request.NOTHING MORE!"
                )
            else:
                self.logger.info(f"by replying to a non-text message: {reply}")
                system_prompt = (
                    f'"User replied to the message :`Non-text message" and asked for channel/group moderation. '
                    f"Using these information : 'replied_message_id={reply.message_id} message_thread_id={message_thread_id} and group_id={group_id}', "
                    f"Answer their request.NOTHING MORE!"
                )

        self.openai.add_to_history(self.user_id, self.username, chat_id, "system", system_prompt)
        await self.process_openai_response(update, context, prompt, chat_id, role="user", super_access=True)
        return

    async def handle_group_chat_prompt(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, chat_id: int, message_thread_id: int
    ):
        """Handles prompts in group chats, including trigger keyword checks and reply handling."""
        user = update.effective_user
        gp_trigger_keyword = self.config["group_trigger_keyword"]
        mod_trigger_keyword = self.config["mod_trigger_keyword"]
        forward_keyword = self.config["forward_keyword"]

        reply = update.effective_message.reply_to_message
        
        if prompt.lower().startswith(forward_keyword.lower()):
            await self.handle_channel_commands(update, context, prompt, chat_id)
        elif prompt.lower().startswith(mod_trigger_keyword.lower()):
            await self.handle_moderation_request(update, context, prompt, chat_id, message_thread_id, update.effective_message.chat.id)
        elif prompt.lower().startswith(gp_trigger_keyword.lower()) or update.effective_message.text.lower().startswith("/chat"):
            if prompt.lower().startswith(gp_trigger_keyword.lower()):
                prompt = prompt[len(gp_trigger_keyword) :].strip()
                if prompt.lower().startswith(forward_keyword.lower()):
                    await self.handle_channel_commands(update, context, prompt, chat_id)
                    return
            elif prompt.lower().startswith("/chat"):
                prompt = prompt[len("/chat") :].strip()

            # Process reply logic (if the message is a reply to another message)
            prompt, handled = await self.process_reply_logic(update, context, prompt, chat_id, original_prompt=prompt, is_group=True)
            if handled:
                return
            self.logger.info("No forwarding/reply information from another source or channel detected.")
            await self.process_openai_response(update, context, prompt, chat_id, role="user")

        
        elif reply.from_user and reply.from_user.id == context.bot.id:
            reply_text = reply.text if reply.text else (reply.caption if hasattr(reply, "caption") else "")
            self.logger.info(f"Group message:{reply_text} is a reply to the Bot itself")
            # Use original_prompt if provided (for private chat) or the current prompt.
            prompt = f'"{reply_text} {prompt} - and here is additional info:{reply}'

            # Process reply logic (if the message is a reply to another message)
            prompt, handled = await self.process_reply_logic(update, context, prompt, chat_id, original_prompt=prompt, is_group=True)
            if handled:
                return
            self.logger.info("No forwarding/reply information from another source or channel detected.")
            await self.process_openai_response(update, context, prompt, chat_id, role="user")

    async def process_reply_logic(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        prompt: str,
        chat_id: int,
        original_prompt: Optional[str] = None,
        is_group: bool = False,
        super_access=False
    ) -> Tuple[Optional[str], bool]:
        """
        Handles reply logic for both group and private chats.

        Returns a tuple:
        - The (possibly updated) prompt (or None if response was already sent)
        - A boolean flag indicating whether processing has been handled (and so the caller should return immediately)
        """
        reply = update.effective_message.reply_to_message
        if not reply:
            return prompt, False

        # In group chats, check both text and caption; in private chats, just text.
        reply_text = reply.text if reply.text else (reply.caption if hasattr(reply, "caption") else "")
        if not reply_text:
            return prompt, False

        # If the reply is to the bot itself:
        if reply.from_user and reply.from_user.id == context.bot.id:
            self.logger.info(f"{'Group' if is_group else 'Private'} message:{reply_text} is a reply to the Bot itself")
            # Use original_prompt if provided (for private chat) or the current prompt.
            return f'"{reply_text} {original_prompt or prompt} - and here is additional info:{reply}', False

        # For group chats, if the reply comes from a forwarded source with chat details:
        if is_group and hasattr(reply, "chat") and reply.chat.first_name and reply.chat.username and not hasattr(reply, "api_kwargs"):
            self.logger.info(
                f"User replied to a forwarded message from another source: "
                f"name: {reply.chat.first_name}, username: {reply.chat.username}"
            )
            new_prompt = (
                f"User replied to a forwarded Telegram message containing the text: `{reply_text}` with extra information: {reply} "
                f"Using these information, Answer their request EXACTLY AS THEY INSTRUCT. NOTHING MORE!"
            )
            self.openai.add_to_history(self.user_id, self.username, chat_id, "system", new_prompt)
            await self.process_openai_response(update, context, prompt, chat_id, role="user",super_access=super_access)
            return None, True

        # If the reply message includes api_kwargs (likely forwarded from a channel)
        if hasattr(reply, "api_kwargs") and "forward_from_chat" in reply.api_kwargs:
            forward_from = reply.api_kwargs["forward_from_chat"]
            # forward_from might be a dict with a username or just a username string
            channel_username = (
                forward_from.get("username") if isinstance(forward_from, dict) and forward_from.get("username") else forward_from
            )
            original_message_id = reply.api_kwargs.get("forward_from_message_id", "")
            self.logger.info(
                f"User replied to a forwarded message from another channel: {channel_username} with the message id: {original_message_id}"
            )
            new_prompt = (
                f"User replied to a forwarded Telegram message containing the text: `{reply_text}` with extra information: {reply} "
                f"and the prompt: {prompt}. Using these information and the link: Telegram_link=https://t.me/{channel_username}/{original_message_id} "
                f"(Recommended to use your tools to get more complete info), Answer their request EXACTLY AS THEY INSTRUCT. NOTHING MORE!"
            )
            self.openai.add_to_history(self.user_id, self.username, chat_id, "system", new_prompt)
            await self.process_openai_response(update, context, prompt, chat_id, role="user", super_access=super_access)
            return None, True

        # Default: prepend the reply text to the prompt.
        return f'"{reply_text} {original_prompt or prompt}', False





    async def handle_private_chat_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str, chat_id: int):
        """Handles prompts in private chats, mirroring group chat handling."""
        user = update.effective_user
        original_prompt = prompt
        mod_trigger_keyword = self.config["mod_trigger_keyword"]
        forward_keyword = self.config["forward_keyword"]
        if prompt.lower().startswith(forward_keyword.lower()):
            await self.handle_channel_commands(update, context, prompt, chat_id)
        elif prompt.lower().startswith(mod_trigger_keyword.lower()):
            await self.handle_moderation_request(update, context, prompt, chat_id, 0, chat_id)  # Using 0 as message_thread_id for private chats
        else:
            # Process reply logic
            prompt, handled = await self.process_reply_logic(update, context, prompt, chat_id, original_prompt=original_prompt, is_group=False)
            if handled:
                return

            self.logger.info("No forwarding/reply information from another source or channel detected.")
            await self.process_openai_response(update, context, prompt, chat_id, role="user")


    async def prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        React to incoming messages and respond accordingly.
        """
        user = update.effective_user
        await self.user_update(update,context)
        if update.edited_message or not update.message or update.message.via_bot:
            return

        # If the user is awaiting channel ID input, do nothing here.
        dummy , is_awaiting = self.usage[user.id].retrieve_config_value('telegram', 'is_awaiting', True)
        if is_awaiting :
            return
        if not await is_allowed(self.config, update, context):
            self.logger.info(f"User:{user.name} with id:{user.id} is added to awaiting list")
            self.usage[user.id].update_telegram_config(True, 'is_awaiting', True)
            await self.send_disallowed_markup(update,context)
            return

        if not await self.check_allowed_and_within_budget(update, context):
            return

        self.logger.info(
            f'New message received from user {update.message.from_user.name} (id: {update.message.from_user.id})')

        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id
        message_thread_id = update.message.message_thread_id
        prompt = message_text(update.message)
        self.last_message[chat_id] = prompt

        if is_group_chat(update):
            await self.handle_group_chat_prompt(update, context, prompt, chat_id, message_thread_id)

        else:
            await self.handle_private_chat_prompt(update, context, prompt, chat_id)
    async def moderate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        React to incoming moderation requests and respond accordingly.
        """
        if update.edited_message or not update.message or update.message.via_bot:
            return

        if not await self.check_allowed_and_within_budget(update, context):
            return

        chat_id = update.effective_chat.id
        user_id = update.message.from_user.id
        prompt = message_text(update.message)
        self.last_message[chat_id] = prompt

        if is_group_chat(update):
            if update.message.text.lower().startswith('/moderate') and update.message.reply_to_message == None :
                self.logger.info(f"User requested for `Direct` Group moderation with message_thread_id:{update.message.message_thread_id} and group_id={update.message.chat.id}")
                prompt = prompt[len("/moderate"):].strip()
                prompt = f"User asked for :`{prompt}`. Using these information : `message_thread_id={update.message.message_thread_id} group_id={update.message.chat.id}`, Answer their request.NOTHING MORE!"                        

            if (update.message.reply_to_message and update.message.reply_to_message.text):
                self.logger.info(f"And replied to the message: {update.message.reply_to_message}")
                prompt = f'"User replied to the text :`{update.message.reply_to_message.text}"' + f". Using these information : 'message_thread_id={update.message.message_thread_id} and group_id={update.message.chat.id}', Answer their request.NOTHING MORE!"
            self.openai.add_to_history(self.user_id, self.username, chat_id, "system", new_prompt)
            await self.process_openai_response(update, context, prompt, chat_id,role="user",super_access=True)
            return



    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle the inline query. This is run when you type: @botusername <query>
        """
        query = update.inline_query.query
        if len(query) < 3:
            return
        if not await self.check_allowed_and_within_budget(update, context, is_inline=True):
            return

        callback_data_suffix = "gpt:"
        result_id = str(uuid4())
        self.inline_queries_cache[result_id] = query
        callback_data = f'{callback_data_suffix}{result_id}'

        await self.send_inline_query_result(update, result_id, message_content=query, callback_data=callback_data)

    async def send_inline_query_result(self, update: Update, result_id, message_content, callback_data=""):
        """
        Send inline query result
        """
        try:
            reply_markup = None
            bot_language = self.config['bot_language']
            if callback_data:
                reply_markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(text=f'🤖 {self.localized_text("answer_with_chatgpt", bot_language)}',
                                         callback_data=callback_data)
                ]])

            inline_query_result = InlineQueryResultArticle(
                id=result_id,
                title=self.localized_text("ask_chatgpt", bot_language),
                input_message_content=InputTextMessageContent(message_content),
                description=message_content,
                thumbnail_url='https://user-images.githubusercontent.com/11541888/223106202-7576ff11-2c8e-408d-94ea-b02a7a32149a.png',
                reply_markup=reply_markup
            )

            await update.inline_query.answer([inline_query_result], cache_time=0)
        except Exception as e:
            self.logger.error(f'An error occurred while generating the result card for inline query {e}')

    async def handle_callback_inline_query(self, update: Update, context: CallbackContext):
        """
        Handle the callback query from the inline query result
        """
        await self.user_update(update,context)

        callback_data = update.callback_query.data
        user_id = update.callback_query.from_user.id
        inline_message_id = update.callback_query.inline_message_id
        name = update.callback_query.from_user.name
        callback_data_suffix = "gpt:"
        query = ""
        bot_language = self.config['bot_language']
        answer_tr = self.localized_text("answer", bot_language)
        loading_tr = self.localized_text("loading", bot_language)

        try:
            if callback_data.startswith(callback_data_suffix):
                unique_id = callback_data.split(':')[1]
                input_tokens = output_tokens = cached_tokens = 0

                # Retrieve the prompt from the cache
                query = self.inline_queries_cache.get(unique_id)
                if query:
                    self.inline_queries_cache.pop(unique_id)
                else:
                    error_message = (
                        f'{self.localized_text("error", bot_language)}. '
                        f'{self.localized_text("try_again", bot_language)}'
                    )
                    await edit_message_with_retry(context, chat_id=None, message_id=inline_message_id,
                                                  text=f'{query}\n\n_{answer_tr}:_\n{error_message}',
                                                  is_inline=True)
                    return

                unavailable_message = self.localized_text("function_unavailable_in_inline_mode", bot_language)
                if self.config['stream']:
                    stream_response = self.openai.get_chat_response_stream(user_id=self.user_id, username=self.username, chat_id=self.chat_id, role="user", query=query)
                    # self.usage[self.user_id].add_chat_tokens(input_string=query)
                    i = 0
                    prev = ''
                    backoff = 0
                    async for content, tokens in stream_response:
                        if is_direct_result(content):
                            cleanup_intermediate_files(content)
                            await edit_message_with_retry(context, chat_id=None,
                                                          message_id=inline_message_id,
                                                          text=f'{query}\n\n_{answer_tr}:_\n{unavailable_message}',
                                                          is_inline=True)
                            return

                        if len(content.strip()) == 0:
                            continue

                        cutoff = get_stream_cutoff_values(update, content)
                        cutoff += backoff

                        if i == 0:
                            try:
                                await edit_message_with_retry(context, chat_id=None,
                                                              message_id=inline_message_id,
                                                              text=f'{query}\n\n{answer_tr}:\n{content}',
                                                              is_inline=True)
                            except:
                                continue

                        elif abs(len(content) - len(prev)) > cutoff or tokens != 'not_finished':
                            prev = content
                            try:
                                use_markdown = tokens != 'not_finished'
                                divider = '_' if use_markdown else ''
                                text = f'{query}\n\n{divider}{answer_tr}:{divider}\n{content}'

                                # We only want to send the first 4096 characters. No chunking allowed in inline mode.
                                text = text[:4096]

                                await edit_message_with_retry(context, chat_id=None, message_id=inline_message_id,
                                                              text=text, markdown=use_markdown, is_inline=True)

                            except RetryAfter as e:
                                backoff += 5
                                await asyncio.sleep(e.retry_after)
                                continue
                            except TimedOut:
                                backoff += 5
                                await asyncio.sleep(0.5)
                                continue
                            except Exception:
                                backoff += 5
                                continue

                            await asyncio.sleep(0.01)

                        i += 1
                        if tokens != 'not_finished':
                            output_tokens = int(tokens)

                else:
                    async def _send_inline_query_response():
                        nonlocal input_tokens, output_tokens, cached_tokens
                        # Edit the current message to indicate that the answer is being processed
                        await context.bot.edit_message_text(inline_message_id=inline_message_id,
                                                            text=f'{query}\n\n_{answer_tr}:_\n{loading_tr}',
                                                            parse_mode=constants.ParseMode.MARKDOWN)

                        self.logger.info(f'Generating response for inline query by {name}')
                        response, input_tokens, output_tokens, cached_tokens = await self.openai.get_chat_response(user_id=self.user_id, username=self.username, chat_id=user_id, role="user", query=query)
                        # self.usage[self.user_id].add_chat_tokens(input_string=query)

                        if is_direct_result(response):
                            cleanup_intermediate_files(response)
                            await edit_message_with_retry(context, chat_id=None,
                                                          message_id=inline_message_id,
                                                          text=f'{query}\n\n_{answer_tr}:_\n{unavailable_message}',
                                                          is_inline=True)
                            return

                        text_content = f'{query}\n\n_{answer_tr}:_\n{response}'

                        # We only want to send the first 4096 characters. No chunking allowed in inline mode.
                        text_content = text_content[:4096]

                        # Edit the original message with the generated content
                        await edit_message_with_retry(context, chat_id=None, message_id=inline_message_id,
                                                      text=text_content, is_inline=True)

                    await wrap_with_indicator(update, context, _send_inline_query_response,
                                              constants.ChatAction.TYPING, is_inline=True)
                output_tokens = int(output_tokens)
                add_chat_request_to_usage_tracker(self.usage, self.config, user_id, input_tokens, output_tokens, cached_tokens)

        except Exception as e:
            self.logger.error(f'Failed to respond to an inline query via button callback: {e}')
            self.logger.exception(e)
            localized_answer = self.localized_text('chat_fail', self.config['bot_language'])
            await edit_message_with_retry(context, chat_id=None, message_id=inline_message_id,
                                          text=f"{query}\n\n_{answer_tr}:_\n{localized_answer} {str(e)}",
                                          is_inline=True)

    async def check_allowed_and_within_budget(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                              is_inline=False) -> bool:
        """
        Checks if the user is allowed to use the bot and if they are within their budget
        :param update: Telegram update object
        :param context: Telegram context object
        :param is_inline: Boolean flag for inline queries
        :return: Boolean indicating if the user is allowed to use the bot
        """
        name = update.inline_query.from_user.name if is_inline else update.message.from_user.name
        user_id = update.inline_query.from_user.id if is_inline else update.message.from_user.id
        await self.user_update(update, context, is_inline)
        if not await is_allowed(self.config, update, context, is_inline=is_inline):
            self.logger.warning(f'User {name} (id: {user_id}) is not allowed to use the bot')
            await self.send_disallowed_markup(update, context, is_inline)
            return False
        if not is_within_budget(self.config, self.usage, update, is_inline=is_inline):
            self.logger.warning(f'User {name} (id: {user_id}) reached their usage limit')
            await self.send_budget_reached_message(update, context, is_inline)
            return False

        return True

    async def send_disallowed_markup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_inline=False):
        """
        Sends the disallowed message to the user along with a join request button.
        """
        if await is_forbidden(self.config,update,context) or await is_allowed(self.config,update,context):
            return
        user = update.effective_user
        fullname = str(user.full_name if user.full_name else 'N/A')
        username = str(user.username if user.username else 'N/A')
        user_id = str(user.id)
        chat_id = self.extract_chat_id(update)
        join_button = InlineKeyboardButton(
            "I wanna join the Bot users!",
            callback_data=f"join_request:{user_id}:{username}:{fullname}:{chat_id}"
        )
        keyboard = [[join_button]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        self.logger.info(f"User:{user.name} with id:{user.id} is not allowed to send message to the bot\n")
        if not is_inline:
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.disallowed_message,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            result_id = str(uuid.uuid4())
            inline_message = f"{self.disallowed_message}\n\nPress the button below to join."
            await self.send_inline_query_result(update, result_id, message_content=inline_message)
    async def send_disallowed_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, is_inline=False):
        """
        Send a simple not allowed message
        """
        if await is_forbidden(self.config,update,context):
            return
        await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.disallowed_message,
                disable_web_page_preview=True
            )
    async def join_request_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the callback when a user presses the join button.
        Notifies the admin with the user's details and options to approve or deny.
        """



        # user = update.effective_user
       # await self.user_update(update,context)
        query = update.callback_query
        await query.answer()
        callback_data = query.data

        self.logger.info(f"callback data:{callback_data}, self.user_id :{self.user_id}, self.chat_id:{self.chat_id}")

        data = callback_data.split(":")
        user_id_str = data[1]
        username = data[2]
        user_fullname = data[3]
        chat_id = data[4]
        # self.usage[self.user_id].update_telegram_config(True, 'is_awaiting', True)
        user_info = (
            f"Join request from:\n"
            f"Name: {user_fullname}\n"
            f"Username: @{username}\n"
            f"User ID: {user_id_str}"
        )
        
        approve_button = InlineKeyboardButton(
            "Approve",
            callback_data=f"admin_approve:{user_id_str}:{username}:{user_fullname}:{chat_id}"
        )
        deny_button = InlineKeyboardButton(
            "Deny",
            callback_data=f"admin_deny:{user_id_str}:{username}:{user_fullname}"
        )
        admin_keyboard = InlineKeyboardMarkup([[approve_button, deny_button]])
        self.logger.info(f"User {user_fullname}:{username} with id:{user_id_str} requested for admin approval.")
        await context.bot.send_message(
            chat_id=self.config['admin_user_id'],
            text=user_info,
            reply_markup=admin_keyboard
        )
        
        await query.edit_message_text("Your request to join has been sent to the admin. Please wait for approval.")

    async def admin_response_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the callback when the admin presses the approve or deny button.
        If approved, the bot instructs the user to send their channel ID.
        """

        query = update.callback_query
        await query.answer()
        callback_data = query.data  # Expected format: "admin_approve:<user_id>" or "admin_deny:<user_id>"

        # logging.info(f"callback data:{callback_data}, self.user_id :{self.user_id}, self.chat_id:{self.chat_id}")

        data = callback_data.split(":")
        action = data[0]
        user_id_str = data[1]
        username = data[2]
        user_fullname = data[3]
        chat_id = data[4]
        self.logger.info(f"action,userid,username:{action}, {user_id_str}, {username}")
        user_id = int(user_id_str)
        
        if action == "admin_approve":
            self.usage[user_id] = UsageTracker(user_id, username, self.chat_id)
            self.usage[user_id].update_telegram_config(True,'is_awaiting',False)
            self.usage[user_id].update_telegram_config(True,'is_allowed',True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="User has been approved to use the bot!\n"
            )
            response_text = f"User {user_fullname} with username {username} (id:{user_id_str}) has been approved."
        elif action == "admin_deny":
            self.usage[user_id].update_telegram_config(True, 'is_awaiting', False)
            self.usage[user_id].update_telegram_config(True,'id_forbidden',True)
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry, you are not granted access to use the bot by the admin."
            )
            response_text = f"User {user_fullname} with username {username} (id:{user_id_str}) has been denied."
        else:
            response_text = "Unknown action."
        self.logger.info(f"{response_text} by the admin: {self.config['admin_user_id']}")
        
        await query.edit_message_text(response_text)


    async def send_budget_reached_message(self, update: Update, _: ContextTypes.DEFAULT_TYPE, is_inline=False):
        """
        Sends the budget reached message to the user.
        """
        if not is_inline:
            await update.effective_message.reply_text(
                message_thread_id=get_thread_id(update),
                text=self.budget_limit_message
            )
        else:
            result_id = str(uuid4())
            await self.send_inline_query_result(update, result_id, message_content=self.budget_limit_message)

    async def post_init(self, application: Application) -> None:
        """
        Post initialization hook for the bot.
        """
        await application.bot.set_my_commands(self.group_commands, scope=BotCommandScopeAllGroupChats())
        await application.bot.set_my_commands(self.commands)
    # Helper: generate a formatted table of all users.
    def get_all_users_table(self) -> str:
        header = f"{'User ID':<12} | {'Username':<20} | {'Allowed':<7}\n" + "-" * 50 + "\n"
        rows = []
        for file_name in os.listdir(self.logs_dir):
            user_dir = os.path.join(self.logs_dir, file_name)
            if os.path.isdir(user_dir):
                file_path = os.path.join(user_dir , f"{file_name}.json")
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    user_id = file_name
                    username = data.get("username", "N/A")
                    allowed = data.get("telegram_config", {}).get("is_allowed", False)
                    rows.append(f"{user_id:<12} | {username:<20} | {str(allowed):<7}")
                except Exception as e:
                    self.logger.info(f"Error reading file {file_name}: {e}")
                    continue
        return header + "\n".join(rows) if rows else "No users found."

    # Helper: update a user's permission status.
    async def update_user_permission(self, update: Update, target_user_id: str, new_status: bool) -> bool:
        file_path = os.path.join(self.logs_dir, target_user_id, f"{target_user_id}.json")
        if not os.path.isfile(file_path):
            await update.message.reply_text("User file not found.")
            return False
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            if "telegram_config" in data:
                data["telegram_config"]["is_allowed"] = new_status
            else:
                data["telegram_config"] = {"is_allowed": new_status}
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            await update.message.reply_text(f"User {target_user_id} allowed status updated to {new_status}.")
            return True
        except Exception as e:
            self.logger.info(f"Failed to update user file: {e}")
            await update.message.reply_text("Failed to update user file.")
            return False

    # Main command handler.
    async def config_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle configuration commands for:
        - get:     /setconfig get <openai|telegram> <config_key> [user_id]
        - set:     /setconfig set <openai|telegram> <config_key> <new_value> [user_id]
        - list:    /setconfig list      (lists allowed users only)
        - all:     /setconfig all       (lists all users with permission status)
        - permit:  /setconfig permit <user_id> <true|false>
        - config:  /setconfig config <user_id> (returns full config for that user)
        - logfile: /setconfig logfile <user_id> [n]
        """
        # Update current user data.
        await self.user_update(update, context)
        user = update.effective_user
        admin_check = is_admin(self.config, user.id)

        # Only admins can run the following commands.
        if not admin_check and context.args[0].lower() in ("list", "all", "permit", "config", "logfile") or await is_forbidden(self.config,update,context) :
            if await is_allowed(self.config, update, context):
                await self.send_disallowed_message(update, context)
            return

        # If no arguments are provided, show usage.
        if not context.args:
            await update.message.reply_text(
                "Usage:\n"
                "  To get:    /setconfig get <openai|telegram> <config_key> [user_id]\n"
                "  To set:    /setconfig set <openai|telegram> <config_key> <new_value> [user_id]\n"
                "  To list allowed users: /setconfig list\n"
                "  To list all users:     /setconfig all\n"
                "  To permit/disallow a user: /setconfig permit <user_id> <true|false>\n"
                "  To get full config:    /setconfig config <user_id>"
                "  To get [n last lines] user_log file: /setconfig logfile <user_id> [n]"
            )
            return

        action = context.args[0].lower()

        # --- Branch: list allowed users ---
        if action == "list":
            if not admin_check :
                if await is_allowed(self.config, update, context):
                    await self.send_disallowed_message(update, context)
                return
            allowed_users = []
            for file_name in os.listdir(self.logs_dir):
                user_dir = os.path.join(self.logs_dir, file_name)
                if os.path.isdir(user_dir):
                    file_path = os.path.join(user_dir, f"{file_name}.json")
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                        if data.get("telegram_config", {}).get("is_allowed", False):
                            allowed_users.append(f"{file_name}: {data.get('username', 'N/A')}")
                    except Exception as e:
                        self.logger.info(f"Error while getting allowed users list: {e}")
                        continue
            msg = "Allowed users:\n" + "\n".join(allowed_users) if allowed_users else "No allowed users found."
            await update.message.reply_text(msg)
            return

        # --- Branch: list all users ---
        if action == "all":
            if not admin_check :
                if await is_allowed(self.config, update, context):
                    await self.send_disallowed_message(update, context)
                return
            table = self.get_all_users_table()
            await update.message.reply_text(table)
            return

        # --- Branch: permit/disallow a user ---
        if action == "permit":
            if not admin_check :
                if await is_allowed(self.config, update, context):
                    await self.send_disallowed_message(update, context)
                return
            if len(context.args) != 3:
                await update.message.reply_text("Usage: /setconfig permit <user_id> <true|false>")
                return
            target_user_id = context.args[1]
            new_status_str = context.args[2].lower()
            if new_status_str not in ("true", "false"):
                await update.message.reply_text("The allowed status must be 'true' or 'false'.")
                return
            new_status = new_status_str == "true"
            await update_user_permission(self, update, target_user_id, new_status)
            return

        # --- Branch: get full configuration for a specified user ---
        if action == "config":
            if not admin_check :
                if await is_allowed(self.config, update, context):
                    await self.send_disallowed_message(update, context)
                return
            if len(context.args) > 2:
                await update.message.reply_text("Usage: /setconfig config <user_id>")
                return
            elif len(context.args) == 1:
                 target_user_id = user.id
            else :
                target_user_id = context.args[1]
            file_path = os.path.join(self.logs_dir, target_user_id, f"{target_user_id}.json")
            if not os.path.isfile(file_path):
                await update.message.reply_text("User file not found.")
                return
            try:
                common_args = {
                    'message_thread_id': get_thread_id(update),
                    'reply_to_message_id': get_reply_to_message_id(self.config, update),
                    'caption': f"Here is the full config for user {target_user_id}",
                }
                user_file = file_path
                await update.message.reply_document(**common_args, document=open(user_file, 'rb'))
            except Exception as e:
                self.logger.info(f"Error reading config for user {target_user_id}: {e}")
                await update.message.reply_text("Error reading user config.")
            return


        if action == "logfile":
            if not admin_check :
                if await is_allowed(self.config, update, context):
                    await self.send_disallowed_message(update, context)
                return
            if len(context.args) == 1:
                target_user_id = user.id
            elif len(context.args) == 2:
                target_user_id = context.args[2]
            elif len(context.args) == 3:
                common_args = {
                    'message_thread_id': get_thread_id(update),
                    'reply_to_message_id': get_reply_to_message_id(self.config, update)
                }
                try:
                    from collections import deque
                    target_user_id = context.args[1]
                    lines = int(context.args[2])
                    user_file = os.path.join(self.logs_dir, target_user_id, f"user_{target_user_id}.log")
                    with open(user_file, 'r') as f:
                        logs = list(deque(f, maxlen=lines))
                        await update.message.reply_text(logs, **common_args)
                        return
                except Exception as e:
                    self.logger.info(f"Error reading config's last {lines} lines for user {target_user_id}: {e}")
                    await update.message.reply_text(f"Error reading user config's last {lines} lines:{e}")
                    return

            else:
                await update.message.reply_text("Usage: /setconfig logfile <user_id> [n lines]")
                return

            user_file = os.path.join(self.logs_dir, str(target_user_id), f"user_{target_user_id}.log")
            if not os.path.isfile(user_file):
                await update.message.reply_text("User file for:{} not found.")
                return
            try:
                common_args = {
                    'message_thread_id': get_thread_id(update),
                    'reply_to_message_id': get_reply_to_message_id(self.config, update),
                    'caption': f"Here is the full log for user {target_user_id}",
                }
                await update.message.reply_document(**common_args, document=open(user_file, 'rb'))
            except Exception as e:
                self.logger.info(f"Error reading config for user {target_user_id}: {e}")
                await update.message.reply_text(f"Error getting user config:{e}")
            return

        # --- Branch: get and set configuration values ---
        # This branch supports an optional target user id.
        # For "set": /setconfig set <openai|telegram> <config_key> <new_value> [target_user_id]
        # For "get": /setconfig get <openai|telegram> <config_key> [target_user_id]
        if action not in ("get", "set"):
            await update.message.reply_text("Invalid action. Use 'get', 'set', 'list', 'all', 'permit', or 'config'.")
            return


        self.logger.info(f"length: {len(context.args)}")
        config_type = context.args[1].lower()
        key = context.args[2] if len(context.args)>=3 else await update.message.reply_text("Invalid usage. Use /setconfig <set|get> <openai|telegram> <config_key>")

        # Determine the target user id.
        # For "get": if there is a 4th argument and it's numeric, use it; otherwise use current user.
        # For "set": if there is more than 3 arguments and the last argument is numeric, treat it as target id.
        target_user_id = user.id  # default to current user
        if action == "set":
            if len(context.args) >= 5 and context.args[-1].isdigit():
                # Only admins can run the following commands.
                if not admin_check :
                    if await is_allowed(self.config, update, context):
                        await self.send_disallowed_message(update, context)
                    return
                target_user_id = str(context.args[-1])
                new_val_str = " ".join(context.args[3:-1])
            else:
                new_val_str = " ".join(context.args[3:])
        elif action == "get":
            if len(context.args) == 4 and context.args[3].isdigit():
                # Only admins can run the following commands.
                if not admin_check :
                    if await is_allowed(self.config, update, context):
                        await self.send_disallowed_message(update, context)
                    return
                target_user_id = str(context.args[3])
        for file_name in os.listdir(self.logs_dir):
            if file_name.startswith(str(target_user_id)):
                file_path = os.path.join(self.logs_dir, file_name, f"{file_name}.json")
            
                with open(file_path, "r") as f:
                    data = json.load(f)
                username = data.get("username", "N/A")
                allowed = data.get("telegram_config", {}).get("is_allowed", False)

        self.usage[target_user_id] = UsageTracker(target_user_id, username, target_user_id)

        user_ids_list = [
                    filename for filename in os.listdir(self.logs_dir)
                    if os.path.isdir(os.path.join(self.logs_dir, filename))
                ]
        # Ensure a configuration manager exists for the target user.
        if str(target_user_id) not in user_ids_list:
            await update.message.reply_text(f"Configuration manager for that user was not found:{target_user_id}")
            return

        if action == "set":
            if config_type == "openai":
                success = self.usage[target_user_id].update_openai_config(admin_check, key, new_val_str)
                if success:
                    await update.message.reply_text(f"Updated OpenAI config for user {target_user_id}: {key} -> {new_val_str}")
                else:
                    await update.message.reply_text("Failed to update OpenAI config. Check the key name and value format.")
            elif config_type == "telegram":
                success = self.usage[target_user_id].update_telegram_config(admin_check, key, new_val_str)
                if success:
                    await update.message.reply_text(f"Updated Telegram config for user {target_user_id}: {key} -> {new_val_str}")
                else:
                    await update.message.reply_text("Failed to update Telegram config. Check the key name and value format.")
            else:
                await update.message.reply_text("Invalid config type. Use either 'openai' or 'telegram'.")
        elif action == "get":
            if config_type == "openai":
                done, current_value = self.usage[target_user_id].retrieve_config_value('openai', key, admin_check)
                if done and current_value is not None:
                    await update.message.reply_text(f"Current OpenAI config for user {target_user_id}: {key} = {current_value}")
                else:
                    await update.message.reply_text("Key not found in OpenAI config.")
            elif config_type == "telegram":
                done, current_value = self.usage[target_user_id].retrieve_config_value('telegram', key, admin_check)
                if done and current_value is not None:
                    await update.message.reply_text(f"Current Telegram config for user {target_user_id}: {key} = {current_value}")
                else:
                    await update.message.reply_text("Key not found in Telegram config.")
            else:
                await update.message.reply_text("Invalid config type. Use either 'openai' or 'telegram'.")

    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Sends a broadcast message to all users who have folders in user_logs directory.
        Only accessible by admin users. Requires text confirmation.
        """
        await self.user_update(update, context)
        if not is_admin(self.config, update.message.from_user.id):
            await self.send_disallowed_message(update, context)
            return

        message_to_broadcast = message_text(update.message)
        if not message_to_broadcast:
            await update.message.reply_text("Please provide a message to broadcast after the /broadcast command.")
            return

        # Count potential recipients
        recipient_count = sum(1 for user_id in os.listdir(self.logs_dir) if os.path.isdir(os.path.join(self.logs_dir, user_id)))
        
        # Store the pending broadcast in the user's data file
        broadcast_id = str(uuid4())
        self.usage[self.user_id].add_pending_broadcast(broadcast_id, message_to_broadcast, recipient_count)

        # Create confirmation message with preview
        confirmation_text = (
            f"📢 Broadcast Preview:\n\n"
            f"{message_to_broadcast}\n\n"
            f"This message will be sent to {recipient_count} users.\n\n"
            f"To confirm, reply with: CONFIRM-{broadcast_id}\n"
            f"To cancel, reply with: CANCEL-{broadcast_id}\n\n"
            f"This confirmation request will expire in 5 minutes."
        )

        await update.message.reply_text(confirmation_text)

    async def handle_broadcast_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Process text-based broadcast confirmations."""
        await self.user_update(update, context)
        
        if not update.message or not update.message.text:
            return False
            
        message_text = update.message.text
        if not message_text.startswith(('CONFIRM-', 'CANCEL-')):
            return False
            
        if not is_admin(self.config, update.message.from_user.id):
            await self.send_disallowed_message(update, context)
            return True

        # Split only on the first occurrence of '-'
        broadcast_id = message_text.split('-', 1)[1]
        
        broadcast_data = self.usage[self.user_id].get_pending_broadcast(broadcast_id)
        if not broadcast_data:
            await update.message.reply_text("This broadcast confirmation code is invalid or has expired.")
            return True

        if message_text.startswith('CANCEL-'):
            self.usage[self.user_id].remove_pending_broadcast(broadcast_id)
            await update.message.reply_text("Broadcast cancelled.")
            return True
            
        if message_text.startswith('CONFIRM-'):
            message_to_broadcast = broadcast_data['message']
            success_count = 0
            fail_count = 0
            
            for user_id in os.listdir(self.logs_dir):
                if os.path.isdir(os.path.join(self.logs_dir, user_id)):
                    try:
                        await context.bot.send_message(
                            chat_id=int(user_id),
                            text=f"📢 Broadcast from admin:\n\n{message_to_broadcast}"
                        )
                        success_count += 1
                    except Exception as e:
                        self.logger.error(f"Failed to send broadcast to user {user_id}: {str(e)}")
                        fail_count += 1
            
            self.usage[self.user_id].remove_pending_broadcast(broadcast_id)
            summary = f"Broadcast completed:\n✅ Successful: {success_count}\n❌ Failed: {fail_count}"
            await update.message.reply_text(summary)
            return True
            
        return False

    def run(self):
        """
        Runs the bot indefinitely until the user presses Ctrl+C
        """
        application = ApplicationBuilder() \
            .token(self.config['token']) \
            .proxy_url(self.config['proxy']) \
            .get_updates_proxy_url(self.config['proxy']) \
            .post_init(self.post_init) \
            .concurrent_updates(True) \
            .build()

        application.add_handler(CommandHandler('reset', self.reset))
        application.add_handler(CommandHandler('help', self.help))
        application.add_handler(CommandHandler('image', self.image))
        application.add_handler(CommandHandler('tts', self.tts))
        application.add_handler(CommandHandler('start', self.help))
        application.add_handler(CommandHandler('stats', self.stats))
        application.add_handler(CommandHandler('resend', self.resend))
        application.add_handler(CommandHandler('broadcast', self.broadcast_message, filters=filters.ChatType.PRIVATE))
        # Add message handler for broadcast confirmations before the general message handler
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'^(CONFIRM|CANCEL)-[a-f0-9-]+$'),
            self.handle_broadcast_confirmation
        ))
        application.add_handler(CommandHandler(
            'chat', self.prompt, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP)
        )
        application.add_handler(CommandHandler(
            'moderate', self.moderate, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP)
        )
        application.add_handler(CommandHandler(
            'setconfig', self.config_commands, filters=filters.ChatType.GROUP | filters.ChatType.SUPERGROUP | filters.ChatType.PRIVATE)
        )
        application.add_handler(MessageHandler(
            filters.PHOTO | filters.Document.IMAGE,
            self.vision))
        application.add_handler(MessageHandler(
            filters.AUDIO | filters.VOICE | filters.Document.AUDIO |
            filters.VIDEO | filters.VIDEO_NOTE | filters.Document.VIDEO,
            self.transcribe))
        
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), self.prompt))
        application.add_handler(InlineQueryHandler(self.inline_query, chat_types=[
            constants.ChatType.GROUP, constants.ChatType.SUPERGROUP, constants.ChatType.PRIVATE
        ]))
        


        application.add_handler(CallbackQueryHandler(self.join_request_callback, pattern=r"^join_request:[0-9-]+:[0-9a-zA-Z_]+:.+:[0-9-]+$"))

        application.add_handler(CallbackQueryHandler(self.admin_response_callback, pattern=r"^admin_(approve|deny):[0-9-]+:[0-9a-zA-Z_]+:.+:[0-9-]+$"))

        application.add_handler(CallbackQueryHandler(self.handle_callback_inline_query,pattern=r"^gpt:"))

        application.add_error_handler(error_handler)
        


        application.run_polling()
