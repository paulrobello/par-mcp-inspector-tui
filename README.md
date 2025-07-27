# PAR MCP Inspector TUI

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
![Runs on Linux | MacOS | Windows](https://img.shields.io/badge/runs%20on-Linux%20%7C%20MacOS%20%7C%20Windows-blue)
![Arch x86-63 | ARM | AppleSilicon](https://img.shields.io/badge/arch-x86--64%20%7C%20ARM%20%7C%20AppleSilicon-blue)

![MIT License](https://img.shields.io/badge/license-MIT-green.svg)
![Development Status](https://img.shields.io/badge/status-stable-green.svg)

A comprehensive Terminal User Interface (TUI) application for inspecting and interacting with Model Context Protocol (MCP) servers. This tool provides an intuitive interface to connect to MCP servers, explore their capabilities, and execute tools, prompts, and resources in real-time.

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/probello3)

## Screenshots

![MCP Inspector TUI Interface](https://raw.githubusercontent.com/paulrobello/par-mcp-inspector-tui/main/Screenshot.png)

*The MCP Inspector TUI showing a connected "Everything" server with available tools (echo, add, printEnv), tool parameter forms, and real-time interaction logs. The interface displays server management on the left, tabbed content areas in the center, and notifications on the right.*

## Features

- **Multiple Transport Support**: Connect to MCP servers via STDIO and TCP
- **CLI Debugging Tools**: Connect to arbitrary servers and inspect interactions without configuration
- **Resource Download CLI**: Download resources by name with automatic file type detection
- **Real-time Introspection**: Discover tools, prompts, and resources from connected servers
- **Dynamic Forms**: Automatically generated forms based on server-provided schemas with real-time validation
- **Form Validation**: Smart execute button control - disabled until all required fields are filled
- **Magic Number Detection**: Automatic file type detection using magic numbers for binary resources
- **Syntax Highlighting**: Rich response formatting with support for JSON, Markdown, and code
- **File Management**: Save and open resources with proper file extensions and MIME type handling
- **Server Management**: Persistent configuration storage for multiple server connections
- **Non-blocking Operations**: Async communication ensuring responsive UI
- **Server Notifications**: Real-time notifications from MCP servers with auto-refresh capabilities
- **Application Notifications**: Real-time status updates and error handling
- **Capability-aware**: Gracefully handles servers with partial MCP implementation

## Technology Stack
- **Python 3.11+** - Modern Python with latest features
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

# Connect to arbitrary TCP server
pmit connect-tcp localhost 3333

# Download resources from servers
pmit download-resource <server-id> <resource-name>
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
2. **Default servers**: The application comes with example server configurations
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
- `--name -n`: Server name for display (default: Ad-hoc Server)

Connect to an arbitrary STDIO server without adding it to configuration. Uses the same enhanced debug output as the `debug` command, including:
- **Color-coded resource display** with download guidance
- **Smart messaging**: Informs users to add server to configuration before downloading resources
- **Full MCP testing**: Resources, tools, and prompts endpoints

**Examples:**
```shell
# Basic usage (PyPI installation)
pmit connect npx -a "-y" -a "@modelcontextprotocol/server-filesystem" -a "/tmp"

# With environment variables and custom name
pmit connect python -a "server.py" -e "DEBUG=1" -e "PORT=8080" -n "My Server"

# Verbose output with debug logging
pmit connect node -a "server.js" --verbose --debug

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
- `--name -n`: Server name for display (default: TCP Server)

Connect to an arbitrary TCP server without adding it to configuration. Uses the same enhanced debug output as other debug commands, including:
- **Enhanced resource listing** with color-coded display
- **Download guidance**: Instructions to add server to configuration first
- **Complete testing**: All MCP endpoints (resources, tools, prompts)

**Examples:**
```shell
# Default host and port (PyPI installation)
pmit connect-tcp

# Custom host and port with verbose and debug output
pmit connect-tcp example.com 8080 -n "Remote Server" --verbose --debug

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

## Server Configuration

The TUI application stores server configurations in `~/.config/mcp-inspector/servers.yaml`. Example configuration:

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

  custom-tcp-server:
    name: "Custom TCP Server"
    transport: "tcp"
    host: "localhost"
    port: 3333
    toast_notifications: false  # Disable toast notifications for this server
```

#### Configuration Options

- **toast_notifications** (boolean, default: true): Controls whether to show toast popup notifications when the server sends notifications. When `false`, notifications are still added to the notifications tab but won't show as toast popups. Note: Toasts are automatically suppressed when viewing the notifications tab regardless of this setting.

#### UI Configuration

You can configure toast notifications through the TUI interface:

1. **Add Server Dialog**: When adding a new server, check/uncheck "Show toast notifications from this server"
2. **Edit Server Dialog**: Select any server and click "Edit Server" to modify the toast notification setting
3. **Per-Server Control**: Each server has different notification settings
4. **Real-time Updates**: Changes take effect immediately after saving

### Supported Transport Types

#### STDIO Transport
For servers that communicate via standard input/output:
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

#### TCP Transport
For servers running on a network port:
```yaml
servers:
  my-tcp-server:
    name: "My TCP Server"
    transport: "tcp"
    host: "localhost"
    port: 8080
```

## User Interface

### Main Layout
- **Left Panel**: Server list and connection status
- **Center Panel**: Tabbed interface with:
  - **Resources**: Browse and read available resources
  - **Prompts**: Execute prompts with dynamic argument forms and validation
  - **Tools**: Call tools with smart parameter validation and form controls
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

**TCP Transport Settings:**
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
- `s` - Focus server panel
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

## Architecture Overview

For detailed architectural diagrams showing the application flow, component structure, protocol communication, and data flow, see the [Architecture Diagrams](docs/diagrams.md) document.

The diagrams include:
- **Application Flow Diagram** - CLI command routing and component interactions including download-resource command
- **TUI Component Architecture** - UI layout and widget organization  
- **MCP Protocol Flow** - Communication sequence between components
- **Client Transport Architecture** - STDIO and TCP transport implementations
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
├── client/                  # MCP client implementations
│   ├── base.py             # Abstract client interface
│   ├── stdio.py            # STDIO transport client
│   └── tcp.py              # TCP transport client
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
