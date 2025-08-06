"""
MCP Resources Module

This module provides a clean, modular way to organize and register MCP resources.
Each resource is defined in its own file for better maintainability and separation of concerns.

Usage:
    from resources import register_all_resources
    register_all_resources(mcp)

Resources:
- Resource #1: Static server info (server://info)
- Resource #2: Dynamic user info (user://{user_id})  
- Resource #3: File system with wildcards (files://{filepath*})
- Resource #4: Database schema info (schema://{table_name})
- Resource #5: Sample data extraction (samples://{table_name})
- Resource #6: Table relationships (relations://{table_name})
- Resource #7: Table statistics (stats://{table_name})
- Resource #8: Database constraints (constraints://{table_name})
- Resource #9: Database indexes (indexes://{table_name})
"""

from .resource_1_static_info import register_static_info_resource
from .resource_2_dynamic_user import register_dynamic_user_resource
from .resource_3_file_system import register_file_system_resource
from .resource_4_db_schema import register_db_schema_resource
from .resource_5_sample_data import register_sample_data_resource
from .resource_6_table_relationships import register_table_relationships_resource
from .resource_7_table_stats import register_table_stats_resource
from .resource_8_db_constraints import register_db_constraints_resource
from .resource_9_db_indexes import register_db_indexes_resource


def register_all_resources(mcp):
    """
    Register all MCP resources with the FastMCP instance.
    
    This function provides a single entry point to register all available resources.
    Each resource is defined in its own module for better organization.
    
    Args:
        mcp: FastMCP instance to register resources with
        
    Returns:
        dict: Mapping of resource names to their registration functions
    """
    print("[DEBUG] Registering all MCP resources...")
    
    # Register each resource and collect references
    registered_resources = {
        "static_info": register_static_info_resource(mcp),
        "dynamic_user": register_dynamic_user_resource(mcp), 
        "file_system": register_file_system_resource(mcp),
        "db_schema": register_db_schema_resource(mcp),
        "sample_data": register_sample_data_resource(mcp),
        "table_relationships": register_table_relationships_resource(mcp),
        "table_stats": register_table_stats_resource(mcp),
        "db_constraints": register_db_constraints_resource(mcp),
        "db_indexes": register_db_indexes_resource(mcp)
    }
    
    print(f"[DEBUG] Successfully registered {len(registered_resources)} resources:")
    for name in registered_resources.keys():
        print(f"[DEBUG]   - {name}")
    
    return registered_resources


# Resource metadata for introspection
RESOURCE_METADATA = {
    "resource_1_static_info": {
        "name": "Static Server Information",
        "uri": "server://info",
        "type": "static",
        "parameters": [],
        "description": "Basic server metadata and capabilities"
    },
    "resource_2_dynamic_user": {
        "name": "Dynamic User Information", 
        "uri": "user://{user_id}",
        "type": "dynamic",
        "parameters": ["user_id"],
        "description": "User data based on user ID parameter"
    },
    "resource_3_file_system": {
        "name": "File System with Wildcards",
        "uri": "files://{filepath*}", 
        "type": "dynamic_wildcard",
        "parameters": ["filepath*"],
        "description": "File content reading with path wildcards"
    },
    "resource_4_db_schema": {
        "name": "Database Schema Information",
        "uri": "schema://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Database schema extraction for LLM SQL generation"
    },
    "resource_5_sample_data": {
        "name": "Sample Data Extraction",
        "uri": "samples://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Representative sample rows for LLM SQL context"
    },
    "resource_6_table_relationships": {
        "name": "Table Relationships",
        "uri": "relations://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Foreign key relationships and JOIN context for SQL generation"
    },
    "resource_7_table_stats": {
        "name": "Table Statistics",
        "uri": "stats://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Essential table statistics for SQL query optimization"
    },
    "resource_8_db_constraints": {
        "name": "Database Constraints",
        "uri": "constraints://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Data validation rules and constraints for accurate SQL generation"
    },
    "resource_9_db_indexes": {
        "name": "Database Indexes",
        "uri": "indexes://{table_name}",
        "type": "dynamic_database",
        "parameters": ["table_name"],
        "description": "Index information for query performance optimization"
    }
}


def get_resource_info():
    """Return metadata about all available resources."""
    return RESOURCE_METADATA


def get_resource_count():
    """Return the total number of available resources."""
    return len(RESOURCE_METADATA)


# Export key functions and data
__all__ = [
    "register_all_resources",
    "get_resource_info", 
    "get_resource_count",
    "RESOURCE_METADATA"
]