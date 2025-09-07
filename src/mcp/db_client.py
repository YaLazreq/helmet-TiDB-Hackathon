# mcp_server.py
import asyncio

# from typing import Any, Dict, List, Optional
# from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

# from src.config.llm_init import model
# from langchain_mcp_adapters.tools import load_mcp_tools


class AsyncToSyncTool(BaseTool):
    """Wrapper to make async MCP tools work synchronously with LangGraph"""

    async_tool: BaseTool

    def __init__(self, async_tool: BaseTool):
        super().__init__(
            name=async_tool.name,
            description=async_tool.description,
            args_schema=async_tool.args_schema,
            async_tool=async_tool,
        )

    def _run(self, **kwargs) -> str:
        """Convert async call to sync using asyncio.run"""
        # LangChain tools expect input as a dictionary
        input_data = kwargs

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, we can use asyncio.run
            return asyncio.run(self.async_tool.ainvoke(input_data))
        else:
            # Event loop is running, we need to run in a thread
            import concurrent.futures

            def run_async():
                return asyncio.run(self.async_tool.ainvoke(input_data))

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                return future.result()


# Global MCP client + cached tools
db_mcp_client: MultiServerMCPClient | None = None
db_mcp_tools: list[BaseTool] = []
db_mcp_tools_for_prompt = []


async def connect_db_mcp():
    """Initialize DB MCP client once and fetch tools."""
    global db_mcp_client, db_mcp_tools, db_mcp_tools_for_prompt
    if (
        db_mcp_client is not None
        and db_mcp_tools is not None
        and db_mcp_tools_for_prompt is not None
    ):
        return db_mcp_client, db_mcp_tools, db_mcp_tools_for_prompt

    print("🔄 Connecting to DB MCP server...")

    db_mcp_client = MultiServerMCPClient(
        {
            "db-server": {
                "transport": "streamable_http",
                "url": "http://localhost:8080/mcp",
            }
        }
    )
    print("✅ Connected to DB MCP server")

    print("🔄 Fetching DB MCP tools...")
    tools_result = await db_mcp_client.get_tools()

    # Wrap async tools to make them sync-compatible
    db_mcp_tools = [AsyncToSyncTool(tool) for tool in tools_result]

    db_mcp_tools_for_prompt = "\n".join(
        [
            f"- {tool.name}: {tool.description.split('.')[0].strip()}."
            for tool in db_mcp_tools
        ]
    )
    print(db_mcp_tools_for_prompt)
    print("✅ Fetching Success...")

    # toto_agent = create_react_agent(
    #     model=model,
    #     tools=[*db_mcp_tools],
    #     prompt="Tu as accès aux outils de la base de données. Tu peux modifier n'importe quel row. ",
    #     name="toto_agent",
    # )

    # res = await toto_agent.ainvoke(
    #     {
    #         "messages": [
    #             {
    #                 "role": "user",
    #                 "content": "change le numéro de téléphone du travailleur Yanis Dupont (ID: 2) à 0606060606",
    #             }
    #         ]
    #     },
    # )

    # print("🤖 >", res["messages"][-1].content)

    return db_mcp_client, db_mcp_tools, db_mcp_tools_for_prompt


def get_db_mcp_tools():
    """Get DB MCP tools if already connected"""
    global db_mcp_tools
    if db_mcp_tools is None:
        print("❌ DB MCP tools not initialized yet.")
    return db_mcp_tools


# def main():
#     asyncio.run(connect_db_mcp())


# if __name__ == "__main__":
#     main()
