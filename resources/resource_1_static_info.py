"""
Resource #1: Static Server Information

Our first MCP resource! This provides basic server metadata.

Purpose:
- Learn basic resource registration and URI patterns
- Understand JSON return types 
- Test resource discovery by MCP clients
- Establish baseline for resource mechanics

URI: server://info
Type: Static (no parameters)
Returns: JSON object with server details
"""

from datetime import datetime


def register_static_info_resource(mcp):
    """Register the static server info resource with the FastMCP instance."""
    
    @mcp.resource("server://info")
    def get_server_info() -> dict:
        """
        Resource #1: Static Server Information
        
        Returns basic server metadata including capabilities and current status.
        This is our foundational resource for learning MCP mechanics.
        """
        print("[DEBUG] get_server_info() called!")  # Debug logging
        
        result = {
            "server_name": "mcp-test-server",
            "version": "1.0.0",
            "description": "Test server for learning MCP resources",
            "startup_time": datetime.now().isoformat(),
            "capabilities": {
                "tools": ["fibonacci", "add_numbers"],
                            "resources": ["server://info", "user://{user_id}", "files://{filepath*}", "schema://{table_name}", "samples://{table_name}", "relations://{table_name}", "stats://{table_name}", "constraints://{table_name}", "indexes://{table_name}"],
            "resource_count": 9
            },
            "learning_phase": "Resource #9 - Database Indexes COMPLETE - Tier 1 Foundation Achieved!",
            "status": "learning",
            "debug_timestamp": datetime.now().isoformat()
        }
        
        print(f"[DEBUG] Returning: {result}")  # Debug logging
        return result
    
    return get_server_info  # Return function for reference