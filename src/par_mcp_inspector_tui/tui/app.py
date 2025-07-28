"""MCP Inspector TUI Application."""

import logging
from datetime import datetime
from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, TabbedContent, TabPane

from .. import __application_title__, __version__
from ..models import MCPServer, ServerNotification, ServerNotificationType, ServerState
from ..services import MCPService, ServerManager
from .widgets.connection_status import ConnectionStatus
from .widgets.notification_panel import NotificationPanel
from .widgets.prompts_view import PromptsView
from .widgets.raw_interactions_view import RawInteractionsView
from .widgets.resources_view import ResourcesView
from .widgets.response_viewer import ResponseViewer
from .widgets.roots_view import RootsView
from .widgets.server_panel import ServerPanel
from .widgets.tools_view import ToolsView


class MCPInspectorApp(App[None]):
    """Main TUI application for MCP Inspector with real-time server notifications.

    Features:
    - Server connection management with STDIO and TCP transport support
    - Real-time server notifications with automatic UI refresh capabilities
    - Interactive tools, resources, and prompts exploration
    - Form validation with smart execute button control
    - File download with automatic type detection using magic numbers
    - Comprehensive error handling and user feedback
    """

    CSS_PATH = "app.tcss"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle dark mode"),
        ("s", "focus_servers", "Focus servers"),
        ("p", "toggle_server_panel", "Toggle server panel"),
        ("r", "refresh", "Refresh"),
    ]

    def __init__(self, debug: bool = False) -> None:
        """Initialize the application.

        Args:
            debug: Whether to enable debug logging to file
        """
        super().__init__()
        self.mcp_service = MCPService(debug=debug)
        self.server_manager = ServerManager()
        self.notification_panel = NotificationPanel()
        self.raw_interactions_view = RawInteractionsView(self.mcp_service)
        self.debug_enabled = debug
        self._shutting_down = False
        self.server_panel_visible = True  # Default to open

        # Set up debug logging to file only if debug is enabled
        if debug:
            self._setup_debug_logging()

    def _setup_debug_logging(self) -> None:
        """Set up debug logging to file."""
        # Create logs directory if it doesn't exist
        log_dir = Path.cwd() / "logs"
        log_dir.mkdir(exist_ok=True)

        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"mcp_inspector_debug_{timestamp}.log"

        # Set up file logger
        self.debug_logger = logging.getLogger("mcp_inspector_debug")
        self.debug_logger.setLevel(logging.DEBUG)

        # Remove any existing handlers
        for handler in self.debug_logger.handlers[:]:
            self.debug_logger.removeHandler(handler)

        # Add file handler
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Create detailed formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
        file_handler.setFormatter(formatter)

        self.debug_logger.addHandler(file_handler)

        # Log the startup
        self.debug_logger.info(f"MCP Inspector TUI started - Log file: {log_file}")
        print(f"Debug logging enabled - Log file: {log_file}")

    def debug_log(self, message: str, level: str = "info") -> None:
        """Log a debug message to file.

        Args:
            message: The message to log
            level: Log level (debug, info, warning, error)
        """
        if self.debug_enabled and hasattr(self, "debug_logger"):
            log_func = getattr(self.debug_logger, level.lower(), self.debug_logger.info)
            log_func(message)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        self.title = f"{__application_title__} v{__version__}"

        yield Header()

        # Docked server panel on the left
        with Vertical(id="docked-server-panel"):
            yield ServerPanel(self.server_manager, self.mcp_service, id="server-panel")
            yield ConnectionStatus(self.mcp_service, id="connection-status")

        with Horizontal(id="main-layout"):
            # Center panel - Tabbed content
            with TabbedContent(id="main-tabs"):
                with TabPane("Resources", id="resources-tab"):
                    yield ResourcesView(self.mcp_service, id="resources-view")

                with TabPane("Prompts", id="prompts-tab"):
                    yield PromptsView(self.mcp_service, id="prompts-view")

                with TabPane("Tools", id="tools-tab"):
                    yield ToolsView(self.mcp_service, id="tools-view")

                with TabPane("Roots", id="roots-tab"):
                    yield RootsView(self.mcp_service, id="roots-view")

                with TabPane("Raw Interactions", id="raw-interactions-tab"):
                    yield self.raw_interactions_view

                with TabPane("Notifications", id="notifications-tab"):
                    yield self.notification_panel

            # Right panel - MCP Interactions/Response Viewer
            yield ResponseViewer(id="response-viewer")

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        self.notify_info(f"Welcome to {__application_title__} v{__version__}")

        # Set up notification forwarding
        self.mcp_service.on_state_change(self._on_connection_state_change)
        self.mcp_service.on_server_notification(self._on_server_notification)
        self.mcp_service.on_interaction(self._on_interaction)

        if self.debug_enabled:
            self.debug_log("Registered interaction callback in on_mount")

    async def on_unmount(self) -> None:
        """Clean up when app is shutting down."""
        # Set shutdown flag to suppress callbacks during teardown
        self._shutting_down = True

        if self.debug:
            self.debug_log("App shutting down, disconnecting from MCP server...")

        # Disconnect from MCP server to clean up subprocess connections
        if self.mcp_service.connected:
            try:
                await self.mcp_service.disconnect()
                if self.debug:
                    self.debug_log("Successfully disconnected from MCP server")
            except Exception as e:
                if self.debug:
                    self.debug_log(f"Error during shutdown disconnect: {e}")

        # Small delay to allow async cleanup to complete
        import asyncio

        await asyncio.sleep(0.1)

    def _on_connection_state_change(self, state: ServerState) -> None:
        """Handle connection state changes."""
        # Skip callbacks during shutdown to avoid UI update errors
        if self._shutting_down:
            return

        if state == ServerState.CONNECTED:
            self.notify_success("Connected to MCP server")
            self._refresh_server_data()
        elif state == ServerState.DISCONNECTED:
            self.notify_info("Disconnected from MCP server")
            self._clear_all_tabs()
        elif state == ServerState.ERROR:
            self.notify_error("Connection error")
            self._clear_all_tabs()

    def _clear_all_tabs(self) -> None:
        """Clear all tab content when disconnecting from server."""
        try:
            # Clear resources view
            resources_view = self.query_one("#resources-view", ResourcesView)
            resources_view.clear_data()
        except Exception:
            pass  # Widget might not be mounted yet

        try:
            # Clear tools view
            tools_view = self.query_one("#tools-view", ToolsView)
            tools_view.clear_data()
        except Exception:
            pass  # Widget might not be mounted yet

        try:
            # Clear prompts view
            prompts_view = self.query_one("#prompts-view", PromptsView)
            prompts_view.clear_data()
        except Exception:
            pass  # Widget might not be mounted yet

        try:
            # Clear roots view
            roots_view = self.query_one("#roots-view", RootsView)
            roots_view.clear_data()
        except Exception:
            pass  # Widget might not be mounted yet

        try:
            # Clear response viewer
            response_viewer = self.query_one("#response-viewer", ResponseViewer)
            response_viewer.clear()
        except Exception:
            pass  # Widget might not be mounted yet

        try:
            # Clear raw interactions view
            self.raw_interactions_view.clear_data()
        except Exception:
            pass  # Widget might not be mounted yet

    def _on_server_notification(self, server_notification: ServerNotification) -> None:
        """Handle server notification callback from MCP service.

        Processes incoming server notifications and triggers appropriate UI updates:
        - list_changed notifications trigger auto-refresh of relevant views
        - message notifications are displayed in the notifications panel
        - All notifications are shown with server context and timestamp
        - Toast notifications respect server config and current tab
        """
        # Skip callbacks during shutdown to avoid UI update errors
        if self._shutting_down:
            return

        # Add to notification panel
        self.notification_panel.add_server_notification(server_notification)

        # Show system notification only if configured and not on notifications tab
        should_show_toast = self._should_show_notification_toast()
        if should_show_toast:
            self.notify(server_notification.message, severity="information", markup=False)

        # Trigger auto-refresh for list_changed notifications
        self._handle_list_changed_notification(server_notification)

    def _on_interaction(self, message: str, interaction_type: str, timestamp: datetime) -> None:
        """Handle raw MCP interaction callback from MCP service.

        Args:
            message: Raw JSON message
            interaction_type: Whether this was sent or received
            timestamp: When the interaction occurred
        """
        # Skip callbacks during shutdown to avoid UI update errors
        if self._shutting_down:
            return

        if self.debug_enabled:
            self.debug_log(f"App _on_interaction: {interaction_type} - {message[:50]}...")

        # Add to raw interactions view
        try:
            from typing import cast

            from .widgets.raw_interactions_view import InteractionType

            interaction_type_typed = cast(InteractionType, interaction_type)
            self.raw_interactions_view.add_interaction(message, interaction_type_typed, timestamp)
        except Exception as e:
            if self.debug_enabled:
                self.debug_log(f"Error adding interaction: {e}", "error")

    def _should_show_notification_toast(self) -> bool:
        """Check if notification toasts should be shown.

        Returns False if:
        - Server has toast_notifications disabled
        - User is currently viewing the notifications tab

        Returns:
            bool: True if toast should be shown, False otherwise
        """
        # Check server configuration
        if self.mcp_service.server and not self.mcp_service.server.toast_notifications:
            return False

        # Check if currently on notifications tab
        try:
            main_tabs = self.query_one("#main-tabs", TabbedContent)
            if main_tabs.active == "notifications-tab":
                return False
        except Exception:
            # If we can't determine the current tab, default to showing toasts
            pass

        return True

    @work
    async def _refresh_server_data(self) -> None:
        """Refresh data from connected server."""
        try:
            # Refresh all views
            resources_view = self.query_one("#resources-view", ResourcesView)
            resources_view.refresh()

            prompts_view = self.query_one("#prompts-view", PromptsView)
            prompts_view.refresh()

            tools_view = self.query_one("#tools-view", ToolsView)
            tools_view.refresh()

            roots_view = self.query_one("#roots-view", RootsView)
            roots_view.refresh()

        except Exception as e:
            self.notify_error(f"Failed to refresh data: {e}")
            import traceback

            traceback.print_exc()

    def _handle_list_changed_notification(self, server_notification: ServerNotification) -> None:
        """Handle list changed notification by auto-refreshing relevant view.

        Automatically refreshes the appropriate tab when servers notify about changes:
        - tools/list_changed: Refreshes tools view
        - resources/list_changed: Refreshes resources view
        - prompts/list_changed: Refreshes prompts view
        - roots/list_changed: Refreshes roots view

        Shows success notifications when refresh completes successfully.
        """
        notification_type = server_notification.notification_type

        if notification_type == ServerNotificationType.TOOLS_LIST_CHANGED:
            self._auto_refresh_tools()
        elif notification_type == ServerNotificationType.RESOURCES_LIST_CHANGED:
            self._auto_refresh_resources()
        elif notification_type == ServerNotificationType.PROMPTS_LIST_CHANGED:
            self._auto_refresh_prompts()
        elif notification_type == ServerNotificationType.ROOTS_LIST_CHANGED:
            self._auto_refresh_roots()
        elif notification_type == ServerNotificationType.MESSAGE:
            # Message notifications don't trigger refreshes, just display
            pass

    @work
    async def _auto_refresh_tools(self) -> None:
        """Auto-refresh tools view."""
        try:
            tools_view = self.query_one("#tools-view", ToolsView)
            tools_view.refresh()
            self.notify_info("Tools list refreshed automatically")
        except Exception as e:
            self.debug_log(f"Failed to auto-refresh tools: {e}", "error")

    @work
    async def _auto_refresh_resources(self) -> None:
        """Auto-refresh resources view."""
        try:
            resources_view = self.query_one("#resources-view", ResourcesView)
            resources_view.refresh()
            self.notify_info("Resources list refreshed automatically")
        except Exception as e:
            self.debug_log(f"Failed to auto-refresh resources: {e}", "error")

    @work
    async def _auto_refresh_prompts(self) -> None:
        """Auto-refresh prompts view."""
        try:
            prompts_view = self.query_one("#prompts-view", PromptsView)
            prompts_view.refresh()
            self.notify_info("Prompts list refreshed automatically")
        except Exception as e:
            self.debug_log(f"Failed to auto-refresh prompts: {e}", "error")

    @work
    async def _auto_refresh_roots(self) -> None:
        """Auto-refresh roots view."""
        try:
            roots_view = self.query_one("#roots-view", RootsView)
            roots_view.refresh()
            self.notify_info("Roots list refreshed automatically")
        except Exception as e:
            self.debug_log(f"Failed to auto-refresh roots: {e}", "error")

    def action_focus_servers(self) -> None:
        """Focus the server panel."""
        if not self.server_panel_visible:
            self.action_toggle_server_panel()
        self.query_exactly_one("#server-list").focus()

    def action_toggle_server_panel(self) -> None:
        """Toggle the visibility of the server panel."""
        self.server_panel_visible = not self.server_panel_visible
        panel = self.query_one("#docked-server-panel")
        if self.server_panel_visible:
            panel.styles.display = "block"
        else:
            panel.styles.display = "none"

    def action_refresh(self) -> None:
        """Refresh server data."""
        if self.mcp_service.connected:
            self._refresh_server_data()
        else:
            self.notify_warning("Not connected to any server")

    def notify_info(self, message: str) -> None:
        """Show info notification."""
        self.notification_panel.add_notification(message, "info")
        self.notify(message, severity="information", markup=False)

    def notify_success(self, message: str) -> None:
        """Show success notification."""
        self.notification_panel.add_notification(message, "success")
        self.notify(message, severity="information", markup=False)

    def notify_warning(self, message: str) -> None:
        """Show warning notification."""
        self.notification_panel.add_notification(message, "warning")
        self.notify(message, severity="warning", markup=False)

    def notify_error(self, message: str) -> None:
        """Show error notification."""
        self.notification_panel.add_notification(message, "error")
        self.notify(message, severity="error", markup=False)

    def show_response(self, title: str, content: str, content_type: str = "json") -> None:
        """Show a response in the response viewer."""
        self.debug_log(
            f"show_response called: title='{title}', content_type='{content_type}', content_len={len(content)}"
        )
        try:
            response_viewer = self.query_one("#response-viewer", ResponseViewer)
            self.debug_log(f"Found response viewer: {response_viewer}")
            response_viewer.show_response(title, content, content_type)
            self.debug_log("Called show_response on viewer - content now displayed in right panel")
        except Exception as e:
            self.debug_log(f"Error in show_response: {e}", "error")
            import traceback

            self.debug_log(f"Traceback: {traceback.format_exc()}", "error")

    def update_mcp_service_with_roots(self, server: "MCPServer") -> None:
        """Update MCP service with appropriate roots for the server."""
        # Determine roots based on server configuration
        roots = []
        if server.transport.value == "stdio" and server.args:
            # For filesystem server, extract directory paths from args
            for arg in server.args:
                # Skip npm package names, flags, and script files - look for actual paths
                if (
                    not arg.startswith("-")
                    and not arg.startswith("@")
                    and ("/" in arg or arg in [".", "~"])
                    and not arg.endswith(".js")
                    and not arg.endswith(".ts")
                ):
                    roots.append(arg)

        # Create new service with roots if different from current
        current_roots = getattr(self.mcp_service, "_roots", [])
        if roots != current_roots:
            # Preserve debug setting if any
            debug = getattr(self.mcp_service, "_debug", False)
            old_service = self.mcp_service

            # Create new service with roots
            self.mcp_service = MCPService(debug=debug, roots=roots)

            # Transfer state callbacks from old service
            if hasattr(old_service, "_state_callbacks"):
                for callback in old_service._state_callbacks:
                    self.mcp_service.on_state_change(callback)

            # Transfer notification callbacks from old service
            if hasattr(old_service, "_notification_callbacks"):
                for callback in old_service._notification_callbacks:
                    self.mcp_service.on_server_notification(callback)

            # Transfer interaction callbacks from old service
            if hasattr(old_service, "_interaction_callbacks"):
                for callback in old_service._interaction_callbacks:
                    self.mcp_service.on_interaction(callback)

            # Update all widgets with new service
            self._update_widgets_with_service()

    def _update_widgets_with_service(self) -> None:
        """Update all widgets to use the new MCP service."""
        try:
            # Update server panel
            server_panel = self.query_one("#server-panel", ServerPanel)
            server_panel.mcp_service = self.mcp_service

            # Update connection status
            connection_status = self.query_one("#connection-status", ConnectionStatus)
            connection_status.mcp_service = self.mcp_service

            # Update view widgets - schedule refresh on main thread
            resources_view = self.query_one("#resources-view", ResourcesView)
            resources_view.mcp_service = self.mcp_service
            self.call_later(resources_view.refresh)

            prompts_view = self.query_one("#prompts-view", PromptsView)
            prompts_view.mcp_service = self.mcp_service
            self.call_later(prompts_view.refresh)

            tools_view = self.query_one("#tools-view", ToolsView)
            tools_view.mcp_service = self.mcp_service
            self.call_later(tools_view.refresh)

            roots_view = self.query_one("#roots-view", RootsView)
            roots_view.mcp_service = self.mcp_service
            self.call_later(roots_view.refresh)

            # Update raw interactions view
            self.raw_interactions_view.mcp_service = self.mcp_service

        except Exception:
            # Widgets might not be mounted yet, that's OK
            pass

    def _create_confirmation_dialog(self, title: str, message: str):
        """Create a confirmation dialog."""
        from .widgets.confirmation_dialog import ConfirmationDialog

        return ConfirmationDialog(title, message)
