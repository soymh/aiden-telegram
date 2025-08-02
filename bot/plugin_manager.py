import json
import logging
import asyncio
from typing import Dict, Any

from plugins.gtts_text_to_speech import GTTSTextToSpeech
from plugins.auto_tts import AutoTextToSpeech
from plugins.kokoro_tts import KokoroTTSPlugin
from plugins.dice import DicePlugin
from plugins.ddg_image_search import DDGImageSearchPlugin
from plugins.weather import WeatherPlugin
from plugins.ddg_web_search import DDGWebSearchPlugin
from plugins.wolfram_alpha import WolframAlphaPlugin
from plugins.deepl import DeeplTranslatePlugin
from plugins.worldtimeapi import WorldTimeApiPlugin
from plugins.whois_ import WhoisPlugin
from plugins.webshot import WebshotPlugin
from plugins.iplocation import IpLocationPlugin
from plugins.telegram_moderator import TelegramModerator
from plugins.web_extract import WebContentScraperPlugin
from plugins.arxiv_search import ArXivSearchPlugin
from plugins.telegram_extract import TelegramScraperPlugin
from plugins.arxiv_extract import ArxivContentScraperPlugin
from plugins.image_gen import ImageGeneratorPlugin
from plugins.reddit_helper import RedditHelper
from plugins.youtube_downloader import YouTubeDownloaderPlugin
from plugins.media_relay import MediaRelayPlugin
from plugins.message_plugin import MessagePlugin
from plugins.vision_plugin import VisionPlugin
from plugins.mcp_loader import MCPPluginLoader
from plugins.pdf_processor import NotedMDPlugin

from os import getenv
log = logging.getLogger(__name__)


class PluginManager:
    """
    A class to manage plugins and call the correct functions.
    Supports both built-in plugins and dynamically loaded MCP plugins.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize basic plugin manager instance.
        The real async initialization is done in `create`.
        """
        self.plugins = []
        self.config = config

    @classmethod
    async def create(cls, config: Dict[str, Any]) -> 'PluginManager':
        """
        Async factory method to create and initialize a PluginManager instance.

        Args:
            config: Configuration dictionary containing:
                - plugins: List of enabled built-in plugins
                - mcpo_servers: List of MCPO server configs for dynamic plugins

        Returns:
            PluginManager instance with all plugins loaded and initialized.
        """
        instance = cls(config)

        # Built-in plugin mapping
        plugin_mapping = {
            'wolfram': WolframAlphaPlugin,
            'weather': WeatherPlugin,
            'ddg_web_search': DDGWebSearchPlugin,
            'ddg_image_search': DDGImageSearchPlugin,
            'worldtimeapi': WorldTimeApiPlugin,
            'dice': DicePlugin,
            'deepl_translate': DeeplTranslatePlugin,
            'gtts_text_to_speech': GTTSTextToSpeech,
            'auto_tts': AutoTextToSpeech,
            'kokoro_tts': KokoroTTSPlugin,
            'whois': WhoisPlugin,
            'webshot': WebshotPlugin,
            'iplocation': IpLocationPlugin,
            'telegram_moderator': TelegramModerator,
            'web_extract': WebContentScraperPlugin,
            'arxiv_search': ArXivSearchPlugin,
            'telegram_extract': TelegramScraperPlugin,
            'arxiv_extract': ArxivContentScraperPlugin,
            'image_gen': ImageGeneratorPlugin,
            'youtube_downloader': YouTubeDownloaderPlugin,
            'reddit_helper': RedditHelper,
            'media_relay': MediaRelayPlugin,
            'message_sender': MessagePlugin,
            'vision': VisionPlugin,
            'pdf_extract': NotedMDPlugin,
        }

        # Initialize built-in plugins
        enabled_plugins = config.get('plugins', [])
        for plugin_key in enabled_plugins:
            if plugin_key in plugin_mapping:
                try:
                    plugin_instance = plugin_mapping[plugin_key]()
                    # Await plugin_instance if it's a coroutine object (rare)
                    if asyncio.iscoroutine(plugin_instance):
                        plugin_instance = await plugin_instance
                    instance.plugins.append(plugin_instance)
                    log.info(f"Initialized built-in plugin: {plugin_key}")
                except Exception as e:
                    log.error(f"Failed to initialize built-in plugin {plugin_key}: {e}")
            else:
                log.warning(f"Enabled plugin '{plugin_key}' is not in known plugin mapping")

        # Load MCP plugins if configured
        mcpo_servers = [
            {
                "url": getenv("MCPO_BASE_URL", "http://localhost:8000"),
                "api_key": getenv('MCPO_API_KEY', "secret-key"),
                "enabled": True,
                "name": "Local MCP Server",
                "description": "Development MCP server",
                "metadata": {
                    "version": "1.0.0",
                    "environment": "development"
                }
            }
        ]

        if mcpo_servers:
            try:
                # Discover MCP plugin factory coroutines: {name: factory_coroutine}
                mcp_plugin_factories = await MCPPluginLoader.discover_and_load_plugins(mcpo_servers)

                # Initialize MCP plugin instances concurrently
                mcp_plugins = await asyncio.gather(
                    *(factory() for factory in mcp_plugin_factories.values()),
                    return_exceptions=True
                )

                # Attach successfully created MCP plugins
                for plugin, factory_name in zip(mcp_plugins, mcp_plugin_factories.keys()):
                    if isinstance(plugin, Exception):
                        log.error(f"Failed to initialize MCP plugin '{factory_name}': {plugin}")
                    else:
                        instance.plugins.append(plugin)
                        log.info(f"Initialized MCP plugin: {factory_name}")

            except Exception as e:
                log.error(f"Error loading MCP plugins: {e}")

        return instance

    def __resolve_schema(self, schema, components):
        """
        Recursively resolves a JSON schema using OpenAPI components.
        
        Args:
            schema: The schema to resolve
            components: The OpenAPI components containing schema definitions
            
        Returns:
            Resolved schema with all references replaced with actual definitions
        """
        schema = schema.copy()
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            resolved = self.__resolve_schema(
                components.get("schemas", {}).get(ref, {}),
                components
            )
            return resolved
        
        # Handle arrays
        if schema.get("type") == "array" and "items" in schema:
            schema["items"] = self.__resolve_schema(schema["items"], components)
            
        # Handle objects
        if schema.get("type") == "object" and "properties" in schema:
            resolved_props = {}
            for prop_name, prop_schema in schema["properties"].items():
                resolved_props[prop_name] = self.__resolve_schema(prop_schema, components)
            schema["properties"] = resolved_props
            
        return schema

    def __convert_openapi_to_function(self, operation, openapi_spec):
        """
        Convert an OpenAPI operation to an OpenAI function specification.
        
        Args:
            operation: The OpenAPI operation object
            openapi_spec: The full OpenAPI specification
            
        Returns:
            OpenAI function specification
        """
        function = {
            "type": "function",
            "function": {
                "name": operation.get("operationId"),
                "description": operation.get("description", 
                             operation.get("summary", "No description available.")),
                "parameters": {"type": "object", "properties": {}, "required": []}
            }
        }

        # Handle path and query parameters
        for param in operation.get("parameters", []):
            param_name = param["name"]
            param_schema = param.get("schema", {})
            description = param_schema.get("description", "") or param.get("description", "")
            
            # Include enum values in description if present
            if param_schema.get("enum"):
                description += f". Possible values: {', '.join(map(str, param_schema.get('enum')))}"
            
            function["function"]["parameters"]["properties"][param_name] = {
                "type": param_schema.get("type", "string"),
                "description": description
            }
            
            if param.get("required", False):
                function["function"]["parameters"]["required"].append(param_name)

        # Handle request body
        request_body = operation.get("requestBody")
        if request_body:
            content = request_body.get("content", {})
            json_schema = content.get("application/json", {}).get("schema")
            if json_schema:
                resolved_schema = self.__resolve_schema(
                    json_schema,
                    openapi_spec.get("components", {})
                )
                
                if resolved_schema.get("properties"):
                    function["function"]["parameters"]["properties"].update(
                        resolved_schema["properties"]
                    )
                    if "required" in resolved_schema:
                        function["function"]["parameters"]["required"].extend(
                            resolved_schema["required"]
                        )

        return function

    def get_functions_specs(self, exception=None):
        """
        Return the list of function specs that can be called by the model.
        Handles both built-in and MCP plugins.

        Returns:
            List of function specifications in OpenAI-compatible format.
        """
        specs = []
        for plugin in self.plugins:
            try:
                plugin_specs = plugin.get_spec()
                if not isinstance(plugin_specs, list):
                    log.warning(f"Plugin {plugin} returned non-list specs: {type(plugin_specs)}")
                    continue
                
                for spec in plugin_specs:
                    log.debug(f"Plugin {plugin} spec missing required fields: {spec}")
                    try:
                        # For MCP plugins, the spec is already in OpenAI format
                        if hasattr(plugin, 'openapi_spec'):
                            specs.append(spec)
                        # For built-in plugins, convert to OpenAI format
                        else:
                            if not all(key in spec for key in ['name', 'description', 'parameters']):
                                log.warning(f"Plugin {plugin} spec missing required fields: {spec}")
                                continue
                            if spec["name"] == exception:
                                continue
                            function = {
                                "type": "function",
                                "function": {
                                    "name": spec["name"],
                                    "description": spec["description"],
                                    "parameters": spec["parameters"]
                                }
                            }
                            specs.append(function)

                    except Exception as e:
                        log.error(f"Error processing spec from plugin {plugin}: {e}", exc_info=True)

            except Exception as e:
                log.error(f"Error getting specs from plugin {plugin}: {e}", exc_info=True)
                continue

        return specs

    async def call_function(self, function_name: str, helper: Any, arguments: str):
        """
        Call a function based on the name and parameters provided.

        Args:
            function_name: Name of the function to call
            helper: Helper object to pass to plugin execution (context, etc)
            arguments: JSON string of parameters to pass to the function

        Returns:
            JSON string of the function execution result or error.
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            error_result = {'error': f'Function {function_name} not found'}
            log.warning(error_result['error'])
            return json.dumps(error_result)

        try:
            args_dict = json.loads(arguments)
        except json.JSONDecodeError as e:
            error_result = {'error': f'Invalid JSON arguments for {function_name}: {e}'}
            log.error(error_result['error'])
            return json.dumps(error_result)

        try:
            # Use function name directly - it's already the correct operationId
            exec_name = function_name
                
            result = await plugin.execute(exec_name, helper, **args_dict)
            
            # For MCP plugins, ensure result is properly formatted
            if hasattr(plugin, 'openapi_spec') and isinstance(result, dict) and 'error' not in result:
                # If result is not wrapped in a result/error key, wrap it
                if not any(key in result for key in ['result', 'error']):
                    result = {'result': result}
                    
            return json.dumps(result, default=str)
        except Exception as e:
            log.error(f"Error calling function '{function_name}' on plugin '{plugin}': {e}")
            return json.dumps({'error': str(e)})

    def get_plugin_source_name(self, function_name: str) -> str:
        """
        Return the source name of the plugin exposing the function.

        Args:
            function_name: Name of the function

        Returns:
            Source name string or empty string if not found.
        """
        plugin = self.__get_plugin_by_function_name(function_name)
        if not plugin:
            return ''
        try:
            return plugin.get_source_name()
        except Exception as e:
            log.error(f"Error getting source name from plugin {plugin}: {e}")
            return ''

    def __get_plugin_by_function_name(self, function_name: str):
        """
        Helper to find a plugin by the function it supports.
        Handles both built-in plugins (flat spec) and MCP plugins (nested spec).
        """
        for plugin in self.plugins:
            try:
                specs = plugin.get_spec()
                
                # For MCP plugins (nested format)
                if hasattr(plugin, 'openapi_spec'):
                    if any(spec.get('function', {}).get('name') == function_name for spec in specs):
                        return plugin
                # For built-in plugins (flat format)
                else:
                    if any(spec.get('name') == function_name for spec in specs):
                        return plugin
                        
            except Exception as e:
                log.error(f"Error searching function {function_name} in plugin {plugin}: {e}")
        return None
