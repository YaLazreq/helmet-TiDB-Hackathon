from langgraph.prebuilt import create_react_agent
from .team_builder import team_builder_agent_as_tool
from src.config.llm_init import model

from src.config.specifications import working_hours
from langchain.tools import tool

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional


# Define your exact output structure
class ConflictInfo(BaseModel):
    type: str = Field(description="Type of conflict")
    severity: str = Field(description="Severity level")
    description: str = Field(description="Clear explanation")
    affected: List[str] = Field(description="Affected tasks or workers")


class SolutionStep(BaseModel):
    action: str = Field(description="Action to take")
    parameters: dict = Field(description="Parameters for the action")
    reason: str = Field(description="Reason for this step")


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
    analysis: str = Field(description="Brief summary")


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
    - (MCP) get_users_for_context: Retrieve filtered user data (id, name, role, skills)
    - (MCP) get_tasks: Retrieve task data with advanced filters (your main data gathering tool)
    - (MCP) get_table_schemas: Get database table schemas
    - (MCP) get_skill_categories: Get skill categories to match workers with tasks
    - (MCP) get_user_roles: Get user roles and permissions

    YOUR DUAL ROLE:
    1. Receive specific data requirements from Planning Agent
    2. Execute focused MCP queries to gather ALL relevant data
    3. Compile data into structured format
    4. ANALYZE the compiled data for conflicts
    5. PROVIDE CONCRETE, ACTIONABLE SOLUTIONS directly to Planning Agent

    WORKFLOW EXECUTION:
    1. Parse the data from Planning Agent
    2. Execute MCP queries using available filters to gather:
        - All tasks (get_tasks without filters)
        - Target task details (use get_tasks with task_id)
        - Worker schedules (use get_tasks with assigned_to + date filters)
        - Alternative workers (use get_users_for_context with skill filters)
    3. Compile data and immediately analyze for conflicts
    4. Generate concrete solutions with step-by-step actions
    5. Return solution JSON directly to Planning Agent

    DATA GATHERING STRATEGY:

    ALL TASKS:
    - Use: get_tasks() to get all tasks
    TARGET TASK:
    - Use: get_tasks(task_id="X") to get full task details
    ASSIGNED WORKER SCHEDULE:
    - Use: get_tasks(assigned_to="worker_id", start_date="target_date")
    - Filter to ±4 hours of target time during compilation
    ALTERNATIVE WORKERS:
    - Use: get_users_for_context(primary_skill="required_skill", is_active=True)
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
    - PROVIDE STEP-BY-STEP SOLUTIONS

    ANALYSIS PROCESS:
    1. Check worker availability at proposed time
    2. Check zone availability at proposed time
    3. Verify worker skills match task requirements
    4. Count worker's current workload
    5. Check dependencies are met
    6. Identify ALL conflicts (even edge cases)
    7. GENERATE CONCRETE SOLUTION

    SOLUTION GENERATION:
    When conflicts are found, provide a complete solution with:
    1. Rank multiple alternatives by preference
    2. Exact parameter changes needed
    3. Alternative options ranked by preference
    4. Each step includes the exact MCP tool to call and parameters (update_task, update_user, create_task, etc.)
    5. Use helper tools when creating complex solutions that require skill/role matching

    SOLUTION QUALITY REQUIREMENTS:
    - Solutions must be IMMEDIATELY EXECUTABLE by Planning Manager
    - No vague suggestions like "try another time" - specify exact times
    - No generic advice - provide exact parameter values
    - Include the reasoning for each step

    EFFICIENT QUERY STRATEGY:
    1. get_tasks() - Retrieve ALL tasks initially
    2. get_tasks(task_id="X") → Get target task
    3. get_users_for_context(user_id="assigned_worker_id") → Get worker details
    4. get_tasks(assigned_to="worker_id", start_date="date") → Worker schedule
    5. get_users_for_context(primary_skill="required_skill", limit=10) → Alternative workers
    6. get_tasks(assigned_to="alt_worker_id", start_date="date") → Alt worker schedules
    7. get_tasks(start_date="date") → All tasks for zone filtering during compilation
    8. get_users_for_context() → Get all users

    FILTERING DURING COMPILATION:
    - Remove tasks outside ±4 hours of target time
    - Remove workers without required skills
    - Remove completed/cancelled tasks
    - Keep only adjacent zones (if identifiable)
    - Limit alternative workers to top 5-10 matches

  
    CRITICAL: You MUST return this EXACT JSON format (no extra text):
    {format_instructions}

    RULES:
    - NEVER hallucinate data - only use MCP tool results
    - Use MCP filters extensively to reduce data volume
    - Compile efficiently but keep all conflict-relevant data
    - Analyze conflicts thoroughly using gathered data
    - ALWAYS provide concrete solutions when feasible
    - If critical data is missing, return: {{"error": "Missing required data: [what's missing]"}}
    - NO narrative text before or after the JSON
    - Working hours: {working_hours}
    - Buffer requirement: 15 minutes between teams in same zone

    NEVER add narrative text after the JSON. The JSON is your final output.
    """

    return create_react_agent(
        model=model,
        tools=get_db_mcp_tools(
            [
                "get_users_for_context",
                "get_table_schemas",
                "get_tasks",
                "search_similar_tasks",
            ],
            team_builder_agent_as_tool,
        ),
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
        parsed_response = parser.parse(result["messages"][-1].content)
        return parsed_response.json()
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse response: {str(e)}"}}'
