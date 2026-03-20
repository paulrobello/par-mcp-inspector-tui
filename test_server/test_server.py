"""MCP Test Server for par-mcp-inspector-tui development and testing.

Resources Available:
- Static server info (server://info)
- Dynamic user info (user://{user_id})
- File system with wildcards (files://{filepath*})

Tools Available:
- fibonacci: Generate Fibonacci sequences
- add_numbers: Simple addition for testing
"""

from fastmcp import FastMCP

from resources import register_all_resources

mcp = FastMCP("mcp-test-server")

registered_resources = register_all_resources(mcp)
print(f"[INFO] MCP Test Server initialized with {len(registered_resources)} resources")


@mcp.tool()
def fibonacci(n: int) -> list[int]:
    """Generate a Fibonacci sequence of length n.

    Args:
        n: Number of Fibonacci numbers to generate (0-1000).

    Returns:
        List of Fibonacci numbers starting from F(0)=0.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i - 1] + seq[i - 2])
    return seq


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two integers.

    Args:
        a: First integer.
        b: Second integer.

    Returns:
        Sum of a and b.
    """
    return a + b


if __name__ == "__main__":
    mcp.run()
