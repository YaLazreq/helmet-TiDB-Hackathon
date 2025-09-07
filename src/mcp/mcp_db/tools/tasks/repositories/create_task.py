from mcp_init import mcp, get_db_connection
from typing import List, Optional
import json
from datetime import datetime
from decimal import Decimal


@mcp.tool()
def create_task(
    title: str,
    description: str,
    room: str,
    floor: int,
    building_section: str,
    zone_type: str,
    assigned_workers: List[str],
    required_worker_count: int,
    skill_requirements: List[str],
    trade_category: str,
    created_by: str,
    supervisor_id: str,
    priority: int,
    status: str,
    start_date: str,
    due_date: str,
    min_estimated_hours: float,
    max_estimated_hours: float,
    actual_hours: float,
    completion_percentage: int,
    dependencies: List[str],
    blocks_tasks: List[str],
    required_materials: List[dict],
    required_equipment: List[str],
    weather_dependent: bool,
    noise_level: str,
    safety_requirements: List[str],
    notes: str,
    vector: Optional[str] = None,
) -> str:
    """
    Creates a new task in the database with comprehensive field requirements.

    ALL PARAMETERS ARE MANDATORY:

    BASIC INFO:
    - title: Task title (string, not empty)
    - description: Detailed task description (string, not empty)
    - notes: Additional comments (string)

    LOCATION:
    - room: Room location (string, e.g., "B200", "A101", "Ext-Nord")
    - floor: Floor number for navigation (int)
    - building_section: Building section (string, e.g., "Aile A", "Bloc B")
    - zone_type: Zone type (string, e.g., "bureau", "sanitaire", "technique", "circulation")

    ASSIGNMENT:
    - assigned_workers: List of worker IDs assigned (List[str])
    - required_worker_count: Minimum number of workers required (int)
    - skill_requirements: Required skills (List[str], e.g., ["plombier", "électricien"])
    - trade_category: Main trade category (string, e.g., "électricité", "plomberie", "peinture")
    - created_by: Creator ID (string)
    - supervisor_id: Supervisor ID (string)

    PRIORITY & STATUS:
    - priority: Urgency level (int, 0=low, 1=normal, 2=high, 3=critical)
    - status: Current status (string, "pending", "in_progress", "completed", "blocked")

    SCHEDULING:
    - start_date: Planned start date (string, format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
    - due_date: Due date (string, format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
    - min_estimated_hours: Lower time estimate (float)
    - max_estimated_hours: Upper time estimate (float)
    - actual_hours: Actual time spent (float, 0.0 for new tasks)
    - completion_percentage: Progress percentage (int, 0-100)

    DEPENDENCIES:
    - dependencies: List of prerequisite task IDs (List[str])
    - blocks_tasks: List of task IDs this task blocks (List[str])

    RESOURCES:
    - required_materials: Materials needed with quantities (List[dict])
    - required_equipment: Equipment needed (List[str], e.g., ["échafaudage", "grue"])

    CONDITIONS:
    - weather_dependent: Whether task depends on weather (bool)
    - noise_level: Noise level (string, "low", "medium", "high")
    - safety_requirements: Safety requirements (List[str])

    OPTIONAL:
    - vector: Vector representation (string, optional for embeddings/vectorization)

    RETURN:
    JSON with created task information or error message.
    """

    # Validate mandatory string fields
    if not title or not title.strip():
        return "❌ Error: Title is required and cannot be empty."
    if not description or not description.strip():
        return "❌ Error: Description is required and cannot be empty."
    if not room or not room.strip():
        return "❌ Error: Room is required and cannot be empty."
    if not building_section or not building_section.strip():
        return "❌ Error: Building section is required and cannot be empty."
    if not zone_type or not zone_type.strip():
        return "❌ Error: Zone type is required and cannot be empty."
    if not trade_category or not trade_category.strip():
        return "❌ Error: Trade category is required and cannot be empty."
    if not created_by or not created_by.strip():
        return "❌ Error: Created by is required and cannot be empty."
    if not supervisor_id or not supervisor_id.strip():
        return "❌ Error: Supervisor ID is required and cannot be empty."
    if not notes or not notes.strip():
        return "❌ Error: Notes are required and cannot be empty."

    # Validate integer fields
    if not isinstance(floor, int):
        return "❌ Error: Floor must be an integer."
    if not isinstance(required_worker_count, int) or required_worker_count <= 0:
        return "❌ Error: Required worker count must be a positive integer."
    if not isinstance(priority, int) or priority not in [0, 1, 2, 3]:
        return (
            "❌ Error: Priority must be 0 (low), 1 (normal), 2 (high), or 3 (critical)."
        )
    if (
        not isinstance(completion_percentage, int)
        or completion_percentage < 0
        or completion_percentage > 100
    ):
        return "❌ Error: Completion percentage must be between 0 and 100."

    # Validate float fields
    if not isinstance(min_estimated_hours, (int, float)) or min_estimated_hours < 0:
        return "❌ Error: Min estimated hours must be a non-negative number."
    if not isinstance(max_estimated_hours, (int, float)) or max_estimated_hours < 0:
        return "❌ Error: Max estimated hours must be a non-negative number."
    if not isinstance(actual_hours, (int, float)) or actual_hours < 0:
        return "❌ Error: Actual hours must be a non-negative number."
    if min_estimated_hours > max_estimated_hours:
        return (
            "❌ Error: Min estimated hours cannot be greater than max estimated hours."
        )

    # Validate boolean fields
    if not isinstance(weather_dependent, bool):
        return "❌ Error: Weather dependent must be a boolean value."

    # Validate list fields
    if not isinstance(assigned_workers, list) or len(assigned_workers) == 0:
        return "❌ Error: Assigned workers must be a non-empty list."
    if not isinstance(skill_requirements, list):
        return "❌ Error: Skill requirements must be a list."
    if not isinstance(dependencies, list):
        return "❌ Error: Dependencies must be a list."
    if not isinstance(blocks_tasks, list):
        return "❌ Error: Blocks tasks must be a list."
    if not isinstance(required_materials, list):
        return "❌ Error: Required materials must be a list."
    if not isinstance(required_equipment, list):
        return "❌ Error: Required equipment must be a list."
    if not isinstance(safety_requirements, list):
        return "❌ Error: Safety requirements must be a list."

    # Validate status
    valid_statuses = ["pending", "in_progress", "completed", "blocked"]
    if status not in valid_statuses:
        return f"❌ Error: Invalid status '{status}'. Valid statuses: {valid_statuses}"

    # Validate noise level
    valid_noise_levels = ["low", "medium", "high"]
    if noise_level not in valid_noise_levels:
        return f"❌ Error: Invalid noise level '{noise_level}'. Valid levels: {valid_noise_levels}"

    # Validate and parse dates (mandatory)
    try:
        if len(start_date) == 10:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        elif len(start_date) == 19:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
        else:
            return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
    except ValueError:
        return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

    try:
        if len(due_date) == 10:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
        elif len(due_date) == 19:
            due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
        else:
            return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
    except ValueError:
        return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

    if start_date_obj >= due_date_obj:
        return "❌ Error: Start date must be before due date."

    # Clean string inputs
    title = title.strip()
    description = description.strip()
    room = room.strip()
    building_section = building_section.strip()
    zone_type = zone_type.strip()
    trade_category = trade_category.strip()
    created_by = created_by.strip()
    supervisor_id = supervisor_id.strip()
    notes = notes.strip()

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        current_time = datetime.now()

        insert_query = """
        INSERT INTO tasks (
            title, description, room, floor, building_section, zone_type,
            assigned_workers, required_worker_count, skill_requirements, trade_category,
            created_by, supervisor_id, priority, status, start_date, due_date,
            min_estimated_hours, max_estimated_hours, actual_hours, completion_percentage,
            dependencies, blocks_tasks, required_materials, required_equipment,
            weather_dependent, noise_level, safety_requirements, notes, vector,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        params = (
            title,
            description,
            room,
            floor,
            building_section,
            zone_type,
            json.dumps(assigned_workers),
            required_worker_count,
            json.dumps(skill_requirements),
            trade_category,
            created_by,
            supervisor_id,
            priority,
            status,
            start_date_obj,
            due_date_obj,
            min_estimated_hours,
            max_estimated_hours,
            actual_hours,
            completion_percentage,
            json.dumps(dependencies),
            json.dumps(blocks_tasks),
            json.dumps(required_materials),
            json.dumps(required_equipment),
            weather_dependent,
            noise_level,
            json.dumps(safety_requirements),
            notes,
            vector,
            current_time,
            current_time,
        )

        cursor.execute(insert_query, params)
        task_id = cursor.lastrowid
        db.commit()

        cursor.execute(
            """
            SELECT id, title, description, room, floor, building_section, zone_type,
                   assigned_workers, required_worker_count, skill_requirements, trade_category,
                   created_by, supervisor_id, priority, status, start_date, due_date,
                   min_estimated_hours, max_estimated_hours, actual_hours, completion_percentage,
                   dependencies, blocks_tasks, required_materials, required_equipment,
                   weather_dependent, noise_level, safety_requirements, notes, vector,
                   created_at, updated_at
            FROM tasks WHERE id = %s
        """,
            (task_id,),
        )

        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            task_dict = {}
            for i, value in enumerate(result):
                column_name = columns[i]
                if isinstance(value, datetime):
                    task_dict[column_name] = value.isoformat()
                elif isinstance(value, Decimal):
                    task_dict[column_name] = float(value)
                elif column_name in [
                    "assigned_workers",
                    "skill_requirements",
                    "dependencies",
                    "blocks_tasks",
                    "required_materials",
                    "required_equipment",
                    "safety_requirements",
                ]:
                    # Parse JSON fields
                    try:
                        if value and isinstance(value, str):
                            task_dict[column_name] = json.loads(value)
                        else:
                            task_dict[column_name] = []
                    except (json.JSONDecodeError, TypeError):
                        task_dict[column_name] = []
                else:
                    task_dict[column_name] = value

            success_result = {
                "success": True,
                "message": f"✅ Task '{title}' created successfully (ID: {task_id}).",
                "task": task_dict,
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Error: Task created but unable to retrieve it."

    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()
