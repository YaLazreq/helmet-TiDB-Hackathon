import asyncio
from src.config.llm_init import model
from server.services.logger_init import logger
import pretty_print_message as ppm

from src.mcp.db_client import connect_db_mcp
from src.mcp.api_client import connect_api_mcp


async def main():
    await connect_db_mcp()
    # await connect_api_mcp()

    # Import after initialization
    from src.mcp.db_client import db_mcp_tools, db_mcp_tools_for_prompt

    # from src.mcp.api_client import api_mcp_tools

    # if db_mcp_tools is None or api_mcp_tools is None:
    if db_mcp_tools is None:
        logger.error("MCP tools not initialized properly.")
        return
    else:
        logger.info(f"✅ {len(db_mcp_tools)} DB MCP tool(s) cached")
        # logger.info(f"✅ {len(api_mcp_tools)} API MCP tool(s) cached")

    # from langgraph.prebuilt import create_react_agent
    # from src.mcp.db_client import get_db_mcp_tools
    # from src.agents.conflict import conflict_agent_as_tool
    # from src.agents.notifier import create_notifier_agent

    # t = create_react_agent(
    #     model=model,
    #     tools=[
    #         *get_db_mcp_tools(["get_users_for_context", "get_tasks"]),
    #     ],
    #     prompt="Récupère ce que demande l'humain",
    #     name="planning_agent",
    # )

    # result = t.invoke(
    #     {
    #         "messages": [
    #             (
    #                 "human",
    #                 "Installation mobilier sur mesure Bureau A202",
    #             )
    #         ]
    #     }
    # )

    # response = result["messages"][-1].content

    # print(response)

    from src.agents.supervisor import supervisor

    final_chunk = None
    for chunk in supervisor.stream(
        input={
            "messages": [
                {
                    "role": "user",
                    "content": "[User ID: 3 - Message Date: Sun. 10 September 2025]: Can you give me the list of tasks planned for this week in the RETAIL zone?",
                    # "content": "[User ID: 3 - Message Date: Sun. 10 September 2025]: We have a problem, the Restaurant Foundation Excavation on the RETAIL Building is delayed.",
                    # Il faut que ce soit fait avant vendredi 12 septembre 2025. Merci !
                    # "content": "Changer le numéroe de téléphone du travailleur Yanis Dupont à 0606060606",
                }
            ],
        },
        # Increase from default 25
        config={
            "run_name": "agent_supervisor",
            "tags": ["debug"],
            "recursion_limit": 100,
        },
        subgraphs=True,
    ):
        ppm.pretty_print_messages(chunk, last_message=True)
        final_chunk = chunk

    # Handle the case where chunk might be a tuple (namespace, update)
    if isinstance(final_chunk, tuple):
        _, update = final_chunk
        if "supervisor" in update:
            final_message_history = update["supervisor"]["messages"]
        else:
            final_message_history = None
    else:
        final_message_history = (
            final_chunk["supervisor"]["messages"]
            if final_chunk and "supervisor" in final_chunk
            else None
        )


if __name__ == "__main__":
    asyncio.run(main())
