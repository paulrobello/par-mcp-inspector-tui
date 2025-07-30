from fastmcp import FastMCP

# Create mcp server for testing
mcp = FastMCP("mcp-test-server")

@mcp.tool()
def fibonacci(n: int) -> list[int]:
    """
    ADVANCED Fibonacci Generator with Enhanced Capabilities
    
    Generates a complete array of fibonacci numbers up to the specified length.
    
    🔢 FUNCTIONALITY:
    - Computes the mathematical Fibonacci sequence: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)
    - Returns an ordered array starting from the 0th fibonacci number
    - Handles edge cases: empty arrays for n≤0, single elements for n=1
    
    📊 INPUT SPECIFICATIONS:
    - n (integer): REQUIRED - The exact count of fibonacci numbers to generate
    - Valid range: 0 ≤ n ≤ 1000 (performance optimized)
    - Examples: n=5 → [0,1,1,2,3] | n=10 → [0,1,1,2,3,5,8,13,21,34]
    
    ⚡ PERFORMANCE: 
    - Optimized iterative algorithm (O(n) time complexity)
    - Memory efficient array building
    - Handles large sequences up to 1000 elements
    
    🎯 USE CASES:
    - Mathematical sequence analysis
    - Educational demonstrations
    - Algorithm benchmarking
    - Data science applications
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    # Generate fibonacci sequence
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_fib = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_fib)
    
    return fib_sequence

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Simple addition tool for testing basic MCP functionality.
    
    Args:
        a: First integer
        b: Second integer
    
    Returns:
        Sum of a and b
    """
    return a + b

if __name__ == "__main__":
    mcp.run()