import logging
import tempfile
from typing import Dict

from .plugin import Plugin


class AutoTextToSpeech(Plugin):
    """
    A plugin to convert text to speech using Openai Speech API
    """

    def get_source_name(self) -> str:
        return "TTS"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "translate_text_to_speech",
            "description": "Translate text to speech and give a voice interacting with the user."
            "Call it wehenever the user asks or you think is appropriate to use this function.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to convert to speech and then give to the user."},
                    "user_id": {
                        "type": "string",
                        "description": "The chat ID to send the response to. Defaults to user_id if not specified.",
                    },
                    "username": {
                        "type": "string",
                        "description": "The username to send the response to.If it is same as the user_id, Defaults to user_id if not specified.",
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "The chat ID to send the response to. Defaults to user_id if not specified.",
                    }
                },
                "required": ["text", "user_id"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        user_id = kwargs['user_id']
        text = kwargs['text']
        username = kwargs.get("username", user_id)
        chat_id = kwargs.get('chat_id', user_id)
        try:
            bytes, text_length = await helper.generate_speech(text=text, user_id=user_id, chat_id=chat_id, username=username)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.opus') as temp_file:
                temp_file.write(bytes.getvalue())
                temp_file_path = temp_file.name
        except Exception as e:
            logging.exception(e)
            return {"Result": "Exception: " + str(e)}
        return {
            'direct_result': {
                'kind': 'file',
                'format': 'path',
                'value': temp_file_path
            }
        }
