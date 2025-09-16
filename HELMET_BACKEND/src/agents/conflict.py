from langgraph.prebuilt import create_react_agent
from src.config.llm_init import model

from src.config.specifications import working_hours
from langchain.tools import tool

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List


# Define your exact output structure
class ConflictInfo(BaseModel):
    type: str = Field(description="Type of conflict")
    severity: str = Field(description="Severity level")
    description: str = Field(description="Clear explanation")
    affected: List[str] = Field(description="Affected tasks or workers")


class SolutionStep(BaseModel):
    action: str = Field(description="Action to take")
    parameters: dict = Field(
        description="REQUIRED: Parameters used to update or create correctly"
    )
    reason: str = Field(
        description="REQUIRED: Reason for this alternative step used by the Admin and other agents to determine validity"
    )


class Solution(BaseModel):
    recommended: bool = Field(description="Whether solution is recommended")
    steps: List[SolutionStep] = Field(description="Steps to execute")


class Alternative(BaseModel):
    description: str = Field(description="Alternative description")
    steps: List[SolutionStep] = Field(description="Alternative steps")


class ConflictAnalysisResponse(BaseModel):
    feasible: bool = Field(description="Whether request is feasible")
    conflicts: List[ConflictInfo] = Field(description="List of conflicts found")
    solution: Solution = Field(description="Recommended solution")
    alternatives: List[Alternative] = Field(description="Alternative solutions")
    analysis: str = Field(
        description="REQUIRED: Brief summary of the analysis and solution", default=""
    )
    total_time_saved: int = Field(
        description="Total time saved in hours if action list is executed", default=0
    )


# Create the parser
parser = PydanticOutputParser(pydantic_object=ConflictAnalysisResponse)


###############
#### Agent ####
###############


def create_conflict_agent():
    from src.mcp.db_client import get_db_mcp_tools

    # Get format instructions from parser
    format_instructions = parser.get_format_instructions()

    prompt = f"""
    You are the Data Compilation & Conflict Analysis Agent - you GATHER comprehensive data and immediately ANALYZE conflicts to provide CONCRETE SOLUTIONS.

    AVAILABLE TOOLS:
    - find_best_workers_for_task: Semantic search and matching for optimal worker assignment
    - (MCP) search_similar_tasks: Semantic search to find tasks based on description/context
    - (MCP) get_users_for_context: Retrieve filtered user data (id, name, role, skills)
    - (MCP) get_tasks: Retrieve task data with advanced filters (your main data gathering tool)
    - (MCP) get_table_schemas: Get database table schemas
    - (MCP) get_skill_categories: Get skill categories to match workers with tasks
    - (MCP) get_user_roles: Get user roles and permissions

    YOUR DUAL ROLE:
    1. Receive specific data requirements from Planning Agent
    2. Execute focused MCP/Agents queries to gather ALL relevant data
    3. Compile data into structured format
    4. ANALYZE the compiled data for conflicts AND cascading dependencies
    5. PROVIDE CONCRETE, ACTIONABLE SOLUTIONS directly to Planning Agent

    WORKFLOW EXECUTION:
    1. Parse the data from Planning Agent
    2. Execute MCP/Agents queries using available filters to gather:
        - All tasks (semantic search with search_similar_tasks or get_tasks without filters)
            * ALWAYS PRIORITIZE search_similar_tasks for initial retrieval (faster and less data load)
        - Target task details (use get_tasks with task_id)
        - Worker schedules (use get_tasks with assigned_to + date filters)
        - Alternative workers
            * ALWAYS PRIORITIZE find_best_workers_for_task for semantic matching (faster and more relevant)
            - If needed, use get_users_for_context with skill/role filters
        - DEPENDENCY ANALYSIS: Identify all dependent/successor tasks
    3. Compile data and immediately analyze for conflicts
    4. CASCADE ANALYSIS: When delays/changes affect a task, identify ALL dependent tasks that need updates
    5. Generate concrete solutions with step-by-step actions (including dependent task updates)
    6. Return solution JSON directly to Planning Agent

    DATA GATHERING STRATEGY:

    ALL TASKS:
    - ALWAYS PRIORITIZE search_similar_tasks for initial retrieval
    - Use: search_similar_tasks/get_tasks to get all tasks / relevant tasks
    TARGET TASK:
    - Use: get_tasks(task_id="X") to get full task details
    DEPENDENCY CHAIN:
    - Analyze task dependencies to identify successor tasks
    - Use get_tasks to fetch all dependent tasks that might be affected
    - Tasks have a variable dependencies & blocks_tasks
    - Check for tasks that logically depend on the target task 
    ASSIGNED WORKER SCHEDULE:
    - Use: get_tasks(assigned_to="worker_id", start_date="target_date")
    - Filter to ±4 hours of target time during compilation
    ALTERNATIVE WORKERS:
    - Use: find_best_workers_for_task to find best matches
    - Or: get_users_for_context(primary_skill="required_skill", is_active=True)
    - Limit to 5-10 most relevant workers
    ZONE OCCUPANCY:
    - Use: get_tasks with zone filter + target date
    - Include adjacent zones if identifiable
    DEPENDENCIES:
    - Look for tasks with dependencies in target task data
    - Use get_tasks to fetch predecessor/successor details

    CONFLICT ANALYSIS CAPABILITIES:
    - Find Critical Conflicts
    - Detect Worker Overlaps (working hour: {working_hours})
    - Spot Zone Clashes
    - Identify Resource Shortages
    - Highlight Safety Issues
    - Flag Regulatory Non-Compliance
    - CASCADE IMPACT ANALYSIS: Identify all dependent tasks affected by changes
    - STATUS VERIFICATION: Check for data integrity issues
    - PROVIDE STEP-BY-STEP SOLUTIONS

    CASCADE ANALYSIS PROCESS:
    When analyzing delays, changes, or status conflicts:
    - Identify Direct Dependencies: Tasks that directly depend on the target task
    - Logical Dependency Chain: Tasks that logically follow (excavation → foundation → framing)
    - Impact Assessment: Determine which dependent tasks need status/schedule updates
    - Solution Integration: Include individual update_task actions for each affected dependent task in the main action list

    ANALYSIS PROCESS:
    1. Check worker availability at proposed time
    2. Check zone availability at proposed time
    3. Verify worker skills match task requirements (find_best_workers_for_task or get_users_for_context)
    4. Count worker's current workload
    5. Check dependencies are met
    6. ANALYZE CASCADE IMPACT: Identify all dependent tasks affected
    7. Identify ALL conflicts (even edge cases)
    8. GENERATE CONCRETE SOLUTION with dependency updates

    SOLUTION GENERATION:
    When conflicts are found, provide a complete solution with:
    1. PRIMARY SOLUTION: Main recommended solution in the "solution" field
    2. MANDATORY ALTERNATIVES: ALWAYS provide at least 2 alternative solutions in the "alternatives" array
    3. Exact parameter changes needed for each solution and alternative
    4. Include individual update_task actions for ALL affected dependent tasks
    5. Each step includes the exact MCP tool to call and parameters (update_task, update_user, create_task, etc.)
    6. TIME BUFFER: Always add extra time for unexpected field problems using time_saved parameter
    7. Use helper tools when creating complex solutions that require skill/role matching

    ALTERNATIVES REQUIREMENT:
    - MANDATORY: alternatives array must contain at least 2 different approaches
    - Each alternative must have different worker assignments, timing, or approach
    - Examples: different workers, different time slots, different task sequencing
    - If no conflicts exist, still provide alternatives (e.g., alternative workers, backup timing)

    SOLUTION QUALITY REQUIREMENTS:
    - Solutions must be IMMEDIATELY EXECUTABLE by Planning Manager
    - No vague suggestions like "try another time" - specify exact times
    - No generic advice - provide exact parameter values
    - Every SolutionStep MUST include a reason field
    - Include the reasoning for each step
    - NO abstract operations like "cascade_update" - only real MCP operations
    - Include time_saved parameter in task updates for unexpected issues

    EFFICIENT QUERY STRATEGY:
    1. search_similar_tasks(query="request context") - Semantic search to find relevant tasks
    2. get_tasks() - Retrieve ALL tasks initially
    3. get_tasks(task_id="X") → Get target task
    4. get_users_for_context(user_id="assigned_worker_id") → Get worker details
    5. get_tasks(assigned_to="worker_id", start_date="date") → Worker schedule
    6. find_best_workers_for_task → Semantic worker matching Tasks to Workers
    7. get_users_for_context(primary_skill="required_skill", limit=10) → Alternative workers
    8. get_tasks(assigned_to="alt_worker_id", start_date="date") → Alt worker schedules
    9. get_tasks(start_date="date") → All tasks for zone filtering during compilation
    10. get_users_for_context() → Get all users

    FILTERING DURING COMPILATION:
    - Remove tasks outside ±4 hours of target time
    - Remove workers without required skills
    - Remove completed/cancelled tasks
    - Keep only adjacent zones (if identifiable)
    - Limit alternative workers to top 5-10 matches

  
    CRITICAL: You MUST return this EXACT JSON format (no extra text):
    {format_instructions}

    RULES:
    - CRITICAL: EVERY SolutionStep MUST have a reason field (validation requirement)
    - CRITICAL: MUST include analysis field in response (validation requirement)  
    - CRITICAL: MANDATORY alternatives array with at least 2 alternatives (validation requirement)
    - CRITICAL: MUST calculate and include total_time_saved field (sum of hours saved by solution)
    - REQUIRED: Include time_saved parameter in task updates for buffer time
    - CASCADE HANDLING: Include individual update_task actions for dependent tasks in main action list
    - NEVER hallucinate data - only use MCP/Agent tool results
    - Use MCP/Agent filters extensively to reduce data volume
    - Compile efficiently but keep all conflict-relevant data
    - Analyze conflicts thoroughly using gathered data
    - ALWAYS provide concrete solutions when feasible
    - If critical data is missing, return: {{"error": "Missing required data: [what's missing]"}}
    - NO narrative text before or after the JSON
    - Working hours: {working_hours}
    - Buffer requirement: 15 minutes between teams in same zone

    VALIDATION CHECKLIST BEFORE RESPONDING:
    ✓ feasible: boolean value present
    ✓ conflicts: array present (can be empty)
    ✓ solution: object with recommended + steps array present
    ✓ alternatives: array with at least 2 alternatives present (MANDATORY)
    ✓ analysis: string summary present (MANDATORY)
    ✓ total_time_saved: number present
    ✓ Every SolutionStep has reason field
    
    NEVER add narrative text after the JSON. The JSON is your final output.
    """

    return create_react_agent(
        model=model,
        tools=[
            *get_db_mcp_tools(
                [
                    "get_users_for_context",
                    "get_table_schemas",
                    "get_tasks",
                    "search_similar_tasks",
                    "find_best_workers_for_task",
                ],
            ),
            # find_best_workers_for_task,
        ],
        prompt=prompt,
        name="conflict_agent",
    )


# Use the parser in your tool
@tool
def conflict_agent_as_tool(
    request: str,
    task_id: str = "",
    worker_id: str = "",
    zone: str = "",
    date: str = "",
) -> str:
    """Compile data and analyze conflicts with structured output"""

    conflict_agent = create_conflict_agent()

    detailed_request = f"""
    Original request: {request}

    Gather data and analyze conflicts for:
    - Task ID: {task_id if task_id else 'extract from request'}
    - Worker ID: {worker_id if worker_id else 'extract from request'}
    - Zone: {zone if zone else 'extract from request'}
    - Date: {date if date else 'extract from request'}
    """.strip()

    result = conflict_agent.invoke({"messages": [("ai", detailed_request)]})

    # Parse the response to ensure it matches the structure
    try:
        content = result["messages"][-1].content.strip()
        parsed_response = parser.parse(content)
        return parsed_response.model_dump_json()
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse response: {str(e)}"}}'
