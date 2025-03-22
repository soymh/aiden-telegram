import os
import urllib.request
import feedparser
from typing import Dict
from .plugin import Plugin
import logging

class ArXivSearchPlugin(Plugin):
    """
    A plugin to search arXiv for a specific paper title and return URLs of matching papers.
    """
    def get_source_name(self) -> str:
        return "arXiv Search"

    def get_spec(self) -> [Dict]:
        return [{
            "name": "search_arxiv",
            "description": "Search arXiv for papers matching a specific title and return URLs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The title of the paper to search for."
                    },
                    "results_num": {
                        "type": "integer",
                        "description": "The number of the results to return;default is 3."
                    }
                },
                "required": ["query","results_num"],
            },
        }]

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        try:
            # Construct the search query URL
            base_url = 'http://export.arxiv.org/api/query?'
            search_query = urllib.parse.quote(f"ti:{kwargs['query']}")
            query = f'search_query={search_query}&start=0&max_results=10'
            results_num = kwargs['results_num']
            url = base_url + query

            # Send a GET request to the API
            response = urllib.request.urlopen(url)

            # Parse the response using feedparser
            feed = feedparser.parse(response.read())

            # Extract and return the URLs of matching papers
            paper_urls = []
            for entry in feed.entries:
                if results_num>0:
                    paper_id = entry.id.split('/abs/')[-1]
                    paper_url = f"https://arxiv.org/pdf/{paper_id}"
                    paper_urls.append(paper_url)
                    results_num-=1
                else:
                    break

            if paper_urls:
                return {
                    'direct_result': {
                        'kind': 'file',
                        'format': 'url',
                        'value': paper_urls,
                    }
                }
            else:
                return {'result': 'No matching papers found'}
        except Exception as e:
            return {'result': f'Failed to search arXiv: {e}'}
