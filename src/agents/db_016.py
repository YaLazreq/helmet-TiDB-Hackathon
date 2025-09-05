import os, asyncio
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv
from src.config.llm_init import model


# # class ToolLogger(BaseCallbackHandler):
# #     def on_tool_start(self, serialized, input_str, **kwargs):
# #         print(f"[Client] Using tool {serialized['name']} with args: {input_str}")


# async def main():
#     user_prompt = input("👤 > ")

#     client = MultiServerMCPClient(
#         {
#             "mcp": {
#                 "transport": "streamable_http",
#                 "url": "http://34.205.37.141:8080/mcp",
#             }
#         }
#     )

#     tools = await client.get_tools()

#     planning_agent = create_react_agent(
#         model=model,
#         tools=tools,
#         prompt="",
#         name="planning_agent",
#     )

# load_dotenv()

# api_key = os.getenv("ANTHROPIC_API_KEY")

# llm = model

# agent = create_react_agent(llm, tools)

# res = await agent.ainvoke(
#     {"messages": [{"role": "user", "content": user_prompt}]},
#     config={"callbacks": [ToolLogger()]},
# )
# print("🤖 >", res["messages"][-1].content)


# # if __name__ == "__main__":
# #     asyncio.run(main())

# import asyncio
# from langchain.agents import AgentExecutor
# from langgraph.prebuilt import create_react_agent
# from langchain_mcp_adapters.client import MultiServerMCPClient

# from src.config.llm_init import model

# prompt = """
#     You are the DB Agent (16) - you create and update rows in the construction site database using MCP SERVER tools.
# """


# async def db_agent_creation():
#     """
#     Create and Update rows in the database.
#     Receive natural language request from other agents, and change the database accordingly.
#     Uses MCP SERVER to get the tools dynamically.
#     """
#     print("🔄 Creating DB Agent...")
#     try:
#         print("🔄 Fetching tools from MCP SERVER...")
#         client = MultiServerMCPClient(
#             {
#                 "mcp": {
#                     "transport": "streamable_http",
#                     "url": "http://34.205.37.141:8080/mcp",
#                 }
#             }
#         )
#         print("✅ Connected to MCP SERVER")

#         tools = await client.get_tools()
#         # print(tools)
#         database_agent = create_react_agent(
#             model,
#             tools=tools,
#             prompt=prompt,
#             name="db_agent",
#         )
#         return database_agent
#     except Exception as e:
#         print(f"❌ Erreur lors de la création de l'agent DB: {str(e)}")
#         return None


# async def db_agent(natural_language_request: str) -> str:
#     """
#     Receive natural language request from other agents and update the database.
#     Only create and Update rows in the database
#     """

#     print(f"🔍 DB_AGENT - Requête reçue: {natural_language_request}")

#     try:
#         # Utiliser asyncio.run pour appeler la fonction async
#         print("🔄 DB_AGENT - Création de l'agent...")
#         agent = await db_agent_creation()

#         if agent is None:
#             print("❌ DB_AGENT - Agent creation failed")
#             return "❌ Impossible de créer l'agent DB"

#         res = await agent.ainvoke(
#             {"messages": [{"role": "user", "content": natural_language_request}]},
#         )

#         print(f"🤖 DB_AGENT - Réponse: {res['messages'][-1].content}")

#         return res["messages"][-1].content

#     except Exception as e:
#         print(f"💥 DB_AGENT - Exception: {str(e)}")
#         return f"❌ Erreur lors de l'exécution de l'agent DB: {str(e)}"


# if __name__ == "__main__":
#     asyncio.run(db_agent("Récupère tous les utilisateurs"))
