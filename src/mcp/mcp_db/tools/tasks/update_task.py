from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime


@mcp.tool()
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assigned_to: Optional[int] = None,
    estimated_time: Optional[int] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[int] = None,
    status: Optional[str] = None,
    completion_percentage: Optional[int] = None,
) -> str:
    """
    Modifies an existing task in the database.

    REQUIRED PARAMETERS:
    - task_id: ID of the task to modify (int, must exist in tasks)

    OPTIONAL PARAMETERS (only provided parameters will be modified):
    - title: New task title (string, not empty if provided)
    - description: New detailed description (string, not empty if provided)
    - assigned_to: New ID of assigned user (int, must exist in users)
    - estimated_time: New estimated time in minutes (int, positive or null)
    - start_date: New start date/time (string format: "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD", null to remove)
    - due_date: New due date/time (string format: "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD", null to remove)
    - priority: New priority level (int, 1=high, 2=normal, 3=low, 4=very low, 5=critical)
    - status: New task status (string)
      OPTIONS: 'pending', 'in_progress', 'completed', 'cancelled', 'on_hold'
    - completion_percentage: New completion percentage (int 0-100)

    AUTOMATIC VALIDATIONS:
    - task_id must exist in database
    - Title and description not empty if provided
    - assigned_to must exist in users if provided
    - Dates in correct format if provided
    - Priority between 1 and 5 if provided
    - Percentage between 0 and 100 if provided
    - Automatic update of updated_at

    USAGE EXAMPLES:
    - Change title: update_task(1, title="New title")
    - Change status: update_task(1, status="in_progress", completion_percentage=50)
    - Complete modification: update_task(1, title="New title", description="New description", assigned_to=2, priority=1, status="in_progress")
    - Remove dates: update_task(1, start_date=None, due_date=None)
    - Update dates: update_task(1, start_date="2024-12-02", due_date="2024-12-03 17:00:00")

    RETURN:
    JSON with modified task information or error message.
    """

    if not isinstance(task_id, int) or task_id <= 0:
        return "❌ Error: task_id must be a valid task ID (positive integer)."

    update_params = [
        title,
        description,
        assigned_to,
        estimated_time,
        start_date,
        due_date,
        priority,
        status,
        completion_percentage,
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

        if assigned_to is not None:
            if not isinstance(assigned_to, int) or assigned_to <= 0:
                return (
                    "❌ Error: assigned_to must be a valid user ID (positive integer)."
                )

            cursor.execute("SELECT id FROM users WHERE id = %s", (assigned_to,))
            if not cursor.fetchone():
                return f"❌ Error: Assigned user (ID: {assigned_to}) does not exist."

            update_fields.append("assigned_to = %s")
            update_values.append(assigned_to)

        if estimated_time is not None:
            if not isinstance(estimated_time, int) or estimated_time <= 0:
                return "❌ Error: Estimated time must be a positive number of minutes."
            update_fields.append("estimated_time = %s")
            update_values.append(estimated_time)

        if priority is not None:
            if priority not in [1, 2, 3, 4, 5]:
                return "❌ Error: Priority must be between 1 (high) and 5 (very low)."
            update_fields.append("priority = %s")
            update_values.append(priority)

        if status is not None:
            valid_statuses = [
                "pending",
                "in_progress",
                "completed",
                "cancelled",
                "on_hold",
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

            cursor.execute(
                """
                SELECT id, title, description, estimated_time, start_date, due_date,
                       priority, status, completion_percentage, assigned_to, created_by,
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
                    if isinstance(value, datetime):
                        task_dict[columns[i]] = value.isoformat()
                    else:
                        task_dict[columns[i]] = value

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
