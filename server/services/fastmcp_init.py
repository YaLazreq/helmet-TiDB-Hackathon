from fastmcp import FastMCP  # Only one import needed

try:
    mcp = FastMCP("api-server", description="Maps API Server")
except Exception as e:
    raise RuntimeError(f"Failed to initialize FastMCP: {str(e)}")

# Export mcp instance
__all__ = [
    "mcp",
]
