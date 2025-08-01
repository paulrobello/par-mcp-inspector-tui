"""
Resource #4: Database Schema Resource

Purpose:
- Provide database schema information for LLM-powered SQL generation
- Extract table structures, relationships, and constraints from your analytics.db
- Support both specific table queries and full schema dumps
- Optimize output format for LLM context and SQL query generation

URI Templates:
- schema://all → All table schemas
- schema://{table_name} → Specific table schema

This resource connects to your existing analytics database for real-world schema extraction.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def register_db_schema_resource(mcp):
    """Register the database schema resource with the FastMCP instance."""
    
    @mcp.resource("schema://{table_name}")
    async def get_database_schema(table_name: str) -> dict:
        """
        Resource #4: Database Schema Resource
        
        Extracts and returns database schema information from your analytics.db.
        Perfect for text-to-SQL workflows and SQL query generation.
        
        Args:
            table_name: Name of specific table, or "all" for complete schema
            
        Returns:
            dict: Comprehensive schema information including tables, columns, 
                  relationships, constraints, and indexes
        """
        print(f"[DEBUG] get_database_schema() called with table_name: {table_name}")
        
        try:
            # Use your existing analytics database
            db_path = Path("/Users/aniruddha/Work/Webonise/fileSysChatbot/textToSpeech2/data/analytics.db")
            if not db_path.exists():
                return {
                    "error": True,
                    "error_type": "database_not_found",
                    "message": f"Analytics database not found at: {db_path}",
                    "table_name": table_name,
                    "resource_info": {
                        "resource_type": "database_schema",
                        "uri_template": "schema://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # Connect to your analytics database
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            if table_name.lower() == "all":
                # Return schema for all tables
                result = await _get_all_tables_schema(cursor)
            else:
                # Return schema for specific table
                result = await _get_single_table_schema(cursor, table_name)
            
            conn.close()
            
            # Add metadata for tracking
            result["resource_info"] = {
                "resource_type": "database_schema",
                "uri_template": "schema://{table_name}",
                "parameter_received": table_name,
                "retrieved_at": datetime.now().isoformat(),
                "learning_phase": "Resource #4 - Database Schema for SQL Generation",
                "database_file": str(db_path.absolute()),
                "database_type": "SQLite"
            }
            
            result["server_info"] = {
                "server_name": "mcp-test-server",
                "resource_purpose": "LLM SQL generation context",
                "schema_extraction": True
            }
            
            print(f"[DEBUG] Successfully extracted schema for: {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] SQLite error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "database_schema",
                    "uri_template": "schema://{table_name}",
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
                    "resource_type": "database_schema",
                    "uri_template": "schema://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_database_schema


async def _get_all_tables_schema(cursor) -> dict:
    """Extract schema information for all tables in the analytics database."""
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        return {
            "error": False,
            "message": "No tables found in analytics database",
            "schema_type": "all_tables",
            "table_count": 0,
            "tables": []
        }
    
    # Extract schema for each table
    table_schemas = {}
    relationships = []
    
    for table_name in tables:
        table_info = await _extract_table_info(cursor, table_name)
        table_schemas[table_name] = table_info
        
        # Collect foreign key relationships
        if table_info.get("foreign_keys"):
            for fk in table_info["foreign_keys"]:
                relationships.append({
                    "from_table": table_name,
                    "from_column": fk["column"],
                    "to_table": fk["references_table"],
                    "to_column": fk["references_column"],
                    "relationship_type": "many_to_one"
                })
    
    return {
        "error": False,
        "schema_type": "all_tables",
        "table_count": len(tables),
        "tables": table_schemas,
        "relationships": relationships,
        "database_summary": {
            "total_tables": len(tables),
            "table_names": tables,
            "total_relationships": len(relationships),
            "schema_complexity": "high" if len(tables) > 5 else "medium" if len(tables) > 2 else "simple"
        },
        "llm_context": {
            "purpose": "This schema from analytics.db can be used to generate SQL queries. All table structures and relationships are included.",
            "usage_hint": "Reference table names, column names, and foreign key relationships when generating SQL.",
            "supported_operations": ["SELECT", "INSERT", "UPDATE", "DELETE", "JOIN operations"]
        }
    }


async def _get_single_table_schema(cursor, table_name: str) -> dict:
    """Extract schema information for a specific table."""
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        return {
            "error": True,
            "error_type": "table_not_found",
            "message": f"Table '{table_name}' not found in analytics database",
            "table_name": table_name,
            "available_tables": await _get_available_tables(cursor)
        }
    
    # Extract detailed table information
    table_info = await _extract_table_info(cursor, table_name)
    
    return {
        "error": False,
        "schema_type": "single_table",
        "table_name": table_name,
        "table_info": table_info,
        "llm_context": {
            "purpose": f"Schema for {table_name} table from analytics.db - use this structure for SQL operations",
            "usage_hint": f"When querying {table_name}, use these exact column names and respect the data types",
            "column_count": len(table_info.get("columns", [])),
            "has_foreign_keys": len(table_info.get("foreign_keys", [])) > 0,
            "has_indexes": len(table_info.get("indexes", [])) > 0
        }
    }


async def _extract_table_info(cursor, table_name: str) -> dict:
    """Extract comprehensive information about a specific table."""
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_raw = cursor.fetchall()
    
    columns = []
    primary_keys = []
    
    for col in columns_raw:
        col_info = {
            "name": col[1],
            "type": col[2],
            "not_null": bool(col[3]),
            "default_value": col[4],
            "primary_key": bool(col[5])
        }
        columns.append(col_info)
        
        if col_info["primary_key"]:
            primary_keys.append(col_info["name"])
    
    # Get foreign key information
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys_raw = cursor.fetchall()
    
    foreign_keys = []
    for fk in foreign_keys_raw:
        foreign_keys.append({
            "column": fk[3],
            "references_table": fk[2],
            "references_column": fk[4],
            "on_update": fk[5],
            "on_delete": fk[6]
        })
    
    # Get indexes
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes_raw = cursor.fetchall()
    
    indexes = []
    for idx in indexes_raw:
        # Get index details
        cursor.execute(f"PRAGMA index_info({idx[1]})")
        index_columns = [col[2] for col in cursor.fetchall()]
        
        indexes.append({
            "name": idx[1],
            "unique": bool(idx[2]),
            "columns": index_columns
        })
    
    return {
        "name": table_name,
        "columns": columns,
        "primary_keys": primary_keys,
        "foreign_keys": foreign_keys,
        "indexes": indexes,
        "column_count": len(columns),
        "has_relationships": len(foreign_keys) > 0
    }


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]