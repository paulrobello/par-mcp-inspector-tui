"""Main application with improved CLI structure and features."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Annotated, Any

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from par_mcp_inspector_tui.tui import MCPInspectorApp

from . import __application_binary__, __application_title__, __version__
from .logging_config import get_logger, setup_logging
from .models import MCPServer, ServerState, TransportType
from .services import MCPService, ServerManager

# Create the main Typer app with rich help
app = typer.Typer(
    name=__application_binary__,
    help=f"{__application_title__} - MCP Server Inspector TUI",
    rich_markup_mode="rich",
    add_completion=False,
)
console = Console(stderr=True)
logger = get_logger(__name__)

# Load environment variables
load_dotenv()
load_dotenv(Path(f"~/.{__application_binary__}.env").expanduser())


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold blue]{__application_title__}[/bold blue] version [bold green]{__version__}[/bold green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", "-v", callback=version_callback, help="Show version and exit"),
    ] = False,
) -> None:
    """MCP Inspector TUI - Inspect and interact with Model Context Protocol servers.

    Features real-time server notifications with automatic UI refresh capabilities."""
    pass


@app.command()
def tui(
    debug: Annotated[
        bool,
        typer.Option("--debug", "-d", help="Enable debug mode"),
    ] = False,
) -> None:
    """Launch the MCP Inspector TUI application.

    Features real-time server notifications and auto-refresh capabilities.
    Connect to servers to receive live updates when tools, resources, or prompts change."""
    try:
        # Only create log file if debug mode is enabled
        log_file = None
        if debug:
            from datetime import datetime

            log_dir = Path.cwd() / "logs"
            log_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"

        setup_logging(debug=debug, log_file=log_file)
        console.print("[bold blue]Starting MCP Inspector TUI[/bold blue]")
        MCPInspectorApp(debug=debug).run()

    except Exception as e:
        logger.error(f"TUI command failed: {e}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def servers() -> None:
    """List configured MCP servers."""
    try:
        setup_logging(debug=False)  # No debug logging for simple listing
        server_manager = ServerManager()
        servers_list = server_manager.list_servers()

        if not servers_list:
            console.print("[yellow]No servers configured[/yellow]")
            return

        table = Table(title="Configured MCP Servers")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Transport", style="cyan")
        table.add_column("Connection", style="green")
        table.add_column("Last Error", style="red")

        for server in servers_list:
            connection_info = ""
            if server.transport.value == "stdio":
                connection_info = f"{server.command} {' '.join(server.args or [])}"
            elif server.transport.value == "tcp":
                connection_info = f"{server.host}:{server.port}"
            elif server.transport.value == "http":
                connection_info = server.url or ""

            last_error = server.error[:50] + "..." if server.error and len(server.error) > 50 else server.error or ""

            table.add_row(server.id, server.name, server.transport.value.upper(), connection_info, last_error)

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def debug(
    server_id_or_name: Annotated[str, typer.Argument(help="Server ID or name to debug")],
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output with raw JSON"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging of MCP messages"),
    ] = False,
    raw_interactions: Annotated[
        bool,
        typer.Option("--raw-interactions", help="Dump raw MCP protocol interactions"),
    ] = False,
) -> None:
    """Connect to a server and dump all interactions for debugging."""
    # Set up logging with file output only if debug is enabled
    log_file = None
    if debug:
        from datetime import datetime

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"
    setup_logging(debug=debug, log_file=log_file)

    asyncio.run(_debug_server(server_id_or_name, verbose, debug, raw_interactions))


@app.command()
def connect(
    command: Annotated[str, typer.Argument(help="Command to execute for STDIO transport")],
    args: Annotated[
        list[str],
        typer.Option("--arg", "-a", help="Command arguments (can be specified multiple times)"),
    ] = [],
    env: Annotated[
        list[str],
        typer.Option("--env", "-e", help="Environment variables in KEY=VALUE format (can be specified multiple times)"),
    ] = [],
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output with raw JSON"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging of MCP messages"),
    ] = False,
    raw_interactions: Annotated[
        bool,
        typer.Option("--raw-interactions", help="Dump raw MCP protocol interactions"),
    ] = False,
    debug_dump: Annotated[
        bool,
        typer.Option(
            "--debug-dump", "-D", help="Perform debug dump like the debug command (lists tools, resources, prompts)"
        ),
    ] = False,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Server name for display"),
    ] = "Ad-hoc Server",
) -> None:
    """Connect to an arbitrary MCP server via STDIO transport."""
    # Set up logging with file output only if debug is enabled
    log_file = None
    if debug:
        from datetime import datetime

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"
    setup_logging(debug=debug, log_file=log_file)

    asyncio.run(_connect_arbitrary_server(command, args, env, verbose, debug, raw_interactions, debug_dump, name))


@app.command()
def download_resource(
    server_id_or_name: Annotated[str, typer.Argument(help="Server ID or name")],
    resource_name: Annotated[str, typer.Argument(help="Resource name to download")],
    output_dir: Annotated[
        str,
        typer.Option("--output", "-o", help="Output directory (default: current directory)"),
    ] = ".",
    filename: Annotated[
        str | None,
        typer.Option("--filename", "-f", help="Custom filename (default: auto-detect from resource)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging"),
    ] = False,
) -> None:
    """Download a resource by name from an MCP server."""
    # Set up logging with file output only if debug is enabled
    log_file = None
    if debug:
        from datetime import datetime

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"
    setup_logging(debug=debug, log_file=log_file)

    asyncio.run(_download_resource(server_id_or_name, resource_name, output_dir, filename, verbose, debug))


@app.command()
def connect_tcp(
    host: Annotated[str, typer.Argument(help="Host to connect to")] = "localhost",
    port: Annotated[int, typer.Argument(help="Port to connect to")] = 3333,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output with raw JSON"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging of MCP messages"),
    ] = False,
    raw_interactions: Annotated[
        bool,
        typer.Option("--raw-interactions", help="Dump raw MCP protocol interactions"),
    ] = False,
    debug_dump: Annotated[
        bool,
        typer.Option(
            "--debug-dump", "-D", help="Perform debug dump like the debug command (lists tools, resources, prompts)"
        ),
    ] = False,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Server name for display"),
    ] = "TCP Server",
) -> None:
    """Connect to an arbitrary MCP server via TCP transport."""
    # Set up logging with file output only if debug is enabled
    log_file = None
    if debug:
        from datetime import datetime

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"
    setup_logging(debug=debug, log_file=log_file)

    asyncio.run(_connect_arbitrary_tcp_server(host, port, verbose, debug, raw_interactions, debug_dump, name))


@app.command()
def connect_http(
    url: Annotated[str, typer.Argument(help="HTTP endpoint URL (e.g., https://example.com/mcp)")],
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose output with raw JSON"),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option("--debug", help="Enable debug logging of MCP messages"),
    ] = False,
    raw_interactions: Annotated[
        bool,
        typer.Option("--raw-interactions", help="Dump raw MCP protocol interactions"),
    ] = False,
    debug_dump: Annotated[
        bool,
        typer.Option(
            "--debug-dump", "-D", help="Perform debug dump like the debug command (lists tools, resources, prompts)"
        ),
    ] = False,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Server name for display"),
    ] = "HTTP Server",
) -> None:
    """Connect to an arbitrary MCP server via Streamable HTTP transport."""
    # Set up logging with file output only if debug is enabled
    log_file = None
    if debug:
        from datetime import datetime

        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"
    setup_logging(debug=debug, log_file=log_file)

    asyncio.run(_connect_arbitrary_http_server(url, verbose, debug, raw_interactions, debug_dump, name))


@app.command()
def roots_list(
    server_id: Annotated[
        str | None,
        typer.Argument(help="Server ID (optional - uses current connected server if not specified)"),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show detailed root information"),
    ] = False,
) -> None:
    """List filesystem roots for a server."""
    asyncio.run(_list_roots(server_id, verbose))


@app.command()
def roots_add(
    server_id: Annotated[
        str,
        typer.Argument(help="Server ID"),
    ],
    path: Annotated[
        str,
        typer.Argument(help="Filesystem path or file:// URI to add as root"),
    ],
    name: Annotated[
        str | None,
        typer.Option("--name", "-n", help="Display name for the root"),
    ] = None,
) -> None:
    """Add a filesystem root to a server configuration."""
    asyncio.run(_add_root(server_id, path, name))


@app.command()
def roots_remove(
    server_id: Annotated[
        str,
        typer.Argument(help="Server ID"),
    ],
    path: Annotated[
        str,
        typer.Argument(help="Filesystem path or file:// URI to remove"),
    ],
) -> None:
    """Remove a filesystem root from a server configuration."""
    asyncio.run(_remove_root(server_id, path))


@app.command()
def copy_config(
    server_id_or_name: Annotated[str, typer.Argument(help="Server ID or name to copy config for")],
    format_type: Annotated[
        str,
        typer.Option("--format", "-f", help="Config format (desktop|code)"),
    ] = "desktop",
) -> None:
    """Copy server configuration to clipboard in specified format.

    Formats:
    - desktop: Claude Desktop config.json format
    - code: Claude Code mcp add command format
    """
    try:
        setup_logging(debug=False)  # No debug logging for simple operation
        server_manager = ServerManager()
        servers = server_manager.list_servers()

        # Find server by ID or name
        server = next((s for s in servers if s.id == server_id_or_name), None)
        if not server:
            server = next((s for s in servers if s.name.lower() == server_id_or_name.lower()), None)

        if not server:
            console.print(f"[bold red]Error:[/bold red] Server '{server_id_or_name}' not found")
            console.print("Available servers:")
            for s in servers:
                console.print(f"  - {s.id}: {s.name}")
            raise typer.Exit(code=1)

        if format_type.lower() in ["desktop", "d"]:
            _copy_for_claude_desktop_cli(server)
        elif format_type.lower() in ["code", "c"]:
            _copy_for_claude_code_cli(server)
        else:
            console.print(f"[bold red]Error:[/bold red] Unknown format '{format_type}'. Use 'desktop' or 'code'")
            raise typer.Exit(code=1)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def copy_desktop(
    server_id_or_name: Annotated[str, typer.Argument(help="Server ID or name to copy config for")],
) -> None:
    """Copy server configuration to clipboard in Claude Desktop format."""
    try:
        setup_logging(debug=False)  # No debug logging for simple operation
        server_manager = ServerManager()
        servers = server_manager.list_servers()

        # Find server by ID or name
        server = next((s for s in servers if s.id == server_id_or_name), None)
        if not server:
            server = next((s for s in servers if s.name.lower() == server_id_or_name.lower()), None)

        if not server:
            console.print(f"[bold red]Error:[/bold red] Server '{server_id_or_name}' not found")
            console.print("Available servers:")
            for s in servers:
                console.print(f"  - {s.id}: {s.name}")
            raise typer.Exit(code=1)

        _copy_for_claude_desktop_cli(server)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def copy_code(
    server_id_or_name: Annotated[str, typer.Argument(help="Server ID or name to copy config for")],
) -> None:
    """Copy server configuration to clipboard in Claude Code format."""
    try:
        setup_logging(debug=False)  # No debug logging for simple operation
        server_manager = ServerManager()
        servers = server_manager.list_servers()

        # Find server by ID or name
        server = next((s for s in servers if s.id == server_id_or_name), None)
        if not server:
            server = next((s for s in servers if s.name.lower() == server_id_or_name.lower()), None)

        if not server:
            console.print(f"[bold red]Error:[/bold red] Server '{server_id_or_name}' not found")
            console.print("Available servers:")
            for s in servers:
                console.print(f"  - {s.id}: {s.name}")
            raise typer.Exit(code=1)

        _copy_for_claude_code_cli(server)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)


def _copy_for_claude_desktop_cli(server: MCPServer) -> None:
    """Copy server config in Claude Desktop format to clipboard."""
    try:
        import json

        # Format for Claude Desktop config.json
        desktop_config = {server.name: _server_to_desktop_config(server)}
        config_text = json.dumps(desktop_config, indent=2)

        # Copy to clipboard
        import pyperclip

        pyperclip.copy(config_text)

        console.print(
            f"[bold green]✓ Server config for '{server.name}' copied to clipboard in Claude Desktop format[/bold green]"
        )
        if console.is_terminal:
            console.print(f"[dim]Preview:[/dim]\n{config_text}")

    except Exception as e:
        console.print(f"[bold red]Error copying config:[/bold red] {e}")
        raise typer.Exit(code=1)


def _copy_for_claude_code_cli(server: MCPServer) -> None:
    """Copy server config in Claude Code MCP add format to clipboard."""
    try:
        # Format for Claude Code mcp add command: "claude mcp add <name> -- <command> [args...]"
        command_parts = ["claude", "mcp", "add", server.name, "--"]

        if server.transport == TransportType.STDIO:
            command_parts.append(server.command or "")
            # Add arguments
            if server.args:
                command_parts.extend(server.args)

        elif server.transport == TransportType.TCP:
            # For TCP transport, we need to represent it as a command that would start a TCP server
            # This is a placeholder as TCP servers typically need custom setup
            command_parts.extend(
                [
                    "# TCP transport not directly supported in claude mcp add",
                    f"# Host: {server.host or 'localhost'}",
                    f"# Port: {server.port or 3333}",
                ]
            )

        elif server.transport == TransportType.HTTP:
            # For HTTP transport, we need to represent it as a command that would start an HTTP server
            # This is a placeholder as HTTP servers typically need custom setup
            command_parts.extend(
                [
                    "# HTTP transport not directly supported in claude mcp add",
                    f"# URL: {server.url or ''}",
                ]
            )

        command_text = " ".join(command_parts)

        # Copy to clipboard
        import pyperclip

        pyperclip.copy(command_text)

        console.print(
            f"[bold green]✓ MCP add command for '{server.name}' copied to clipboard for Claude Code[/bold green]"
        )
        if console.is_terminal:
            console.print(f"[dim]Preview:[/dim]\n{command_text}")

    except Exception as e:
        console.print(f"[bold red]Error copying command:[/bold red] {e}")
        raise typer.Exit(code=1)


def _server_to_desktop_config(server: MCPServer) -> dict[str, Any]:
    """Convert MCPServer to Claude Desktop config format."""

    if server.transport == TransportType.STDIO:
        config: dict[str, Any] = {
            "command": server.command or "",
        }

        if server.args:
            config["args"] = server.args

        if server.env:
            config["env"] = server.env

        return config

    elif server.transport == TransportType.TCP:
        return {"transport": {"type": "tcp", "host": server.host or "localhost", "port": server.port or 3333}}

    elif server.transport == TransportType.HTTP:
        return {"transport": {"type": "http", "url": server.url or ""}}

    return {}


async def _list_roots(server_id: str | None, verbose: bool) -> None:
    """List filesystem roots for a server."""
    manager = ServerManager()

    if server_id:
        server = manager.get_server(server_id)
        if not server:
            console.print(f"[red]Server '{server_id}' not found[/red]")
            raise typer.Exit(code=1)
    else:
        # Try to find currently connected server
        servers = manager.list_servers()
        connected_servers = [s for s in servers if s.state == ServerState.CONNECTED]
        if not connected_servers:
            console.print("[red]No connected servers found. Please specify a server ID.[/red]")
            raise typer.Exit(code=1)
        server = connected_servers[0]
        server_id = server.id

    console.print(f"[bold]Roots for server '{server.name}' ({server_id}):[/bold]")

    if server.roots:
        for i, root_path in enumerate(server.roots, 1):
            # Check if path exists and get info
            try:
                from pathlib import Path
                from urllib.parse import urlparse

                # Convert file:// URI to path if needed
                if root_path.startswith("file://"):
                    parsed = urlparse(root_path)
                    local_path = Path(parsed.path)
                else:
                    local_path = Path(root_path)

                status = "✓" if local_path.exists() else "✗"
                type_info = ""
                if verbose and local_path.exists():
                    if local_path.is_dir():
                        type_info = " (directory)"
                    elif local_path.is_file():
                        type_info = " (file)"

                console.print(f"  {i}. {status} {root_path}{type_info}")
            except Exception:
                console.print(f"  {i}. ? {root_path} (invalid path)")
    else:
        console.print("  [dim]No roots configured[/dim]")


async def _add_root(server_id: str, path: str, name: str | None) -> None:
    """Add a root to a server configuration."""
    manager = ServerManager()
    server = manager.get_server(server_id)

    if not server:
        console.print(f"[red]Server '{server_id}' not found[/red]")
        raise typer.Exit(code=1)

    # Convert to file:// URI if it's a local path
    if not path.startswith("file://"):
        from pathlib import Path

        abs_path = Path(path).resolve()
        uri = f"file://{abs_path}"
    else:
        uri = path

    # Initialize roots list if None
    if server.roots is None:
        server.roots = []

    # Check if already exists
    if uri in server.roots:
        console.print(f"[yellow]Root already exists: {uri}[/yellow]")
        return

    # Add the root
    server.roots.append(uri)
    manager.save()

    console.print(f"[green]Added root to server '{server.name}': {uri}[/green]")

    if name:
        console.print(f"[dim]Note: Display name '{name}' will be used in the UI[/dim]")


async def _remove_root(server_id: str, path: str) -> None:
    """Remove a root from a server configuration."""
    manager = ServerManager()
    server = manager.get_server(server_id)

    if not server:
        console.print(f"[red]Server '{server_id}' not found[/red]")
        raise typer.Exit(code=1)

    if not server.roots:
        console.print(f"[yellow]No roots configured for server '{server.name}'[/yellow]")
        return

    # Convert to file:// URI if it's a local path
    if not path.startswith("file://"):
        from pathlib import Path

        abs_path = Path(path).resolve()
        uri = f"file://{abs_path}"
    else:
        uri = path

    # Try to remove
    if uri in server.roots:
        server.roots.remove(uri)
        manager.save()
        console.print(f"[green]Removed root from server '{server.name}': {uri}[/green]")
    else:
        console.print(f"[yellow]Root not found: {uri}[/yellow]")
        console.print("[dim]Available roots:[/dim]")
        for root in server.roots:
            console.print(f"  - {root}")


async def _connect_arbitrary_server(
    command: str,
    args: list[str],
    env: list[str],
    verbose: bool,
    debug: bool,
    raw_interactions: bool,
    debug_dump: bool,
    name: str,
) -> None:
    """Connect to an arbitrary STDIO MCP server."""
    try:
        console.print(f"[bold blue]Connecting to arbitrary server:[/bold blue] {name}")
        console.print(f"Command: {command} {' '.join(args)}")

        # Parse environment variables
        env_dict: dict[str, str] = {}
        for env_var in env:
            if "=" not in env_var:
                console.print(f"[bold red]Error:[/bold red] Invalid environment variable format: {env_var}")
                console.print("Environment variables must be in KEY=VALUE format")
                raise typer.Exit(code=1)
            key, value = env_var.split("=", 1)
            env_dict[key] = value

        if env_dict:
            console.print("Environment variables:")
            for key, value in env_dict.items():
                console.print(f"  {key}={value}")

        # Create temporary server configuration
        server = MCPServer(
            id="temp-server", name=name, transport=TransportType.STDIO, command=command, args=args, env=env_dict
        )

        # If debug_dump is enabled, run the full debug logic, otherwise just connect
        if debug_dump:
            await _run_server_debug(server, verbose, debug, raw_interactions)
        else:
            await _run_simple_connection(server, verbose, debug, raw_interactions)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


async def _connect_arbitrary_tcp_server(
    host: str, port: int, verbose: bool, debug: bool, raw_interactions: bool, debug_dump: bool, name: str
) -> None:
    """Connect to an arbitrary TCP MCP server."""
    try:
        console.print(f"[bold blue]Connecting to arbitrary TCP server:[/bold blue] {name}")
        console.print(f"Address: {host}:{port}")

        # Create temporary server configuration
        server = MCPServer(id="temp-tcp-server", name=name, transport=TransportType.TCP, host=host, port=port)

        # If debug_dump is enabled, run the full debug logic, otherwise just connect
        if debug_dump:
            await _run_server_debug(server, verbose, debug, raw_interactions)
        else:
            await _run_simple_connection(server, verbose, debug, raw_interactions)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


async def _connect_arbitrary_http_server(
    url: str, verbose: bool, debug: bool, raw_interactions: bool, debug_dump: bool, name: str
) -> None:
    """Connect to an arbitrary HTTP MCP server."""
    try:
        console.print(f"[bold blue]Connecting to arbitrary HTTP server:[/bold blue] {name}")
        console.print(f"URL: {url}")

        # Create temporary server configuration
        server = MCPServer(id="temp-http-server", name=name, transport=TransportType.HTTP, url=url)

        # If debug_dump is enabled, run the full debug logic, otherwise just connect
        if debug_dump:
            await _run_server_debug(server, verbose, debug, raw_interactions)
        else:
            await _run_simple_connection(server, verbose, debug, raw_interactions)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


async def _run_simple_connection(server: MCPServer, verbose: bool, debug: bool, raw_interactions: bool) -> None:
    """Run simple server connection logic (without debug dump)."""
    # For filesystem servers, provide roots based on command args
    roots = []
    if server.transport == TransportType.STDIO and server.args:
        # For filesystem server, use the directory arguments as roots
        for arg in server.args:
            # Skip npm package names and flags, look for actual paths
            if (
                not arg.startswith("-")
                and not arg.startswith("@")
                and ("/" in arg or arg in [".", "~"])
                and not arg.endswith(".js")
                and not arg.endswith(".ts")
            ):
                roots.append(arg)

    if debug and roots:
        console.print(f"[dim]Providing roots: {roots}[/dim]")

    if raw_interactions:
        console.print("[bold yellow]Raw MCP interactions will be dumped to console[/bold yellow]")

    # Create service and connect
    service = MCPService(debug=debug or raw_interactions, roots=roots)

    console.print("\n[bold yellow]Connecting...[/bold yellow]")
    try:
        await service.connect(server)
        console.print("[bold green]✓ Connected successfully[/bold green]")

        # Give server time to process initialization
        if debug:
            console.print("[dim]Waiting for server to complete initialization and potential roots request...[/dim]")
        await asyncio.sleep(5.0)

        # Get basic server info
        server_info = service.server_info
        if server_info:
            console.print(
                f"\n[bold blue]Connected to:[/bold blue] {server_info.name or 'Unknown'} v{server_info.version}"
            )
            if verbose:
                console.print(f"Protocol Version: {server_info.protocol_version}")

        console.print("[bold green]Connection established and ready for interaction[/bold green]")

    except Exception as e:
        console.print(f"[bold red]✗ Connection failed:[/bold red] {e}")
        return

    # Disconnect
    console.print("\n[bold yellow]Disconnecting...[/bold yellow]")
    await service.disconnect()
    console.print("[bold green]✓ Disconnected[/bold green]")


async def _run_server_debug(server: MCPServer, verbose: bool, debug: bool, raw_interactions: bool) -> None:
    """Run server debugging logic (shared between configured and arbitrary servers)."""
    # For filesystem servers, provide roots based on command args
    roots = []
    if server.transport == TransportType.STDIO and server.args:
        # For filesystem server, use the directory arguments as roots
        for arg in server.args:
            # Skip npm package names and flags, look for actual paths
            if (
                not arg.startswith("-")
                and not arg.startswith("@")
                and ("/" in arg or arg in [".", "~"])
                and not arg.endswith(".js")
                and not arg.endswith(".ts")
            ):
                roots.append(arg)

    if debug and roots:
        console.print(f"[dim]Providing roots: {roots}[/dim]")

    if raw_interactions:
        console.print("[bold yellow]Raw MCP interactions will be dumped to console[/bold yellow]")

    # Create service and connect
    service = MCPService(debug=debug or raw_interactions, roots=roots)

    console.print("\n[bold yellow]Connecting...[/bold yellow]")
    try:
        await service.connect(server)
        console.print("[bold green]✓ Connected successfully[/bold green]")

        # Give server time to process initialization and set up tools
        if debug:
            console.print("[dim]Waiting for server to complete initialization and potential roots request...[/dim]")
        await asyncio.sleep(5.0)

    except Exception as e:
        console.print(f"[bold red]✗ Connection failed:[/bold red] {e}")
        return

    # Get server info
    server_info = service.server_info
    if server_info:
        console.print("\n[bold blue]Server Information:[/bold blue]")
        console.print(f"Name: {server_info.name or 'Unknown'}")
        console.print(f"Version: {server_info.version}")
        console.print(f"Protocol Version: {server_info.protocol_version}")

        if verbose:
            console.print("\n[dim]Raw ServerInfo:[/dim]")
            console.print(server_info.model_dump_json(indent=2))

    # Test resources
    console.print("\n[bold blue]Testing Resources:[/bold blue]")
    try:
        resources = await service.list_resources()
        console.print(f"Found {len(resources)} resources:")
        if resources:
            if server.id.startswith("temp-"):
                console.print(
                    "[dim]To download resources, add this server to your configuration first, then use:[/dim]"
                )
                console.print("[dim]'download-resource <server-id> \"<resource-name>\"'[/dim]\n")
            else:
                console.print(
                    f"[dim]Use 'download-resource {server.id} \"<resource-name>\"' to download any resource[/dim]\n"
                )
        for i, resource in enumerate(resources, 1):
            console.print(f"  {i}. [bold green]Name:[/bold green] [bold]{resource.name}[/bold]")
            console.print(f"     [cyan]URI:[/cyan] {resource.uri}")
            if resource.description:
                console.print(f"     [yellow]Description:[/yellow] {resource.description}")
            if resource.mime_type:
                console.print(f"     [magenta]MIME Type:[/magenta] {resource.mime_type}")
            if verbose:
                console.print("     [dim]Raw Resource:[/dim]")
                console.print(f"     {resource.model_dump_json(indent=2)}")
            console.print()
    except Exception as e:
        console.print(f"[red]Error listing resources: {e}[/red]")
        if verbose:
            import traceback

            traceback.print_exc()

    # Test tools
    console.print("[bold blue]Testing Tools:[/bold blue]")
    try:
        tools = await service.list_tools()
        console.print(f"Found {len(tools)} tools:")
        for i, tool in enumerate(tools, 1):
            console.print(f"  {i}. [bold]{tool.name}[/bold]")
            if tool.description:
                console.print(f"     Description: {tool.description}")
            console.print(f"     Parameters: {list(tool.input_schema.properties.keys())}")
            console.print(f"     Required: {tool.input_schema.required or []}")
            if verbose:
                console.print("     [dim]Raw Tool:[/dim]")
                console.print(f"     {tool.model_dump_json(indent=2)}")
            console.print()
    except Exception as e:
        console.print(f"[red]Error listing tools: {e}[/red]")
        if verbose:
            import traceback

            traceback.print_exc()

    # Test prompts
    console.print("[bold blue]Testing Prompts:[/bold blue]")
    try:
        prompts = await service.list_prompts()
        console.print(f"Found {len(prompts)} prompts:")
        for i, prompt in enumerate(prompts, 1):
            console.print(f"  {i}. [bold]{prompt.name}[/bold]")
            if prompt.description:
                console.print(f"     Description: {prompt.description}")
            if prompt.arguments:
                console.print(f"     Arguments: {[arg.name for arg in prompt.arguments]}")
                console.print(f"     Required: {prompt.get_required_args()}")
            if verbose:
                console.print("     [dim]Raw Prompt:[/dim]")
                console.print(f"     {prompt.model_dump_json(indent=2)}")
            console.print()
    except Exception as e:
        console.print(f"[red]Error listing prompts: {e}[/red]")
        if verbose:
            import traceback

            traceback.print_exc()

    # Disconnect
    console.print("[bold yellow]Disconnecting...[/bold yellow]")
    await service.disconnect()
    console.print("[bold green]✓ Disconnected[/bold green]")


async def _debug_server(server_id_or_name: str, verbose: bool, debug: bool, raw_interactions: bool) -> None:
    """Debug server connection and interactions."""
    try:
        console.print(f"[bold blue]Debugging server:[/bold blue] {server_id_or_name}")

        # Load server configuration
        server_manager = ServerManager()
        servers = server_manager.list_servers()

        # Try to find server by ID first, then by name
        server = next((s for s in servers if s.id == server_id_or_name), None)
        if not server:
            # Try to find by name (case-insensitive)
            server = next((s for s in servers if s.name.lower() == server_id_or_name.lower()), None)

        if not server:
            console.print(f"[bold red]Error:[/bold red] Server '{server_id_or_name}' not found")
            console.print("Available servers:")
            for s in servers:
                console.print(f"  - {s.id}: {s.name}")
            raise typer.Exit(code=1)

        console.print(f"[bold green]Found server:[/bold green] {server.name}")
        console.print(f"Transport: {server.transport.value}")
        if server.transport.value == "stdio":
            console.print(f"Command: {server.command} {' '.join(server.args or [])}")
        elif server.transport.value == "tcp":
            console.print(f"Address: {server.host}:{server.port}")
        elif server.transport.value == "http":
            console.print(f"URL: {server.url}")

        # Run the debug logic
        await _run_server_debug(server, verbose, debug, raw_interactions)

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


async def _download_resource(
    server_id_or_name: str, resource_name: str, output_dir: str, filename: str | None, verbose: bool, debug: bool
) -> None:
    """Download a resource by name from an MCP server."""
    import base64

    try:
        console.print(f"[bold blue]Downloading resource:[/bold blue] {resource_name}")
        console.print(f"[bold blue]From server:[/bold blue] {server_id_or_name}")

        # Load server configuration
        server_manager = ServerManager()
        servers = server_manager.list_servers()

        # Try to find server by ID first, then by name
        server = next((s for s in servers if s.id == server_id_or_name), None)
        if not server:
            # Try to find by name (case-insensitive)
            server = next((s for s in servers if s.name.lower() == server_id_or_name.lower()), None)

        if not server:
            console.print(f"[bold red]Error:[/bold red] Server '{server_id_or_name}' not found")
            console.print("Available servers:")
            for s in servers:
                console.print(f"  - {s.id}: {s.name}")
            raise typer.Exit(code=1)

        console.print(f"[bold green]Found server:[/bold green] {server.name}")

        # For filesystem servers, provide roots based on command args
        roots = []
        if server.transport == TransportType.STDIO and server.args:
            for arg in server.args:
                if (
                    not arg.startswith("-")
                    and not arg.startswith("@")
                    and ("/" in arg or arg in [".", "~"])
                    and not arg.endswith(".js")
                    and not arg.endswith(".ts")
                ):
                    roots.append(arg)

        # Create service and connect
        service = MCPService(debug=debug, roots=roots)

        console.print("\n[bold yellow]Connecting...[/bold yellow]")
        try:
            await service.connect(server)
            console.print("[bold green]✓ Connected successfully[/bold green]")
            await asyncio.sleep(2.0)  # Give server time to initialize
        except Exception as e:
            console.print(f"[bold red]✗ Connection failed:[/bold red] {e}")
            return

        # List resources to find the target
        console.print(f"\n[bold blue]Finding resource:[/bold blue] {resource_name}")
        try:
            resources = await service.list_resources()
            target_resource = None

            # Try exact name match first
            for resource in resources:
                if resource.name == resource_name:
                    target_resource = resource
                    break

            # If not found, try case-insensitive match
            if not target_resource:
                for resource in resources:
                    if resource.name.lower() == resource_name.lower():
                        target_resource = resource
                        break

            # If still not found, try partial name match
            if not target_resource:
                matches = [r for r in resources if resource_name.lower() in r.name.lower()]
                if len(matches) == 1:
                    target_resource = matches[0]
                elif len(matches) > 1:
                    console.print(f"[bold red]Error:[/bold red] Multiple resources match '{resource_name}':")
                    for match in matches:
                        console.print(f"  - {match.name}")
                    raise typer.Exit(code=1)

            if not target_resource:
                console.print(f"[bold red]Error:[/bold red] Resource '{resource_name}' not found")
                console.print("Available resources:")
                for resource in resources:
                    console.print(f"  - {resource.name}")
                raise typer.Exit(code=1)

            console.print(f"[bold green]Found resource:[/bold green] {target_resource.name}")
            if verbose:
                console.print(f"URI: {target_resource.uri}")
                console.print(f"MIME Type: {target_resource.mime_type or 'Unknown'}")
                if target_resource.description:
                    console.print(f"Description: {target_resource.description}")

        except Exception as e:
            console.print(f"[bold red]Error listing resources:[/bold red] {e}")
            return

        # Read the resource
        console.print("\n[bold blue]Reading resource content...[/bold blue]")
        try:
            result = await service.read_resource(target_resource.uri)
            if not result or "contents" not in result:
                console.print("[bold red]Error:[/bold red] No content returned from resource")
                return

            content = result.get("contents", [])
            if not content or not isinstance(content, list) or len(content) == 0:
                console.print("[bold red]Error:[/bold red] Empty or invalid content structure")
                return

            item = content[0]
            if not isinstance(item, dict):
                console.print("[bold red]Error:[/bold red] Invalid content item structure")
                return

            # Get response details
            response_name = item.get("name") or target_resource.name
            response_mime_type = item.get("mimeType") or target_resource.mime_type

            # Handle binary or text content
            blob_data = item.get("blob")
            text_data = item.get("text")

            if not blob_data and not text_data:
                console.print("[bold red]Error:[/bold red] No blob or text data found in resource")
                return

            # Determine output directory and filename
            output_path = Path(output_dir).expanduser().resolve()
            output_path.mkdir(parents=True, exist_ok=True)

            if filename:
                file_path = output_path / filename
            else:
                # Auto-detect filename and extension
                extension = _get_file_extension_for_cli(response_name, response_mime_type, blob_data)
                safe_name = _make_safe_filename_for_cli(response_name)
                file_path = output_path / f"{safe_name}{extension}"

            # Save the content
            if blob_data:
                console.print(f"[bold blue]Saving binary content to:[/bold blue] {file_path}")
                try:
                    binary_data = base64.b64decode(blob_data)
                    with open(file_path, "wb") as f:
                        f.write(binary_data)
                    console.print(f"[bold green]✓ Successfully saved {len(binary_data)} bytes[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]Error saving binary data:[/bold red] {e}")
                    return
            else:
                console.print(f"[bold blue]Saving text content to:[/bold blue] {file_path}")
                try:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(text_data or "")
                    console.print(f"[bold green]✓ Successfully saved {len(text_data or '')} characters[/bold green]")
                except Exception as e:
                    console.print(f"[bold red]Error saving text data:[/bold red] {e}")
                    return

            if verbose:
                console.print(f"File path: {file_path}")
                console.print(f"Content type: {'Binary' if blob_data else 'Text'}")
                console.print(f"MIME type: {response_mime_type or 'Unknown'}")

        except Exception as e:
            console.print(f"[bold red]Error reading resource:[/bold red] {e}")
            if verbose:
                import traceback

                traceback.print_exc()
            return

        # Disconnect
        console.print("\n[bold yellow]Disconnecting...[/bold yellow]")
        await service.disconnect()
        console.print("[bold green]✓ Resource downloaded successfully[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        raise typer.Exit(code=1)


def _get_file_extension_for_cli(resource_name: str, mime_type: str | None, blob_data: str | None) -> str:
    """Determine file extension for CLI download."""
    import mimetypes

    import filetype

    # First, try to get extension from MIME type
    if mime_type:
        extension = mimetypes.guess_extension(mime_type)
        if extension:
            return extension

    # For generic binary MIME types, try magic number detection
    if blob_data and mime_type in ["application/octet-stream", "binary/octet-stream"]:
        try:
            import base64

            binary_data = base64.b64decode(blob_data)
            detected_type = filetype.guess(binary_data)
            if detected_type:
                return f".{detected_type.extension}"
        except Exception:
            pass

    # Fallback: try to get extension from resource name
    if "." in resource_name:
        return Path(resource_name).suffix

    # Default to .txt for unknown files
    return ".txt"


def _make_safe_filename_for_cli(name: str) -> str:
    """Create a safe filename from resource name for CLI."""
    # Remove unsafe characters and limit length
    safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
    safe_name = "".join(c if c in safe_chars else "_" for c in name)

    # Remove extension if present (we'll add our own)
    if "." in safe_name:
        safe_name = Path(safe_name).stem

    # Limit length and ensure it's not empty
    safe_name = safe_name[:50] or "resource"

    return safe_name


if __name__ == "__main__":
    app()
