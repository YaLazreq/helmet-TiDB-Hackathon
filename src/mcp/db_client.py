# mcp_server.py
import asyncio
from typing import Any, Dict, List, Optional
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from src.config.llm_init import model
from langchain_mcp_adapters.tools import load_mcp_tools


# Global MCP client + cached tools
db_mcp_client: MultiServerMCPClient | None = None
db_mcp_tools: list[BaseTool] = []


async def connect_db_mcp():
    """Initialize DB MCP client once and fetch tools."""
    global db_mcp_client, db_mcp_tools
    if db_mcp_client is not None and db_mcp_tools is not None:
        return db_mcp_client, db_mcp_tools

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
    db_mcp_tools = tools_result
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

    return db_mcp_client, db_mcp_tools


# def main():
#     asyncio.run(connect_db_mcp())


# if __name__ == "__main__":
#     main()
