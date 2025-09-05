from mcp_init import mcp

@mcp.tool()
def ask_for_user_input(query: str) -> str:
    """
    Demande à l'utilisateur de saisir une entrée en réponse à une question/demande.
    """
    user_input = input(f"{query} ")
    return user_input