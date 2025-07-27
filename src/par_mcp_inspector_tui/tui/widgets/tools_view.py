"""Tools view widget."""

from typing import TYPE_CHECKING

from rich.text import Text
from textual import work
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Label, ListItem, ListView, Static

from ...models import Tool
from ...services import MCPService
from .dynamic_form import DynamicForm

if TYPE_CHECKING:
    from ..app import MCPInspectorApp


class ToolItem(ListItem):
    """Individual tool item."""

    def __init__(self, tool: Tool) -> None:
        """Initialize tool item."""
        super().__init__()
        self.tool = tool

    def compose(self) -> ComposeResult:
        """Create tool item display."""
        # Build tool content as Rich Text with formatted parameters
        content = Text()

        if self.tool.description:
            content.append(self.tool.description)
            content.append("\n\n")

        # Show parameter info with red asterisks for required params
        params = self.tool.get_all_params()
        required = self.tool.get_required_params()
        if params:
            content.append("Params: ", style="dim")

            for i, param in enumerate(params):
                if i > 0:
                    content.append(", ", style="dim")

                content.append(param, style="dim")
                if param in required:
                    content.append("*", style="red bold")

        if not content.plain:
            content.append("No description available", style="dim")

        # Create Static widget with border and tool name as title
        static_widget = Static(content, classes="tool-item-content")
        static_widget.border_title = self.tool.name
        yield static_widget


class ToolsView(Widget):
    """View for displaying and interacting with tools."""

    @property
    def app(self) -> "MCPInspectorApp":  # type: ignore[override]
        """Get typed app instance."""
        return super().app  # type: ignore[return-value]

    def __init__(self, mcp_service: MCPService, **kwargs) -> None:
        """Initialize tools view."""
        super().__init__(**kwargs)
        self.mcp_service = mcp_service
        self.tools: list[Tool] = []
        self.selected_tool: Tool | None = None
        self.dynamic_form: DynamicForm | None = None
        self._form_counter = 0

    def compose(self) -> ComposeResult:
        """Create tools view UI."""
        # Create ListView with border title
        tools_list = ListView(id="tools-list", classes="item-list-with-title")
        tools_list.border_title = "Tools"
        yield tools_list
        tool_form_container = VerticalScroll(id="tool-form-container")
        tool_form_container.border_title = "Tool Parameters"
        yield tool_form_container
        yield Button("Execute Tool", id="execute-tool-button", disabled=True, classes="execute-button")

    @work
    async def refresh(self, **kwargs) -> None:
        """Refresh tools from server."""
        if not self.mcp_service.connected:
            self.tools = []
            # Schedule UI update on main thread
            self.call_later(self._update_display)
            return

        try:
            self.tools = await self.mcp_service.list_tools()
            # Schedule UI update on main thread
            self.call_later(self._update_display)
        except Exception as e:
            self.app.notify_error(f"Failed to fetch tools: {e}")

    def _update_display(self) -> None:
        """Update the tools display."""
        tools_list = self.query_one("#tools-list", ListView)
        tools_list.clear()

        if not self.tools:
            if self.mcp_service.connected:
                tools_list.append(ListItem(Label("No tools available", classes="empty-message")))
            else:
                tools_list.append(ListItem(Label("Connect to a server to view tools", classes="empty-message")))
        else:
            for tool in self.tools:
                tools_list.append(ToolItem(tool))

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle tool selection."""
        if isinstance(event.item, ToolItem):
            self.selected_tool = event.item.tool
            await self._show_tool_form()

    async def _show_tool_form(self) -> None:
        """Show form for selected tool."""
        if not self.selected_tool:
            return

        form_container = self.query_one("#tool-form-container", VerticalScroll)

        # Create dynamic form for tool parameters
        fields = []
        for param_name, param_props in self.selected_tool.input_schema.properties.items():
            field_type = self._get_field_type(param_props.type)
            self.app.debug_log(f"Parameter {param_name}: raw_type={param_props.type}, mapped_type={field_type}")

            field = {
                "name": param_name,
                "label": param_name,
                "type": field_type,
                "required": param_name in (self.selected_tool.input_schema.required or []),
                "description": param_props.description,
            }

            # Add enum options if available
            if param_props.enum:
                field["options"] = param_props.enum

            # Add default value if available
            if param_props.default is not None:
                field["default"] = param_props.default

            fields.append(field)

        # Reuse existing form if it exists, otherwise create new one
        if hasattr(self, "dynamic_form") and self.dynamic_form:
            # No fields, remove the form
            await self.dynamic_form.remove()
            self.dynamic_form = None
        # Create new form if needed
        await form_container.remove_children()  # Clear container first
        if fields:
            # Use a unique ID for each form instance
            self._form_counter += 1
            form_id = f"tool-args-form-{self._form_counter}"
            self.dynamic_form = DynamicForm(fields, id=form_id)
            await form_container.mount(self.dynamic_form)
        else:
            self.dynamic_form = None

        # Enable/disable execute button based on form validity
        self._update_execute_button_state()

    def _get_field_type(self, param_type: str) -> str:
        """Convert parameter type to form field type."""
        type_mapping = {
            "string": "text",
            "number": "number",
            "integer": "number",
            "boolean": "checkbox",
            "array": "array",  # Now properly handled with ArrayField
            "object": "text",  # Will need special handling
        }
        return type_mapping.get(param_type, "text")

    def _update_execute_button_state(self) -> None:
        """Update execute button state based on form validity."""
        execute_button = self.query_one("#execute-tool-button", Button)
        if not self.selected_tool:
            execute_button.disabled = True
            return

        if self.dynamic_form:
            # Disable if form is invalid
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
        if event.button.id == "execute-tool-button" and self.selected_tool:
            await self._execute_tool()

    async def _execute_tool(self) -> None:
        """Execute selected tool."""
        if not self.selected_tool:
            self.app.debug_log("_execute_tool called but no tool selected")
            return

        try:
            # Get arguments from form
            arguments = {}
            if self.dynamic_form:
                arguments = self.dynamic_form.get_values()

            self.app.debug_log(f"Executing tool: {self.selected_tool.name} with arguments: {arguments}")
            self.app.notify_info(f"Executing tool: {self.selected_tool.name}")
            result = await self.mcp_service.call_tool(self.selected_tool.name, arguments)

            self.app.debug_log(f"Tool execution result: {result}")

            # Show result in response viewer
            if result:
                content = result.get("content", [])
                self.app.debug_log(f"Result content: {content}, type: {type(content)}")

                if content and isinstance(content, list) and len(content) > 0:
                    # Format content items
                    formatted_content = []
                    for i, item in enumerate(content):
                        self.app.debug_log(f"Processing content item {i}: {item}, type: {type(item)}")
                        if isinstance(item, dict):
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                formatted_content.append(text)
                                self.app.debug_log(f"Extracted text: {text[:100]}...")
                            else:
                                formatted_content.append(str(item))
                        else:
                            formatted_content.append(str(item))

                    final_content = "\n\n".join(formatted_content)
                    self.app.debug_log(f"Final formatted content length: {len(final_content)}")
                    self.app.debug_log(
                        f"Calling show_response with title='Tool: {self.selected_tool.name}', content_type='text'"
                    )
                    self.app.show_response(f"Tool: {self.selected_tool.name}", final_content, "text")
                else:
                    self.app.debug_log("Using fallback - showing result as JSON")
                    self.app.show_response(f"Tool: {self.selected_tool.name}", str(result), "json")
            else:
                self.app.debug_log("No result returned from tool execution")
        except Exception as e:
            self.app.debug_log(f"Tool execution failed: {e}", "error")
            import traceback

            self.app.debug_log(f"Traceback: {traceback.format_exc()}", "error")
            self.app.notify_error(f"Failed to execute tool: {e}")
