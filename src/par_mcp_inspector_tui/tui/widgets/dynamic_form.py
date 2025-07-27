"""Dynamic form builder widget."""

from typing import TYPE_CHECKING, Any

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ArrayField(Widget):
    """Widget for handling array/list fields with add/remove functionality."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, field_name: str, **kwargs) -> None:
        """Initialize array field."""
        super().__init__(**kwargs)
        self.field_name = field_name
        self.items: list[Input] = []
        self.item_counter = 0

    def compose(self) -> ComposeResult:
        """Create array field interface."""

        with Vertical(id=f"array-container-{self.field_name}", classes="array-container"):
            yield Button("Add Item", id=f"add-{self.field_name}", classes="add-button")
            yield Vertical(id=f"array-items-{self.field_name}", classes="array-items")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == f"add-{self.field_name}":
            self._add_item()
        elif event.button.id and event.button.id.startswith(f"remove-{self.field_name}-"):
            item_id = event.button.id.replace(f"remove-{self.field_name}-", "")
            self._remove_item(int(item_id))

    def _add_item(self) -> None:
        """Add a new item to the array."""

        items_container = self.query_one(f"#array-items-{self.field_name}")

        item_container = Horizontal(classes="array-item")
        items_container.mount(item_container)

        # Add input field
        input_widget = Input(placeholder="Enter value", id=f"array-input-{self.field_name}-{self.item_counter}")
        item_container.mount(input_widget)

        # Add remove button
        remove_button = Button("Remove", id=f"remove-{self.field_name}-{self.item_counter}", classes="remove-button")
        item_container.mount(remove_button)

        self.items.append(input_widget)
        self.item_counter += 1
        self._notify_parent_change()

    def _remove_item(self, item_id: int) -> None:
        """Remove an item from the array."""
        # Find the item container to remove
        try:
            item_input = self.query_one(f"#array-input-{self.field_name}-{item_id}")
            item_container = item_input.parent

            # Remove from tracking list
            self.items = [item for item in self.items if item.id != item_input.id]

            # Remove the container from DOM
            if item_container and isinstance(item_container, Widget):
                item_container.remove()
                self._notify_parent_change()
        except Exception:
            pass  # Item already removed or not found

    def get_values(self) -> list[str]:
        """Get all array values."""
        values = []
        for item in self.items:
            if hasattr(item, "value") and item.value.strip():
                values.append(item.value.strip())
        return values

    def clear_items(self) -> None:
        """Clear all items."""
        items_container = self.query_one(f"#array-items-{self.field_name}")
        items_container.remove_children()
        self.items.clear()

    def _notify_parent_change(self) -> None:
        """Notify parent DynamicForm of array changes."""
        parent = self.parent
        while parent and not isinstance(parent, DynamicForm):
            parent = parent.parent
        if isinstance(parent, DynamicForm):
            parent._check_validation_state()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes in array items."""
        self._notify_parent_change()


class DynamicForm(Widget):
    """Dynamic form builder for tool and prompt arguments."""

    class ValidationChanged(Message):
        """Message sent when form validation state changes."""

        def __init__(self, is_valid: bool) -> None:
            """Initialize validation changed message."""
            super().__init__()
            self.is_valid = is_valid

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, fields: list[dict[str, Any]], **kwargs) -> None:
        """Initialize dynamic form.

        Args:
            fields: List of field definitions with:
                - name: Field name
                - label: Display label
                - type: Field type (text, number, checkbox, select)
                - required: Whether field is required
                - description: Field description
                - options: List of options for select fields
                - default: Default value
        """
        super().__init__(**kwargs)
        self.fields = fields
        self.inputs: dict[str, Widget] = {}
        self.array_fields: dict[str, ArrayField] = {}
        self._last_validation_state: bool | None = None

    def compose(self) -> ComposeResult:
        """Create form fields."""
        for field in self.fields:
            with Vertical(classes="form-field"):
                # Label with red asterisk for required fields
                if field.get("required"):
                    label_text = Text()
                    label_text.append(field["label"], style="default")
                    label_text.append(" *", style="red bold")
                    yield Static(label_text, classes="form-label")
                else:
                    yield Label(field["label"], classes="form-label")

                # Description
                if field.get("description"):
                    yield Static(field["description"], classes="form-description")

                # Input field
                field_type = field.get("type", "text")
                field_name = field["name"]

                if field_type == "array":
                    # Array field with add/remove functionality
                    array_widget = ArrayField(field_name, id=f"array-{field_name}")
                    self.array_fields[field_name] = array_widget
                    yield array_widget
                elif field_type == "checkbox":
                    input_widget = Checkbox(label="", value=field.get("default", False), id=f"field-{field_name}")
                    self.inputs[field_name] = input_widget
                    yield input_widget
                elif field_type == "select" and field.get("options"):
                    options = [(str(opt), str(opt)) for opt in field["options"]]
                    input_widget = Select(options=options, value=field.get("default"), id=f"field-{field_name}")
                    self.inputs[field_name] = input_widget
                    yield input_widget
                else:
                    # Text or number input
                    input_widget = Input(
                        placeholder=field.get("placeholder", ""),
                        value=str(field.get("default", "")),
                        id=f"field-{field_name}",
                    )
                    self.inputs[field_name] = input_widget
                    yield input_widget

    def get_values(self) -> dict[str, Any]:
        """Get form values as dictionary."""
        values = {}

        for field in self.fields:
            field_name = field["name"]
            field_type = field.get("type", "text")

            # Handle array fields
            if field_type == "array":
                array_widget = self.array_fields.get(field_name)
                if array_widget:
                    array_values = array_widget.get_values()
                    if array_values:  # Only include non-empty arrays
                        values[field_name] = array_values
                continue

            # Handle regular fields
            widget = self.inputs.get(field_name)
            if not widget:
                continue

            if isinstance(widget, Checkbox):
                values[field_name] = widget.value
            elif isinstance(widget, Select):
                values[field_name] = widget.value
            elif isinstance(widget, Input):
                value = widget.value

                # Convert to appropriate type
                if field_type == "number" and value:
                    try:
                        # Try int first, then float
                        if "." not in value:
                            values[field_name] = int(value)
                        else:
                            values[field_name] = float(value)
                    except ValueError:
                        values[field_name] = value
                elif value:  # Only include non-empty values
                    values[field_name] = value

        return values

    def validate(self) -> list[str]:
        """Validate form and return list of errors."""
        errors = []

        for field in self.fields:
            if field.get("required"):
                field_name = field["name"]
                field_type = field.get("type", "text")

                # Handle array field validation
                if field_type == "array":
                    array_widget = self.array_fields.get(field_name)
                    if not array_widget or not array_widget.get_values():
                        errors.append(f"{field['label']} is required")
                    continue

                # Handle regular field validation
                widget = self.inputs.get(field_name)
                if isinstance(widget, Input) and not widget.value:
                    errors.append(f"{field['label']} is required")
                elif isinstance(widget, Select) and not widget.value:
                    errors.append(f"{field['label']} is required")

        return errors

    def is_valid(self) -> bool:
        """Check if form is valid (no validation errors)."""
        return len(self.validate()) == 0

    def _check_validation_state(self) -> None:
        """Check validation state and emit change event if state changed."""
        current_state = self.is_valid()
        if current_state != self._last_validation_state:
            self._last_validation_state = current_state
            self.post_message(self.ValidationChanged(current_state))

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input field changes."""
        self._check_validation_state()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select field changes."""
        self._check_validation_state()

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        """Handle checkbox field changes."""
        self._check_validation_state()

    def on_mount(self) -> None:
        """Called when the form is mounted and ready.

        Triggers initial validation check to ensure parent views update their
        button states correctly. This prevents race conditions where validation
        runs before form inputs are fully populated.
        """
        # Trigger initial validation check now that form is fully mounted
        self.call_later(self._check_validation_state)

    def update_fields(self, fields: list[dict[str, Any]]) -> None:
        """Update form with new fields."""
        # Clear existing form
        self.fields = fields
        self.inputs.clear()
        self.array_fields.clear()
        self.remove_children()

        # Rebuild form with new fields
        for field in self.fields:
            # Create field container and mount it first
            field_container = Vertical(classes="form-field")
            self.mount(field_container)

            # Label with red asterisk for required fields
            if field.get("required"):
                label_text = Text()
                label_text.append(field["label"], style="default")
                label_text.append(" *", style="red bold")
                field_container.mount(Static(label_text, classes="form-label"))
            else:
                field_container.mount(Label(field["label"], classes="form-label"))

            # Description
            if field.get("description"):
                field_container.mount(Static(field["description"], classes="form-description"))

            # Input field
            field_type = field.get("type", "text")
            field_name = field["name"]

            if field_type == "array":
                # Array field with add/remove functionality
                array_widget = ArrayField(field_name, id=f"array-{field_name}")
                self.array_fields[field_name] = array_widget
                field_container.mount(array_widget)
            elif field_type == "checkbox":
                input_widget = Checkbox(label="", value=field.get("default", False), id=f"field-{field_name}")
                self.inputs[field_name] = input_widget
                field_container.mount(input_widget)
            elif field_type == "select" and field.get("options"):
                options = [(str(opt), str(opt)) for opt in field["options"]]
                input_widget = Select(options=options, value=field.get("default"), id=f"field-{field_name}")
                self.inputs[field_name] = input_widget
                field_container.mount(input_widget)
            else:
                # Text or number input
                input_widget = Input(
                    placeholder=field.get("placeholder", ""),
                    value=str(field.get("default", "")),
                    id=f"field-{field_name}",
                )
                self.inputs[field_name] = input_widget
                field_container.mount(input_widget)
