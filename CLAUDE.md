# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

A TUI application for inspecting and interacting with Model Context Protocol (MCP) servers. Features terminal interface and CLI commands with real-time notifications, MCP roots support, and comprehensive raw MCP protocol interaction monitoring.

## Development Workflow

### Essential Commands
- `make checkall` - Format, lint, and type check (run after code changes)
- `uv run pmit tui` - Launch the TUI application  
- `uv run pmit --help` - Show all available commands

### Testing Commands
- `uv run pmit debug <server-id> --verbose` - Debug server connections
- `uv run pmit connect <command> --verbose` - Test arbitrary STDIO server
- `uv run pmit servers` - List configured servers

### Clipboard Commands
- `uv run pmit copy-config <server-id-or-name> --format <desktop|code>` - Copy server config to clipboard
- `uv run pmit copy-desktop <server-id-or-name>` - Copy server config for Claude Desktop
- `uv run pmit copy-code <server-id-or-name>` - Copy server config for Claude Code

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
- `tui/app.py` - Main TUI application with tabbed interface
- `tui/widgets/raw_interactions_view.py` - Raw MCP protocol interaction viewer
- `~/.config/par-mcp-inspector-tui/servers.yaml` - Server configuration

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
- Raw interactions are captured automatically via callback system
- New tabs require integration with service callback transfers

### TUI Features
- **Raw Interactions Tab**: Real-time MCP JSON-RPC message monitoring
  - Syntax highlighted JSON display
  - Regex search functionality
  - Sent/received message color coding
  - Chronological ordering with timestamps
  - Memory management (200 interaction limit)

## Testing Notes
- Test with official MCP servers (filesystem, sqlite, everything)
- Use `--verbose` flag for debugging
- Test both STDIO and HTTP transports
- Verify roots functionality with filesystem servers
- Test Raw Interactions tab with all server types
- Verify interaction capture works for both initial connection and ongoing operations

## Important Warnings
- Do not run the TUI application when working on code - it can corrupt the terminal. Use CLI commands for testing.
