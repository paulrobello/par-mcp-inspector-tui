"""HTTP MCP client implementation using FastMCP's StreamableHttpTransport."""

import logging
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

from ..models import Prompt, Resource, ResourceTemplate, ServerInfo, Tool
from ..models.tool import ToolParameter
from .base import MCPClient, MCPClientError

logger = logging.getLogger(__name__)


class HttpMCPClient(MCPClient):
    """MCP client using Streamable HTTP transport with FastMCP.

    This implementation uses FastMCP's StreamableHttpTransport which provides
    a simple and reliable way to connect to HTTP-based MCP servers.
    """

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize HTTP client.

        Args:
            debug: Enable debug logging
            roots: List of root paths for filesystem servers (not used for HTTP)
        """
        super().__init__(debug=debug, roots=roots)
        self._transport: StreamableHttpTransport | None = None
        self._client: Client | None = None
        self._endpoint_url: str = ""

    async def connect(self, url: str, **kwargs: Any) -> None:
        """Connect to MCP server via HTTP.

        Args:
            url: Server endpoint URL (e.g., "https://example.com/mcp")
            **kwargs: Additional connection parameters
        """
        if self._connected:
            raise MCPClientError("Already connected")

        self._endpoint_url = url

        # Create StreamableHttp transport
        self._transport = StreamableHttpTransport(url=url)

        # Create FastMCP client with transport
        self._client = Client(self._transport)

        self._connected = True

        if self._debug:
            logger.debug(f"Connected to HTTP endpoint: {self._endpoint_url}")

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if not self._connected:
            return

        self._connected = False

        # Close client (this will handle transport cleanup)
        if self._client:
            try:
                await self._client.close()
            except Exception as e:
                if self._debug:
                    logger.debug(f"Error closing client: {e}")
            self._client = None

        # Explicitly close transport if it has close method
        if self._transport:
            try:
                if hasattr(self._transport, "close"):
                    await self._transport.close()
                elif hasattr(self._transport, "_session"):
                    # Close underlying aiohttp session if accessible
                    session = getattr(self._transport, "_session", None)
                    if session and hasattr(session, "close"):
                        await session.close()
            except Exception as e:
                if self._debug:
                    logger.debug(f"Error closing transport: {e}")
            self._transport = None

        if self._debug:
            logger.debug("Disconnected from HTTP endpoint")

    async def _send_data(self, data: str) -> None:
        """Not used in this implementation - using FastMCP client methods instead."""
        raise NotImplementedError("Use FastMCP client methods instead")

    async def _receive_data(self) -> str | None:
        """Not used in this implementation - using FastMCP client methods instead."""
        raise NotImplementedError("Use FastMCP client methods instead")

    async def initialize(self) -> ServerInfo:
        """Initialize connection and get server info."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Use FastMCP's connection context
            async with self._client:
                # Ping server to verify connection
                await self._client.ping()

                # FastMCP doesn't expose separate methods for server info/capabilities
                # The capabilities are available through the transport after connection
                capabilities = {}
                if self._transport and hasattr(self._transport, "server_capabilities"):
                    server_capabilities = getattr(self._transport, "server_capabilities", None)
                    capabilities = server_capabilities or {}

                server_name = "HTTP MCP Server"
                server_version = "unknown"
                protocol_version = "2025-06-18"

                # Try to get server info from transport if available
                if self._transport and hasattr(self._transport, "server_info"):
                    server_info_attr = getattr(self._transport, "server_info", None)
                    server_info_dict = server_info_attr or {}
                    if isinstance(server_info_dict, dict):
                        server_name = server_info_dict.get("name", server_name)
                        server_version = server_info_dict.get("version", server_version)

                # Convert to our ServerInfo model
                server_info_data = {
                    "protocol_version": protocol_version,
                    "capabilities": capabilities,
                    "name": server_name,
                    "version": server_version,
                }

                self._server_info = ServerInfo(**server_info_data)

                if self._debug:
                    logger.debug(f"Initialized server: {self._server_info.name}")

                return self._server_info
        except Exception as e:
            raise MCPClientError(f"Failed to initialize: {e}")

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                tools_data = await self._client.list_tools()
                tools = []

                # FastMCP returns the raw tools list
                if isinstance(tools_data, list):
                    tools_list = tools_data
                else:
                    # Sometimes it might be wrapped in a result dict
                    tools_list = tools_data.get("tools", []) if isinstance(tools_data, dict) else []

                for tool_info in tools_list:
                    # Handle tool data (should be dict from JSON response)
                    if isinstance(tool_info, dict):
                        input_schema_data = tool_info.get("inputSchema", {})

                        if self._debug:
                            logger.debug(f"Raw tool schema: {input_schema_data}")

                        # The server already has properties, don't override them
                        # Just ensure our model can handle the schema
                        if "properties" not in input_schema_data:
                            input_schema_data["properties"] = {}

                        if self._debug:
                            logger.debug(f"Final tool schema: {input_schema_data}")

                        tool_parameter = ToolParameter(**input_schema_data)
                        tool = Tool(
                            name=tool_info["name"],
                            description=tool_info.get("description", ""),
                            inputSchema=tool_parameter,
                        )
                        tools.append(tool)
                    elif hasattr(tool_info, "name"):
                        # It's a Tool object - extract attributes
                        # FastMCP uses camelCase 'inputSchema' not snake_case 'input_schema'
                        input_schema_data = getattr(tool_info, "inputSchema", {})
                        if not input_schema_data or "properties" not in input_schema_data:
                            input_schema_data = (
                                {"properties": {}, **input_schema_data} if input_schema_data else {"properties": {}}
                            )

                        tool_parameter = ToolParameter(**input_schema_data)
                        tool = Tool(
                            name=tool_info.name,
                            description=getattr(tool_info, "description", ""),
                            inputSchema=tool_parameter,
                        )
                        tools.append(tool)

                return tools
        except Exception as e:
            if self._debug:
                logger.debug(f"Error listing tools: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list tools: {e}")

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                resources_data = await self._client.list_resources()
                resources = []
                for resource_info in resources_data:
                    resource = None
                    # FastMCP may return Resource objects or dictionaries
                    if hasattr(resource_info, "uri"):
                        # It's a Resource object - extract attributes
                        # Convert AnyUrl to string if needed
                        uri_value = resource_info.uri
                        if hasattr(uri_value, "__str__"):
                            uri_value = str(uri_value)

                        resource = Resource(
                            uri=str(uri_value),
                            name=getattr(resource_info, "name", ""),
                            description=getattr(resource_info, "description", None),
                            mimeType=getattr(resource_info, "mimeType", None),  # Use camelCase alias
                        )
                    elif isinstance(resource_info, dict):
                        # It's a dictionary - use dict access
                        resource = Resource(
                            uri=resource_info["uri"],
                            name=resource_info.get("name", ""),
                            description=resource_info.get("description"),
                            mimeType=resource_info.get("mimeType"),  # Use camelCase alias
                        )
                    if resource:
                        resources.append(resource)
                return resources
        except Exception as e:
            if self._debug:
                logger.debug(f"Error listing resources: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list resources: {e}")

    async def list_resource_templates(self) -> list[ResourceTemplate]:
        """List available resource templates."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                templates_data = await self._client.list_resource_templates()
                templates = []
                for template_info in templates_data:
                    template = None
                    # FastMCP may return ResourceTemplate objects or dictionaries
                    if hasattr(template_info, "uriTemplate"):
                        # It's a ResourceTemplate object - extract attributes with camelCase
                        template = ResourceTemplate(
                            uriTemplate=getattr(template_info, "uriTemplate", ""),  # Use camelCase alias
                            name=getattr(template_info, "name", ""),
                            description=getattr(template_info, "description", None),
                            mimeType=getattr(template_info, "mimeType", None),  # Use camelCase alias
                        )
                    elif isinstance(template_info, dict):
                        # It's a dictionary - use dict access
                        template = ResourceTemplate(
                            uriTemplate=template_info["uriTemplate"],  # Use camelCase alias
                            name=template_info.get("name", ""),
                            description=template_info.get("description"),
                            mimeType=template_info.get("mimeType"),  # Use camelCase alias
                        )
                    if template:
                        templates.append(template)
                return templates
        except Exception as e:
            if self._debug:
                logger.debug(f"Error listing resource templates: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list resource templates: {e}")

    async def list_prompts(self) -> list[Prompt]:
        """List available prompts."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                prompts_data = await self._client.list_prompts()
                prompts = []
                for prompt_info in prompts_data:
                    prompt = None
                    # FastMCP may return Prompt objects or dictionaries
                    if hasattr(prompt_info, "name"):
                        # It's a Prompt object - extract attributes
                        arguments = []
                        prompt_arguments = getattr(prompt_info, "arguments", [])
                        if prompt_arguments:
                            for arg_info in prompt_arguments:
                                from ..models.prompt import PromptArgument

                                # Handle both object and dict arguments
                                if hasattr(arg_info, "name"):
                                    arg = PromptArgument(
                                        name=arg_info.name,
                                        description=getattr(arg_info, "description", None),
                                        required=getattr(arg_info, "required", False),
                                    )
                                elif isinstance(arg_info, dict):
                                    arg = PromptArgument(
                                        name=arg_info["name"],
                                        description=arg_info.get("description"),
                                        required=arg_info.get("required", False),
                                    )
                                arguments.append(arg)

                        prompt = Prompt(
                            name=prompt_info.name,
                            description=getattr(prompt_info, "description", ""),
                            arguments=arguments,
                        )
                    elif isinstance(prompt_info, dict):
                        # It's a dictionary - use dict access
                        arguments = []
                        if prompt_info.get("arguments"):
                            for arg_info in prompt_info["arguments"]:
                                from ..models.prompt import PromptArgument

                                arg = PromptArgument(
                                    name=arg_info["name"],
                                    description=arg_info.get("description"),
                                    required=arg_info.get("required", False),
                                )
                                arguments.append(arg)

                        prompt = Prompt(
                            name=prompt_info["name"], description=prompt_info.get("description"), arguments=arguments
                        )
                    if prompt:
                        prompts.append(prompt)
                return prompts
        except Exception as e:
            if self._debug:
                logger.debug(f"Error listing prompts: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list prompts: {e}")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool with arguments."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.call_tool(name, arguments)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to call tool {name}: {e}")

    async def read_resource(self, uri: str) -> Any:
        """Read a resource by URI."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.read_resource(uri)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to read resource {uri}: {e}")

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get a prompt with arguments."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            async with self._client:
                result = await self._client.get_prompt(name, arguments)
                return result
        except Exception as e:
            raise MCPClientError(f"Failed to get prompt {name}: {e}")
