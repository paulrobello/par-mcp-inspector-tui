"""
MCP Resources Module

This module provides a clean, modular way to organize and register MCP resources.
Each resource is defined in its own file for better maintainability and separation of concerns.

Usage:
    from resources import register_all_resources
    register_all_resources(mcp)

Resources:
- Resource #1: Static server info (server://info)
- Resource #2: Dynamic user info (user://{user_id})
- Resource #3: File system with wildcards (files://{filepath*})
"""

from collections.abc import Callable
from typing import Any

from .resource_1_static_info import register_static_info_resource
from .resource_2_dynamic_user import register_dynamic_user_resource
from .resource_3_file_system import register_file_system_resource


def register_all_resources(mcp: Any) -> dict[str, Callable[..., Any]]:
    """Register all MCP resources with the FastMCP instance.

    Args:
        mcp: FastMCP instance to register resources with

    Returns:
        Dictionary of registered resource names to their handler functions
    """
    registered: dict[str, Callable[..., Any]] = {}

    registered.update(register_static_info_resource(mcp))
    registered.update(register_dynamic_user_resource(mcp))
    registered.update(register_file_system_resource(mcp))

    return registered


__all__ = ["register_all_resources"]
