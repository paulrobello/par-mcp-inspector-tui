"""
Resource #3: File System Resource with Wildcard Parameters

This demonstrates:
- Wildcard parameters ({filepath*}) that capture multiple path segments
- Async file I/O operations  
- Text vs binary file detection
- Comprehensive error handling
- Security considerations (safe path validation)

Examples:
- files://README.md
- files://src/main.py  
- files://docs/api/resources.md
- files://config/settings.json

The wildcard parameter allows capturing full file paths including
subdirectories, unlike regular parameters that only match single segments.
"""

import aiofiles
from datetime import datetime
from pathlib import Path


def register_file_system_resource(mcp):
    """Register the file system resource with wildcard parameters."""
    
    @mcp.resource("files://{filepath*}")
    async def read_file_content(filepath: str) -> dict:
        """
        Resource #3: File System Resource with Wildcard Parameters
        
        Reads file content with comprehensive error handling and security checks.
        Supports both text and binary file detection.
        """
        print(f"[DEBUG] read_file_content() called with filepath: {filepath}")
        
        try:
            # Convert to Path object for better handling
            file_path = Path(filepath)
            
            # Security check: Prevent path traversal attacks
            if '..' in str(file_path) or str(file_path).startswith('/'):
                print(f"[DEBUG] Security violation: unsafe path {filepath}")
                return {
                    "error": True,
                    "error_type": "security_violation", 
                    "message": f"Unsafe file path: {filepath}",
                    "filepath": filepath,
                    "security_note": "Path traversal (.. or absolute paths) not allowed",
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath,
                        "safety_check": "failed"
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if file exists
            if not file_path.exists():
                print(f"[DEBUG] File not found: {filepath}")
                return {
                    "error": True,
                    "error_type": "file_not_found",
                    "message": f"File not found: {filepath}",
                    "filepath": filepath,
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath,
                        "file_exists": False
                    },
                    "suggestions": [
                        "Check if the file path is correct",
                        "Ensure the file exists in the current directory",
                        "Try a relative path from the project root"
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            
            # Check if it's a file (not a directory)
            if not file_path.is_file():
                print(f"[DEBUG] Not a file: {filepath}")
                return {
                    "error": True,
                    "error_type": "not_a_file",
                    "message": f"Path is not a file: {filepath}",
                    "filepath": filepath,
                    "path_type": "directory" if file_path.is_dir() else "unknown",
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath,
                        "is_file": False
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Check for reasonable file size (prevent reading huge files)
            max_size = 10 * 1024 * 1024  # 10MB limit
            if file_size > max_size:
                print(f"[DEBUG] File too large: {file_size} bytes")
                return {
                    "error": True,
                    "error_type": "file_too_large",
                    "message": f"File too large: {file_size} bytes (max: {max_size})",
                    "filepath": filepath,
                    "file_size": file_size,
                    "max_size": max_size,
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Try to read as text first
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    content = await f.read()
                
                print(f"[DEBUG] Successfully read text file: {filepath} ({len(content)} chars)")
                return {
                    "error": False,
                    "file_content": content,
                    "file_info": {
                        "filepath": filepath,
                        "file_size": file_size,
                        "content_type": "text",
                        "encoding": "utf-8",
                        "lines": content.count('\n') + 1 if content else 0,
                        "characters": len(content)
                    },
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath,
                        "read_at": datetime.now().isoformat(),
                        "learning_phase": "Resource #3 - File System with Wildcard Parameters"
                    },
                    "server_info": {
                        "server_name": "mcp-test-server",
                        "read_mode": "text",
                        "async_io": True
                    }
                }
                
            except UnicodeDecodeError:
                # File is binary, read as bytes and provide info
                print(f"[DEBUG] Binary file detected: {filepath}")
                async with aiofiles.open(file_path, 'rb') as f:
                    binary_content = await f.read()
                
                # Get first few bytes for file type detection
                first_bytes = binary_content[:16]
                hex_preview = first_bytes.hex()
                
                return {
                    "error": False,
                    "message": "Binary file detected - content not displayed but file info provided",
                    "file_info": {
                        "filepath": filepath,
                        "file_size": file_size,
                        "content_type": "binary",
                        "first_bytes_hex": hex_preview,
                        "file_extension": file_path.suffix,
                        "binary_size": len(binary_content)
                    },
                    "resource_info": {
                        "resource_type": "file_content",
                        "uri_template": "files://{filepath*}",
                        "parameter_received": filepath,
                        "read_at": datetime.now().isoformat(),
                        "learning_phase": "Resource #3 - File System with Wildcard Parameters"
                    },
                    "server_info": {
                        "server_name": "mcp-test-server",
                        "read_mode": "binary",
                        "async_io": True
                    },
                    "note": "Binary files are detected but content not returned for safety"
                }
                
        except PermissionError:
            print(f"[DEBUG] Permission denied: {filepath}")
            return {
                "error": True,
                "error_type": "permission_denied",
                "message": f"Permission denied accessing file: {filepath}",
                "filepath": filepath,
                "resource_info": {
                    "resource_type": "file_content",
                    "uri_template": "files://{filepath*}",
                    "parameter_received": filepath
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[DEBUG] Unexpected error reading {filepath}: {e}")
            return {
                "error": True,
                "error_type": "unexpected_error",
                "message": f"Unexpected error reading file: {str(e)}",
                "filepath": filepath,
                "exception_type": type(e).__name__,
                "resource_info": {
                    "resource_type": "file_content",
                    "uri_template": "files://{filepath*}",
                    "parameter_received": filepath
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return read_file_content  # Return function for reference