# mcp_server.py
import asyncio
from typing import Any, Dict, List, Optional
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from src.config.llm_init import model

# Global MCP client + cached tools
api_mcp_client: MultiServerMCPClient | None = None
api_mcp_tools = None
_MCP_SERVER_KEY = "api-server"


async def connect_api_mcp():
    """Initialize API MCP client once and fetch tools."""
    global api_mcp_client, api_mcp_tools
    if api_mcp_client is not None and api_mcp_tools is not None:
        return api_mcp_client, api_mcp_tools

    print("🔄 Connecting to API MCP server...")
    api_mcp_client = MultiServerMCPClient(
        {
            _MCP_SERVER_KEY: {
                "transport": "streamable_http",
                "url": "http://44.211.71.81:8080/mcp",
            }
        }
    )
    print("✅ Connected to API MCP server")

    print("🔄 Fetching API MCP tools...")
    tools_result = await api_mcp_client.get_tools()

    return api_mcp_client, api_mcp_tools
