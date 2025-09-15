"""
Get table schemas for all tables
"""
from mcp_init import mcp, get_db_connection
import json


@mcp.tool()
def get_table_schemas() -> str:
    """
    📊 Get complete table schemas for all database tables
    
    Returns the schema information for all tables in the current database
    in a clean, readable format perfect for use with AI agents.
    
    RETURN FORMAT:
    =============
    Formatted schema text showing:
    - Table names
    - Column names with data types
    - Primary keys (pk)
    - Auto-increment fields
    - Nullable constraints
    
    Example output:
    - users:
        id int pk auto_increment
        first_name varchar(100)
        email varchar(255)
        is_active boolean
    - tasks:
        id int pk auto_increment  
        title varchar(255)
        description text
    """
    
    # Database connection
    db = get_db_connection()
    if not db:
        return json.dumps({
            "success": False,
            "error": "Database connection failed",
            "message": "Unable to establish database connection"
        }, indent=2)
    
    cursor = db.cursor(buffered=True)
    
    try:
        # Get table schemas from INFORMATION_SCHEMA
        query = """
        SELECT 
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_KEY,
            COLUMN_DEFAULT,
            EXTRA
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = DATABASE()
        ORDER BY TABLE_NAME, ORDINAL_POSITION
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Group by table
        tables = {}
        for row in results:
            table_name, column_name, data_type, is_nullable, column_key, column_default, extra = row
            
            if table_name not in tables:
                tables[table_name] = []
            
            # Format column info
            col_info = f"{column_name} {data_type}"
            
            # Add constraints and attributes
            attributes = []
            if column_key == 'PRI':
                attributes.append("pk")
            if extra == 'auto_increment':
                attributes.append("auto_increment")
            if is_nullable == 'NO' and column_key != 'PRI':
                attributes.append("not_null")
            
            if attributes:
                col_info += " " + " ".join(attributes)
                
            tables[table_name].append(col_info)
        
        # Format as schema string
        schema_text = ""
        for table_name, columns in tables.items():
            schema_text += f"    - {table_name}:\n"
            for column in columns:
                schema_text += f"        {column}\n"
            schema_text += "\n"
        
        return schema_text.rstrip()
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": "Database query failed", 
            "message": f"Database error: {str(e)}"
        }, indent=2)
        
    finally:
        cursor.close()