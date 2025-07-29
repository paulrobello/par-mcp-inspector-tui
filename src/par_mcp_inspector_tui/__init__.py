"""PAR MCP Inspector TUI.

A comprehensive Terminal User Interface (TUI) application for inspecting and interacting
with Model Context Protocol (MCP) servers. Features smart content detection, automatic
syntax highlighting, markdown rendering, and complete MCP protocol debugging capabilities.

Key Features:
- Smart content detection with automatic viewer selection
- Raw MCP protocol interaction monitoring
- Multi-language syntax highlighting (20+ languages)
- Intelligent markdown rendering
- File management with copy/open functionality
- Real-time server introspection and debugging
"""

from __future__ import annotations

import os
import warnings

warnings.simplefilter("ignore", category=DeprecationWarning)


__author__ = "Paul Robello"
__credits__ = ["Paul Robello"]
__maintainer__ = "Paul Robello"
__email__ = "probello@gmail.com"
__version__ = "0.9.0"
__application_title__ = "PAR MCP Inspector TUI"
__application_binary__ = "pmit"
__licence__ = "MIT"


os.environ["USER_AGENT"] = f"{__application_title__} {__version__}"


__all__: list[str] = [
    "__author__",
    "__credits__",
    "__maintainer__",
    "__email__",
    "__version__",
    "__application_binary__",
    "__licence__",
    "__application_title__",
]
