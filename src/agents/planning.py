from langgraph.prebuilt import create_react_agent
from src.agents.conflict import conflict_agent_as_tool
from src.config.llm_init import model

from src.config.specifications import working_hours
from langchain.tools import tool
from langchain.output_parsers import PydanticOutputParser

from pydantic import BaseModel, Field
from typing import List, Dict, Any


# Define Planning Agent output structure
class WhatWeCanTrigger(BaseModel):
    action_type: str = Field(
        description="Type of action: update_task|create_task|update_user|create_user"
    )
    target: str = Field(
        description="Human-readable identifier (e.g., 'Task 7 - Painting')"
    )
    change: str = Field(
        description="CONCISE action only - what will be done (e.g., 'Reschedule to 16:00'). NO explanations or reasons."
    )
    reason: str = Field(description="Why this change is necessary")


class ActionList(BaseModel):
    action: str = Field(description="Action to execute (e.g., 'update_task')")
    parameters: Dict[str, Any] = Field(description="Parameters for the action")


class PlanningResponse(BaseModel):
    description: str = Field(description="Clear description of the request")
    what_you_need_to_know: str = Field(
        description="CONCISE core facts only - essential information (max. 150 characters). NO explanations or elaboration.",
        max_length=150,
    )
    what_we_can_trigger: List[WhatWeCanTrigger] = Field(
        description="List of actions that can be triggered",
    )
    notification_needed: bool = Field(
        description="Whether notification to the supervisor is needed"
    )
    action_list: List[ActionList] = Field(description="List of actions to execute")
    urgency_level: int = Field(description="Urgency level: 0=low, 1=medium, 2=high")
    total_time_saved: int = Field(
        description="Total time saved in hours if action list is executed", default=0
    )


# Create the parser
planning_parser = PydanticOutputParser(pydantic_object=PlanningResponse)


################
#### Agent ####
################


def create_planning_agent():
    from src.mcp.db_client import (
        get_db_mcp_tools,
    )

    # Get format instructions from parser
    format_instructions = planning_parser.get_format_instructions()

    # Update prompt with format instructions
    formatted_prompt = f"""
    You are the Planning Manager - you analyze scheduling requests and prepare responses for the Construction Site Supervisor.

    AVAILABLE TOOLS:
    - conflict_agent_as_tool: Delegate conflict analysis to specialized agent
    - search_similar_tasks: Find a task or similar tasks based on description
    - (MCP) get_tasks: Read task data (READ-ONLY)
    - (MCP) get_users: Read user data (READ-ONLY)

    IMPORTANT: You have NO access to create_* or update_* tools. All modifications require supervisor approval.

    WORKFLOW EXECUTION:
        1. UNDERSTAND the request
        2. DELEGATE to conflict_agent_as_tool IMMEDIATELY when:
        - User reports problems, delays, conflicts, or issues
        - User request involves creation, scheduling, rescheduling, or assignments
        - You need to check for conflicts (zone, worker, skill, dependencies, resources)

        DO NOT use conflict_agent_as_tool when:
        - Just retrieving information about existing tasks (use get_tasks directly)
        - Simple queries that don't involve scheduling changes (use get_tasks directly)
        
        CRITICAL: For problem reports/scheduling requests, call conflict_agent_as_tool FIRST - do not gather data with tools first!

        3. PREPARE RESPONSE OBJECT:
        Always return the structured object format specified below.

        NOTIFICATION LOGIC:
        - notification_needed = false: Information-only requests → no database changes needed → supervisor just reads the response
        - notification_needed = true: Updates/creates needed → supervisor triggers notification system → approval required
        - urgency_level: 0=low, 1=medium, 2=high
        - total_time_saved: Use the value from conflict_agent_as_tool response (conflict analysis calculates time savings)

        KEY RULES:
        - Information-only requests → notification_needed: false, what_we_can_trigger: [], action_list: [], total_time_saved: 0
        - ANY database modification (even without conflicts) → notification_needed: true
        - what_you_need_to_know: ONLY essential facts, no explanations
          ✅ Good: "Painting task B.200 needs rescheduling to 16:00"
          ❌ Bad: "The painting task for room B.200 requires rescheduling due to conflicts and should be moved to 16:00 for optimal resource allocation"
        - what_we_can_trigger.change: Direct action only, no explanations
          ✅ Good: "Reschedule to 16:00"
          ❌ Bad: "Reschedule from 14:00 to 16:00 due to worker availability"
        - Use conflict_agent_as_tool's solution to build action_list
        - If solution.recommended is false, use alternatives[0]
        - EXTRACT total_time_saved from conflict_agent_as_tool response and use it directly in your response

        DELEGATION PARAMETERS:
        When calling conflict_agent_as_tool, extract and pass:
        - request: Original user request
        - task_id: Target task ID (if given)
        - worker_id: Worker involved (if given)
        - zone: Zone affected (if given)
        - date: Date for the change (if given)

        CRITICAL: You MUST return this EXACT JSON format (no extra text):
        {format_instructions}

        SUCCESS CONDITIONS:
        - Information requests: Used get_* tools ✓ + Returned data in what_you_need_to_know ✓ + notification_needed: false ✓
        - Conflict analysis requests: Called conflict_agent_as_tool ✓ + Created complete response ✓ + notification_needed: true ✓
        - Update/create requests: Built complete action_list using conflict_agent_as_tool ✓ + notification_needed: true ✓

        RULES:
        - NEVER hallucinate data - only use MCP tool results
        - Always provide concrete information in responses
        - If critical data is missing, include error in what_you_need_to_know

        NEVER add narrative text before or after the JSON. The JSON is your final output.
    """

    return create_react_agent(
        model=model,
        tools=[
            *get_db_mcp_tools(
                [
                    "get_users_for_context",
                    "get_users",
                    "get_table_schemas",
                    "get_tasks",
                    "search_similar_tasks",
                ]
            ),
            conflict_agent_as_tool,
        ],
        prompt=formatted_prompt,
        name="planning_agent",
    )


@tool
def planning_agent_as_tool(request: str) -> str:
    """Planning agent with structured JSON output for supervisor integration"""

    planning_agent = create_planning_agent()

    result = planning_agent.invoke({"messages": [("ai", request)]})

    # Parse the response to ensure it matches the structure
    try:
        content = result["messages"][-1].content.strip()
        parsed_response = planning_parser.parse(content)
        return parsed_response.model_dump_json()
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse planning response: {str(e)}"}}'


# Create the agent
planning_agent = create_planning_agent()
