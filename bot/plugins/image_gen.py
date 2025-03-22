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
                return await self.generate_image_flux(prompt)
            else:
                return await self.generate_image_openai(prompt)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return {'result': f"Unable to generate image: {str(e)}"}

    async def generate_image_openai(self, prompt: str) -> Dict:
        """
        Generates an image from the given prompt using OpenAI's DALL-E model.
        """
        try:
            # Fetch OpenAI API parameters from environment variables
            model = os.environ.get('IMAGE_MODEL', 'dall-e-3')
            quality = os.environ.get('IMAGE_QUALITY', 'standard')
            style = os.environ.get('IMAGE_STYLE', 'vivid')
            size = os.environ.get('IMAGE_SIZE', '1024x1024')
            api_key = os.environ['OPENAI_API_KEY']
            proxy = os.environ.get('PROXY', None) or os.environ.get('OPENAI_PROXY', None)
            
            # Build the OpenAI client
            http_client = httpx.AsyncClient(proxy=proxy) if proxy else None
            client = openai.AsyncOpenAI(api_key=api_key, http_client=http_client)

            # Generate image using OpenAI API
            response = await client.images.generate(
                prompt=prompt,
                n=1,
                model=model,
                quality=quality,
                style=style,
                size=size
            )

            if not response.data:
                raise Exception("No response from OpenAI API.")

            image_url = response.data[0].url

            # Download the image
            response = requests.get(image_url)
            if response.status_code != 200:
                raise Exception(f"Failed to download image from OpenAI: {response.status_code}")

            # Save the image locally
            image_file_path = self.save_image(response.content, "openai_images")
            return {
                'direct_result': {
                    'kind': 'photo',
                    'format': 'path',
                    'value': image_file_path
                }
            }
        except Exception as e:
            raise Exception(f"OpenAI generation error: {str(e)}")

    async def generate_image_flux(self, prompt: str) -> Dict:
        """
        Generates an image from the given prompt using FLUX model.
        """
        try:
            # Fetch FLUX API parameters from environment variables
            model = os.environ.get('IMAGE_MODEL', 'dall-e-2')
            size = os.environ.get('IMAGE_SIZE', '1024x1024')
            api_key = os.environ.get('FLUX_API_KEY', 'XXX')

            if api_key == 'XXX':
                raise ValueError("Invalid API Key set for FLUX_API_KEY in the config.")

            # Parse the image_size string to extract width and height
            image_size_parts = size.split('x')
            if len(image_size_parts) != 2:
                raise ValueError("Invalid image_size format. Expected format: 'widthxheight'.")

            image_width = int(image_size_parts[0])
            image_height = int(image_size_parts[1])

            # Prepare the request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "width": image_width,
                "height": image_height,
                "steps": 24,
                "n": 1,
                "response_format": "b64_json"
            }

            # Set the headers
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Make the POST request
            response = requests.post(
                "/images/generations",
                headers=headers,
                data=json.dumps(payload)
            )

            if response.status_code != 200:
                raise Exception(f"FLUX API error: {response.status_code} - {response.text}")

            response_data = response.json()
            if 'data' not in response_data or not response_data['data']:
                raise Exception("No data in response from FLUX API.")

            b64_json = response_data['data'][0]['b64_json']

            # Decode Base64 and save as image
            image_data = base64.b64decode(b64_json)

            # Save the image locally
            image_file_path = self.save_image(image_data, "flux_images")
            return {
                'direct_result': {
                    'kind': 'document',
                    'format': 'path',
                    'value': image_file_path
                }
            }
        except Exception as e:
            raise Exception(f"FLUX generation error: {str(e)}")

    def save_image(self, image_data: bytes, folder_name: str) -> str:
        """Save an image to a local folder."""
        if not os.path.exists(f"uploads/{folder_name}"):
            os.makedirs(f"uploads/{folder_name}")
        try:
            image_file_path = os.path.join(f"uploads/{folder_name}", f"{self.generate_random_string(15)}.png")
            with open(image_file_path, "wb") as f:
                f.write(image_data)

            return image_file_path
        except e:
            return e
