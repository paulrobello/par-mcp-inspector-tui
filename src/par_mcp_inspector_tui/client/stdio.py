"""STDIO MCP client implementation using FastMCP's StdioTransport."""

import logging
from typing import Any

import mcp.types
from fastmcp import Client
from fastmcp.client.messages import MessageHandler
from fastmcp.client.transports import StdioTransport

from ..models import MCPNotification, Prompt, Resource, ResourceTemplate, ServerInfo, Tool
from .base import MCPClient, MCPClientError

logger = logging.getLogger(__name__)


class NotificationBridge(MessageHandler):
    """Bridge FastMCP notifications to our notification system."""

    def __init__(self, client: "StdioMCPClient") -> None:
        """Initialize the notification bridge."""
        self.client = client

    async def on_notification(self, message: mcp.types.ServerNotification) -> None:
        """Handle all notifications from FastMCP and forward to our handlers."""
        if self.client._debug:
            logger.debug(f"FastMCP notification received: {message.root}")

        # Convert FastMCP notification to our MCPNotification format
        # The actual notification data is in message.root
        params = getattr(message.root, "params", None)

        # Convert Pydantic params object to dict if needed
        if params is not None and hasattr(params, "model_dump"):
            params = params.model_dump()

        mcp_notification = MCPNotification(
            method=message.root.method,
            params=params,
        )

        # Call the base client's notification handler
        await self.client._handle_notification(mcp_notification)

    async def on_tool_list_changed(self, message: mcp.types.ToolListChangedNotification) -> None:
        """Handle tool list changed notifications."""
        if self.client._debug:
            logger.debug(f"Tools list changed notification: {message}")

    async def on_resource_list_changed(self, message: mcp.types.ResourceListChangedNotification) -> None:
        """Handle resource list changed notifications."""
        if self.client._debug:
            logger.debug(f"Resources list changed notification: {message}")

    async def on_prompt_list_changed(self, message: mcp.types.PromptListChangedNotification) -> None:
        """Handle prompt list changed notifications."""
        if self.client._debug:
            logger.debug(f"Prompts list changed notification: {message}")

    async def on_logging_message(self, message: mcp.types.LoggingMessageNotification) -> None:
        """Handle logging message notifications."""
        if self.client._debug:
            logger.debug(f"Logging message notification: {message}")


class StdioMCPClient(MCPClient):
    """MCP client using FastMCP's StdioTransport.

    This implementation uses FastMCP's StdioTransport which provides
    robust subprocess management and process lifecycle handling.
    """

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize STDIO client.

        Args:
            debug: Enable debug logging
            roots: List of root paths for filesystem servers
        """
        super().__init__(debug=debug, roots=roots)
        self._transport: StdioTransport | None = None
        self._client: Client | None = None
        self._command: str = ""
        self._args: list[str] = []

    async def connect(self, command: str, args: list[str] | None = None, env: dict[str, str] | None = None) -> None:
        """Connect to MCP server via STDIO.

        Args:
            command: Command to execute
            args: Command arguments
            env: Environment variables
        """
        if self._connected:
            raise MCPClientError("Already connected")

        self._command = command
        self._args = args or []

        # Prepare environment - FastMCP requires explicit env passing
        process_env = {}
        if env:
            process_env.update(env)

        # Create StdioTransport with FastMCP
        if self._debug:
            logger.debug(f"Creating StdioTransport with command: {command}, args: {self._args}, env: {process_env}")

        try:
            # Always suppress server stderr to prevent output interference with TUI
            # Server stderr often contains status messages that bleed through to TUI display
            import shlex

            # Build the command string with proper quoting
            cmd_parts = [shlex.quote(command)] + [shlex.quote(arg) for arg in self._args]
            # Only redirect stderr - stdout is needed for MCP communication
            # but stderr often contains server status/logging messages that interfere with TUI
            cmd_string = " ".join(cmd_parts) + " 2>/dev/null"

            # Use shell wrapper to enable stderr redirection
            logger.debug(f"Using stderr-suppressed command: {cmd_string}")
            self._transport = StdioTransport(
                command="sh", args=["-c", cmd_string], env=process_env if process_env else None
            )

            # Create notification bridge to handle FastMCP notifications
            notification_bridge = NotificationBridge(self)

            # Create FastMCP client with transport and notification handler
            self._client = Client(self._transport, message_handler=notification_bridge)

            self._connected = True

            if self._debug:
                logger.debug(f"Connected to STDIO process: {command} {' '.join(self._args)}")
        except Exception as e:
            # Handle EPIPE and other subprocess errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e):
                raise MCPClientError(f"Subprocess communication failed (EPIPE): {e}")
            else:
                raise MCPClientError(f"Failed to create subprocess: {e}")

    async def disconnect(self) -> None:
        """Disconnect from MCP server."""
        if not self._connected:
            return

        self._connected = False

        # Close client (this will handle transport cleanup)
        if self._client:
            try:
                await self._client.close()
                if self._debug:
                    logger.debug("FastMCP client closed successfully")
            except Exception as e:
                if self._debug:
                    logger.debug(f"Error closing client: {e}")
            finally:
                self._client = None

        # Ensure transport is cleaned up
        if self._transport:
            try:
                # If transport has a close method, call it
                if hasattr(self._transport, "close"):
                    await self._transport.close()
                if self._debug:
                    logger.debug("Transport cleaned up")
            except Exception as e:
                if self._debug:
                    logger.debug(f"Error cleaning up transport: {e}")
            finally:
                self._transport = None

        if self._debug:
            logger.debug("Disconnected from STDIO process")

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

                server_name = "STDIO MCP Server"
                server_version = "unknown"
                protocol_version = "2025-06-18"

                # Try to get server info from transport if available
                if self._transport and hasattr(self._transport, "server_info"):
                    server_info_dict = getattr(self._transport, "server_info", None) or {}
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
            # Handle EPIPE and other subprocess communication errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e) or "errno: -32" in str(e):
                raise MCPClientError(f"Subprocess communication failed during initialization (EPIPE): {e}")
            else:
                raise MCPClientError(f"Failed to initialize: {e}")

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Log the request
            import json

            self._notify_interaction(json.dumps({"method": "tools/list", "params": {}}), "sent")

            async with self._client:
                tools_data = await self._client.list_tools()

                # Log the response (handle complex objects safely)
                try:
                    # Convert tools data to serializable format
                    serializable_tools = []
                    for tool in tools_data:
                        if hasattr(tool, "model_dump"):
                            # Pydantic model - use model_dump
                            serializable_tools.append(tool.model_dump())
                        elif hasattr(tool, "__dict__"):
                            # Regular object - convert attributes
                            tool_dict = {}
                            for key, value in tool.__dict__.items():
                                if hasattr(value, "model_dump"):
                                    tool_dict[key] = value.model_dump()
                                elif hasattr(value, "__dict__"):
                                    tool_dict[key] = value.__dict__
                                else:
                                    tool_dict[key] = (
                                        str(value)
                                        if not isinstance(value, str | int | float | bool | type(None))
                                        else value
                                    )
                            serializable_tools.append(tool_dict)
                        else:
                            # Already a dict or simple value
                            serializable_tools.append(tool)

                    self._notify_interaction(json.dumps({"result": {"tools": serializable_tools}}), "received")
                except (TypeError, AttributeError) as e:
                    # If serialization still fails, log a more detailed message
                    self._notify_interaction(
                        json.dumps(
                            {"result": {"tools": f"[{len(tools_data)} tools returned - serialization error: {str(e)}]"}}
                        ),
                        "received",
                    )
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

                        # The server may have properties, don't override them
                        if "properties" not in input_schema_data:
                            input_schema_data["properties"] = {}

                        if self._debug:
                            logger.debug(f"Final tool schema: {input_schema_data}")

                        # Convert dict to ToolParameter
                        from ..models.tool import ToolParameter

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

                        # Convert dict to ToolParameter
                        from ..models.tool import ToolParameter

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
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            # Handle EPIPE and other subprocess communication errors
            if "EPIPE" in str(e) or "Broken pipe" in str(e) or "errno: -32" in str(e):
                raise MCPClientError(f"Subprocess communication failed during list_tools (EPIPE): {e}")
            raise MCPClientError(f"Failed to list tools: {e}")

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Log the request
            import json

            self._notify_interaction(json.dumps({"method": "resources/list", "params": {}}), "sent")

            async with self._client:
                resources_data = await self._client.list_resources()

                # Log the response (handle complex objects safely)
                try:
                    # Convert resources data to serializable format
                    serializable_resources = []
                    for resource in resources_data:
                        if hasattr(resource, "model_dump"):
                            # Pydantic model - use model_dump
                            serializable_resources.append(resource.model_dump())
                        elif hasattr(resource, "__dict__"):
                            # Regular object - convert attributes
                            resource_dict = {}
                            for key, value in resource.__dict__.items():
                                if hasattr(value, "model_dump"):
                                    resource_dict[key] = value.model_dump()
                                elif hasattr(value, "__dict__"):
                                    resource_dict[key] = value.__dict__
                                else:
                                    resource_dict[key] = (
                                        str(value)
                                        if not isinstance(value, str | int | float | bool | type(None))
                                        else value
                                    )
                            serializable_resources.append(resource_dict)
                        else:
                            # Already a dict or simple value
                            serializable_resources.append(resource)

                    self._notify_interaction(json.dumps({"result": {"resources": serializable_resources}}), "received")
                except (TypeError, AttributeError) as e:
                    # If serialization still fails, log a more detailed message
                    self._notify_interaction(
                        json.dumps(
                            {
                                "result": {
                                    "resources": f"[{len(resources_data)} resources returned - serialization error: {str(e)}]"
                                }
                            }
                        ),
                        "received",
                    )
                resources = []
                for resource_info in resources_data:
                    # FastMCP may return Resource objects or dictionaries
                    if hasattr(resource_info, "uri"):
                        # It's a Resource object - extract attributes
                        # Convert AnyUrl to string if needed
                        uri_value = getattr(resource_info, "uri", "")
                        uri_value = str(uri_value)  # Always convert to string

                        resource = Resource(
                            uri=uri_value,
                            name=getattr(resource_info, "name", ""),
                            description=getattr(resource_info, "description", None),
                            mimeType=getattr(resource_info, "mimeType", None),  # Use camelCase
                        )
                    elif isinstance(resource_info, dict):
                        # It's a dictionary - use dict access
                        resource = Resource(
                            uri=resource_info["uri"],
                            name=resource_info.get("name", ""),
                            description=resource_info.get("description"),
                            mimeType=resource_info.get("mimeType"),  # Use camelCase
                        )
                    else:
                        # Skip invalid resource_info
                        continue
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
                    # FastMCP may return ResourceTemplate objects or dictionaries
                    if hasattr(template_info, "uriTemplate"):
                        # It's a ResourceTemplate object - extract attributes with camelCase
                        template = ResourceTemplate(
                            uriTemplate=getattr(template_info, "uriTemplate", ""),  # Use camelCase
                            name=getattr(template_info, "name", ""),
                            description=getattr(template_info, "description", None),
                            mimeType=getattr(template_info, "mimeType", None),  # Use camelCase
                        )
                    elif isinstance(template_info, dict):
                        # It's a dictionary - use dict access
                        template = ResourceTemplate(
                            uriTemplate=template_info["uriTemplate"],  # Use camelCase
                            name=template_info.get("name", ""),
                            description=template_info.get("description"),
                            mimeType=template_info.get("mimeType"),  # Use camelCase
                        )
                    else:
                        # Skip invalid template_info
                        continue
                    templates.append(template)
                return templates
        except Exception as e:
            if self._debug:
                logger.debug(f"Error listing resource templates: {e}")
            if "timeout" in str(e).lower() or "not supported" in str(e).lower() or "method not found" in str(e).lower():
                return []
            raise MCPClientError(f"Failed to list resource templates: {e}")

    async def list_prompts(self) -> list[Prompt]:
        """List available prompts."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Log the request
            import json

            self._notify_interaction(json.dumps({"method": "prompts/list", "params": {}}), "sent")

            async with self._client:
                prompts_data = await self._client.list_prompts()

                # Log the response (handle complex objects safely)
                try:
                    # Convert prompts data to serializable format
                    serializable_prompts = []
                    for prompt in prompts_data:
                        if hasattr(prompt, "model_dump"):
                            # Pydantic model - use model_dump
                            serializable_prompts.append(prompt.model_dump())
                        elif hasattr(prompt, "__dict__"):
                            # Regular object - convert attributes
                            prompt_dict = {}
                            for key, value in prompt.__dict__.items():
                                if hasattr(value, "model_dump"):
                                    prompt_dict[key] = value.model_dump()
                                elif hasattr(value, "__dict__"):
                                    prompt_dict[key] = value.__dict__
                                else:
                                    prompt_dict[key] = value
                            serializable_prompts.append(prompt_dict)
                        else:
                            # Already a dict or simple value
                            serializable_prompts.append(prompt)

                    self._notify_interaction(json.dumps({"result": {"prompts": serializable_prompts}}), "received")
                except (TypeError, AttributeError) as e:
                    # If serialization still fails, log a more detailed message
                    self._notify_interaction(
                        json.dumps(
                            {
                                "result": {
                                    "prompts": f"[{len(prompts_data)} prompts returned - serialization error: {str(e)}]"
                                }
                            }
                        ),
                        "received",
                    )
                prompts = []
                for prompt_info in prompts_data:
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
                                else:
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
                    else:
                        # Skip invalid prompt_info
                        continue
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
            # Log the request
            request_data = {"method": "tools/call", "params": {"name": name, "arguments": arguments}}
            self._notify_interaction(f'{{"method": "tools/call", "params": {request_data["params"]}}}', "sent")

            async with self._client:
                result = await self._client.call_tool(name, arguments)

                # Log the response (handle complex objects safely)
                import json

                try:
                    self._notify_interaction(json.dumps({"result": result}), "received")
                except (TypeError, AttributeError):
                    # If serialization fails, log a simple message
                    self._notify_interaction(json.dumps({"result": "[Tool execution completed]"}), "received")

                return result
        except Exception as e:
            raise MCPClientError(f"Failed to call tool {name}: {e}")

    async def read_resource(self, uri: str) -> Any:
        """Read a resource by URI."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Log the request
            request_data = {"method": "resources/read", "params": {"uri": uri}}
            import json

            self._notify_interaction(json.dumps(request_data), "sent")

            async with self._client:
                result = await self._client.read_resource(uri)

                # Log the response (handle complex objects safely)
                import json

                try:
                    self._notify_interaction(json.dumps({"result": result}), "received")
                except (TypeError, AttributeError):
                    # If serialization fails, log a simple message
                    self._notify_interaction(json.dumps({"result": "[Resource read completed]"}), "received")

                return result
        except Exception as e:
            raise MCPClientError(f"Failed to read resource {uri}: {e}")

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get a prompt with arguments."""
        if not self._client:
            raise MCPClientError("Not connected")

        try:
            # Log the request
            request_data = {"method": "prompts/get", "params": {"name": name, "arguments": arguments}}
            import json

            self._notify_interaction(json.dumps(request_data), "sent")

            async with self._client:
                result = await self._client.get_prompt(name, arguments)

                # Log the response (handle complex objects safely)
                import json

                try:
                    self._notify_interaction(json.dumps({"result": result}), "received")
                except (TypeError, AttributeError):
                    # If serialization fails, log a simple message
                    self._notify_interaction(json.dumps({"result": "[Prompt retrieved]"}), "received")

                return result
        except Exception as e:
            raise MCPClientError(f"Failed to get prompt {name}: {e}")
