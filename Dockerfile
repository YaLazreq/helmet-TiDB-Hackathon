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

# Create simple startup script
RUN echo '#!/bin/bash\n\
    echo "Starting MCP server..."\n\
    cd HELMET_MCP/mcp/mcp_db && python3 mcp_server.py &\n\
    echo "Starting backend..."\n\
    cd /app/HELMET_BACKEND && python3 backend.py &\n\
    wait\n\
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