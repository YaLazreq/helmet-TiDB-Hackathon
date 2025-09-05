from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

try:
    mcp = FastMCP("api-server")
except Exception as e:
    raise RuntimeError(f"Failed to initialize FastMCP: {str(e)}")

# Export
__all__ = [
    "mcp",
]
