"""Content type detection utilities for appropriate viewer selection."""

import json
import re
from pathlib import Path
from typing import Any

try:
    import filetype
except ImportError:
    filetype = None


def detect_content_type(
    content: str,
    file_path: str | None = None,
    mime_type: str | None = None,
    tool_arguments: dict[str, Any] | None = None,
) -> str:
    """Detect the appropriate content type for the response viewer.

    Uses multiple detection strategies in order of preference:
    1. File extension from tool arguments (e.g., path parameter)
    2. File extension from explicit file_path
    3. MIME type mapping
    4. Content pattern analysis
    5. Fallback to text

    Args:
        content: The content to analyze
        file_path: Optional file path for extension detection
        mime_type: Optional MIME type hint
        tool_arguments: Optional tool arguments that might contain file paths

    Returns:
        Content type string suitable for ResponseViewer (e.g., 'markdown', 'python', 'json', 'text')
    """
    # Strategy 1: Extract file path from tool arguments
    detected_path = _extract_file_path_from_arguments(tool_arguments)
    if detected_path:
        content_type = _detect_from_file_extension(detected_path)
        if content_type != "text":
            return content_type

    # Strategy 2: Use explicit file_path
    if file_path:
        content_type = _detect_from_file_extension(file_path)
        if content_type != "text":
            return content_type

    # Strategy 3: MIME type mapping
    if mime_type:
        content_type = _detect_from_mime_type(mime_type)
        if content_type != "text":
            return content_type

    # Strategy 4: Content pattern analysis
    content_type = _detect_from_content_patterns(content)
    if content_type != "text":
        return content_type

    # Strategy 5: Fallback
    return "text"


def _extract_file_path_from_arguments(tool_arguments: dict[str, Any] | None) -> str | None:
    """Extract file path from tool arguments.

    Common parameter names that might contain file paths:
    - path, file_path, filepath, filename
    - uri (for file:// URIs)

    Args:
        tool_arguments: Dictionary of tool arguments

    Returns:
        Extracted file path or None
    """
    if not tool_arguments:
        return None

    # Common parameter names for file paths
    path_params = ["path", "file_path", "filepath", "filename", "file", "uri"]

    for param in path_params:
        if param in tool_arguments:
            value = tool_arguments[param]
            if isinstance(value, str) and value:
                # Handle file:// URIs
                if value.startswith("file://"):
                    return value[7:]  # Remove file:// prefix
                return value

    return None


def _detect_from_file_extension(file_path: str) -> str:
    """Detect content type from file extension.

    Args:
        file_path: Path to analyze for extension

    Returns:
        Content type or 'text' if not recognized
    """
    try:
        path = Path(file_path.lower())
        extension = path.suffix

        # Mapping of file extensions to content types
        extension_map = {
            ".md": "markdown",
            ".markdown": "markdown",
            ".py": "python",
            ".pyi": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".mjs": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".html": "html",
            ".htm": "html",
            ".css": "css",
            ".scss": "css",
            ".sass": "css",
            ".less": "css",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".toml": "toml",
            ".xml": "html",  # Use html syntax highlighting for XML
            ".sh": "bash",
            ".bash": "bash",
            ".zsh": "bash",
            ".fish": "bash",
            ".sql": "sql",
            ".dockerfile": "dockerfile",
            ".rs": "rust",
            ".go": "go",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".h": "c",
            ".hpp": "cpp",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".scala": "scala",
            ".clj": "clojure",
            ".r": "r",
            ".m": "matlab",
            ".lua": "lua",
            ".pl": "perl",
            ".ps1": "powershell",
            ".vim": "vim",
        }

        return extension_map.get(extension, "text")

    except Exception:
        return "text"


def _detect_from_mime_type(mime_type: str) -> str:
    """Detect content type from MIME type.

    Args:
        mime_type: MIME type string

    Returns:
        Content type or 'text' if not recognized
    """
    mime_type = mime_type.lower().strip()

    # MIME type to content type mapping
    mime_map = {
        "text/markdown": "markdown",
        "application/json": "json",
        "text/x-python": "python",
        "application/x-python": "python",
        "text/javascript": "javascript",
        "application/javascript": "javascript",
        "text/typescript": "typescript",
        "application/typescript": "typescript",
        "text/html": "html",
        "application/xhtml+xml": "html",
        "text/css": "css",
        "application/x-yaml": "yaml",
        "text/yaml": "yaml",
        "text/x-yaml": "yaml",
        "application/toml": "toml",
        "text/xml": "html",  # Use html highlighting for XML
        "application/xml": "html",
        "application/x-sh": "bash",
        "text/x-shellscript": "bash",
    }

    # Check exact matches first
    if mime_type in mime_map:
        return mime_map[mime_type]

    # Check prefixes for broader categories
    if mime_type.startswith("application/json"):
        return "json"
    elif mime_type.startswith("text/x-python") or "python" in mime_type:
        return "python"
    elif mime_type.startswith("text/javascript") or mime_type.startswith("application/javascript"):
        return "javascript"
    elif mime_type.startswith("text/html") or mime_type.startswith("application/xhtml"):
        return "html"
    elif mime_type.startswith("text/css"):
        return "css"
    elif "yaml" in mime_type:
        return "yaml"
    elif "xml" in mime_type:
        return "html"

    return "text"


def _detect_from_content_patterns(content: str) -> str:
    """Detect content type from content patterns.

    Analyzes the actual content to determine the most likely format.

    Args:
        content: Content to analyze

    Returns:
        Content type or 'text' if not recognized
    """
    if not content or not content.strip():
        return "text"

    content_strip = content.strip()

    # JSON detection - must be valid JSON
    if _is_json_content(content_strip):
        return "json"

    # Markdown detection - look for markdown patterns
    if _is_markdown_content(content):
        return "markdown"

    # YAML detection - look for YAML patterns
    if _is_yaml_content(content):
        return "yaml"

    # HTML detection - look for HTML tags
    if _is_html_content(content):
        return "html"

    # Python detection - look for Python syntax patterns
    if _is_python_content(content):
        return "python"

    # JavaScript detection - look for JS patterns
    if _is_javascript_content(content):
        return "javascript"

    return "text"


def _is_json_content(content: str) -> bool:
    """Check if content is valid JSON."""
    try:
        json.loads(content)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def _is_markdown_content(content: str) -> bool:
    """Check if content appears to be Markdown."""
    # Look for common Markdown patterns
    markdown_patterns = [
        r"^#{1,6}\s+.+$",  # Headers
        r"^\*\s+.+$",  # Unordered lists
        r"^\d+\.\s+.+$",  # Ordered lists
        r"\*\*.+\*\*",  # Bold text
        r"\*.+\*",  # Italic text
        r"`[^`]+`",  # Inline code
        r"```",  # Code blocks
        r"^\|.+\|$",  # Tables
        r"^\[.+\]\(.+\)$",  # Links
        r"^>\s+.+$",  # Blockquotes
    ]

    for pattern in markdown_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True

    return False


def _is_yaml_content(content: str) -> bool:
    """Check if content appears to be YAML."""
    # Look for YAML patterns
    yaml_patterns = [
        r"^[a-zA-Z_][a-zA-Z0-9_]*:\s*",  # Key-value pairs
        r"^-\s+[a-zA-Z_]",  # List items
        r"---\s*$",  # Document separator
        r"^\s*[a-zA-Z_][a-zA-Z0-9_]*:\s*\|",  # Multi-line strings
    ]

    for pattern in yaml_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True

    return False


def _is_html_content(content: str) -> bool:
    """Check if content appears to be HTML."""
    # Look for HTML tags
    html_pattern = r"<[a-zA-Z][^<>]*>"
    return bool(re.search(html_pattern, content))


def _is_python_content(content: str) -> bool:
    """Check if content appears to be Python code."""
    # Look for Python syntax patterns
    python_patterns = [
        r"^\s*def\s+\w+\s*\(",  # Function definitions
        r"^\s*class\s+\w+",  # Class definitions
        r"^\s*import\s+\w+",  # Import statements
        r"^\s*from\s+\w+\s+import",  # From imports
        r"if\s+__name__\s*==\s*[\"']__main__[\"']:",  # Main block
        r"^\s*#.*$",  # Comments (but this is weak)
    ]

    for pattern in python_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True

    return False


def _is_javascript_content(content: str) -> bool:
    """Check if content appears to be JavaScript code."""
    # Look for JavaScript patterns
    js_patterns = [
        r"^\s*function\s+\w+\s*\(",  # Function declarations
        r"^\s*const\s+\w+\s*=",  # Const declarations
        r"^\s*let\s+\w+\s*=",  # Let declarations
        r"^\s*var\s+\w+\s*=",  # Var declarations
        r"=>\s*{",  # Arrow functions
        r"console\.log\s*\(",  # Console.log
        r"document\.\w+",  # DOM access
        r"window\.\w+",  # Window object
    ]

    for pattern in js_patterns:
        if re.search(pattern, content, re.MULTILINE):
            return True

    return False


def extract_file_path_from_content(content: str) -> str | None:
    """Extract file path from content if present.

    Looks for common file path patterns in the content.

    Args:
        content: Content to search for file paths

    Returns:
        Extracted file path or None
    """
    # Look for file path patterns
    patterns = [
        r"File Location:\s*(.+)",  # "File Location: /path/to/file"
        r"•\s*File Location:\s*(.+)",  # "• File Location: /path/to/file"
        r"Path:\s*([^\s]+)",  # "Path: /path/to/file"
        r"File:\s*([^\s]+)",  # "File: /path/to/file"
        r"Reading file:\s*([^\s]+)",  # "Reading file: /path/to/file"
        r"Loaded from:\s*([^\s]+)",  # "Loaded from: /path/to/file"
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            file_path = match.group(1).strip()
            # Remove quotes if present
            file_path = file_path.strip("\"'")
            return file_path

    return None
