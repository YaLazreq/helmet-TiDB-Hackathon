from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import asyncio
import os
from server.services.logger_init import logger


# class MapsResponse(BaseModel):
#     topic: str
#     description: str
#     source: list[str]
#     tools_used: list[str]


# async def main():
#     logger.info("Starting MCP client...")
#     # client = MultiServerMCPClient(
#     #     {
#     #         "api-server": {
#     #             "url": "http://localhost:8080/mcp",
#     #             "transport": "streamable_http",
#     #         },
#     #     },
#     # )
#     # tools = await client.get_tools(server_name="api-server")

#     model = ChatAnthropic(
#         model_name="claude-sonnet-4-20250514",
#         timeout=60,
#     )  # .with_fallbacks([ChatXAI(model="grok-3-mini", timeout=60)])

#     parser = PydanticOutputParser(pydantic_object=MapsResponse)

#     prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 "system",
#                 """
#                 You are a helpful assistant that provides information about:
#                     - maps
#                     - locations
#                     - geocoding
#                     - places
#                     - directions
#                     - points of interest

#                 CRITICAL RULES:
#                     - If you don't have access to real-time data or tools, explicitly say so
#                     - Never claim to use tools that aren't available to you
#                     - If you're unsure about information, clearly state your uncertainty
#                     - Distinguish between general knowledge and real-time/precise data
#                     - When providing estimates, clearly label them as estimates
#                     - If you cannot provide accurate information, say "I don't know" or "I cannot access that information"

#                 Wrap the output in this format and provide no other text:\n{format_instructions}

#             """,
#             ),
#             ("placeholder", "{chat_history}"),
#             ("human", "{query}"),
#             ("placeholder", "{agent_scratchpad}"),
#         ]
#     ).partial(format_instructions=parser.get_format_instructions())

#     agent = create_tool_calling_agent(model, tools, prompt)
#     agent_executor = AgentExecutor(
#         agent=agent,
#         tools=tools,
#         verbose=True,
#     )
#     query = input("Hey, what would you like to know? ")

#     # return raw_response


# asyncio.run(main())
