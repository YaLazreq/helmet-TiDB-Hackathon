from mcp_init import mcp, get_db_connection
from typing import Optional, List
import json
from datetime import datetime, date
from decimal import Decimal
import re


@mcp.tool()
def update_user(
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    role: Optional[str] = None,
    role_description: Optional[str] = None,
    is_active: Optional[bool] = None,
    hire_date: Optional[str] = None,
    primary_skills: Optional[List[str]] = None,
    secondary_skills: Optional[List[str]] = None,
    trade_categories: Optional[List[str]] = None,
    experience_years: Optional[float] = None,
    skill_levels: Optional[dict] = None,
    work_preferences: Optional[List[str]] = None,
    equipment_mastery: Optional[List[str]] = None,
    project_experience: Optional[List[str]] = None,
    certifications: Optional[List[str]] = None,
    safety_training: Optional[List[str]] = None,
    last_training_date: Optional[str] = None,
) -> str:
    """
    🔧 ADVANCED USER UPDATE TOOL - Update User Profiles with Full Skill Management
    
    Updates comprehensive user profiles optimized for skill matching and project assignment.
    Only provided parameters will be modified.
    
    MANDATORY PARAMETERS:
    ====================
    user_id: ID of the user to modify (int, must exist in users table)
    
    OPTIONAL BASIC INFO (only provided parameters modified):
    ======================================================
    first_name: New first name (string, non-empty if provided)
    last_name: New last name (string, non-empty if provided)
    email: New email address (string, valid format, unique in DB)
    phone: New phone number (string)
    address: New work address/location (string)
    role: New user role (string)
        OPTIONS: 'worker', 'team_leader', 'supervisor', 'site_manager'
    role_description: New description of the user's role/position (string)
    is_active: New active/inactive status (boolean)
    hire_date: New hire date (string, format: "YYYY-MM-DD")
    
    OPTIONAL SKILLS & EXPERIENCE:
    =============================
    primary_skills: New main skills (List[str])
    secondary_skills: New additional skills (List[str])
    trade_categories: New trade categories (List[str])
    experience_years: New years of experience (float)
    skill_levels: New skill ratings 1-10 (dict)
    work_preferences: New work preferences (List[str])
    equipment_mastery: New equipment skills (List[str])
    project_experience: New project types (List[str])
    
    OPTIONAL CERTIFICATIONS & TRAINING:
    ===================================
    certifications: New certifications (List[str])
    safety_training: New safety training (List[str])
    last_training_date: New last training date (string, format: "YYYY-MM-DD")
    
    USAGE EXAMPLES:
    ==============
    # Update basic info
    update_user(1, first_name="Jean", last_name="Dupont")
    update_user(1, role="supervisor", is_active=True)
    
    # Update skills profile
    update_user(1, 
        primary_skills=["electrical_installation", "industrial_wiring"],
        experience_years=10.5,
        skill_levels={"electrical_installation": 9, "industrial_wiring": 8}
    )
    
    # Add certifications
    update_user(1, 
        certifications=["electrical_permit_B1V", "high_voltage"],
        last_training_date="2024-01-15"
    )

    RETURN:
    JSON with modified user information or error message.
    """
    # Basic validation
    if not isinstance(user_id, int) or user_id <= 0:
        return "❌ Error: user_id must be a positive integer."

    # Check if at least one parameter is provided
    update_params = [
        first_name, last_name, email, phone, address, role, role_description, is_active, hire_date,
        primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
        work_preferences, equipment_mastery, project_experience,
        certifications, safety_training, last_training_date
    ]
    if all(param is None for param in update_params):
        return "❌ Error: At least one parameter to modify must be provided."

    # Validate role if provided
    if role is not None:
        valid_roles = ["worker", "team_leader", "supervisor", "site_manager"]
        if role not in valid_roles:
            return f"❌ Error: Invalid role '{role}'. Valid roles: {valid_roles}"

    # Validate email format if provided
    if email is not None:
        if not email.strip():
            return "❌ Error: Email cannot be empty if provided."
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email.strip()):
            return "❌ Error: Invalid email format."

    # Validate date formats
    hire_date_obj = None
    if hire_date is not None:
        try:
            hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d").date()
        except ValueError:
            return "❌ Error: Invalid hire_date format. Use 'YYYY-MM-DD'."

    last_training_date_obj = None
    if last_training_date is not None:
        try:
            last_training_date_obj = datetime.strptime(last_training_date, "%Y-%m-%d").date()
        except ValueError:
            return "❌ Error: Invalid last_training_date format. Use 'YYYY-MM-DD'."

    # Validate experience years
    if experience_years is not None and (experience_years < 0 or experience_years > 50):
        return "❌ Error: Experience years must be between 0 and 50."

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return f"❌ Error: User with ID '{user_id}' does not exist."

        # Check email uniqueness if provided
        if email is not None:
            email = email.strip().lower()
            cursor.execute(
                "SELECT id FROM users WHERE email = %s AND id != %s", (email, user_id)
            )
            if cursor.fetchone():
                return f"❌ Error: Email '{email}' is already used by another user."

        update_fields = []
        update_values = []

        # Basic info fields
        if first_name is not None:
            if not first_name.strip():
                return "❌ Error: First name cannot be empty if provided."
            update_fields.append("first_name = %s")
            update_values.append(first_name.strip())

        if last_name is not None:
            if not last_name.strip():
                return "❌ Error: Last name cannot be empty if provided."
            update_fields.append("last_name = %s")
            update_values.append(last_name.strip())

        if email is not None:
            update_fields.append("email = %s")
            update_values.append(email)

        if phone is not None:
            phone_value = phone.strip() if phone else None
            update_fields.append("phone = %s")
            update_values.append(phone_value)

        if address is not None:
            address_value = address.strip() if address else None
            update_fields.append("address = %s")
            update_values.append(address_value)

        if role is not None:
            update_fields.append("role = %s")
            update_values.append(role)

        if role_description is not None:
            role_description_value = role_description.strip() if role_description else None
            update_fields.append("role_description = %s")
            update_values.append(role_description_value)

        if is_active is not None:
            update_fields.append("is_active = %s")
            update_values.append(is_active)

        if hire_date is not None:
            update_fields.append("hire_date = %s")
            update_values.append(hire_date_obj)

        # Skills and experience fields
        if primary_skills is not None:
            update_fields.append("primary_skills = %s")
            update_values.append(json.dumps(primary_skills))

        if secondary_skills is not None:
            update_fields.append("secondary_skills = %s")
            update_values.append(json.dumps(secondary_skills))

        if trade_categories is not None:
            update_fields.append("trade_categories = %s")
            update_values.append(json.dumps(trade_categories))

        if experience_years is not None:
            update_fields.append("experience_years = %s")
            update_values.append(experience_years)

        if skill_levels is not None:
            update_fields.append("skill_levels = %s")
            update_values.append(json.dumps(skill_levels))

        if work_preferences is not None:
            update_fields.append("work_preferences = %s")
            update_values.append(json.dumps(work_preferences))

        if equipment_mastery is not None:
            update_fields.append("equipment_mastery = %s")
            update_values.append(json.dumps(equipment_mastery))

        if project_experience is not None:
            update_fields.append("project_experience = %s")
            update_values.append(json.dumps(project_experience))

        # Certifications and training fields
        if certifications is not None:
            update_fields.append("certifications = %s")
            update_values.append(json.dumps(certifications))

        if safety_training is not None:
            update_fields.append("safety_training = %s")
            update_values.append(json.dumps(safety_training))

        if last_training_date is not None:
            update_fields.append("last_training_date = %s")
            update_values.append(last_training_date_obj)


        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())

            update_values.append(user_id)

            update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)
            db.commit()
            
            # 🔄 Synchronisation automatique des vecteurs
            try:
                from ...vector_sync import auto_sync_user_vector
                # Récupérer les données mises à jour pour la synchronisation vectorielle
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                updated_user_row = cursor.fetchone()
                if updated_user_row:
                    columns = [desc[0] for desc in cursor.description]
                    updated_user_data = dict(zip(columns, updated_user_row))
                    auto_sync_user_vector(user_id, updated_user_data, "update")
            except Exception as sync_error:
                print(f"⚠️  Synchronisation vectorielle échouée pour utilisateur {user_id}: {sync_error}")

            cursor.execute(
                """
                SELECT id, first_name, last_name, email, password_hash, phone, address,
                       role, role_description, is_active, hire_date,
                       primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
                       work_preferences, equipment_mastery, project_experience,
                       certifications, safety_training, last_training_date,
                       created_at, updated_at
                FROM users WHERE id = %s
            """,
                (user_id,),
            )

            result = cursor.fetchone()
            if result:
                columns = [desc[0] for desc in cursor.description]
                user_dict = {}
                for i, value in enumerate(result):
                    column_name = columns[i]
                    if isinstance(value, datetime):
                        user_dict[column_name] = value.isoformat()
                    elif isinstance(value, Decimal):
                        user_dict[column_name] = float(value)
                    elif column_name in [
                        "primary_skills",
                        "secondary_skills", 
                        "trade_categories",
                        "work_preferences",
                        "equipment_mastery",
                        "project_experience",
                        "certifications",
                        "safety_training"
                    ]:
                        # Parse JSON list fields
                        try:
                            if value and isinstance(value, str):
                                user_dict[column_name] = json.loads(value)
                            else:
                                user_dict[column_name] = []
                        except (json.JSONDecodeError, TypeError):
                            user_dict[column_name] = []
                    elif column_name == "skill_levels":
                        # Parse JSON object field
                        try:
                            if value and isinstance(value, str):
                                user_dict[column_name] = json.loads(value)
                            else:
                                user_dict[column_name] = {}
                        except (json.JSONDecodeError, TypeError):
                            user_dict[column_name] = {}
                    elif isinstance(value, date):
                        user_dict[column_name] = value.isoformat()
                    else:
                        user_dict[column_name] = value

                success_result = {
                    "success": True,
                    "message": f"✅ User ID {user_id} modified successfully.",
                    "user": user_dict,
                    "fields_updated": len(update_fields) - 1,  # -1 to not count updated_at
                }
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                return "❌ Error: User modified but unable to retrieve it."
        else:
            return "❌ Error: No valid fields to update."

    except Exception as e:
        db.rollback()
        return f"❌ Erreur base de données: {str(e)}"
    finally:
        cursor.close()
