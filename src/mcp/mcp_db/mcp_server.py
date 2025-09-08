from mcp_init import mcp
import os

# Users
import tools.users.repositories.get_users
import tools.users.repositories.create_user
import tools.users.repositories.update_user
import tools.users.repositories.get_users_for_context

import tools.users.others.get_user_roles
import tools.users.others.get_skill_categories

# Tasks
import tools.tasks.repositories.get_tasks
import tools.tasks.repositories.create_task
import tools.tasks.repositories.update_task

# Storage
import tools.storage.get_table_schemas


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8080))

    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )
