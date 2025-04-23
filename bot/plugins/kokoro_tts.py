import logging
import tempfile
from typing import Dict

from .plugin import Plugin


class KokoroTTSPlugin(Plugin):
    """
    A plugin to convert text to speech using KokoroTTS
    """

    def get_source_name(self) -> str:
        return "KokoroTTS"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "generate_kokoro_speech",
            "description": "Generate speech from text using KokoroTTS. This provides a different voice style compared to OpenAI's TTS.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to convert to speech."},
                    "voice": {
                        "type": "string",
                        "description": "The voice style to use for speech generation.",
                        "enum": ["voice1", "voice2", "voice3"]  # Update with actual voice options
                    }
                },
                "required": ["text"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            bytes, text_length = await helper.generate_kokoro_speech(text=kwargs['text'])
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
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