FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    pkg-config \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create initialization script
RUN echo '#!/bin/bash\n\
    set -e\n\
    \n\
    echo "Starting application initialization..."\n\
    \n\
    # Wait for database to be ready\n\
    echo "Waiting for database connection..."\n\
    python -c "import mysql.connector; import os; import time; \
    config = {\"host\": os.getenv(\"TIDB_HOST\"), \"port\": int(os.getenv(\"TIDB_PORT\", 4000)), \"database\": os.getenv(\"TIDB_DATABASE\"), \"user\": os.getenv(\"TIDB_USER\"), \"password\": os.getenv(\"TIDB_PASSWORD\")}; \
    for i in range(30): \
    try: \
    conn = mysql.connector.connect(**config); \
    conn.close(); \
    print(\"Database connected!\"); \
    break; \
    except: \
    print(f\"Waiting for database... ({i+1}/30)\"); \
    time.sleep(2); \
    else: \
    raise Exception(\"Database connection failed after 30 attempts\")"\n\
    \n\
    # Initialize database schemas if needed\n\
    echo "Initializing database schemas..."\n\
    if [ -f "HELMET_MCP/mcp/mcp_db/schema/create_tables.sql" ]; then\n\
    echo "Database schema file found, executing..."\n\
    # Note: Schema execution would need to be handled by your application\n\
    echo "Schema initialization completed"\n\
    fi\n\
    \n\
    # Initialize dataset if needed\n\
    echo "Loading initial dataset..."\n\
    cd HELMET_MCP/mcp/mcp_db/data && python dataset_001.py\n\
    cd /app\n\
    \n\
    echo "Starting MCP database server..."\n\
    cd HELMET_MCP/mcp/mcp_db && python mcp_server.py &\n\
    MCP_PID=$!\n\
    \n\
    # Wait a bit for MCP server to start\n\
    sleep 5\n\
    \n\
    echo "Starting backend server..."\n\
    cd /app/HELMET_BACKEND && python backend.py &\n\
    BACKEND_PID=$!\n\
    \n\
    echo "Application started successfully!"\n\
    echo "MCP Server PID: $MCP_PID"\n\
    echo "Backend Server PID: $BACKEND_PID"\n\
    \n\
    # Wait for any process to exit\n\
    wait -n\n\
    \n\
    # Exit with status of process that exited first\n\
    exit $?\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Set environment variables
ENV PYTHONPATH="/app:/app/HELMET_MCP/mcp/mcp_db:/app/HELMET_BACKEND"
ENV MCP_PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose ports
EXPOSE 8080 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["/app/start.sh"]