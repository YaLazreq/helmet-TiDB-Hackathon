from services.fastmcp_init import mcp
from services.logger_init import logger
import os

# Import all tools so their decorators get executed
import tools.distance_matrix
import tools.find_place
import tools.places_nearby
import tools.places_search
import tools.geocode
import tools.reverse_geocode

if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8080))
    logger.info(f"MCP server starting on port {port}")

    mcp.run(
        transport="streamable-http",  # Use underscore, not hyphen
        host="0.0.0.0",
        port=port,
    )
