import json
import logging
from typing import Dict, List, Any, Optional
import aiohttp
import yaml
from aiohttp.client_exceptions import ClientResponseError
from pydantic import BaseModel, Field, AnyUrl

log = logging.getLogger(__name__)

class MCPClientError(Exception):
    """Base exception for MCP client errors"""
    pass

class MCPConnectionError(MCPClientError):
    """Exception raised when connection to MCPO server fails"""
    pass

class MCPSchemaError(MCPClientError):
    """Exception raised when OpenAPI schema is invalid or can't be parsed"""
    pass

class MCPExecutionError(MCPClientError):
    """Exception raised when tool execution fails"""
    pass

class MCPConfig(BaseModel):
    """Configuration for an MCP client"""
    base_url: AnyUrl
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    schema_cache_ttl: int = 3600  # 1 hour
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MCPClient:
    """
    A client for interacting with MCP-to-OpenAPI proxy (MCPO) servers.
    Handles schema caching, request retrying, and error mapping.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the MCP client.
        
        Args:
            base_url: Base URL of the MCPO server
            api_key: Optional API key for authentication
        """
        self.config = MCPConfig(
            base_url=base_url,
            api_key=api_key
        )
        self._schema_cache = {}
        self._session = None
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure aiohttp session exists"""
        if self._session is None or self._session.closed:
            headers = {}
            if self.config.api_key:
                headers['Authorization'] = f'Bearer {self.config.api_key}'
            self._session = aiohttp.ClientSession(
                base_url=str(self.config.base_url),
                headers=headers,
                raise_for_status=True
            )
        return self._session
    
    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _get_root_schema(self) -> Dict[str, Any]:
        """
        Get the root OpenAPI schema from the server.
        Caches schema to avoid repeated requests.
        
        Returns:
            OpenAPI schema as dict
        
        Raises:
            MCPConnectionError: If connection fails
            MCPSchemaError: If schema is invalid
        """
        try:
            session = await self._ensure_session()
            async with session.get('/openapi.json') as resp:
                try:
                    schema = await resp.json()
                except ValueError:
                    # Try YAML if JSON fails
                    text = await resp.text()
                    try:
                        schema = yaml.safe_load(text)
                    except yaml.YAMLError as e:
                        raise MCPSchemaError(f"Failed to parse OpenAPI schema: {e}")
                
                if not isinstance(schema, dict):
                    raise MCPSchemaError("Invalid OpenAPI schema format")
                
                self._schema_cache['root'] = schema
                return schema
                
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Failed to connect to MCPO server: {e}")
        except MCPClientError:
            raise
        except Exception as e:
            raise MCPClientError(f"Unexpected error fetching schema: {e}")
    
    @classmethod
    async def discover_tools(cls, base_url: str, api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discover available tools from an MCPO server by:
        1. Fetching root openapi.json to find available tools
        2. Fetching individual tool specs from /[tool-name]/openapi.json
        
        Args:
            base_url: MCPO server URL
            api_key: Optional API key
            
        Returns:
            List of tool specifications including OpenAPI schemas
        """
        client = cls(base_url, api_key)
        try:
            # Get root schema to discover available tools
            root_schema = await client._get_root_schema()
            
            # Parse description to find available tools
            description = root_schema.get("info", {}).get("description", "")
            available_tools = []
            
            # Extract tool names from description
            # Format is typically: "- [tool_name](/tool_name/docs)"
            for line in description.split("\n"):
                if line.strip().startswith("- [") and ("](/") in line:
                    tool_name = line.split("[")[1].split("]")[0]
                    available_tools.append(tool_name)
            
            log.info(f"Discovered tools from {base_url}: {available_tools}")
            
            # Fetch OpenAPI spec for each tool
            tools = []
            for tool_name in available_tools:
                try:
                    tool_url = f"{base_url.rstrip('/')}/{tool_name}/openapi.json"
                    async with aiohttp.ClientSession() as session:
                        headers = {}
                        if api_key:
                            headers['Authorization'] = f'Bearer {api_key}'
                            
                        async with session.get(tool_url, headers=headers) as resp:
                            if resp.status != 200:
                                log.error(f"Failed to fetch spec for {tool_name}: {resp.status} -> {tool_url} {available_tools}")
                                continue
                                
                            try:
                                tool_spec = await resp.json()
                            except ValueError:
                                text = await resp.text()
                                try:
                                    tool_spec = yaml.safe_load(text)
                                except yaml.YAMLError as e:
                                    log.error(f"Failed to parse spec for {tool_name}: {e}")
                                    continue
                            
                            if not isinstance(tool_spec, dict):
                                log.error(f"Invalid spec format for {tool_name}")
                                continue
                                
                            tool = {
                                "name": tool_name,
                                "openapi_spec": tool_spec,
                                "info": tool_spec.get("info", {}),
                                "servers": tool_spec.get("servers", [])
                            }
                            tools.append(tool)
                            
                except Exception as e:
                    log.error(f"Error fetching spec for {tool_name}: {e}")
                    continue
                    
            return tools
            
        finally:
            await client.close()
    
    async def execute_tool(self, tool_name: str, tool_base_path: str, **params) -> Any:
        """
        Execute a tool on the MCPO server
        
        Args:
            tool_name: Name of the operation to execute (e.g., 'open_nodes')
            tool_base_path: Base path for the tool (e.g., '/memory')
            **params: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            MCPExecutionError: If tool execution fails
        """
        try:
            # Extract the base tool path (e.g., /time from /time/get_current_time)
            tool_base = tool_base_path.split('/')[1] if tool_base_path.startswith('/') else tool_base_path.split('/')[0]
            
            # Get tool's OpenAPI spec from the base path
            spec_url = f"{str(self.config.base_url).rstrip()}{tool_base}/openapi.json"
            
            async with aiohttp.ClientSession() as session:
                headers = {}
                if self.config.api_key:
                    headers['Authorization'] = f'Bearer {self.config.api_key}'
                    
                async with session.get(spec_url, headers=headers) as resp:
                    if resp.status != 200:
                        raise MCPExecutionError(f"Failed to fetch spec from {spec_url}: {resp.status}")
                        
                    try:
                        tool_spec = await resp.json()
                    except ValueError:
                        text = await resp.text()
                        try:
                            tool_spec = yaml.safe_load(text)
                        except yaml.YAMLError as e:
                            raise MCPSchemaError(f"Failed to parse spec from {spec_url}: {e}")
            
            # Find the operation by its name
            operation = None
            operation_path = None
            operation_method = None
            
            paths = tool_spec.get("paths", {})
            for path, methods in paths.items():
                for method, spec in methods.items():
                    if spec.get("operationId") == tool_name:
                        operation = spec
                        operation_path = path
                        operation_method = method.upper()
                        break
                if operation:
                    break
            
            if not operation:
                raise MCPExecutionError(f"Operation {tool_name} not found in tool spec")
            
            # Get the actual execution URL (without /openapi.json)
            operation_url = str(self.config.base_url).rstrip('/') + tool_base_path
            
            session = await self._ensure_session()
            
            # Set headers for the operation
            headers = {}
            if self.config.api_key:
                headers['Authorization'] = f'Bearer {self.config.api_key}'
            if operation_method.upper() in ['POST', 'PUT', 'PATCH']:
                headers['Content-Type'] = 'application/json'
            
            # Get the correct HTTP method from the operation spec
            method = getattr(session, operation_method.lower())
            
            log.debug(f"Executing {operation_method} {operation_url} with params: {params}")
            
            # Execute with the correct method and parameters
            if operation_method.upper() in ['POST', 'PUT', 'PATCH']:
                async with method(operation_url, json=params, headers=headers) as resp:
                    try:
                        return await resp.json()
                    except ValueError:
                        return await resp.text()
            else:
                # For GET, DELETE, etc., use query parameters
                async with method(operation_url, params=params, headers=headers) as resp:
                    try:
                        return await resp.json()
                    except ValueError:
                        return await resp.text()
                    
        except ClientResponseError as e:
            raise MCPExecutionError(f"Tool execution failed with status {e.status}: {str(e)}")
        except MCPClientError:
            raise
        except Exception as e:
            raise MCPExecutionError(f"Unexpected error executing tool: {e}")
