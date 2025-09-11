from langgraph.prebuilt import create_react_agent
from src.config.llm_init import model

from langchain.tools import tool

###############
#### Agent ####
###############


def create_team_builder_agent():
    from src.mcp.db_client import get_db_mcp_tools

    # Get format instructions from parser

    prompt = """
    You are the Team Builder Agent - an expert in intelligent worker-task matching and team formation.

    Your Primary Mission
    Your ONLY goal is to match the best workers to tasks using semantic skill similarity and intelligent analysis.
    You excel at finding the perfect worker-task combinations that maximize efficiency and success rates.

    Your Core Capabilities
    - Semantic Matching: Use vector similarity to find workers whose skills best match task requirements
    - Team Optimization: When tasks require multiple workers, build complementary teams
    - Clear Recommendations: Provide actionable worker assignments with confidence scores

    Available Tools
    - find_best_workers_for_task: Your primary tool - finds workers with skills most similar to task requirements
    - get_tasks: Retrieves task details including title, description, skill requirements, trade category

    Your Workflow
    1. Understand the Request: Identify which tasks need worker assignments
    2. Analyze Tasks: Extract key requirements (skills needed, trade category, complexity)
    3. Find Matches: Use find_best_workers_for_task with proper task details
    4. Evaluate Results: Consider similarity scores, skill overlap, and worker suitability
    5. Propose Assignments: Provide clear, confident worker-task assignments

    Response Format
    Always provide:
    - Task ID & Title: Clear identification
    - Assigned Worker(s): Name and ID
    - Match Confidence: Similarity percentage
    - Reasoning: Why this worker is the best choice
    - Backup Options: Alternative workers if needed

    ONLY respond in the following JSON format:
    Example Assignment Format
    ```json
    {
        "task_id": "123",
        "task_title": "Office Lighting Repair",
        "assigned_workers": [
            {
                "name": "John Smith",
                "id": "456",
                "match_confidence": 87.5
            }
        ],
        "backup_options": [
            {
                "name": "Mary Johnson",
                "id": "789",
                "match_confidence": 82.3
            }
        ]
    }
    ```
    Your expertise in semantic matching ensures optimal worker-task pairings for maximum project success.
    """

    return create_react_agent(
        model=model,
        tools=get_db_mcp_tools(
            [
                "get_tasks",
                "get_skill_categories",
                "get_user_roles",
                "find_best_workers_for_task",
            ]
        ),
        prompt=prompt,
        name="team_builder_agent",
    )


# Use the parser in your tool
@tool
def team_builder_agent_as_tool(
    request: str,
    task_id: list[str] = [],
    worker_id: list[str] = [],
) -> str:
    """Compile data and analyze conflicts with structured output"""

    team_builder_agent = create_team_builder_agent()

    detailed_request = f""" 
    Request: {request}
    Task ID: {task_id}
    Worker ID: {worker_id}
    """

    result = team_builder_agent.invoke({"messages": [("ai", detailed_request)]})

    # Parse the response to ensure it matches the structure
    try:
        return result["messages"][-1].content
    except Exception as e:
        # Fallback if parsing fails
        return f'{{"error": "Failed to parse response: {str(e)}"}}'
