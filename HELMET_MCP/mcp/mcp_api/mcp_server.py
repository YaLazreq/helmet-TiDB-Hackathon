from mcp_init import mcp
import os

import tools.other.ask_for_user_input
import tools.other.get_current_datetime


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8080))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )
