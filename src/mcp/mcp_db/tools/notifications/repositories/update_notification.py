from mcp_init import mcp, get_db_connection
from typing import Optional, List, Dict, Any
import json


@mcp.tool()
def update_notification(
    notification_id: int,
    title: Optional[str] = None,
    what_you_need_to_know: Optional[str] = None,
    what_we_can_trigger: Optional[str] = None,
    action_list: Optional[List[Dict[str, Any]]] = None,
    is_triggered: Optional[bool] = None,
    is_readed: Optional[bool] = None,
) -> str:
    """
    🔔 NOTIFICATION UPDATE TOOL - Update Existing Notifications
    
    Updates existing notifications in the system. Only provided parameters will be modified.
    This tool is useful for marking notifications as read, triggered, or updating their content.
    
    MANDATORY PARAMETERS:
    ====================
    notification_id: ID of the notification to modify (int, must exist in notifications table)
    
    OPTIONAL PARAMETERS (only provided parameters modified):
    ======================================================
    title: New notification title (string, non-empty if provided)
    what_you_need_to_know: New important information content (string, non-empty if provided)
    what_we_can_trigger: New description of triggerable actions (string, non-empty if provided)
    action_list: New list of action objects (List[Dict], optional)
      Each action object must have:
      * "action": Action name to execute (string, required, e.g., 'update_task')
      * "parameters": Parameters for the action (dict, required)
    is_triggered: New triggered status (boolean)
    is_readed: New read status (boolean)
    
    USAGE EXAMPLES:
    ==============
    # Mark notification as read
    update_notification(1, is_readed=True)
    
    # Trigger a notification
    update_notification(2, is_triggered=True)
    
    # Update notification content
    update_notification(
        3, 
        title="Updated: Budget Approval Required",
        what_you_need_to_know="Project budget has been revised and requires re-approval"
    )
    
    # Add new actions to a notification
    update_notification(
        4,
        action_list=[
            {
                "action": "approve_request",
                "parameters": {"request_id": 4}
            },
            {
                "action": "reject_request",
                "parameters": {"request_id": 4, "reason": "insufficient_data"}
            },
            {
                "action": "escalate_request",
                "parameters": {"request_id": 4, "level": "manager"}
            }
        ]
    )
    
    # Mark as both triggered and read
    update_notification(5, is_triggered=True, is_readed=True)
    
    RETURN:
    JSON with the updated notification's information or an error message.
    """
    
    # Basic validation
    if not isinstance(notification_id, int) or notification_id <= 0:
        return "❌ Error: notification_id must be a positive integer."
    
    # Validate non-empty strings if provided
    if title is not None and (not title or not title.strip()):
        return "❌ Error: Title cannot be empty if provided."
    
    if what_you_need_to_know is not None and (not what_you_need_to_know or not what_you_need_to_know.strip()):
        return "❌ Error: 'What you need to know' content cannot be empty if provided."
    
    if what_we_can_trigger is not None and (not what_we_can_trigger or not what_we_can_trigger.strip()):
        return "❌ Error: 'What we can trigger' description cannot be empty if provided."
    
    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"
    
    cursor = db.cursor(buffered=True)
    try:
        # Check if notification exists
        cursor.execute("SELECT id FROM notifications WHERE id = %s", (notification_id,))
        if not cursor.fetchone():
            return f"❌ Error: Notification with ID {notification_id} does not exist."
        
        # Build update query dynamically based on provided parameters
        update_fields = []
        params = []
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title.strip())
        
        if what_you_need_to_know is not None:
            update_fields.append("what_you_need_to_know = %s")
            params.append(what_you_need_to_know.strip())
        
        if what_we_can_trigger is not None:
            update_fields.append("what_we_can_trigger = %s")
            params.append(what_we_can_trigger.strip())
        
        if action_list is not None:
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
            
            update_fields.append("action_list = %s")
            params.append(json.dumps(action_list))
        
        if is_triggered is not None:
            update_fields.append("is_triggered = %s")
            params.append(is_triggered)
        
        if is_readed is not None:
            update_fields.append("is_readed = %s")
            params.append(is_readed)
        
        if not update_fields:
            return "❌ Error: No fields to update. Please provide at least one parameter to modify."
        
        # Add notification_id to params for WHERE clause
        params.append(notification_id)
        
        update_query = f"""
        UPDATE notifications 
        SET {', '.join(update_fields)}
        WHERE id = %s
        """
        
        cursor.execute(update_query, params)
        
        if cursor.rowcount == 0:
            return f"❌ Error: No changes were made to notification {notification_id}."
        
        db.commit()
        
        # Retrieve the updated notification
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
            columns = [desc[0] for desc in cursor.description]
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
                "message": f"✅ Notification {notification_id} updated successfully.",
                "notification": notification_dict,
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Error: Notification updated but unable to retrieve it."
    
    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()