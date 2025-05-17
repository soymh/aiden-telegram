import os
import logging
import tempfile
from typing import Dict
import yt_dlp
import shutil
import json
import random
import string

from .plugin import Plugin


class YouTubeDownloaderPlugin(Plugin):
    """
    A plugin to download YouTube videos, extract audio, and get subtitles using yt-dlp
    """

    def get_source_name(self) -> str:
        return "YouTube Downloader"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "download_youtube_video",
            "description": "Download a YouTube video, extract audio, or get subtitles",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The YouTube video URL to download"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["video", "audio", "subtitles"],
                        "description": "What to download: full video, audio-only, or subtitles",
                        "default": "video"
                    },
                    "subtitle_lang": {
                        "type": "string",
                        "description": "Language code for subtitles (e.g. 'en', 'es', 'fr'). If not specified, will try to get all available subtitles",
                        "default": "en"
                    }
                },
                "required": ["url"]
            }
        }]

    def generate_random_string(self, length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        url = kwargs['url']
        action = kwargs.get('action', 'video')
        subtitle_lang = kwargs.get('subtitle_lang', 'en')
        
        # Create upload directory for youtube downloads
        temp_dir = "uploads/youtube"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            
        # Generate a random filename
        random_filename = self.generate_random_string(15)
        output_path = os.path.join(temp_dir, f"%(title)s_{random_filename}.%(ext)s")

        try:
            # Common yt-dlp options
            ydl_opts = {
                'quiet': True,
                'no-warnings': True,
                'outtmpl': output_path,
                # Enable cleanup of downloaded fragments
                'cleanup': True
            }

            if action == 'video':
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }]
                })
            elif action == 'audio':
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'extract_audio': True,
                    'audio_format': 'mp3',
                    'audio_quality': '0',  # Best quality (0 = best, 9 = worst)
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '320',  # Highest MP3 bitrate
                    }, {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    }]
                })
            elif action == 'subtitles':
                ydl_opts.update({
                    'skip_download': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': [subtitle_lang],
                    'postprocessors': [{
                        'key': 'FFmpegSubtitlesConvertor',
                        'format': 'srt',
                    }]
                })

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if not info:
                        return {"error": "Failed to extract video information"}

                    # Get the path of the downloaded file
                    base_filename = ydl.prepare_filename(info)
                    
                    if action == 'subtitles':
                        # Look for the subtitle file
                        srt_path = os.path.splitext(base_filename)[0] + f'.{subtitle_lang}.srt'
                        if not os.path.exists(srt_path):
                            auto_srt_path = os.path.splitext(base_filename)[0] + f'.{subtitle_lang}.auto.srt'
                            if os.path.exists(auto_srt_path):
                                srt_path = auto_srt_path
                            else:
                                return {"error": f"No subtitles found for language {subtitle_lang}"}
                        
                        with open(srt_path, 'r', encoding='utf-8') as f:
                            subtitles_content = f.read()
                        return {"result": subtitles_content}
                    else:
                        # For video and audio, correct the extension
                        if action == 'audio':
                            actual_file = os.path.splitext(base_filename)[0] + '.mp3'
                        else:  # video
                            actual_file = os.path.splitext(base_filename)[0] + '.mp4'

                        if not os.path.exists(actual_file):
                            return {"error": f"Failed to download {action}"}

                        return {
                            'direct_result': {
                                'kind': 'document',
                                'format': 'path',
                                'value': actual_file
                            }
                        }

            except Exception as e:
                logging.error(f"Error downloading from YouTube: {str(e)}")
                return {"error": f"Failed to process video: {str(e)}"}

        except Exception as e:
            logging.error(f"Error in YouTube downloader: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}