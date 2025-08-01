"""
Resource #5: Simple Sample Data Resource

Purpose:
- Provide basic sample rows from database tables (LIMIT 5)
- Complement schema information with actual data examples
- Lightweight resource for LLM context (proper GET-like behavior)
- No complex computation - just simple data retrieval

URI Template:
- samples://{table_name} → 5 sample rows from specified table

This is a proper lightweight resource that pairs with Resource #4 (schema).
For advanced sampling strategies, use appropriate tools instead.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def register_sample_data_resource(mcp):
    """Register the sample data resource with the FastMCP instance."""
    
    @mcp.resource("samples://{table_name}")
    async def get_sample_data(table_name: str) -> dict:
        """
        Resource #5: Simple Sample Data Resource
        
        Returns 5 basic sample rows from database tables for LLM context.
        Lightweight resource with no complex computation.
        
        Args:
            table_name: Name of the table to sample from
            
        Returns:
            dict: Simple sample data (5 rows) with basic metadata
        """
        print(f"[DEBUG] get_sample_data() called with table_name: {table_name}")
        
        try:
            # Use the same analytics database as Resource #4
            db_path = Path("/Users/aniruddha/Work/Webonise/fileSysChatbot/textToSpeech2/data/analytics.db")
            if not db_path.exists():
                return {
                    "error": True,
                    "error_type": "database_not_found",
                    "message": f"Analytics database not found at: {db_path}",
                    "table_name": table_name,
                    "resource_info": {
                        "resource_type": "sample_data",
                        "uri_template": "samples://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Connect to analytics database
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                available_tables = await _get_available_tables(cursor)
                conn.close()
                return {
                    "error": True,
                    "error_type": "table_not_found", 
                    "message": f"Table '{table_name}' not found in analytics database",
                    "table_name": table_name,
                    "available_tables": available_tables,
                    "resource_info": {
                        "resource_type": "sample_data",
                        "uri_template": "samples://{table_name}",
                        "parameter_received": table_name
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Simple sample data retrieval - just get 5 rows
            sample_data = await _get_simple_sample_data(cursor, table_name)
            
            conn.close()
            
            # Build simple response - proper lightweight resource
            result = {
                "error": False,
                "table_name": table_name,
                "sample_rows": sample_data["rows"],
                "column_names": sample_data["columns"],
                "sample_size": len(sample_data["rows"]),
                "resource_info": {
                    "resource_type": "sample_data",
                    "uri_template": "samples://{table_name}",
                    "parameter_received": table_name,
                    "retrieved_at": datetime.now().isoformat(),
                    "learning_phase": "Resource #5 - Simple Sample Data",
                    "database_file": str(db_path.absolute()),
                    "database_type": "SQLite"
                },
                "llm_context": {
                    "purpose": f"Simple sample data from {table_name} table",
                    "usage_hint": f"5 sample rows from {table_name}. Use with schema://{table_name} for complete context.",
                    "note": "For advanced sampling strategies, use appropriate tools"
                },
                "server_info": {
                    "server_name": "mcp-test-server",
                    "resource_purpose": "Basic sample data for LLM context"
                }
            }
            
            print(f"[DEBUG] Successfully sampled {len(sample_data['rows'])} rows from {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] SQLite error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "sample_data",
                    "uri_template": "samples://{table_name}",
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
                "exception_type": type(e).__name__,
                "resource_info": {
                    "resource_type": "sample_data",
                    "uri_template": "samples://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_sample_data


async def _get_simple_sample_data(cursor, table_name: str) -> dict:
    """Get simple sample data - just 5 rows for LLM context."""
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_raw = cursor.fetchall()
    column_names = [col[1] for col in columns_raw]
    
    # Get 5 simple sample rows
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = [dict(row) for row in cursor.fetchall()]
    
    return {
        "columns": column_names,
        "rows": rows
    }


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]