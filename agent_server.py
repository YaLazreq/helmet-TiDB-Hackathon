from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import asyncio
import logging
import traceback
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class LocationData(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    place_id: str = ""
    rating: float = 0.0
    types: list[str] = []

class MapsResponse(BaseModel):
    topic: str
    description: str
    answer: list[str]
    source: list[str]
    tools_used: list[str]
    locations: list[LocationData] = []


# Global variables to store the agent setup
agent_executor = None
client = None


async def initialize_agent():
    global agent_executor, client

    if agent_executor is not None:
        return agent_executor

    logger.info("Initializing MCP client and agent...")

    client = MultiServerMCPClient(
        {
            "api-server": {
                "url": "http://localhost:8080/mcp",
                "transport": "streamable_http",
            },
        },
    )

    tools = await client.get_tools(server_name="api-server")
    logger.info("Retrieved %d tools from 'api-server'", len(tools))

    model = ChatAnthropic(
        model_name="claude-sonnet-4-20250514",
        timeout=60,
    )

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

    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
    )

    logger.info("Agent initialized successfully")
    return agent_executor


@app.post("/agent")
async def query_agent(request: QueryRequest):
    try:
        executor = await initialize_agent()

        logger.info(f"Processing query: {request.query}")

        raw_response = await executor.ainvoke(
            {
                "query": request.query,
            }
        )

        logger.info("Agent execution completed")
        logger.info(f"Raw response: {raw_response}")

        # Extract the actual output from the agent response
        if isinstance(raw_response, dict) and "output" in raw_response:
            output = raw_response["output"]
            # Handle case where output is a list of content objects
            if isinstance(output, list):
                output_text = ""
                for item in output:
                    if isinstance(item, dict) and "text" in item:
                        output_text += item["text"]
                    else:
                        output_text += str(item)
            else:
                output_text = str(output)
        else:
            output_text = str(raw_response)

        # Extract tools used and location data from intermediate steps
        tools_used = []
        locations = []
        
        if isinstance(raw_response, dict) and "intermediate_steps" in raw_response:
            for step in raw_response["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) >= 1:
                    # Extract tool name from the agent action
                    if hasattr(step[0], "tool"):
                        tools_used.append(step[0].tool)
                    elif hasattr(step[0], "name"):
                        tools_used.append(step[0].name)
                    
                    # Extract location data from tool results
                    if len(step) >= 2 and step[1]:
                        tool_result = step[1]
                        try:
                            # Try to parse JSON result from tools
                            import json
                            if isinstance(tool_result, str):
                                result_data = json.loads(tool_result)
                            else:
                                result_data = tool_result
                            
                            # Extract locations based on common Google Maps API response structure
                            if isinstance(result_data, dict):
                                # Handle places_nearby, places_search results
                                if "results" in result_data:
                                    for place in result_data["results"][:10]:  # Limit to 10 places
                                        if "geometry" in place and "location" in place["geometry"]:
                                            location_data = {
                                                "name": place.get("name", "Unknown"),
                                                "address": place.get("vicinity", place.get("formatted_address", "")),
                                                "lat": place["geometry"]["location"]["lat"],
                                                "lng": place["geometry"]["location"]["lng"],
                                                "place_id": place.get("place_id", ""),
                                                "rating": place.get("rating", 0.0),
                                                "types": place.get("types", [])
                                            }
                                            locations.append(location_data)
                                
                                # Handle geocode results
                                elif "results" in result_data and result_data["results"]:
                                    for geocode_result in result_data["results"][:5]:  # Limit to 5 results
                                        if "geometry" in geocode_result:
                                            location_data = {
                                                "name": geocode_result.get("formatted_address", "Location"),
                                                "address": geocode_result.get("formatted_address", ""),
                                                "lat": geocode_result["geometry"]["location"]["lat"],
                                                "lng": geocode_result["geometry"]["location"]["lng"],
                                                "place_id": geocode_result.get("place_id", ""),
                                                "rating": 0.0,
                                                "types": geocode_result.get("types", [])
                                            }
                                            locations.append(location_data)
                        except Exception as e:
                            logger.debug(f"Could not parse location data from tool result: {e}")
                            continue

        # Try to parse the structured response
        try:
            parser = PydanticOutputParser(pydantic_object=MapsResponse)
            parsed_response = parser.parse(output_text)
            response_dict = parsed_response.model_dump()
            # Ensure tools_used contains only strings and add locations
            response_dict["tools_used"] = tools_used
            response_dict["locations"] = locations
            return response_dict
        except Exception as parse_error:
            logger.warning(f"Could not parse structured response: {parse_error}")
            # Fallback to a simple format
            return {
                "topic": "Maps Query Response",
                "description": output_text,
                "answer": [],
                "source": [],
                "tools_used": tools_used,
                "locations": locations,
            }

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3001)
