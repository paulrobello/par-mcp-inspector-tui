"""
Resource #6: Table Relationships Resource

Purpose:
- Provide foreign key and relationship information for database tables
- Essential for LLM JOIN query generation (shows how tables connect)
- Lightweight resource - just metadata queries (PRAGMA commands)
- Complements schema and sample data for complete SQL generation context

URI Template:
- relations://{table_name} → Relationships for specified table
- relations://all → All relationships in the database

This completes our SQL generation trilogy: schema + samples + relationships.
Perfect for LLM-powered text-to-SQL applications.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def register_table_relationships_resource(mcp):
    """Register the table relationships resource with the FastMCP instance."""
    
    @mcp.resource("relations://{table_name}")
    async def get_table_relationships(table_name: str) -> dict:
        """
        Resource #6: Table Relationships Resource
        
        Returns foreign key relationships for database tables.
        Lightweight resource - just metadata extraction.
        
        Args:
            table_name: Name of the table to get relationships for, or "all"
            
        Returns:
            dict: Table relationships with foreign keys and references
        """
        print(f"[DEBUG] get_table_relationships() called with table_name: {table_name}")
        
        try:
            # Use the same analytics database as Resources #4 and #5
            db_path = Path("/Users/aniruddha/Work/Webonise/fileSysChatbot/textToSpeech2/data/analytics.db")
            
            if not db_path.exists():
                return {
                    "error": True,
                    "error_type": "database_not_found",
                    "message": f"Database not found at: {db_path}",
                    "table_name": table_name,
                    "resource_info": {
                        "resource_type": "table_relationships",
                        "uri_template": "relations://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            relationships_data = {}
            
            if table_name.lower() == "all":
                # Get relationships for all tables
                available_tables = await _get_available_tables(cursor)
                for table in available_tables:
                    relationships_data[table] = await _get_table_relationship_data(cursor, table)
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
                            "resource_type": "table_relationships",
                            "uri_template": "relations://{table_name}",
                            "parameter_received": table_name
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                
                relationships_data[table_name] = await _get_table_relationship_data(cursor, table_name)
            
            conn.close()
            
            # Build response
            result = {
                "error": False,
                "table_name": table_name,
                "relationships": relationships_data,
                "resource_info": {
                    "resource_type": "table_relationships",
                    "uri_template": "relations://{table_name}",
                    "parameter_received": table_name,
                    "retrieved_at": datetime.now().isoformat(),
                    "learning_phase": "Resource #6 - Table Relationships",
                    "database_file": str(db_path.absolute()),
                    "database_type": "SQLite"
                },
                "llm_context": {
                    "purpose": f"Foreign key relationships for {table_name} - essential for JOIN queries",
                    "usage_hint": f"Use this relationship data to understand how {table_name} connects to other tables for JOIN operations.",
                    "recommended_use": "Combine with schema://{table} and samples://{table} for complete SQL generation context."
                },
                "server_info": {
                    "server_name": "mcp-test-server",
                    "resource_purpose": "JOIN context for LLM SQL generation"
                }
            }
            
            print(f"[DEBUG] Successfully retrieved relationships for {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] Database error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "table_relationships",
                    "uri_template": "relations://{table_name}",
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
                    "resource_type": "table_relationships",
                    "uri_template": "relations://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_table_relationships


async def _get_table_relationship_data(cursor, table_name: str) -> dict:
    """Get comprehensive relationship data for a specific table."""
    
    # Get outgoing foreign keys (this table references others)
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys_raw = cursor.fetchall()
    
    outgoing_relationships = []
    for fk in foreign_keys_raw:
        relationship = {
            "local_column": fk[3],  # from column
            "foreign_table": fk[2],  # to table
            "foreign_column": fk[4],  # to column
            "relationship_type": "many_to_one",  # this table -> referenced table
            "constraint_name": f"fk_{table_name}_{fk[3]}"
        }
        outgoing_relationships.append(relationship)
    
    # Get incoming foreign keys (other tables reference this table)
    incoming_relationships = await _get_incoming_relationships(cursor, table_name)
    
    return {
        "table_name": table_name,
        "outgoing_foreign_keys": outgoing_relationships,
        "incoming_foreign_keys": incoming_relationships,
        "total_relationships": len(outgoing_relationships) + len(incoming_relationships),
        "can_join_to": [rel["foreign_table"] for rel in outgoing_relationships],
        "referenced_by": [rel["local_table"] for rel in incoming_relationships]
    }


async def _get_incoming_relationships(cursor, table_name: str) -> list:
    """Find tables that have foreign keys pointing to this table."""
    
    # Get all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    all_tables = [row[0] for row in cursor.fetchall()]
    
    incoming_relationships = []
    
    for other_table in all_tables:
        if other_table == table_name:
            continue
            
        # Check if other_table has foreign keys pointing to table_name
        cursor.execute(f"PRAGMA foreign_key_list({other_table})")
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            if fk[2] == table_name:  # foreign table matches our table
                relationship = {
                    "local_table": other_table,
                    "local_column": fk[3],  # from column in other table
                    "foreign_column": fk[4],  # to column in our table
                    "relationship_type": "one_to_many",  # our table -> other table
                    "constraint_name": f"fk_{other_table}_{fk[3]}"
                }
                incoming_relationships.append(relationship)
    
    return incoming_relationships


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]