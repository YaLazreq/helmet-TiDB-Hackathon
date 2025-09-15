import asyncio
from src.config.llm_init import model
from server.services.logger_init import logger
import pretty_print_message as ppm

from src.mcp.db_client import connect_db_mcp
from src.mcp.api_client import connect_api_mcp


async def run():
    await connect_db_mcp()
    # await connect_api_mcp()

    from src.agents.supervisor import supervisor

    # TODO: Move this to a route handler
    # Consider: supervisor.invoke() for single response or supervisor.stream() for streaming
    message_content = "[User ID: 2 - Message Date: Sun. 10 September 2025]: Can you assign me in another task please?"

    result = await supervisor.ainvoke(
        input={
            "messages": [
                {
                    "role": "user",
                    "content": message_content,
                }
            ],
        },
        config={
            "run_name": "agent_supervisor",
            "tags": ["debug"],
            "recursion_limit": 100,
        },
    )

    return result
