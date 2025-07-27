"""MCP server models."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .base import TransportType


class ServerState(str, Enum):
    """Server connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class ServerCapabilities(BaseModel):
    """MCP server capabilities."""

    prompts: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    tools: dict[str, Any] | None = None
    logging: dict[str, Any] | None = None
    sampling: dict[str, Any] | None = None


class ServerInfo(BaseModel):
    """MCP server information."""

    model_config = {"populate_by_name": True}

    name: str | None = None
    version: str
    protocol_version: str = Field(alias="protocolVersion")
    capabilities: ServerCapabilities | None = None
    vendor_info: dict[str, Any] | None = Field(None, alias="vendorInfo")


class MCPServer(BaseModel):
    """MCP server configuration and state."""

    id: str
    name: str
    transport: TransportType
    command: str | None = None  # For STDIO transport
    args: list[str] | None = None  # For STDIO transport
    host: str | None = None  # For TCP transport
    port: int | None = None  # For TCP transport
    url: str | None = None  # For HTTP transport
    env: dict[str, str] | None = None
    roots: list[str] | None = None  # Filesystem roots for the server
    toast_notifications: bool = True  # Show toast notifications for server notifications
    state: ServerState = ServerState.DISCONNECTED
    info: ServerInfo | None = None
    last_connected: datetime | None = None
    error: str | None = None

    def get_connection_params(self) -> dict[str, Any]:
        """Get connection parameters based on transport type."""
        if self.transport == TransportType.STDIO:
            return {
                "command": self.command,
                "args": self.args or [],
                "env": self.env or {},
            }
        elif self.transport == TransportType.TCP:
            return {
                "host": self.host,
                "port": self.port,
            }
        elif self.transport == TransportType.HTTP:
            return {
                "url": self.url,
            }
        else:
            raise ValueError(f"Unknown transport type: {self.transport}")
