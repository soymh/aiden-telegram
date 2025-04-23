import os
import openai
import httpx
import json
import logging
import requests
from typing import Dict
from .plugin import Plugin
import random
import string
import base64

class ImageGeneratorPlugin(Plugin):
    """
    A plugin to generate images using OpenAI's DALL-E or FLUX model based on user prompts.
    """

    def get_source_name(self) -> str:
        return "ImageGenerator"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "generate_image",
            "description": "Generate an image based on a text prompt using OpenAI's DALL-E or FLUX model;Default is DALL-E (Recommended)",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "A text description of the image to generate."
                    },
                    "use_flux": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether to use the FLUX model instead of OpenAI's DALL-E."
                    }
                },
                "required": ["prompt"],
            },
        }]

    def generate_random_string(self, length: int) -> str:
        """Generate a random string of a given length."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    async def execute(self, function_name: str, helper, **kwargs) -> Dict:
        try:
            prompt = kwargs["prompt"]
            use_flux = kwargs.get("use_flux", False)
            
            if use_flux:
                return await self.generate_image_flux(helper, prompt)
            else:
                return await self.generate_image_openai(helper, prompt)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return {'result': f"Unable to generate image: {str(e)}"}

    async def generate_image_openai(self, helper, prompt: str) -> Dict:
        """
        Generates an image from the given prompt using OpenAI's DALL-E model.
        """
        try:
            image_url, image_size = await helper.generate_image(user_id=None, username=None, chat_id=None, prompt=prompt)
            return {
                'direct_result': {
                    'kind': 'document',
                    'format': 'url',
                    'value': image_url,
                    'costly': True,
                    'image_size': image_size
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI generation error: {str(e)}")

    async def generate_image_flux(self, helper, prompt: str) -> Dict:
        """
        Generates an image from the given prompt using FLUX model.
        """
        try:
            b64_json, image_size = await helper.generate_image_flux(user_id=None, username=None, prompt=prompt)


            # Decode Base64 and save as image
            image_data = base64.b64decode(b64_json)
            image_bytes = BytesIO(image_data)
            image_bytes.name = 'generated_image.png'
            # Save the image locally
            # image_file_path = self.save_image(image_data, "flux_images")
            return {
                'direct_result': {
                    'kind': 'document',
                    'format': 'url',
                    'value': image_bytes,
                    'costly': True,
                    'image_size': image_size
                }
            }
        except Exception as e:
            raise Exception(f"FLUX generation error: {str(e)}")

    # def save_image(self, image_data: bytes, folder_name: str) -> str:
    #     """Save an image to a local folder."""
    #     if not os.path.exists(f"uploads/{folder_name}"):
    #         os.makedirs(f"uploads/{folder_name}")
    #     try:
    #         image_file_path = os.path.join(f"uploads/{folder_name}", f"{self.generate_random_string(15)}.png")
    #         with open(image_file_path, "wb") as f:
    #             f.write(image_data)

    #         return image_file_path
    #     except e:
    #         return e
