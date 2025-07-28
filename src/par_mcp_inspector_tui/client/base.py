"""Base MCP client interface."""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from os import path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from datetime import datetime

from ..models import (
    MCPNotification,
    MCPRequest,
    MCPResponse,
    Prompt,
    Resource,
    ResourceTemplate,
    ServerInfo,
    Tool,
)

logger = logging.getLogger(__name__)

InteractionType = Literal["sent", "received"]


class MCPClientError(Exception):
    """MCP client error."""

    pass


class MCPClient(ABC):
    """Abstract base class for MCP clients with notification support.

    Provides common functionality for both STDIO and TCP transports:
    - JSON-RPC message handling with proper request/response matching
    - Server notification registration and callback system
    - Client capability declaration for receiving notifications
    - Roots support for filesystem servers
    - Debug logging for protocol troubleshooting
    """

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize the client."""
        self._connected: bool = False
        self._request_id: int = 0
        self._pending_requests: dict[str | int, asyncio.Future[MCPResponse]] = {}
        self._notification_handlers: dict[str, list[Callable[[MCPNotification], None]]] = {}
        self._interaction_handlers: list[Callable[[str, InteractionType, datetime], None]] = []
        self._server_info: ServerInfo | None = None
        self._debug: bool = debug
        self._roots: list[str] = roots or []

    @property
    def connected(self) -> bool:
        """Check if client is connected."""
        return self._connected

    @property
    def server_info(self) -> ServerInfo | None:
        """Get server information."""
        return self._server_info

    def _get_next_id(self) -> int:
        """Get next request ID."""
        self._request_id += 1
        return self._request_id

    @abstractmethod
    async def connect(self, **kwargs: Any) -> None:
        """Connect to the MCP server."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        pass

    @abstractmethod
    async def _send_data(self, data: str) -> None:
        """Send raw data to the server."""
        pass

    @abstractmethod
    async def _receive_data(self) -> str | None:
        """Receive raw data from the server."""
        pass

    async def _send_request(self, method: str, params: dict[str, Any] | None = None) -> MCPResponse:
        """Send a request and wait for response."""
        request_id = self._get_next_id()
        request = MCPRequest(id=request_id, method=method, params=params)

        # Create future for response
        future: asyncio.Future[MCPResponse] = asyncio.Future()
        self._pending_requests[request_id] = future

        # Send request
        request_json = request.model_dump_json() + "\n"
        if self._debug:
            logger.debug(f"Sending: {request_json.strip()}")

        # Notify interaction handlers
        self._notify_interaction(request_json.strip(), "sent")

        await self._send_data(request_json)

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=10.0)
            if self._debug:
                logger.debug(f"Received: {response.model_dump_json()}")

            # Note: interaction notification already handled in _handle_incoming_data with raw data

            if response.error:
                raise MCPClientError(f"Server error: {response.error.message}")
            return response
        except TimeoutError:
            if self._debug:
                logger.debug(f"Timeout waiting for response to {method}")
            raise MCPClientError(f"Timeout waiting for response to {method}")
        finally:
            self._pending_requests.pop(request_id, None)

    async def _send_notification(self, method: str, params: dict[str, Any] | None = None) -> None:
        """Send a notification (no response expected)."""
        notification = MCPNotification(method=method, params=params)
        notification_json = notification.model_dump_json() + "\n"
        if self._debug:
            logger.debug(f"Sending notification: {notification_json.strip()}")

        # Notify interaction handlers
        self._notify_interaction(notification_json.strip(), "sent")

        await self._send_data(notification_json)

    async def _handle_incoming_data(self, data: str) -> None:
        """Handle incoming data from server."""
        try:
            message = json.loads(data)

            if self._debug:
                logger.debug(f"Raw incoming: {data.strip()}")

            # Notify interaction handlers
            self._notify_interaction(data.strip(), "received")

            # Check if it's a response
            if "id" in message and ("result" in message or "error" in message):
                response = MCPResponse(**message)
                if self._debug:
                    logger.debug(
                        f"Processing response for ID {response.id}, pending: {list(self._pending_requests.keys())}"
                    )
                if response.id in self._pending_requests:
                    self._pending_requests[response.id].set_result(response)
                else:
                    logger.warning(f"Received response for unknown request ID: {response.id}")

            # Check if it's a request from server
            elif "id" in message and "method" in message:
                await self._handle_request(message)

            # Check if it's a notification
            elif "method" in message and "id" not in message:
                notification = MCPNotification(**message)
                await self._handle_notification(notification)

        except Exception as e:
            # Log error but don't crash
            logger.error(f"Error handling incoming data: {e}")

    async def _handle_request(self, message: dict[str, Any]) -> None:
        """Handle incoming request from server."""
        request_id = message["id"]
        method = message["method"]

        if self._debug:
            logger.debug(f"Received request: {method}")

        try:
            if method == "roots/list":
                # Convert local paths to file:// URIs
                roots = []
                for root_path in self._roots:
                    # Convert to absolute path and file:// URI
                    abs_path = path.abspath(root_path)
                    file_uri = f"file://{abs_path}"
                    roots.append({"uri": file_uri, "name": path.basename(abs_path) or abs_path})

                response = {"jsonrpc": "2.0", "id": request_id, "result": {"roots": roots}}

                if self._debug:
                    logger.debug(f"Sending roots response: {json.dumps(response)}")

                await self._send_data(json.dumps(response) + "\n")
            else:
                # Method not found
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }
                await self._send_data(json.dumps(error_response) + "\n")
        except Exception as e:
            # Internal error
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
            }
            await self._send_data(json.dumps(error_response) + "\n")

    async def _handle_notification(self, notification: MCPNotification) -> None:
        """Handle incoming notification from server.

        Processes server notifications by finding registered handlers
        and calling them with the notification. Supports real-time
        updates for tools, resources, prompts changes and messages.
        """
        if self._debug:
            logger.debug(f"Received notification: {notification.method}")

        handlers = self._notification_handlers.get(notification.method, [])
        if self._debug:
            logger.debug(f"Found {len(handlers)} handlers for {notification.method}")

        for handler in handlers:
            try:
                handler(notification)
            except Exception as e:
                logger.error(f"Error in notification handler: {e}")

    def on_notification(self, method: str, handler: Callable[[MCPNotification], None]) -> None:
        """Register a notification handler."""
        if method not in self._notification_handlers:
            self._notification_handlers[method] = []
        self._notification_handlers[method].append(handler)

    def on_interaction(self, handler: Callable[[str, InteractionType, "datetime"], None]) -> None:
        """Register an interaction handler for capturing raw MCP messages.

        Args:
            handler: Function called with (message, interaction_type, timestamp) for each interaction
        """
        self._interaction_handlers.append(handler)

    def _notify_interaction(self, message: str, interaction_type: InteractionType) -> None:
        """Notify all interaction handlers of a new message.

        Args:
            message: Raw JSON message
            interaction_type: Whether this was sent or received
        """
        from datetime import datetime

        timestamp = datetime.now()
        if self._debug:
            logger.debug(
                f"_notify_interaction: {interaction_type} - {len(self._interaction_handlers)} handlers - {message[:100]}..."
            )
        for handler in self._interaction_handlers:
            try:
                handler(message, interaction_type, timestamp)
            except Exception as e:
                logger.error(f"Error in interaction handler: {e}")

    async def initialize(self) -> ServerInfo:
        """Initialize connection and get server info."""
        response = await self._send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "tools": {"listChanged": True},
                    "resources": {"listChanged": True},
                    "prompts": {"listChanged": True},
                },
                "clientInfo": {
                    "name": "MCP Inspector",
                    "version": "0.1.0",
                },
            },
        )

        if not response.result:
            raise MCPClientError("No result in initialize response")

        # Handle the MCP response structure
        # protocolVersion is at top level, but name/version are in serverInfo
        server_info_data = {
            "protocol_version": response.result.get("protocolVersion", "unknown"),
            "capabilities": response.result.get("capabilities"),
        }

        # Extract nested serverInfo fields
        if "serverInfo" in response.result:
            nested_info = response.result["serverInfo"]
            server_info_data.update(
                {
                    "name": nested_info.get("name"),
                    "version": nested_info.get("version", "unknown"),
                }
            )
        else:
            # Fallback: try top-level fields
            server_info_data.update(
                {
                    "name": response.result.get("name"),
                    "version": response.result.get("version", "unknown"),
                }
            )

        # Add vendor info if present
        if "vendorInfo" in response.result:
            server_info_data["vendor_info"] = response.result["vendorInfo"]

        self._server_info = ServerInfo(**server_info_data)

        # Send initialized notification as required by MCP spec
        await self._send_notification("notifications/initialized")

        # Give server time to process the initialized notification
        await asyncio.sleep(0.1)

        return self._server_info

    async def list_tools(self) -> list[Tool]:
        """List available tools."""
        # Check if server supports tools
        if self._server_info and self._server_info.capabilities:
            if self._server_info.capabilities.tools is None:
                # Server doesn't support tools
                return []

        try:
            response = await self._send_request("tools/list", {})
            if not response.result:
                return []

            tools_data = response.result.get("tools", [])
            return [Tool(**tool) for tool in tools_data]
        except MCPClientError as e:
            # If server times out or errors on tools/list, it likely doesn't actually support tools
            # despite reporting tools capability as {}
            if "Timeout" in str(e):
                return []
            raise

    async def list_resources(self) -> list[Resource]:
        """List available resources."""
        # Check if server supports resources
        if self._server_info and self._server_info.capabilities:
            if self._server_info.capabilities.resources is None:
                # Server doesn't support resources
                return []

        try:
            response = await self._send_request("resources/list", {})
            if not response.result:
                return []

            resources_data = response.result.get("resources", [])
            return [Resource(**resource) for resource in resources_data]
        except MCPClientError as e:
            # If server times out or errors on resources/list, it likely doesn't actually support resources
            # despite reporting resources capability as {}
            if "Timeout" in str(e):
                return []
            raise

    async def list_resource_templates(self) -> list[ResourceTemplate]:
        """List available resource templates."""
        # Check if server supports resources
        if self._server_info and self._server_info.capabilities:
            if self._server_info.capabilities.resources is None:
                # Server doesn't support resources
                return []

        try:
            response = await self._send_request("resources/templates/list", {})
            if not response.result:
                return []

            templates_data = response.result.get("resourceTemplates", [])
            return [ResourceTemplate(**template) for template in templates_data]
        except MCPClientError as e:
            # If server times out or errors on resources/templates/list, it likely doesn't actually support resources
            # despite reporting resources capability as {}
            if "Timeout" in str(e):
                return []
            raise

    async def list_prompts(self) -> list[Prompt]:
        """List available prompts."""
        # Check if server supports prompts
        if self._server_info and self._server_info.capabilities:
            if self._server_info.capabilities.prompts is None:
                # Server doesn't support prompts
                return []

        try:
            response = await self._send_request("prompts/list", {})
            if not response.result:
                return []

            prompts_data = response.result.get("prompts", [])
            return [Prompt(**prompt) for prompt in prompts_data]
        except MCPClientError as e:
            # If server times out or errors on prompts/list, it likely doesn't actually support prompts
            # despite reporting prompts capability as {}
            if "Timeout" in str(e):
                return []
            raise

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool with arguments."""
        response = await self._send_request(
            "tools/call",
            {
                "name": name,
                "arguments": arguments,
            },
        )
        return response.result

    async def read_resource(self, uri: str) -> Any:
        """Read a resource by URI."""
        response = await self._send_request("resources/read", {"uri": uri})
        return response.result

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get a prompt with arguments."""
        response = await self._send_request(
            "prompts/get",
            {
                "name": name,
                "arguments": arguments,
            },
        )
        return response.result

    def get_roots(self) -> list[dict[str, Any]]:
        """Get current filesystem roots."""
        roots = []
        for root_path in self._roots:
            # Convert to absolute path and file:// URI
            abs_path = path.abspath(root_path)
            file_uri = f"file://{abs_path}"
            roots.append({"uri": file_uri, "name": path.basename(abs_path) or abs_path})
        return roots

    def add_root(self, root_path: str) -> None:
        """Add a new filesystem root."""
        # Convert file:// URI to local path if needed
        if root_path.startswith("file://"):
            from urllib.parse import urlparse

            parsed = urlparse(root_path)
            root_path = parsed.path

        # Add to roots if not already present
        abs_path = path.abspath(root_path)
        if abs_path not in self._roots:
            self._roots.append(abs_path)
            # Send notification to server about roots change
            asyncio.create_task(self._notify_roots_changed())

    def remove_root(self, root_path: str) -> bool:
        """Remove a filesystem root. Returns True if removed, False if not found."""
        # Convert file:// URI to local path if needed
        if root_path.startswith("file://"):
            from urllib.parse import urlparse

            parsed = urlparse(root_path)
            root_path = parsed.path

        abs_path = path.abspath(root_path)
        if abs_path in self._roots:
            self._roots.remove(abs_path)
            # Send notification to server about roots change
            asyncio.create_task(self._notify_roots_changed())
            return True
        return False

    def set_roots(self, root_paths: list[str]) -> None:
        """Set the complete list of filesystem roots."""
        new_roots = []
        for root_path in root_paths:
            # Convert file:// URI to local path if needed
            if root_path.startswith("file://"):
                from urllib.parse import urlparse

                parsed = urlparse(root_path)
                root_path = parsed.path
            new_roots.append(path.abspath(root_path))

        self._roots = new_roots
        # Send notification to server about roots change
        asyncio.create_task(self._notify_roots_changed())

    async def _notify_roots_changed(self) -> None:
        """Send notification to server that roots list has changed."""
        if self._connected:
            try:
                await self._send_notification("notifications/roots/list_changed")
            except Exception as e:
                if self._debug:
                    logger.debug(f"Failed to send roots changed notification: {e}")
