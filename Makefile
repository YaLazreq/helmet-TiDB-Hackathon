# TiDB Hackathon Project Makefile
# Commands to run the main application and MCP database server

.PHONY: help main mcp-db mcp-api install clean test lint format

# Run the main application
main:
	@echo "🚀 Starting main application..."
	python main.py

# Start the MCP database server
mcp-db:
	@echo "🗄️  Starting MCP database server..."
	python src/mcp/mcp_db/mcp_server.py

# Start the MCP API server  
# mcp-api:
# 	@echo "🌐 Starting MCP API server..."
# 	cd src/mcp/mcp_api && python mcp_server.py

# # Install dependencies
# install:
# 	@echo "📦 Installing dependencies..."
# 	pip install -r requirements.txt

# # Run tests
# test:
# 	@echo "🧪 Running tests..."
# 	python -m pytest tests/ -v

# # Run linting
# lint:
# 	@echo "🔍 Running linting..."
# 	python -m flake8 src/ --max-line-length=88 --ignore=E203,W503
# 	python -m pylint src/

# # Format code
# format:
# 	@echo "✨ Formatting code..."
# 	python -m black src/ main.py
# 	python -m isort src/ main.py

# # Clean cache files
# clean:
# 	@echo "🧹 Cleaning cache files..."
# 	find . -type d -name "__pycache__" -exec rm -rf {} +
# 	find . -type f -name "*.pyc" -delete
# 	find . -type f -name "*.pyo" -delete
# 	find . -type d -name "*.egg-info" -exec rm -rf {} +

# # Test specific agents
# test-notifier:
# 	@echo "🔔 Testing notifier agent..."
# 	python -m src.agents.notifier

# test-planning:
# 	@echo "📋 Testing planning agent..."
# 	python -c "from src.agents.planning import planning_agent_as_tool; print(planning_agent_as_tool('Show me all tasks for tomorrow'))"

# test-conflict:
# 	@echo "⚠️  Testing conflict agent..."
# 	python -c "from src.agents.conflict import conflict_agent_as_tool; print(conflict_agent_as_tool('Check conflicts for moving task 5 to 15:00 tomorrow'))"

# # Development helpers
# dev-setup: install
# 	@echo "🛠️  Setting up development environment..."
# 	pip install black isort flake8 pylint pytest

# # Run all tests
# test-all: test-notifier test-planning test-conflict
# 	@echo "✅ All agent tests completed!"

# # Start development server (with auto-reload)
# dev:
# 	@echo "🔄 Starting development mode..."
# 	python -m watchdog src/ --patterns="*.py" --command="make main"