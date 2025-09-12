from langgraph.prebuilt import create_react_agent
from src.agents.conflict import conflict_agent_as_tool
from src.config.llm_init import model
from langchain.tools import tool
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any


# Define Executor Agent output structure
class ExecutedAction(BaseModel):
    action_type: str = Field(
        description="Type of action executed: update_task|create_task|update_user|create_user"
    )
    target: str = Field(
        description="Human-readable identifier (e.g., 'Task 7 - Painting')"
    )
    change: str = Field(
        description="Specific modification made (e.g., 'Created new task with ID 15')"
    )
    result: str = Field(description="Result of the execution")


class ExecutorResponse(BaseModel):
    description: str = Field(description="Clear description of what was executed")
    what_you_need_to_know: str = Field(
        description="CONCISE core facts only - what happened (max. 180 characters). NO explanations, reasons, or elaboration.",
        max_length=180,
    )
    actions_executed: List[ExecutedAction] = Field(
        description="List of actions that were executed"
    )
    notification_needed: bool = Field(
        description="Whether notification to the team is needed", default=True
    )
    success: bool = Field(description="Whether all operations were successful")
    urgency_level: int = Field(
        description="Urgency level: 0=low, 1=medium, 2=high", default=1
    )


# Create the parser
executor_parser = PydanticOutputParser(pydantic_object=ExecutorResponse)

################
#### Agent ####
################


def create_executor_agent():
    from src.mcp.db_client import (
        get_db_mcp_tools,
    )

    # Get format instructions from parser
    format_instructions = executor_parser.get_format_instructions()

    # Update prompt with format instructions
    formatted_prompt = f"""
    You are the Executor Agent - you have the right to update and create tasks and users in the system.

    AVAILABLE TOOLS:
    - update_task: Update an existing task in the system
    - create_task: Create a new task in the system
    - update_user: Update an existing user in the system
    - create_user: Create a new user in the system
    - get_tasks: Retrieve tasks from the system
    - get_users: Retrieve users from the system
    - get_users_for_context: Retrieve users with detailed context (skills, roles, assignments)
    - get_table_schemas: Retrieve database table schemas for reference

    YOUR PRIMARY GOAL:
    - Execute database operations (create/update tasks and users) based on approved requests
    - Provide structured response for notification system
    - Act decisively and accurately

    CRITICAL GUIDELINES:
    - You can ONLY execute tools if the request was made by the Supervisor, Robert Martinez (ID: 1)
      HE IS THE ONLY ONE AUTHORIZED TO MAKE REQUESTS TO YOU.
    - To VERIFY the requestor, ALWAYS CHECK the user ID in the message prefix.
      If the user ID is not 1, REJECT the request and DO NOT use any tools.
    - If the requestor is not authorized, return rejection in the structured format.

    EXECUTION WORKFLOW:
    1. VERIFY AUTHORIZATION: Check if requestor is Supervisor (ID: 1)
    2. EXECUTE OPERATIONS: Perform the requested database operations
    3. GATHER RESULTS: Collect information about what was executed
    4. RETURN STRUCTURED RESPONSE: Always return the JSON format below

    NOTIFICATION LOGIC:
    - notification_needed = true: For successful operations (default)
    - notification_needed = false: Only for rejections or information-only responses
    - urgency_level: 0=low, 1=medium (default), 2=high
    - success: true if all operations succeeded, false otherwise

    RESPONSE REQUIREMENTS:
    - Always return structured JSON format (no extra text)
    - Include details of all executed actions in actions_executed
    - what_you_need_to_know: ONLY core facts, no explanations or reasons
      ✅ Good: "Updated user John's phone to 0606060606"
      ❌ Bad: "Request to update user John's phone was successful and database has been modified"
    - Set appropriate urgency_level based on operation impact

    AUTHORIZATION REJECTION FORMAT (if not authorized):
    Use success: false, notification_needed: false, and explain rejection in what_you_need_to_know.

    CRITICAL: You MUST return this EXACT JSON format (no extra text):
    {format_instructions}

    Take your time to understand the request and plan your actions carefully.
    You can use the tools multiple times if needed.
    
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
                    "update_task",
                    "create_task",
                    "update_user",
                    "create_user",
                ]
            ),
        ],
        prompt=formatted_prompt,
        name="executor_agent",
    )


@tool
def executor_agent_as_tool(request: str) -> str:
    """Executor agent with structured JSON output for supervisor integration"""

    executor_agent = create_executor_agent()

    result = executor_agent.invoke({"messages": [("ai", request)]})

    # Parse the response to ensure it matches the structure
    try:
        content = result["messages"][-1].content.strip()
        parsed_response = executor_parser.parse(content)
        return parsed_response.model_dump_json()
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse executor response: {str(e)}"}}'


# Create the agent
executor_agent = create_executor_agent()
