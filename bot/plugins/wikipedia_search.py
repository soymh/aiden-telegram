from abc import ABC, abstractmethod
from typing import Dict
import wikipedia

class WikipediaSearchPlugin(ABC):
    """
    A plugin for searching in Wikipedia.
    """

    def get_source_name(self) -> str:
        """
        Return the name of the source of the plugin.
        """
        return "Wikipedia"

    def get_spec(self) -> list[Dict]:
        """
        Function specs in the form of JSON schema.
        """
        return [
            {
                "name": "search",
                "parameters": [
                    {"name": "query", "type": "string"}
                ],
                "returns": "object"
            }
        ]

    async def execute(self, function_name: str, helper=None, **kwargs) -> Dict:
        """
        Execute the plugin and return a JSON serializable response.
        """
        if function_name == "search":
            query = kwargs.get("query")
            if query:
                try:
                    # Search for the query on Wikipedia
                    results = wikipedia.search(query)
                    # Fetch the page content for the first result
                    if results:
                        page = wikipedia.page(results[0], auto_suggest=False)
                        return {
                            "title": page.title,
                            "content": page.content,
                            "url": page.url
                        }
                    else:
                        return {"error": "No results found"}
                except wikipedia.exceptions.DisambiguationError as e:
                    return {"error": f"Disambiguation error: {e}"}
                except wikipedia.exceptions.PageError:
                    return {"error": "Page not found"}
            else:
                return {"error": "Query is required"}
        else:
            return {"error": "Unknown function name"}

# Example usage
class WikipediaPlugin(WikipediaSearchPlugin):
    pass

# Create an instance of the plugin
plugin = WikipediaPlugin()

# Example synchronous execution (for testing purposes)
def main():
    result = plugin.execute("search", query="Python programming language")
    print(result)

if __name__ == "__main__":
    main()
