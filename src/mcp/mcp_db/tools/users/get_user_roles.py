from mcp_init import mcp
import json


@mcp.tool()
def get_user_roles() -> str:
    """
    Lists all possible roles in the system.

    Useful to know the exact values accepted by the 'role' parameter
    of the search_users() tool.
    """
    roles = {
        "available_roles": ["worker", "chief", "manager", "admin"],
        "descriptions": {
            "worker": "Worker",
            "chief": "Team leader or site supervisor",
            "manager": "Manager/supervisor",
            "admin": "System administrator",
        },
    }

    return json.dumps(roles, indent=2, ensure_ascii=False)
