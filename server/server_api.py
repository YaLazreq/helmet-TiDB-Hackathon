from services.fastmcp_init import mcp
from services.logger_init import logger
import os

# ? Connection to last Google Maps MCP server

# if __name__ == "__main__":
#     port = int(os.getenv("MCP_PORT", 8080))
#     logger.info(f"MCP server starting on port {port}")

#     mcp.run(
#         transport="streamable-http",  # Use underscore, not hyphen
#         host="0.0.0.0",
#         port=port,
#     )
