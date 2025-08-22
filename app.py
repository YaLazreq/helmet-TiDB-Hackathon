from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
import tools.manager as t


class MapsResponse(BaseModel):
    topic: str
    description: str
    source: list[str]
    tools_used: list[str]


llm = ChatAnthropic(
    model_name="claude-sonnet-4-20250514",
    timeout=60,
).with_fallbacks([ChatXAI(model="grok-3-mini", timeout=60)])
parser = PydanticOutputParser(pydantic_object=MapsResponse)

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

# Define the tools to be used by the agent
tools = [
    t.distance_matrix_tool,
    t.places_nearby_tool,
    t.geocode_tool,
    t.reverse_geocode_tool,
]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)

query = input("What would you like to know? ")
raw_response = agent_executor.invoke(
    {
        "query": query,
    }
)


# safely extract the agent output text
outputs = raw_response.get("output", []) or []
if not outputs:
    raise ValueError("No output from agent")
