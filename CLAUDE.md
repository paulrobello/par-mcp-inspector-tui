# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A TUI application for inspecting and interacting with Model Context Protocol (MCP) servers. Features both terminal interface and CLI commands with real-time server notifications.

## Development Commands

### Essential Workflow
- `make checkall` - Format, lint, and type check (run after code changes)
- `uv run pmit tui` - Launch the TUI application
- `uv run pmit --help` - Show all available commands

### Testing & Development
- `uv run pmit servers` - List configured servers
- `uv run pmit debug <server-id> --verbose` - Debug server connections
- `uv run pmit connect <command> --verbose` - Connect to STDIO server
- `uv run pmit connect-tcp <host> <port> --verbose` - Connect to TCP server
- `uv run pmit download-resource <server> <resource>` - Download resources

### Package Management
- `uv sync` - Sync dependencies
- `uv add/remove <package>` - Manage dependencies
- `make setup` - Initial setup (uv lock + sync)

### Quality Tools
- `make format` / `make lint` / `make typecheck` - Individual tools
- `textual console` - TUI debugging console

## Architecture Overview

### Core Structure
- **models/**: MCP protocol data models (Pydantic-based)
- **client/**: MCP client implementations (STDIO/TCP transports)
- **services/**: Business logic layer (MCP service, server manager)
- **tui/**: Textual-based UI components and main application

### Key Components
- **Entry Point**: `par_mcp_inspector_tui.__main__:app` (Typer CLI)
- **Main App**: `tui/app.py` - MCPInspectorApp class
- **Configuration**: `~/.config/mcp-inspector/servers.yaml`

### Primary Dependencies
- `textual` - TUI framework
- `typer` - CLI framework
- `pydantic` - Data validation

## Development Guidance

### Code Standards
- Python 3.12+ with type annotations
- Use `uv` for package management
- Google-style docstrings
- Async-first architecture
- UTF-8 encoding for file operations

### TUI Development
- Use `@work` decorator for async MCP operations
- Service injection pattern for widgets
- Reactive state management
- Error handling via notification panel

### MCP Protocol
- STDIO and TCP transport support
- Server capability introspection
- Real-time server notification support

## Testing Notes
- Test with official MCP servers (filesystem, sqlite, everything)
- Verify both transport types (STDIO/TCP)
- Test error scenarios and connection failures
- Use `--verbose` flag for debugging
- Test server notifications with Everything server (sends notifications every 20 seconds)
- Test UI controls for toast notifications (add/edit server dialogs)

## Development Warnings
- Do not run the actual TUI application when working on code, as the user must do it to prevent terminal corruption. The other app cli commands are safe.
