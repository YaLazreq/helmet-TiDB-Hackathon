# Maps Agent Web Interface

This setup creates a complete web interface for your MCP Google Maps agent, allowing users to interact with your agent through a modern web UI.

## Architecture

```
Frontend (Next.js) -> Agent Server (FastAPI) -> MCP Server (FastMCP) -> Google Maps API
     :3000                :3001                    :8080
```

## Components

1. **Next.js Frontend** (`maps-agent-ui/`): React-based web interface with a clean, modern UI
2. **Agent Server** (`agent_server.py`): FastAPI wrapper around your existing agent logic
3. **MCP Server** (`server/server_api.py`): Your existing MCP server with Google Maps tools

## Setup

### 1. Install Dependencies

Make sure you have all Python dependencies:
```bash
pip install -r requirements.txt
```

Install Node.js dependencies for the frontend:
```bash
cd maps-agent-ui
npm install
```

### 2. Environment Setup

Make sure your `.env` file contains:
- `ANTHROPIC_API_KEY`: Your Claude API key
- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key
- Any other required environment variables

### 3. Start the Stack

Use the provided startup script:
```bash
./start_stack.sh
```

This will start all three services:
- MCP Server on port 8080
- Agent Server on port 3001  
- Next.js Frontend on port 3000

### 4. Access the Interface

Open your browser and go to: `http://localhost:3000`

## Usage

1. Enter your maps-related question in the text area
2. Click "Ask Agent" 
3. The system will:
   - Send your query to the Agent Server
   - Agent Server processes it using your MCP tools
   - Results are displayed with topic, description, tools used, and sources

## Example Queries

- "Find coffee shops near Times Square, New York"
- "Get directions from Central Park to Brooklyn Bridge"
- "What's the distance between Los Angeles and San Francisco?"
- "Find restaurants within 5 miles of the Eiffel Tower"

## Manual Startup (Alternative)

If you prefer to start services individually:

1. **Start MCP Server:**
   ```bash
   python server/server_api.py
   ```

2. **Start Agent Server:**
   ```bash
   python agent_server.py
   ```

3. **Start Frontend:**
   ```bash
   cd maps-agent-ui
   npm run dev
   ```

## Troubleshooting

### Port Conflicts
If any ports are in use, the startup script will notify you. You can:
- Stop existing services on those ports
- Modify the ports in the respective configuration files

### MCP Connection Issues
- Ensure your MCP server is running on port 8080
- Check that the Google Maps API key is valid
- Verify all tools are properly registered

### Agent Server Issues
- Check that `langchain-mcp-adapters` is installed
- Verify your Anthropic API key is set
- Ensure the MCP client can connect to localhost:8080

## File Structure

```
.
├── agent_server.py              # FastAPI server wrapping the agent
├── client.py                    # Original CLI client
├── start_stack.sh              # Startup script
├── server/                      # MCP server
│   ├── server_api.py
│   └── tools/                  # Google Maps tools
└── maps-agent-ui/              # Next.js frontend
    ├── src/
    │   ├── app/
    │   │   ├── api/agent/route.ts  # API endpoint
    │   │   └── page.tsx            # Main UI
    └── package.json
```

## Development

- Frontend: Hot reloading enabled, edit files in `maps-agent-ui/src/`
- Agent Server: Restart server after changes to `agent_server.py`
- MCP Server: Restart server after changes to tools or server code