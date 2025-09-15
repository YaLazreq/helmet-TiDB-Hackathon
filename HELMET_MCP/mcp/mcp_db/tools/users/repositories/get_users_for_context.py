"""
Lightweight Users Context Tool for MCP Database Server
====================================================

This tool returns only essential user information for context purposes.
Returns: ID, First_name, Last_name, role, trade_categories & primary_skills.

Author: Assistant
Date: 2025-09-08
"""

from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime, date
from decimal import Decimal


@mcp.tool()
def get_users_for_context(
    user_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
) -> str:
    """
    LIGHTWEIGHT USER CONTEXT TOOL - Get Essential User Information

    This tool returns only essential user information for context purposes:
    - ID, First_name, Last_name, role, role_description, trade_categories, primary_skills

    PARAMETERS (All Optional)
    IDENTIFICATION:
    user_id : int - Exact user ID (1, 2, 123, etc.)
    first_name : str - Partial name search ("Jean" finds "Jean Dupont")
    last_name : str - Partial surname search ("Dup" finds "Dupont")
     is_active : bool - Filter by active status (true/false)

    PAGINATION:
    limit : int - Max results (1-1000, default: 50)
    offset : int - Skip records for pagination (default: 0)

    RETURN FORMAT:
    JSON object with essential user information:
    {
        "success": true/false,
        "message": "descriptive message",
        "total_returned": number,
        "query_params": {...used parameters...},
        "users": [
            {
                "id": user_id,
                "first_name": "John",
                "last_name": "Doe",
                "role": "worker|team_leader|supervisor|site_manager",
                "role_description": "Senior Construction Worker",
                "trade_categories": ["electricity", "plumbing"],
                "primary_skills": ["electrical_installation", "plumbing_repair"]
            }
        ]
    }
    """

    # Parameter validation
    if limit and (limit < 1 or limit > 1000):
        return json.dumps(
            {
                "success": False,
                "error": "Parameter validation failed",
                "message": "Limit must be between 1 and 1000",
                "query_params": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": None,
                    "is_active": is_active,
                    "primary_skill": None,
                    "trade_category": None,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    if offset and offset < 0:
        return json.dumps(
            {
                "success": False,
                "error": "Parameter validation failed",
                "message": "Offset must be 0 or greater",
                "query_params": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": None,
                    "is_active": is_active,
                    "primary_skill": None,
                    "trade_category": None,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    # Build query based on parameters
    conditions = []
    params = []

    # Identification filters
    if user_id is not None:
        conditions.append("id = %s")
        params.append(user_id)

    if first_name:
        conditions.append("first_name LIKE %s")
        params.append(f"%{first_name}%")

    if last_name:
        conditions.append("last_name LIKE %s")
        params.append(f"%{last_name}%")

    # Status filters
    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)

    # Build WHERE clause
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Build complete query - only select essential fields
    query = f"""
    SELECT 
        id,
        first_name,
        last_name,
        role,
        role_description,
        trade_categories,
        primary_skills
    FROM users 
    WHERE {where_clause}
    ORDER BY 
        CASE 
            WHEN is_active = 1 THEN 0 
            ELSE 1 
        END,
        CASE role
            WHEN 'site_manager' THEN 1
            WHEN 'supervisor' THEN 2  
            WHEN 'team_leader' THEN 3
            WHEN 'worker' THEN 4
            ELSE 5
        END,
        first_name ASC,
        last_name ASC
    LIMIT {limit or 50}
    OFFSET {offset or 0}
    """

    # Database connection and execution
    db = get_db_connection()
    if not db:
        return json.dumps(
            {
                "success": False,
                "error": "Database connection failed",
                "message": "Unable to establish database connection",
                "query_params": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": None,
                    "is_active": is_active,
                    "primary_skill": None,
                    "trade_category": None,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    cursor = db.cursor(buffered=True)

    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()

        # Process results
        users_list = []
        for row in results:
            user_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i]

                # Handle datetime and date serialization
                if isinstance(value, datetime):
                    user_dict[column_name] = value.isoformat()
                elif isinstance(value, date):
                    user_dict[column_name] = value.isoformat()
                # Handle Decimal serialization
                elif isinstance(value, Decimal):
                    user_dict[column_name] = float(value)
                else:
                    user_dict[column_name] = value

            users_list.append(user_dict)

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": "Database query failed",
                "message": f"Database error: {str(e)}",
                "query_params": {
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": None,
                    "is_active": is_active,
                    "primary_skill": None,
                    "trade_category": None,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
            ensure_ascii=False,
        )

    finally:
        cursor.close()

    # Build response with used parameters
    used_params = {
        k: v
        for k, v in {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "role": None,
            "is_active": is_active,
            "primary_skill": None,
            "trade_category": None,
            "limit": limit or 50,
            "offset": offset or 0,
        }.items()
        if v is not None
    }

    # Generate smart message
    if user_id:
        if users_list:
            message = f" User context for ID '{user_id}' found successfully"
        else:
            message = f"L No user found with ID '{user_id}'"
    elif (
        len(
            [
                p
                for p in [
                    first_name,
                    last_name,
                    is_active,
                ]
                if p is not None
            ]
        )
        > 0
    ):
        message = f" Found {len(users_list)} user(s) context matching search criteria"
    else:
        message = f" Retrieved {len(users_list)} user(s) context (simple listing)"

    result = {
        "success": True,
        "message": message,
        "total_returned": len(users_list),
        "query_params": used_params,
        "users": users_list,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)
