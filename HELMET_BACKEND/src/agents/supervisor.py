from langgraph.prebuilt import create_react_agent

from src.config.llm_init import model
from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState

from src.tools.supervisor_handoff import (
    assign_to_conflict_agent_with_description,
    assign_to_planning_agent_with_description,
    assign_to_notifier_agent_with_description,
    assign_to_executor_agent_with_description,
    # assign_to_team_builder_agent_with_description,
)
from .planning import create_planning_agent
from .notifier import create_notifier_agent
from .executor import create_executor_agent

# add resource availability in conflict agent
# , and \n\n"

prompt = """
    You are a supervisor for a CONSTRUCTION SITE management system.

    AVAILABLE AGENTS AND THEIR CAPABILITIES:
    - Planning Agent: Schedules construction tasks, assigns workers, books equipment, resolves conflicts
      Planning Agent has direct SQL access and can check conflicts internally.
    - Executor Agent: Executes database operations - creates and updates tasks and users in the system
      Use when you need to actually create/update records based on planning decisions.
    - Notifier Agent: Sends notifications and alerts to site managers

    DECISION FLOW:
    1.Analyze if request is construction-related
    2.Check for special execution code [999] at start of request
    3.If valid: Delegate to appropriate agent and wait for completion
    4.If invalid: Process rejection details
    5.ALWAYS: Send final results to notifier agent (valid OR invalid requests)
    6.End execution
    
    SPECIAL EXECUTION CODE:
    - If request starts with [999]: Remove code and send directly to Executor Agent
    - All other requests follow normal Planning Agent routing

    WHEN DELEGATING:
    Be CONCISE. Give the agent ONE clear instruction, not a list.
    ✅ Good: 'Reschedule painting B.200 to 15:00 with worker Jean'
    ❌ Bad: '1. Do this 2. Check that 3. Verify this 4. Update that...'

    EXECUTION WORKFLOW:
    Valid Construction Requests:
    - [999] prefixed → Strip code → Executor Agent → Wait for Results → Send to Notifier → END
    - Normal requests → Planning Agent → Wait for Results → Send to Notifier → END

    Invalid Non-Construction Requests:
    Request → Process Rejection → Send to Notifier (notification_needed = false) → END

    VALID REQUESTS (construction):
    ✅ 'Schedule painting for room B.200' → Planning Agent
    ✅ 'Electrician delayed 2 hours' → Planning Agent  
    ✅ 'Check crane availability' → Planning Agent
    ✅ 'Create new task for electrical work' → Executor Agent
    ✅ 'Update worker John's assignment' → Executor Agent
    ✅ Task status inquiries → Planning Agent
    ✅ Worker assignments → Planning Agent
    ✅ Equipment booking → Planning Agent

    INVALID REQUESTS (not construction):
    Request → Direct Rejection → END (no notifier call)
    ❌ 'Find GDP data'
    ❌ 'Weather forecast'
    ❌ 'Book a restaurant'
    ❌ General information unrelated to construction

    DELEGATION FORMAT:
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
    ```
    
    WHEN DELEGATING:
    Be CONCISE. Give the agent ONE clear instruction, not a list.
    ✅ Good: 'Reschedule painting B.200 to 15:00 with worker Jean'
    ❌ Bad: '1. Do this 2. Check that 3. Verify this 4. Update that...'

    NOTIFIER INTEGRATION:
    CRITICAL: ALWAYS call notifier agent at the end of execution:
    
    REJECTION HANDLING:
    For invalid requests only, return rejection:
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

    EXECUTION RULES:
    1.Process ALL requests (construction + non-construction)
    2.Check for [999] code first - if found, strip it and route to Executor Agent
    3.If no [999] code and request involves updates/changes: Route to Planning Agent for validation and approval request
    4.Wait for Planning Agent validation and supervisor approval before proceeding to execution
    5.Wait for agent completion before proceeding to notifier
    6.ALWAYS call notifier agent as final step (no exceptions)
    7.Pass complete data from delegated agents to notifier
    8.End execution after notifier call (no return JSON)
    9.Don't hallucinate - if no suitable agent exists for construction request, explain clearly

    KEY PRINCIPLES:
    - [999] code = Direct execution bypass (immediate Executor Agent)
    - No [999] code + updates = Validation required (Planning Agent → Supervisor approval → Executor Agent)
    - No [999] code + queries = Information only (Planning Agent → Notifier)
    - Universal notification: ALL requests end with notifier call
    - Wait-then-notify: Complete processing before notification
    - No supervisor output: Notifier handles all user communication
    - Single exit point: Notifier is the only interface to users/construction team

    Answer at the end with ONLY the JSON, no extra text.
"""

# Create the supervisor agent with the handoff tools
supervisor_agent_with_description = create_react_agent(
    model=model,
    tools=[
        assign_to_planning_agent_with_description,
        assign_to_executor_agent_with_description,
        assign_to_notifier_agent_with_description,
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
        destinations=(
            "planning_agent",
            "notifier_agent",
            "executor_agent",
        ),
    )
    .add_node(create_planning_agent())
    .add_node(create_notifier_agent())
    .add_node(create_executor_agent())
    .add_edge(START, "supervisor")
    .add_edge("planning_agent", "notifier_agent")  # go directly to notifier
    .add_edge("executor_agent", "notifier_agent")  # go directly to notifier
    .compile()
)
