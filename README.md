# ERDDAP MCP Servers - Local & Remote

Access oceanographic and environmental data from ERDDAP servers worldwide through Claude Desktop via **two complete MCP implementations**: local stdio and remote HTTP.

**🚀 Now with dynamic server loading from `erddaps.json` - 63+ ERDDAP servers available!**

## 🌊 Two Servers, All Possibilities

This repository provides **both local and remote MCP server implementations**:

### 📍 Local MCP Server (`erddapy_mcp_server.py`)
- **Traditional stdio-based MCP server** for local Claude Desktop use
- **4 comprehensive ERDDAP tools** for data discovery and access
- **Easy setup** via claude_desktop_config.json
- **No network dependencies** - runs completely locally

### ☁️ Remote MCP Server (`erddap_remote_mcp_oauth.py`)
- **HTTP-based MCP server** for cloud deployment
- **Production-ready** with fly.io deployment configuration
- **mcp-remote proxy compatible** for Claude Desktop integration
- **Same 4 core tools** optimized for remote performance

## 🚨 CRITICAL: Remote MCP Connection Requirements

**Claude Desktop does NOT support direct remote MCP connections!** You MUST use the `mcp-remote` proxy for remote servers.

### The Secret Architecture:
```
Claude Desktop (stdio) ↔ mcp-remote proxy ↔ Remote MCP Server (HTTP)
```

## What is ERDDAP?

ERDDAP (Environmental Research Division's Data Access Program) is a data server that provides simple, consistent access to scientific datasets in common file formats. These MCP servers make ERDDAP's powerful oceanographic data accessible to AI assistants through natural language queries.

## Quick Start

### Option 1: Local MCP Server (Recommended for Getting Started)

**1. Install Dependencies:**
```bash
pip install erddapy mcp pandas
```

**2. Configure Claude Desktop:**
Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "erddap-local": {
      "command": "python",
      "args": ["/path/to/erddapy_mcp_server.py"]
    }
  }
}
```

**Windows Users:** Use `%APPDATA%\Claude\claude_desktop_config.json` and double backslashes in paths:
```json
{
  "mcpServers": {
    "erddap-local": {
      "command": "python", 
      "args": ["C:\\Users\\YourName\\path\\to\\erddapy_mcp_server.py"]
    }
  }
}
```

**3. Restart Claude Desktop:**
After updating the configuration, restart Claude Desktop. The server will start automatically and the ERDDAP tools will be available.

### Option 2: Remote MCP Server (Access the Cloud Instance)

**1. Install mcp-remote proxy:**
```bash
npm install -g mcp-remote
```

**2. Configure Claude Desktop:**
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

**3. Restart Claude Desktop:**
The remote server will be accessible through the mcp-remote proxy.

## Available Tools

### Available Tools (Both Servers)
| Tool | Description | Example Use |
|------|-------------|-------------|
| `list_servers` | Show well-known ERDDAP servers worldwide | "Show me available ERDDAP servers" |
| `search_datasets` | Search for datasets by keyword | "Find temperature datasets on IOOS ERDDAP" |
| `get_dataset_info` | Get detailed metadata about a dataset | "Tell me about dataset jplMURSST41" |
| `to_pandas` | Download and preview data | "Show me temperature data from January 2024" |

## Usage Examples

### List Available ERDDAP Servers
**You:** "Show me available ERDDAP servers"

**Claude:** Here are some well-known ERDDAP servers you can access:

- **NOAA CoastWatch** (https://coastwatch.pfeg.noaa.gov/erddap) - Satellite and in-situ oceanographic data
- **IOOS ERDDAP** (https://erddap.ioos.us/erddap) - Integrated Ocean Observing System data
- **Marine Institute Ireland** (https://erddap.marine.ie/erddap) - Irish marine data
- **Ocean Networks Canada** (https://data.oceannetworks.ca/erddap) - Canadian ocean data
- **GCOOS ERDDAP** (https://gcoos5.geos.tamu.edu/erddap) - Gulf of Mexico data

### Search for Datasets
**You:** "Search for glider datasets on GCOOS ERDDAP"

**Claude:** I found 26 glider datasets on the GCOOS ERDDAP server. Here are some examples:

- **Stommel-20200813T1200**: Ocean glider deployment
- **usf-sam-20210331T0000**: University of South Florida glider
- **mote-dora-20210318T1200**: Mote Marine Laboratory glider

These datasets contain oceanographic measurements collected by autonomous underwater gliders.

### Analyze Data
**You:** "Get information about the dataset mote-dora-20210318T1200"

**Claude:** This dataset contains oceanographic measurements from a Mote Marine Laboratory glider deployment:

**Time Coverage**: March 18, 2021 - April 15, 2021  
**Variables**: Temperature, salinity, density, dissolved oxygen, chlorophyll  
**Location**: Eastern Gulf of Mexico coastal waters

## Architecture Comparison

### Local Server
- **Communication**: stdio (standard input/output)
- **Deployment**: Runs on your local machine
- **Tools**: 4 comprehensive data access tools
- **Setup**: Single config file entry
- **Dependencies**: Python + MCP library

### Remote Server  
- **Communication**: HTTP with JSON-RPC 2.0
- **Deployment**: Cloud platforms (fly.io, AWS, etc.)
- **Tools**: Same 4 data access tools
- **Setup**: Requires mcp-remote proxy
- **Dependencies**: FastAPI + Docker + HTTPS

## For Developers: Cloud Deployment

*This section is for developers who want to deploy their own instance of the remote server.*

### fly.io Deployment (Recommended)

The remote server is configured for one-command deployment to fly.io:

```bash
# Deploy from the erddap2mcp directory
fly deploy
```

**fly.toml Configuration:**
```toml
app = 'erddap2mcp'
primary_region = 'mia'

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = 'stop'
  auto_start_machines = true

[[vm]]
  memory = '1gb'
  cpu_kind = 'shared'
  cpus = 1
```

**Key Features:**
- ✅ **Automatic HTTPS** - SSL certificates managed automatically
- ✅ **Auto-scaling** - Machines start/stop based on traffic
- ✅ **Global CDN** - Fast access worldwide
- ✅ **Zero-downtime deploys** - Seamless updates

### Container Deployment (Other Platforms)
```bash
# Build container
docker build -t erddap-mcp-server .

# Run locally
docker run -p 8000:8000 erddap-mcp-server

# Deploy to other platforms:
# - AWS Lambda (requires HTTPS setup)
# - Railway/Render (usually provide HTTPS automatically)
# - Google Cloud Run
# - Azure Container Instances
```

## Testing Your Setup

### For Users: Verify Installation

After configuring Claude Desktop, restart it and check if the ERDDAP tools appear in the tools list.

### For Developers: Manual Testing

#### Test Local Server
```bash
# Test the server directly (for debugging)
python erddapy_mcp_server.py

# Send test commands:
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python erddapy_mcp_server.py
```

#### Test Remote Server
```bash
# Test basic connectivity
curl http://localhost:8000/

# Test MCP protocol
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'

# Test with mcp-remote proxy
npx mcp-remote http://localhost:8000/ --test
```

## Configuration Examples

### Both Servers Together
You can run both local and remote servers simultaneously:

```json
{
  "mcpServers": {
    "erddap-local": {
      "command": "python",
      "args": ["/Users/rdc/src/mcp/erddap2mcp/erddapy_mcp_server.py"]
    },
    "erddap-remote": {
      "command": "npx", 
      "args": ["mcp-remote", "https://erddap2mcp.fly.dev/"]
    }
  }
}
```

This gives you the full local toolset plus cloud accessibility!

## Common Tool Parameters

Both servers accept these parameters:
- `server_url`: ERDDAP server URL (defaults to NOAA CoastWatch)
- `protocol`: Either "tabledap" (tabular data) or "griddap" (gridded data)
- `dataset_id`: The dataset identifier
- `variables`: List of variables to retrieve
- `constraints`: Dictionary of constraints (e.g., time/space bounds)

## Tips for Best Results

1. **Start with local**: Local server has easier setup and no proxy requirement
2. **Use remote for sharing**: Remote server can be accessed by multiple users
3. **Check metadata first**: Use `get_dataset_info` before downloading data
4. **Use constraints**: Limit data requests to avoid timeouts
5. **Choose correct protocol**: tabledap for tabular, griddap for gridded data

## Troubleshooting

### Local Server Issues
- **"No such file"**: Check Python path in configuration
- **"Connection failed"**: Verify server is running
- **Tool errors**: Check stderr for debug output

### Remote Server Issues  
- **"No tools available"**: Ensure mcp-remote proxy is installed (`npm install -g mcp-remote`)
- **"Connection failed"**: Verify server URL is accessible and uses HTTPS
- **Protocol errors**: Check server logs with `fly logs -a erddap2mcp`

### General ERDDAP Issues
- **Timeouts**: Reduce spatial/temporal extent of requests
- **Protocol errors**: Specify correct protocol (tabledap vs griddap)
- **Server unavailable**: Some ERDDAP servers may be temporarily down

## The Remote MCP Discovery Journey

This remote implementation represents months of debugging the Remote MCP mystery:

### Failed Approaches:
1. **Direct SSE connections** - Claude Desktop doesn't support this
2. **Config file remote URLs** - Only works for local stdio servers
3. **Connector UI attempts** - Also doesn't support direct connections

### The Breakthrough:
The `mcp-remote` proxy requirement was buried in third-party documentation. This critical piece enables Claude Desktop to talk to remote MCP servers via HTTP.

## Credits

- **ERDDAP** was developed by Bob Simons at NOAA's Environmental Research Division. Learn more at the [ERDDAP website](https://coastwatch.pfeg.noaa.gov/erddap/information.html).
- **erddapy** is the official Python client for ERDDAP, developed by [Filipe Fernandes](https://github.com/ocefpaf) and the IOOS community. Visit the [erddapy documentation](https://ioos.github.io/erddapy/).
- **mcp-remote** proxy enables remote MCP connections to Claude Desktop

## Common Use Cases

- **Climate Research**: Access historical temperature, salinity, and current data
- **Marine Biology**: Find chlorophyll concentrations and ocean color data  
- **Coastal Management**: Monitor sea level, wave heights, and coastal conditions
- **Fisheries**: Access environmental data for fisheries management
- **Education**: Explore real oceanographic data for teaching and learning

## Server List Management

**ERDDAP servers are now loaded dynamically from `erddaps.json`:**
- 63 ERDDAP servers pre-configured (worldwide coverage)
- Easy to add/remove servers by editing JSON file
- Automatic fallback if file is missing
- Servers grouped by public/private access
- Each server entry includes name, short_name, url, and public flag

To add new servers, simply edit `erddaps.json`:
```json
{
  "name": "Your ERDDAP Server",
  "short_name": "YES",
  "url": "https://your-erddap.org/erddap/",
  "public": true
}
```

## Contributing

Contributions welcome! This project demonstrates how to build both local and remote MCP servers. Key areas for improvement:

- Additional ERDDAP tools and data processing capabilities
- Enhanced error handling and performance optimization
- Multi-server load balancing and caching strategies
- Adding more ERDDAP servers to erddaps.json

## License

This project is open source and available under the MIT License.