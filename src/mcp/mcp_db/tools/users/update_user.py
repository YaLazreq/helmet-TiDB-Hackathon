from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime


@mcp.tool()
def update_user(
    user_id: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    role: Optional[str] = None,
    specialization: Optional[str] = None,
    is_active: Optional[bool] = None,
) -> str:
    """
    Modifies an existing user in the database.

    MANDATORY PARAMETERS:
    - user_id: ID of the user to modify (string, must exist in users table)

    OPTIONAL PARAMETERS (only provided parameters will be modified):
    - first_name: New first name (string, non-empty if provided)
    - last_name: New last name (string, non-empty if provided)
    - email: New email address (string, valid email format, unique)
    - phone: New phone number (string)
    - role: New role in the company (string)
      EXACT OPTIONS: 'worker', 'chief', 'manager', 'admin'
    - specialization: New specialization/trade (string)
      EXAMPLES: 'electrician', 'plumber', 'mason', 'painter', 'roofer', 'carpenter'
    - is_active: New active/inactive status (boolean: true/false)

    AUTOMATIC VALIDATIONS:
    - user_id must exist in the database
    - First name and last name non-empty if provided
    - Valid email format if provided
    - Email unique in database if provided
    - Role among allowed values if provided
    - Automatic update of updated_at timestamp

    USAGE EXAMPLES:
    - Change name: update_user("user123", first_name="Jean", last_name="Dupont")
    - Change role: update_user("user123", role="manager")
    - Deactivate user: update_user("user123", is_active=false)
    - Change specialization: update_user("user123", specialization="electrician")
    - Complete modification: update_user("user123", first_name="Pierre", email="pierre@email.com", role="chief", is_active=true)
    - Update contact: update_user("user123", email="nouveau@email.com", phone="0123456789")

    RETURN:
    JSON with modified user information or error message.
    """
    print(
        f"🔧 Modifying user '{user_id}' with params: first_name={first_name}, last_name={last_name}, email={email}, phone={phone}, role={role}, specialization={specialization}, is_active={is_active}"
    )

    import re

    if not user_id or not user_id.strip():
        return "❌ Erreur: user_id est obligatoire et ne peut pas être vide."

    user_id = user_id.strip()

    update_params = [
        first_name,
        last_name,
        email,
        phone,
        role,
        specialization,
        is_active,
    ]
    if all(param is None for param in update_params):
        return "❌ Error: At least one parameter to modify must be provided."

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return f"❌ Error: User with ID '{user_id}' does not exist."

        update_fields = []
        update_values = []

        if first_name is not None:
            if not first_name or not first_name.strip():
                return "❌ Erreur: Le prénom ne peut pas être vide."
            update_fields.append("first_name = %s")
            update_values.append(first_name.strip())

        if last_name is not None:
            if not last_name or not last_name.strip():
                return "❌ Erreur: Le nom de famille ne peut pas être vide."
            update_fields.append("last_name = %s")
            update_values.append(last_name.strip())

        if email is not None:
            if not email or not email.strip():
                return "❌ Erreur: L'email ne peut pas être vide."

            email = email.strip().lower()

            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                return "❌ Erreur: Format d'email invalide."

            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id)
            )
            if cursor.fetchone():
                return f"❌ Erreur: L'email '{email}' est déjà utilisé par un autre utilisateur."

            update_fields.append("email = %s")
            update_values.append(email)

        if phone is not None:
            phone_value = phone.strip() if phone else None
            update_fields.append("phone = %s")
            update_values.append(phone_value)

        if role is not None:
            valid_roles = ["worker", "chief", "manager", "admin"]
            if role not in valid_roles:
                return (
                    f"❌ Erreur: Rôle '{role}' invalide. Rôles possibles: {valid_roles}"
                )
            update_fields.append("role = %s")
            update_values.append(role)

        if specialization is not None:
            spec_value = specialization.strip() if specialization else None
            update_fields.append("specialization = %s")
            update_values.append(spec_value)

        if is_active is not None:
            if not isinstance(is_active, bool):
                return "❌ Erreur: is_active doit être un booléen (true/false)."
            update_fields.append("is_active = %s")
            update_values.append(is_active)

        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())

            update_values.append(user_id)

            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)
            db.commit()

            cursor.execute(
                """
                SELECT id, first_name, last_name, email, phone, role, specialization,
                       created_at, updated_at, is_active
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
                    "message": f"✅ Utilisateur '{user_id}' modifié avec succès.",
                    "user": user_dict,
                    "fields_updated": len(update_fields) - 1,
                }
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                return "❌ Erreur: Utilisateur modifié mais impossible de le récupérer."
        else:
            return "❌ Erreur: Aucun champ valide à mettre à jour."

    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()
