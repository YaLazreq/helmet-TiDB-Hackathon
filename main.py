import asyncio
from server.services.logger_init import logger
import pretty_print_message as ppm

from src.mcp.db_client import connect_db_mcp
from src.mcp.api_client import connect_api_mcp


async def main():
    await connect_db_mcp()
    # await connect_api_mcp()

    # Import after initialization
    from src.mcp.db_client import db_mcp_tools

    # from src.mcp.api_client import api_mcp_tools

    # if db_mcp_tools is None or api_mcp_tools is None:
    if db_mcp_tools is None:
        logger.error("MCP tools not initialized properly.")
        return
    else:
        logger.info(f"✅ {len(db_mcp_tools)} DB MCP tool(s) cached")
        # logger.info(f"✅ {len(api_mcp_tools)} API MCP tool(s) cached")

    from src.agents.supervisor_002 import supervisor

    final_chunk = None
    for chunk in supervisor.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Change the time for installing security cameras to 3 p.m. the next day",
                    # "content": "Changer le numéroe de téléphone du travailleur Yanis Dupont à 0606060606",
                }
            ]
        },
        config={"run_name": "agent_supervisor", "tags": ["debug"]},
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
