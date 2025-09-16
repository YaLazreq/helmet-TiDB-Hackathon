from mcp_init import mcp, get_db_connection
from typing import List, Optional, Union
import json
from datetime import datetime
from decimal import Decimal
import sys
import os
import traceback
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the mcp_db directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from backend_notifier import notify_db_update


@mcp.tool()
def create_task(
    title: str,
    description: str,
    room: str,
    floor: int,
    building_section: str,
    zone_type: str,
    assigned_workers: List[Union[str, int]],
    required_worker_count: int,
    skill_requirements: List[str],
    trade_category: str,
    created_by: Union[str, int],
    supervisor_id: Union[str, int],
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
) -> str:
    """
    Creates a new task in the database with comprehensive field requirements.
    Enhanced with detailed error logging for debugging execution issues.

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

    AUTOMATIC:

    RETURN:
    JSON with created task information or error message.
    """

    # Log function entry for debugging
    logger.info(f"🚀 create_task function called with title: '{title}'")
    logger.debug(f"Function parameters: title={title}, description={description[:50]}..., room={room}, floor={floor}")

    try:
        # Validate mandatory string fields
        logger.debug("✅ Starting validation phase")
        if not title or not title.strip():
            logger.error("❌ Validation failed: Title is empty")
            return "❌ Error: Title is required and cannot be empty."
        if not description or not description.strip():
            logger.error("❌ Validation failed: Description is empty")
            return "❌ Error: Description is required and cannot be empty."
        if not room or not room.strip():
            logger.error("❌ Validation failed: Room is empty")
            return "❌ Error: Room is required and cannot be empty."
        if not building_section or not building_section.strip():
            logger.error("❌ Validation failed: Building section is empty")
            return "❌ Error: Building section is required and cannot be empty."
        if not zone_type or not zone_type.strip():
            logger.error("❌ Validation failed: Zone type is empty")
            return "❌ Error: Zone type is required and cannot be empty."
        if not trade_category or not trade_category.strip():
            logger.error("❌ Validation failed: Trade category is empty")
            return "❌ Error: Trade category is required and cannot be empty."
        if not created_by:
            logger.error("❌ Validation failed: Created by is empty")
            return "❌ Error: Created by is required and cannot be empty."
        if not supervisor_id:
            logger.error("❌ Validation failed: Supervisor ID is empty")
            return "❌ Error: Supervisor ID is required and cannot be empty."
        if not notes or not notes.strip():
            logger.error("❌ Validation failed: Notes are empty")
            return "❌ Error: Notes are required and cannot be empty."

        logger.debug("✅ String validation passed")

        # Validate integer fields
        logger.debug("🔢 Starting integer validation")
        if not isinstance(floor, int):
            logger.error(f"❌ Validation failed: Floor is not integer, got type {type(floor)}")
            return "❌ Error: Floor must be an integer."
        if not isinstance(required_worker_count, int) or required_worker_count <= 0:
            logger.error(f"❌ Validation failed: Required worker count invalid: {required_worker_count}")
            return "❌ Error: Required worker count must be a positive integer."
        if not isinstance(priority, int) or priority not in [0, 1, 2, 3]:
            logger.error(f"❌ Validation failed: Priority invalid: {priority}")
            return (
                "❌ Error: Priority must be 0 (low), 1 (normal), 2 (high), or 3 (critical)."
            )
        if (
            not isinstance(completion_percentage, int)
            or completion_percentage < 0
            or completion_percentage > 100
        ):
            logger.error(f"❌ Validation failed: Completion percentage invalid: {completion_percentage}")
            return "❌ Error: Completion percentage must be between 0 and 100."

        logger.debug("✅ Integer validation passed")

        # Validate float fields
        logger.debug("🔢 Starting float validation")
        if not isinstance(min_estimated_hours, (int, float)) or min_estimated_hours < 0:
            logger.error(f"❌ Validation failed: Min estimated hours invalid: {min_estimated_hours}")
            return "❌ Error: Min estimated hours must be a non-negative number."
        if not isinstance(max_estimated_hours, (int, float)) or max_estimated_hours < 0:
            logger.error(f"❌ Validation failed: Max estimated hours invalid: {max_estimated_hours}")
            return "❌ Error: Max estimated hours must be a non-negative number."
        if not isinstance(actual_hours, (int, float)) or actual_hours < 0:
            logger.error(f"❌ Validation failed: Actual hours invalid: {actual_hours}")
            return "❌ Error: Actual hours must be a non-negative number."
        if min_estimated_hours > max_estimated_hours:
            logger.error(f"❌ Validation failed: Min hours ({min_estimated_hours}) > Max hours ({max_estimated_hours})")
            return (
                "❌ Error: Min estimated hours cannot be greater than max estimated hours."
            )

        logger.debug("✅ Float validation passed")

        # Validate boolean fields
        logger.debug("🔘 Starting boolean validation")
        if not isinstance(weather_dependent, bool):
            logger.error(f"❌ Validation failed: Weather dependent not boolean: {type(weather_dependent)}")
            return "❌ Error: Weather dependent must be a boolean value."

        logger.debug("✅ Boolean validation passed")

        # Validate list fields
        logger.debug("📋 Starting list validation")
        if not isinstance(assigned_workers, list):
            logger.error(f"❌ Validation failed: Assigned workers not list: {type(assigned_workers)}")
            return "❌ Error: Assigned workers must be a list (can be empty for unassigned tasks)."
        if not isinstance(skill_requirements, list):
            logger.error(f"❌ Validation failed: Skill requirements not list: {type(skill_requirements)}")
            return "❌ Error: Skill requirements must be a list."
        if not isinstance(dependencies, list):
            logger.error(f"❌ Validation failed: Dependencies not list: {type(dependencies)}")
            return "❌ Error: Dependencies must be a list."
        if not isinstance(blocks_tasks, list):
            logger.error(f"❌ Validation failed: Blocks tasks not list: {type(blocks_tasks)}")
            return "❌ Error: Blocks tasks must be a list."
        if not isinstance(required_materials, list):
            logger.error(f"❌ Validation failed: Required materials not list: {type(required_materials)}")
            return "❌ Error: Required materials must be a list."
        if not isinstance(required_equipment, list):
            logger.error(f"❌ Validation failed: Required equipment not list: {type(required_equipment)}")
            return "❌ Error: Required equipment must be a list."
        if not isinstance(safety_requirements, list):
            logger.error(f"❌ Validation failed: Safety requirements not list: {type(safety_requirements)}")
            return "❌ Error: Safety requirements must be a list."

        logger.debug("✅ List validation passed")

        # Validate status
        logger.debug("📊 Starting status validation")
        valid_statuses = ["pending", "in_progress", "completed", "blocked"]
        if status not in valid_statuses:
            logger.error(f"❌ Validation failed: Invalid status '{status}'")
            return f"❌ Error: Invalid status '{status}'. Valid statuses: {valid_statuses}"

        # Validate noise level
        valid_noise_levels = ["low", "medium", "high"]
        if noise_level not in valid_noise_levels:
            logger.error(f"❌ Validation failed: Invalid noise level '{noise_level}'")
            return f"❌ Error: Invalid noise level '{noise_level}'. Valid levels: {valid_noise_levels}"

        logger.debug("✅ Status and noise level validation passed")

        # Validate and parse dates (mandatory)
        logger.debug("📅 Starting date validation")
        try:
            if len(start_date) == 10:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            elif len(start_date) == 19:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            else:
                logger.error(f"❌ Invalid start_date format: {start_date}")
                return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
        except ValueError as e:
            logger.error(f"❌ Start date parsing failed: {e}")
            return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

        try:
            if len(due_date) == 10:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            elif len(due_date) == 19:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            else:
                logger.error(f"❌ Invalid due_date format: {due_date}")
                return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
        except ValueError as e:
            logger.error(f"❌ Due date parsing failed: {e}")
            return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."

        if start_date_obj >= due_date_obj:
            logger.error(f"❌ Date validation failed: start {start_date_obj} >= due {due_date_obj}")
            return "❌ Error: Start date must be before due date."

        logger.debug("✅ Date validation passed")

        # Clean string inputs
        logger.debug("🧹 Cleaning string inputs")
        title = title.strip()
        description = description.strip()
        room = room.strip()
        building_section = building_section.strip()
        zone_type = zone_type.strip()
        trade_category = trade_category.strip()
        notes = notes.strip()

        # Convert IDs to integers - handle both string and integer inputs
        logger.debug("🔢 Converting user IDs")
        try:
            if isinstance(created_by, str):
                created_by = (
                    int(created_by.strip()) if created_by.strip().isdigit() else 1
                )  # Default to user 1 if not numeric
            if isinstance(supervisor_id, str):
                supervisor_id = (
                    int(supervisor_id.strip()) if supervisor_id.strip().isdigit() else 1
                )  # Default to user 1 if not numeric
        except ValueError as e:
            logger.error(f"❌ ID conversion failed: {e}")
            return (
                "❌ Error: created_by and supervisor_id must be valid user IDs (integers)."
            )

        logger.debug("✅ All validations passed, proceeding to database operations")

        # Database connection with detailed logging
        logger.debug("🔌 Attempting database connection")
        db = get_db_connection()
        if not db:
            logger.error("❌ Database connection failed")
            return "❌ Database connection failed"
        logger.debug("✅ Database connection established")

        cursor = db.cursor(buffered=True)
        logger.debug("✅ Database cursor created")

        try:
            # Database operations with detailed logging
            current_time = datetime.now()
            logger.debug(f"⏰ Current time set: {current_time}")

            insert_query = """
            INSERT INTO tasks (
                title, description, room, floor, building_section, zone_type,
                assigned_workers, required_worker_count, skill_requirements, trade_category,
                created_by, supervisor_id, priority, status, start_date, due_date,
                min_estimated_hours, max_estimated_hours, actual_hours, completion_percentage,
                dependencies, blocks_tasks, required_materials, required_equipment,
                weather_dependent, noise_level, safety_requirements, notes,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                current_time,
                current_time,
            )

            logger.debug("📝 Executing INSERT query")
            logger.debug(f"Query: {insert_query}")
            logger.debug(f"First 5 params: {params[:5]}")

            cursor.execute(insert_query, params)
            task_id = cursor.lastrowid
            logger.debug(f"✅ Task inserted with ID: {task_id}")

            db.commit()
            logger.debug("✅ Database transaction committed")

            # 🔄 Synchronisation automatique des vecteurs
            logger.debug("🔄 Starting vector synchronization")
            try:
                from ...vector_sync import auto_sync_task_vector
                logger.debug("✅ Vector sync module imported")

                # Récupérer les données de la nouvelle tâche pour la synchronisation vectorielle
                cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                new_task_row = cursor.fetchone()
                if new_task_row:
                    columns = [desc[0] for desc in cursor.description]
                    new_task_data = dict(zip(columns, new_task_row))
                    logger.debug(f"📋 Task data retrieved for vector sync: {list(new_task_data.keys())}")
                    auto_sync_task_vector(task_id, new_task_data, "create")
                    logger.debug("✅ Vector synchronization completed")
                else:
                    logger.warning("⚠️  No task data found for vector sync")
            except Exception as sync_error:
                error_details = traceback.format_exc()
                logger.error(f"❌ Vector synchronization failed for task {task_id}: {sync_error}")
                logger.error(f"Full traceback: {error_details}")
                print(f"⚠️  Synchronisation vectorielle échouée pour nouvelle tâche {task_id}: {sync_error}")

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

                # Notify backend about task creation
                logger.debug("📢 Notifying backend about task creation")
                try:
                    notify_db_update("task")
                    logger.debug("✅ Backend notification sent")
                except Exception as notify_error:
                    logger.error(f"❌ Backend notification failed: {notify_error}")
                    print(f"Warning: Backend notification failed: {notify_error}")

                success_result = {
                    "success": True,
                    "message": f"✅ Task '{title}' created successfully (ID: {task_id}).",
                    "task": task_dict,
                }
                logger.info(f"🎉 Task creation completed successfully: {task_id}")
                return json.dumps(success_result, indent=2, ensure_ascii=False)
            else:
                logger.error("❌ Task created but unable to retrieve it from database")
                return "❌ Error: Task created but unable to retrieve it."

        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"❌ Database error occurred: {str(e)}")
            logger.error(f"Full traceback: {error_details}")
            db.rollback()
            logger.debug("🔄 Database transaction rolled back")
            return f"❌ Database error: {str(e)}"
        finally:
            cursor.close()
            logger.debug("🔒 Database cursor closed")

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"❌ Unexpected error in create_task function: {str(e)}")
        logger.error(f"Full traceback: {error_details}")
        return f"❌ Unexpected error: {str(e)}"
