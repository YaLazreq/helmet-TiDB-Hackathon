from mcp_init import mcp
import json

@mcp.tool() 
def get_user_roles() -> str:
    """
    Liste tous les rôles possibles dans le système.
    
    Utile pour connaître les valeurs exactes acceptées par le paramètre 'role' 
    de l'outil search_users().
    """
    roles = {
        "available_roles": ["worker", "chief", "manager", "admin"],
        "descriptions": {
            "worker": "Ouvrier",
            "chief": "Chef d'équipe ou responsable de chantier", 
            "manager": "Manager/superviseur",
            "admin": "Administrateur système"
        }
    }
    
    return json.dumps(roles, indent=2, ensure_ascii=False)
