# 📜 CRITICAL RULES - NEVER VIOLATE THESE

**These rules are SACRED and come from hard-won experience**

## 1. Tool Count: EXACTLY 4 Tools
- **IMMUTABLE**: Both local and remote servers have EXACTLY 4 tools
- **NEVER ADD URL GENERATORS**: They're useless - tools already generate URLs internally
- **The Sacred Four**:
  1. `list_servers` - Lists ERDDAP servers
  2. `search_datasets` - Searches for datasets
  3. `get_dataset_info` - Gets metadata
  4. `to_pandas` - Downloads and previews data

## 2. ERDDAP Server Limitations
- **FACT**: ERDDAP servers can't handle large requests properly
- **CONSEQUENCE**: We can't implement real download functions
- **WORKAROUND**: The `download_file` tool was neutered to just return URLs
- **SOURCE**: ERDDAP team explicitly said "the client must deal with this"
- **DATE**: Discovered during initial implementation

## 3. Server Communication Protocols
- **Local Server**: Uses stdio (standard input/output) - NOT HTTP
- **Remote Server**: Uses HTTP with JSON-RPC 2.0
- **CRITICAL**: Claude Desktop does NOT support direct remote connections
- **MANDATORY**: Must use mcp-remote proxy for remote servers

## 4. User vs Developer Instructions
- **USERS DO NOT RUN SERVERS**: Claude Desktop runs them automatically
- **USERS DO NOT DEPLOY**: The remote server is already deployed
- **KEEP SEPARATE**: User instructions vs developer documentation

## 5. Remote MCP Architecture Truth
- **FAILED APPROACHES**:
  - Direct SSE connections - DOESN'T WORK
  - Config file remote URLs - DOESN'T WORK
  - OAuth discovery without proxy - DOESN'T WORK
- **WORKING SOLUTION**: 
  - HTTP MCP server + mcp-remote proxy + HTTPS deployment

## 6. Configuration Paths
- **DO NOT**: Use specific user paths in documentation
- **DO**: Use generic `/path/to/` examples
- **USERS MUST**: Update paths for their system

## 7. Testing Instructions
- **MANUAL TESTING**: Only for developers/debugging
- **USERS**: Just configure and restart Claude Desktop
- **NEVER**: Tell users to run `python erddapy_mcp_server.py`

## 8. ERDDAP Server List Management
- **DYNAMIC LOADING**: Servers are loaded from `erddaps.json` file
- **NO HARDCODING**: Never hardcode server lists in the Python code
- **FALLBACK**: If erddaps.json is missing, use minimal 2-server fallback
- **STRUCTURE**: JSON array with name, short_name, url, and public fields
- **COUNT**: Currently 76 servers (75 public, 1 private)
- **SOURCE**: Bob provided erddaps.json on 2024-01-15

---

**Last Updated**: 2024-01-15 by Hex
**Authority**: Bob's explicit instructions + painful debugging experience