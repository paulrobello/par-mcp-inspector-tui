"""MCP tool models."""

from typing import Any

from pydantic import BaseModel, Field


class ToolParameterProperties(BaseModel):
    """Properties for a tool parameter."""

    type: str
    description: str | None = None
    enum: list[Any] | None = None
    items: dict[str, Any] | None = None
    properties: dict[str, "ToolParameterProperties"] | None = None
    required: list[str] | None = None
    default: Any = None
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = Field(None, alias="minLength")
    max_length: int | None = Field(None, alias="maxLength")
    pattern: str | None = None
    format: str | None = None


class ToolParameter(BaseModel):
    """Tool parameter schema."""

    type: str = "object"
    properties: dict[str, ToolParameterProperties]
    required: list[str] | None = None
    additional_properties: bool = Field(False, alias="additionalProperties")


class Tool(BaseModel):
    """MCP tool definition."""

    model_config = {"populate_by_name": True}

    name: str
    description: str | None = None
    input_schema: ToolParameter = Field(alias="inputSchema")

    def get_required_params(self) -> list[str]:
        """Get list of required parameters."""
        return self.input_schema.required or []

    def get_all_params(self) -> list[str]:
        """Get list of all parameters."""
        return list(self.input_schema.properties.keys())
