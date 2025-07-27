# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

A TUI application for inspecting and interacting with Model Context Protocol (MCP) servers. Features terminal interface and CLI commands with real-time notifications and MCP roots support.

## Development Workflow

### Essential Commands
- `make checkall` - Format, lint, and type check (run after code changes)
- `uv run pmit tui` - Launch the TUI application  
- `uv run pmit --help` - Show all available commands

### Testing Commands
- `uv run pmit debug <server-id> --verbose` - Debug server connections
- `uv run pmit connect <command> --verbose` - Test arbitrary STDIO server
- `uv run pmit servers` - List configured servers

### Package Management
- `uv sync` - Sync dependencies
- `uv add/remove <package>` - Manage dependencies
- `make setup` - Initial setup

## Architecture

### Core Structure
- **models/**: Pydantic data models for MCP protocol
- **client/**: Transport implementations (STDIO/HTTP/TCP)
- **services/**: Business logic (MCP service, server manager)
- **tui/**: Textual UI components and main application

### Key Files
- `__main__.py` - CLI entry point
- `tui/app.py` - Main TUI application
- `~/.config/mcp-inspector/servers.yaml` - Server configuration

## Development Guidelines

### Code Standards
- Python 3.12+ with type annotations
- Use `uv` for package management
- Async-first architecture
- Google-style docstrings

### TUI Development
- Use `@work` decorator for async MCP operations
- Service injection pattern for widgets
- Error handling via notification panel

## Testing Notes
- Test with official MCP servers (filesystem, sqlite, everything)
- Use `--verbose` flag for debugging
- Test both STDIO and HTTP transports
- Verify roots functionality with filesystem servers

## Important Warnings
- Do not run the TUI application when working on code - it can corrupt the terminal. Use CLI commands for testing.
