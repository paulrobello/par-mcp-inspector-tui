"""Response viewer widget with syntax highlighting."""

import json
import platform
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING

from rich.console import RenderableType
from rich.json import JSON
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Label, Static

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ResponseItem(Widget, can_focus=True):
    """Individual response item widget with border and title."""

    def __init__(self, title: str, content: str, content_type: str = "json", **kwargs) -> None:
        """Initialize response item.

        Args:
            title: Response title
            content: Response content
            content_type: Type of content (json, text, markdown, etc.)
        """
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.content_type = content_type
        self.formatted_content = self._format_content()

    def _format_content(self) -> RenderableType:
        """Format content based on type."""
        if self.content_type == "json":
            try:
                # Parse and pretty-print JSON
                parsed = json.loads(self.content)
                return JSON(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                # Fallback to plain text if not valid JSON
                return Syntax(self.content, "text", theme="monokai", line_numbers=True, word_wrap=True)

        elif self.content_type == "markdown":
            return Markdown(self.content)

        elif self.content_type in ["python", "javascript", "typescript", "html", "css", "yaml", "toml"]:
            return Syntax(self.content, self.content_type, theme="monokai", line_numbers=True, word_wrap=True)

        else:  # Plain text
            formatted_content = Text(self.content)
            formatted_content.no_wrap = False  # Enable word wrapping
            return formatted_content

    def compose(self) -> ComposeResult:
        """Create response item UI."""
        # Use Static widget to display the formatted content
        static_widget = Static(self.formatted_content, id=f"response-item-{id(self)}", classes="response-item-content")
        static_widget.border_title = self.title
        yield static_widget


class ResponseViewer(Widget, can_focus_children=True):
    """Widget for displaying formatted responses."""

    # Define key bindings for this widget
    BINDINGS = [
        Binding("ctrl+o", "open_file", "Open File", show=False),
    ]

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, **kwargs) -> None:
        """Initialize response viewer."""
        super().__init__(**kwargs)
        self.responses: list[tuple[datetime, str, str, str]] = []
        self._last_saved_file: str | None = None

    def compose(self) -> ComposeResult:
        """Create response viewer UI."""
        with Horizontal(classes="response-header"):
            yield Label("MCP Interactions", classes="view-title")
            yield Button("Clear", id="clear-responses-button", classes="clear-button")

        with VerticalScroll():
            yield Vertical(id="responses-container")

    def show_response(self, title: str, content: str, content_type: str = "json") -> None:
        """Show a response with appropriate formatting.

        Args:
            title: Response title
            content: Response content
            content_type: Type of content (json, text, markdown, etc.)
        """
        self.app.debug_log(
            f"ResponseViewer.show_response: title='{title}', content_type='{content_type}', content_len={len(content)}"
        )
        timestamp = datetime.now()
        self.responses.insert(0, (timestamp, title, content, content_type))

        try:
            container = self.query_one("#responses-container", Vertical)

            # Create header with timestamp
            header = f"[{timestamp.strftime('%H:%M:%S')}] {title}"

            # Create and mount response item widget at the top
            response_item = ResponseItem(header, content, content_type)
            container.mount(response_item, before=0)

            # Use set_timer to delay focus until after the widget is fully mounted
            self.set_timer(0.1, lambda: self._focus_new_item(response_item))

            self.app.debug_log("ResponseItem created and mounted successfully")
        except Exception as e:
            self.app.debug_log(f"Error in ResponseViewer.show_response: {e}", "error")
            import traceback

            self.app.debug_log(f"Traceback: {traceback.format_exc()}", "error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "clear-responses-button":
            self.clear()

    def clear(self) -> None:
        """Clear all responses."""
        self.responses.clear()
        container = self.query_one("#responses-container", Vertical)
        container.remove_children()

    def save_history(self, filename: str) -> None:
        """Save response history to file."""
        with open(filename, "w", encoding="utf-8") as f:
            for timestamp, title, content, content_type in self.responses:
                f.write(f"=== {timestamp.isoformat()} - {title} ===\n")
                f.write(f"Type: {content_type}\n")
                f.write(f"Content:\n{content}\n")
                f.write("\n" + "=" * 50 + "\n\n")

    def action_open_file(self) -> None:
        """Action to open the last saved file."""
        if self._last_saved_file:
            self._open_file_with_default_app(self._last_saved_file)
        else:
            self.app.notify_info("No file to open. Read a resource first.")

    def _open_file_with_default_app(self, file_path: str) -> None:
        """Open file with default system application.

        Args:
            file_path: Path to the file to open
        """
        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", file_path], check=True)
            elif system == "Windows":
                subprocess.run(["start", file_path], shell=True, check=True)
            else:  # Linux and other Unix-like systems
                subprocess.run(["xdg-open", file_path], check=True)

            self.app.notify_info(f"Opened file: {file_path}")
        except Exception as e:
            self.app.notify_error(f"Failed to open file: {e}")

    def set_last_saved_file(self, file_path: str) -> None:
        """Set the last saved file path for opening.

        Args:
            file_path: Path to the saved file
        """
        self._last_saved_file = file_path

    def _focus_new_item(self, response_item: ResponseItem) -> None:
        """Focus the newly added response item.

        Args:
            response_item: The response item to focus
        """
        try:
            if response_item.is_mounted:
                response_item.focus()
                self.app.debug_log(f"Focused new response item: {response_item.title}")
            else:
                self.app.debug_log("Response item not yet mounted, skipping focus")
        except Exception as e:
            self.app.debug_log(f"Error focusing response item: {e}", "error")
