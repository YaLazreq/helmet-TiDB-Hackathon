from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def create_task(title: str, description: str, assigned_to: int, created_by: int, estimated_time: Optional[int] = None, start_date: Optional[str] = None, due_date: Optional[str] = None, priority: int = 2, status: str = "pending", completion_percentage: int = 0) -> str:
    """
    Creates a new task in the database.
    
    REQUIRED PARAMETERS:
    - title: Task title (string, not empty)
    - description: Detailed task description (string, not empty)
    - assigned_to: ID of the assigned user (int, must exist in users)
    - created_by: ID of the creator user (int, must exist in users)
    
    OPTIONAL PARAMETERS:
    - estimated_time: Estimated time in minutes (int, optional)
    - start_date: Start date/time (string format: "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD", optional)
    - due_date: Due date/time (string format: "YYYY-MM-DD HH:MM:SS" or "YYYY-MM-DD", optional)
    - priority: Priority level (int, 1=high, 2=normal, 3=low, default: 2)
    - status: Task status (string, default: "pending")
      OPTIONS: 'pending', 'in_progress', 'completed', 'cancelled', 'on_hold'
    - completion_percentage: Completion percentage (int 0-100, default: 0)
    
    AUTOMATIC VALIDATIONS:
    - Title and description not empty
    - assigned_to and created_by exist in users table
    - Dates in correct format
    - Priority between 1 and 5
    - Percentage between 0 and 100
    - Automatic timestamps (created_at, updated_at)
    
    USAGE EXAMPLES:
    - Simple task: create_task("Fix faucet", "Change the gasket", assigned_to=3, created_by=1)
    - Complete task: create_task("Bathroom plumbing", "Fix leak and change faucet", assigned_to=3, created_by=1, estimated_time=240, start_date="2024-12-01 14:00:00", due_date="2024-12-01 18:00:00", priority=3)
    - With status: create_task("Living room painting", "Paint walls white", assigned_to=5, created_by=2, status="in_progress", completion_percentage=25)
    
    RETURN:
    JSON with created task information or error message.
    """
    
    if not title or not title.strip():
        return "❌ Error: Title is required and cannot be empty."
    
    if not description or not description.strip():
        return "❌ Error: Description is required and cannot be empty."
    
    if not isinstance(assigned_to, int) or assigned_to <= 0:
        return "❌ Error: assigned_to must be a valid user ID (positive integer)."
    
    if not isinstance(created_by, int) or created_by <= 0:
        return "❌ Error: created_by must be a valid user ID (positive integer)."
    
    if priority not in [1, 2, 3, 4, 5]:
        return "❌ Error: Priority must be between 1 (high) and 5 (very low)."
    
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled', 'on_hold']
    if status not in valid_statuses:
        return f"❌ Error: Invalid status '{status}'. Valid statuses: {valid_statuses}"
    
    if not isinstance(completion_percentage, int) or completion_percentage < 0 or completion_percentage > 100:
        return "❌ Error: Completion percentage must be between 0 and 100."
    
    if estimated_time is not None and (not isinstance(estimated_time, int) or estimated_time <= 0):
        return "❌ Error: Estimated time must be a positive number of minutes."
    
    start_date_obj = None
    due_date_obj = None
    
    if start_date:
        try:
            if len(start_date) == 10:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            elif len(start_date) == 19:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            else:
                return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
        except ValueError:
            return "❌ Error: Invalid start_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
    
    if due_date:
        try:
            if len(due_date) == 10:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
            elif len(due_date) == 19:
                due_date_obj = datetime.strptime(due_date, "%Y-%m-%d %H:%M:%S")
            else:
                return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
        except ValueError:
            return "❌ Error: Invalid due_date format. Use 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."
    
    if start_date_obj and due_date_obj and start_date_obj >= due_date_obj:
        return "❌ Error: Start date must be before due date."
    
    title = title.strip()
    description = description.strip()
    
    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"
        
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute("SELECT id FROM users WHERE id = %s", (assigned_to,))
        if not cursor.fetchone():
            return f"❌ Error: Assigned user (ID: {assigned_to}) does not exist."
        
        cursor.execute("SELECT id FROM users WHERE id = %s", (created_by,))
        if not cursor.fetchone():
            return f"❌ Error: Creator user (ID: {created_by}) does not exist."
        
        current_time = datetime.now()
        
        insert_query = """
        INSERT INTO tasks (
            title, description, estimated_time, start_date, due_date, 
            priority, status, completion_percentage, assigned_to, created_by,
            created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        params = (
            title, description, estimated_time, start_date_obj, due_date_obj,
            priority, status, completion_percentage, assigned_to, created_by,
            current_time, current_time
        )
        
        cursor.execute(insert_query, params)
        task_id = cursor.lastrowid
        db.commit()
        
        cursor.execute("""
            SELECT id, title, description, estimated_time, start_date, due_date,
                   priority, status, completion_percentage, assigned_to, created_by,
                   created_at, updated_at
            FROM tasks WHERE id = %s
        """, (task_id,))
        
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
                "message": f"✅ Task '{title}' created successfully (ID: {task_id}).",
                "task": task_dict
            }
            return json.dumps(success_result, indent=2, ensure_ascii=False)
        else:
            return "❌ Error: Task created but unable to retrieve it."
            
    except Exception as e:
        db.rollback()
        return f"❌ Database error: {str(e)}"
    finally:
        cursor.close()
