from mcp_init import mcp
import json


@mcp.tool()
def get_specializations() -> str:
    """
    Lists the most common specializations in the system.

    Helps to know the typical values for the 'specialization' parameter
    of the search_users() tool.
    """
    specializations = {
        "common_specializations": [
            "electrician",
            "plumber",
            "mason",
            "painter",
            "roofer",
            "carpenter",
            "hvac_technician",
            "welder",
        ]
    }
    # WE COULD ALSO SEARCH THEM DIRECTLY IN THE DB FOR COMPLETE GENERIC COVERAGE
    return json.dumps(specializations, indent=2, ensure_ascii=False)
