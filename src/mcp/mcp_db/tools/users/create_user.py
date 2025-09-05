from mcp_init import mcp, db
from typing import Optional
import json
from datetime import datetime
import re


@mcp.tool()
def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: Optional[str] = None,
    role: str = "worker",
    specialization: Optional[str] = None,
    is_active: bool = True,
) -> str:
    """
    Create a new user in the database.

    REQUIRED PARAMETERS:
    first_name: User's first name (string, not empty)
    last_name: User's last name (string, not empty)
    email: Valid email address (string, unique in the DB)
    password: Password (string, not empty)

    OPTIONAL PARAMETERS:
    phone: Phone number (string, optional)
    role: Role in the company (string, default: "worker")
        ALLOWED OPTIONS: 'worker', 'chief', 'manager', 'admin'
    specialization: Job/specialization (string, optional)
        EXAMPLES: 'electrician', 'plumber', 'mason', 'painter', 'roofer', 'carpenter'
        is_active: Active status (boolean, default: true)

    AUTOMATIC VALIDATIONS:
    - Valid and unique email
    - Role must be in the allowed list
    - Names must not be empty
    - Automatic generation of a unique ID (MySQL AUTO_INCREMENT)
    - Automatic timestamps (created_at, updated_at)

    USAGE EXAMPLES:
    Simple user:
    create_user("Jean", "Dupont", "jean.dupont@email.com", "motdepasse123")
    Full electrician:
    create_user("Marie", "Martin", "marie@email.com", "password456", phone="0123456789", role="worker", specialization="electrician")
    Manager:
    create_user("Pierre", "Durand", "pierre@email.com", "admin789", role="manager")
    Inactive user:
    create_user("Paul", "Bernard", "paul@email.com", "pass123", is_active=false)

    RETURN:
    JSON with the created user’s information or an error message.
    """

    if not first_name or not first_name.strip():
        return "❌ Error: First name is required and cannot be empty."

    if not last_name or not last_name.strip():
        return "❌ Error: Last name is required and cannot be empty."

    if not email or not email.strip():
        return "❌ Error: Email is required and cannot be empty."

    if not password or not password.strip():
        return "❌ Error: Password is required and cannot be empty."

    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_pattern, email.strip()):
        return "❌ Error: Invalid email format."

    valid_roles = ["worker", "chief", "manager", "admin"]
    if role not in valid_roles:
        return f"❌ Error: Invalid role '{role}'. Valid roles: {valid_roles}"

    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()
    password = password.strip()
    phone = phone.strip() if phone else None
    specialization = specialization.strip() if specialization else None

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return f"❌ Error: A user with email '{email}' already exists."

        current_time = datetime.now()

        insert_query = """
        INSERT INTO users (
            first_name, last_name, email, password, phone, role, 
            specialization, is_active, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            first_name,
            last_name,
            email,
            password,
            phone,
            role,
            specialization,
            is_active,
            current_time,
            current_time,
        )

        cursor.execute(insert_query, params)
        user_id = cursor.lastrowid
        db.commit()

        cursor.execute(
            """
            SELECT id, first_name, last_name, email, phone, role, 
                   specialization, is_active, created_at, updated_at
            FROM users WHERE id = %s
        """,
            (user_id,),
        )

        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            user_dict = {}
            for i, value in enumerate(result):
                if isinstance(value, datetime):
                    user_dict[columns[i]] = value.isoformat()
                else:
                    user_dict[columns[i]] = value

            success_result = {
                "success": True,
                "message": f"✅ User '{first_name} {last_name}' created successfully.",
                "user": user_dict,
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Error: User created but unable to retrieve it."

    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()
