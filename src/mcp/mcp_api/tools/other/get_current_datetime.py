from mcp_init import mcp
from typing import Optional
import json
from datetime import datetime
import pytz

@mcp.tool()
def get_current_datetime(timezone: Optional[str] = None, format: Optional[str] = None) -> str:
    """
    Retrieves the current date and time.
    
    OPTIONAL PARAMETERS:
    - timezone: Time zone (string, optional)
      EXAMPLES: 'Europe/Paris', 'America/New_York', 'UTC', 'Asia/Tokyo'
      DEFAULT: System local time
    - format: Custom output format (string, optional)
      EXAMPLES: 
        - '%Y-%m-%d %H:%M:%S' (MySQL format)
        - '%d/%m/%Y %H:%M' (French format)
        - '%Y-%m-%d' (date only)
        - '%H:%M:%S' (time only)
      DEFAULT: Complete ISO format
    
    PREDEFINED FORMATS AVAILABLE:
    - 'mysql': Format for MySQL database (YYYY-MM-DD HH:MM:SS)
    - 'date_only': Date only (YYYY-MM-DD)
    - 'time_only': Time only (HH:MM:SS)
    - 'french': French format (DD/MM/YYYY HH:MM)
    - 'iso': Complete ISO format (default)
    
    USAGE EXAMPLES:
    - Simple current time: get_current_datetime()
    - Paris time: get_current_datetime(timezone="Europe/Paris")
    - MySQL format: get_current_datetime(format="mysql")
    - Custom format: get_current_datetime(format="%d/%m/%Y at %H:%M")
    - Paris + MySQL: get_current_datetime(timezone="Europe/Paris", format="mysql")
    
    RETURN:
    JSON with formatted date/time and timezone information.
    """
    
    try:
        if timezone:
            try:
                tz = pytz.timezone(timezone)
                current_time = datetime.now(tz)
            except pytz.exceptions.UnknownTimeZoneError:
                return f"❌ Error: Invalid timezone '{timezone}'. Valid examples: 'Europe/Paris', 'UTC', 'America/New_York'"
        else:
            current_time = datetime.now()
        
        # Predefined formats
        predefined_formats = {
            'mysql': '%Y-%m-%d %H:%M:%S',
            'date_only': '%Y-%m-%d', 
            'time_only': '%H:%M:%S',
            'french': '%d/%m/%Y %H:%M',
            'iso': None  # Default format
        }
        
        # Determine format to use
        if format in predefined_formats:
            if format == 'iso':
                formatted_time = current_time.isoformat()
            else:
                formatted_time = current_time.strftime(predefined_formats[format])
        elif format:
            # Custom format
            try:
                formatted_time = current_time.strftime(format)
            except ValueError as e:
                return f"❌ Error: Invalid format '{format}'. Error: {str(e)}"
        else:
            # Default format (ISO)
            formatted_time = current_time.isoformat()
        
        # Prepare result
        result = {
            "success": True,
            "datetime": formatted_time,
            "timestamp": current_time.timestamp(),
            "timezone": str(current_time.tzinfo) if current_time.tzinfo else "Local",
            "weekday": current_time.strftime("%A"),
            "weekday_fr": {
                "Monday": "Monday",
                "Tuesday": "Tuesday", 
                "Wednesday": "Wednesday",
                "Thursday": "Thursday",
                "Friday": "Friday",
                "Saturday": "Saturday",
                "Sunday": "Sunday"
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
        return f"❌ Unexpected error: {str(e)}"