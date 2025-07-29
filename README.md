# PAR MCP Inspector TUI

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
![Runs on Linux | MacOS | Windows](https://img.shields.io/badge/runs%20on-Linux%20%7C%20MacOS%20%7C%20Windows-blue)
![Arch x86-63 | ARM | AppleSilicon](https://img.shields.io/badge/arch-x86--64%20%7C%20ARM%20%7C%20AppleSilicon-blue)

![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-0.9.0-green.svg)
![Development Status](https://img.shields.io/badge/status-stable-green.svg)

A comprehensive Terminal User Interface (TUI) application for inspecting and interacting with Model Context Protocol (MCP) servers. This tool provides an intuitive interface to connect to MCP servers, explore their capabilities, and execute tools, prompts, and resources in real-time.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/probello3)

## Screenshots

![MCP Inspector TUI Interface](https://raw.githubusercontent.com/paulrobello/par-mcp-inspector-tui/main/Screenshot.png)

*The MCP Inspector TUI showing a connected "Everything" server with available tools (echo, add, printEnv), tool parameter forms, and real-time interaction logs. The interface displays server management on the left, tabbed content areas in the center, and notifications on the right.*

![MCP Inspector TUI Raw Interactions](https://raw.githubusercontent.com/paulrobello/par-mcp-inspector-tui/main/Screenshot2.png)

*The Raw Interactions tab displaying real-time MCP JSON-RPC protocol messages with syntax highlighting, showing both sent (green) and received (blue) messages with timestamps and comprehensive protocol monitoring capabilities.*

## 🆕 What's New in v0.9.0

**🔍 Enhanced Connect Commands**: Added `--debug-dump` flag to all connect commands for comprehensive server debugging.

- **New `--debug-dump` Flag**: Available for `connect`, `connect-tcp`, and `connect-http` commands
- **Full Debug Analysis**: Performs complete server inspection like the `debug` command (lists tools, resources, prompts)
- **Flexible Testing**: Connect to any MCP server with or without full debug output
- **Convenient Short Flag**: Use `-D` for quick debug dumps
- **Consistent Interface**: Same debug output format across all connect commands

Examples:
```shell
# Connect with full debug dump
pmit connect npx -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" --debug-dump

# Quick debug dump with short flag
pmit connect-tcp localhost 3333 -D

# HTTP server with debug analysis
pmit connect-http https://api.example.com/mcp --debug-dump --verbose
```

## What's New in v0.6.0

**🔧 Bug Fix**: Fixed missing PyYAML dependency that was causing installation issues.

## What's New in v0.5.0

**🔍 Raw Interactions Tab** - The most requested feature is here! Get complete visibility into MCP JSON-RPC protocol communications:
- **Real-time Protocol Monitoring**: See every message sent and received between client and server
- **Rich JSON Display**: Syntax-highlighted JSON with color-coded message direction
- **Advanced Search**: Regex pattern matching across entire message content for powerful debugging
- **Universal Compatibility**: Works with all MCP servers (STDIO, HTTP, filesystem, etc.)
- **Developer Essential**: Perfect for MCP server development, debugging, and protocol analysis

**🎨 Smart Content Detection & Viewers** - Tool results now automatically use appropriate viewers based on content type:
- **Intelligent Detection**: Automatically detects content type from file extensions, MIME types, and content patterns
- **Markdown Rendering**: `.md` files display with proper formatting, headers, lists, and code blocks
- **Syntax Highlighting**: Code files (.py, .js, .ts, .html, .css, etc.) get language-specific highlighting
- **JSON Pretty-Printing**: JSON responses are automatically formatted with syntax highlighting
- **File Location Integration**: File path display with copy button and Ctrl+O quick-open functionality
- **20+ Languages Supported**: Python, JavaScript, TypeScript, HTML, CSS, YAML, TOML, and more

**Plus**: Enhanced clipboard integration, improved search functionality, and critical bug fixes for filesystem servers.

[📖 See full changelog](#changelog) for complete details.

## Features

- **Multiple Transport Support**: Connect to MCP servers via STDIO and HTTP+SSE
- **MCP Roots Support**: Full implementation of MCP filesystem roots protocol with TUI and CLI management
- **Raw Interactions Monitoring**: Real-time display of all MCP JSON-RPC protocol messages with syntax highlighting
- **Smart Content Detection**: Automatic content type detection and appropriate viewer selection for tool results
- **Enhanced Tool Results Display**: File location headers with copy buttons and Ctrl+O quick-open functionality
- **Multi-Language Syntax Highlighting**: Support for 20+ programming languages and file formats
- **Intelligent Markdown Rendering**: Automatic detection and rich rendering of Markdown content
- **CLI Debugging Tools**: Connect to arbitrary servers and inspect interactions without configuration
- **Resource Download CLI**: Download resources by name with automatic file type detection
- **Real-time Introspection**: Discover tools, prompts, and resources from connected servers
- **Dynamic Forms**: Automatically generated forms based on server-provided schemas with real-time validation
- **Form Validation**: Smart execute button control - disabled until all required fields are filled
- **Magic Number Detection**: Automatic file type detection using magic numbers for binary resources
- **Advanced Content Viewers**: JSON pretty-printing, code syntax highlighting, and markdown rendering
- **Regex Search**: Real-time filtering of MCP responses and raw interactions with regex pattern matching
- **File Management**: Save and open resources with proper file extensions and MIME type handling
- **Server Management**: Persistent configuration storage for multiple server connections
- **Non-blocking Operations**: Async communication ensuring responsive UI
- **Server Notifications**: Real-time notifications from MCP servers with auto-refresh capabilities
- **Application Notifications**: Real-time status updates and error handling
- **Tab Auto-clearing**: Automatically clears all tabs when disconnecting from servers
- **Capability-aware**: Gracefully handles servers with partial MCP implementation

## Technology Stack
- **Python 3.11+** - Modern Python with latest features
- **FastMCP** - High-performance Model Context Protocol implementation with robust transport layer
- **Textual** - Beautiful, responsive terminal user interfaces
- **Pydantic** - Data validation and serialization
- **Rich** - Terminal output formatting and syntax highlighting
- **filetype** - Magic number file type detection
- **YAML** - Configuration file format
- **Asyncio** - Asynchronous programming for responsive interfaces

## Prerequisites

To install PAR MCP Inspector TUI, make sure you have Python 3.11+.

### [uv](https://pypi.org/project/uv/) is recommended

#### Linux and Mac
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Installation

### Installation from PyPI (Recommended)

Install the latest stable version using uv:

```bash
uv tool install par-mcp-inspector-tui
```

Or using pip:

```bash
pip install par-mcp-inspector-tui
```

After installation, you can run the tool directly:

```bash
# Launch the TUI application
pmit tui

# Show all available commands
pmit --help
```

### Installation From Source

For development or to get the latest features:

1. Clone the repository:
   ```bash
   git clone https://github.com/paulrobello/par-mcp-inspector-tui.git
   cd par-mcp-inspector-tui
   ```

2. Install the package dependencies using uv:
   ```bash
   uv sync
   ```

3. Run using uv:
   ```bash
   uv run pmit tui
   ```

## Usage

### CLI Commands Overview

If installed from PyPI:
```shell
# Show all available commands
pmit --help

# Show version information
pmit --version

# Launch the TUI application
pmit tui

# Launch TUI with debug mode
pmit tui --debug

# List configured servers
pmit servers

# Debug a configured server
pmit debug <server-id> --verbose

# Connect to arbitrary STDIO server
pmit connect npx --arg "-y" --arg "@modelcontextprotocol/server-filesystem" --arg "/tmp"

# Connect with debug dump for full server analysis
pmit connect npx --arg "-y" --arg "@modelcontextprotocol/server-filesystem" --arg "/tmp" --debug-dump

# Connect to arbitrary TCP server
pmit connect-tcp localhost 3333

# Connect to TCP server with debug dump
pmit connect-tcp localhost 3333 --debug-dump

# Download resources from servers
pmit download-resource <server-id> <resource-name>

# Manage filesystem roots for servers
pmit roots-list [server-id]
pmit roots-add <server-id> <path>
pmit roots-remove <server-id> <path>

# Copy server configurations to clipboard
pmit copy-config <server-id-or-name> [--format desktop|code]
pmit copy-desktop <server-id-or-name>
pmit copy-code <server-id-or-name>
```

If running from source:
```shell
# Show all available commands
uv run pmit --help

# Show version information
uv run pmit --version

# Launch the TUI application
uv run pmit tui

# Launch TUI with debug mode
uv run pmit tui --debug

# List configured servers
uv run pmit servers

# Debug a configured server
uv run pmit debug <server-id> --verbose

# Connect to arbitrary STDIO server
uv run pmit connect npx --arg "-y" --arg "@modelcontextprotocol/server-filesystem" --arg "/tmp"

# Connect to arbitrary TCP server
uv run pmit connect-tcp localhost 3333

# Download resources from servers
uv run pmit download-resource <server-id> <resource-name>

# Manage filesystem roots for servers
uv run pmit roots-list [server-id]
uv run pmit roots-add <server-id> <path>
uv run pmit roots-remove <server-id> <path>

# Copy server configurations to clipboard
uv run pmit copy-config <server-id-or-name> [--format desktop|code]
uv run pmit copy-desktop <server-id-or-name>
uv run pmit copy-code <server-id-or-name>
```

### TUI Application

```shell
# Start the MCP Inspector TUI (if installed from PyPI)
pmit tui

# Enable debug mode for troubleshooting
pmit tui --debug

# If running from source
uv run pmit tui
uv run pmit tui --debug
```

**Options:**
- `--debug -d`: Enable debug mode for detailed logging and troubleshooting

### First Time Setup

1. **Launch the application**: `pmit tui` (or `uv run pmit tui` if running from source)
2. **Default servers**: The application comes with working example server configurations:
   - **Example STDIO Server**: Filesystem server for `/tmp` directory
   - **Everything**: Comprehensive test server with tools, resources, and notifications
3. **Add your servers**: Use the "Add Server" button to configure your MCP servers
4. **Connect**: Select a server from the list and click "Connect"
5. **Explore**: Browse resources, prompts, and tools in the tabbed interface

### Quick Testing without Configuration

Test any MCP server instantly without adding it to configuration:

```shell
# Test a filesystem server
uv run pmit connect npx \
  --arg "-y" \
  --arg "@modelcontextprotocol/server-filesystem" \
  --arg "/tmp" \
  --name "My Test Server" \
  --verbose

# Test with environment variables
uv run pmit connect python \
  --arg "my_server.py" \
  --env "DEBUG=1" \
  --env "DATABASE_URL=sqlite:///test.db"

# Test TCP server
uv run pmit connect-tcp myhost.com 8080 --verbose
```

## CLI Commands Reference

### Global Options
- `--version -v`: Show version and exit
- `--help`: Show help message and exit

### `tui` - Launch TUI Application
```shell
# If installed from PyPI
pmit tui [OPTIONS]

# If running from source
uv run pmit tui [OPTIONS]
```

**Options:**
- `--debug -d`: Enable debug mode for detailed logging and troubleshooting

### `servers` - List Configured Servers
```shell
# If installed from PyPI
pmit servers

# If running from source
uv run pmit servers
```
Shows a formatted table of all configured MCP servers with their connection details and status.

### `debug` - Debug Configured Server
```shell
# If installed from PyPI
pmit debug <server-id-or-name> [OPTIONS]

# If running from source
uv run pmit debug <server-id-or-name> [OPTIONS]
```

**Arguments:**
- `server-id-or-name`: Server ID or name to debug (required)

**Options:**
- `--verbose -v`: Verbose output with raw JSON
- `--debug`: Enable debug logging of MCP messages

Connect to a pre-configured server and test all MCP endpoints:
- Shows server information and capabilities
- Tests resources, tools, and prompts endpoints with enhanced display
- **Enhanced Resource Display**: Color-coded labels and ready-to-use download commands
- Displays detailed error information
- Use `--verbose` for raw JSON responses
- Use `--debug` for detailed MCP message logging

**Enhanced Resource Display Features:**
- **Resource Names**: Clearly highlighted for use with `download-resource` command
- **Download Instructions**: Exact command syntax for configured servers
- **Color-Coded Output**: Green names, cyan URIs, yellow descriptions, magenta MIME types
- **Smart Guidance**: Different messages for configured vs temporary servers

### `connect` - Connect to Arbitrary STDIO Server
```shell
# If installed from PyPI
pmit connect <command> [OPTIONS]

# If running from source
uv run pmit connect <command> [OPTIONS]
```

**Arguments:**
- `command`: Command to execute for STDIO transport (required)

**Options:**
- `--arg -a`: Command arguments (can be specified multiple times)
- `--env -e`: Environment variables in KEY=VALUE format (can be specified multiple times)
- `--verbose -v`: Verbose output with raw JSON
- `--debug`: Enable debug logging of MCP messages
- `--debug-dump -D`: Perform debug dump like the debug command (lists tools, resources, prompts)
- `--name -n`: Server name for display (default: Ad-hoc Server)

Connect to an arbitrary STDIO server without adding it to configuration. With `--debug-dump`, uses the same enhanced debug output as the `debug` command, including:
- **Color-coded resource display** with download guidance  
- **Smart messaging**: Informs users to add server to configuration before downloading resources
- **Full MCP testing**: Resources, tools, and prompts endpoints
- **Flexible Output**: Basic connection info without `--debug-dump`, full analysis with it

**Examples:**
```shell
# Basic usage (PyPI installation)
pmit connect npx -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp"

# With environment variables and custom name
pmit connect python -a "server.py" -e "DEBUG=1" -e "PORT=8080" -n "My Server"

# Verbose output with debug logging
pmit connect node -a "server.js" --verbose --debug

# With debug dump for full server analysis
pmit connect node -a "server.js" --debug-dump --verbose

# From source
uv run pmit connect npx -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp"
```

### `connect-tcp` - Connect to Arbitrary TCP Server
```shell
# If installed from PyPI
pmit connect-tcp [HOST] [PORT] [OPTIONS]

# If running from source
uv run pmit connect-tcp [HOST] [PORT] [OPTIONS]
```

**Arguments:**
- `host`: Host to connect to (default: localhost)
- `port`: Port to connect to (default: 3333)

**Options:**
- `--verbose -v`: Verbose output with raw JSON
- `--debug`: Enable debug logging of MCP messages
- `--debug-dump -D`: Perform debug dump like the debug command (lists tools, resources, prompts)
- `--name -n`: Server name for display (default: TCP Server)

Connect to an arbitrary TCP server without adding it to configuration. With `--debug-dump`, uses the same enhanced debug output as other debug commands, including:
- **Enhanced resource listing** with color-coded display
- **Download guidance**: Instructions to add server to configuration first
- **Complete testing**: All MCP endpoints (resources, tools, prompts)
- **Flexible Output**: Basic connection info without `--debug-dump`, full analysis with it

**Examples:**
```shell
# Default host and port (PyPI installation)
pmit connect-tcp

# Custom host and port with verbose and debug output
pmit connect-tcp example.com 8080 -n "Remote Server" --verbose --debug

# With debug dump for comprehensive analysis
pmit connect-tcp example.com 8080 -n "Remote Server" --debug-dump

# From source
uv run pmit connect-tcp
uv run pmit connect-tcp example.com 8080 -n "Remote Server" --verbose --debug
```

### `download-resource` - Download Resources by Name
```shell
# If installed from PyPI
pmit download-resource <server-id-or-name> <resource-name> [OPTIONS]

# If running from source
uv run pmit download-resource <server-id-or-name> <resource-name> [OPTIONS]
```

**Arguments:**
- `server-id-or-name`: Server ID or name to download from (required)
- `resource-name`: Resource name to download (required)

**Options:**
- `--output -o`: Output directory (default: current directory)
- `--filename -f`: Custom filename (default: auto-detect from resource)
- `--verbose -v`: Verbose output with detailed information
- `--debug`: Enable debug logging of MCP messages

**Features:**
- **Smart Resource Finding**: Exact name match, case-insensitive fallback, and partial matching
- **Automatic File Type Detection**: Uses MIME types and magic number detection for proper extensions
- **Custom Output**: Specify output directory and custom filenames
- **Error Handling**: Clear error messages for missing servers/resources

**Examples:**
```shell
# Download resource with auto-detection (PyPI installation)
pmit download-resource Everything "Resource 1"

# Custom output directory
pmit download-resource filesystem-server "config.json" --output ~/Downloads

# Custom filename with verbose output
pmit download-resource Everything "Resource 2" --filename my-file.txt --verbose

# Download binary resource (automatic type detection)
pmit download-resource image-server "logo.png" --output ./assets

# From source
uv run pmit download-resource Everything "Resource 1"
```

### `roots-list` - List Filesystem Roots
```shell
# If installed from PyPI
pmit roots-list [SERVER_ID] [OPTIONS]

# If running from source
uv run pmit roots-list [SERVER_ID] [OPTIONS]
```

**Arguments:**
- `server-id`: Server ID (optional - uses current connected server if not specified)

**Options:**
- `--verbose -v`: Show detailed root information including path validation and type

**Features:**
- **Automatic Server Detection**: If no server ID provided, uses the currently connected server
- **Path Validation**: Shows ✓ for existing paths, ✗ for missing paths
- **Type Detection**: Displays whether paths are directories or files (with `--verbose`)
- **URI Support**: Handles both local paths and `file://` URIs
- **Clear Display**: Numbered list with status indicators

**Examples:**
```shell
# List roots for connected server (PyPI installation)
pmit roots-list

# List roots for specific server with details
pmit roots-list my-server-id --verbose

# From source
uv run pmit roots-list
uv run pmit roots-list my-server-id --verbose
```

### `roots-add` - Add Filesystem Root
```shell
# If installed from PyPI
pmit roots-add <server-id> <path> [OPTIONS]

# If running from source
uv run pmit roots-add <server-id> <path> [OPTIONS]
```

**Arguments:**
- `server-id`: Server ID (required)
- `path`: Filesystem path or `file://` URI to add as root (required)

**Options:**
- `--name -n`: Display name for the root (used in TUI interface)

**Features:**
- **Automatic URI Conversion**: Converts local paths to proper `file://` URIs
- **Duplicate Prevention**: Prevents adding the same root path multiple times
- **Path Resolution**: Automatically resolves relative paths to absolute paths
- **Persistent Storage**: Saves roots to server configuration immediately
- **Display Name Support**: Optional display names for better TUI presentation

**Examples:**
```shell
# Add current directory as root (PyPI installation)
pmit roots-add my-server-id . --name "Project Root"

# Add absolute path
pmit roots-add my-server-id /home/user/documents

# Add with file:// URI
pmit roots-add my-server-id file:///tmp/workspace --name "Workspace"

# From source
uv run pmit roots-add my-server-id . --name "Project Root"
uv run pmit roots-add my-server-id /home/user/documents
```

### `roots-remove` - Remove Filesystem Root
```shell
# If installed from PyPI
pmit roots-remove <server-id> <path>

# If running from source
uv run pmit roots-remove <server-id> <path>
```

**Arguments:**
- `server-id`: Server ID (required)
- `path`: Filesystem path or `file://` URI to remove (required)

**Features:**
- **Flexible Path Matching**: Accepts both local paths and `file://` URIs
- **Automatic URI Conversion**: Converts local paths to URIs for matching
- **Path Resolution**: Resolves relative paths to match stored absolute paths
- **Not Found Handling**: Shows available roots if specified path not found
- **Immediate Persistence**: Updates server configuration immediately

**Examples:**
```shell
# Remove by local path (PyPI installation)
pmit roots-remove my-server-id /tmp/workspace

# Remove by file:// URI
pmit roots-remove my-server-id file:///home/user/documents

# Remove relative path (resolved automatically)
pmit roots-remove my-server-id ../parent-dir

# From source
uv run pmit roots-remove my-server-id /tmp/workspace
uv run pmit roots-remove my-server-id file:///home/user/documents
```

### `copy-config` - Copy Server Configuration (Universal)
```shell
# If installed from PyPI
pmit copy-config <server-id-or-name> [OPTIONS]

# If running from source
uv run pmit copy-config <server-id-or-name> [OPTIONS]
```

**Arguments:**
- `server-id-or-name`: Server ID or name to copy configuration for (required)

**Options:**
- `--format -f`: Config format (desktop|code) - default: desktop

**Features:**
- **Dual Format Support**: Copy configurations for Claude Desktop or Claude Code
- **Server Lookup**: Accepts both server ID and server name (case-insensitive)
- **Error Handling**: Shows available servers if specified server not found
- **Preview Output**: Shows copied content when run in terminal
- **Format Shortcuts**: Supports "d" for desktop and "c" for code

**Examples:**
```shell
# Copy for Claude Desktop (default format) - PyPI installation
pmit copy-config "Example STDIO Server"

# Copy for Claude Code using format option
pmit copy-config "filesystem-server" --format code

# Use format shortcuts
pmit copy-config "Everything" -f c

# Use server ID instead of name
pmit copy-config a49a17c3-a91c-4757-8ec8-effa589fffa1 --format desktop

# From source
uv run pmit copy-config "Example STDIO Server"
uv run pmit copy-config "filesystem-server" --format code
```

### `copy-desktop` - Copy Claude Desktop Configuration
```shell
# If installed from PyPI
pmit copy-desktop <server-id-or-name>

# If running from source
uv run pmit copy-desktop <server-id-or-name>
```

**Arguments:**
- `server-id-or-name`: Server ID or name to copy configuration for (required)

**Features:**
- **Claude Desktop Format**: Generates config.json format for Claude Desktop MCP configuration
- **Complete Transport Support**: Handles STDIO, TCP, and HTTP transport configurations
- **Environment Variables**: Includes all environment variables and command arguments
- **Immediate Clipboard**: Automatically copies to system clipboard
- **Preview Display**: Shows the copied JSON configuration in terminal

**Examples:**
```shell
# Copy STDIO server config for Claude Desktop - PyPI installation
pmit copy-desktop "Example STDIO Server"

# Copy HTTP server config using server ID
pmit copy-desktop 47221007-90ba-4c6f-8dce-a5167f819309

# From source
uv run pmit copy-desktop "Example STDIO Server"
uv run pmit copy-desktop "Everything"
```

**Output Format:**
```json
{
  "Example STDIO Server": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
    "env": {
      "NODE_ENV": "production"
    }
  }
}
```

### `copy-code` - Copy Claude Code MCP Add Command
```shell
# If installed from PyPI
pmit copy-code <server-id-or-name>

# If running from source
uv run pmit copy-code <server-id-or-name>
```

**Arguments:**
- `server-id-or-name`: Server ID or name to copy configuration for (required)

**Features:**
- **Claude Code Format**: Generates `claude mcp add` command syntax
- **STDIO Support**: Full support for STDIO transport with command and arguments
- **Transport Limitations**: Shows helpful comments for TCP/HTTP transports (not directly supported)
- **Ready to Execute**: Command can be run directly in terminal
- **Complete Syntax**: Includes server name, command, and all arguments

**Examples:**
```shell
# Copy MCP add command for Claude Code - PyPI installation
pmit copy-code "Example STDIO Server"

# Copy using server ID
pmit copy-code 90ab905f-dc7c-48f1-8696-5b43a609d549

# From source
uv run pmit copy-code "Example STDIO Server"
uv run pmit copy-code "Everything"
```

**Output Format:**
```shell
# For STDIO servers
claude mcp add "Example STDIO Server" -- npx -y @modelcontextprotocol/server-filesystem /tmp

# For TCP servers (with helpful comments)
claude mcp add "TCP Server" -- # TCP transport not directly supported in claude mcp add # Host: localhost # Port: 3333

# For HTTP servers (with helpful comments)  
claude mcp add "HTTP Server" -- # HTTP transport not directly supported in claude mcp add # URL: https://api.example.com/mcp
```

## Server Configuration

The TUI application stores server configurations in `~/.config/par-mcp-inspector-tui/servers.yaml`. Example configuration:

```yaml
servers:
  filesystem-server:
    name: "Filesystem Server"
    transport: "stdio"
    command: "npx"
    args:
      - "-y"
      - "@modelcontextprotocol/server-filesystem"
      - "/tmp"
    env:
      NODE_ENV: "production"
    toast_notifications: true  # Show toast notifications (default: true)
    roots:  # MCP filesystem roots (optional)
      - "file:///tmp"
      - "file:///home/user/documents"
      - "file:///var/log"

  http-mcp-server:
    name: "HTTP MCP Server"
    transport: "http"
    url: "https://api.example.com/mcp"
    toast_notifications: true  # Show toast notifications for this server
    roots:  # Roots can be specified for any transport type
      - "file:///workspace/project"
      - "file:///shared/resources"
```

#### Configuration Options

- **toast_notifications** (boolean, default: true): Controls whether to show toast popup notifications when the server sends notifications. When `false`, notifications are still added to the notifications tab but won't show as toast popups. Note: Toasts are automatically suppressed when viewing the notifications tab regardless of this setting.

- **roots** (array of strings, optional): List of filesystem roots that define the boundaries of filesystem access for MCP servers. Each root should be a `file://` URI pointing to a directory or file. These roots are sent to the server during connection to establish filesystem boundaries according to the MCP roots protocol. Roots can be managed through the TUI interface (Roots tab) or via CLI commands (`roots-add`, `roots-remove`, `roots-list`).

#### UI Configuration

You can configure toast notifications through the TUI interface:

1. **Add Server Dialog**: When adding a new server, check/uncheck "Show toast notifications from this server"
2. **Edit Server Dialog**: Select any server and click "Edit Server" to modify the toast notification setting
3. **Per-Server Control**: Each server has different notification settings
4. **Real-time Updates**: Changes take effect immediately after saving

### Supported Transport Types

#### STDIO Transport (Recommended)
For servers that communicate via standard input/output (most common):
```yaml
servers:
  my-stdio-server:
    name: "My STDIO Server"
    transport: "stdio"
    command: "python"
    args:
      - "server.py"
    env:
      DEBUG: "1"
```

#### HTTP Transport
For HTTP-based MCP servers with SSE (Server-Sent Events) support:
```yaml
servers:
  my-http-server:
    name: "My HTTP MCP Server"
    transport: "http"
    url: "https://api.example.com/mcp"
```

#### TCP Transport (Legacy HTTP+SSE)
For backward compatibility with HTTP-based MCP servers:
```yaml
servers:
  my-tcp-server:
    name: "My TCP Server"
    transport: "tcp"
    host: "localhost"
    port: 8080
```

**Important Notes**:
- **STDIO transport** is recommended for most MCP servers (filesystem, everything, etc.)
- **HTTP transport** is for servers with full HTTP URLs
- **TCP transport** actually uses HTTP+SSE protocol, not raw TCP sockets
- Use HTTP/TCP transports only for servers that explicitly support HTTP+SSE protocol

## User Interface

### Main Layout
- **Docked Server Panel**: Toggleable left sidebar for server management
  - **Docked Position**: Anchored to the left side of the interface  
  - **Toggle Control**: Press `p` to show/hide the panel
  - **Default State**: Opens visible by default
  - **Contents**: Server list and connection status
  - **Persistent Functionality**: All server management features remain available when hidden/shown
- **Center Panel**: Tabbed interface with:
  - **Resources**: Browse and read available resources
  - **Prompts**: Execute prompts with dynamic argument forms and validation
  - **Tools**: Call tools with smart parameter validation and form controls
  - **Roots**: Manage filesystem roots for MCP server access boundaries
  - **Raw Interactions**: Real-time display of MCP JSON-RPC protocol messages with syntax highlighting and regex search
  - **Notifications**: Real-time server notifications with auto-refresh capabilities
- **Right Panel**: Response viewer with formatted output and syntax highlighting

### Form Validation Features
- **Required Field Indicators**: Red asterisks (*) mark required parameters
- **Smart Execute Button**: Automatically disabled when required fields are empty
- **Real-time Validation**: Button state updates as you type in form fields
- **Array Field Support**: Add/remove dynamic list items with validation
- **Multiple Field Types**: Text, number, checkbox, select, and array inputs

### Server Notifications Features
- **Real-time Updates**: Receive notifications from MCP servers as they happen
- **Auto-refresh**: Automatically refresh tools, resources, and prompts when server lists change
- **Server Context**: Each notification shows which server sent it
- **Message Types**: Supports different notification types:
  - `notifications/tools/list_changed` - Tools list has changed
  - `notifications/resources/list_changed` - Resources list has changed  
  - `notifications/prompts/list_changed` - Prompts list has changed
  - `notifications/message` - General server messages with level indicators
- **Visual Distinction**: Server notifications have unique styling and icons (🔔)
- **Chronological Order**: Newest notifications appear at the top
- **Notification History**: View complete history of server communications
- **Toast Control**: Per-server configuration for toast popup notifications
  - Enable/disable through Add/Edit Server dialogs
  - Automatic suppression when viewing notifications tab
  - Real-time configuration updates without restart

### Filesystem Roots Management

The **Roots** tab provides comprehensive management of filesystem boundaries for MCP servers:

**Root Management Features:**
- **Add New Roots**: Click "Add Root" to add filesystem paths or `file://` URIs
- **Remove Roots**: Select roots and click "Remove Root" to delete them
- **Path Validation**: Real-time status indicators show if root paths exist (✓/✗)
- **Type Display**: Shows whether roots are directories, files, or URIs
- **Server Integration**: Roots are automatically sent to servers during connection
- **Persistent Storage**: Root configurations are saved with server settings

**Root Display Format:**
- **Status Indicator**: ✓ (exists), ✗ (missing), or ? (unknown)
- **Path Information**: Shows the full `file://` URI or local path
- **Type Information**: (directory), (file), or (URI) designations
- **Organized List**: Clean, numbered display of all configured roots

**MCP Protocol Integration:**
- **Automatic Transmission**: Roots are sent to servers during connection establishment
- **Protocol Compliance**: Implements MCP `roots/list` protocol specification
- **Boundary Enforcement**: Servers use roots to restrict filesystem access
- **Notification Support**: Responds to `notifications/roots/list_changed` from servers

### Raw Interactions Monitoring

The **Raw Interactions** tab provides comprehensive monitoring of all MCP JSON-RPC protocol messages:

**Interaction Display Features:**
- **Real-time Capture**: Automatically captures all sent and received messages during server communication
- **Syntax Highlighting**: Rich JSON formatting with color-coded syntax highlighting
- **Message Direction**: Visual distinction between sent (green theme) and received (blue theme) messages
- **Timestamps**: Precise timestamps (HH:MM:SS.ms) for each interaction
- **Chronological Order**: Newest interactions appear at the top

**Search and Filtering:**
- **Regex Search**: Real-time filtering with regex pattern matching
- **Full-text Search**: Search across entire JSON message content
- **Graceful Fallback**: Invalid regex patterns fall back to simple string search
- **Pattern Highlighting**: Search matches are highlighted within the JSON content

**Technical Features:**
- **Memory Management**: Automatically limits to 200 interactions to prevent memory issues
- **Performance Optimized**: Efficient display updates without blocking the UI
- **Error Handling**: Graceful handling of malformed JSON or connection issues
- **Protocol Coverage**: Captures all MCP operations including:
  - Connection handshake and initialization
  - Resource/tool/prompt listing operations
  - Tool execution and resource reading
  - Server notifications and responses
  - Error messages and protocol exceptions

**Use Cases:**
- **Protocol Debugging**: Understand exactly what messages are being exchanged
- **Server Development**: Validate MCP server implementations
- **Performance Analysis**: Monitor response times and message patterns
- **Troubleshooting**: Identify communication issues between client and server

### Server Management

#### Add/Edit Server Dialog

The server configuration dialog provides comprehensive settings for MCP servers:

**Basic Configuration:**
- **Server Name**: Descriptive name for identification
- **Transport Type**: Choose between STDIO or TCP communication

**STDIO Transport Settings:**
- **Command**: Executable command (e.g., `python`, `npx`, `node`)
- **Arguments**: Command-line arguments (one per line)
- **Environment Variables**: KEY=value pairs (one per line)

**HTTP Transport Settings:**
- **URL**: Complete HTTP/HTTPS URL to the MCP server endpoint

**TCP Transport Settings (Legacy):**
- **Host**: Server hostname or IP address  
- **Port**: Network port number (1-65535)

**Notification Settings:**
- **Toast Notifications Checkbox**: Control popup notifications for this server
  - ✅ **Checked (default)**: Display toast popups + notifications tab
  - ❌ **Unchecked**: Notifications tab only (quiet mode)
  - 🎯 **Smart Behavior**: Toasts auto-suppressed when viewing notifications tab

**Dialog Features:**
- Real-time form validation with helpful error messages
- Dynamic sections based on transport type selection
- Persistent settings with immediate effect after save
- Maintains UI selection state after edits

### Keyboard Shortcuts
- `q` - Quit application
- `d` - Toggle dark/light mode
- `s` - Focus server panel (when visible)
- `p` - Toggle server panel visibility
- `r` - Refresh server data
- `Ctrl+O` - Open last saved resource file (when viewing resources)

## Testing with MCP Servers

### Example Servers for Testing

Test these official MCP servers using the CLI commands:

1. **Filesystem Server**:
   ```shell
   # Using CLI connect (PyPI installation)
   pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" \
     --verbose

   # From source
   uv run pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp" \
     --verbose

   # Direct command for reference
   npx -y @modelcontextprotocol/server-filesystem /tmp
   ```

2. **SQLite Server**:
   ```shell
   # Using CLI connect (PyPI installation)
   pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-sqlite" \
     -a "--db-path" -a "test.db" \
     --verbose

   # From source
   uv run pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-sqlite" \
     -a "--db-path" -a "test.db" \
     --verbose

   # Direct command for reference
   npx -y @modelcontextprotocol/server-sqlite --db-path test.db
   ```

3. **Custom Python Server**:
   ```shell
   # Test your custom server (PyPI installation)
   pmit connect python \
     -a "my_mcp_server.py" \
     -e "DATABASE_URL=sqlite:///data.db" \
     -n "My Custom Server" \
     --verbose

   # From source
   uv run pmit connect python \
     -a "my_mcp_server.py" \
     -e "DATABASE_URL=sqlite:///data.db" \
     -n "My Custom Server" \
     --verbose
   ```

4. **GitHub MCP Server**:
   ```shell
   # Test GitHub integration server (PyPI installation)
   pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-github" \
     -e "GITHUB_PERSONAL_ACCESS_TOKEN=your_token" \
     --verbose

   # From source
   uv run pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-github" \
     -e "GITHUB_PERSONAL_ACCESS_TOKEN=your_token" \
     --verbose
   ```

5. **Everything Server (for testing notifications)**:
   ```shell
   # Test server that sends regular notifications (PyPI installation)
   pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-everything" \
     --verbose

   # From source
   uv run pmit connect npx \
     -a "-y" -a "@modelcontextprotocol/server-everything" \
     --verbose
   ```
   This server sends `notifications/message` every 20 seconds, perfect for testing the notification system.

### Server Capability Testing

The CLI commands automatically test server capabilities with enhanced display formatting:

#### Enhanced Resource Display
- **Color-Coded Labels**: Green names, cyan URIs, yellow descriptions, magenta MIME types
- **Download Ready**: Shows exact `download-resource` commands for configured servers
- **Smart Guidance**: Different messages for configured vs temporary servers

Example output for configured servers:
```
Testing Resources:
Found 3 resources:
Use 'download-resource my-server-id "<resource-name>"' to download any resource

  1. Name: config.json
     URI: file:///path/to/config.json
     Description: Application configuration file
     MIME Type: application/json

  2. Name: logo.png
     URI: file:///path/to/logo.png
     MIME Type: image/png
```

#### Standard Testing Features
- **Server Info**: Name, version, protocol version
- **Tools**: Available tools with parameter schemas  
- **Prompts**: Available prompts with argument definitions
- **Error Handling**: Timeouts and capability-based filtering

Use `--verbose` flag to see raw JSON responses and detailed debugging information.

## Changelog

### v0.9.0 - Enhanced Connect Commands with Debug Dump
- **🔍 New `--debug-dump` Flag**: Added comprehensive debug analysis to all connect commands
  - Available for `connect`, `connect-tcp`, and `connect-http` commands
  - Performs same complete server inspection as `debug` command
  - Lists tools, resources, and prompts with enhanced color-coded display
  - Provides flexible testing options (basic connection vs full debug analysis)
  - Short flag `-D` available for convenience
  - Consistent debug output format across all connect commands
- **📖 Documentation Updates**: Updated README and CLAUDE.md with new command examples
- **🧪 Enhanced Testing**: Better support for arbitrary server testing and analysis

### v0.8.0 - Fixed Claude Code Command Format
- **🔧 Bug Fix**: Fixed server copy commands for Claude Code to use correct `claude` command instead of `claude-code`
  - Updated CLI copy commands to generate proper `claude mcp add` syntax
  - Fixed TUI dialog copy functionality
  - Updated documentation examples

### v0.7.0 - Scroll Bar Bug Fix
- **🔧 Bug Fix**: Fixed scroll bar for long tool parameter lists in the TUI interface
  - Resolved scrolling issues when tool parameter forms exceed the visible area
  - Improved usability for tools with many parameters or long parameter descriptions
  - Enhanced form navigation and parameter accessibility

### v0.6.0 - PyYAML Dependency Fix
- **🔧 Bug Fix**: Fixed missing PyYAML dependency that was causing installation issues

### v0.5.0 - Raw Interactions Monitoring, Smart Content Detection & Configuration Export
- **🔍 Raw Interactions Tab**: Brand new tab for comprehensive MCP JSON-RPC protocol monitoring
  - Real-time capture and display of all sent and received MCP messages
  - Rich JSON syntax highlighting with color-coded message direction (green=sent, blue=received)
  - Precise timestamps (HH:MM:SS.ms) with chronological ordering (newest first)
  - Memory management with automatic limiting to 200 interactions for performance
  - Universal compatibility with all MCP servers and transport types
- **🔎 Advanced Interaction Search**: Powerful regex search functionality for protocol debugging
  - Real-time regex pattern matching across entire JSON message content
  - Full-text search with graceful fallback for invalid regex patterns
  - Essential tool for MCP server development and troubleshooting
- **🎨 Smart Content Detection & Viewers**: Revolutionary automatic content type detection for tool results
  - **Multi-Strategy Detection**: File extension analysis, MIME type mapping, and content pattern recognition
  - **Intelligent Markdown Rendering**: Automatic detection and rich rendering of `.md` files with headers, lists, code blocks, and formatting
  - **Advanced Syntax Highlighting**: 20+ programming languages including Python, JavaScript, TypeScript, HTML, CSS, YAML, TOML, SQL, Bash, and more
  - **JSON Pretty-Printing**: Automatic detection and beautiful formatting of JSON responses
  - **File Integration**: Seamless file location headers with copy buttons and Ctrl+O quick-open functionality
  - **Content Pattern Analysis**: Smart detection even without file extensions using content structure analysis
- **📁 Enhanced Tool Results Display**: Complete file management integration for tool outputs
  - File location display with one-click copy to clipboard functionality
  - Ctrl+O keyboard shortcut for instant file opening with default applications
  - Clean separation of file metadata from content rendering
  - Cross-platform file opening support (macOS, Windows, Linux)
- **📋 Clipboard Copy Commands**: Three new CLI commands for copying server configurations to clipboard
  - `pmit copy-config <server> [--format desktop|code]` - Universal command with format selection
  - `pmit copy-desktop <server>` - Direct Claude Desktop config.json format
  - `pmit copy-code <server>` - Direct Claude Code mcp add command format
- **🔄 Multi-Format Support**: Copy configurations for both Claude Desktop and Claude Code
- **🎯 Smart Server Lookup**: Support for both server ID and server name (case-insensitive)
- **📄 Format Options**: Desktop format (JSON config) and Code format (mcp add command)
- **⚡ Quick Access**: Direct commands for common use cases without format selection
- **🖥️ Terminal Preview**: Shows copied content when run in terminal for verification
- **🛠️ Enhanced Workflow**: Streamlines server configuration sharing between applications
- **🔍 Enhanced Response Search**: Improved regex search for MCP responses with full-width layout
  - Live search input field in response viewer with regex pattern matching
  - Case-insensitive search across both response titles and content
  - Graceful fallback to simple string search for invalid regex patterns
  - Real-time filtering as you type with instant visual feedback
- **🐛 Critical Bug Fix**: Fixed missing interaction callback transfer for filesystem servers
  - Raw interactions now properly display for all server types including filesystem servers
  - Resolved timing issue where interaction callbacks weren't transferred when creating new MCP services with roots

### v0.4.0 - MCP Roots Protocol & Enhanced Filesystem Support
- **🌿 MCP Roots Protocol Implementation**: Full support for MCP filesystem roots protocol
- **📁 Comprehensive Roots Management**: Complete TUI and CLI interface for managing filesystem boundaries
- **🎛️ Roots Tab in TUI**: Dedicated interface for visual root management with real-time validation
- **⚡ CLI Root Commands**: Three new commands for root management:
  - `pmit roots-list [server-id] [--verbose]` - List and validate filesystem roots
  - `pmit roots-add <server-id> <path> [--name]` - Add roots with display names
  - `pmit roots-remove <server-id> <path>` - Remove roots with flexible path matching
- **🔒 Automatic Root Transmission**: Roots are automatically sent to servers during connection
- **✅ Path Validation**: Real-time validation with status indicators (✓/✗) for root paths
- **🔄 Protocol Compliance**: Implements `roots/list` and `notifications/roots/list_changed` protocols
- **📊 Enhanced Server Configuration**: Persistent root storage in server configurations
- **🛠️ Developer Features**: URI conversion, path resolution, and comprehensive testing support
- **🐛 Bug Fixes**:
  - Fixed server panel widget error with #server-list query during state changes
  - Enhanced error handling for widget lifecycle management
  - Improved stderr output suppression for cleaner TUI display

### v0.3.0 - FastMCP Integration & Major Improvements
- **🔥 Major Architecture Overhaul**: Migrated to FastMCP for robust, high-performance MCP protocol handling
- **✨ Enhanced Transport Support**: Added HTTP+SSE transport alongside improved STDIO transport  
- **🧹 Tab Auto-clearing**: Automatically clears all tabs when disconnecting from servers for clean state management
- **🔧 Improved Error Handling**: Enhanced connection error reporting and recovery with FastMCP integration
- **📋 Real-time Notifications**: Fixed and enhanced MCP server notifications with FastMCP's MessageHandler system
- **🎯 Configuration Cleanup**: Removed problematic TCP server examples from default setup
- **📚 Comprehensive Documentation**: Updated all documentation and architecture diagrams to reflect FastMCP integration
- **🐛 Bug Fixes**:
  - Fixed resource reading errors with FastMCP's object-based responses
  - Fixed prompt and tool execution compatibility issues
  - Fixed app shutdown callback errors
  - Resolved all type checking errors across transport implementations
- **⚡ Performance**: Connection reuse enabled by default for better performance
- **🔒 Stability**: Enhanced subprocess management and cleanup for STDIO transport

**🔄 Migration Note**: Existing users may have legacy server configurations. Use the [Clean Installation](#clean-installation) steps if you encounter connection issues with old TCP server examples.

### v0.2.0 - Previous Release
- Initial stable release with custom MCP implementation
- Basic STDIO and TCP transport support
- TUI interface with resource, tool, and prompt management

## Development

### Setup Development Environment

```shell
# Clone repository
git clone https://github.com/paulrobello/par-mcp-inspector-tui.git
cd par-mcp-inspector-tui

# Install dependencies
uv sync

# Run formatting, linting, and type checking
make checkall

# Run the application
uv run pmit tui
```

### Development Commands

```shell
# Format, lint, and type check
make checkall

# Individual tools
make format      # Format with ruff
make lint        # Lint with ruff
make typecheck   # Type check with pyright

# Update dependencies
uv sync -U

# Build package
uv build
```

### Clean Installation

To start with a completely clean configuration (removes any problematic legacy servers):

```shell
# Remove existing configuration
rm ~/.config/par-mcp-inspector-tui/servers.yaml

# Launch app - will create new default configuration
pmit tui
```

## Architecture Overview

The application is built on a modern, layered architecture leveraging **FastMCP** as the core Model Context Protocol implementation. This provides robust transport handling, automatic serialization, and real-time notification support.

### Key Architectural Components

#### FastMCP Integration
- **StdioTransport**: Handles subprocess communication with automatic process lifecycle management
- **WSTransport**: Manages WebSocket connections for TCP-based MCP servers  
- **NotificationBridge**: Custom bridge that adapts FastMCP's `MessageHandler` system to our notification architecture
- **Automatic Protocol Handling**: JSON-RPC 2.0 serialization, error handling, and capability negotiation

#### Transport Layer Architecture
- **STDIO Transport**: Uses FastMCP's `StdioTransport` with a `NotificationBridge` to convert FastMCP notifications to our `MCPNotification` format
- **TCP Transport**: Uses FastMCP's `WSTransport` with direct `MessageHandler` integration
- **Connection Management**: Robust connection handling with automatic cleanup and error recovery

#### Notification System
- **Real-time Notifications**: FastMCP's native notification support enables instant server-to-client communication
- **Protocol Bridge**: `NotificationBridge` class seamlessly converts FastMCP notifications to application-level events
- **Auto-refresh Logic**: List change notifications automatically refresh relevant UI views
- **Toast Control**: Per-server notification preferences with intelligent suppression

### Detailed Diagrams

For comprehensive architectural diagrams showing the FastMCP integration, component structure, protocol communication, and data flow, see the [Architecture Diagrams](docs/diagrams.md) document.

The diagrams include:
- **Application Flow Diagram** - CLI command routing and component interactions including download-resource command
- **TUI Component Architecture** - UI layout and widget organization  
- **MCP Protocol Flow** - FastMCP-based communication sequence with notification bridge
- **Client Transport Architecture** - FastMCP transport implementations with notification bridge architecture
- **Server Notifications Architecture** - FastMCP notification system with protocol adaptation
- **Data Flow Through Layers** - Information flow across system layers
- **Form Validation Flow** - Real-time validation system for execute button control
- **Dynamic Form Architecture** - Form widget structure and validation relationships
- **File Type Detection Flow** - Magic number detection and MIME type handling for resource downloads

## Project Structure

```
src/par-mcp-inspector-tui/
├── __init__.py              # Package metadata
├── __main__.py              # CLI entry point
├── models/                  # Data models
│   ├── base.py             # MCP protocol base types
│   ├── server.py           # Server configuration
│   ├── tool.py             # Tool definitions
│   ├── resource.py         # Resource definitions
│   └── prompt.py           # Prompt definitions
├── client/                  # FastMCP-based client implementations
│   ├── base.py             # Abstract client interface
│   ├── stdio.py            # STDIO transport client with FastMCP StdioTransport
│   └── tcp.py              # TCP transport client with FastMCP WSTransport
├── services/                # Service layer
│   ├── mcp_service.py      # MCP connection service
│   └── server_manager.py   # Server configuration management
└── tui/                     # Terminal UI components
    ├── app.py              # Main TUI application
    ├── app.tcss            # Textual CSS styling
    └── widgets/            # Custom UI widgets
        ├── server_panel.py        # Server list and connection
        ├── connection_status.py   # Connection status display
        ├── resources_view.py      # Resources browser
        ├── prompts_view.py        # Prompts interface
        ├── tools_view.py          # Tools interface
        ├── response_viewer.py     # Response display
        ├── dynamic_form.py        # Dynamic form builder with validation
        └── notification_panel.py  # Notifications
```

## Troubleshooting

### Common Issues

1. **Server won't connect**:
   - Check the command/path for STDIO servers
   - Verify host/port for TCP servers
   - Use CLI debug commands for detailed connection testing
   - Enable debug mode for detailed error messages
   - FastMCP provides enhanced error reporting for connection issues

2. **No tools/resources showing**:
   - Use `--verbose` flag to see server capabilities
   - Check if server supports the requested endpoints (resources/tools/prompts)
   - Verify server implements MCP protocol correctly
   - Some servers may only implement partial MCP functionality

3. **Request timeouts**:
   - Server may not support the requested endpoint
   - Check server capabilities with `debug` command
   - Verify server is responsive and not hanging

4. **Form validation errors**:
   - Check parameter types and requirements
   - Ensure all required fields are filled
   - Review server documentation for parameter formats

5. **Resource download issues**:
   - Use `debug` command to see available resource names with color-coded display
   - Ensure resource name matches exactly (case-sensitive)
   - Check if server is configured (temporary servers need to be added to configuration)
   - Verify resource actually contains downloadable content
   - Use `--verbose` flag with download command for detailed error information

### Debugging Tools

#### CLI Debugging
```shell
# Test any STDIO server without configuration (PyPI installation)
pmit connect <command> --verbose --debug

# Test any TCP server without configuration  
pmit connect-tcp <host> <port> --verbose --debug

# Debug configured servers
pmit debug <server-id-or-name> --verbose --debug

# List all configured servers
pmit servers

# Download resources from configured servers
pmit download-resource <server-id> "<resource-name>" --verbose

# From source (prefix all commands with 'uv run')
uv run pmit connect <command> --verbose --debug
uv run pmit connect-tcp <host> <port> --verbose --debug
# etc...
```

#### TUI Debug Mode
```shell
# Enable debug logging in TUI (PyPI installation)
pmit tui --debug

# From source
uv run pmit tui --debug
```

#### Enhanced Debug Features
The debug commands provide enhanced resource display:
- **Color-coded output**: Green names, cyan URIs, yellow descriptions, magenta MIME types
- **Download instructions**: Ready-to-use `download-resource` commands for configured servers
- **Smart guidance**: Different messages for configured vs temporary servers

#### Capability Checking  
The application automatically checks server capabilities to avoid timeouts:
- If a server reports `null` for resources/tools/prompts capabilities, those endpoints are skipped
- Use `--verbose` to see raw server capability information
- Servers with `{}` (empty object) capabilities will still be tested

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run `make checkall` to ensure code quality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Paul Robello - probello@gmail.com

## Related Projects

- [Model Context Protocol](https://modelcontextprotocol.io/) - The protocol specification
- [MCP Servers](https://github.com/modelcontextprotocol/servers) - Official MCP server implementations
- [Textual](https://textual.textualize.io/) - The TUI framework used by this application
