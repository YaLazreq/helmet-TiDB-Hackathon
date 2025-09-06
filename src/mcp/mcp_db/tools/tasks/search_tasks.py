from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime

@mcp.tool()
def search_tasks(id: Optional[str] = None, title: Optional[str] = None, description: Optional[str] = None, assigned_to: Optional[str] = None, created_by: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None, start_date: Optional[str] = None, due_date: Optional[str] = None, min_estimated_hours: Optional[float] = None, max_estimated_hours: Optional[float] = None, min_completion: Optional[int] = None, max_completion: Optional[int] = None, overdue_only: Optional[bool] = None, limit: Optional[int] = 20) -> str:
    """
    Search for tasks based on various criteria.
    
    AVAILABLE PARAMETERS:
    
    IDENTIFICATION:
    - id: Unique task identifier (string)
    - title: Task title (string, partial search allowed)
    - description: Task description (string, partial search allowed)
    
    ASSIGNMENT:
    - assigned_to: ID or name of assigned user (string)
    - created_by: ID or name of creator user (string)
    
    PRIORITY:
    - priority: Priority level (1=Low, 2=Medium, 3=High)
    
    STATUS:
    - status: Task progress status (string)
      EXAMPLES: 'pending', 'in_progress', 'completed', 'cancelled'
    
    DATES:
    - start_date: Start date (format: 'YYYY-MM-DD')
    - due_date: Due date (format: 'YYYY-MM-DD')
    - overdue_only: Only overdue tasks (boolean: true/false)
    
    ESTIMATION & PROGRESS:
    - min_estimated_hours: Minimum estimated duration (hours, calculated from estimated_time in minutes)
    - max_estimated_hours: Maximum estimated duration (hours, calculated from estimated_time in minutes)
    - min_completion: Minimum completion percentage (0-100)
    - max_completion: Maximum completion percentage (0-100)
    
    OTHER:
    - limit: Maximum number of results (default: 20)
    
    USAGE EXAMPLES:
    - User tasks: search_tasks(assigned_to="1")
    - High priority tasks: search_tasks(priority="3")
    - Tasks in progress: search_tasks(status="in_progress")
    - Overdue tasks: search_tasks(overdue_only=true)
    - Nearly finished tasks: search_tasks(min_completion=80)
    - Big tasks: search_tasks(min_estimated_hours=10)
    - Search by title: search_tasks(title="repair")
    
    RETURN:
    JSON with list of found tasks and their complete information.
    """
    
    if min_completion is not None and (min_completion < 0 or min_completion > 100):
        return f"Error: min_completion must be between 0 and 100, received: {min_completion}"
        
    if max_completion is not None and (max_completion < 0 or max_completion > 100):
        return f"Error: max_completion must be between 0 and 100, received: {max_completion}"
    
    conditions = []
    params = []
    
    if id:
        conditions.append("t.id = %s")
        params.append(id)
        
    if title:
        conditions.append("t.title LIKE %s")
        params.append(f"%{title}%")
        
    if description:
        conditions.append("t.description LIKE %s")
        params.append(f"%{description}%")
        
    if assigned_to:
        conditions.append("(CONCAT(u_assigned.first_name, ' ', u_assigned.last_name) LIKE %s OR t.assigned_to = %s)")
        params.extend([f"%{assigned_to}%", assigned_to])
        
    if created_by:
        conditions.append("(CONCAT(u_creator.first_name, ' ', u_creator.last_name) LIKE %s OR t.created_by = %s)")
        params.extend([f"%{created_by}%", created_by])
        
    if priority:
        conditions.append("t.priority = %s")
        params.append(priority)
        
    if status:
        conditions.append("t.status = %s")
        params.append(status)
        
    if start_date:
        conditions.append("DATE(t.start_date) = %s")
        params.append(start_date)
        
    if due_date:
        conditions.append("DATE(t.due_date) = %s")
        params.append(due_date)
        
    if min_estimated_hours is not None:
        conditions.append("t.estimated_time >= %s")
        params.append(min_estimated_hours * 60)  # Convert hours to minutes
        
    if max_estimated_hours is not None:
        conditions.append("t.estimated_time <= %s")
        params.append(max_estimated_hours * 60)  # Convert hours to minutes
        
    if min_completion is not None:
        conditions.append("t.completion_percentage >= %s")
        params.append(min_completion)
        
    if max_completion is not None:
        conditions.append("t.completion_percentage <= %s")
        params.append(max_completion)
        
    if overdue_only:
        conditions.append("t.due_date < NOW() AND t.status NOT IN ('completed', 'cancelled')")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    query = f"""
    SELECT 
        t.id,
        t.title,
        t.description,
        t.estimated_time,
        t.start_date,
        t.due_date,
        t.priority,
        t.status,
        t.completion_percentage,
        t.assigned_to,
        CONCAT(u_assigned.first_name, ' ', u_assigned.last_name) as assigned_to_name,
        u_assigned.email as assigned_to_email,
        t.created_by,
        CONCAT(u_creator.first_name, ' ', u_creator.last_name) as created_by_name,
        u_creator.email as created_by_email,
        t.created_at,
        t.updated_at
    FROM tasks t
    LEFT JOIN users u_assigned ON t.assigned_to = u_assigned.id
    LEFT JOIN users u_creator ON t.created_by = u_creator.id
    WHERE {where_clause}
    ORDER BY 
        CASE 
            WHEN t.priority = 3 THEN 1  -- High priority
            WHEN t.priority = 2 THEN 2  -- Medium priority
            WHEN t.priority = 1 THEN 3  -- Low priority
            ELSE 4
        END,
        t.due_date ASC,
        t.created_at DESC
    LIMIT {limit or 20}
    """

    db = get_db_connection()
    if not db:
        return "❌ Database connection failed"
        
    cursor = db.cursor(buffered=True)
    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        # Convert to dictionaries with datetime handling
        tasks_list = []
        for row in results:
            task_dict = {}
            for i, value in enumerate(row):
                if isinstance(value, datetime):
                    task_dict[columns[i]] = value.isoformat()
                else:
                    task_dict[columns[i]] = value
            
            # Calculate estimated hours from minutes
            if 'estimated_time' in task_dict and task_dict['estimated_time']:
                task_dict['estimated_hours'] = round(task_dict['estimated_time'] / 60, 2)
            else:
                task_dict['estimated_hours'] = 0
                
            tasks_list.append(task_dict)
        
    except Exception as e:
        return f"Database error: {str(e)}"
    finally:
        cursor.close()
    
    if not tasks_list:
        return "❌ No tasks found with these criteria."
    
    # Statistics calculations
    total_estimated_hours = sum(task.get("estimated_hours", 0) for task in tasks_list)
    avg_completion = sum(task.get("completion_percentage", 0) for task in tasks_list) / len(tasks_list)
    
    status_count = {}
    for task in tasks_list:
        status = task.get("status", "unknown")
        status_count[status] = status_count.get(status, 0) + 1
    
    result = {
        "summary": {
            "total_found": len(tasks_list),
            "total_estimated_hours": round(total_estimated_hours, 2),
            "average_completion": round(avg_completion, 1),
            "status_breakdown": status_count
        },
        "criteria_used": {k: v for k, v in {
            "id": id, "title": title, "description": description,
            "assigned_to": assigned_to, "created_by": created_by,
            "priority": priority, "status": status,
            "start_date": start_date, "due_date": due_date,
            "min_estimated_hours": min_estimated_hours,
            "max_estimated_hours": max_estimated_hours,
            "min_completion": min_completion, "max_completion": max_completion,
            "overdue_only": overdue_only
        }.items() if v is not None},
        "tasks": tasks_list
    }
    
    return json.dumps(result, indent=2, ensure_ascii=False)