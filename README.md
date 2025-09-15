# 🚧 TiDB Hackathon - Intelligent Task Management System

A multi-agent system using LangGraph for automated construction task management with TiDB database.

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
- **Team Builder**: Intelligent team allocation
- **Notifier**: Automated notifications and alerts
- **Executor**: Task execution and tracking

### 🎲 Code Specialties

- **Multi-agent architecture** with LangGraph for complex workflows
- **Vector database** TiDB for advanced semantic search
- **MCP protocol** for secure database interaction
- **Intelligent tracing** with LangSmith for real-time monitoring
- **Automated conflict management** for resource optimization
- **RESTful API** with FastAPI for external integration
- **Multilingual support** (French/English) in interactions

## 🚀 Installation and Configuration

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
ANTHROPIC_API_KEY=sk-ant-api03-your-key

# LangSmith Configuration (for monitoring)
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=lsv2_pt_your-langsmith-key
LANGSMITH_PROJECT="your-project-name"
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
- `projects`: Construction projects
- `task_assignments`: Task assignments
- `notifications`: Notification system
- Views: `active_tasks`, `overdue_tasks`, `worker_workload`

### 3. LangSmith Configuration (Monitoring)

LangSmith will allow you to see in real-time:

- ⏱️ **Execution time** for each agent
- 🔢 **Number of tokens** used
- 🔍 **Detailed execution** of inter-agent communications
- 📊 **Global performance** metrics

Create an account on [LangSmith](https://smith.langchain.com/) and add your keys to the `.env`.

## 🎮 Usage

### 1. Launch the MCP database server

```bash
make mcp-db
```

This server must run in the background to allow agents to access the database.

### 2. Configure test message

In `main.py`, line 28, replace the message with your worker's message:

```python
message = "[User ID: 2 - Message Date: Sun. 10 September 2025]: Your message here"
```

### 3. Execute the main application

```bash
make main
```

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

## 🔧 Available Commands

```bash
# Initialize database schema
python src/mcp/mcp_db/schema/execute_schema.py

# Start MCP database server
make mcp-db

# Launch main application after MCP server
make main
```

## 🧪 Usage Examples

### Test messages for agents

```python
# Task assignment
"[User ID: 2]: Can you find someone to help me on my actual task ?"

# Contact update
"[User ID: 1]: Update Michael Rodriguez's phone: +1-711-123-4567"

# Site emergency
"[User ID: 3]: Container blocking main entrance needs urgent removal"

# Project delay
"[User ID: 3]: Restaurant Foundation Excavation on RETAIL Building is delayed"

# Resource shortage
"[User ID: 2]: we don't have enough sheath anymore"
```

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