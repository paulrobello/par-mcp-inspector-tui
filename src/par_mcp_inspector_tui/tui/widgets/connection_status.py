"""Connection status widget."""

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from ...models import ServerState
from ...services import MCPService


class ConnectionStatus(Widget):
    """Widget showing current connection status."""

    status = reactive(ServerState.DISCONNECTED)

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize connection status widget."""
        super().__init__(**kwargs)
        self.mcp_service = mcp_service

    def compose(self) -> ComposeResult:
        """Create status display."""
        yield Label("Connection Status", classes="status-title")
        yield Static("", id="status-text")
        yield Static("", id="server-info")

    def on_mount(self) -> None:
        """Initialize when mounted."""
        self.mcp_service.on_state_change(self._update_status)
        self._update_display()

    def _update_status(self, state: ServerState) -> None:
        """Update status from service."""
        self.status = state
        self._update_display()

    def _update_display(self) -> None:
        """Update the status display."""
        try:
            status_text = self.query_one("#status-text", Static)
            server_info = self.query_one("#server-info", Static)
        except Exception:
            # Widget may be unmounted during shutdown
            return

        # Update status text and styling
        if self.status == ServerState.CONNECTED:
            status_text.update("● Connected")
            status_text.add_class("status-connected")
            status_text.remove_class("status-disconnected", "status-error", "status-connecting")

            # Show server info
            if self.mcp_service.server_info:
                info = self.mcp_service.server_info
                name = info.name or "Unknown Server"
                server_info.update(f"{name} v{info.version}")
            else:
                server_info.update("")

        elif self.status == ServerState.CONNECTING:
            status_text.update("◐ Connecting...")
            status_text.add_class("status-connecting")
            status_text.remove_class("status-connected", "status-disconnected", "status-error")
            server_info.update("")

        elif self.status == ServerState.ERROR:
            status_text.update("✗ Error")
            status_text.add_class("status-error")
            status_text.remove_class("status-connected", "status-disconnected", "status-connecting")

            # Show error message
            if self.mcp_service.server and self.mcp_service.server.error:
                server_info.update(self.mcp_service.server.error[:50] + "...")
            else:
                server_info.update("")

        else:  # DISCONNECTED
            status_text.update("○ Disconnected")
            status_text.add_class("status-disconnected")
            status_text.remove_class("status-connected", "status-error", "status-connecting")
            server_info.update("")
