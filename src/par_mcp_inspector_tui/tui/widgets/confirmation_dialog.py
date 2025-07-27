"""Confirmation dialog widget."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ConfirmationDialog(ModalScreen[bool]):
    """Modal confirmation dialog."""

    DEFAULT_BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, title: str, message: str, **kwargs) -> None:
        """Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Confirmation message
        """
        super().__init__(**kwargs)
        self.dialog_title = title
        self.message = message

    def compose(self) -> ComposeResult:
        """Create dialog UI."""
        with Container(id="confirmation-container"):
            yield Static(self.dialog_title, id="confirmation-title")
            yield Static(self.message, id="confirmation-message")

            with Horizontal(id="confirmation-buttons"):
                yield Button("Cancel", id="cancel-button", variant="default")
                yield Button("Confirm", id="confirm-button", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "confirm-button":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        """Cancel dialog."""
        self.dismiss(False)
