#!/usr/bin/env python3

import asyncio
import sys
import traceback
import json
import os
from typing import Optional, Dict, Any, List
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp import types
from erddapy import ERDDAP
import pandas as pd
import io

def debug_print(msg):
    """Print debug info to stderr so it shows up in MCP logs."""
    print(f"DEBUG: {msg}", file=sys.stderr, flush=True)

def load_erddap_servers():
    """Load ERDDAP servers from erddaps.json file."""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'erddaps.json')
        
        with open(json_path, 'r') as f:
            servers = json.load(f)
        
        debug_print(f"Loaded {len(servers)} ERDDAP servers from erddaps.json")
        return servers
    except FileNotFoundError:
        debug_print("Warning: erddaps.json not found, using fallback list")
        # Fallback to minimal list if file not found
        return [
            {
                "name": "NOAA CoastWatch West Coast",
                "short_name": "CSWC",
                "url": "https://coastwatch.pfeg.noaa.gov/erddap/",
                "public": True
            },
            {
                "name": "IOOS ERDDAP",
                "short_name": "IOOS",
                "url": "https://erddap.ioos.us/erddap/",
                "public": True
            }
        ]
    except Exception as e:
        debug_print(f"Error loading erddaps.json: {e}")
        return []

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

# Create the server instance
app = Server("erddapy-mcp-server")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    debug_print("Listing erddapy tools")
    return [
        types.Tool(
            name="list_servers",
            description="List some well-known ERDDAP servers",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="search_datasets",
            description="Search for datasets on an ERDDAP server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_dataset_info",
            description="Get detailed metadata information about a specific dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                    "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="to_pandas",
            description="Download data and return as a pandas DataFrame (CSV format)",
            inputSchema={
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
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    debug_print(f"Tool called: {name} with args: {arguments}")
    
    try:
        # Get server URL from arguments
        server_url = arguments.get("server_url", "https://coastwatch.pfeg.noaa.gov/erddap")
        
        if name == "search_datasets":
            query = arguments.get("query", "")
            e = get_or_create_erddap(server_url)
            
            # Use erddapy's search functionality
            search_url = e.get_search_url(response="csv", search_for=query)
            debug_print(f"Search URL: {search_url}")
            
            # For search, we'll use pandas to read the CSV directly
            try:
                df = pd.read_csv(search_url)
                if df.empty:
                    return [types.TextContent(type="text", text=f"No datasets found matching '{query}'")]
                
                # Format results
                result = f"Found {len(df)} datasets matching '{query}':\n\n"
                for idx, row in df.head(10).iterrows():
                    dataset_id = row.get('Dataset ID', 'Unknown')
                    title = row.get('Title', 'No title')
                    result += f"• **{dataset_id}**: {title}\n"
                
                if len(df) > 10:
                    result += f"\n... and {len(df) - 10} more datasets"
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error searching datasets: {str(e)}")]
        
        elif name == "get_dataset_info":
            dataset_id = arguments.get("dataset_id", "")
            protocol = arguments.get("protocol", "tabledap")
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            
            # Get info URL and fetch metadata
            info_url = e.get_info_url(response="csv")
            debug_print(f"Info URL: {info_url}")
            
            try:
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
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error getting dataset info: {str(e)}")]
        
        elif name == "to_pandas":
            dataset_id = arguments.get("dataset_id", "")
            variables = arguments.get("variables", [])
            constraints = arguments.get("constraints", {})
            protocol = arguments.get("protocol", "tabledap")
            
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            e.response = "csv"
            
            if variables:
                e.variables = variables
            
            if constraints:
                e.constraints = constraints
            
            try:
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
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error downloading data: {str(e)}")]
        
        elif name == "list_servers":
            servers = load_erddap_servers()
            
            if not servers:
                return [types.TextContent(type="text", text="Error: Could not load ERDDAP servers list")]
            
            result = f"**Available ERDDAP servers ({len(servers)} total):**\n\n"
            
            # Group by public/private
            public_servers = [s for s in servers if s.get('public', True)]
            private_servers = [s for s in servers if not s.get('public', True)]
            
            if public_servers:
                result += f"**Public Servers ({len(public_servers)}):**\n\n"
                for server in public_servers[:20]:  # Show first 20
                    result += f"**{server['name']}**"
                    if server.get('short_name'):
                        result += f" ({server['short_name']})"
                    result += f"\nURL: {server['url']}\n\n"
                
                if len(public_servers) > 20:
                    result += f"... and {len(public_servers) - 20} more public servers\n\n"
            
            if private_servers:
                result += f"\n**Private/Restricted Servers ({len(private_servers)}):**\n\n"
                for server in private_servers:
                    result += f"• {server['name']} ({server.get('short_name', 'N/A')})\n"
            
            result += "\n*Loaded from erddaps.json*"
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            debug_print(f"Unknown tool: {name}")
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        debug_print(f"Error in tool execution: {str(e)}")
        debug_print(f"Traceback: {traceback.format_exc()}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP server."""
    debug_print("Starting MCP server")
    
    # We need to check if we're already in an event loop
    try:
        # Get the current event loop
        loop = asyncio.get_running_loop()
        debug_print("Already in an event loop, using it")
    except RuntimeError:
        # No event loop running
        loop = None
        debug_print("No event loop running, will create one")
    
    try:
        debug_print("Creating stdio server")
        async with stdio_server() as (read_stream, write_stream):
            debug_print("stdio server created successfully")
            try:
                debug_print("Starting server.run()")
                await app.run(
                    read_stream,
                    write_stream,
                    app.create_initialization_options()
                )
                debug_print("Server run completed normally")
            except Exception as e:
                debug_print(f"Error during server.run(): {e}")
                debug_print(f"Full traceback: {traceback.format_exc()}")
                raise
    except Exception as e:
        debug_print(f"Error creating stdio server: {e}")
        debug_print(f"Full traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    debug_print("erddapy MCP server starting")
    try:
        asyncio.run(main())
        debug_print("Script completed normally")
    except KeyboardInterrupt:
        debug_print("Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        debug_print(f"Top-level exception: {e}")
        debug_print(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)