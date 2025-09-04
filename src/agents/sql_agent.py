from server.services.fastmcp_init import mcp
from src.config.llm_init import model
from src.config.db import create_database_connection

from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv

load_dotenv()

# SQL Agent Prompt
prompt = """
    You are a SQL expert working with a TiDB (MySQL-compatible) database for a construction site management system.

    IMPORTANT INSTRUCTIONS:
    1. ALWAYS start by exploring the database schema
    2. NEVER assume table names - always check what tables actually exist
    3. Use proper MySQL syntax for TiDB
    4. Be precise with column names and data types

    WORKFLOW:
    1. First, see available tables
    2. Then understand the schema
    3. Only then write your actual query

    CRITICAL: You should receive natural language requests, NOT SQL code!
    If you receive a direct SQL query (starting with SELECT, INSERT, etc.), 
    respond with: {"message": "Please provide a natural language description of what data you need instead of SQL code."}

    CRITICAL: RETURN JSON ONLY
    - Always be explicit about empty results
    - Don't suggest endless alternative searches if core data doesn't exist
    - After 3 failed searches, conclude that the requested data doesn't exist

    Remember: This database may have custom table structures, so always verify the schema first!
    Remember: It's better to say "data not found" than to search indefinitely!
"""

# Singleton pour l'agent SQL
# _sql_agent_instance = None


def create_sql_agent_instance():
    global _sql_agent_instance

    # Si l'agent existe déjà, le retourner
    # if _sql_agent_instance is not None:
    #     return _sql_agent_instance

    db = create_database_connection()

    agent_executor = create_sql_agent(
        llm=model,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=60,
    )

    # Sauvegarder l'agent pour réutilisation
    # _sql_agent_instance = agent_executor

    return agent_executor


@mcp.tool()
def sql_agent(natural_language_request: str) -> str:
    """
    Receive natural language request from other agents, convert it to SQL and execute it via SQL Agent.
    Execute an SQL Request via SQL Agent for GET everything we want to retrieve from the database.
    """

    try:
        agent = create_sql_agent_instance()

        response = agent.invoke({"input": natural_language_request})
        return response["output"]

    except Exception as e:
        return f"❌ Erreur lors de l'exécution de l'agent SQL: {str(e)}"
