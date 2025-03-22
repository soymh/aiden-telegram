import os
import re
import requests
import html2text
from bs4 import BeautifulSoup
from typing import Dict, List
from .plugin import Plugin  # Adjust the import based on your project structure

class TelegramScraperPlugin(Plugin):
    """
    A plugin to scrape a Telegram post for its text content, author, date/time,
    image URLs, and video URLs.
    """
    def get_source_name(self) -> str:
        return "TelegramScraper"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "scrape_telegram_post",
            "description": (
                "Scrapes a Telegram post given its URL (or multiple URLs separated by commas) "
                "and returns a dictionary with the post content, author, datetime, image URLs, "
                "and video URLs."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "post_url": {
                        "type": "string",
                        "description": (
                            "The Telegram post URL. For multiple posts, separate URLs with commas."
                        )
                    }
                },
                "required": ["post_url"]
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        post_url = kwargs.get("post_url")
        if not post_url:
            return {"error": "No post URL provided."}
        
        # Build list of URLs (append the embed parameters to each URL)
        url_list = [entry.strip() + '?embed=1&mode=tme' for entry in post_url.split(",")]
        headers = {
            'user-agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/77.0.3865.90 Safari/537.36 TelegramBot (like TwitterBot)'
            )
        }
        
        posts = []
        for url in url_list:
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract text content from the post
                content_div = soup.find('div', {'class': 'tgme_widget_message_text', 'dir': 'auto'})
                content_html = str(content_div) if content_div else ""
                text_content = self.html_to_text(content_html)
                
                # Extract author
                author = ""
                author_div = soup.find('div', {'class': 'tgme_widget_message_author'})
                if author_div:
                    author_span = author_div.find('span', {'dir': 'auto'})
                    if author_span:
                        author = self.html_to_text(str(author_span))
                
                # Extract datetime information
                datetime_value = ""
                datetime_span = soup.find('span', {'class': 'tgme_widget_message_meta'})
                if datetime_span:
                    time_tag = datetime_span.find('time', {'class': 'datetime'})
                    if time_tag:
                        datetime_value = self.html_to_text(str(time_tag))
                
                # Extract image URLs from inline styles
                image_urls: List[str] = []
                img_tags = soup.findAll('a', {'class': 'tgme_widget_message_photo_wrap'})
                for tag in img_tags:
                    style = tag.get('style', '')
                    match_obj = re.search(r"background-image:url\('(.*)'\)", style)
                    if match_obj:
                        image_urls.append(match_obj.group(1))
                
                # Extract video URLs from video tags (if present)
                video_urls: List[str] = []
                video_wraps = soup.findAll('div', {'class': 'tgme_widget_message_video_wrap'})
                for video_wrap in video_wraps:
                    video_tag = video_wrap.find('video')
                    if video_tag and video_tag.get('src'):
                        video_urls.append(video_tag.get('src'))
                
                posts.append({
                    "post_url": url,
                    "author": author,
                    "datetime": datetime_value,
                    "content": text_content,
                    "image_urls": image_urls,
                    "video_urls": video_urls,
                })
            except Exception as e:
                posts.append({"post_url": url, "error": str(e)})
        
        return {"posts": posts}

    def html_to_text(self, html: str) -> str:
        h = html2text.HTML2Text()
        h.body_width = 0  # Disable line wrapping
        h.ignore_links = True  # Ignore hyperlinks
        h.ignore_emphasis = True  # Ignore bold and italic formatting
        h.ignore_images = True  # Ignore images
        h.protect_links = True  # Protect hyperlinks from being stripped out
        h.unicode_snob = True  # Use Unicode characters instead of ASCII
        h.wrap_links = False  # Disable link wrapping
        h.wrap_lists = False  # Disable list wrapping
        h.decode_errors = 'ignore'  # Ignore Unicode decoding errors

        text = h.handle(html)
        text = re.sub(r'\*+', '', text)  # Remove asterisks
        text = re.sub(r'^[ \t]*[\\`]', '', text, flags=re.MULTILINE)  # Remove leading \ or `
        return text
