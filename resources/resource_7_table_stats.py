"""
Resource #7: Table Statistics Resource

Purpose:
- Provide essential table statistics for SQL query optimization
- Lightweight aggregation queries (COUNT, MIN, MAX)
- Critical context for LLM performance guidance and index recommendations
- Complements the SQL generation trilogy with performance insights

URI Template:
- stats://{table_name} → Statistics for specified table
- stats://all → Basic statistics for all tables

This is a Tier 1 essential resource for enterprise SQL generation.
Focuses on lightweight queries that provide maximum optimization value.
"""

import sqlite3
from datetime import datetime
from pathlib import Path


def register_table_stats_resource(mcp):
    """Register the table statistics resource with the FastMCP instance."""
    
    @mcp.resource("stats://{table_name}")
    async def get_table_statistics(table_name: str) -> dict:
        """
        Resource #7: Table Statistics Resource
        
        Returns essential table statistics for SQL query optimization.
        Lightweight resource - basic aggregation queries only.
        
        Args:
            table_name: Name of the table to get statistics for, or "all"
            
        Returns:
            dict: Table statistics with row counts, column ranges, and optimization hints
        """
        print(f"[DEBUG] get_table_statistics() called with table_name: {table_name}")
        
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
                        "resource_type": "table_statistics",
                        "uri_template": "stats://{table_name}",
                        "parameter_received": table_name,
                        "expected_db_path": str(db_path)
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            stats_data = {}
            
            if table_name.lower() == "all":
                # Get basic statistics for all tables
                available_tables = await _get_available_tables(cursor)
                for table in available_tables:
                    stats_data[table] = await _get_basic_table_stats(cursor, table)
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
                            "resource_type": "table_statistics",
                            "uri_template": "stats://{table_name}",
                            "parameter_received": table_name
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                
                stats_data[table_name] = await _get_detailed_table_stats(cursor, table_name)
            
            conn.close()
            
            # Build response
            result = {
                "error": False,
                "table_name": table_name,
                "statistics": stats_data,
                "resource_info": {
                    "resource_type": "table_statistics",
                    "uri_template": "stats://{table_name}",
                    "parameter_received": table_name,
                    "retrieved_at": datetime.now().isoformat(),
                    "learning_phase": "Resource #7 - Table Statistics",
                    "database_file": str(db_path.absolute()),
                    "database_type": "SQLite"
                },
                "llm_context": {
                    "purpose": f"Table statistics for {table_name} - essential for SQL query optimization",
                    "usage_hint": f"Use row counts and column ranges to optimize queries on {table_name}. Consider indexes for large tables.",
                    "optimization_guidance": "Large tables (>1000 rows) benefit from indexes on frequently queried columns.",
                    "recommended_use": "Combine with schema://{table} and relations://{table} for complete optimization context."
                },
                "server_info": {
                    "server_name": "mcp-test-server",
                    "resource_purpose": "SQL query optimization context"
                }
            }
            
            print(f"[DEBUG] Successfully retrieved statistics for {table_name}")
            return result
            
        except sqlite3.Error as e:
            print(f"[DEBUG] Database error: {e}")
            return {
                "error": True,
                "error_type": "database_error",
                "message": f"Database error: {str(e)}",
                "table_name": table_name,
                "resource_info": {
                    "resource_type": "table_statistics",
                    "uri_template": "stats://{table_name}",
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
                    "resource_type": "table_statistics",
                    "uri_template": "stats://{table_name}",
                    "parameter_received": table_name
                },
                "timestamp": datetime.now().isoformat()
            }
    
    return get_table_statistics


async def _get_basic_table_stats(cursor, table_name: str) -> dict:
    """Get basic statistics for a table (lightweight for 'all' queries)."""
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    return {
        "table_name": table_name,
        "row_count": row_count,
        "size_category": _categorize_table_size(row_count)
    }


async def _get_detailed_table_stats(cursor, table_name: str) -> dict:
    """Get detailed statistics for a specific table."""
    
    # Get basic info
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    
    # Get column information
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns_raw = cursor.fetchall()
    
    column_stats = {}
    numeric_columns = []
    date_columns = []
    
    # Identify column types for targeted statistics
    for col in columns_raw:
        col_name = col[1]
        col_type = col[2].lower()
        
        column_info = {
            "type": col_type,
            "nullable": not bool(col[3])
        }
        
        # Categorize columns for statistics
        if any(num_type in col_type for num_type in ['int', 'real', 'numeric', 'decimal', 'float']):
            numeric_columns.append(col_name)
        elif any(date_type in col_type for date_type in ['date', 'time', 'timestamp']):
            date_columns.append(col_name)
        
        column_stats[col_name] = column_info
    
    # Get statistics for numeric columns (lightweight approach)
    for col_name in numeric_columns[:5]:  # Limit to first 5 numeric columns
        try:
            cursor.execute(f"SELECT MIN({col_name}), MAX({col_name}), AVG({col_name}) FROM {table_name} WHERE {col_name} IS NOT NULL")
            min_val, max_val, avg_val = cursor.fetchone()
            
            column_stats[col_name].update({
                "min": min_val,
                "max": max_val,
                "average": round(avg_val, 2) if avg_val else None,
                "range_size": max_val - min_val if (min_val is not None and max_val is not None) else None
            })
        except sqlite3.Error:
            # Skip problematic columns
            pass
    
    # Get statistics for date columns (lightweight approach)  
    for col_name in date_columns[:3]:  # Limit to first 3 date columns
        try:
            cursor.execute(f"SELECT MIN({col_name}), MAX({col_name}) FROM {table_name} WHERE {col_name} IS NOT NULL")
            min_date, max_date = cursor.fetchone()
            
            column_stats[col_name].update({
                "earliest": min_date,
                "latest": max_date,
                "date_range": f"{min_date} to {max_date}" if (min_date and max_date) else None
            })
        except sqlite3.Error:
            # Skip problematic columns
            pass
    
    # Calculate estimated table size (very rough estimate)
    estimated_size_kb = _estimate_table_size(row_count, len(columns_raw))
    
    return {
        "table_name": table_name,
        "row_count": row_count,
        "column_count": len(columns_raw),
        "estimated_size_kb": estimated_size_kb,
        "size_category": _categorize_table_size(row_count),
        "column_statistics": column_stats,
        "optimization_hints": _generate_optimization_hints(row_count, len(columns_raw), numeric_columns, date_columns),
        "performance_tier": _get_performance_tier(row_count)
    }


def _categorize_table_size(row_count: int) -> str:
    """Categorize table size for optimization guidance."""
    if row_count == 0:
        return "empty"
    elif row_count < 100:
        return "small"
    elif row_count < 10000:
        return "medium"
    elif row_count < 100000:
        return "large"
    else:
        return "very_large"


def _estimate_table_size(row_count: int, column_count: int) -> int:
    """Rough estimate of table size in KB."""
    # Very rough estimate: assume ~50 bytes per column per row
    bytes_estimate = row_count * column_count * 50
    return max(1, bytes_estimate // 1024)  # Convert to KB, minimum 1KB


def _generate_optimization_hints(row_count: int, column_count: int, numeric_cols: list, date_cols: list) -> dict:
    """Generate LLM-friendly optimization hints."""
    hints = {
        "indexing_recommended": row_count > 1000,
        "full_table_scan_cost": "low" if row_count < 1000 else "high" if row_count < 10000 else "very_high",
        "join_performance": "excellent" if row_count < 1000 else "good" if row_count < 10000 else "requires_optimization"
    }
    
    if numeric_cols:
        hints["numeric_columns"] = f"Consider indexes on {numeric_cols[:3]} for range queries"
    
    if date_cols:
        hints["date_columns"] = f"Consider indexes on {date_cols[:2]} for time-based queries"
    
    return hints


def _get_performance_tier(row_count: int) -> str:
    """Get performance tier for query planning."""
    if row_count < 100:
        return "instant"
    elif row_count < 1000:
        return "fast"
    elif row_count < 10000:
        return "moderate"
    elif row_count < 100000:
        return "slow"
    else:
        return "optimization_required"


async def _get_available_tables(cursor) -> list:
    """Get list of all available table names."""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    return [row[0] for row in cursor.fetchall()]