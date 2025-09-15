from mcp_init import mcp
import json


@mcp.tool()
def get_user_roles() -> str:
    """
    Lists all possible roles in the system.

    Useful to know the exact values accepted by the 'role'.
    """
    roles = {
        "available_roles": [
            {"role": "worker", "description": "Worker"},
            {"role": "team_leader", "description": "Team leader or site supervisor"},
            {"role": "supervisor", "description": "Project supervisor"},
            {"role": "admin", "description": "System administrator"},
        ]
    }

    return json.dumps(roles, indent=2, ensure_ascii=False)
