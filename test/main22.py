# from browser_use.llm import ChatOpenAI
# # from browser_use import Agent, ChatAnthropic

# Import relevant functionality
from importlib import metadata
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

load_dotenv()

# Create the agent
# memory = MemorySaver()
# model = init_chat_model("anthropic:claude-sonnet-4-20250514")
# search = TavilySearch(max_results=2)
# tools = [search]
# config = {"configurable": {"thread_id": "abc123"}}


#
# Initialize the AgentExecutor   
#

# response = agent_executor.invoke({"messages": [input_message]})

async def main():
    input_message = {"role": "user", "content": "What's my name ?"}
    agent_executor = create_react_agent(model, tools, checkpointer=memory)

    for step, metadata in agent_executor.stream(
    {"messages": [input_message]}, config,stream_mode="messages"):
        if metadata["langgraph_node"] == "agent" and (text := step.text()):
            print(text, end="|")







# # Use the agent
# config = {"configurable": {"thread_id": "abc123"}}

# input_message = {
#     "role": "user",
#     "content": "Hi, I'm Bob and I live in SF.",
# }
# for step in agent_executor.stream(
#     {"messages": [input_message]}, config, stream_mode="values"
# ):
#     step["messages"][-1].pretty_print()


