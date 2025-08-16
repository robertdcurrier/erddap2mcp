# 🏗️ ERDDAP MCP Architecture

## Two Servers, One Purpose

### Local MCP Server (`erddapy_mcp_server.py`)
- **Protocol**: stdio (standard input/output)
- **Framework**: Official MCP Python library
- **Communication**: JSON-RPC over stdin/stdout
- **Deployment**: Runs on user's machine
- **Launch**: Automatic via Claude Desktop

### Remote MCP Server (`erddap_remote_mcp_oauth.py`)
- **Protocol**: HTTP with JSON-RPC 2.0
- **Framework**: FastAPI
- **Communication**: HTTP POST requests
- **Deployment**: fly.io (or any cloud platform)
- **Access**: Via mcp-remote proxy ONLY

## The Critical Architecture Secret

```
Claude Desktop (stdio) ↔ mcp-remote proxy ↔ Remote MCP Server (HTTP)
```

**This is the ONLY way remote MCP works with Claude Desktop!**

## Tool Architecture (Both Servers)

### The Four Sacred Tools
1. **list_servers**: Returns hardcoded list of ERDDAP servers
2. **search_datasets**: Calls `erddapy.get_search_url()` then fetches CSV
3. **get_dataset_info**: Calls `erddapy.get_info_url()` then parses metadata
4. **to_pandas**: Uses `erddapy.to_pandas()` to fetch and preview data

### Internal Flow
```python
User Request → MCP Tool → ERDDAP Instance → erddapy library → ERDDAP Server
                               ↓
                        (cached per server/protocol)
```

## ERDDAP Instance Management
- Instances cached by `{server_url}_{protocol}` key
- Reused across requests for performance
- Separate instances for tabledap vs griddap

## Why This Architecture?

### Local Server
- Zero network setup required
- Direct integration with Claude Desktop
- No authentication needed
- Instant response times

### Remote Server
- Shareable across team/organization
- No local dependencies
- Cloud scalability
- Centralized updates

## Protocol Specifications

### Local: MCP stdio Protocol
```json
{"jsonrpc": "2.0", "method": "tools/list", "id": 1}
```

### Remote: HTTP + JSON-RPC 2.0
```http
POST / HTTP/1.1
Content-Type: application/json

{"jsonrpc": "2.0", "method": "tools/list", "id": 1}
```

## Critical Version Requirements
- **Protocol Version**: "2025-06-18" (MUST match Claude Desktop)
- **MCP Library**: >= 1.0.0
- **FastAPI**: >= 0.100.0 (for remote)

## What NOT to Do
- ❌ Try direct HTTP connections from Claude Desktop
- ❌ Implement SSE (Server-Sent Events) - deprecated
- ❌ Skip the mcp-remote proxy for remote servers
- ❌ Add URL generator tools (they're useless)
- ❌ Implement actual download functions (ERDDAP can't handle it)

## Performance Considerations
- ERDDAP instance caching prevents connection overhead
- CSV format used for metadata (fastest for ERDDAP)
- Data previews limited to head() and describe()
- Constraints should be used to limit data volume

---

**Remember**: This architecture was refined through painful trial and error. Don't change it without understanding why each decision was made!