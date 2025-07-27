"""Prompts view widget."""

from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView

from ...models import Prompt
from ...services import MCPService
from .dynamic_form import DynamicForm

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class PromptItem(ListItem):
    """Individual prompt item."""

    def __init__(self, prompt: Prompt) -> None:
        """Initialize prompt item."""
        super().__init__()
        self.prompt = prompt
        self.border_title = self.prompt.name

    def compose(self) -> ComposeResult:
        """Create prompt item display."""
        if self.prompt.description:
            yield Label(self.prompt.description, classes="prompt-description")
        if self.prompt.arguments:
            args_text = f"Args: {', '.join(arg.name for arg in self.prompt.arguments)}"
            yield Label(args_text, classes="prompt-params")


class PromptsView(Widget):
    """View for displaying and interacting with prompts."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize prompts view."""
        super().__init__(**kwargs)
        self.mcp_service = mcp_service
        self.prompts: list[Prompt] = []
        self.selected_prompt: Prompt | None = None
        self.dynamic_form: DynamicForm | None = None
        self._form_counter = 0

    def compose(self) -> ComposeResult:
        """Create prompts view UI."""
        # Create ListView with border title
        prompts_list = ListView(id="prompts-list", classes="item-list-with-title-prompts")
        prompts_list.border_title = "Prompts"
        yield prompts_list

        yield Vertical(id="prompt-form-container")
        yield Button("Execute Prompt", id="execute-prompt-button", disabled=True)

    @work
    async def refresh(self, **kwargs) -> None:
        """Refresh prompts from server."""
        if not self.mcp_service.connected:
            self.prompts = []
            # Schedule UI update on main thread
            self.call_later(self._update_display)
            return

        try:
            self.prompts = await self.mcp_service.list_prompts()
            # Schedule UI update on main thread
            self.call_later(self._update_display)
        except Exception as e:
            self.app.notify_error(f"Failed to fetch prompts: {e}")

    def clear_data(self) -> None:
        """Clear all prompts data and display."""
        self.prompts = []
        self.selected_prompt = None
        self._update_display()
        # Clear form and disable execute button
        try:
            form_container = self.query_one("#form-container")
            form_container.remove_children()
        except Exception:
            pass  # Container might not exist yet

    def _update_display(self) -> None:
        """Update the prompts display."""
        prompts_list = self.query_one("#prompts-list", ListView)
        prompts_list.clear()

        if not self.prompts:
            if self.mcp_service.connected:
                prompts_list.append(ListItem(Label("No prompts available", classes="empty-message")))
            else:
                prompts_list.append(ListItem(Label("Connect to a server to view prompts", classes="empty-message")))
        else:
            for prompt in self.prompts:
                prompts_list.append(PromptItem(prompt))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle prompt selection.

        Immediately disables execute button to prevent race conditions during form creation.
        Button is re-enabled only after validation confirms all required fields are filled.
        """
        if isinstance(event.item, PromptItem):
            self.selected_prompt = event.item.prompt
            # Immediately disable execute button when switching prompts to prevent race conditions
            execute_button = self.query_one("#execute-prompt-button", Button)
            execute_button.disabled = True
            self._show_prompt_form()

    def _show_prompt_form(self) -> None:
        """Show form for selected prompt."""
        if not self.selected_prompt:
            return

        form_container = self.query_one("#prompt-form-container", Vertical)
        execute_button = self.query_one("#execute-prompt-button", Button)

        # Ensure button starts disabled while form is being built
        execute_button.disabled = True

        # Clear the old form reference
        self.dynamic_form = None

        # Remove ALL children from the container to ensure clean slate
        form_container.remove_children()

        if self.selected_prompt.arguments:
            # Create dynamic form for arguments
            fields = []
            for arg in self.selected_prompt.arguments:
                fields.append(
                    {
                        "name": arg.name,
                        "label": arg.name,
                        "type": "text",
                        "required": arg.required,
                        "description": arg.description,
                    }
                )

            # Use a unique ID for each form instance
            self._form_counter += 1
            form_id = f"prompt-args-form-{self._form_counter}"
            self.dynamic_form = DynamicForm(fields, id=form_id)
            form_container.mount(self.dynamic_form)

            # Use call_later to ensure form is fully initialized before validation check
            self.call_later(self._update_execute_button_state)
        else:
            # No arguments needed
            self.dynamic_form = None
            # Use call_later for consistency to ensure button state is updated after form clearing
            self.call_later(self._update_execute_button_state)

    def _update_execute_button_state(self) -> None:
        """Update execute button state based on form validity.

        Implements race condition protection by checking if form inputs are ready
        before validating. This prevents premature button enabling during form mounting.
        """
        execute_button = self.query_one("#execute-prompt-button", Button)
        if not self.selected_prompt:
            execute_button.disabled = True
            return

        if self.dynamic_form:
            # Check if form has required fields but inputs aren't populated yet (race condition protection)
            has_required_fields = any(field.get("required", False) for field in self.dynamic_form.fields)
            form_inputs_ready = bool(self.dynamic_form.inputs)

            if has_required_fields and not form_inputs_ready:
                # Form has required fields but inputs aren't ready yet - disable button
                execute_button.disabled = True
            else:
                # Form is ready - check validity normally
                execute_button.disabled = not self.dynamic_form.is_valid()
        else:
            # No form needed, enable button
            execute_button.disabled = False

    def on_dynamic_form_validation_changed(self, event: DynamicForm.ValidationChanged) -> None:
        """Handle form validation changes."""
        self._update_execute_button_state()

    @work
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "execute-prompt-button" and self.selected_prompt:
            await self._execute_prompt()

    async def _execute_prompt(self) -> None:
        """Execute selected prompt."""
        if not self.selected_prompt:
            return

        try:
            # Get arguments from form
            arguments = {}
            if self.dynamic_form:
                arguments = self.dynamic_form.get_values()

            self.app.notify_info(f"Executing prompt: {self.selected_prompt.name}")
            result = await self.mcp_service.get_prompt(self.selected_prompt.name, arguments)

            # Show result in response viewer
            if result:
                # FastMCP returns GetPromptResult objects with attributes, not dict
                messages = getattr(result, "messages", [])
                if messages:
                    # Format messages nicely - messages may be objects or dicts
                    formatted_messages = []
                    for msg in messages:
                        if hasattr(msg, "role") and hasattr(msg, "content"):
                            # It's a message object
                            role = getattr(msg, "role", "unknown")
                            content = getattr(msg, "content", "")
                        else:
                            # It's a dictionary
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")
                        formatted_messages.append(f"**{role}**:\n{content}")

                    content = "\n\n".join(formatted_messages)
                    self.app.show_response(f"Prompt: {self.selected_prompt.name}", content, "markdown")
                else:
                    self.app.show_response(f"Prompt: {self.selected_prompt.name}", str(result), "json")
        except Exception as e:
            self.app.notify_error(f"Failed to execute prompt: {e}")
