from dotenv import load_dotenv
import asyncio
import os

from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model


from server.services.logger_init import logger
import agents.math_agent as math_tools
import agents.supervisor_manager as sm
import pretty_print_message as ppm


load_dotenv()
init_chat_model()
model = ChatAnthropic(
    model_name="claude-sonnet-4-20250514",
    timeout=60,
)  # .with_fallbacks([ChatXAI(model="grok-3-mini", timeout=60)])

math_agent = create_react_agent(
    model=model,
    tools=[math_tools.add, math_tools.subtract, math_tools.multiply],
    name="math_agent",
    prompt="You are a math expert. Always use one tool at a time.",
)

import agents.research_agent as research_tools

research_agent = create_react_agent(
    model=model,
    tools=[research_tools.web_search],
    name="research_agent",
    prompt="You are a world class researcher with access to web search. Do not do any math",
)

# Créer le workflow superviseur complet
from langgraph.graph import StateGraph, START
from langgraph.graph.message import MessagesState

supervisor_agent_with_description = create_react_agent(
    model=model,
    tools=[
        sm.assign_to_research_agent_with_description,
        sm.assign_to_math_agent_with_description,
    ],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- a research agent. Assign research-related tasks to this assistant\n"
        "- a math agent. Assign math-related tasks to this assistant\n"
        "Assign work to one agent at a time, do not call agents in parallel.\n"
        "Do not do any work yourself."
    ),
    name="supervisor",
)

supervisor_with_description = (
    StateGraph(MessagesState)
    .add_node(
        supervisor_agent_with_description, destinations=("research_agent", "math_agent")
    )
    .add_node(research_agent)
    .add_node(math_agent)
    .add_edge(START, "supervisor")
    .add_edge("research_agent", "supervisor")
    .add_edge("math_agent", "supervisor")
    .compile()
)

from langchain_core.messages import HumanMessage

for chunk in supervisor_with_description.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "find US and New York state GDP in 2024. what % of US GDP was New York state?",
            }
        ]
    },
    subgraphs=True,
):
    ppm.pretty_print_messages(chunk, last_message=True)

final_message_history = chunk["supervisor"]["messages"]

# for chunk in math_agent.stream(
#     {"messages": [{"role": "user", "content": "What is 25 multiplied by 4?"}]}
# ):
#     ppm.pretty_print_messages(chunk)


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
