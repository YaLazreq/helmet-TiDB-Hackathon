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
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MapsResponse(BaseModel):
    topic: str
    description: str
    source: list[str]
    tools_used: list[str]


async def main():
    logger.info("Starting MCP client...")
    client = MultiServerMCPClient(
        {
            "api-server": {
                "url": "http://localhost:8080/mcp",
                "transport": "streamable_http",
            },
        },
    )
    logger.debug("MCP client created: %s", client)

    logger.info("Fetching tools from server 'api-server'...")
    tools = await client.get_tools(server_name="api-server")
    logger.info("Retrieved %d tools from  'api-server'", len(tools))
    # logger.info("Tools: %s", tools)

    logger.info("Initializing ChatAnthropic model...")
    model = ChatAnthropic(
        model_name="claude-sonnet-4-20250514",
        timeout=60,
    )  # .with_fallbacks([ChatXAI(model="grok-3-mini", timeout=60)])
    logger.debug("Model initialized: %s", model)

    logger.info("Setting up output parser...")
    parser = PydanticOutputParser(pydantic_object=MapsResponse)
    logger.debug("Parser created: %s", parser)

    logger.info("Building prompt template...")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                You are a helpful assistant that provides information about:
                    - maps
                    - locations
                    - geocoding
                    - places
                    - directions
                    - points of interest
                
                CRITICAL RULES:
                    - If you don't have access to real-time data or tools, explicitly say so
                    - Never claim to use tools that aren't available to you
                    - If you're unsure about information, clearly state your uncertainty
                    - Distinguish between general knowledge and real-time/precise data
                    - When providing estimates, clearly label them as estimates
                    - If you cannot provide accurate information, say "I don't know" or "I cannot access that information"
            
                Wrap the output in this format and provide no other text:\n{format_instructions}

            """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    ).partial(format_instructions=parser.get_format_instructions())
    logger.debug("Prompt template created")

    logger.info("Creating tool-calling agent...")
    agent = create_tool_calling_agent(model, tools, prompt)
    logger.debug("Agent created: %s", agent)

    logger.info("Creating AgentExecutor...")
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )
    logger.info("AgentExecutor ready")

    query = input("Hey, what would you like to know? ")
    logger.info("User query received")

    logger.info("Invoking agent executor...")
    try:
        raw_response = await agent_executor.ainvoke(
            {
                "query": query,
            }
        )
        logger.info("Agent executor returned a response")
        logger.debug("Raw response: %s", raw_response)
    except Exception:
        logger.exception("Agent execution failed")
        return None

    return raw_response


asyncio.run(main())
