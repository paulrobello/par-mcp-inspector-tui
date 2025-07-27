"""Base MCP protocol models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel


class TransportType(str, Enum):
    """MCP transport types."""

    STDIO = "stdio"
    TCP = "tcp"
    HTTP = "http"


class ServerNotificationType(str, Enum):
    """MCP server notification types for real-time updates."""

    TOOLS_LIST_CHANGED = "notifications/tools/list_changed"
    RESOURCES_LIST_CHANGED = "notifications/resources/list_changed"
    PROMPTS_LIST_CHANGED = "notifications/prompts/list_changed"
    ROOTS_LIST_CHANGED = "notifications/roots/list_changed"
    MESSAGE = "notifications/message"


class MCPError(BaseModel):
    """MCP error response."""

    code: int
    message: str
    data: dict[str, Any] | None = None


class MCPRequest(BaseModel):
    """Base MCP request."""

    jsonrpc: str = "2.0"
    id: str | int
    method: str
    params: dict[str, Any] | None = None


class MCPResponse(BaseModel):
    """Base MCP response."""

    jsonrpc: str = "2.0"
    id: str | int | None = None
    result: dict[str, Any] | None = None
    error: MCPError | None = None


class MCPNotification(BaseModel):
    """MCP notification (no ID)."""

    jsonrpc: str = "2.0"
    method: str
    params: dict[str, Any] | None = None


class ServerNotification(BaseModel):
    """Server notification with server context for TUI display."""

    server_name: str
    notification_type: ServerNotificationType
    message: str
    method: str
    params: dict[str, Any] | None = None
