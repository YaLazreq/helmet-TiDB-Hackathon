# 🚧 TiDB Hackathon - Intelligent Task Management System

A multi-agent system using LangGraph for automated construction task management with TiDB database.

> Our insight was simple: What if construction sites possessed reflexion, an intelligent system capable of preventing cascade failures through real-time optimization? 
Helmet embodies this vision through an agentic architecture that transforms construction sites into self-organizing, continuously adaptive systems. By leveraging the voices of workers on the field, their real-time observations, concerns and insights, we feed this critical human intelligence to AI agents that can instantly reorganize the worksite based on what workers are reporting and provide a clear action plan to the construction site supervisor.

> This creates a dynamic feedback loop where field expertise directly drives intelligent orchestration,  automated resolutions completed in ~140 seconds. This enable the site to adapt and optimize in real-time as conditions change and challenges emerge.

## 🎯 Overview

This project implements an intelligent task management system for the construction industry, using:

- **TiDB** as a distributed vector database
- **LangGraph** for AI agent orchestration
- **MCP (Model Context Protocol)** for database integration
- **LangSmith** for monitoring and agent tracing

## ✨ Main Features

### 🤖 Intelligent Agents

- **Supervisor**: Central task orchestration and delegation
- **Planning**: Task planning and scheduling
- **Conflict**: Resource conflict detection and resolution
- **Notifier**: Automated notifications and alerts
- **Executor**: Task execution and tracking

### 🎲 Code Specialties

- **Multi-agent architecture** with LangGraph for complex workflows
- **Vector database** TiDB for semantic search
- **MCP protocol** for secure database interaction
- **Intelligent tracing** with LangSmith for real-time monitoring
- **RESTful API** with FastAPI for external integration
- **Multilingual support** in interactions

## 🚀 Installation and Configuration

### Use the project hosted

[Helmet Supervisor App Link](https://google.com)

[Helmet Worker App Link](https://google.com)

### Use locally

### Prerequisites

- Python 3.11+
- TiDB Cloud database (or local instance)
- LangSmith account for monitoring
- Anthropic (Claude) or XAI API key

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. TiDB Database Configuration

#### 2.1 Configure .env file

Create a `.env` file at the project root with your TiDB information:

```env
# TiDB Connection Settings
TIDB_HOST=your-tidb-host.tidbcloud.com
TIDB_PORT=4000
TIDB_USER=your-username.root
TIDB_PASSWORD=your-password
TIDB_DATABASE=your-database-name

# AI API Keys
ANTHROPIC_API_KEY=""

# LangSmith Configuration (for monitoring)
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=lsv2_pt_your-langsmith-key
LANGSMITH_PROJECT="your-project-name"
```

## 🐳 Running with Docker

### Build and run the application

```bash
# Build the Docker image
docker build -t helmet-tidb .

# Run the container with environment variables
docker run -d \
  --name helmet-app \
  -p 8000:8000 \
  -p 8080:8080 \
  --env-file .env \
  helmet-tidb
```

### Monitor the application

```bash
# Check container status
docker ps

# View application logs
docker logs -f helmet-app

# Health check
curl http://localhost:8000/health
```

### Stop the application

```bash
# Stop and remove the container
docker stop helmet-app
docker rm helmet-app
```

### Docker Compose (Alternative)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  helmet:
    build: .
    ports:
      - "8000:8000"
      - "8080:8080"
    env_file:
      - .env
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Then run:

```bash
docker-compose up -d
```

#### 2.2 Initialize database schema

```bash
python src/mcp/mcp_db/schema/execute_schema.py
```

This script will:

- Connect to your TiDB database
- Create all necessary tables (users, tasks, projects, etc.)
- Initialize views for optimized queries

#### 2.3 Verify table creation

Connect to your TiDB interface and verify that the following tables have been created:

- `users`: User and worker management
- `tasks`: Tasks with geolocation and skills
- `notifications`: Notification system
- `messages`: Notification system
- `task_vectors`: Vector representations of tasks for semantic search
- `user_vectors`: Vector representations of users for skill matching

### 3. LangSmith Configuration (Monitoring)

LangSmith will allow you to see in real-time:

- ⏱️ **Execution time** for each agent
- 🔢 **Number of tokens** used
- 🔍 **Detailed execution** of inter-agent communications
- 📊 **Global performance** metrics

Create an account on [LangSmith](https://smith.langchain.com/) and add your keys to the `.env`.

## 🎮 Usage


!!!!!!!!!!!!!!!!!!!!!!!


### 4. Observe execution in LangSmith

1. Connect to your LangSmith interface
2. Select your project configured in `.env`
3. Observe real-time agent execution, communications, and performance

## 📁 Project Structure

```text
├── main.py                     # Main entry point
├── src/
│   ├── agents/                 # Intelligent agents
│   │   ├── supervisor.py       # Main orchestrator
│   │   ├── planning.py         # Planning agent
│   │   ├── conflict.py         # Conflict resolution
│   │   ├── team_builder.py     # Team allocation
│   │   ├── notifier.py         # Notifications
│   │   └── executor.py         # Task execution
│   ├── mcp/                    # MCP protocols
│   │   ├── db_client.py        # Database client
│   │   └── mcp_db/            # TiDB MCP server
│   │       ├── mcp_server.py   # Main server
│   │       └── schema/         # Database schemas
│   ├── config/                 # Configuration
│   └── tools/                  # Utilities
├── server/                     # REST API
├── Makefile                    # Development commands
└── requirements.txt            # Python dependencies
```


## 🧪 Usage Examples

### Test messages for agents

See CRISIS_TEST_SCENARIOS.md for various crisis scenarios to test the agents.

## 📊 Monitoring with LangSmith

Once configured, LangSmith will give you access to:

- **Real-time dashboard**: Visualization of active agents
- **Detailed traces**: Every decision and inter-agent communication
- **Cost metrics**: Tokens used per agent and per session
- **Complete history**: All past executions with details
- **Performance alerts**: Detection of slow or erroring agents

## ⚡ Advanced Features

- **Vector search**: Semantic search in tasks and documents
- **Conflict detection**: Automatic algorithms for resource conflict resolution
- **Notifications**: Real-time alert system

## 🤝 Support

For any questions or issues:

1. Verify that TiDB is accessible from your network
2. Confirm that all tables are created in the TiDB interface
3. Check that LangSmith is receiving traces properly
4. Consult MCP server logs to debug connections

---

**Developed for TiDB Hackathon 2025** 🚀