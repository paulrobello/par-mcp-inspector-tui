"""Resources view widget."""

import base64
import mimetypes
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import filetype
from textual import work
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView

from ...models import Resource
from ...services import MCPService

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ResourceItem(ListItem):
    """Individual resource item."""

    def __init__(self, resource: Resource, mcp_service: MCPService) -> None:
        """Initialize resource item."""
        super().__init__()
        self.resource = resource
        self.mcp_service = mcp_service
        self.text_preview: str | None = None

    def compose(self) -> ComposeResult:
        """Create resource item display."""
        yield Label(self.resource.name, classes="resource-name")
        if self.resource.description:
            yield Label(self.resource.description, classes="resource-description")

        # Show text preview if available
        if self.text_preview:
            yield Label(f"Preview: {self.text_preview}", classes="resource-preview")

    async def load_text_preview(self) -> None:
        """Load text preview for text-based resources."""
        # Only try to load preview for text-based MIME types
        if not self._is_text_resource():
            return

        try:
            result = await self.mcp_service.read_resource(self.resource.uri)

            if result and isinstance(result, list) and len(result) > 0:
                item = result[0]

                # Check if it has text content (not blob/binary)
                if hasattr(item, "text") and not hasattr(item, "blob"):
                    text_content = getattr(item, "text", "")
                    if text_content:
                        # Truncate to 100 characters and clean up formatting
                        preview = text_content.strip()[:100]
                        if len(text_content) > 100:
                            preview += "..."

                        # Replace newlines and multiple spaces for cleaner display
                        preview = " ".join(preview.split())
                        self.text_preview = preview

                        # Update display
                        self.refresh()

        except Exception:
            # Silently fail for preview loading - don't disturb the UI
            pass

    def _is_text_resource(self) -> bool:
        """Check if this resource is likely to contain text content."""
        if not self.resource.mime_type:
            return False

        text_mime_types = [
            "text/plain",
            "text/markdown",
            "text/html",
            "text/css",
            "text/javascript",
            "text/csv",
            "application/json",
            "application/xml",
            "text/xml",
            "application/yaml",
            "text/yaml",
        ]

        return any(self.resource.mime_type.startswith(mime) for mime in text_mime_types)


class ResourcesView(Widget, can_focus_children=True):
    """View for displaying and interacting with resources."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize resources view."""
        super().__init__(**kwargs)
        self.mcp_service = mcp_service
        self.resources: list[Resource] = []
        self.selected_resource: Resource | None = None

        # Add CSS classes for styling
        self.add_class("resources-view")

    def compose(self) -> ComposeResult:
        """Create resources view UI."""
        # Create ListView with border title
        resources_list = ListView(id="resources-list", classes="item-list-with-title-resources")
        resources_list.border_title = "Resources"
        yield resources_list

        yield Button("Read Resource", id="read-resource-button", disabled=True)

    @work
    async def refresh(self, **kwargs) -> None:
        """Refresh resources from server."""
        if not self.mcp_service.connected:
            self.resources = []
            # Schedule UI update on main thread
            self.call_later(self._update_display)
            return

        try:
            self.resources = await self.mcp_service.list_resources()
            # Schedule UI update on main thread
            self.call_later(self._update_display)
        except Exception as e:
            self.app.notify_error(f"Failed to fetch resources: {e}")
            import traceback

            traceback.print_exc()

    def clear_data(self) -> None:
        """Clear all resources data and display."""
        self.resources = []
        self.selected_resource = None
        self._update_display()
        # Disable read button
        try:
            read_button = self.query_one("#read-resource-button", Button)
            read_button.disabled = True
        except Exception:
            pass  # Button might not exist yet

    def _update_display(self) -> None:
        """Update the resources display."""
        resources_list = self.query_one("#resources-list", ListView)
        resources_list.clear()

        if not self.resources:
            if self.mcp_service.connected:
                resources_list.append(ListItem(Label("No resources available", classes="empty-message")))
            else:
                resources_list.append(ListItem(Label("Connect to a server to view resources", classes="empty-message")))
        else:
            for resource in self.resources:
                resource_item = ResourceItem(resource, self.mcp_service)
                resources_list.append(resource_item)

                # Load text preview for text resources
                if resource_item._is_text_resource():
                    self._load_preview_async(resource_item)

    @work
    async def _load_preview_async(self, resource_item: ResourceItem) -> None:
        """Load text preview asynchronously."""
        await resource_item.load_text_preview()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle resource selection."""
        if isinstance(event.item, ResourceItem):
            self.selected_resource = event.item.resource
            self.query_one("#read-resource-button", Button).disabled = False

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "read-resource-button" and self.selected_resource:
            await self._read_resource()

    async def _read_resource(self) -> None:
        """Read selected resource."""
        if not self.selected_resource:
            return

        try:
            self.app.notify_info(f"Reading resource: {self.selected_resource.name}")
            result = await self.mcp_service.read_resource(self.selected_resource.uri)

            # Debug: Log the complete MCP response
            self.app.debug_log(f"Complete MCP response: {result}")
            self.app.debug_log(f"Response type: {type(result)}")

            # Show result in response viewer
            if result:
                # FastMCP returns a list of ResourceContents objects directly
                if isinstance(result, list) and len(result) > 0:
                    item = result[0]

                    # Handle both object and dict formats
                    if hasattr(item, "text") or hasattr(item, "blob"):
                        # It's a ResourceContents object
                        self.app.debug_log(f"Resource item (object): {item}")

                        # Check for binary content first
                        blob_data = getattr(item, "blob", None)
                        if blob_data:
                            # Debug: Log blob data info
                            self.app.debug_log(
                                f"Found blob data, type: {type(blob_data)}, length: {len(str(blob_data))}"
                            )
                            self.app.debug_log(f"Blob data preview: {str(blob_data)[:100]}...")

                            # Use name from response if available, fallback to resource name
                            resource_name = getattr(item, "name", None) or self.selected_resource.name

                            # Use mimeType from response, fallback to resource metadata
                            response_mime_type = getattr(item, "mimeType", None) or self.selected_resource.mime_type

                            # Handle binary content - decode base64 and save to temp file
                            file_path = self._save_blob_to_file(blob_data, resource_name, response_mime_type)
                            self._show_file_response(file_path, "Binary", resource_name, response_mime_type)
                        else:
                            # Handle text content - save to temp file as well
                            text = getattr(item, "text", "")
                            self.app.debug_log(f"Found text data, length: {len(text)}")

                            # Use name from response if available, fallback to resource name
                            resource_name = getattr(item, "name", None) or self.selected_resource.name

                            # Use mimeType from response, fallback to resource metadata
                            response_mime_type = getattr(item, "mimeType", None) or self.selected_resource.mime_type

                            file_path = self._save_text_to_file(text, resource_name, response_mime_type)
                            self._show_file_response(file_path, "Text", resource_name, response_mime_type)
                    else:
                        self.app.show_response(f"Resource: {self.selected_resource.name}", str(item), "json")
                else:
                    self.app.show_response(f"Resource: {self.selected_resource.name}", str(result), "json")
        except Exception as e:
            self.app.notify_error(f"Failed to read resource: {e}")

    def _save_text_to_file(self, text_data: str, resource_name: str, mime_type: str | None) -> str:
        """Save text data to a temporary file.

        Args:
            text_data: Text content to save
            resource_name: Resource label/name to use as filename
            mime_type: MIME type from response to determine file extension

        Returns:
            Path to the saved file
        """
        try:
            # For generic MIME types, try magic number detection on encoded text
            binary_data = None
            if mime_type in ["application/octet-stream", "binary/octet-stream"]:
                binary_data = text_data.encode("utf-8")

            # Determine file extension from MIME type or resource name
            extension = self._get_file_extension(resource_name, mime_type, binary_data)

            # Create safe filename
            safe_name = self._make_safe_filename(resource_name)

            # Create temp file in /tmp
            temp_file = Path(tempfile.mkdtemp(prefix="mcp_resource_", dir="/tmp")) / f"{safe_name}{extension}"

            # Write text data to file
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(text_data)

            return str(temp_file)

        except Exception as e:
            # Fallback: create a simple text file
            temp_file = (
                Path(tempfile.mkdtemp(prefix="mcp_resource_", dir="/tmp"))
                / f"{self._make_safe_filename(resource_name)}.txt"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(f"Failed to save text data: {e}\n\nContent:\n{text_data}")
            return str(temp_file)

    def _show_file_response(self, file_path: str, content_type: str, resource_name: str, mime_type: str | None) -> None:
        """Show file response with integrated open functionality.

        Args:
            file_path: Path to the saved file
            content_type: Type of content (Binary/Text)
            resource_name: Name of the resource
            mime_type: MIME type of the resource
        """
        # Store the file path in the response viewer for potential opening
        from .response_viewer import ResponseViewer

        response_viewer = self.app.query_one("#response-viewer", ResponseViewer)
        response_viewer.set_last_saved_file(file_path)

        # Create detailed response text with resource info and open instructions
        response_text = f"""Resource Details:
• Name: {resource_name}
• MIME Type: {mime_type or "Unknown"}
• Content Type: {content_type}
• File Location: {file_path}

To open this file with your default application:
🚀 Press Ctrl+O for quick open

The file has been saved and is ready to view."""

        self.app.show_response(
            f"Resource: {resource_name}",
            response_text,
            "text",
        )

        # Show notification with file info
        self.app.notify_info(f"{content_type} resource '{resource_name}' saved to {Path(file_path).name}")

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

            self.app.notify_info(f"Opened file: {Path(file_path).name}")

        except subprocess.CalledProcessError as e:
            self.app.notify_error(f"Failed to open file: {e}")
        except Exception as e:
            self.app.notify_error(f"Error opening file: {e}")

    def _save_blob_to_file(self, blob_data: str, resource_name: str, mime_type: str | None) -> str:
        """Save base64 blob data to a temporary file.

        Args:
            blob_data: Base64 encoded binary data
            resource_name: Resource label/name to use as filename
            mime_type: MIME type from response to determine file extension

        Returns:
            Path to the saved file
        """
        try:
            # Debug: Log what we're trying to decode
            self.app.debug_log(f"Attempting to decode blob_data: type={type(blob_data)}")
            self.app.debug_log(f"Raw blob_data: {repr(blob_data)[:200]}...")

            # Decode base64 data
            binary_data = base64.b64decode(blob_data)
            self.app.debug_log(f"Successfully decoded {len(binary_data)} bytes from base64")

            # Determine file extension from MIME type or resource name
            extension = self._get_file_extension(resource_name, mime_type, binary_data)

            # If extension is .bin, check if content is actually text
            if extension == ".bin":
                extension = self._check_if_text_content(binary_data)

            # Create safe filename
            safe_name = self._make_safe_filename(resource_name)

            # Create temp file in /tmp
            temp_file = Path(tempfile.mkdtemp(prefix="mcp_resource_", dir="/tmp")) / f"{safe_name}{extension}"

            self.app.debug_log(f"Saving to file: {temp_file}")

            # Write binary data to file
            with open(temp_file, "wb") as f:
                f.write(binary_data)

            return str(temp_file)

        except Exception as e:
            # Fallback: create a text file with the blob content
            self.app.debug_log(f"Error in _save_blob_to_file: {e}")
            temp_file = (
                Path(tempfile.mkdtemp(prefix="mcp_resource_", dir="/tmp"))
                / f"{self._make_safe_filename(resource_name)}.txt"
            )
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(f"Failed to decode binary data: {e}\n\nOriginal blob_data:\n{blob_data}")
            return str(temp_file)

    def _check_if_text_content(self, binary_data: bytes) -> str:
        """Check if binary data is actually text and return appropriate extension.

        Args:
            binary_data: The decoded binary data to check

        Returns:
            File extension: .txt if content is text, .bin if binary
        """
        try:
            # Try to decode as UTF-8 text
            text_content = binary_data.decode("utf-8")

            # Check if it contains mostly printable characters
            printable_chars = sum(1 for c in text_content if c.isprintable() or c.isspace())
            total_chars = len(text_content)

            # If more than 95% of characters are printable, consider it text
            if total_chars > 0 and (printable_chars / total_chars) > 0.95:
                self.app.debug_log("Content appears to be text, using .txt extension")
                return ".txt"
            else:
                self.app.debug_log("Content contains too many non-printable characters, keeping .bin")
                return ".bin"

        except UnicodeDecodeError:
            # If it can't be decoded as UTF-8, it's likely binary
            self.app.debug_log("Content cannot be decoded as UTF-8, keeping .bin extension")
            return ".bin"

    def _get_file_extension(self, resource_name: str, mime_type: str | None, binary_data: bytes | None = None) -> str:
        """Determine file extension from MIME type, falling back to magic number detection, resource name, then .bin.

        Args:
            resource_name: Name of the resource
            mime_type: MIME type
            binary_data: Optional binary data for magic number detection

        Returns:
            File extension including the dot
        """
        # First, try to get extension from MIME type using Python's standard library
        if mime_type:
            extension = mimetypes.guess_extension(mime_type)
            if extension:
                return extension

        # For generic binary MIME types, try magic number detection
        if binary_data and mime_type in ["application/octet-stream", "binary/octet-stream"]:
            detected_type = filetype.guess(binary_data)
            if detected_type:
                self.app.debug_log(f"Magic number detection found: {detected_type.extension} ({detected_type.mime})")
                return f".{detected_type.extension}"

        # Fallback: try to get extension from resource name
        if "." in resource_name:
            return Path(resource_name).suffix

        # Default to .bin for unknown binary files
        return ".bin"

    def _make_safe_filename(self, name: str) -> str:
        """Create a safe filename from resource name.

        Args:
            name: Original resource name

        Returns:
            Safe filename
        """
        # Remove unsafe characters and limit length
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        safe_name = "".join(c if c in safe_chars else "_" for c in name)

        # Remove extension if present (we'll add our own)
        if "." in safe_name:
            safe_name = Path(safe_name).stem

        # Limit length and ensure it's not empty
        safe_name = safe_name[:50] or "resource"

        return safe_name
