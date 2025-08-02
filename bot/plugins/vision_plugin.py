import io
import logging
from typing import Dict

from PIL import Image
from telegram import Bot

from .plugin import Plugin
from os import getenv

class VisionPlugin(Plugin):
    """
    A plugin to interpret images from Telegram using the Vision model.
    """

    def get_source_name(self) -> str:
        return "Telegram Vision"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "interpret_telegram_image",
            "description": "Interpret an image from user using the Vision model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {
                        "type": "string",
                        "description": "The user file ID of the image.",
                    },
                    "prompt": {
                        "type": "string",
                        "description": "A prompt to guide the image interpretation. Use the user query as prompt.",
                    },
                    },
                },
                "required": ["file_id", "prompt"],
            },
        ]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            file_id = kwargs["file_id"]
            prompt = kwargs.get("prompt")

            # Download the image from Telegram
            try:
                bot = Bot(getenv('TELEGRAM_BOT_TOKEN'))
                media_file = await bot.get_file(file_id)
                temp_file = io.BytesIO(await media_file.download_as_bytearray())
            except Exception as e:
                return {"result": f"Error downloading image: {str(e)}"}

            # Convert the image to PNG format
            temp_file_png = io.BytesIO()
            try:
                original_image = Image.open(temp_file)
                original_image.save(temp_file_png, format="PNG")
                temp_file_png.seek(0)  # Reset the buffer position to the beginning
            except Exception as e:
                return {"result": f"Error converting image to PNG: {str(e)}"}

            # Interpret the image using the OpenAIHelper
            interpretation, tokens = await helper.interpret_image(helper.user_id, helper.username, helper.chat_id, temp_file_png, prompt=prompt)
            return {"result": interpretation}

        except Exception as e:
            logging.exception(e)
            return {"result": f"Error interpreting image: {str(e)}"}