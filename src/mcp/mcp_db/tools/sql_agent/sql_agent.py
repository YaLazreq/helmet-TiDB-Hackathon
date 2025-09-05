from mcp_init import mcp

from langchain_anthropic import ChatAnthropic
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_types import AgentType
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from urllib.parse import quote_plus

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
llm = ChatAnthropic(model="claude-sonnet-4-20250514", anthropic_api_key=api_key)

def create_database_connection():
    
    host = os.getenv('TIDB_HOST')
    port = int(os.getenv('TIDB_PORT', 4000))
    user = os.getenv('TIDB_USER')
    password = os.getenv('TIDB_PASSWORD')
    database = os.getenv('TIDB_DATABASE')
    ssl_ca = os.getenv('TIDB_SSL_CA', './ca_tidb.pem')
    
    password_encoded = quote_plus(password)
    
    connection_string = f"mysql+pymysql://{user}:{password_encoded}@{host}:{port}/{database}"
    
    engine = create_engine(
        connection_string,
        connect_args={
            'ssl': {
                'ssl_ca': ssl_ca,
                'ssl_disabled': False,
                'ssl_verify_cert': True,
                'ssl_verify_identity': False
            }
        },
        echo=False
    )
    
    try:
        with engine.connect() as conn:
            print("✅ Connexion SQLAlchemy à TiDB réussie!")
    except Exception as e:
        print(f"❌ Erreur de connexion SQLAlchemy: {e}")
        raise
    
    db = SQLDatabase(engine)
    
    return db

def create_sql_agent_instance():

    db = create_database_connection()

    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False,
        handle_parsing_errors=True,
        max_iterations=10,
        max_execution_time=60
    )
    
    return agent_executor

@mcp.tool()
def sql_agent(query: str) -> str:
    """
    
    Exécute une requête SQL via l'agent SQL. Pour GET tout ce qu'on veut récupérer dans la base de données.
    """

    try:
        agent = create_sql_agent_instance()
                
        response = agent.invoke({"input": query})
        return response['output']
        
    except Exception as e:
        return f"❌ Erreur lors de l'exécution de l'agent SQL: {str(e)}"
