# MCP Test Server

A comprehensive test server demonstrating Model Context Protocol (MCP) resource patterns, tools, and best practices.

## Purpose

This test server provides:
- Examples of different MCP resource patterns
- Security best practices for resource implementation
- Testing tools for MCP client development
- Learning resources for MCP developers

## Structure

```
test_server/
├── test_server.py              # Main server implementation
├── resources/                  # Modular resource implementations
│   ├── __init__.py            # Resource registration
│   ├── mock_data.py           # Test data for examples
│   ├── resource_1_static_info.py       # Static resource example
│   ├── resource_2_dynamic_user.py      # Dynamic resource with parameters
│   ├── resource_3_file_system.py       # File system with security
│   ├── resource_4_db_schema.py         # Database schema resource
│   ├── resource_5_sample_data.py       # Sample data extraction
│   ├── resource_6_table_relationships.py # Table relationships
│   ├── resource_7_table_stats.py       # Table statistics
│   ├── resource_8_db_constraints.py    # Database constraints
│   └── resource_9_db_indexes.py        # Database indexes
├── MCP_RESOURCES_CHANGELOG.md  # Learning journey documentation
└── README.md                   # This file
```

## Running the Server

### Standalone
```bash
cd test_server
uv run python test_server.py
```

### With pmit (MCP Inspector TUI)
```bash
# Server is pre-configured in pmit
pmit debug "MCP Test Server"

# Or connect directly
pmit connect "uv" -a "run" -a "python" -a "test_server/test_server.py" --debug-dump
```

## Available Resources

1. **server://info** - Static server information
2. **user://{user_id}** - Dynamic user data
3. **files://{filepath*}** - File system access (with security)
4. **schema://{table_name}** - Database schema information
5. **samples://{table_name}** - Sample data from tables
6. **relations://{table_name}** - Table relationships
7. **stats://{table_name}** - Table statistics
8. **constraints://{table_name}** - Database constraints
9. **indexes://{table_name}** - Database indexes

## Available Tools

1. **fibonacci(n)** - Generate Fibonacci sequence
2. **add_numbers(a, b)** - Simple addition

## Security Features

- **Path Traversal Protection**: File resources use `Path.resolve()` with base directory validation
- **File Size Limits**: 10MB maximum file size to prevent DoS
- **Error Handling**: Comprehensive error types and messages
- **Type Safety**: Full type hints throughout

## Development

This server is intended for:
- Testing MCP client implementations
- Learning MCP resource patterns
- Demonstrating security best practices
- Prototyping new MCP features

## Credits

Originally created by aniruddhad-webonise as part of PR #1, with security enhancements and modular refactoring.
