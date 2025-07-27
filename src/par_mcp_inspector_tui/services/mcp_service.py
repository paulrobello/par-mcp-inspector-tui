"""MCP service for managing server connections, operations, and real-time notifications."""

import asyncio
from collections.abc import Callable
from datetime import datetime
from typing import Any

from ..client import HttpMCPClient, MCPClient, MCPClientError, StdioMCPClient, TcpMCPClient
from ..models import (
    MCPNotification,
    MCPServer,
    Prompt,
    Resource,
    ResourceTemplate,
    ServerInfo,
    ServerNotification,
    ServerNotificationType,
    ServerState,
    Tool,
    TransportType,
)


class MCPService:
    """Service for managing MCP server connections and operations."""

    def __init__(self, debug: bool = False, roots: list[str] | None = None) -> None:
        """Initialize MCP service."""
        self._client: MCPClient | None = None
        self._server: MCPServer | None = None
        self._connection_lock = asyncio.Lock()
        self._state_callbacks: list[Callable[[ServerState], None]] = []
        self._notification_callbacks: list[Callable[[ServerNotification], None]] = []
        self._debug: bool = debug
        self._roots: list[str] = roots or []

    @property
    def connected(self) -> bool:
        """Check if connected to a server."""
        return self._client is not None and self._client.connected

    @property
    def server(self) -> MCPServer | None:
        """Get current server configuration."""
        return self._server

    @property
    def server_info(self) -> ServerInfo | None:
        """Get server information."""
        return self._client.server_info if self._client else None

    def on_state_change(self, callback: Callable[[ServerState], None]) -> None:
        """Register a state change callback."""
        self._state_callbacks.append(callback)

    def on_server_notification(self, callback: Callable[[ServerNotification], None]) -> None:
        """Register a server notification callback."""
        self._notification_callbacks.append(callback)

    def _notify_state_change(self, state: ServerState) -> None:
        """Notify all state change callbacks."""
        if self._server:
            self._server.state = state

        for callback in self._state_callbacks:
            try:
                callback(state)
            except Exception as e:
                print(f"Error in state callback: {e}")

    def _notify_server_notification(self, notification: ServerNotification) -> None:
        """Notify all server notification callbacks."""
        for callback in self._notification_callbacks:
            try:
                callback(notification)
            except Exception as e:
                print(f"Error in notification callback: {e}")

    def _handle_mcp_notification(self, mcp_notification: MCPNotification) -> None:
        """Handle incoming MCP notification from server."""
        if self._debug:
            print(f"[DEBUG] MCPService received notification: {mcp_notification.method}")

        if not self._server:
            if self._debug:
                print("[DEBUG] No server configured, ignoring notification")
            return

        server_name = self._server.name or "Unknown Server"
        method = mcp_notification.method

        # Check if it's a known notification type
        notification_type = None
        message = f"Server notification: {method}"

        try:
            if method == ServerNotificationType.TOOLS_LIST_CHANGED:
                notification_type = ServerNotificationType.TOOLS_LIST_CHANGED
                message = f"Tools list changed on server '{server_name}'"
            elif method == ServerNotificationType.RESOURCES_LIST_CHANGED:
                notification_type = ServerNotificationType.RESOURCES_LIST_CHANGED
                message = f"Resources list changed on server '{server_name}'"
            elif method == ServerNotificationType.PROMPTS_LIST_CHANGED:
                notification_type = ServerNotificationType.PROMPTS_LIST_CHANGED
                message = f"Prompts list changed on server '{server_name}'"
            elif method == ServerNotificationType.MESSAGE:
                notification_type = ServerNotificationType.MESSAGE
                # Extract message content from params
                if mcp_notification.params and "data" in mcp_notification.params:
                    level = mcp_notification.params.get("level", "info")
                    data = mcp_notification.params["data"]
                    message = f"[{level.upper()}] {data}"
                else:
                    message = f"Server '{server_name}' sent a message notification"
            else:
                # Unknown notification type, use generic message
                message = f"Server '{server_name}' sent notification: {method}"
                notification_type = ServerNotificationType.MESSAGE  # Default to message type

            server_notification = ServerNotification(
                server_name=server_name,
                notification_type=notification_type,
                message=message,
                method=method,
                params=mcp_notification.params,
            )

            self._notify_server_notification(server_notification)

        except Exception as e:
            print(f"Error processing server notification: {e}")

    async def connect(self, server: MCPServer) -> None:
        """Connect to an MCP server.

        Args:
            server: Server configuration

        Raises:
            MCPClientError: If connection fails
        """
        async with self._connection_lock:
            # Disconnect if already connected
            if self.connected:
                await self.disconnect()

            self._server = server
            self._notify_state_change(ServerState.CONNECTING)

            try:
                # Create appropriate client
                if server.transport == TransportType.STDIO:
                    self._client = StdioMCPClient(debug=self._debug, roots=self._roots)
                    await self._client.connect(
                        command=server.command or "",
                        args=server.args,
                        env=server.env,
                    )
                elif server.transport == TransportType.TCP:
                    self._client = TcpMCPClient(debug=self._debug, roots=self._roots)
                    await self._client.connect(
                        host=server.host or "localhost",
                        port=server.port or 3333,
                    )
                elif server.transport == TransportType.HTTP:
                    self._client = HttpMCPClient(debug=self._debug, roots=self._roots)
                    await self._client.connect(
                        url=server.url or "",
                    )
                else:
                    raise MCPClientError(f"Unsupported transport: {server.transport}")

                # Initialize connection
                server_info = await self._client.initialize()
                server.info = server_info
                server.last_connected = datetime.now()

                # Register notification handlers
                if self._debug:
                    print(f"[DEBUG] Registering notification handlers for server: {server.name}")

                self._client.on_notification(ServerNotificationType.TOOLS_LIST_CHANGED, self._handle_mcp_notification)
                self._client.on_notification(
                    ServerNotificationType.RESOURCES_LIST_CHANGED, self._handle_mcp_notification
                )
                self._client.on_notification(ServerNotificationType.PROMPTS_LIST_CHANGED, self._handle_mcp_notification)
                self._client.on_notification(ServerNotificationType.MESSAGE, self._handle_mcp_notification)

                if self._debug:
                    print(f"[DEBUG] Registered handlers for: {list(ServerNotificationType)}")

                self._notify_state_change(ServerState.CONNECTED)

            except Exception as e:
                server.error = str(e)
                self._notify_state_change(ServerState.ERROR)

                # Clean up
                if self._client:
                    try:
                        await self._client.disconnect()
                    except Exception:
                        pass
                    self._client = None

                raise MCPClientError(f"Connection failed: {e}")

    async def disconnect(self) -> None:
        """Disconnect from current server."""
        if not self._client:
            return

        try:
            await self._client.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        finally:
            self._client = None
            self._notify_state_change(ServerState.DISCONNECTED)

    async def list_tools(self) -> list[Tool]:
        """List available tools from connected server.

        Returns:
            List of available tools

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.list_tools()

    async def list_resources(self) -> list[Resource]:
        """List available resources from connected server.

        Returns:
            List of available resources

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.list_resources()

    async def list_resource_templates(self) -> list[ResourceTemplate]:
        """List available resource templates from connected server.

        Returns:
            List of available resource templates

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.list_resource_templates()

    async def list_prompts(self) -> list[Prompt]:
        """List available prompts from connected server.

        Returns:
            List of available prompts

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.list_prompts()

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call a tool on the connected server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.call_tool(name, arguments)

    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the connected server.

        Args:
            uri: Resource URI

        Returns:
            Resource content

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.read_resource(uri)

    async def get_prompt(self, name: str, arguments: dict[str, Any]) -> Any:
        """Get a prompt from the connected server.

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            Prompt result

        Raises:
            MCPClientError: If not connected or request fails
        """
        if not self._client or not self.connected:
            raise MCPClientError("Not connected to server")

        return await self._client.get_prompt(name, arguments)
