import os
from typing import Dict
import requests
from bs4 import BeautifulSoup
import markdownify

from .plugin import Plugin


class WebContentScraperPlugin(Plugin):
    """
    A plugin to scrape web content from a given URL and return it in Markdown format
    """
    def __init__(self):
        pass

    def get_source_name(self) -> str:
        return "Web Content Scraper"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "scrape_to_markdown",
            "description": "Scrape web content from a URL and return it in Markdown format",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "the URL to scrape"
                    }
                },
                "required": ["url"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        url = kwargs['url']
        
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unnecessary elements
            for script in soup(["script", "style"]):
                script.decompose()
                
            # Convert to Markdown
            markdown_content = markdownify.markdownify(str(soup))
            
            return {"result": markdown_content}
        except Exception as e:
            return {"error": str(e)}
