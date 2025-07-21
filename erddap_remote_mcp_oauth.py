"""
ERDDAP MCP Server with OAuth Support
Implements OAuth2 flow for Claude Desktop compatibility
"""

from fastapi import FastAPI, Request, HTTPException, Query, Depends, Header
from fastapi.responses import StreamingResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import secrets
from urllib.parse import urlencode, parse_qs
import uuid

# Import ERDDAP functionality
from erddapy import ERDDAP
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ERDDAP Remote MCP Server",
    description="MCP server with OAuth for ERDDAP oceanographic data tools",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store auth sessions and tokens
auth_sessions: Dict[str, Dict[str, Any]] = {}
access_tokens: Dict[str, Dict[str, Any]] = {}

# Global dictionary to store ERDDAP instances per server
erddap_instances: Dict[str, ERDDAP] = {}

def get_or_create_erddap(server_url: str, protocol: str = "tabledap") -> ERDDAP:
    """Get existing or create new ERDDAP instance for a server."""
    key = f"{server_url}_{protocol}"
    if key not in erddap_instances:
        e = ERDDAP(server=server_url)
        e.protocol = protocol
        erddap_instances[key] = e
    return erddap_instances[key]


class ERDDAPMCPServer:
    """MCP server for ERDDAP oceanographic tools"""
    
    def __init__(self):
        self.tools = {
            "search_datasets": {
                "description": "Search for datasets on an ERDDAP server",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query string"},
                        "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"}
                    },
                    "required": ["query"]
                }
            },
            "get_dataset_info": {
                "description": "Get detailed metadata information about a specific dataset",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {"type": "string", "description": "Dataset ID"},
                        "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                        "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                    },
                    "required": ["dataset_id"]
                }
            },
            "list_servers": {
                "description": "List some well-known ERDDAP servers",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            "to_pandas": {
                "description": "Download data and return as a pandas DataFrame (CSV format)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dataset_id": {"type": "string", "description": "Dataset ID"},
                        "variables": {"type": "array", "items": {"type": "string"}, "description": "Variables to download"},
                        "constraints": {"type": "object", "description": "Constraints dict (e.g., {'time>=': '2020-01-01', 'latitude>': 30})"},
                        "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                        "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                    },
                    "required": ["dataset_id"]
                }
            }
        }
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle JSON-RPC 2.0 requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        logger.info(f"Method: {method}, ID: {request_id}")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {
                        "tools": {
                            "listTools": {},
                            "callTool": {}
                        }
                    },
                    "serverInfo": {
                        "name": "erddap-mcp-server",
                        "version": "1.0.0"
                    }
                }
            }
        
        elif method == "notifications/initialized":
            return {
                "jsonrpc": "2.0", 
                "id": None,
                "result": {}
            }
        
        elif method == "tools/list":
            tools_list = [
                {
                    "name": name,
                    "description": tool["description"],
                    "inputSchema": tool["inputSchema"]
                }
                for name, tool in self.tools.items()
            ]
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools_list}
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            args = params.get("arguments", {})
            
            try:
                if tool_name == "list_servers":
                    result = await self._list_servers()
                elif tool_name == "search_datasets":
                    result = await self._search_datasets(args)
                elif tool_name == "get_dataset_info":
                    result = await self._get_dataset_info(args)
                elif tool_name == "to_pandas":
                    result = await self._to_pandas(args)
                else:
                    result = f"Unknown tool: {tool_name}"
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{"type": "text", "text": result}]
                    }
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution failed: {str(e)}"
                    }
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    async def _list_servers(self) -> str:
        """List well-known ERDDAP servers"""
        servers = [
            ("NOAA CoastWatch", "https://coastwatch.pfeg.noaa.gov/erddap"),
            ("IOOS ERDDAP", "https://erddap.ioos.us/erddap"),
            ("Marine Institute Ireland", "https://erddap.marine.ie/erddap"),
            ("ONC ERDDAP", "https://data.oceannetworks.ca/erddap"),
            ("GCOOS ERDDAP", "https://gcoos5.geos.tamu.edu/erddap"),
            ("EMODnet Physics", "https://erddap.emodnet-physics.eu/erddap"),
            ("IOOS GDAC", "https://gliders.ioos.us/erddap/"),
        ]
        
        result = "**Well-known ERDDAP servers:**\n\n"
        for name, url in servers:
            result += f"• **{name}**: {url}\n"
        
        return result
    
    async def _search_datasets(self, args: Dict[str, Any]) -> str:
        """Search for datasets on an ERDDAP server"""
        query = args.get("query", "")
        server_url = args.get("server_url", "https://coastwatch.pfeg.noaa.gov/erddap")
        
        if not query:
            raise ValueError("Query parameter is required")
        
        try:
            e = get_or_create_erddap(server_url)
            search_url = e.get_search_url(response="csv", search_for=query)
            df = pd.read_csv(search_url)
            
            if df.empty:
                return f"No datasets found matching '{query}'"
            
            # Format results
            result = f"Found {len(df)} datasets matching '{query}':\n\n"
            for idx, row in df.head(10).iterrows():
                dataset_id = row.get('Dataset ID', 'Unknown')
                title = row.get('Title', 'No title')
                result += f"• **{dataset_id}**: {title}\n"
            
            if len(df) > 10:
                result += f"\n... and {len(df) - 10} more datasets"
            
            return result
            
        except Exception as e:
            raise Exception(f"Error searching datasets: {str(e)}")
    
    async def _get_dataset_info(self, args: Dict[str, Any]) -> str:
        """Get detailed metadata for a specific dataset"""
        dataset_id = args.get("dataset_id", "")
        protocol = args.get("protocol", "tabledap")
        server_url = args.get("server_url", "https://coastwatch.pfeg.noaa.gov/erddap")
        
        if not dataset_id:
            raise ValueError("Dataset ID is required")
        
        try:
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            
            # Get info URL and fetch metadata
            info_url = e.get_info_url(response="csv")
            df = pd.read_csv(info_url)
            
            # Parse the info dataframe
            global_attrs = df[df['Variable Name'] == 'NC_GLOBAL']
            variables = df[df['Row Type'] == 'variable']['Variable Name'].unique()
            
            result = f"🌊 **Dataset: {dataset_id}**\n\n"
            
            # Extract key metadata
            title = global_attrs[global_attrs['Attribute Name'] == 'title']['Value'].values
            if len(title) > 0:
                result += f"**Title:** {title[0]}\n\n"
            
            summary = global_attrs[global_attrs['Attribute Name'] == 'summary']['Value'].values
            if len(summary) > 0:
                result += f"**Summary:** {summary[0][:300]}...\n\n"
            
            # Time coverage
            time_start = global_attrs[global_attrs['Attribute Name'] == 'time_coverage_start']['Value'].values
            time_end = global_attrs[global_attrs['Attribute Name'] == 'time_coverage_end']['Value'].values
            if len(time_start) > 0 and len(time_end) > 0:
                result += f"**Time Coverage:** {time_start[0]} to {time_end[0]}\n\n"
            
            # Variables
            result += f"**Variables ({len(variables)}):**\n"
            for var in variables[:10]:
                var_attrs = df[df['Variable Name'] == var]
                long_name = var_attrs[var_attrs['Attribute Name'] == 'long_name']['Value'].values
                units = var_attrs[var_attrs['Attribute Name'] == 'units']['Value'].values
                
                var_desc = var
                if len(long_name) > 0:
                    var_desc = f"{var}: {long_name[0]}"
                if len(units) > 0:
                    var_desc += f" ({units[0]})"
                result += f"• {var_desc}\n"
            
            if len(variables) > 10:
                result += f"• ... and {len(variables) - 10} more variables"
            
            return result
            
        except Exception as e:
            raise Exception(f"Error getting dataset info: {str(e)}")
    
    async def _to_pandas(self, args: Dict[str, Any]) -> str:
        """Download data and return as pandas DataFrame preview"""
        dataset_id = args.get("dataset_id", "")
        variables = args.get("variables", [])
        constraints = args.get("constraints", {})
        protocol = args.get("protocol", "tabledap")
        server_url = args.get("server_url", "https://coastwatch.pfeg.noaa.gov/erddap")
        
        if not dataset_id:
            raise ValueError("Dataset ID is required")
        
        try:
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            e.response = "csv"
            
            if variables:
                e.variables = variables
            
            if constraints:
                e.constraints = constraints
            
            # Initialize griddap if needed
            if protocol == "griddap":
                e.griddap_initialize()
                
            # Download data as pandas DataFrame
            df = e.to_pandas()
            
            # Format the output
            result = f"**Data from {dataset_id}**\n\n"
            result += f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n"
            result += "**Columns:** " + ", ".join(df.columns.tolist()) + "\n\n"
            result += "**First 5 rows:**\n```\n"
            result += df.head().to_string() + "\n```\n\n"
            result += "**Summary statistics:**\n```\n"
            result += df.describe().to_string() + "\n```"
            
            return result
            
        except Exception as e:
            raise Exception(f"Error downloading data: {str(e)}")


# Initialize MCP server
mcp_server = ERDDAPMCPServer()


@app.get("/")
async def root():
    """Root endpoint with info and auth instructions"""
    return HTMLResponse("""
    <html>
        <head>
            <title>ERDDAP MCP Server</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .status { color: green; font-weight: bold; }
                code { background: #f0f0f0; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🌊 ERDDAP MCP Server</h1>
            <p class="status">✓ Server is running</p>
            
            <h2>About</h2>
            <p>This MCP server provides tools for accessing oceanographic data through ERDDAP servers.</p>
            
            <h2>Available Tools</h2>
            <ul>
                <li><strong>search_datasets</strong> - Search for datasets on any ERDDAP server</li>
                <li><strong>get_dataset_info</strong> - Get detailed metadata about a specific dataset</li>
                <li><strong>list_servers</strong> - List well-known ERDDAP servers</li>
                <li><strong>to_pandas</strong> - Download data and preview as DataFrame</li>
            </ul>
            
            <h2>Connection Info</h2>
            <p>Transport: <code>streamable-http</code></p>
            <p>Auth: OAuth2 (automatic via Claude Desktop)</p>
            
            <h2>Setup</h2>
            <p>Add this server URL to Claude Desktop via Settings → Connectors</p>
        </body>
    </html>
    """)


@app.get("/.well-known/oauth-authorization-server")
async def oauth_metadata(request: Request):
    """OAuth 2.0 Authorization Server Metadata"""
    base_url = str(request.base_url).rstrip('/')
    
    return {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],  # Public client
        "service_documentation": base_url,
        "ui_locales_supported": ["en-US"]
    }


@app.post("/oauth/register")
async def oauth_register(request: Request):
    """OAuth 2.0 Dynamic Client Registration"""
    body = await request.json()
    
    # Generate a unique client ID
    client_id = f"client_{uuid.uuid4().hex[:16]}"
    
    # Store client registration (in production, use a database)
    # For this example, we'll accept any registration
    
    response = {
        "client_id": client_id,
        "client_id_issued_at": int(datetime.now().timestamp()),
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "redirect_uris": body.get("redirect_uris", []),
        "token_endpoint_auth_method": "none",  # Public client
        "application_type": "web"
    }
    
    # If client_name was provided, include it
    if "client_name" in body:
        response["client_name"] = body["client_name"]
    
    return response


@app.get("/oauth/authorize")
async def oauth_authorize(
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(...),
    response_type: str = Query(...),
    code_challenge: str = Query(None),
    code_challenge_method: str = Query(None)
):
    """OAuth2 authorization endpoint"""
    logger.info(f"OAuth authorize: client_id={client_id}, redirect_uri={redirect_uri}")
    
    # For this example, we'll auto-approve all requests
    # In production, you'd show a consent screen here
    
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    
    # Store session with PKCE challenge if provided
    auth_sessions[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "created_at": datetime.now(),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": code_challenge_method
    }
    
    # Redirect back with auth code
    params = {
        "code": auth_code,
        "state": state
    }
    
    redirect_url = f"{redirect_uri}?{urlencode(params)}"
    
    # Return a simple auto-submit form for automatic redirect
    return HTMLResponse(f"""
    <html>
        <head>
            <title>Authorizing...</title>
        </head>
        <body>
            <h2>Authorizing ERDDAP MCP Server...</h2>
            <p>Redirecting back to Claude Desktop...</p>
            <script>
                window.location.href = "{redirect_url}";
            </script>
        </body>
    </html>
    """)


@app.post("/oauth/token")
async def oauth_token(request: Request):
    """OAuth2 token endpoint"""
    form_data = await request.form()
    grant_type = form_data.get("grant_type")
    
    if grant_type == "authorization_code":
        code = form_data.get("code")
        client_id = form_data.get("client_id")
        code_verifier = form_data.get("code_verifier")  # PKCE
        
        # Validate auth code
        session = auth_sessions.get(code)
        if not session:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        # Check if code is expired (5 minutes)
        if datetime.now() - session["created_at"] > timedelta(minutes=5):
            del auth_sessions[code]
            raise HTTPException(status_code=400, detail="Authorization code expired")
        
        # Validate client_id
        if session["client_id"] != client_id:
            raise HTTPException(status_code=400, detail="Invalid client_id")
        
        # TODO: Validate PKCE code_verifier against code_challenge if present
        
        # Generate access token
        access_token = secrets.token_urlsafe(32)
        access_tokens[access_token] = {
            "client_id": client_id,
            "created_at": datetime.now(),
            "scope": "mcp"
        }
        
        # Clean up used auth code
        del auth_sessions[code]
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "mcp"
        }
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant type")


async def verify_token(authorization: str = Header(None)) -> str:
    """Verify OAuth token for protected endpoints"""
    if not authorization or not authorization.startswith("Bearer "):
        return None  # No auth required for MCP currently
    
    token = authorization.split(" ")[1]
    if token not in access_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Check token expiration (1 hour for this example)
    token_data = access_tokens[token]
    if datetime.now() - token_data["created_at"] > timedelta(hours=1):
        del access_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    return token


@app.post("/")
async def mcp_endpoint(request: Request, token: Optional[str] = Depends(verify_token)):
    """Main MCP endpoint - handles all MCP protocol messages"""
    body = await request.json()
    logger.info(f"Request: {json.dumps(body, indent=2)}")
    
    # Process request
    response = await mcp_server.handle_request(body)
    logger.info(f"Response: {json.dumps(response, indent=2)}")
    
    return response


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "erddap-mcp-server",
        "auth": "oauth2"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)