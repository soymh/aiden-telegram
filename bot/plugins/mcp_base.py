from typing import Dict, List, Any, Optional, Type, ClassVar
import json
import logging
from pydantic import BaseModel, Field

from .plugin import Plugin
from .mcp_client import MCPClient, MCPClientError

log = logging.getLogger(__name__)

class MCPPluginError(Exception):
    """Base exception for MCP plugin errors"""
    pass

class MCPPluginConfig(BaseModel):
    """Configuration for an MCP plugin"""
    url: str
    api_key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MCPPlugin(Plugin):
    """
    Base class for MCP plugins.
    Provides functionality for resolving OpenAPI schemas and executing MCP tools.
    """
    
    # Class variables to store plugin metadata
    plugin_config: ClassVar[MCPPluginConfig]
    tool_info: ClassVar[Dict[str, Any]]
    
    def __init__(self):
        super().__init__()
        self._client: Optional[MCPClient] = None
    
    @property
    def client(self) -> MCPClient:
        """Get or create MCP client"""
        if self._client is None:
            self._client = MCPClient(
                base_url=self.plugin_config.url,
                api_key=self.plugin_config.api_key
            )
        return self._client
    
    @classmethod
    async def create_from_schema(cls, tool_info: Dict[str, Any], api_key: Optional[str] = None) -> 'MCPPlugin':
        """
        Create a new MCPPlugin instance from an OpenAPI tool schema
        
        Args:
            tool_info: Tool information including OpenAPI spec and metadata
            api_key: Optional API key for authentication
            
        Returns:
            Initialized MCPPlugin instance
        """
        instance = cls()
        
        # Create plugin config from tool info
        instance.plugin_config = MCPPluginConfig(
            url=tool_info['server_info']['url'],
            api_key=api_key,
            name=tool_info['info'].get('title'),
            description=tool_info['info'].get('description'),
            metadata={
                'version': tool_info['info'].get('version'),
                'servers': tool_info.get('servers', []),
                **tool_info['server_info'].get('metadata', {})
            }
        )
        
        # Store complete OpenAPI spec
        instance.openapi_spec = tool_info['openapi_spec']
        
        return instance
    
    @staticmethod
    def _resolve_schema_refs(schema: Dict[str, Any], components: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve OpenAPI schema references recursively using open-webui's approach
        
        Args:
            schema: Schema containing $refs
            components: OpenAPI components containing referenced schemas
            
        Returns:
            Schema with all references resolved
        """
        schema = schema.copy()
        if "$ref" in schema:
            ref = schema["$ref"].split("/")[-1]
            resolved = MCPPlugin._resolve_schema_refs(
                components.get("schemas", {}).get(ref, {}),
                components
            )
            return resolved
        
        # Handle array types
        if schema.get("type") == "array" and "items" in schema:
            schema["items"] = MCPPlugin._resolve_schema_refs(schema["items"], components)
            
        # Handle object types
        if schema.get("type") == "object" and "properties" in schema:
            resolved_props = {}
            for prop_name, prop_schema in schema["properties"].items():
                resolved_props[prop_name] = MCPPlugin._resolve_schema_refs(prop_schema, components)
            schema["properties"] = resolved_props
            
            # Handle additional properties
            if "additionalProperties" in schema:
                if isinstance(schema["additionalProperties"], dict):
                    schema["additionalProperties"] = MCPPlugin._resolve_schema_refs(
                        schema["additionalProperties"],
                        components
                    )
                    
        # Handle allOf, oneOf, anyOf
        for key in ["allOf", "oneOf", "anyOf"]:
            if key in schema:
                schema[key] = [
                    MCPPlugin._resolve_schema_refs(sub_schema, components)
                    for sub_schema in schema[key]
                ]
                
        return schema
    
    def _convert_openapi_to_plugin_spec(self, openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert an OpenAPI spec to plugin function specs using open-webui's approach
        
        Args:
            openapi_spec: Full OpenAPI specification
            
        Returns:
            List of function specifications in plugin format
        """
        try:
            specs = []
            paths = openapi_spec.get("paths", {})
            components = openapi_spec.get("components", {})
            
            # Process each path and method
            for path, methods in paths.items():
                for method, operation in methods.items():
                    if not operation.get("operationId"):
                        continue
                        
                    # Create base function spec
                    function_spec = { # Renamed 'spec' to 'function_spec' for clarity
                        "name": operation["operationId"],
                        "description": operation.get("description", 
                                     operation.get("summary", "No description available.")),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                    
                    # Handle path and query parameters
                    for param in operation.get("parameters", []):
                        param_name = param["name"]
                        param_schema = param.get("schema", {})
                        description = param_schema.get("description", "") or param.get("description", "")
                        
                        # Include enum values in description
                        if param_schema.get("enum"):
                            description += f". Possible values: {', '.join(map(str, param_schema['enum']))}"
                            
                        # Resolve parameter schema
                        resolved_schema = self._resolve_schema_refs(param_schema, components)
                        
                        function_spec["parameters"]["properties"][param_name] = {
                            "type": resolved_schema.get("type", "string"),
                            "description": description,
                            **{k:v for k,v in resolved_schema.items() 
                               if k not in ["type", "description"]}
                        }
                        
                        if param.get("required", False):
                            function_spec["parameters"]["required"].append(param_name)
                            
                    # Handle request body
                    request_body = operation.get("requestBody")
                    if request_body:
                        content = request_body.get("content", {})
                        json_schema = content.get("application/json", {}).get("schema")
                        if json_schema:
                            resolved_schema = self._resolve_schema_refs(json_schema, components)
                            
                            # Merge resolved body schema
                            if resolved_schema.get("properties"):
                                function_spec["parameters"]["properties"].update(
                                    resolved_schema["properties"]
                                )
                                if "required" in resolved_schema:
                                    function_spec["parameters"]["required"].extend(
                                        resolved_schema["required"]
                                    )
                                    
                    # Add server metadata 
                    # if hasattr(self, 'plugin_config'):
                    #     function_spec["server"] = {
                    #         'url': str(self.plugin_config.url),
                    #         'name': self.plugin_config.name or "Unknown MCP Server",
                    #         'description': self.plugin_config.description,
                    #         'metadata': self.plugin_config.metadata
                    #     }
                        
                    # Wrap the function_spec in the desired format
                    specs.append({"type": "function", "function": function_spec})
            return specs
            
        except Exception as e:
            log.error(f"Error converting OpenAPI spec to plugin format: {e}")
            raise MCPPluginError(f"Invalid OpenAPI spec format: {e}")
    
    def get_spec(self) -> List[Dict[str, Any]]:
        """
        Get function specifications for this plugin by converting the OpenAPI spec
        
        Returns:
            List of OpenAI function specifications
        """
        return self._convert_openapi_to_plugin_spec(self.openapi_spec)
    
    async def execute(self, function_name: str, helper: Any, **kwargs) -> Dict[str, Any]:
        """
        Execute an MCP tool function
        
        Args:
            function_name: Name of the function to execute
            helper: Telegram bot helper instance (unused)
            **kwargs: Function parameters
            
        Returns:
            Function execution result
            
        Raises:
            MCPPluginError: If execution fails
        """
        try:
            result = await self.client.execute_tool(function_name, **kwargs)
            return {'result': result}
        except MCPClientError as e:
            log.error(f"MCP tool execution failed: {e}")
            return {'error': str(e)}
        except Exception as e:
            log.error(f"Unexpected error executing MCP tool: {e}")
            return {'error': f"Internal error: {str(e)}"}
