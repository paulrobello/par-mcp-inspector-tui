"""Raw interactions view widget for displaying MCP protocol messages."""

import json
import re
from datetime import datetime
from typing import Literal

from rich.json import JSON
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

from ...services import MCPService

InteractionType = Literal["sent", "received"]


class InteractionItem(Widget):
    """Individual interaction item."""

    def __init__(
        self,
        message: str,
        interaction_type: InteractionType,
        timestamp: "datetime | None" = None,
        **kwargs,
    ) -> None:
        """Initialize interaction item.

        Args:
            message: Raw JSON message content
            interaction_type: Whether this was sent or received
            timestamp: When the interaction occurred
        """
        super().__init__(**kwargs)
        self.message = message
        self.interaction_type = interaction_type
        self.timestamp = timestamp or datetime.now()
        self.add_class("interaction-item")
        self.add_class(interaction_type)
        # Make the item focusable and clickable
        self.can_focus = True

    def compose(self) -> ComposeResult:
        """Create interaction display."""
        # Format icon and direction
        icon = "→" if self.interaction_type == "sent" else "←"
        direction = "SENT" if self.interaction_type == "sent" else "RECEIVED"

        # Create time label with direction
        time_text = f"{icon} {self.timestamp.strftime('%H:%M:%S.%f')[:-3]} {direction}"

        yield Label(time_text, classes="interaction-time")

        # Pretty-print JSON with syntax highlighting if possible, otherwise show raw
        try:
            parsed = json.loads(self.message.strip())
            # Use Rich's JSON formatter for syntax highlighting
            json_renderable = JSON(json.dumps(parsed, indent=2))
            yield Static(json_renderable, classes="interaction-message")
        except json.JSONDecodeError:
            yield Static(self.message, classes="interaction-message", markup=False)


class RawInteractionsView(Widget):
    """View for displaying raw MCP protocol interactions.

    Features:
    - Shows all sent and received JSON-RPC messages
    - Chronological ordering (newest first)
    - Pretty-printed JSON formatting
    - Direction indicators (sent/received)
    - Memory management (limits to 200 interactions)
    - Auto-scroll to latest messages
    """

    interaction_count = reactive(0)

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize raw interactions view.

        Args:
            mcp_service: MCP service to monitor for interactions
        """
        super().__init__(**kwargs)
        self.mcp_service = mcp_service
        self._all_interactions: list[tuple[str, InteractionType, datetime]] = []

    def compose(self) -> ComposeResult:
        """Create raw interactions UI."""
        with Horizontal(classes="panel-header"):
            yield Label("Raw MCP Interactions", classes="panel-title")
            yield Button("Clear", id="clear-interactions", classes="clear-button")
        with Horizontal(classes="search-header"):
            yield Input(placeholder="Regex search interactions...", id="search-input", classes="search-input")
        with VerticalScroll(id="interactions-list"):
            yield Static("No interactions yet", id="empty-message", classes="empty-message")

    def add_interaction(
        self,
        message: str,
        interaction_type: InteractionType,
        timestamp: "datetime | None" = None,
    ) -> None:
        """Add a new interaction.

        Args:
            message: Raw JSON message
            interaction_type: Whether this was sent or received
            timestamp: When the interaction occurred
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Store interaction in our list
        self._all_interactions.insert(0, (message, interaction_type, timestamp))

        # Limit stored interactions to prevent memory issues
        if len(self._all_interactions) > 200:
            self._all_interactions = self._all_interactions[:150]

        # Update count
        self.interaction_count = len(self._all_interactions)

        # Refresh the displayed interactions based on current filter
        self._refresh_display()

    def _refresh_display(self) -> None:
        """Refresh the displayed interactions based on current search filter."""
        try:
            interactions_list = self.query_one("#interactions-list", VerticalScroll)

            # Get current search pattern
            search_pattern = ""
            try:
                search_input = self.query_one("#search-input", Input)
                if search_input is not None and hasattr(search_input, "value"):
                    search_pattern = search_input.value.strip()
            except Exception:
                # Search input not ready or not found, use empty pattern
                search_pattern = ""

            # Clear current display
            interactions_list.remove_children()

            # Filter interactions based on search pattern
            filtered_interactions = self._all_interactions
            if search_pattern:
                try:
                    regex = re.compile(search_pattern, re.IGNORECASE)
                    filtered_interactions = [
                        (msg, itype, ts) for msg, itype, ts in self._all_interactions if regex.search(msg)
                    ]
                except re.error:
                    # Invalid regex, show all interactions
                    filtered_interactions = self._all_interactions

            # Display filtered interactions
            if not filtered_interactions:
                if search_pattern:
                    interactions_list.mount(
                        Static("No interactions match the search pattern", id="empty-message", classes="empty-message")
                    )
                else:
                    interactions_list.mount(Static("No interactions yet", id="empty-message", classes="empty-message"))
            else:
                for message, interaction_type, timestamp in filtered_interactions:
                    # Type cast to ensure proper typing
                    from typing import cast

                    typed_interaction_type = cast(InteractionType, interaction_type)
                    interaction = InteractionItem(message, typed_interaction_type, timestamp)
                    interactions_list.mount(interaction)

                # Scroll to top to show latest
                interactions_list.scroll_home(animate=False)

        except Exception:
            # Widget may be unmounted during shutdown
            return

    def clear_interactions(self) -> None:
        """Clear all interactions."""
        # Clear stored interactions
        self._all_interactions.clear()
        self.interaction_count = 0

        # Refresh display
        self._refresh_display()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "clear-interactions":
            self.clear_interactions()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._refresh_display()

    def refresh_data(self) -> None:
        """Refresh the view data - called when switching tabs or reconnecting."""
        # For now, interactions are added in real-time, so no need to refresh
        pass

    def clear_data(self) -> None:
        """Clear all data - called when disconnecting from server."""
        self.clear_interactions()
