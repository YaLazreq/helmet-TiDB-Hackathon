from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def search_users(id: Optional[str] = None, first_name: Optional[str] = None, last_name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None, role: Optional[str] = None, specialization: Optional[str] = None, is_active: Optional[bool] = None, limit: Optional[int] = 1000) -> str:
    """
    Search for users based on various criteria.

    AVAILABLE PARAMETERS:

    IDENTIFICATION:
    - id: Unique user identifier (string)
    - first_name: User's first name (string, partial search allowed)
    - last_name: User's last name (string, partial search allowed)
    - email: Email address (string, partial search allowed)
    - phone: Phone number (string)

    ROLE & FUNCTION:
    - role: Role in the company (enum)
      EXACT OPTIONS: see the get_user_roles() function
    - specialization: Trade/specialization (string)
      EXAMPLES: 'electrician', 'plumber', 'mason', 'painter', 'roofer', 'carpenter'

    STATUS:
    - is_active: Whether the user is active (boolean: true/false)

    OTHER:
    - limit: Maximum number of results (default: 1000)

    USAGE EXAMPLES:
    - Find a user by ID: search_users(id="user123")
    - All active electricians: search_users(role="worker", specialization="electrician", is_active=true)
    - Search by partial name: search_users(name="Jean")
    - All managers: search_users(role="manager")
    - Inactive users: search_users(is_active=false)

    RETURN:
    JSON with the list of found users and their complete information.
    """
    
    conditions = []
    params = []
    
    if id:
        conditions.append("id = %s")
        params.append(id)

    if first_name:
        conditions.append("first_name LIKE %s")
        params.append(f"%{first_name}%")

    if last_name:
        conditions.append("last_name LIKE %s")
        params.append(f"%{last_name}%")

    if email:
        conditions.append("email LIKE %s")
        params.append(f"%{email}%")
        
    if phone:
        conditions.append("phone = %s")
        params.append(phone)
        
    if role:
        valid_roles = ['worker', 'chief', 'manager', 'admin']
        if role not in valid_roles:
            return f"❌ Error: Invalid role '{role}'. Valid roles: {valid_roles}"
        conditions.append("role = %s")
        params.append(role)
        
    if specialization:
        conditions.append("specialization LIKE %s")
        params.append(f"%{specialization}%")
        
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT 
        id,
        first_name,
        last_name,
        email, 
        phone,
        role,
        specialization,
        created_at,
        updated_at,
        is_active
    FROM users 
    WHERE {where_clause}
    ORDER BY first_name ASC
    LIMIT {limit or 10}
    """

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        users_list = []
        for row in results:
            user_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, datetime):
                    user_dict[columns[i]] = value.isoformat()
                else:
                    user_dict[columns[i]] = value
            users_list.append(user_dict)
        
    except Exception as e:
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()

    if not users_list:
        return "❌ No users found with these criteria."
    
    result = {
        "total_found": len(users_list),
        "criteria_used": {k: v for k, v in {
            "id": id, "first_name": first_name, "last_name": last_name, "email": email, "phone": phone,
            "role": role, "specialization": specialization, "is_active": is_active
        }.items() if v is not None},
        "users": users_list
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)