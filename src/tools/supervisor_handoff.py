from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from langgraph.graph import MessagesState
from langgraph.types import Command, Send


def create_task_description_handoff_tool(
    *, agent_name: str, description: str | None = None
):
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
        # this is populated by the supervisor LLM
        task_description: Annotated[
            str,
            "Description of what the next agent should do, including all of the relevant context.",
        ],
        # these parameters are ignored by the LLM
        state: Annotated[MessagesState, InjectedState],
    ) -> Command:
        task_description_message = {"role": "user", "content": task_description}
        agent_input = {**state, "messages": [task_description_message]}
        return Command(
            goto=[Send(agent_name, agent_input)],
            graph=Command.PARENT,
        )

    return handoff_tool


################
### Handoffs ###
################

assign_to_planning_agent_with_description = create_task_description_handoff_tool(
    agent_name="planning_agent",
    description="Assign task to a planning agent that specializes in project planning, scheduling, resource allocation, timeline creation, and strategic roadmap development.",
)

assign_to_conflict_agent_with_description = create_task_description_handoff_tool(
    agent_name="conflict_agent",
    description="Assign task to a conflict agent that specializes in identifying, analyzing, and resolving conflicts in project schedules, resource allocations, and task dependencies.",
)

# assign_to_team_builder_agent_with_description = create_task_description_handoff_tool(
#     agent_name="team_builder_agent",
#     description="Assign task to a team builder agent that specializes in intelligent worker-task matching and team formation.",
# )

assign_to_notifier_agent_with_description = create_task_description_handoff_tool(
    agent_name="notifier_agent",
    description="Assign task to a notifier agent that specializes in sending notifications and alerts at the supervisor workflow.",
)

assign_to_executor_agent_with_description = create_task_description_handoff_tool(
    agent_name="executor_agent",
    description="Assign task to an executor agent that specializes in executing database operations - creating and updating tasks and users in the system.",
)
