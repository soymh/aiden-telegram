import os
import json
from typing import Dict
import requests

from .plugin import Plugin


class MessagePlugin(Plugin):
    """
    A plugin to send messages via the Telegram bot API.
    """

    def get_source_name(self) -> str:
        return "Message API"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "send_message",
            "description": "Send a message to a Telegram user or group.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID to send the message to."
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "The chat ID to send the message to. Defaults to user_id if not specified.",
                    },
                    "message_type": {
                        "type": "string",
                        "enum": ["text", "photo", "voice", "document", "direct_result"],
                        "description": "The type of message to send.",
                        "default": "text"
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the message (text, URL, base64 data, etc.)."
                    },
                    "caption": {
                        "type": "string",
                        "description": "The caption for photo, voice, or document messages."
                    },
                    "file_id": {
                        "type": "string",
                        "description": "The file_id for file sending messages."
                    }
                },
                "required": ["user_id", "content", "message_type"]
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        user_id = kwargs['user_id']
        chat_id = kwargs.get('chat_id', user_id)
        message_type = kwargs['message_type']
        content = kwargs['content']
        caption = kwargs.get('caption', '')
        file_id = kwargs.get('file_id', 'document.bin')

        api_url = 'http://localhost:5000/api/send_message'
        api_key = os.getenv('TELEGRAM_BOT_API_KEY', 'bfb59390-0fdb-4f80-8986-10cb0c31c090')

        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'user_id': user_id,
            'chat_id': chat_id,
            'message_type': message_type,
            'content': content,
            'caption': caption,
            'file_id': file_id,
        }
        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            return {"result": result}

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}