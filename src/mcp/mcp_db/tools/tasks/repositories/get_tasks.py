"""
Universal Tasks Tool for MCP Database Server
==========================================

This is the ONE-STOP tool for ALL task operations in your MCP database server.
Whether you need to list, search, filter, or analyze tasks - this tool does it all!

Author: Assistant
Date: 2025-09-06
"""

from mcp_init import mcp, get_db_connection
from typing import Optional
import json
from datetime import datetime
from decimal import Decimal


@mcp.tool()
def get_tasks(
    task_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    assigned_to: Optional[str] = None,
    created_by: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    min_estimated_hours: Optional[float] = None,
    max_estimated_hours: Optional[float] = None,
    min_completion: Optional[int] = None,
    max_completion: Optional[int] = None,
    overdue_only: Optional[bool] = None,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
) -> str:
    """
    🔍 UNIVERSAL TASK TOOL - Get, List, Search & Filter Tasks

    This is your ONE-STOP tool for ALL task operations! Whether you need to:
    - 📋 List all tasks
    - 🎯 Find a specific task by ID
    - 🔍 Search tasks by title, assignee, status, etc.
    - 📄 Get paginated results
    - 🚨 Find overdue tasks
    - 📊 Analyze task statistics

    PARAMETERS (All Optional - Mix & Match!):
    ========================================

    🆔 IDENTIFICATION:
    task_id : str - Exact task ID ("1", "42", etc.)
    title : str - Partial title search ("repair" finds "Repair elevator")
    description : str - Partial description search ("urgent" finds tasks with "urgent")

    👥 ASSIGNMENT:
    assigned_to : str - User ID who is assigned the task ("2", "1", etc.)
    created_by : str - User ID who created the task ("1", "3", etc.)

    ⭐ PRIORITY & STATUS:
    priority : str - Priority level: "1" (Low), "2" (Medium), "3" (High)
    status : str - Task status: "pending", "in_progress", "completed", "cancelled"

    📅 DATES & DEADLINES:
    start_date : str - Start date (format: "YYYY-MM-DD", e.g., "2025-09-06")
    due_date : str - Due date (format: "YYYY-MM-DD")
    overdue_only : bool - Only overdue tasks (true/false)

    ⏱️ ESTIMATION & PROGRESS:
    min_estimated_hours : float - Min duration in hours (e.g., 2.5)
    max_estimated_hours : float - Max duration in hours (e.g., 8.0)
    min_completion : int - Min completion % (0-100)
    max_completion : int - Max completion % (0-100)

    📄 PAGINATION:
    limit : int - Max results (1-1000, default: 50)
    offset : int - Skip records for pagination (default: 0)

    💡 USAGE EXAMPLES (Copy & Use!):
    ===============================

    # 📋 SIMPLE LISTING:
    get_tasks()  # First 50 tasks
    get_tasks(limit=10)  # First 10 tasks

    # 🎯 SPECIFIC TASK:
    get_tasks(task_id="7")  # Exact task by ID

    # 👥 USER TASKS:
    get_tasks(assigned_to="2")  # Tasks assigned to user ID 2
    get_tasks(assigned_to="1")  # Tasks assigned to user ID 1
    get_tasks(created_by="3")  # Tasks created by user ID 3

    # 🔍 TEXT SEARCHES:
    get_tasks(title="camera")  # Tasks with "camera" in title
    get_tasks(description="urgent")  # Tasks with "urgent" in description

    # ⭐ PRIORITY & STATUS:
    get_tasks(priority="3")  # High priority tasks
    get_tasks(status="in_progress")  # Tasks in progress
    get_tasks(status="completed")  # Completed tasks

    # 📅 DATE FILTERING:
    get_tasks(due_date="2025-09-06")  # Tasks due on specific date
    get_tasks(overdue_only=True)  # Only overdue tasks
    get_tasks(start_date="2025-09-01")  # Tasks starting on date

    # ⏱️ PROGRESS & ESTIMATION:
    get_tasks(min_completion=80)  # Nearly finished tasks (80%+)
    get_tasks(max_completion=20)  # Just started tasks (<20%)
    get_tasks(min_estimated_hours=5)  # Big tasks (5+ hours)
    get_tasks(max_estimated_hours=2)  # Quick tasks (<2 hours)

    # 📄 PAGINATION:
    get_tasks(limit=20, offset=0)   # Page 1 (first 20)
    get_tasks(limit=20, offset=20)  # Page 2 (next 20)

    # 🔥 COMPLEX COMBINATIONS:
    get_tasks(assigned_to="2", status="in_progress", priority="3")
    get_tasks(overdue_only=True, assigned_to="2", limit=10)
    get_tasks(min_completion=50, max_completion=80, status="in_progress")

    RETURN FORMAT:
    =============
    JSON object with:
    {
        "success": true/false,
        "message": "descriptive message",
        "summary": {
            "total_found": number,
            "total_estimated_hours": number,
            "average_completion": percentage,
            "status_breakdown": {"pending": 5, "completed": 3}
        },
        "query_params": {...used parameters...},
        "tasks": [
            {
                "id": "task_id",
                "title": "Task Title",
                "description": "Task description",
                "estimated_time": minutes,
                "estimated_hours": hours,
                "start_date": "2025-01-01T10:00:00",
                "due_date": "2025-01-15T17:00:00",
                "priority": 1-3,
                "status": "in_progress",
                "completion_percentage": 75,
                "assigned_to": "user_id",
                "created_by": "creator_id",
                "created_at": "2025-01-01T09:00:00",
                "updated_at": "2025-01-10T14:00:00"
            }
        ]
    }
    """

    # Parameter validation
    if limit and (limit < 1 or limit > 1000):
        return json.dumps(
            {
                "success": False,
                "error": "Parameter validation failed",
                "message": "Limit must be between 1 and 1000",
                "query_params": {
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "created_by": created_by,
                    "priority": priority,
                    "status": status,
                    "start_date": start_date,
                    "due_date": due_date,
                    "min_estimated_hours": min_estimated_hours,
                    "max_estimated_hours": max_estimated_hours,
                    "min_completion": min_completion,
                    "max_completion": max_completion,
                    "overdue_only": overdue_only,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    if offset and offset < 0:
        return json.dumps(
            {
                "success": False,
                "error": "Parameter validation failed",
                "message": "Offset must be 0 or greater",
                "query_params": {
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "created_by": created_by,
                    "priority": priority,
                    "status": status,
                    "start_date": start_date,
                    "due_date": due_date,
                    "min_estimated_hours": min_estimated_hours,
                    "max_estimated_hours": max_estimated_hours,
                    "min_completion": min_completion,
                    "max_completion": max_completion,
                    "overdue_only": overdue_only,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    # Completion percentage validation
    if min_completion is not None and (min_completion < 0 or min_completion > 100):
        return json.dumps(
            {
                "success": False,
                "error": "Invalid completion range",
                "message": f"min_completion must be between 0 and 100, received: {min_completion}",
            },
            indent=2,
        )

    if max_completion is not None and (max_completion < 0 or max_completion > 100):
        return json.dumps(
            {
                "success": False,
                "error": "Invalid completion range",
                "message": f"max_completion must be between 0 and 100, received: {max_completion}",
            },
            indent=2,
        )

    # Priority validation
    if priority and priority not in ["1", "2", "3"]:
        return json.dumps(
            {
                "success": False,
                "error": "Invalid priority",
                "message": f"Priority must be '1' (Low), '2' (Medium), or '3' (High). Received: '{priority}'",
            },
            indent=2,
        )

    # Build query conditions
    conditions = []
    params = []

    # Identification filters
    if task_id:
        conditions.append("t.id = %s")
        params.append(task_id)

    if title:
        conditions.append("t.title LIKE %s")
        params.append(f"%{title}%")

    if description:
        conditions.append("t.description LIKE %s")
        params.append(f"%{description}%")

    # Assignment filters
    if assigned_to:
        conditions.append("JSON_CONTAINS(t.assigned_workers, %s)")
        params.append(assigned_to)

    if created_by:
        conditions.append("t.created_by LIKE %s")
        params.append(f"%{created_by}%")

    # Priority & Status filters
    if priority:
        conditions.append("t.priority = %s")
        params.append(priority)

    if status:
        conditions.append("t.status = %s")
        params.append(status)

    # Date filters
    if start_date:
        conditions.append("DATE(t.start_date) = %s")
        params.append(start_date)

    if due_date:
        conditions.append("DATE(t.due_date) = %s")
        params.append(due_date)

    # Estimation and hours filters
    if min_estimated_hours is not None:
        conditions.append("t.min_estimated_hours >= %s")
        params.append(min_estimated_hours)

    if max_estimated_hours is not None:
        conditions.append("t.max_estimated_hours <= %s")
        params.append(max_estimated_hours)

    # Completion filters
    if min_completion is not None:
        conditions.append("t.completion_percentage >= %s")
        params.append(min_completion)

    if max_completion is not None:
        conditions.append("t.completion_percentage <= %s")
        params.append(max_completion)

    # Overdue filter
    if overdue_only:
        conditions.append(
            "t.due_date < NOW() AND t.status NOT IN ('completed', 'blocked')"
        )

    # Build WHERE clause
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Build complete query with intelligent sorting
    query = f"""
    SELECT 
        t.id,
        t.title,
        t.description,
        t.assigned_workers,
        t.created_by,
        t.priority,
        t.status,
        t.start_date,
        t.due_date,
        t.min_estimated_hours,
        t.max_estimated_hours,
        t.completion_percentage,
        t.vector,
        t.created_at,
        t.updated_at
    FROM tasks t
    WHERE {where_clause}
    ORDER BY 
        CASE 
            WHEN t.due_date < NOW() AND t.status NOT IN ('completed', 'cancelled') THEN 0  -- Overdue first
            WHEN t.priority = 3 THEN 1  -- High priority
            WHEN t.priority = 2 THEN 2  -- Medium priority
            WHEN t.priority = 1 THEN 3  -- Low priority  
            ELSE 4
        END,
        t.due_date ASC,
        t.created_at DESC
    LIMIT {limit or 50}
    OFFSET {offset or 0}
    """

    # Database connection and execution
    db = get_db_connection()
    if not db:
        return json.dumps(
            {
                "success": False,
                "error": "Database connection failed",
                "message": "Unable to establish database connection",
                "query_params": {
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "created_by": created_by,
                    "priority": priority,
                    "status": status,
                    "start_date": start_date,
                    "due_date": due_date,
                    "min_estimated_hours": min_estimated_hours,
                    "max_estimated_hours": max_estimated_hours,
                    "min_completion": min_completion,
                    "max_completion": max_completion,
                    "overdue_only": overdue_only,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
        )

    cursor = db.cursor(buffered=True)

    try:
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()

        # Process results
        tasks_list = []
        for row in results:
            task_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i]

                # Handle datetime and Decimal serialization
                if isinstance(value, datetime):
                    task_dict[column_name] = value.isoformat()
                elif isinstance(value, Decimal):
                    task_dict[column_name] = float(value)
                else:
                    task_dict[column_name] = value

            # No JSON field parsing needed for simplified task structure

            tasks_list.append(task_dict)

    except Exception as e:
        return json.dumps(
            {
                "success": False,
                "error": "Database query failed",
                "message": f"Database error: {str(e)}",
                "query_params": {
                    "task_id": task_id,
                    "title": title,
                    "description": description,
                    "assigned_to": assigned_to,
                    "created_by": created_by,
                    "priority": priority,
                    "status": status,
                    "start_date": start_date,
                    "due_date": due_date,
                    "min_estimated_hours": min_estimated_hours,
                    "max_estimated_hours": max_estimated_hours,
                    "min_completion": min_completion,
                    "max_completion": max_completion,
                    "overdue_only": overdue_only,
                    "limit": limit,
                    "offset": offset,
                },
            },
            indent=2,
            ensure_ascii=False,
        )

    finally:
        cursor.close()

    # Build response with used parameters
    used_params = {
        k: v
        for k, v in {
            "task_id": task_id,
            "title": title,
            "description": description,
            "assigned_to": assigned_to,
            "created_by": created_by,
            "priority": priority,
            "status": status,
            "start_date": start_date,
            "due_date": due_date,
            "min_estimated_hours": min_estimated_hours,
            "max_estimated_hours": max_estimated_hours,
            "min_completion": min_completion,
            "max_completion": max_completion,
            "overdue_only": overdue_only,
            "limit": limit or 50,
            "offset": offset or 0,
        }.items()
        if v is not None
    }

    # Calculate statistics
    summary_stats = {}
    if tasks_list:
        total_estimated_hours = (
            sum(
                (task.get("min_estimated_hours", 0) or 0)
                + (task.get("max_estimated_hours", 0) or 0)
                for task in tasks_list
            )
            / 2
        )
        avg_completion = sum(
            task.get("completion_percentage", 0) or 0 for task in tasks_list
        ) / len(tasks_list)

        status_count = {}
        for task in tasks_list:
            status = task.get("status", "unknown")
            status_count[status] = status_count.get(status, 0) + 1

        summary_stats = {
            "total_found": len(tasks_list),
            "total_estimated_hours": round(total_estimated_hours, 2),
            "average_completion": round(avg_completion, 1),
            "status_breakdown": status_count,
        }
    else:
        summary_stats = {
            "total_found": 0,
            "total_estimated_hours": 0,
            "average_completion": 0,
            "status_breakdown": {},
        }

    # Generate smart message
    if task_id:
        if tasks_list:
            message = f"✅ Task with ID '{task_id}' found successfully"
        else:
            message = f"❌ No task found with ID '{task_id}'"
    elif overdue_only:
        message = f"🚨 Found {len(tasks_list)} overdue task(s)"
    elif (
        len(
            [
                p
                for p in [
                    title,
                    description,
                    assigned_to,
                    created_by,
                    priority,
                    status,
                    start_date,
                    due_date,
                    min_estimated_hours,
                    max_estimated_hours,
                    min_completion,
                    max_completion,
                ]
                if p is not None
            ]
        )
        > 0
    ):
        message = f"✅ Found {len(tasks_list)} task(s) matching search criteria"
    else:
        message = f"✅ Retrieved {len(tasks_list)} task(s) (simple listing)"

    result = {
        "success": True,
        "message": message,
        "summary": summary_stats,
        "query_params": used_params,
        "tasks": tasks_list,
    }

    return json.dumps(result, indent=2, ensure_ascii=False)
