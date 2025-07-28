"""Response viewer widget with syntax highlighting."""

import json
import platform
import re
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING

import pyperclip
from rich.console import RenderableType
from rich.json import JSON
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ResponseItem(Widget, can_focus=True):
    """Individual response item widget with border and title."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

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
        self._visible = True

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

    def _format_remaining_content(self, remaining_content: str) -> RenderableType:
        """Format the remaining content (after file location is removed) based on content type."""
        if self.content_type == "json":
            try:
                # Parse and pretty-print JSON
                parsed = json.loads(remaining_content)
                return JSON(json.dumps(parsed, indent=2))
            except json.JSONDecodeError:
                # Fallback to plain text if not valid JSON
                return Syntax(remaining_content, "text", theme="monokai", line_numbers=True, word_wrap=True)

        elif self.content_type == "markdown":
            return Markdown(remaining_content)

        elif self.content_type in ["python", "javascript", "typescript", "html", "css", "yaml", "toml"]:
            return Syntax(remaining_content, self.content_type, theme="monokai", line_numbers=True, word_wrap=True)

        else:  # Plain text
            formatted_content = Text(remaining_content)
            formatted_content.no_wrap = False  # Enable word wrapping
            return formatted_content

    def compose(self) -> ComposeResult:
        """Create response item UI."""
        # Extract file path if present in content
        file_path = self._extract_file_path()

        if file_path:
            # Create content with inline copy button after file location
            with Vertical(classes="response-item-container") as v:
                v.border_title = self.title

                # File location line with inline copy button
                with Horizontal(classes="file-location-line"):
                    yield Button(
                        "📋", id=f"copy-path-{id(self)}", classes="icon-button-inline", tooltip="Copy to clipboard"
                    )
                    yield Label(" File Location ", classes="file-location-label")
                    yield Label(f": {file_path}", classes="file-location-path")

                # Instruction text for opening the file
                yield Label(
                    "To open this file with your default application: 🚀 Press Ctrl+O for quick open",
                    classes="file-open-instruction",
                )

                # Rest of the content (excluding the file location line) with appropriate formatting
                remaining_content = self._get_content_without_file_location()
                if remaining_content:
                    # Create a temporary ResponseItem with the remaining content to get proper formatting
                    formatted_remaining_content = self._format_remaining_content(remaining_content)
                    content_widget = Static(formatted_remaining_content, classes="response-content-text")
                    yield content_widget
        else:
            # Use Static widget to display the formatted content with title
            static_widget = Static(
                self.formatted_content, id=f"response-item-{id(self)}", classes="response-item-content"
            )
            static_widget.border_title = self.title
            yield static_widget

    def set_visible(self, visible: bool) -> None:
        """Set the visibility of this response item.

        Args:
            visible: Whether the item should be visible
        """
        self._visible = visible
        self.display = visible

    def matches_search(self, pattern: str) -> bool:
        """Check if this response item matches the search pattern.

        Args:
            pattern: Regex pattern to search for

        Returns:
            bool: True if the item matches the pattern
        """
        if not pattern:
            return True

        try:
            regex = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
            # Search in both title and content
            return bool(regex.search(self.title) or regex.search(self.content))
        except re.error:
            # If regex is invalid, fall back to simple string search
            pattern_lower = pattern.lower()
            return pattern_lower in self.title.lower() or pattern_lower in self.content.lower()

    def _extract_file_path(self) -> str | None:
        """Extract file path from content if present.

        Returns:
            str | None: File path if found, None otherwise
        """
        # Look for file path pattern in content
        file_path_pattern = r"• File Location: (.+)"
        match = re.search(file_path_pattern, self.content)
        if match:
            return match.group(1).strip()
        return None

    def _get_content_without_file_location(self) -> str:
        """Get content with the file location line removed.

        Returns:
            str: Content without the file location line
        """
        lines = self.content.split("\n")
        # Filter out the file location line and any empty lines after it
        filtered_lines = []
        skip_empty_after_file_location = False

        for line in lines:
            if line.strip().startswith("• File Location:"):
                skip_empty_after_file_location = True
                continue
            elif skip_empty_after_file_location and not line.strip():
                # Skip the first empty lines after file location
                skip_empty_after_file_location = False
                continue
            else:
                skip_empty_after_file_location = False
                filtered_lines.append(line)

        return "\n".join(filtered_lines).strip()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id and event.button.id.startswith(f"copy-path-{id(self)}"):
            self._copy_file_path_to_clipboard()

    def _copy_file_path_to_clipboard(self) -> None:
        """Copy the file path to clipboard."""
        file_path = self._extract_file_path()
        if file_path:
            try:
                pyperclip.copy(file_path)
                # Get the app instance to show notification
                app = self.app
                if hasattr(app, "notify_success"):
                    app.notify_success("File path copied to clipboard!")
                else:
                    app.notify("File path copied to clipboard!", severity="information")
            except Exception as e:
                app = self.app
                if hasattr(app, "notify_error"):
                    app.notify_error(f"Failed to copy to clipboard: {e}")
                else:
                    app.notify(f"Failed to copy to clipboard: {e}", severity="error")


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
        self._search_pattern = ""

    def compose(self) -> ComposeResult:
        """Create response viewer UI."""
        with Horizontal(classes="response-header"):
            yield Label("MCP Interactions", classes="view-title")
            yield Button("Clear", id="clear-responses-button", classes="clear-button")

        with Horizontal(classes="search-container"):
            yield Input(
                placeholder="Enter regex pattern to filter responses...", id="search-input", classes="search-input"
            )

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

            # Set last saved file if content contains a file path (for Ctrl+O functionality)
            file_path = response_item._extract_file_path()
            if file_path:
                self.set_last_saved_file(file_path)

            # Apply current search filter to the new item
            if self._search_pattern:
                matches = response_item.matches_search(self._search_pattern)
                response_item.set_visible(matches)

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

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._search_pattern = event.value
            self._filter_responses()

    def clear(self) -> None:
        """Clear all responses."""
        self.responses.clear()
        container = self.query_one("#responses-container", Vertical)
        container.remove_children()
        # Clear search input as well
        try:
            search_input = self.query_one("#search-input", Input)
            search_input.value = ""
            self._search_pattern = ""
        except Exception:
            pass

    def _filter_responses(self) -> None:
        """Filter responses based on current search pattern."""
        try:
            container = self.query_one("#responses-container", Vertical)

            # Get all response items
            response_items = container.query(ResponseItem)

            for response_item in response_items:
                # Check if this response item matches the search pattern
                matches = response_item.matches_search(self._search_pattern)
                response_item.set_visible(matches)

        except Exception as e:
            self.app.debug_log(f"Error filtering responses: {e}", "error")

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
