# from langchain_anthropic import ChatAnthropic
# from langgraph.prebuilt import create_react_agent
# from langchain_mcp_adapters.client import MultiServerMCPClient

# async def agent_db():

#     client = MultiServerMCPClient({
#         "mcp": {
#             "transport": "streamable_http",
#             "url": "http://98.84.19.198:8080/mcp"
#         }
#     })

#     tools = await client.get_tools()

#     llm = ChatAnthropic(model="claude-sonnet-4-20250514")

#     agent = create_react_agent(llm, tools)

#     return agent
