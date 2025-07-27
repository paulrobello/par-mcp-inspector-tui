"""Notification panel widget for displaying server notifications and application messages."""

from datetime import datetime
from typing import Literal

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from ...models import ServerNotification

NotificationType = Literal["info", "success", "warning", "error", "server"]


class NotificationItem(Widget):
    """Individual notification item."""

    def __init__(
        self,
        message: str,
        notification_type: NotificationType,
        timestamp: datetime | None = None,
        server_name: str | None = None,
        **kwargs,
    ) -> None:
        """Initialize notification item."""
        super().__init__(**kwargs)
        self.message = message
        self.notification_type = notification_type
        self.timestamp = timestamp or datetime.now()
        self.server_name = server_name
        self.add_class("notification-item")
        self.add_class(notification_type)

    def compose(self) -> ComposeResult:
        """Create notification display."""
        icon = {
            "info": "ℹ",
            "success": "✓",
            "warning": "⚠",
            "error": "✗",
            "server": "🔔",
        }.get(self.notification_type, "•")

        # Create time label with server context if available
        time_text = f"{icon} {self.timestamp.strftime('%H:%M:%S')}"
        if self.server_name and self.notification_type == "server":
            time_text += f" [{self.server_name}]"

        yield Label(time_text, classes="notification-time")
        yield Static(self.message, classes="notification-message", markup=False)


class NotificationPanel(Widget):
    """Panel for displaying real-time server notifications and application messages.

    Features:
    - Server notifications with context (server name and icon)
    - Auto-refresh notifications for list changes
    - Message notifications with level indicators
    - Chronological ordering (newest first)
    - Memory management (limits to 100 notifications)
    """

    notification_count = reactive(0)

    def compose(self) -> ComposeResult:
        """Create notification panel UI."""
        yield Label("Notifications", classes="panel-title")
        with VerticalScroll(id="notification-list"):
            yield Static("No notifications", id="empty-message", classes="empty-message")

    def add_notification(
        self,
        message: str,
        notification_type: NotificationType = "info",
        server_name: str | None = None,
    ) -> None:
        """Add a new notification.

        Args:
            message: Notification message
            notification_type: Type of notification
            server_name: Optional server name for server notifications
        """
        # Remove empty message if present
        try:
            empty_msg = self.query_one("#empty-message")
            empty_msg.remove()
        except Exception:
            pass

        # Add new notification at the top
        try:
            notification_list = self.query_one("#notification-list", VerticalScroll)
            notification = NotificationItem(message, notification_type, server_name=server_name)
            notification_list.mount(notification, before=0)

            # Scroll to top to show latest
            notification_list.scroll_home(animate=True)
        except Exception:
            # Widget may be unmounted during shutdown
            return

        # Update count
        self.notification_count += 1

        # Limit notifications to prevent memory issues
        if self.notification_count > 100:
            # Remove oldest notifications (from the bottom since newest are at top)
            children = list(notification_list.children)
            for child in children[-20:]:
                child.remove()
            self.notification_count = 80

    def add_server_notification(self, server_notification: ServerNotification) -> None:
        """Add a server notification.

        Args:
            server_notification: Server notification to add
        """
        self.add_notification(
            message=server_notification.message,
            notification_type="server",
            server_name=server_notification.server_name,
        )

    def clear_notifications(self) -> None:
        """Clear all notifications."""
        try:
            notification_list = self.query_one("#notification-list", VerticalScroll)
            notification_list.remove_children()
            notification_list.mount(Static("No notifications", id="empty-message", classes="empty-message"))
        except Exception:
            # Widget may be unmounted during shutdown
            return
        self.notification_count = 0
