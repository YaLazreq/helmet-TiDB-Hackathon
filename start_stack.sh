#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Starting Maps Agent Stack${NC}"
echo "=========================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Check required ports
echo -e "${YELLOW}Checking ports...${NC}"
if ! check_port 8080; then
    echo -e "${RED}Error: MCP Server port 8080 is already in use${NC}"
    echo "Please stop the existing MCP server or change the port"
    exit 1
fi

if ! check_port 3001; then
    echo -e "${RED}Error: Agent Server port 3001 is already in use${NC}"
    echo "Please stop the existing service or change the port"
    exit 1
fi

if ! check_port 3000; then
    echo -e "${RED}Error: Next.js port 3000 is already in use${NC}"
    echo "Please stop the existing service or change the port"
    exit 1
fi

# Start MCP Server
echo -e "${GREEN}1. Starting MCP Server on port 8080...${NC}"
cd /Users/yan/Development/TiDB/tiDB-Hackathon
python server/server_api.py &
MCP_PID=$!
sleep 3

# Check if MCP server started successfully
if ! kill -0 $MCP_PID 2>/dev/null; then
    echo -e "${RED}Failed to start MCP server${NC}"
    exit 1
fi

# Start Agent Server
echo -e "${GREEN}2. Starting Agent Server on port 3001...${NC}"
python agent_server.py &
AGENT_PID=$!
sleep 3

# Check if Agent server started successfully
if ! kill -0 $AGENT_PID 2>/dev/null; then
    echo -e "${RED}Failed to start Agent server${NC}"
    kill $MCP_PID 2>/dev/null
    exit 1
fi

# Start Next.js Frontend
echo -e "${GREEN}3. Starting Next.js Frontend on port 3000...${NC}"
cd maps-agent-ui
npm run dev &
NEXTJS_PID=$!
sleep 3

# Check if Next.js started successfully
if ! kill -0 $NEXTJS_PID 2>/dev/null; then
    echo -e "${RED}Failed to start Next.js frontend${NC}"
    kill $MCP_PID $AGENT_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo "=========================="
echo -e "🌐 Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "🤖 Agent API: ${YELLOW}http://localhost:3001${NC}"
echo -e "🛠️  MCP Server: ${YELLOW}http://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Function to cleanup processes
cleanup() {
    echo -e "\n${YELLOW}Stopping all services...${NC}"
    kill $NEXTJS_PID $AGENT_PID $MCP_PID 2>/dev/null
    wait $NEXTJS_PID $AGENT_PID $MCP_PID 2>/dev/null
    echo -e "${GREEN}All services stopped${NC}"
    exit 0
}

# Handle Ctrl+C
trap cleanup INT

# Wait for processes
wait