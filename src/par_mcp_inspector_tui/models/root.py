"""MCP root models for filesystem access control."""

from typing import Any

from pydantic import BaseModel, Field


class Root(BaseModel):
    """A filesystem root that defines access boundaries for MCP servers.

    Roots are exposed by clients to servers to define which directories
    and files the server has access to operate within.
    """

    uri: str = Field(..., description="Unique identifier for the root (must be file:// URI)")
    name: str | None = Field(None, description="Optional human-readable name for display")

    def __str__(self) -> str:
        """String representation of the root."""
        return f"{self.name or 'Root'}: {self.uri}"


class RootListRequest(BaseModel):
    """MCP request to list available roots."""

    jsonrpc: str = "2.0"
    id: str | int
    method: str = "roots/list"


class RootListResponse(BaseModel):
    """MCP response containing list of roots."""

    jsonrpc: str = "2.0"
    id: str | int
    result: dict[str, list[Root]] = Field(default_factory=lambda: {"roots": []})


class RootListChangedNotification(BaseModel):
    """MCP notification sent when the roots list changes."""

    jsonrpc: str = "2.0"
    method: str = "notifications/roots/list_changed"
    params: dict[str, Any] | None = None


class RootInfo(BaseModel):
    """Extended root information for display purposes."""

    root: Root
    exists: bool = Field(default=False, description="Whether the root path exists")
    accessible: bool = Field(default=False, description="Whether the root is accessible")
    type: str = Field(default="unknown", description="Type: directory, file, or unknown")
    size: int | None = Field(None, description="Size in bytes (for files)")
    modified: int | None = Field(None, description="Last modified timestamp (nanoseconds)")
