import os
from typing import Dict
import requests

from .plugin import Plugin


class ArxivContentScraperPlugin(Plugin):
    """
    A plugin to scrape web content from a given URL or Arxiv paper and return it in Markdown format using Jina AI Reader API.
    """
    def __init__(self):
        pass

    def get_source_name(self) -> str:
        return "Web Content Scraper"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "jina_scrape_to_markdown",
            "description": "Scrape web content from a URL, especially useful for arXiv papers, and return it in Markdown format using Jina AI Reader API",
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
            # Use Jina AI Reader API to convert URL to Markdown
            jina_url = f"https://r.jina.ai/{url}"
            response = requests.get(jina_url)
            
            if response.status_code == 200:
                markdown_content = response.text
                return {"result": markdown_content}
            else:
                return {"error": f"Failed to retrieve Markdown content. Status code: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
