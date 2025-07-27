"""Server panel widget for managing MCP server connections."""

from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView

from ...models import MCPServer, ServerState
from ...services import MCPService, ServerManager

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ServerItem(ListItem):
    """Individual server item in the list."""

    def __init__(self, server: MCPServer) -> None:
        """Initialize server item."""
        super().__init__()
        self.server = server
        self._update_display()

    def _update_display(self) -> None:
        """Update the display based on server state."""
        self.remove_class("connected", "error")
        if self.server.state == ServerState.CONNECTED:
            self.add_class("connected")
        elif self.server.state == ServerState.ERROR:
            self.add_class("error")

    def compose(self) -> ComposeResult:
        """Create server item display."""
        status_icon = {
            ServerState.CONNECTED: "● ",
            ServerState.CONNECTING: "◐ ",
            ServerState.DISCONNECTED: "○ ",
            ServerState.ERROR: "✗ ",
        }.get(self.server.state, "○ ")

        transport = f"[{self.server.transport.value.upper()}]"

        yield Label(f"{status_icon}{self.server.name} {transport}")


class ServerPanel(Widget):
    """Panel for managing server connections."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, server_manager: ServerManager, mcp_service: MCPService, **kwargs) -> None:
        """Initialize server panel."""
        super().__init__(**kwargs)
        self.server_manager = server_manager
        self.mcp_service = mcp_service
        self.selected_server: MCPServer | None = None

    def compose(self) -> ComposeResult:
        """Create server panel UI."""
        yield Label("MCP Servers", classes="panel-title")

        # ListView already extends VerticalScroll - no wrapper needed
        yield ListView(id="server-list", classes="server-list")

        with VerticalScroll():
            yield Button("Connect", id="connect-button", classes="connection-button", disabled=True)
            yield Button("Add Server", id="add-server-button", variant="primary")
            yield Button("Edit Server", id="edit-server-button", disabled=True)
            yield Button("Delete Server", id="delete-server-button", variant="error", disabled=True)

    def on_mount(self) -> None:
        """Initialize when mounted."""
        self._refresh_server_list()
        self.mcp_service.on_state_change(self._on_server_state_change)

    def _refresh_server_list(self) -> None:
        """Refresh the server list display."""
        server_list = self.query_one("#server-list", ListView)
        selected_server_id = self.selected_server.id if self.selected_server else None

        server_list.clear()
        selected_index = None

        for i, server in enumerate(self.server_manager.list_servers()):
            server_list.append(ServerItem(server))
            # Track which server should be selected
            if selected_server_id and server.id == selected_server_id:
                # Update the selected_server reference to the fresh server object
                self.selected_server = server
                selected_index = i

        # Restore the selection after all items are added
        if selected_index is not None:
            self.call_after_refresh(lambda: self._restore_selection(selected_index))

    def _restore_selection(self, index: int) -> None:
        """Restore the selection to the specified index."""
        try:
            server_list = self.query_one("#server-list", ListView)
            if index < len(server_list.children):
                server_list.index = index
                # Trigger the selection event manually to update buttons
                self._update_buttons()
        except Exception:
            # If restoration fails, just update buttons anyway
            self._update_buttons()

    def _on_server_state_change(self, state: ServerState) -> None:
        """Handle server state changes."""
        # Update button states
        self._update_buttons()

        # Update server item displays - but only if widget is still mounted
        try:
            server_list = self.query_one("#server-list", ListView)
            for item in server_list.children:
                if isinstance(item, ServerItem):
                    item._update_display()
        except Exception:
            # Widget may be unmounted or not yet fully composed
            pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle server selection."""
        if isinstance(event.item, ServerItem):
            self.selected_server = event.item.server
            self._update_buttons()

    def _update_buttons(self) -> None:
        """Update button states based on selection."""
        try:
            connect_btn = self.query_one("#connect-button", Button)
            edit_btn = self.query_one("#edit-server-button", Button)
            delete_btn = self.query_one("#delete-server-button", Button)
        except Exception:
            # Widgets may be unmounted during shutdown
            return

        if self.selected_server:
            edit_btn.disabled = False
            delete_btn.disabled = False

            if self.mcp_service.connected and self.mcp_service.server == self.selected_server:
                connect_btn.label = "Disconnect"
                connect_btn.disabled = False
                connect_btn.variant = "error"
            else:
                connect_btn.label = "Connect"
                connect_btn.disabled = False
                connect_btn.variant = "success"
        else:
            connect_btn.disabled = True
            edit_btn.disabled = True
            delete_btn.disabled = True

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "connect-button":
            await self._handle_connect_button()
        elif event.button.id == "add-server-button":
            await self._show_add_server_dialog()
        elif event.button.id == "edit-server-button":
            await self._show_edit_server_dialog()
        elif event.button.id == "delete-server-button":
            await self._handle_delete_server()

    async def _handle_connect_button(self) -> None:
        """Handle connect/disconnect button press."""
        if not self.selected_server:
            return

        try:
            if self.mcp_service.connected and self.mcp_service.server == self.selected_server:
                # Disconnect
                await self.mcp_service.disconnect()
                self.app.notify_info("Disconnected from server")
            else:
                # Connect
                self.app.notify_info(f"Connecting to {self.selected_server.name}...")

                # Update MCP service with appropriate roots for this server
                self.app.update_mcp_service_with_roots(self.selected_server)

                # Update our reference to the potentially new service
                self.mcp_service = self.app.mcp_service

                await self.mcp_service.connect(self.selected_server)
        except Exception as e:
            self.app.notify_error(f"Connection failed: {e}")

    async def _show_add_server_dialog(self) -> None:
        """Show dialog to add a new server."""
        from .server_dialog import ServerConfigDialog

        result = await self.app.push_screen_wait(ServerConfigDialog(mode="add"))

        if result:
            # Add the new server
            self.server_manager.add_server(result)
            # Set the newly added server as selected
            self.selected_server = result
            self._refresh_server_list()
            self.app.notify_success(f"Added server: {result.name}")

    async def _show_edit_server_dialog(self) -> None:
        """Show dialog to edit selected server."""
        if not self.selected_server:
            return

        from .server_dialog import ServerConfigDialog

        result = await self.app.push_screen_wait(ServerConfigDialog(server=self.selected_server, mode="edit"))

        if result:
            # Update the server
            self.server_manager.update_server(result)
            # Update the selected server reference to the new updated server
            self.selected_server = result
            self._refresh_server_list()
            self.app.notify_success(f"Updated server: {result.name}")

    async def _handle_delete_server(self) -> None:
        """Handle delete server button press."""
        if not self.selected_server:
            return

        # Check if server is currently connected
        if self.mcp_service.connected and self.mcp_service.server == self.selected_server:
            self.app.notify_error("Cannot delete connected server. Disconnect first.")
            return

        # Confirm deletion
        server_name = self.selected_server.name
        confirmed = await self.app.push_screen_wait(
            self.app._create_confirmation_dialog(
                "Delete Server",
                f"Are you sure you want to delete '{server_name}'?\nThis action cannot be undone.",
            )
        )

        if confirmed:
            # Delete the server
            self.server_manager.remove_server(self.selected_server.id)
            self.selected_server = None
            self._refresh_server_list()
            self._update_buttons()
            self.app.notify_success(f"Deleted server: {server_name}")
