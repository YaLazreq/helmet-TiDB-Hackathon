from mcp_init import mcp

@mcp.tool()
def ask_for_user_input(query: str) -> str:
    """
    Asks the user to enter input in response to a question/request.
    """
    user_input = input(f"{query} ")
    return user_input