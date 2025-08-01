"""
Resource #2: Dynamic User Information Resource

Our second MCP resource! This demonstrates parameterized resources.

Purpose:
- Learn URI templates and parameter extraction
- Test dynamic content generation based on parameters
- Explore error handling for invalid parameters
- Understand resource templates vs static resources

URI Template: user://{user_id}
Type: Dynamic (takes user_id parameter)
Returns: JSON object with user details or error
"""

from datetime import datetime
from .mock_data import MOCK_USERS


def register_dynamic_user_resource(mcp):
    """Register the dynamic user info resource with the FastMCP instance."""
    
    @mcp.resource("user://{user_id}")
    def get_user_info(user_id: str) -> dict:
        """
        Resource #2: Dynamic User Information Resource
        
        Returns user details based on the provided user_id parameter.
        Demonstrates URI templates, parameter extraction, and error handling.
        """
        print(f"[DEBUG] get_user_info() called with user_id: {user_id}")
        
        # Check if user exists in our mock database
        if user_id not in MOCK_USERS:
            print(f"[DEBUG] User {user_id} not found in database")
            # Return error information instead of raising exception
            # This way we can see how MCP handles error responses
            error_result = {
                "error": True,
                "error_type": "user_not_found",
                "message": f"User with ID '{user_id}' not found",
                "user_id": user_id,
                "available_users": list(MOCK_USERS.keys()),
                "timestamp": datetime.now().isoformat(),
                "resource_info": {
                    "resource_type": "user_info",
                    "uri_template": "user://{user_id}",
                    "parameter_received": user_id
                }
            }
            print(f"[DEBUG] Returning error result: {error_result}")
            return error_result
        
        # User found - return user data with additional metadata
        user_data = MOCK_USERS[user_id].copy()  # Copy to avoid modifying original
        
        # Add some dynamic metadata
        result = {
            "error": False,
            "user_data": user_data,
            "resource_info": {
                "resource_type": "user_info", 
                "uri_template": "user://{user_id}",
                "parameter_received": user_id,
                "retrieved_at": datetime.now().isoformat(),
                "learning_phase": "Resource #2 - Dynamic Resources with Parameters"
            },
            "server_info": {
                "server_name": "mcp-test-server",
                "total_users": len(MOCK_USERS),
                "user_exists": True
            }
        }
        
        print(f"[DEBUG] Returning user data for {user_id}: {user_data['name']}")
        return result
    
    return get_user_info  # Return function for reference