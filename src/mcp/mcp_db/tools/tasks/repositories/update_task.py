from mcp_init import mcp, get_db_connection
from typing import Optional, List, Union
import json
from datetime import datetime
from decimal import Decimal
from ...backend_notifier import notify_db_update


@mcp.tool()
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    room: Optional[str] = None,
    floor: Optional[int] = None,
    building_section: Optional[str] = None,
    zone_type: Optional[str] = None,
    assigned_workers: Optional[List[Union[str, int]]] = None,
    required_worker_count: Optional[int] = None,
    skill_requirements: Optional[List[str]] = None,
    trade_category: Optional[str] = None,
    supervisor_id: Optional[Union[str, int]] = None,
    priority: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    min_estimated_hours: Optional[float] = None,
    max_estimated_hours: Optional[float] = None,
    actual_hours: Optional[float] = None,
    completion_percentage: Optional[int] = None,
    dependencies: Optional[List[str]] = None,
    blocks_tasks: Optional[List[str]] = None,
    required_materials: Optional[List[dict]] = None,
    required_equipment: Optional[List[str]] = None,
    weather_dependent: Optional[bool] = None,
    noise_level: Optional[str] = None,
    safety_requirements: Optional[List[str]] = None,
    notes: Optional[str] = None,
) -> str:
    """
    Modifies an existing task in the database with comprehensive field support.

    REQUIRED PARAMETERS:
    - task_id: ID of the task to modify (int, must exist in tasks)

    OPTIONAL PARAMETERS (only provided parameters will be modified):

    BASIC INFO:
    - title: New task title (string, not empty if provided)
    - description: New detailed description (string, not empty if provided)
    - notes: New additional comments (string)

    LOCATION:
    - room: New room location (string, e.g., "B200", "A101")
    - floor: New floor number (int)
    - building_section: New building section (string, e.g., "Aile A")
    - zone_type: New zone type (string, e.g., "bureau", "sanitaire")

    ASSIGNMENT:
    - assigned_workers: New list of worker IDs (List[str])
    - required_worker_count: New minimum worker count (int, positive)
    - skill_requirements: New required skills (List[str])
    - trade_category: New trade category (string)
    - supervisor_id: New supervisor ID (string)

    PRIORITY & STATUS:
    - priority: New priority level (int, 0=low, 1=normal, 2=high, 3=critical)
    - status: New task status (string: 'pending', 'in_progress', 'completed', 'blocked')

    SCHEDULING:
    - start_date: New start date (string format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
    - due_date: New due date (string format: "YYYY-MM-DD" or "YYYY-MM-DD HH:MM:SS")
    - min_estimated_hours: New lower time estimate (float, non-negative)
    - max_estimated_hours: New upper time estimate (float, non-negative)
    - actual_hours: New actual time spent (float, non-negative)
    - completion_percentage: New progress percentage (int, 0-100)

    DEPENDENCIES:
    - dependencies: New list of prerequisite task IDs (List[str])
    - blocks_tasks: New list of task IDs this task blocks (List[str])

    RESOURCES:
    - required_materials: New materials needed (List[dict])
    - required_equipment: New equipment needed (List[str])

    CONDITIONS:
    - weather_dependent: New weather dependency (bool)
    - noise_level: New noise level (string: "low", "medium", "high")
    - safety_requirements: New safety requirements (List[str])

    AUTOMATIC VALIDATIONS:
    - task_id must exist in database
    - All field validations as in create_task
    - Automatic update of updated_at timestamp

    RETURN:
    JSON with modified task information or error message.
    """

    if not isinstance(task_id, int) or task_id <= 0:
        return "❌ Error: task_id must be a valid task ID (positive integer)."

    update_params = [
        title,
        description,
        room,
        floor,
        building_section,
        zone_type,
        assigned_workers,
        required_worker_count,
        skill_requirements,
        trade_category,
        supervisor_id,
        priority,
        status,
        start_date,
        due_date,
        min_estimated_hours,
        max_estimated_hours,
        actual_hours,
        completion_percentage,
        dependencies,
        blocks_tasks,
        required_materials,
        required_equipment,
        weather_dependent,
        noise_level,
        safety_requirements,
        notes,
    ]
    if all(param is None for param in update_params):
        return "❌ Error: At least one parameter to modify must be provided."

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        if not cursor.fetchone():
            return f"❌ Error: Task with ID {task_id} does not exist."

        update_fields = []
        update_values = []

        if title is not None:
            if not title or not title.strip():
                return "❌ Error: Title cannot be empty."
            update_fields.append("title = %s")
            update_values.append(title.strip())

        if description is not None:
            if not description or not description.strip():
                return "❌ Error: Description cannot be empty."
            update_fields.append("description = %s")
            update_values.append(description.strip())

        # Location fields
        if room is not None:
            if not room or not room.strip():
                return "❌ Error: Room cannot be empty."
            update_fields.append("room = %s")
            update_values.append(room.strip())

        if floor is not None:
            if not isinstance(floor, int):
                return "❌ Error: Floor must be an integer."
            update_fields.append("floor = %s")
            update_values.append(floor)

        if building_section is not None:
            if not building_section or not building_section.strip():
                return "❌ Error: Building section cannot be empty."
            update_fields.append("building_section = %s")
            update_values.append(building_section.strip())

        if zone_type is not None:
            if not zone_type or not zone_type.strip():
                return "❌ Error: Zone type cannot be empty."
            update_fields.append("zone_type = %s")
            update_values.append(zone_type.strip())

        # Assignment fields
        if assigned_workers is not None:
            if not isinstance(assigned_workers, list):
                return "❌ Error: Assigned workers must be a list."
            update_fields.append("assigned_workers = %s")
            update_values.append(json.dumps(assigned_workers))

        if required_worker_count is not None:
            if not isinstance(required_worker_count, int) or required_worker_count <= 0:
                return "❌ Error: Required worker count must be a positive integer."
            update_fields.append("required_worker_count = %s")
            update_values.append(required_worker_count)

        if skill_requirements is not None:
            if not isinstance(skill_requirements, list):
                return "❌ Error: Skill requirements must be a list."
            update_fields.append("skill_requirements = %s")
            update_values.append(json.dumps(skill_requirements))

        if trade_category is not None:
            if not trade_category or not trade_category.strip():
                return "❌ Error: Trade category cannot be empty."
            update_fields.append("trade_category = %s")
            update_values.append(trade_category.strip())

        if supervisor_id is not None:
            if not supervisor_id:
                return "❌ Error: Supervisor ID cannot be empty."
            # Convert to integer if string
            if isinstance(supervisor_id, str) and supervisor_id.strip().isdigit():
                supervisor_id = int(supervisor_id.strip())
            update_fields.append("supervisor_id = %s")
            update_values.append(supervisor_id)

        # Estimation and hours fields
        if min_estimated_hours is not None:
            if (
                not isinstance(min_estimated_hours, (int, float))
                or min_estimated_hours < 0
            ):
                return "❌ Error: Min estimated hours must be a non-negative number."
            update_fields.append("min_estimated_hours = %s")
            update_values.append(min_estimated_hours)

        if max_estimated_hours is not None:
            if (
                not isinstance(max_estimated_hours, (int, float))
                or max_estimated_hours < 0
            ):
                return "❌ Error: Max estimated hours must be a non-negative number."
            update_fields.append("max_estimated_hours = %s")
            update_values.append(max_estimated_hours)

        if actual_hours is not None:
            if not isinstance(actual_hours, (int, float)) or actual_hours < 0:
                return "❌ Error: Actual hours must be a non-negative number."
            update_fields.append("actual_hours = %s")
            update_values.append(actual_hours)

        # Dependencies and resources
        if dependencies is not None:
            if not isinstance(dependencies, list):
                return "❌ Error: Dependencies must be a list."
            update_fields.append("dependencies = %s")
            update_values.append(json.dumps(dependencies))

        if blocks_tasks is not None:
            if not isinstance(blocks_tasks, list):
                return "❌ Error: Blocks tasks must be a list."
            update_fields.append("blocks_tasks = %s")
            update_values.append(json.dumps(blocks_tasks))

        if required_materials is not None:
            if not isinstance(required_materials, list):
                return "❌ Error: Required materials must be a list."
            update_fields.append("required_materials = %s")
            update_values.append(json.dumps(required_materials))

        if required_equipment is not None:
            if not isinstance(required_equipment, list):
                return "❌ Error: Required equipment must be a list."
            update_fields.append("required_equipment = %s")
            update_values.append(json.dumps(required_equipment))

        if weather_dependent is not None:
            if not isinstance(weather_dependent, bool):
                return "❌ Error: Weather dependent must be a boolean value."
            update_fields.append("weather_dependent = %s")
            update_values.append(weather_dependent)

        if noise_level is not None:
            valid_noise_levels = ["low", "medium", "high"]
            if noise_level not in valid_noise_levels:
                return f"❌ Error: Invalid noise level '{noise_level}'. Valid levels: {valid_noise_levels}"
            update_fields.append("noise_level = %s")
            update_values.append(noise_level)

        if safety_requirements is not None:
            if not isinstance(safety_requirements, list):
                return "❌ Error: Safety requirements must be a list."
            update_fields.append("safety_requirements = %s")
            update_values.append(json.dumps(safety_requirements))

        if notes is not None:
            if not notes or not notes.strip():
                return "❌ Error: Notes cannot be empty."
            update_fields.append("notes = %s")
            update_values.append(notes.strip())


        if priority is not None:
            if priority not in [0, 1, 2, 3]:
                return "❌ Error: Priority must be 0 (low), 1 (normal), 2 (high), or 3 (critical)."
            update_fields.append("priority = %s")
            update_values.append(priority)

        if status is not None:
            valid_statuses = [
                "pending",
                "in_progress",
                "completed",
                "blocked",
            ]
            if status not in valid_statuses:
                return f"❌ Error: Invalid status '{status}'. Valid statuses: {valid_statuses}"
            update_fields.append("status = %s")
            update_values.append(status)

        if completion_percentage is not None:
            if (
                not isinstance(completion_percentage, int)
                or completion_percentage < 0
                or completion_percentage > 100
            ):
                return "❌ Error: Completion percentage must be between 0 and 100."
            update_fields.append("completion_percentage = %s")
            update_values.append(completion_percentage)

        if start_date is not None:
            if start_date == "":
                start_date = None

            if start_date is None:
                update_fields.append("start_date = %s")
                update_values.append(None)
            else:
                try:
                    if len(start_date) == 10:
                        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    elif len(start_date) == 19:
                        start_date_obj = datetime.strptime(
                            start_date, "%Y-%m-%d %H:%M:%S"
                        )
                    else:
                        return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
                    update_fields.append("start_date = %s")
                    update_values.append(start_date_obj)
                except ValueError:
                    return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

        if due_date is not None:
            if due_date == "":
                due_date = None

            if due_date is None:
                update_fields.append("due_date = %s")
                update_values.append(None)
            else:
                try:
                    if len(due_date) == 10:
                        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
                    elif len(due_date) == 19:
                        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
                    else:
                        return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
                    update_fields.append("due_date = %s")
                    update_values.append(due_date_obj)
                except ValueError:
                    return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

        if start_date is not None and due_date is not None and start_date and due_date:
            current_start = None
            current_due = None

            if start_date is None:
                cursor.execute("SELECT start_date FROM tasks WHERE id = %s", (task_id,))
                result = cursor.fetchone()
                current_start = result[0] if result else None

            if due_date is None:
                cursor.execute("SELECT due_date FROM tasks WHERE id = %s", (task_id,))
                result = cursor.fetchone()
                current_due = result[0] if result else None

            check_start = (
                start_date_obj if "start_date_obj" in locals() else current_start
            )
            check_due = due_date_obj if "due_date_obj" in locals() else current_due

            if check_start and check_due and check_start >= check_due:
                return "❌ Error: Start date must be before due date."

        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())

            update_values.append(task_id)

            update_query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
            cursor.execute(update_query, update_values)
            db.commit()
            
            # 🔄 Synchronisation automatique des vecteurs
            try:
                from ..vector_sync import auto_sync_task_vector
                # Récupérer les données mises à jour pour la synchronisation vectorielle
                cursor.execute(
                    "SELECT * FROM tasks WHERE id = %s", (task_id,)
                )
                updated_task_row = cursor.fetchone()
                if updated_task_row:
                    columns = [desc[0] for desc in cursor.description]
                    updated_task_data = dict(zip(columns, updated_task_row))
                    auto_sync_task_vector(task_id, updated_task_data, "update")
            except Exception as sync_error:
                print(f"⚠️  Synchronisation vectorielle échouée pour tâche {task_id}: {sync_error}")

            cursor.execute(
                """
                SELECT id, title, description, room, floor, building_section, zone_type,
                       assigned_workers, required_worker_count, skill_requirements, trade_category,
                       created_by, supervisor_id, priority, status, start_date, due_date,
                       min_estimated_hours, max_estimated_hours, actual_hours, completion_percentage,
                       dependencies, blocks_tasks, required_materials, required_equipment,
                       weather_dependent, noise_level, safety_requirements, notes,
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

                # Notify backend about task update
                try:
                    notify_db_update("task")
                except Exception as notify_error:
                    print(f"Warning: Backend notification failed: {notify_error}")
                
                success_result = {
                    "success": True,
                    "message": f"✅ Task ID {task_id} modified successfully.",
                    "task": task_dict,
                    "fields_updated": len(update_fields)
                    - 1,  # -1 to not count updated_at
                }
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                return "❌ Error: Task modified but unable to retrieve it."
        else:
            return "❌ Error: No valid fields to update."

    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()
