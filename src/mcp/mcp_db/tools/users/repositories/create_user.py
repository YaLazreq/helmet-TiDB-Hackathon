from mcp_init import mcp, get_db_connection
from typing import Optional, List
import json
from datetime import datetime, date
from decimal import Decimal
import re
import bcrypt


@mcp.tool()
def create_user(
    first_name: str,
    last_name: str,
    email: str,
    password: str,
    phone: Optional[str] = None,
    address: Optional[str] = None,
    role: str = "worker",
    is_active: bool = True,
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
    vector: Optional[str] = None,
) -> str:
    """
    🔧 ADVANCED USER CREATION TOOL - Create Users with Full Skill Profiles

    Creates comprehensive user profiles optimized for skill matching and project assignment.

    REQUIRED PARAMETERS:
    ==================
    first_name: User's first name (string, not empty)
    last_name: User's last name (string, not empty)
    email: Valid email address (string, unique in DB)
    password: Password (string, will be hashed automatically)

    OPTIONAL BASIC INFO:
    ===================
    phone: Phone number (string, e.g., "+33123456789")
    address: Work address/location (string, e.g., "15 Rue de la Paix, Paris")
    role: User role (string, default: "worker")
        OPTIONS: 'worker', 'team_leader', 'supervisor', 'site_manager'
    is_active: Active status (boolean, default: True)
    hire_date: Hire date (string, format: "YYYY-MM-DD", e.g., "2024-01-15")

    SKILLS & EXPERIENCE (for vectorization):
    =======================================
    primary_skills: Main skills (List[str], e.g., ["electrical_installation", "plumbing_repair"])
    secondary_skills: Additional skills (List[str], e.g., ["welding", "height_work"])
    trade_categories: Trade categories (List[str], e.g., ["electricity", "plumbing"])
    experience_years: Years of experience (float, e.g., 5.5)
    skill_levels: Skill ratings 1-10 (dict, e.g., {"plumbing": 8, "electricity": 6})
    work_preferences: Work preferences (List[str], e.g., ["height_work", "indoor", "teamwork"])
    equipment_mastery: Equipment skills (List[str], e.g., ["scaffolding", "drill", "multimeter"])
    project_experience: Project types (List[str], e.g., ["residential", "industrial"])

    CERTIFICATIONS & TRAINING:
    ==========================
    certifications: Certifications (List[str], e.g., ["crane_license", "electrical_permit"])
    safety_training: Safety training (List[str], e.g., ["fall_prevention", "first_aid"])
    last_training_date: Last training date (string, format: "YYYY-MM-DD")

    USAGE EXAMPLES:
    ==============
    # Simple worker
    create_user("Jean", "Dupont", "jean@email.com", "password123")

    # Experienced electrician
    create_user(
        "Marie", "Martin", "marie@email.com", "pass456",
        phone="+33123456789", role="worker", hire_date="2020-01-15",
        primary_skills=["electrical_installation", "industrial_wiring"],
        trade_categories=["electricity"], experience_years=8.0,
        skill_levels={"electrical_installation": 9, "industrial_wiring": 8},
        certifications=["electrical_permit_B1V", "high_voltage"],
        safety_training=["electrical_safety", "confined_space"]
    )
    Inactive user:
    create_user("Paul", "Bernard", "paul@email.com", "pass123", is_active=false)

    OPTIONAL:
    vector: Vector representation (string, optional for embeddings/vectorization)

    RETURN:
    JSON with the created user’s information or an error message.
    """

    # Basic validation
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

    valid_roles = ["worker", "team_leader", "supervisor", "site_manager"]
    if role not in valid_roles:
        return f"❌ Error: Invalid role '{role}'. Valid roles: {valid_roles}"

    # Date validation
    hire_date_obj = None
    if hire_date:
        try:
            hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d").date()
        except ValueError:
            return "❌ Error: Invalid hire_date format. Use 'YYYY-MM-DD'."

    last_training_date_obj = None
    if last_training_date:
        try:
            last_training_date_obj = datetime.strptime(
                last_training_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return "❌ Error: Invalid last_training_date format. Use 'YYYY-MM-DD'."

    # Experience validation
    if experience_years is not None and (experience_years < 0 or experience_years > 50):
        return "❌ Error: Experience years must be between 0 and 50."

    # Clean and prepare data
    first_name = first_name.strip()
    last_name = last_name.strip()
    email = email.strip().lower()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    phone = phone.strip() if phone else None
    address = address.strip() if address else None

    # Prepare JSON fields with defaults
    primary_skills = primary_skills or []
    secondary_skills = secondary_skills or []
    trade_categories = trade_categories or []
    skill_levels = skill_levels or {}
    work_preferences = work_preferences or []
    equipment_mastery = equipment_mastery or []
    project_experience = project_experience or []
    certifications = certifications or []
    safety_training = safety_training or []

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            return f"❌ Error: A user with email '{email}' already exists."

        current_time = datetime.now()

        insert_query = """
        INSERT INTO users (
            first_name, last_name, email, password_hash, phone, address,
            role, is_active, hire_date,
            primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
            work_preferences, equipment_mastery, project_experience,
            certifications, safety_training, last_training_date, vector,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            first_name,
            last_name,
            email,
            password_hash,
            phone,
            address,
            role,
            is_active,
            hire_date_obj,
            json.dumps(primary_skills),
            json.dumps(secondary_skills),
            json.dumps(trade_categories),
            experience_years,
            json.dumps(skill_levels),
            json.dumps(work_preferences),
            json.dumps(equipment_mastery),
            json.dumps(project_experience),
            json.dumps(certifications),
            json.dumps(safety_training),
            last_training_date_obj,
            vector,
            current_time,
            current_time,
        )

        cursor.execute(insert_query, params)
        user_id = cursor.lastrowid
        db.commit()

        cursor.execute(
            """
            SELECT id, first_name, last_name, email, password_hash, phone, address,
                   role, is_active, hire_date,
                   primary_skills, secondary_skills, trade_categories, experience_years, skill_levels,
                   work_preferences, equipment_mastery, project_experience,
                   certifications, safety_training, last_training_date, vector,
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
                    "safety_training",
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
