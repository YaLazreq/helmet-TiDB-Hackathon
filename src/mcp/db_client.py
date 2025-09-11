# mcp_server.py
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool


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

    return db_mcp_client, db_mcp_tools, db_mcp_tools_for_prompt


def get_db_mcp_tools(tool_names=None):
    """
    Get DB MCP tools if already connected

    Args:
        tool_names (list, optional): List of specific tool names to return.
                                   If None, returns all tools.
                                   Example: ['get_users', 'create_task']

    Returns:
        list: List of requested MCP tools
    """
    global db_mcp_tools
    if db_mcp_tools is None:
        print("❌ DB MCP tools not initialized yet.")
        return []

    # If no specific tools requested, return all
    if tool_names is None:
        return db_mcp_tools

    # Filter tools by name
    filtered_tools = []
    for tool in db_mcp_tools:
        if tool.name in tool_names:
            filtered_tools.append(tool)

    # Check if all requested tools were found
    found_tool_names = [tool.name for tool in filtered_tools]
    missing_tools = [name for name in tool_names if name not in found_tool_names]

    if missing_tools:
        print(f"⚠️ Warning: Requested tools not found: {missing_tools}")
        print(f"Available tools: {[tool.name for tool in db_mcp_tools]}")

    return filtered_tools
