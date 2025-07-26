from typing import Dict, List, Any, Optional, Type, Callable, Awaitable, Union
import logging
from pydantic import BaseModel, HttpUrl, Field
from .mcp_base import MCPPlugin, MCPPluginError
from .mcp_client import MCPClient, MCPClientError

log = logging.getLogger(__name__)

class MCPServerConfig(BaseModel):
    """Configuration for an MCPO server"""
    url: HttpUrl
    api_key: Optional[str] = None
    enabled: bool = True
    name: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DynamicMCPPlugin(MCPPlugin):
    """
    A dynamic MCP plugin that can be created from any MCP tool schema.
    Includes metadata about its source server and capabilities.
    """
    def __init__(self):
        super().__init__()
        self.server_info = {}
        
    def get_source_name(self) -> str:
        """
        Get the source name of this plugin
        
        Returns:
            The name of the tool from its OpenAPI info, or server name if not available
        """
        if hasattr(self, 'openapi_spec'):
            title = self.openapi_spec.get('info', {}).get('title')
            if title:
                return title
                
        if hasattr(self, 'plugin_config'):
            return self.plugin_config.name or "Unknown MCP Plugin"
            
        return "Unknown MCP Plugin"
        
    # def get_spec(self) -> List[Dict[str, Any]]:
    #     """
    #     Get the OpenAPI function specifications in OpenAI format.
        
    #     Returns:
    #         List of function specifications
    #     """
    #     if not hasattr(self, 'openapi_spec'):
    #         return []
            
    #     paths = self.openapi_spec.get('paths', {})
    #     components = self.openapi_spec.get('components', {})
    #     schemas = self.openapi_spec.get('schemas', {})
    #     functions = []
        
    #     for path, methods in paths.items():
    #         for method, operation in methods.items():
    #             if method.lower() != 'post':  # Only handle POST operations
    #                 continue
                    
    #             # Skip if no operationId
    #             if 'operationId' not in operation:
    #                 continue
                    
    #             # Get basic function info with OpenAI format
    #             function = {
    #                 'type': 'function',
    #                 'function': {
    #                     'name': operation['operationId'],
    #                     'description': operation.get('description', operation.get('summary', '')),
    #                     'parameters': {
    #                         'type': 'object',
    #                         'properties': {},
    #                         'required': []
    #                     }
    #                 }
    #             }
                
    #             # Add source info
    #             # if hasattr(self, 'plugin_config'):
    #             #     function['function']['source'] = {
    #             #         'server_url': str(self.plugin_config.url),
    #             #         'server_name': self.plugin_config.name or 'Unknown MCP Server',
    #             #     }
                
    #             # Add parameters from path and query params
    #             for param in operation.get('parameters', []):
    #                 param_name = param['name']
    #                 param_schema = param.get('schema', {})
    #                 param_desc = param.get('description', '') or param_schema.get('description', '')
                    
    #                 # Include enum values in description if present
    #                 if param_schema.get('enum'):
    #                     param_desc += f". Possible values: {', '.join(map(str, param_schema.get('enum')))}"
                    
    #                 # Add to properties
    #                 function['function']['parameters']['properties'][param_name] = {
    #                     'type': param_schema.get('type', 'string'),
    #                     'title': param.get('name'),
    #                     'description': param_desc
    #                 }
                    
    #                 # Add to required if marked as such
    #                 if param.get('required', False):
    #                     function['function']['parameters']['required'].append(param_name)
                
    #             # Add request body parameters
    #             if 'requestBody' in operation:
    #                 content = operation['requestBody'].get('content', {})
    #                 schema = content.get('application/json', {}).get('schema', {})
                    
    #                 # Resolve schema refs and merge into parameters
    #                 if 'properties' in schema:
    #                     function['function']['parameters']['properties'].update(schema['properties'])
    #                 if 'required' in schema:
    #                     function['function']['parameters']['required'].extend(schema['required'])
                
    #             functions.append(function)
                
    #     return functions
        
    async def execute(self, function_name: str, helper, **kwargs) -> Dict:
        """
        Execute a function on the MCP tool
        
        Args:
            function_name: Name of function to execute
            helper: Plugin helper (unused)
            **kwargs: Function parameters
            
        Returns:
            Function result
        """
        try:
            if not hasattr(self, 'server_info'):
                return {'error': 'No server info available'}
            
            # Get the tool name from OpenAPI spec
            tool_name = self.openapi_spec.get('servers', {})[0].get('url', '').lower()
            if not tool_name:
                tool_name = 'time'  # Default to 'time' if no title found
                
            # Strip 'mcp-' prefix if present
            # tool_name = tool_name.replace('mcp-', '').replace('-server', '')
            
            # Base path is the tool name
            # base_path = f'/{tool_name}'
            base_path = tool_name
            
            # Find the endpoint path for this function from the OpenAPI spec
            paths = self.openapi_spec.get('paths', {})
            endpoint_path = None
            for path, methods in paths.items():
                for method, op in methods.items():
                    if method.lower() == 'post' and op.get('operationId') == function_name:
                        endpoint_path = path
                        break
                if endpoint_path:
                    break
            
            # Verify we found the endpoint
            if not endpoint_path:
                return {'error': f'Endpoint {endpoint_path} not found in OpenAPI spec'}
                    
            # Combine base path and endpoint path
            full_path = f"{base_path}{endpoint_path}"
            
            # Execute the tool with the correct path
            result = await self.client.execute_tool(function_name, full_path, **kwargs)
            return {'result': result}
        except Exception as e:
            return {'error': str(e)}

class MCPPluginLoader:
    """
    A utility class to dynamically discover and load MCP plugins from MCPO servers
    """
    
    @staticmethod
    def validate_server_config(config: Dict[str, Any]) -> MCPServerConfig:
        """
        Validate and normalize MCPO server configuration
        
        Args:
            config: Raw server configuration dictionary
            
        Returns:
            Validated MCPServerConfig object
        
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            return MCPServerConfig(**config)
        except Exception as e:
            raise ValueError(f"Invalid MCPO server configuration: {str(e)}")
    
    @staticmethod
    async def test_server_connection(url: str, api_key: Optional[str] = None) -> bool:
        """
        Test connection to an MCPO server
        
        Args:
            url: Server URL
            api_key: Optional API key
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            client = MCPClient(url, api_key)
            await client._get_root_schema()
            return True
        except:
            return False
    
    @classmethod
    async def discover_and_load_plugins(cls, mcpo_servers: List[Dict[str, Any]]) -> Dict[str, Callable[[], Awaitable[MCPPlugin]]]:
        """
        Discover and load plugins from multiple MCPO servers
        
        Args:
            mcpo_servers: List of MCPO server configurations
                
        Returns:
            Dictionary mapping plugin names to async factory functions
        
        Example config:
        ```python
        mcpo_servers = [
            {
                "url": "http://localhost:8000",
                "api_key": "secret-key",
                "enabled": True,
                "name": "Local MCP Server",
                "description": "Development MCP server",
                "metadata": {
                    "version": "1.0.0",
                    "environment": "development"
                }
            }
        ]
        ```
        """
        plugin_mapping = {}
        
        for server_config in mcpo_servers:
            # Validate server configuration
            try:
                config = cls.validate_server_config(server_config)
                if not config.enabled:
                    log.info(f"Skipping disabled MCPO server: {config.url}")
                    continue
                    
                # Test connection
                if not await cls.test_server_connection(str(config.url), config.api_key):
                    log.error(f"Failed to connect to MCPO server: {config.url}")
                    continue
                
                # Discover tools
                tools = await MCPClient.discover_tools(
                    base_url=str(config.url),
                    api_key=config.api_key
                )
                
                for tool in tools:
                    try:
                        # Create plugin name from tool info
                        base_name = tool['info'].get('title', tool['name']).lower()
                        plugin_name = f"mcp_{base_name}"
                        
                        # Handle name conflicts
                        if plugin_name in plugin_mapping:
                            i = 1
                            while f"{plugin_name}_{i}" in plugin_mapping:
                                i += 1
                            plugin_name = f"{plugin_name}_{i}"
                        
                        # Add server metadata to tool info
                        tool['server_info'] = {
                            'url': str(config.url),
                            'name': config.name,
                            'description': config.description,
                            'metadata': config.metadata
                        }
                        
                        # Create plugin factory
                        async def make_plugin(tool_info: Dict[str, Any], api_key: Optional[str]) -> MCPPlugin:
                            try:
                                plugin = await DynamicMCPPlugin.create_from_schema(
                                    tool_info=tool_info,
                                    api_key=api_key
                                )
                                plugin.server_info = tool_info['server_info']
                                return plugin
                            except Exception as e:
                                log.error(f"Error creating plugin instance: {str(e)}")
                                raise MCPPluginError(f"Failed to create plugin: {str(e)}")
                        
                        # Create a factory function closure
                        def make_factory(t: Dict[str, Any], k: Optional[str]) -> Callable[[], Awaitable[MCPPlugin]]:
                            return lambda: make_plugin(t, k)
                        
                        plugin_mapping[plugin_name] = make_factory(tool, config.api_key)
                        
                        log.info(
                            f"Discovered MCP plugin: {plugin_name} "
                            f"({tool['info'].get('title', '')}) "
                            f"from {config.url}"
                        )
                        
                    except Exception as e:
                        log.error(f"Error loading MCP tool {tool.get('name', 'unknown')}: {str(e)}")
                        continue
                    
            except ValueError as e:
                log.error(f"Invalid MCPO server configuration: {str(e)}")
                continue
            except MCPClientError as e:
                log.error(f"Error communicating with MCPO server {server_config.get('url', 'unknown')}: {str(e)}")
                continue
            except Exception as e:
                log.error(f"Unexpected error loading plugins from MCPO server: {str(e)}")
                continue
                
        return plugin_mapping
