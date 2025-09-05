from mcp_init import mcp
import json

@mcp.tool()
def get_specializations() -> str:
    """
    Liste les spécialisations les plus courantes dans le système.
    
    Aide à connaître les valeurs typiques pour le paramètre 'specialization'
    de l'outil search_users().
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
            "welder"
        ]
    }
    # ON POURRAIT AUSSI LES CHERCHER DANS LA DB DIRECT COMME çA C COMPLET GENERIQUEMENT
    return json.dumps(specializations, indent=2, ensure_ascii=False)
