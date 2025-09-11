from mcp_init import mcp, get_db_connection
from typing import List, Dict, Any
import json


@mcp.tool()
def create_notification(
    title: str,
    what_you_need_to_know: str,
    what_we_can_trigger: str,
    action_list: List[Dict[str, Any]],
    is_triggered: bool = False,
    is_readed: bool = False,
) -> str:
    """
    NOTIFICATION CREATION TOOL - Create New Notifications
    Creates new notifications in the system to inform users about important events,
    updates, or actions that need to be taken.

    REQUIRED PARAMETERS:
    - title: Notification title (string, not empty)
    - what_you_need_to_know: Important information content (string, not empty)
    - what_we_can_trigger: Description of what actions can be triggered (string, not empty)
    - action_list: List of action objects (List[Dict], required)
      Each action object must have:
      * "action": Action name to execute (string, required, e.g., 'update_task')
      * "parameters": Parameters for the action (dict, required)

    OPTIONAL PARAMETERS:
    - is_triggered: Whether the notification has been triggered (boolean, default: False)
    - is_readed: Whether the notification has been read (boolean, default: False)

    USAGE EXAMPLES:
    Simple notification with no actions
    create_notification(
        "New Task Assignment",
        "You have been assigned to Project Alpha",
        "You can accept or decline this assignment",
        []
    )

    # Notification with actions
    create_notification(
        "Budget Approval Required",
        "Project budget exceeds threshold and requires approval",
        "Approve or reject the budget proposal",
        [
            {
                "action": "update_task",
                "parameters": {"task_id": 123, "status": "approved"}
            },
            {
                "action": "update_task",
                "parameters": {"task_id": 123, "status": "rejected"}
            },
            {
                "action": "request_budget_revision",
                "parameters": {"task_id": 123, "reason": "needs_clarification"}
            }
        ]
    )

    # Pre-triggered notification
    create_notification(
        "System Maintenance",
        "Scheduled maintenance will occur tonight",
        "No action required from users",
        [],
        is_triggered=True
    )

    RETURN:
    JSON with the created notification's information or an error message.
    """

    # Basic validation
    if not title or not title.strip():
        return "❌ Error: Title is required and cannot be empty."

    if not what_you_need_to_know or not what_you_need_to_know.strip():
        return (
            "❌ Error: 'What you need to know' content is required and cannot be empty."
        )

    if not what_we_can_trigger or not what_we_can_trigger.strip():
        return "❌ Error: 'What we can trigger' description is required and cannot be empty."

    # Validate action_list structure
    if not isinstance(action_list, list):
        return "❌ Error: action_list must be a list."

    for i, action in enumerate(action_list):
        if not isinstance(action, dict):
            return f"❌ Error: action_list[{i}] must be a dictionary."

        required_fields = ["action", "parameters"]
        for field in required_fields:
            if field not in action:
                return f"❌ Error: action_list[{i}] missing required field '{field}'."

        if not isinstance(action["action"], str) or not action["action"].strip():
            return f"❌ Error: action_list[{i}]['action'] must be a non-empty string."

        if not isinstance(action["parameters"], dict):
            return f"❌ Error: action_list[{i}]['parameters'] must be a dictionary."

    # Clean and prepare data
    title = title.strip()
    what_you_need_to_know = what_you_need_to_know.strip()
    what_we_can_trigger = what_we_can_trigger.strip()

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"

    cursor = db.cursor(buffered=True)
    try:
        insert_query = """
        INSERT INTO notifications (
            title, what_you_need_to_know, what_we_can_trigger, 
            is_triggered, action_list, is_readed
        ) VALUES (%s, %s, %s, %s, %s, %s)
        """

        params = (
            title,
            what_you_need_to_know,
            what_we_can_trigger,
            is_triggered,
            json.dumps(action_list),
            is_readed,
        )

        cursor.execute(insert_query, params)
        notification_id = cursor.lastrowid
        db.commit()

        # Retrieve the created notification
        cursor.execute(
            """
            SELECT id, title, what_you_need_to_know, what_we_can_trigger,
                   is_triggered, action_list, is_readed
            FROM notifications WHERE id = %s
            """,
            (notification_id,),
        )

        result = cursor.fetchone()
        if result:
            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            notification_dict = {}
            for i, value in enumerate(result):
                column_name = columns[i]
                if column_name == "action_list":
                    # Parse JSON array field
                    try:
                        if value and isinstance(value, str):
                            notification_dict[column_name] = json.loads(value)
                        else:
                            notification_dict[column_name] = []
                    except (json.JSONDecodeError, TypeError):
                        notification_dict[column_name] = []
                else:
                    notification_dict[column_name] = value

            success_result = {
                "success": True,
                "message": f"✅ Notification '{title}' created successfully.",
                "notification": notification_dict,
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Error: Notification created but unable to retrieve it."

    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()
