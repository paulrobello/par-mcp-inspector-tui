"""MCP prompt models."""

from typing import Any

from pydantic import BaseModel


class PromptArgument(BaseModel):
    """Prompt argument definition."""

    name: str
    description: str | None = None
    required: bool = True


class PromptMessage(BaseModel):
    """Prompt message."""

    role: str
    content: str | dict[str, Any]


class Prompt(BaseModel):
    """MCP prompt definition."""

    name: str
    description: str | None = None
    arguments: list[PromptArgument] | None = None

    def get_required_args(self) -> list[str]:
        """Get list of required argument names."""
        if not self.arguments:
            return []
        return [arg.name for arg in self.arguments if arg.required]

    def get_all_args(self) -> list[str]:
        """Get list of all argument names."""
        if not self.arguments:
            return []
        return [arg.name for arg in self.arguments]
