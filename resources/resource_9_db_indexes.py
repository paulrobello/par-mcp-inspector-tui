"""
Resource #9: Database Indexes Resource

Purpose:
- Provide basic database index metadata (names, columns, uniqueness)
- Lightweight resource - pure metadata extraction (PRAGMA commands only)
- No computation or analysis - just raw index information
- Completes Tier 1 database foundation for enterprise SQL generation

URI Template:
- indexes://{table_name} → Basic indexes for specified table
- indexes://all → Basic indexes across database

This is a proper lightweight resource following GET-like principles.
For optimization analysis and recommendations, use tools instead.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def register_db_indexes_resource(mcp):
    """Register the database indexes resource with the FastMCP instance."""
    
    @mcp.resource("indexes://{table_name}")
    async def get_database_indexes(table_name: str) -> dict:
        """
        Resource #9: Database Indexes Resource
        
        Returns database index information for query performance optimization.
        Lightweight resource - pure metadata extraction.
        
        Args:
            table_name: Name of the table to get indexes for, or "all"
            
        Returns:
            dict: Database indexes including names, columns, uniqueness, and optimization hints
        """
        print(f"[DEBUG] get_database_indexes() called with table_name: {table_name}")
        
        try:
            # Use the same analytics database as other DB resources
            db_path = Path("/Users/aniruddha/Work/Webonise/fileSysChatbot/textToSpeech2/data/analytics.db")
            
            if not db_path.exists():
                return {
                    "error": True,
                    "error_type": "database_not_found",
                    "message": f"Database not found at: {db_path}",
                    "table_name": table_name,
                    "resource_info": {
                        "resource_type": "database_indexes",
                        "uri_template": "indexes://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            indexes_data = {}
            
            if table_name.lower() == "all":
                # Get indexes for all tables
                available_tables = await _get_available_tables(cursor)
                for table in available_tables:
                    indexes_data[table] = await _get_table_indexes(cursor, table)
            else:
                # Check if specific table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    available_tables = await _get_available_tables(cursor)
                    conn.close()
                    return {
                        "error": True,
                        "error_type": "table_not_found",
                        "message": f"Table '{table_name}' not found in database",
                        "table_name": table_name,
                        "available_tables": available_tables,
                        "resource_info": {
                            "resource_type": "database_indexes",
                            "uri_template": "indexes://{table_name}",
                            "parameter_received": table_name
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                
                indexes_data[table_name] = await _get_table_indexes(cursor, table_name)
            
            conn.close()
            
            # Build response
            result = {
                "error": False,
                "table_name": table_name,
                "indexes": indexes_data,
                "resource_info": {
                    "resource_type": "database_indexes",
                    "uri_template": "indexes://{table_name}",
                    "parameter_received": table_name,
                    "retrieved_at": datetime.now().isoformat(),
                    "learning_phase": "Resource #9 - Database Indexes",
                    "database_file": str(db_path.absolute()),
                    "database_type": "SQLite"
                },
                "llm_context": {
                    "purpose": f"Basic database index metadata for {table_name}",
                    "usage_hint": f"Index names and columns for {table_name}. Prefer indexed columns in WHERE clauses.",
                    "data_provided": "Index names, columns, uniqueness flags, and basic counts",
                    "recommended_use": "For detailed optimization analysis, use appropriate tools rather than this lightweight resource."
                },
                "server_info": {
                    "server_name": "mcp-test-server",
                    "resource_purpose": "Performance optimization context for LLM SQL generation"
                }
            }
            
            print(f"[DEBUG] Successfully retrieved indexes for {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] Database error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "database_indexes",
                    "uri_template": "indexes://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"[DEBUG] Unexpected error: {e}")
            return {
                "error": True,
                "error_type": "unexpected_error",
                "message": f"Unexpected error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "database_indexes",
                    "uri_template": "indexes://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_database_indexes


async def _get_table_indexes(cursor, table_name: str) -> dict:
    """Get basic index information for a specific table - lightweight resource."""
    
    indexes = {
        "table_name": table_name,
        "indexes": [],
        "index_summary": {
            "total_indexes": 0,
            "unique_indexes": 0,
            "non_unique_indexes": 0
        }
    }
    
    # Get all indexes for the table - pure metadata extraction
    cursor.execute(f"PRAGMA index_list({table_name})")
    index_list = cursor.fetchall()
    
    for index_info in index_list:
        index_name = index_info[1]
        is_unique = bool(index_info[2])
        origin = index_info[3]  # 'c' for CREATE INDEX, 'u' for UNIQUE constraint, 'pk' for PRIMARY KEY
        
        # Get columns in this index
        cursor.execute(f"PRAGMA index_info({index_name})")
        index_columns_info = cursor.fetchall()
        
        column_names = [col_info[2] for col_info in index_columns_info]
        
        # Simple index details - no computation, just metadata
        index_details = {
            "index_name": index_name,
            "columns": column_names,
            "column_count": len(column_names),
            "is_unique": is_unique,
            "origin": origin
        }
        
        indexes["indexes"].append(index_details)
    
    # Simple counting - no analysis
    indexes["index_summary"]["total_indexes"] = len(indexes["indexes"])
    indexes["index_summary"]["unique_indexes"] = sum(1 for idx in indexes["indexes"] if idx["is_unique"])
    indexes["index_summary"]["non_unique_indexes"] = indexes["index_summary"]["total_indexes"] - indexes["index_summary"]["unique_indexes"]
    
    return indexes


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]