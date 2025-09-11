from langgraph.prebuilt import create_react_agent
from src.agents.conflict import conflict_agent_as_tool
from src.config.llm_init import model

from src.config.specifications import working_hours
from langchain.tools import tool
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# Define Planning Agent output structure
class WhatWeCanTrigger(BaseModel):
    action_type: str = Field(
        description="Type of action: update_task|create_task|update_user|create_user"
    )
    target: str = Field(
        description="Human-readable identifier (e.g., 'Task 7 - Painting')"
    )
    change: str = Field(
        description="Specific modification (e.g., 'Reschedule from 14:00 to 16:00')"
    )
    reason: str = Field(description="Why this change is necessary")


class ActionList(BaseModel):
    action: str = Field(description="Action to execute (e.g., 'update_task')")
    parameters: Dict[str, Any] = Field(description="Parameters for the action")


class PlanningResponse(BaseModel):
    description: str = Field(description="Clear description of the request")
    what_you_need_to_know: str = Field(description="Context explaining the situation")
    what_we_can_trigger: List[WhatWeCanTrigger] = Field(
        description="List of actions that can be triggered"
    )
    notification_needed: bool = Field(description="Whether notification is needed")
    action_list: List[ActionList] = Field(description="List of actions to execute")
    urgency_level: int = Field(description="Urgency level: 0=low, 1=medium, 2=high")


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
    - (MCP) get_tasks: Read task data (READ-ONLY)
    - (MCP) get_users: Read user data (READ-ONLY)

    IMPORTANT: You have NO access to create_* or update_* tools. All modifications require supervisor approval.

    WORKFLOW EXECUTION:
        1. UNDERSTAND the request
        2. DELEGATE to conflict_agent_as_tool when:
        - User request involves creation, scheduling, rescheduling, or assignments
        - You need to check for conflicts (zone, worker, skill, dependencies, resources)
    
        DO NOT use conflict_agent_as_tool when:
        - Just retrieving information about existing tasks
        - Simple queries that don't involve scheduling changes

        3. PREPARE RESPONSE OBJECT:
        Always return the structured object format specified below.

        NOTIFICATION LOGIC:
        - notification_needed = false: Information-only requests → no database changes needed → supervisor just reads the response
        - notification_needed = true: Updates/creates needed → supervisor triggers notification system → approval required
        - urgency_level: 0=low, 1=medium, 2=high

        KEY RULES:
        - Information-only requests → notification_needed: false, what_we_can_trigger: [], action_list: []
        - ANY database modification (even without conflicts) → notification_needed: true
        - Always provide context in "what_you_need_to_know" (data for info requests, conflict analysis for updates)
        - Use conflict_agent_as_tool's solution to build action_list
        - If solution.recommended is false, use alternatives[0]

        DELEGATION PARAMETERS:
        When calling conflict_agent_as_tool, extract and pass:
        - request: Original user request
        - task_id: Target task ID (if identifiable)
        - worker_id: Worker involved (if specified)
        - zone: Zone affected (if specified)  
        - date: Date for the change (if specified)

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
        - NO narrative text before or after the JSON
        - Working hours: {working_hours}

        NEVER add narrative text after the JSON. The JSON is your final output.
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


# Use the parser in a tool wrapper
@tool
def planning_agent_as_tool(request: str) -> str:
    """Planning agent with structured JSON output for supervisor integration"""

    planning_agent = create_planning_agent()

    result = planning_agent.invoke({"messages": [("human", request)]})

    # Parse the response to ensure it matches the structure
    try:
        parsed_response = planning_parser.parse(result["messages"][-1].content)
        return parsed_response.model_dump_json()
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse planning response: {str(e)}"}}'


# Create the agent
planning_agent = create_planning_agent()
