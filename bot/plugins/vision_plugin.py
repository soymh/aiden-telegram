import os
import json
from typing import Dict
import requests
from .plugin import Plugin


class VisionPlugin(Plugin):
    """
    A plugin to interact with the vision endpoint of the Telegram bot API.
    """

    def get_source_name(self) -> str:
        return "Vision API"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "interpret_image",
            "description": "Send an image to the vision endpoint for interpretation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "The user ID to associate with the request."
                    },
                    "file_id": {
                        "type": "string",
                        "description": "The Telegram file_id of the image to interpret."
                    },
                    "prompt": {
                        "type": "string",
                        "description": "A prompt to guide the image interpretation."
                    },
                    "chat_id": {
                        "type": "string",
                        "description": "The chat ID to send the response to. Defaults to user_id if not specified.",
                    },
                    "username": {
                        "type": "string",
                        "description": "The username to send the response to. Defaults to user_id if not specified.",
                    }
                },
                "required": ["user_id", "file_id", "prompt"]
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        user_id = kwargs['user_id']
        file_id = kwargs['file_id']
        username = kwargs.get("username", user_id)
        prompt = kwargs['prompt']
        chat_id = kwargs.get('chat_id', user_id)

        api_url = 'http://localhost:5000/api/send_message'
        api_key = os.getenv('TELEGRAM_BOT_API_KEY', 'bfb59390-0fdb-4f80-8986-10cb0c31c090')

        headers = {
            'X-API-Key': api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'user_id': user_id,
            'chat_id': chat_id,
            'message_type': 'vision',
            'file_id': file_id,
            'prompt': prompt,
            'username': username
        }

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

            result = response.json()
            return {"result": result}

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
