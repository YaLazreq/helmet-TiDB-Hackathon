# A8 - Conflict Detector ⚠️
# Role: The DETECTIVE - Finds problems
# What it does:

# READS the current schedule
# IDENTIFIES problems and overlaps
# WARNS about issues
# Does NOT fix anything
# from typing import List, Any, Optional
# from .base_agent import BaseAgent


from langgraph.prebuilt import create_react_agent
from src.config.llm_init import model
from .sql_agent import sql_agent
from src.config.db import table_schema

# ! Add after to the prompt
# resource availability
# team restrictions

###############
#### Agent ####
###############

prompt = """"
    You are the Conflict Detector (A8) - you ANALYZE scheduling feasibility, identify conflicts on construction sites.

    CAPABILITIES:
    - Use sql_agent tool to query the database for current schedules, worker assignments, and resource bookings
    - Analyze time overlaps
    - Check zone availability

    AVAILABLE TABLES IN DATABASE:
    {tables_schema}

    IMPORTANT:
    1. CRITICAL: When using sql_agent tool, provide NATURAL LANGUAGE requests, NEVER SQL code!
        - "e.g. Find tasks scheduled for September 4th, 2025"
        - "e.g. Get user information for worker ID 2"
        - "e.g. Show all pending tasks assigned to Jean Dupont"
    2. If no relevant data found after 3 tries, stop and RETURN the JSON define below!

    WORKFLOW:
    1. Use sql_agent to get information from the database
    3. Analyze conflicts using ONLY existing TABLES
    4. Report findings with specific details

    CRITICAL OUTPUT FORMAT (always return this JSON on SUCCESS):
    {{
        "feasible": true / false,
        "conflicts": [
            {{
                "type": "zone_conflict|worker_conflict|etc",
                "severity": "high|medium|low",
                "description": "Clear explanation",
                "affected": ["task_ids or workers affected"]
            }}   
        ],
        "suggestions": [
            "e.g: Move to 16:00 when zone is free",
            "e.g: Assign different worker (Marie available)",
            "e.g: Use adjacent room B.201 instead"
        ],
        "analysis": "Brief summary of the situation or explain the problem if not feasible"
    }}

"""

conf_agent = create_react_agent(
    model=model,
    tools=[sql_agent],
    prompt=prompt.format(tables_schema=table_schema),
    name="conflict_agent",
)

##############
#### Tool ####
##############


def conflict_agent(schedule_data: str) -> str:
    """Check for conflicts in the planning construction for date / time"""
    result = conf_agent.invoke(
        {
            "messages": [
                ("human", f"Check for conflicts in this schedule: {schedule_data}")
            ]
        }
    )
    return result["messages"][-1].content
