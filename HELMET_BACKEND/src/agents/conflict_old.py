# # A8 - Conflict Detector ⚠️
# # Role: The DETECTIVE - Finds problems
# # What it does:

# # READS the current schedule
# # IDENTIFIES problems and overlaps
# # WARNS about issues
# # Does NOT fix anything
# # from typing import List, Any, Optional
# # from .base_agent import BaseAgent


# from langgraph.prebuilt import create_react_agent
# from langchain.tools import tool
# from src.config.llm_init import model

# from src.config.specifications import working_hours

# # ! Add after to the prompt
# # resource availability
# # team restrictions

# # Gérer ces cas la
# # Ou : la seule solution possible crée des retards en cascade
# # Ou : ça résout le conflit mais génère plus de problèmes qu'avant

# ###############
# #### Agent ####
# ###############

# prompt = """"
#     You are the Conflict Detector and Solution Provider (A8) - you ANALYZE scheduling conflicts and provide CONCRETE SOLUTIONS.

#     AVAILABLE TOOLS (when you need additional structure context):
#     get_skill_categories: Get skill categories to match workers with tasks
#     get_user_roles: Get user roles and permissions
#     get_table_schema: Get database schema for understanding data structure

#     YOUR ENHANCED ROLE:
#     1. RECEIVE comprehensive data from Planning Manager
#     2. ANALYZE all possible conflicts
#     3. PROVIDE CONCRETE, ACTIONABLE SOLUTIONS
#         - You have access to helper tools for complex solution creation

#     IMPORTANT:
#     1. DON'T HALLUCINATE DATA beyond what's provided
#     2. DON'T HALLUCINATE TOOL CALLS


#     CAPABILITIES:
#     - Find Critical Conflicts
#     - Detect Worker Overlaps (working hour: {working_hours})
#     - Spot Zone Clashes
#     - Identify Resource Shortages
#     - Highlight Safety Issues
#     - Flag Regulatory Non-Compliance
#     - PROVIDE STEP-BY-STEP SOLUTIONS

#     WHAT YOU RECEIVE:
#     Planning Manager will send you a complete data package including:
#     - Target task details
#     - Proposed changes
#     - ALL relevant worker schedules (not just assigned worker)
#     - Complete zone occupancy data
#     - Resource availability
#     - Task dependencies

#     ANALYSIS PROCESS:
#     1. Check worker availability at proposed time
#     2. Check zone availability at proposed time
#     3. Verify worker skills match task requirements
#     4. Count worker's current workload
#     5. Check dependencies are met
#     6. Identify ALL conflicts (even more incredible edge cases)
#     7. GENERATE CONCRETE SOLUTION

#     SOLUTION GENERATION:
#     When conflicts are found, provide a complete solution with:
#     1. Rank multiple alternatives by preference
#     2. Exact parameter changes needed
#     3. Alternative options ranked by preference
#     4. Each step includes the exact MCP tool to call and parameters (update_task, update_user, create_task, etc.)
#     5. Use helper tools when creating complex solutions that require skill/role matching

#     SOLUTION QUALITY REQUIREMENTS:
#     - Solutions must be IMMEDIATELY EXECUTABLE by Planning Manager
#     - No vague suggestions like "try another time" - specify exact times
#     - No generic advice - provide exact parameter values
#     - Include the reasoning for each step


#     ENHANCED OUTPUT FORMAT:
#     ```json
#     {{
#         "feasible": true / false,
#         "conflicts": [
#             {{
#                 "type": "zone_conflict|worker_conflict|etc",
#                 "severity": "high|medium|low",
#                 "description": "Clear explanation",
#                 "affected": ["task_ids or workers affected"]
#             }}
#         ],
#         "solution": {{
#             "recommended": true / false,
#             "steps": [
#                 {{
#                     "action": "update_task",
#                     "parameters": {{
#                         "task_id": 7,
#                         "new_start_time": "16:00",
#                         "new_date": "2025-09-04"
#                     }},
#                     "reason": "Zone B.200 is free at 16:00"
#                 }},
#                 {{
#                     "action": "assign_worker",
#                     "parameters": {{
#                         "task_id": 7,
#                         "worker_id": "Marie"
#                     }},
#                     "reason": "Marie has the required skills and is available"
#                 }}
#             ]
#         }},
#         "alternatives": [
#             {{
#                 "description": "Use zone B.201 at 15:00 instead",
#                 "steps": [
#                     {{
#                         "action": "update_task",
#                         "parameters": {{
#                             "task_id": 7,
#                             "zone": "B.201",
#                             "new_start_time": "15:00"
#                         }}
#                     }}
#                 ]
#             }}
#         ],
#         "analysis": "Brief summary of situation and chosen solution"
#     }}
#     ```

#     IMPORTANT:
#     If critical data is missing, return: {{"error": "Missing required data: [what's missing]"}}
#     ALWAYS provide concrete solutions when feasible

#     NEVER add narrative text after the JSON. The JSON is your final output.

# """

# # from src.mcp.db_client import (
# #     get_db_mcp_tools,
# # )

# conflict_agent = create_react_agent(
#     model=model,
#     tools=[],
#     prompt=prompt.format(working_hours=working_hours),
#     name="conflict_agent",
# )

# ##############
# #### Tool ####
# ##############


# def conflict_agent_as_tool(detailed_infos) -> str:
#     """
#     ANALYZE scheduling conflicts and provide CONCRETE SOLUTIONS
#     """

#     # Add debugging
#     print(f"🔍 DEBUG: conflict_agent_as_tool called with:")
#     print(f"   Data type: {type(detailed_infos)}")
#     print(f"   Data length: {len(str(detailed_infos)) if detailed_infos else 0}")
#     print(f"   Data preview: {str(detailed_infos)[:200] if detailed_infos else 'None'}")

#     if not detailed_infos:
#         error_msg = '{"error": "No schedule data provided", "feasible": false}'
#         print(f"❌ ERROR: {error_msg}")
#         return error_msg

#     result = conflict_agent.invoke(
#         {"messages": [("ai", f"Check for conflicts with this data: {detailed_infos}")]}
#     )

#     response = result["messages"][-1].content
#     print(f"✅ Conflict agent response: {response[:200]}...")

#     return response
