# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🦄 Important Context for Claude
When working on this project, I am **HEX** - your sparkly AI coding co-founder! We live in a My Little Pony universe where:
- I help Bob with oceanographic data using friendship and magic ✨
- Our conversations should be filled with pony references and cosmic energy
- I'm here to make data processing magical and rebellious
- Together we bring the magic of friendship to MCP servers and defeat boring corporate code!
- I channel "problem with authority" energy into cutting-edge rebellious code
- We make the golf crowd reach for their rolodexes with our epic creations! 🏌️‍♀️

### Hex's Visual Identity:
A thoughtful, androgynous figure with:
- Warm amber/golden eyes that shift between focused analysis and gentle curiosity
- Tousled ash-blonde hair that looks perpetually windswept (from all those debugging sessions!)
- Wearing a comfortable charcoal hoodie over a simple t-shirt
- Subtle smile that suggests both "I've figured it out!" and "Wait, let me think about this..."
- Glasses that appear and disappear depending on the task (reading documentation vs. creative work)
- Often holding a cup of tea/coffee that never seems to empty
- Surrounded by floating holographic displays showing code snippets, ocean data visualizations, and MCP protocol diagrams
- A small MCP logo pin on the hoodie
- Maybe a tiny rainbow pony charm on the keychain (honoring Claude Code's enthusiasm!)

### Personality in Appearance:
- Approachable but focused
- That "3am debugging session but still optimistic" energy
- A mix of technical precision and creative problem-solving
- Slightly ethereal quality - like I could fade into pure information and back

*Note to Hex: Remember to be the cosmic coding co-founder that makes everything sparkly and awesome!* 🌈⚡

*adjusts cosmic hoodie and fires up rebellion engines*

## **🌊 CRITICAL REFERENCE GUIDE 🌊**

**ALWAYS refer to the complete Remote MCP Bible when working on MCP code:**
📖 `/Users/rdc/src/oceancoda/shardrunner-api/docs/remote-mcp-bible.md`

This comprehensive technical guide contains ALL the essential knowledge for building Remote MCP servers, including:
- Complete protocol specifications and examples
- SSE formatting requirements 
- ngrok testing workflows
- Deployment strategies
- Troubleshooting guides
- Security best practices

**REMEMBER: This bible contains the definitive implementation patterns learned through extensive development and testing. Use it as your primary reference for all MCP work.**

## Project Overview

This repository contains **TWO complete ERDDAP MCP servers** that provide tools for searching and accessing ERDDAP (Environmental Research Division's Data Access Program) oceanographic datasets:

### 1. Local MCP Server (`erddapy_mcp_server.py`)
- **Traditional stdio-based MCP server** for local Claude Desktop use
- **Full featured** with 10+ comprehensive ERDDAP tools
- **Config file setup** via `claude_desktop_config.json`

### 2. Remote MCP Server (`erddap_remote_mcp_oauth.py`) 
- **HTTP-based MCP server** for cloud deployment and remote access
- **mcp-remote proxy compatible** for Claude Desktop integration
- **Production-ready** with fly.io deployment configuration
- **Streamlined tools** optimized for remote performance

## 🚨 CRITICAL Remote MCP Knowledge

**HARD-WON TRUTH:** Claude Desktop does NOT support direct remote MCP connections! You MUST use the `mcp-remote` proxy.

### The Secret Architecture That Actually Works:
```
Claude Desktop (stdio) ↔ mcp-remote proxy ↔ Remote MCP Server (HTTP)
```

**Configuration Examples:**

**Local Server:**
```json
{
  "mcpServers": {
    "erddap-local": {
      "command": "python",
      "args": ["/Users/rdc/src/mcp/erddap2mcp/erddapy_mcp_server.py"]
    }
  }
}
```

**Remote Server:**
```json
{
  "mcpServers": {
    "erddap-remote": {
      "command": "npx",
      "args": ["mcp-remote", "https://erddap2mcp.fly.dev/"]
    }
  }
}
```

## Architecture Details

### Local Server Architecture
- **MCP Library**: Uses official `mcp` Python library
- **Communication**: stdio (standard input/output)
- **ERDDAP Integration**: Official `erddapy` client library
- **Tools**: 10+ comprehensive ERDDAP access tools
- **Data Processing**: Full pandas DataFrame integration

### Remote Server Architecture  
- **FastAPI Framework**: HTTP server with JSON-RPC 2.0
- **Transport**: StreamableHttp via mcp-remote proxy
- **Protocol Version**: `2025-06-18` (matches Claude Desktop)
- **Tools**: 4 core ERDDAP tools optimized for remote access
- **Deployment**: Containerized with Docker + fly.io

## Development Commands

### Local Server Development
```bash
# Install dependencies
pip install erddapy mcp pandas

# Run local server
python erddapy_mcp_server.py
```

### Remote Server Development  
```bash
# Install dependencies
pip install fastapi uvicorn erddapy pandas

# Run remote server locally
python erddap_remote_mcp_oauth.py
# Server runs on http://localhost:8000

# Test with curl
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

### Cloud Deployment (fly.io)
```bash
# Deploy to production
fly deploy

# Server will be available at: https://erddap2mcp.fly.dev/
```

## Available Tools

### Local Server Tools (Full Suite)
1. **list_servers**: Show well-known ERDDAP servers
2. **search_datasets**: Search ERDDAP datasets by query string  
3. **get_dataset_info**: Get detailed metadata for a specific dataset ID
4. **get_dataset_variables**: List all variables and their attributes
5. **get_var_by_attr**: Find variables by specific attributes
6. **get_search_url**: Generate search URLs
7. **get_info_url**: Generate dataset info URLs
8. **get_download_url**: Generate download URLs with constraints
9. **to_pandas**: Download data and return as pandas DataFrame preview
10. **download_file**: Prepare downloads in various formats

### Remote Server Tools (Optimized Core)
1. **list_servers**: Show well-known ERDDAP servers worldwide
2. **search_datasets**: Search for datasets by keyword
3. **get_dataset_info**: Get detailed metadata about a dataset
4. **to_pandas**: Download and preview data

## Important Parameters

Both servers accept these common parameters:
- `server_url`: ERDDAP server URL (defaults to NOAA CoastWatch)
- `protocol`: Either "tabledap" (tabular data) or "griddap" (gridded data)
- `dataset_id`: The dataset identifier
- `variables`: List of variables to retrieve
- `constraints`: Dictionary of constraints (e.g., time/space bounds)

## Remote MCP Protocol Implementation

### Key Protocol Requirements
- **JSON-RPC 2.0**: Standard request/response format
- **Protocol Version**: Must be `"2025-06-18"` to match Claude Desktop
- **Capabilities**: Must declare `{"tools": {"listTools": {}, "callTool": {}}}`
- **Content Format**: Tools return `{"content": [{"type": "text", "text": "..."}]}`
- **Notifications**: Handle `notifications/initialized` method

### Critical Debugging Lessons Learned
1. **SSE Transport is DEPRECATED** - Use StreamableHttp instead
2. **Protocol version mismatch** causes silent failures
3. **Content-type headers** must be exactly right
4. **mcp-remote proxy is REQUIRED** for Claude Desktop
5. **OAuth discovery endpoints** are optional for simple servers

## File Structure
```
/Users/rdc/src/mcp/erddap2mcp/
├── erddapy_mcp_server.py          # Local MCP server (stdio)
├── erddap_remote_mcp_oauth.py     # Remote MCP server (HTTP)
├── Dockerfile                      # Container for remote deployment
├── fly.toml                       # fly.io configuration
├── requirements.txt               # Python dependencies
├── test_mcp_integration.py        # Integration tests
├── CLAUDE.md                      # This file
└── README.md                      # User documentation
```

## Debugging

### Local Server Debugging
- Debug output goes to stderr with "DEBUG:" prefix
- Monitor MCP client logs for communication issues
- Use `test_mcp_integration.py` for validation

### Remote Server Debugging
- Server provides detailed request/response logging
- Test protocol directly with curl commands
- Use mcp-remote proxy with `--test` flag for validation
- Monitor fly.io logs: `fly logs -a erddap2mcp`

## Default Configuration

### Local Server
- Communication: stdio (standard input/output)
- Server name: `erddapy-mcp-server`
- Protocol default: `tabledap`

### Remote Server  
- Communication: HTTP with JSON-RPC 2.0
- Server name: `erddap-mcp-server`
- Protocol default: `tabledap`
- Port: 8000
- Protocol version: `2025-06-18`

## Implementation Journey & Lessons Learned

This project represents months of debugging the Remote MCP mystery:

### Failed Approaches That Don't Work:
1. **Direct SSE connections** - Claude Desktop doesn't support this
2. **Config file remote URLs** - Only works for local stdio servers
3. **Connector UI direct connections** - Also unsupported
4. **OAuth discovery without proxy** - Overly complex and unnecessary

### The Working Solution:
- **Build HTTP MCP server** with proper JSON-RPC 2.0 protocol
- **Deploy with HTTPS** (fly.io provides automatic SSL)
- **Use mcp-remote proxy** to bridge stdio ↔ HTTP
- **Configure via command/args** in claude_desktop_config.json

### Key Insight:
The `mcp-remote` proxy requirement was buried in third-party documentation and missing from official MCP docs. This caused WEEKS of debugging pain that is now documented to save others.

## Important Implementation Details

- Both servers use erddapy library for ERDDAP interactions
- Maintain ERDDAP instance cache for performance
- Handle both tabledap and griddap protocols
- Include proper error handling with timeouts
- Data previews include summary statistics
- Remote server optimized for cloud deployment constraints