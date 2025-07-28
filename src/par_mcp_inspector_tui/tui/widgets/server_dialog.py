"""Server configuration dialog widget."""

import json
import uuid
from typing import TYPE_CHECKING, Any, Literal

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.validation import Number
from textual.widgets import Button, Checkbox, Input, Label, RadioButton, RadioSet, Static, TextArea

from ...models import MCPServer, TransportType

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ServerConfigDialog(ModalScreen[MCPServer | None]):
    """Modal dialog for configuring MCP servers."""

    DEFAULT_BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(
        self,
        server: MCPServer | None = None,
        mode: Literal["add", "edit"] = "add",
        **kwargs,
    ) -> None:
        """Initialize server config dialog.

        Args:
            server: Server to edit (None for new server)
            mode: Dialog mode ("add" or "edit")
        """
        super().__init__(**kwargs)
        self.server = server
        self.mode = mode
        self.dialog_title = "Edit Server" if mode == "edit" else "Add Server"

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def compose(self) -> ComposeResult:
        """Create dialog UI."""
        with Container(id="dialog-container"):
            yield Static(self.dialog_title, id="dialog-title")

            with VerticalScroll(id="form-container"):
                # Basic server info
                yield Label("Server Name:")
                yield Input(
                    placeholder="Enter server name",
                    id="server-name",
                    value=self.server.name if self.server else "",
                )

                # Transport selection
                yield Label("Transport Type:")
                yield RadioSet("STDIO", "WebSocket", "HTTP", id="transport-type")

                # STDIO configuration
                with Container(id="stdio-config", classes="transport-config"):
                    yield Label("Command:")
                    yield Input(
                        placeholder="e.g., python, npx, node",
                        id="command",
                        value=self.server.command or "" if self.server else "",
                    )

                    yield Label("Arguments (one per line):")
                    yield TextArea(
                        text="\n".join(self.server.args) if self.server and self.server.args else "",
                        id="args",
                        classes="config-textarea",
                    )

                    yield Label("Environment Variables (KEY=value, one per line):")
                    yield TextArea(
                        text=self._format_env(self.server.env) if self.server and self.server.env else "",
                        id="env",
                        classes="config-textarea",
                    )

                # WebSocket configuration
                with Container(id="tcp-config", classes="transport-config"):
                    yield Label("Host:")
                    yield Input(
                        placeholder="e.g., localhost, 127.0.0.1",
                        id="host",
                        value=self.server.host or "localhost" if self.server else "localhost",
                    )

                    yield Label("Port:")
                    yield Input(
                        placeholder="e.g., 3333",
                        id="port",
                        value=str(self.server.port) if self.server else "3333",
                        validators=[Number(minimum=1, maximum=65535)],
                    )

                # HTTP configuration
                with Container(id="http-config", classes="transport-config"):
                    yield Label("URL:")
                    yield Input(
                        placeholder="e.g., https://example.com/mcp, http://localhost:8080/mcp",
                        id="url",
                        value=self.server.url or "" if self.server else "",
                    )

                # Toast notifications configuration
                yield Label("Notification Settings:")
                yield Checkbox(
                    "Show toast notifications from this server",
                    id="toast-notifications",
                    value=self.server.toast_notifications if self.server else True,
                )

            # Copy buttons (only show in edit mode when server exists)
            if self.mode == "edit" and self.server:
                with Horizontal(id="copy-button-container", classes="copy-buttons"):
                    yield Button("Copy for Claude Desktop", id="copy-desktop-button", variant="primary")
                    yield Button("Copy for Claude Code", id="copy-code-button", variant="primary")

            # Action buttons
            with Horizontal(id="button-container"):
                yield Button("Cancel", id="cancel-button", variant="default")
                yield Button(
                    "Save" if self.mode == "edit" else "Add",
                    id="save-button",
                    variant="success",
                )

    def on_mount(self) -> None:
        """Initialize dialog when mounted."""
        # Set transport selection - handled via callback after widget is fully mounted
        self.call_after_refresh(self._set_initial_transport_selection)

        # Show/hide appropriate config sections
        self._update_transport_config()

    def _set_initial_transport_selection(self) -> None:
        """Set initial transport selection after widget is mounted."""
        transport_radio = self.query_one("#transport-type", RadioSet)
        buttons = transport_radio.query(RadioButton)

        # Use action to press the correct radio button
        if self.server:
            if self.server.transport.value == "tcp":
                # Press the WebSocket button (index 1)
                if len(buttons) > 1:
                    buttons[1].value = True
            elif self.server.transport.value == "http":
                # Press the HTTP button (index 2)
                if len(buttons) > 2:
                    buttons[2].value = True
            else:
                # Press the STDIO button (index 0) - default
                if len(buttons) > 0:
                    buttons[0].value = True
        else:
            # Press the STDIO button (index 0) - default for new servers
            if len(buttons) > 0:
                buttons[0].value = True

        # Update the transport config after setting selection
        self._update_transport_config()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle transport type change."""
        if event.radio_set.id == "transport-type":
            self._update_transport_config()

    def _update_transport_config(self) -> None:
        """Show/hide transport config sections based on selection."""
        transport_radio = self.query_one("#transport-type", RadioSet)
        stdio_config = self.query_one("#stdio-config")
        tcp_config = self.query_one("#tcp-config")
        http_config = self.query_one("#http-config")

        if transport_radio.pressed_index == 0:  # STDIO
            stdio_config.display = True
            tcp_config.display = False
            http_config.display = False
        elif transport_radio.pressed_index == 1:  # WebSocket
            stdio_config.display = False
            tcp_config.display = True
            http_config.display = False
        else:  # HTTP
            stdio_config.display = False
            tcp_config.display = False
            http_config.display = True

    def _format_env(self, env: dict[str, str] | None) -> str:
        """Format environment variables for display."""
        if not env:
            return ""
        return "\n".join(f"{k}={v}" for k, v in env.items())

    def _parse_env(self, env_text: str) -> dict[str, str]:
        """Parse environment variables from text."""
        env = {}
        for line in env_text.strip().split("\n"):
            line = line.strip()
            if "=" in line:
                key, value = line.split("=", 1)
                env[key.strip()] = value.strip()
        return env

    def _validate_form(self) -> str | None:
        """Validate form data. Returns error message or None if valid."""
        name_input = self.query_one("#server-name", Input)
        transport_radio = self.query_one("#transport-type", RadioSet)

        if not name_input.value.strip():
            return "Server name is required"

        if transport_radio.pressed_index == 0:  # STDIO
            command_input = self.query_one("#command", Input)
            if not command_input.value.strip():
                return "Command is required for STDIO transport"
        elif transport_radio.pressed_index == 1:  # WebSocket
            host_input = self.query_one("#host", Input)
            port_input = self.query_one("#port", Input)

            if not host_input.value.strip():
                return "Host is required for WebSocket transport"

            if not port_input.value.strip():
                return "Port is required for WebSocket transport"

            try:
                port = int(port_input.value)
                if port < 1 or port > 65535:
                    return "Port must be between 1 and 65535"
            except ValueError:
                return "Port must be a valid number"
        else:  # HTTP
            url_input = self.query_one("#url", Input)
            url = url_input.value.strip()

            if not url:
                return "URL is required for HTTP transport"

            # Basic URL validation
            if not (url.startswith("http://") or url.startswith("https://")):
                return "URL must start with http:// or https://"

            # Check for valid URL structure
            from urllib.parse import urlparse

            try:
                parsed = urlparse(url)
                if not parsed.netloc:
                    return "URL must include a valid hostname"
            except Exception:
                return "Invalid URL format"

        return None

    def _create_server_from_form(self) -> MCPServer:
        """Create server object from form data."""
        name_input = self.query_one("#server-name", Input)
        transport_radio = self.query_one("#transport-type", RadioSet)
        toast_checkbox = self.query_one("#toast-notifications", Checkbox)

        # Get server ID (existing for edit, new for add)
        server_id = self.server.id if self.server else str(uuid.uuid4())

        # Determine transport type
        if transport_radio.pressed_index == 0:
            transport = TransportType.STDIO
        elif transport_radio.pressed_index == 1:
            transport = TransportType.TCP
        else:
            transport = TransportType.HTTP

        # Common fields
        server_data = {
            "id": server_id,
            "name": name_input.value.strip(),
            "transport": transport,
            "toast_notifications": toast_checkbox.value,
        }

        if transport_radio.pressed_index == 0:  # STDIO
            command_input = self.query_one("#command", Input)
            args_textarea = self.query_one("#args", TextArea)
            env_textarea = self.query_one("#env", TextArea)

            server_data["command"] = command_input.value.strip()

            # Parse arguments
            args_text = args_textarea.text.strip()
            if args_text:
                server_data["args"] = [arg.strip() for arg in args_text.split("\n") if arg.strip()]

            # Parse environment variables
            env_text = env_textarea.text.strip()
            if env_text:
                server_data["env"] = self._parse_env(env_text)

        elif transport_radio.pressed_index == 1:  # WebSocket
            host_input = self.query_one("#host", Input)
            port_input = self.query_one("#port", Input)

            server_data["host"] = host_input.value.strip()
            server_data["port"] = int(port_input.value)

        else:  # HTTP
            url_input = self.query_one("#url", Input)
            server_data["url"] = url_input.value.strip()

        return MCPServer(**server_data)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.action_cancel()
        elif event.button.id == "save-button":
            self._save_server()
        elif event.button.id == "copy-desktop-button":
            self._copy_for_claude_desktop()
        elif event.button.id == "copy-code-button":
            self._copy_for_claude_code()

    def _save_server(self) -> None:
        """Save server configuration."""
        # Validate form
        error = self._validate_form()
        if error:
            self.app.notify_error(error)
            return

        try:
            # Create server from form data
            server = self._create_server_from_form()

            # Return the server to close dialog
            self.dismiss(server)

        except Exception as e:
            self.app.notify_error(f"Failed to save server: {e}")

    def action_cancel(self) -> None:
        """Cancel dialog."""
        self.dismiss(None)

    def _copy_for_claude_desktop(self) -> None:
        """Copy server config in Claude Desktop format to clipboard."""
        if not self.server:
            return

        try:
            # Create the current server config from form
            current_server = self._create_server_from_form()

            # Format for Claude Desktop config.json
            desktop_config = {current_server.name: self._server_to_desktop_config(current_server)}

            config_text = json.dumps(desktop_config, indent=2)

            # Copy to clipboard
            import pyperclip

            pyperclip.copy(config_text)

            self.app.notify_success("Server config copied to clipboard for Claude Desktop")

        except Exception as e:
            self.app.notify_error(f"Failed to copy config: {e}")

    def _copy_for_claude_code(self) -> None:
        """Copy server config in Claude Code MCP add format to clipboard."""
        if not self.server:
            return

        try:
            # Create the current server config from form
            current_server = self._create_server_from_form()

            # Format for Claude Code mcp add command: "claude mcp add <name> -- <command> [args...]"
            command_parts = ["claude", "mcp", "add", current_server.name, "--"]

            if current_server.transport == TransportType.STDIO:
                command_parts.append(current_server.command or "")

                # Add arguments
                if current_server.args:
                    command_parts.extend(current_server.args)

            elif current_server.transport == TransportType.TCP:
                # For TCP transport, we need to represent it as a command that would start a TCP server
                # This is a placeholder as TCP servers typically need custom setup
                command_parts.extend(
                    [
                        "# TCP transport not directly supported in claude mcp add",
                        f"# Host: {current_server.host or 'localhost'}",
                        f"# Port: {current_server.port or 3333}",
                    ]
                )

            elif current_server.transport == TransportType.HTTP:
                # For HTTP transport, we need to represent it as a command that would start an HTTP server
                # This is a placeholder as HTTP servers typically need custom setup
                command_parts.extend(
                    [
                        "# HTTP transport not directly supported in claude mcp add",
                        f"# URL: {current_server.url or ''}",
                    ]
                )

            command_text = " ".join(command_parts)

            # Copy to clipboard
            import pyperclip

            pyperclip.copy(command_text)

            self.app.notify_success("MCP add command copied to clipboard for Claude Code")

        except Exception as e:
            self.app.notify_error(f"Failed to copy command: {e}")

    def _server_to_desktop_config(self, server: MCPServer) -> dict[str, Any]:
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
