"""
Universal Users Tool for MCP Database Server
==========================================

This is the ONE-STOP tool for ALL user operations in your MCP database server.
Whether you need to list, search, filter, or paginate users - this tool does it all!

Author: Assistant
Date: 2025-09-06
"""

from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime, date
from decimal import Decimal


@mcp.tool()
def get_users(
    user_id: Optional[int] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    hire_date: Optional[str] = None,
    primary_skill: Optional[str] = None,
    trade_category: Optional[str] = None,
    min_experience_years: Optional[float] = None,
    max_experience_years: Optional[float] = None,
    has_certification: Optional[str] = None,
    has_safety_training: Optional[str] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
) -> str:
    """
    🔍 ADVANCED USER SEARCH TOOL - Get, List, Search & Filter Users with Skills

    This is your ONE-STOP tool for ALL user search operations! Whether you need to:
    - 📋 List all users with full skill profiles
    - 🎯 Find specific users by ID
    - 🔍 Search by name, email, skills, certifications
    - 🛠️ Filter by trade categories and experience
    - 📄 Get paginated results with comprehensive data

    PARAMETERS (All Optional - Mix & Match!):
    ========================================

    🆔 IDENTIFICATION:
    user_id : int - Exact user ID (1, 2, 123, etc.)
    first_name : str - Partial name search ("Jean" finds "Jean Dupont")
    last_name : str - Partial surname search ("Dup" finds "Dupont")
    email : str - Partial email search ("jean" finds "jean.dupont@...")
    phone : str - Partial phone search ("+33" finds French numbers)
    address : str - Partial address search ("Paris" finds Paris addresses)

    👷 ROLE & STATUS:
    role : str - Exact role: "worker", "team_leader", "supervisor", "site_manager"
    is_active : bool - User status (true/false/null for all)
    hire_date : str - Exact hire date (format: "YYYY-MM-DD")

    🛠️ SKILLS & EXPERIENCE:
    primary_skill : str - Search in primary skills ("electrical_installation")
    trade_category : str - Search in trade categories ("electricity", "plumbing")
    min_experience_years : float - Minimum years of experience (e.g., 5.0)
    max_experience_years : float - Maximum years of experience (e.g., 15.0)

    🎓 CERTIFICATIONS & TRAINING:
    has_certification : str - Search in certifications ("crane_license", "electrical_permit")
    has_safety_training : str - Search in safety training ("fall_prevention", "first_aid")

    📄 PAGINATION:
    limit : int - Max results (1-1000, default: 50)
    offset : int - Skip records for pagination (default: 0)

    💡 USAGE EXAMPLES (Copy & Use!):
    ===============================

    # 📋 SIMPLE LISTING:
    get_users()  # First 50 users with full profiles
    get_users(limit=10)  # First 10 users
    get_users(is_active=True)  # All active users

    # 🎯 SPECIFIC USER:
    get_users(user_id=2)  # Exact user by ID

    # 🔍 NAME & CONTACT SEARCHES:
    get_users(first_name="Jean")  # All Jeans
    get_users(email="gmail")  # Users with gmail addresses
    get_users(address="Paris")  # Users in Paris

    # 👷 ROLE & HIERARCHY:
    get_users(role="supervisor")  # All supervisors
    get_users(role="worker", is_active=True)  # Active workers

    # 🛠️ SKILLS & TRADES:
    get_users(primary_skill="electrical_installation")  # Electricians
    get_users(trade_category="plumbing")  # All plumbers
    get_users(min_experience_years=10.0)  # Experienced workers (10+ years)
    get_users(max_experience_years=2.0)  # Junior workers (<2 years)

    # 🎓 CERTIFICATIONS:
    get_users(has_certification="crane_license")  # Crane operators
    get_users(has_safety_training="first_aid")  # First aid trained

    # 🔥 COMPLEX COMBINATIONS:
    get_users(role="worker", trade_category="electricity", min_experience_years=5.0)
    get_users(has_certification="electrical_permit", is_active=True, limit=10)


    RETURN FORMAT:
    =============
    JSON object with complete user profiles:
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
                "email": "john.doe@company.com",
                "phone": "+1234567890",
                "address": "15 Rue de la Paix, Paris",
                "role": "worker|team_leader|supervisor|site_manager",
                "is_active": true,
                "hire_date": "2020-01-15",
                "primary_skills": ["electrical_installation", "plumbing_repair"],
                "secondary_skills": ["welding", "height_work"],
                "trade_categories": ["electricity", "plumbing"],
                "experience_years": 8.5,
                "skill_levels": {"electrical_installation": 9, "plumbing": 7},
                "work_preferences": ["indoor", "teamwork"],
                "equipment_mastery": ["drill", "multimeter"],
                "project_experience": ["residential", "commercial"],
                "certifications": ["electrical_permit_B1V", "first_aid"],
                "safety_training": ["fall_protection", "electrical_safety"],
                "last_training_date": "2024-01-15",
                "created_at": "2020-01-15T10:00:00",
                "updated_at": "2024-01-15T14:30:00"
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
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "role": role,
                    "is_active": is_active,
                    "hire_date": hire_date,
                    "primary_skill": primary_skill,
                    "trade_category": trade_category,
                    "min_experience_years": min_experience_years,
                    "max_experience_years": max_experience_years,
                    "has_certification": has_certification,
                    "has_safety_training": has_safety_training,
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
                    "email": email,
                    "phone": phone,
                    "role": role,
                    "address": address,
                    "is_active": is_active,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    # Role validation
    if role:
        valid_roles = ["worker", "team_leader", "supervisor", "site_manager"]
        if role not in valid_roles:
            return json.dumps(
                {
                    "success": False,
                    "error": "Invalid role",
                    "message": f"Role '{role}' is invalid. Valid roles: {valid_roles}",
                },
                indent=2,
            )

    # Experience validation
    if min_experience_years is not None and min_experience_years < 0:
        return json.dumps({"success": False, "error": "min_experience_years must be >= 0"}, indent=2)
    
    if max_experience_years is not None and max_experience_years < 0:
        return json.dumps({"success": False, "error": "max_experience_years must be >= 0"}, indent=2)
    
    if (min_experience_years is not None and max_experience_years is not None 
        and min_experience_years > max_experience_years):
        return json.dumps({"success": False, "error": "min_experience_years cannot be greater than max_experience_years"}, indent=2)

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

    if email:
        conditions.append("email LIKE %s")
        params.append(f"%{email}%")

    if phone:
        conditions.append("phone LIKE %s")
        params.append(f"%{phone}%")

    if address:
        conditions.append("address LIKE %s")
        params.append(f"%{address}%")

    # Role & Status filters
    if role:
        conditions.append("role = %s")
        params.append(role)

    if is_active is not None:
        conditions.append("is_active = %s")
        params.append(is_active)

    if hire_date:
        conditions.append("hire_date = %s")
        params.append(hire_date)

    # Skills & Experience filters
    if primary_skill:
        conditions.append("JSON_CONTAINS(primary_skills, %s)")
        params.append(f'"{primary_skill}"')

    if trade_category:
        conditions.append("JSON_CONTAINS(trade_categories, %s)")
        params.append(f'"{trade_category}"')

    if min_experience_years is not None:
        conditions.append("experience_years >= %s")
        params.append(min_experience_years)

    if max_experience_years is not None:
        conditions.append("experience_years <= %s")
        params.append(max_experience_years)

    # Certifications & Training filters
    if has_certification:
        conditions.append("JSON_CONTAINS(certifications, %s)")
        params.append(f'"{has_certification}"')

    if has_safety_training:
        conditions.append("JSON_CONTAINS(safety_training, %s)")
        params.append(f'"{has_safety_training}"')

    # Build WHERE clause
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Build complete query with intelligent sorting
    query = f"""
    SELECT 
        id,
        first_name,
        last_name,
        email,
        phone,
        address,
        role,
        is_active,
        hire_date,
        primary_skills,
        secondary_skills,
        trade_categories,
        experience_years,
        skill_levels,
        work_preferences,
        equipment_mastery,
        project_experience,
        certifications,
        safety_training,
        last_training_date,
        vector,
        created_at,
        updated_at
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
        experience_years DESC,
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
                    "email": email,
                    "phone": phone,
                    "role": role,
                    "address": address,
                    "is_active": is_active,
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
                # Handle boolean values (MySQL returns 0/1)
                elif column_name == "is_active" and isinstance(value, int):
                    user_dict[column_name] = bool(value)
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
                    "email": email,
                    "phone": phone,
                    "role": role,
                    "address": address,
                    "is_active": is_active,
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
            "email": email,
            "phone": phone,
            "role": role,
            "address": address,
            "is_active": is_active,
            "limit": limit or 50,
            "offset": offset or 0,
        }.items()
        if v is not None
    }

    # Generate smart message
    if user_id:
        if users_list:
            message = f"✅ User with ID '{user_id}' found successfully"
        else:
            message = f"❌ No user found with ID '{user_id}'"
    elif (
        len(
            [
                p
                for p in [
                    first_name,
                    last_name,
                    email,
                    phone,
                    role,
                    address,
                    is_active,
                ]
                if p is not None
            ]
        )
        > 0
    ):
        message = f"✅ Found {len(users_list)} user(s) matching search criteria"
    else:
        message = f"✅ Retrieved {len(users_list)} user(s) (simple listing)"

    result = {
        "success": True,
        "message": message,
        "total_returned": len(users_list),
        "query_params": used_params,
        "users": users_list,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)
