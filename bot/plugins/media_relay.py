from typing import Dict
from .plugin import Plugin

class MediaRelayPlugin(Plugin):
    """
    A plugin to relay media files (images, PDFs, videos, etc) directly to users
    """
    def get_source_name(self) -> str:
        return "MediaRelay"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "relay_media",
            "description": "Send a media file (image, PDF, video, etc) directly to the user from a URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the media file to send"
                    },
                    "kind": {
                        "type": "string",
                        "enum": ["photo", "document", "video", "file"],
                        "description": "The type of media to send. Use 'photo' for images, 'document' for PDFs, 'video' for videos, or 'file' for other files",
                        "default": "file"
                    }
                },
                "required": ["url"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        url = kwargs['url']
        kind = kwargs.get('kind', 'file')

        return {
            'direct_result': {
                'kind': kind,
                'format': 'url',
                'value': url
            }
        }