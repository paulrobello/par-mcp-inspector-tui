"""Roots view widget for managing MCP filesystem roots."""

import os
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from ...models import Root, RootInfo
from ...services import MCPService

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class RootItem(ListItem):
    """Individual root item."""

    def __init__(self, root_info: RootInfo) -> None:
        """Initialize root item."""
        super().__init__()
        self.root_info = root_info

    def compose(self) -> ComposeResult:
        """Create root item display."""
        root = self.root_info.root

        # Extract path from file:// URI for display
        parsed = urlparse(root.uri)
        path = parsed.path if parsed.scheme == "file" else root.uri

        # Status indicator
        status = "✓" if self.root_info.accessible else "✗" if self.root_info.exists else "?"

        # Build display text with status, name/path, and type info
        if root.name:
            # Use custom name if provided
            display_name = root.name
            show_path = True
        else:
            # Use the path itself as display name
            display_name = path
            show_path = False

        type_info = f" ({self.root_info.type})" if self.root_info.type != "unknown" else ""

        # Create main display line
        main_text = f"{status} {display_name}{type_info}"

        yield Label(main_text, classes="root-main")
        if show_path:
            yield Label(f"  → {path}", classes="root-path")


class RootsView(Widget, can_focus_children=True):
    """View for displaying and managing filesystem roots."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize roots view."""
        super().__init__(**kwargs)
        self.mcp_service = mcp_service
        self.roots: list[Root] = []
        self.root_infos: list[RootInfo] = []
        self.selected_root: Root | None = None

        # Add CSS classes for styling
        self.add_class("roots-view")

    def compose(self) -> ComposeResult:
        """Create roots view UI."""
        yield Vertical(
            # Roots list
            ListView(id="roots-list", classes="item-list-with-title-roots"),
            # Status display
            Static("Loading roots...", id="root-status", classes="root-status"),
            # Add new root controls
            Horizontal(
                Input(placeholder="Enter path or file:// URI", id="root-path-input"),
                Input(placeholder="Display name (optional)", id="root-name-input"),
                classes="root-input-row",
            ),
            # Action buttons
            Horizontal(
                Button("Add Root", id="add-root-button"),
                Button("Remove Root", id="remove-root-button", disabled=True),
                Button("Refresh", id="refresh-roots-button"),
                classes="root-buttons",
            ),
        )

    async def on_mount(self) -> None:
        """Initialize when mounted."""
        # Set border title for roots list
        roots_list = self.query_one("#roots-list", ListView)
        roots_list.border_title = "Filesystem Roots"

        # Refresh roots on mount
        self.refresh()

    @work
    async def refresh(self, **kwargs) -> None:
        """Refresh roots from service."""
        if not self.mcp_service.connected:
            self.roots = []
            self.root_infos = []
            self.call_later(self._update_display)
            return

        try:
            # Get current roots from service
            self.roots = await self.mcp_service.get_roots()

            # Build root info for each root
            self.root_infos = []
            for root in self.roots:
                info = await self._build_root_info(root)
                self.root_infos.append(info)

            # Schedule UI update on main thread
            self.call_later(self._update_display)
            self.call_later(self._update_status)
        except Exception as e:
            self.app.notify_error(f"Failed to fetch roots: {e}")

    async def _build_root_info(self, root: Root) -> RootInfo:
        """Build extended information for a root."""
        info = RootInfo(root=root, size=None, modified=None)

        try:
            # Parse URI to get local path
            parsed = urlparse(root.uri)
            if parsed.scheme == "file":
                path = Path(parsed.path)

                info.exists = path.exists()
                if info.exists:
                    info.accessible = os.access(path, os.R_OK)
                    if path.is_file():
                        info.type = "file"
                        info.size = path.stat().st_size
                    elif path.is_dir():
                        info.type = "directory"
                    else:
                        info.type = "other"

                    info.modified = path.stat().st_mtime_ns
        except Exception:
            # If we can't analyze the root, mark as unknown
            pass

        return info

    def clear_data(self) -> None:
        """Clear all roots data and display."""
        self.roots = []
        self.root_infos = []
        self.selected_root = None
        self._update_display()
        self._update_buttons()

    def _update_display(self) -> None:
        """Update the roots display."""
        roots_list = self.query_one("#roots-list", ListView)
        roots_list.clear()

        for root_info in self.root_infos:
            item = RootItem(root_info)
            roots_list.append(item)

    def _update_buttons(self) -> None:
        """Update button states."""
        remove_button = self.query_one("#remove-root-button", Button)
        remove_button.disabled = self.selected_root is None

    def _update_status(self) -> None:
        """Update status display."""
        status_widget = self.query_one("#root-status", Static)

        if not self.root_infos:
            status_widget.update("No roots configured")
            return

        accessible_count = sum(1 for info in self.root_infos if info.accessible)
        total_count = len(self.root_infos)

        status_widget.update(f"{accessible_count}/{total_count} roots accessible")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle root selection."""
        if event.list_view.id == "roots-list" and event.item is not None:
            if isinstance(event.item, RootItem):
                self.selected_root = event.item.root_info.root
                self._update_buttons()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "add-root-button":
            await self._add_root()
        elif event.button.id == "remove-root-button":
            await self._remove_root()
        elif event.button.id == "refresh-roots-button":
            self.refresh()

    async def _add_root(self) -> None:
        """Add a new root."""
        path_input = self.query_one("#root-path-input", Input)
        name_input = self.query_one("#root-name-input", Input)

        path_str = path_input.value.strip()
        name_str = name_input.value.strip()

        if not path_str:
            self.app.notify_error("Please enter a path or URI")
            return

        try:
            # Convert to file:// URI if needed
            if not path_str.startswith("file://"):
                # Assume it's a local path
                abs_path = Path(path_str).resolve()
                uri = f"file://{abs_path}"
            else:
                uri = path_str

            # Create root
            root = Root(uri=uri, name=name_str or None)

            # Add to service
            await self.mcp_service.add_root(root)

            # Clear inputs
            path_input.value = ""
            name_input.value = ""

            # Refresh display
            self.refresh()

            self.app.notify_info(f"Added root: {root.name or uri}")
        except Exception as e:
            self.app.notify_error(f"Failed to add root: {e}")

    async def _remove_root(self) -> None:
        """Remove the selected root."""
        if self.selected_root is None:
            return

        try:
            await self.mcp_service.remove_root(self.selected_root)
            self.selected_root = None
            self.refresh()
            self.app.notify_info("Root removed")
        except Exception as e:
            self.app.notify_error(f"Failed to remove root: {e}")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        if event.input.id in ["root-path-input", "root-name-input"]:
            await self._add_root()
