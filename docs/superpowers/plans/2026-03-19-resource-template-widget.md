# Resource Template Widget Architecture Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fragile fake-Resource display hack for resource templates with a proper `ResourceTemplateItem` widget that holds a `ResourceTemplate` directly.

**Architecture:** Add `ResourceTemplateItem(ListItem)` alongside `ResourceItem`. The `_update_display()` method renders templates as `ResourceTemplateItem`s. The `on_list_view_selected()` handler uses `isinstance` dispatch to get either `resource` or `template` directly — eliminating all URI-prefix string surgery. Dead code (`_is_resource_template`, `_get_template_by_uri`) and the backup file are removed.

**Tech Stack:** Python 3.13, Textual, Pydantic models (`Resource`, `ResourceTemplate`)

---

### Task 1: Add `ResourceTemplateItem` widget

**Files:**
- Modify: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py:27-98`

- [ ] **Step 1: Add `ResourceTemplateItem` class after `ResourceItem`**

Insert immediately after the `ResourceItem` class (before `class ResourcesView`):

```python
class ResourceTemplateItem(ListItem):
    """Individual resource template item."""

    def __init__(self, template: ResourceTemplate) -> None:
        """Initialize resource template item."""
        super().__init__()
        self.template = template

    def compose(self) -> ComposeResult:
        """Create resource template item display."""
        display_name = self.template.name or self.template.uri_template
        yield Label(display_name, classes="resource-name")
        yield Label(self.template.uri_template, classes="resource-description")
        if self.template.description:
            yield Label(self.template.description, classes="resource-description")
```

- [ ] **Step 2: Verify `ResourceTemplate` is already imported**

Check line 19 of `resources_view.py` — `from ...models import Resource, ResourceTemplate` should already be present (it was added in PR #1 integration). If not, add it.

- [ ] **Step 3: Run lint/typecheck to confirm no issues**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui && uv run ruff check src/par_mcp_inspector_tui/tui/widgets/resources_view.py && uv run pyright src/par_mcp_inspector_tui/tui/widgets/resources_view.py
```

Expected: no errors.

---

### Task 2: Fix `_update_display()` to use `ResourceTemplateItem`

**Files:**
- Modify: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py:254-267`

- [ ] **Step 1: Replace fake-Resource template rendering block**

Replace the entire "Show resource templates with a visual distinction" block (lines 254–267):

```python
# OLD — remove this:
for template in self.resource_templates:
    template_as_resource = Resource(
        uri=f"🔧 {template.uri_template}",
        name=f"[Template] {template.name}" if template.name else f"[Template] {template.uri_template}",
        description=f"Resource Template: {template.description}"
        if template.description
        else "Resource Template",
        mimeType=template.mime_type,
    )
    template_item = ResourceItem(template_as_resource, self.mcp_service)
    resources_list.append(template_item)
```

```python
# NEW — replace with:
for template in self.resource_templates:
    resources_list.append(ResourceTemplateItem(template))
```

- [ ] **Step 2: Run lint/typecheck**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui && uv run ruff check src/par_mcp_inspector_tui/tui/widgets/resources_view.py && uv run pyright src/par_mcp_inspector_tui/tui/widgets/resources_view.py
```

Expected: no errors.

---

### Task 3: Fix `on_list_view_selected()` to use `isinstance` dispatch

**Files:**
- Modify: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py:274-290`

- [ ] **Step 1: Replace the event handler body**

Replace the current `on_list_view_selected` method:

```python
# OLD — remove:
@work
async def on_list_view_selected(self, event: ListView.Selected) -> None:
    """Handle resource selection."""
    if isinstance(event.item, ResourceItem):
        self.selected_resource = event.item.resource

        # Check if this is a template
        if self._is_resource_template(self.selected_resource):
            # This is a template - find the corresponding ResourceTemplate
            self.selected_template = self._get_template_by_uri(self.selected_resource.uri)
            await self._show_resource_form()
        else:
            # Static resource - no form needed
            self.selected_template = None
            await self._clear_resource_form()

        self._update_read_button_state()
```

```python
# NEW — replace with:
@work
async def on_list_view_selected(self, event: ListView.Selected) -> None:
    """Handle resource selection."""
    if isinstance(event.item, ResourceTemplateItem):
        self.selected_resource = None
        self.selected_template = event.item.template
        await self._show_resource_form()
        self._update_read_button_state()
    elif isinstance(event.item, ResourceItem):
        self.selected_resource = event.item.resource
        self.selected_template = None
        await self._clear_resource_form()
        self._update_read_button_state()
```

- [ ] **Step 2: Run lint/typecheck**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui && uv run ruff check src/par_mcp_inspector_tui/tui/widgets/resources_view.py && uv run pyright src/par_mcp_inspector_tui/tui/widgets/resources_view.py
```

Expected: no errors.

---

### Task 4: Fix `_construct_resource_uri()` and `_read_resource()` for template-only selection

**Files:**
- Modify: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py:193-229,363-425`

- [ ] **Step 1: Fix `_construct_resource_uri()`**

The current method guards on `self.selected_resource` being set, but when a template is selected `selected_resource` is `None`. Replace:

```python
# OLD:
def _construct_resource_uri(self) -> str:
    """Construct the actual URI for reading a resource."""
    if not self.selected_resource:
        return ""

    # For static resources, use the URI as-is
    if not self._is_resource_template(self.selected_resource):
        return self.selected_resource.uri

    # For templates, we need to replace parameters with values from the form
    if not self.selected_template or not self.dynamic_form:
        # Fallback to original URI if no form data
        return self.selected_resource.uri

    # Get parameter values from the form
    parameter_values = self.dynamic_form.get_values()

    # Start with the template URI (clean version without display prefixes)
    actual_uri = self.selected_template.uri_template

    # We need to map clean field names back to original parameter names
    # Extract original parameters from the template
    original_parameters = self._extract_template_parameters(self.selected_template.uri_template)

    # Create mapping from clean names to original names
    param_mapping = {}
    for original_param in original_parameters:
        clean_param = original_param.rstrip("*")
        param_mapping[clean_param] = original_param

    # Replace each {parameter} with the actual value using original parameter names
    for clean_name, param_value in parameter_values.items():
        original_param = param_mapping.get(clean_name, clean_name)
        placeholder = f"{{{original_param}}}"
        actual_uri = actual_uri.replace(placeholder, str(param_value))

    return actual_uri
```

```python
# NEW:
def _construct_resource_uri(self) -> str:
    """Construct the actual URI for reading a resource.

    For static resources returns the URI directly.
    For templates, substitutes form values into the URI template.
    """
    if self.selected_resource:
        return self.selected_resource.uri

    if not self.selected_template:
        return ""

    if not self.dynamic_form:
        return self.selected_template.uri_template

    parameter_values = self.dynamic_form.get_values()
    actual_uri = self.selected_template.uri_template
    original_parameters = self._extract_template_parameters(actual_uri)

    param_mapping = {p.rstrip("*"): p for p in original_parameters}
    for clean_name, param_value in parameter_values.items():
        original_param = param_mapping.get(clean_name, clean_name)
        actual_uri = actual_uri.replace(f"{{{original_param}}}", str(param_value))

    return actual_uri
```

- [ ] **Step 2: Fix `_update_read_button_state()` to handle template-only selection**

The current method has an early-return when `selected_resource` is `None`, which permanently disables the button for template selections. Replace:

```python
# OLD:
def _update_read_button_state(self) -> None:
    """Update read button state based on selection and form validity."""
    read_button = self.query_one("#read-resource-button", Button)

    if not self.selected_resource:
        read_button.disabled = True
        return

    if self.selected_template and self.dynamic_form:
        # Template resource - check if form is valid
        read_button.disabled = not self.dynamic_form.is_valid()
    else:
        # Static resource or no form needed
        read_button.disabled = False
```

```python
# NEW:
def _update_read_button_state(self) -> None:
    """Update read button state based on selection and form validity."""
    read_button = self.query_one("#read-resource-button", Button)

    if not self.selected_resource and not self.selected_template:
        read_button.disabled = True
        return

    if self.selected_template and self.dynamic_form:
        # Template resource - check if form is valid
        read_button.disabled = not self.dynamic_form.is_valid()
    else:
        # Static resource or no form needed
        read_button.disabled = False
```

- [ ] **Step 3: Fix `on_button_pressed()` call-site guard**

The call site gates on `self.selected_resource`, so the button press is silently dropped when a template is selected. Replace:

```python
# OLD:
if event.button.id == "read-resource-button" and self.selected_resource:
    await self._read_resource()
```

```python
# NEW:
if event.button.id == "read-resource-button" and (self.selected_resource or self.selected_template):
    await self._read_resource()
```

- [ ] **Step 4: Fix display name in `_read_resource()`**

The method uses `self.selected_resource.name` in several places. When a template is selected, `self.selected_resource` is `None`. Add a helper property and update all uses:

After the `_construct_resource_uri` method, add:

```python
@property
def _selected_display_name(self) -> str:
    """Return the display name for the currently selected resource or template."""
    if self.selected_resource:
        return self.selected_resource.name
    if self.selected_template:
        return self.selected_template.name or self.selected_template.uri_template
    return "Unknown"
```

Fix the guard at the top of `_read_resource()`:

```python
# OLD:
async def _read_resource(self) -> None:
    """Read selected resource."""
    if not self.selected_resource:
        return
```

```python
# NEW:
async def _read_resource(self) -> None:
    """Read selected resource."""
    if not self.selected_resource and not self.selected_template:
        return
```

Then replace all occurrences of `self.selected_resource.name` with `self._selected_display_name` inside `_read_resource()`. These appear at the following lines (in the original file):
- `self.app.notify_info(f"Reading resource: {self.selected_resource.name}")` (line ~371)
- `resource_name = getattr(item, "name", None) or self.selected_resource.name` (lines ~399 and ~413)
- `self.app.show_response(f"Resource: {self.selected_resource.name}", ...)` (lines ~421 and ~423)

Also replace `f"Resource: {self.selected_resource.name}"` in the fallback `show_response` calls.

- [ ] **Step 3: Run lint/typecheck**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui && uv run ruff check src/par_mcp_inspector_tui/tui/widgets/resources_view.py && uv run pyright src/par_mcp_inspector_tui/tui/widgets/resources_view.py
```

Expected: no errors.

---

### Task 5: Remove dead code and backup file

**Files:**
- Modify: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py`
- Delete: `src/par_mcp_inspector_tui/tui/widgets/resources_view.py.backup`

- [ ] **Step 1: Remove `_is_resource_template()` method** (no longer called anywhere)

Delete the entire method:
```python
def _is_resource_template(self, resource: Resource) -> bool:
    """Check if a resource is actually a template (has parameters in URI)."""
    return bool(re.search(r"\{[^}]+\}", resource.uri))
```

- [ ] **Step 2: Remove `_get_template_by_uri()` method** (no longer called anywhere)

Delete the entire method:
```python
def _get_template_by_uri(self, uri: str) -> ResourceTemplate | None:
    """Find the ResourceTemplate that matches this URI pattern."""
    # Remove the 🔧 prefix and [Template] prefix we added for display
    clean_uri = uri.replace("🔧 ", "").replace("[Template] ", "")

    for template in self.resource_templates:
        if template.uri_template == clean_uri:
            return template
    return None
```

- [ ] **Step 3: Check if `re` import is still needed**

`_extract_template_parameters()` still uses `re.findall`, so the `import re` at the top stays.

- [ ] **Step 4: Delete the backup file**

```bash
rm /Users/probello/Repos/par-mcp-inspector-tui/src/par_mcp_inspector_tui/tui/widgets/resources_view.py.backup
```

- [ ] **Step 5: Run full checkall**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui && make checkall
```

Expected: all checks pass.

- [ ] **Step 6: Commit**

```bash
cd /Users/probello/Repos/par-mcp-inspector-tui
git add src/par_mcp_inspector_tui/tui/widgets/resources_view.py
git rm src/par_mcp_inspector_tui/tui/widgets/resources_view.py.backup
git commit -m "refactor: replace fake-Resource template display with ResourceTemplateItem widget"
```
