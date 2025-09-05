from mcp_init import mcp
from typing import Optional
import json
from datetime import datetime
import pytz

@mcp.tool()
def get_current_datetime(timezone: Optional[str] = None, format: Optional[str] = None) -> str:
    """
    Récupère la date et l'heure actuelles.
    
    PARAMÈTRES OPTIONNELS:
    - timezone: Fuseau horaire (string, optionnel)
      EXEMPLES: 'Europe/Paris', 'America/New_York', 'UTC', 'Asia/Tokyo'
      DÉFAUT: Heure locale du système
    - format: Format de sortie personnalisé (string, optionnel)
      EXEMPLES: 
        - '%Y-%m-%d %H:%M:%S' (format MySQL)
        - '%d/%m/%Y %H:%M' (format français)
        - '%Y-%m-%d' (date seulement)
        - '%H:%M:%S' (heure seulement)
      DÉFAUT: Format ISO complet
    
    FORMATS PRÉDÉFINIS DISPONIBLES:
    - 'mysql': Format pour base de données MySQL (YYYY-MM-DD HH:MM:SS)
    - 'date_only': Date seulement (YYYY-MM-DD)
    - 'time_only': Heure seulement (HH:MM:SS)
    - 'french': Format français (DD/MM/YYYY HH:MM)
    - 'iso': Format ISO complet (défaut)
    
    EXEMPLES D'UTILISATION:
    - Heure actuelle simple: get_current_datetime()
    - Heure de Paris: get_current_datetime(timezone="Europe/Paris")
    - Format MySQL: get_current_datetime(format="mysql")
    - Format personnalisé: get_current_datetime(format="%d/%m/%Y à %H:%M")
    - Paris + MySQL: get_current_datetime(timezone="Europe/Paris", format="mysql")
    
    RETOUR:
    JSON avec la date/heure formatée et les informations de timezone.
    """
    
    try:
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                return f"❌ Erreur: Timezone '{timezone}' invalide. Exemples valides: 'Europe/Paris', 'UTC', 'America/New_York'"
        else:
            current_time = datetime.now()
        
        # Formats prédéfinis
        predefined_formats = {
            'mysql': '%Y-%m-%d %H:%M:%S',
            'date_only': '%Y-%m-%d', 
            'time_only': '%H:%M:%S',
            'french': '%d/%m/%Y %H:%M',
            'iso': None  # Format par défaut
        }
        
        # Déterminer le format à utiliser
        if format in predefined_formats:
            if format == 'iso':
                formatted_time = current_time.isoformat()
            else:
                formatted_time = current_time.strftime(predefined_formats[format])
        elif format:
            # Format personnalisé
            try:
                formatted_time = current_time.strftime(format)
            except ValueError as e:
                return f"❌ Erreur: Format '{format}' invalide. Erreur: {str(e)}"
        else:
            # Format par défaut (ISO)
            formatted_time = current_time.isoformat()
        
        # Préparer le résultat
        result = {
            "success": True,
            "datetime": formatted_time,
            "timestamp": current_time.timestamp(),
            "timezone": str(current_time.tzinfo) if current_time.tzinfo else "Local",
            "weekday": current_time.strftime("%A"),
            "weekday_fr": {
                "Monday": "Lundi",
                "Tuesday": "Mardi", 
                "Wednesday": "Mercredi",
                "Thursday": "Jeudi",
                "Friday": "Vendredi",
                "Saturday": "Samedi",
                "Sunday": "Dimanche"
            }.get(current_time.strftime("%A"), current_time.strftime("%A")),
            "details": {
                "year": current_time.year,
                "month": current_time.month,
                "day": current_time.day,
                "hour": current_time.hour,
                "minute": current_time.minute,
                "second": current_time.second,
                "microsecond": current_time.microsecond
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return f"❌ Erreur inattendue: {str(e)}"