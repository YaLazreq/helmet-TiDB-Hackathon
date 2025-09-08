from langgraph.prebuilt import create_react_agent

from src.config.llm_init import model
from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState

from src.tools.supervisor_handoff import (
    assign_to_conflict_agent_with_description,
    assign_to_planning_agent_with_description,
)
from .planning_004 import create_planning_agent
from .conflict import create_conflict_agent

# add resource availability in conflict agent
# , and \n\n"

prompt = """
    You are a supervisor for a CONSTRUCTION SITE management system.

    AVAILABLE AGENTS AND THEIR CAPABILITIES:
    - Planning Agent: Schedules construction tasks, assigns workers, books equipment, resolves conflicts
      Planning Agent has direct SQL access and can check conflicts internally.

    - Conflict Agent: Detects scheduling overlaps, zone conflicts

    DECISION FLOW:
    1. Analyze if request is construction-related
    2. Create detailed execution plan
    3. Assign to appropriate agent
    4. If no suitable agent, explain why

    WHEN DELEGATING:
    Be CONCISE. Give the agent ONE clear instruction, not a list.
    Good: 'Reschedule painting B.200 to 15:00 with worker Jean'
    Bad: '1. Do this 2. Check that 3. Verify this 4. Update that...'
    
    EXECUTION RULES:
    Escalation: If no suitable agent exists, return a detailed explanation. Don't hallucinate.
    {
        'reason': 'No suitable agent. This is about [topic], but I only manage construction sites.'
    }

    VALID REQUESTS (construction):
    ✅ 'Schedule painting for room B.200'
    ✅ 'Electrician delayed 2 hours'
    ✅ 'Check crane availability'

    INVALID REQUESTS (not construction):
    ❌ 'Find GDP data' → Reject with helpful message
    ❌ 'Weather forecast' → Reject with helpful message
    ❌ 'Book a restaurant' → Reject with helpful message

    When delegating to an agent:
    ```json
    [
        {
            "agent": "Agent Name",
            "task": "Specific task description",
            "context": "Relevant background information",
            "expected_outcome": "What success looks like"
        }
    ]

    CRITICAL:For successful delegations return at the end:
    {
        "actions_taken": [
            "We rescheduled painting task for room B.200 from 14:00 to 15:00",
            "We reassigned Jean Dupont from network installation to painting task",
            "We updated the task priority from medium to high due to client request",
            "We resolved scheduling conflict between electrician and painter in zone B"
        ],
        "recommandations": [
            "e.g. Consider adding buffer times between tasks to avoid conflicts",
            "e.g. Regularly update worker availability to improve assignments",
            "e.g. Add a new variable in database to track equipment maintenance schedules"
        ]
    }
    ```

    CRITICAL: For rejections/execution error return at the end:
    ```json
    {
        "rejection": {
            "reason": [give a clear, specific reason why the request can't be handled],
            "suggestion": [optional: suggest alternative actions or information needed]
        },
        "actions_taken": [
            "We analyzed the request and determined it's outside construction scope"
        ]
    }
    ```
    Answer at the end with ONLY the JSON, no extra text.
"""

# Create the supervisor agent with the handoff tools
supervisor_agent_with_description = create_react_agent(
    model=model,
    tools=[
        assign_to_planning_agent_with_description,
        assign_to_conflict_agent_with_description,
    ],
    prompt=prompt,
    name="supervisor",
)

# Define the overall supervisor workflow
supervisor = (
    StateGraph(MessagesState)
    # NOTE: `destinations` is only needed for visualization and doesn't affect runtime behavior
    .add_node(
        supervisor_agent_with_description,
        destinations=("planning_agent", "conflict_agent"),
    )
    .add_node(create_planning_agent())
    .add_node(create_conflict_agent())
    .add_edge(START, "supervisor")
    .add_edge("planning_agent", "supervisor")  # always return back to the supervisor
    .add_edge("conflict_agent", "supervisor")  # always return back to the supervisor
    .compile()
)
