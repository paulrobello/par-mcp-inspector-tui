"""
Resource #8: Database Constraints Resource

Purpose:
- Provide database constraint information for data validation understanding
- Essential for LLM to understand business rules and data integrity requirements
- Lightweight resource - pure metadata extraction (PRAGMA commands)
- Critical for accurate SQL generation that respects data validation rules

URI Template:
- constraints://{table_name} → Constraints for specified table
- constraints://all → All constraints across database

This completes Tier 1 essential database resources for enterprise SQL generation.
Focuses on data integrity rules that LLMs must understand for valid SQL.
"""

import sqlite3
import re
from datetime import datetime
from pathlib import Path


def register_db_constraints_resource(mcp):
    """Register the database constraints resource with the FastMCP instance."""
    
    @mcp.resource("constraints://{table_name}")
    async def get_database_constraints(table_name: str) -> dict:
        """
        Resource #8: Database Constraints Resource
        
        Returns database constraint information for data validation understanding.
        Lightweight resource - pure metadata extraction.
        
        Args:
            table_name: Name of the table to get constraints for, or "all"
            
        Returns:
            dict: Database constraints including NOT NULL, UNIQUE, CHECK, DEFAULT, etc.
        """
        print(f"[DEBUG] get_database_constraints() called with table_name: {table_name}")
        
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
                        "resource_type": "database_constraints",
                        "uri_template": "constraints://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            constraints_data = {}
            
            if table_name.lower() == "all":
                # Get constraints for all tables
                available_tables = await _get_available_tables(cursor)
                for table in available_tables:
                    constraints_data[table] = await _get_table_constraints(cursor, table)
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
                            "resource_type": "database_constraints",
                            "uri_template": "constraints://{table_name}",
                            "parameter_received": table_name
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                
                constraints_data[table_name] = await _get_table_constraints(cursor, table_name)
            
            conn.close()
            
            # Build response
            result = {
                "error": False,
                "table_name": table_name,
                "constraints": constraints_data,
                "resource_info": {
                    "resource_type": "database_constraints",
                    "uri_template": "constraints://{table_name}",
                    "parameter_received": table_name,
                    "retrieved_at": datetime.now().isoformat(),
                    "learning_phase": "Resource #8 - Database Constraints",
                    "database_file": str(db_path.absolute()),
                    "database_type": "SQLite"
                },
                "llm_context": {
                    "purpose": f"Database constraints for {table_name} - essential for understanding data validation rules",
                    "usage_hint": f"Use constraint information to generate valid SQL that respects data integrity rules for {table_name}.",
                    "validation_importance": "Constraints define business rules - SQL queries must respect these to avoid errors.",
                    "recommended_use": "Combine with schema://{table} for complete table understanding including validation rules."
                },
                "server_info": {
                    "server_name": "mcp-test-server",
                    "resource_purpose": "Data validation context for LLM SQL generation"
                }
            }
            
            print(f"[DEBUG] Successfully retrieved constraints for {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] Database error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "database_constraints",
                    "uri_template": "constraints://{table_name}",
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
                    "resource_type": "database_constraints",
                    "uri_template": "constraints://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_database_constraints


async def _get_table_constraints(cursor, table_name: str) -> dict:
    """Get comprehensive constraint information for a specific table."""
    
    constraints = {
        "table_name": table_name,
        "column_constraints": {},
        "table_constraints": {
            "primary_keys": [],
            "foreign_keys": [],
            "unique_constraints": [],
            "check_constraints": []
        },
        "constraint_summary": {
            "total_constraints": 0,
            "has_primary_key": False,
            "has_foreign_keys": False,
            "has_unique_constraints": False,
            "has_check_constraints": False,
            "nullable_columns": 0,
            "not_null_columns": 0
        }
    }
    
    # Get column-level constraints from PRAGMA table_info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_info = cursor.fetchall()
    
    for col in columns_info:
        col_name = col[1]
        col_type = col[2]
        not_null = bool(col[3])
        default_value = col[4]
        is_pk = bool(col[5])
        
        column_constraint = {
            "column_name": col_name,
            "data_type": col_type,
            "not_null": not_null,
            "primary_key": is_pk,
            "default_value": default_value,
            "constraints": []
        }
        
        # Build constraint list for this column
        if is_pk:
            column_constraint["constraints"].append("PRIMARY KEY")
            constraints["table_constraints"]["primary_keys"].append(col_name)
            constraints["constraint_summary"]["has_primary_key"] = True
        
        if not_null:
            column_constraint["constraints"].append("NOT NULL")
            constraints["constraint_summary"]["not_null_columns"] += 1
        else:
            constraints["constraint_summary"]["nullable_columns"] += 1
        
        if default_value is not None:
            column_constraint["constraints"].append(f"DEFAULT {default_value}")
        
        constraints["column_constraints"][col_name] = column_constraint
    
    # Get foreign key constraints
    cursor.execute(f"PRAGMA foreign_key_list({table_name})")
    foreign_keys = cursor.fetchall()
    
    for fk in foreign_keys:
        fk_constraint = {
            "column": fk[3],
            "references_table": fk[2],
            "references_column": fk[4],
            "constraint_name": f"fk_{table_name}_{fk[3]}"
        }
        constraints["table_constraints"]["foreign_keys"].append(fk_constraint)
        
        # Add to column constraint info
        if fk[3] in constraints["column_constraints"]:
            constraints["column_constraints"][fk[3]]["constraints"].append(
                f"FOREIGN KEY REFERENCES {fk[2]}({fk[4]})"
            )
    
    if foreign_keys:
        constraints["constraint_summary"]["has_foreign_keys"] = True
    
    # Get unique constraints from indexes
    unique_constraints = await _get_unique_constraints(cursor, table_name)
    constraints["table_constraints"]["unique_constraints"] = unique_constraints
    if unique_constraints:
        constraints["constraint_summary"]["has_unique_constraints"] = True
    
    # Get CHECK constraints from CREATE TABLE statement
    check_constraints = await _get_check_constraints(cursor, table_name)
    constraints["table_constraints"]["check_constraints"] = check_constraints
    if check_constraints:
        constraints["constraint_summary"]["has_check_constraints"] = True
    
    # Calculate total constraints
    constraints["constraint_summary"]["total_constraints"] = (
        len(constraints["table_constraints"]["primary_keys"]) +
        len(constraints["table_constraints"]["foreign_keys"]) +
        len(constraints["table_constraints"]["unique_constraints"]) +
        len(constraints["table_constraints"]["check_constraints"]) +
        constraints["constraint_summary"]["not_null_columns"]
    )
    
    return constraints


async def _get_unique_constraints(cursor, table_name: str) -> list:
    """Extract UNIQUE constraints from table indexes."""
    
    unique_constraints = []
    
    # Get all indexes for the table
    cursor.execute(f"PRAGMA index_list({table_name})")
    indexes = cursor.fetchall()
    
    for index in indexes:
        index_name = index[1]
        is_unique = bool(index[2])
        
        if is_unique:
            # Get columns in this unique index
            cursor.execute(f"PRAGMA index_info({index_name})")
            index_columns = cursor.fetchall()
            
            columns = [col[2] for col in index_columns]
            
            # Skip primary key indexes (they're already captured as PK)
            if len(columns) == 1:
                cursor.execute(f"PRAGMA table_info({table_name})")
                table_info = cursor.fetchall()
                for col_info in table_info:
                    if col_info[1] == columns[0] and col_info[5]:  # is primary key
                        break
                else:
                    # Not a primary key, it's a unique constraint
                    unique_constraints.append({
                        "constraint_name": index_name,
                        "columns": columns,
                        "constraint_type": "UNIQUE"
                    })
            else:
                # Multi-column unique constraint
                unique_constraints.append({
                    "constraint_name": index_name,
                    "columns": columns,
                    "constraint_type": "UNIQUE"
                })
    
    return unique_constraints


async def _get_check_constraints(cursor, table_name: str) -> list:
    """Extract CHECK constraints from CREATE TABLE statement."""
    
    check_constraints = []
    
    try:
        # Get the CREATE TABLE statement
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        result = cursor.fetchone()
        
        if result and result[0]:
            create_sql = result[0]
            
            # Look for CHECK constraints in the CREATE TABLE statement
            # This is a simplified parser - SQLite CHECK constraints can be complex
            check_pattern = r'CHECK\s*\(([^)]+)\)'
            matches = re.finditer(check_pattern, create_sql, re.IGNORECASE)
            
            for i, match in enumerate(matches):
                check_condition = match.group(1).strip()
                check_constraints.append({
                    "constraint_name": f"check_{table_name}_{i+1}",
                    "check_condition": check_condition,
                    "constraint_type": "CHECK"
                })
    
    except Exception:
        # If parsing fails, just return empty list
        pass
    
    return check_constraints


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]