from mcp_init import mcp
import os

import tools.users.get_user_roles
import tools.users.get_specializations
import tools.users.create_user
import tools.users.update_user
import tools.tasks.create_task
import tools.tasks.update_task
# import tools.sql_agent.sql_agent


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8080))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port, 
    )