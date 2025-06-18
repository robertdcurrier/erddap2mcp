#!/usr/bin/env python3

import asyncio
import sys
import traceback
import json
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
        # Dataset Discovery Tools
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
            name="get_dataset_variables",
            description="Get all variables and their attributes for a dataset",
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
            name="get_var_by_attr",
            description="Find variables in a dataset by their attributes",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "attr_name": {"type": "string", "description": "Attribute name to search for (e.g., 'standard_name')"},
                    "attr_value": {"type": "string", "description": "Attribute value to match"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                    "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                },
                "required": ["dataset_id", "attr_name", "attr_value"]
            }
        ),
        
        # URL Generation Tools
        types.Tool(
            name="get_search_url",
            description="Generate a search URL for ERDDAP datasets",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "response_format": {"type": "string", "description": "Response format (csv, json, etc.)", "default": "csv"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_info_url",
            description="Generate an info URL for a specific dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "response_format": {"type": "string", "description": "Response format (csv, json, html)", "default": "csv"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"}
                },
                "required": ["dataset_id"]
            }
        ),
        types.Tool(
            name="get_download_url",
            description="Generate a download URL for dataset with specified parameters",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "variables": {"type": "array", "items": {"type": "string"}, "description": "Variables to download"},
                    "constraints": {"type": "object", "description": "Constraints dict (e.g., {'time>=': '2020-01-01', 'latitude>': 30})"},
                    "response_format": {"type": "string", "description": "Response format (csv, nc, json, etc.)", "default": "csv"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                    "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        # Data Access Tools
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
        ),
        types.Tool(
            name="download_file",
            description="Download a dataset file in a specific format",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "variables": {"type": "array", "items": {"type": "string"}, "description": "Variables to download"},
                    "constraints": {"type": "object", "description": "Constraints dict (e.g., {'time>=': '2020-01-01', 'latitude>': 30})"},
                    "file_format": {"type": "string", "description": "File format (csv, nc, json, mat, etc.)", "default": "csv"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://coastwatch.pfeg.noaa.gov/erddap"},
                    "protocol": {"type": "string", "description": "Protocol type (tabledap or griddap)", "default": "tabledap"}
                },
                "required": ["dataset_id"]
            }
        ),
        
        # Utility Tools
        types.Tool(
            name="list_servers",
            description="List some well-known ERDDAP servers",
            inputSchema={
                "type": "object",
                "properties": {}
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
        
        elif name == "get_dataset_variables":
            dataset_id = arguments.get("dataset_id", "")
            protocol = arguments.get("protocol", "tabledap")
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            
            info_url = e.get_info_url(response="csv")
            try:
                df = pd.read_csv(info_url)
                variables = df[df['Row Type'] == 'variable']['Variable Name'].unique()
                
                result = f"**Variables in dataset {dataset_id}:**\n\n"
                for var in variables:
                    var_attrs = df[df['Variable Name'] == var]
                    attrs_dict = {}
                    for _, row in var_attrs.iterrows():
                        if row['Attribute Name'] and pd.notna(row['Value']):
                            attrs_dict[row['Attribute Name']] = row['Value']
                    
                    result += f"**{var}**\n"
                    for attr, value in list(attrs_dict.items())[:5]:
                        result += f"  - {attr}: {value}\n"
                    if len(attrs_dict) > 5:
                        result += f"  - ... and {len(attrs_dict) - 5} more attributes\n"
                    result += "\n"
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error getting variables: {str(e)}")]
        
        elif name == "get_var_by_attr":
            dataset_id = arguments.get("dataset_id", "")
            attr_name = arguments.get("attr_name", "")
            attr_value = arguments.get("attr_value", "")
            protocol = arguments.get("protocol", "tabledap")
            
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            
            try:
                # Use erddapy's get_var_by_attr method
                matching_vars = e.get_var_by_attr(attr_name=attr_name, value=attr_value)
                
                if not matching_vars:
                    return [types.TextContent(type="text", text=f"No variables found with {attr_name}='{attr_value}'")]
                
                result = f"Variables with {attr_name}='{attr_value}':\n"
                for var in matching_vars:
                    result += f"• {var}\n"
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error finding variables: {str(e)}")]
        
        elif name == "get_search_url":
            query = arguments.get("query", "")
            response_format = arguments.get("response_format", "csv")
            
            e = get_or_create_erddap(server_url)
            url = e.get_search_url(response=response_format, search_for=query)
            
            return [types.TextContent(type="text", text=f"Search URL:\n{url}")]
        
        elif name == "get_info_url":
            dataset_id = arguments.get("dataset_id", "")
            response_format = arguments.get("response_format", "csv")
            
            e = get_or_create_erddap(server_url)
            e.dataset_id = dataset_id
            url = e.get_info_url(response=response_format)
            
            return [types.TextContent(type="text", text=f"Info URL:\n{url}")]
        
        elif name == "get_download_url":
            dataset_id = arguments.get("dataset_id", "")
            variables = arguments.get("variables", [])
            constraints = arguments.get("constraints", {})
            response_format = arguments.get("response_format", "csv")
            protocol = arguments.get("protocol", "tabledap")
            
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            e.response = response_format
            
            if variables:
                e.variables = variables
            
            if constraints:
                e.constraints = constraints
            
            url = e.get_download_url()
            
            return [types.TextContent(type="text", text=f"Download URL:\n{url}")]
        
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
        
        elif name == "download_file":
            dataset_id = arguments.get("dataset_id", "")
            variables = arguments.get("variables", [])
            constraints = arguments.get("constraints", {})
            file_format = arguments.get("file_format", "csv")
            protocol = arguments.get("protocol", "tabledap")
            
            e = get_or_create_erddap(server_url, protocol)
            e.dataset_id = dataset_id
            e.response = file_format
            
            if variables:
                e.variables = variables
            
            if constraints:
                e.constraints = constraints
            
            try:
                # Get download URL
                url = e.get_download_url()
                
                # For demonstration, we'll just return the URL and file info
                result = f"**Download ready for {dataset_id}**\n\n"
                result += f"Format: {file_format}\n"
                if variables:
                    result += f"Variables: {', '.join(variables)}\n"
                if constraints:
                    result += f"Constraints: {json.dumps(constraints, indent=2)}\n"
                result += f"\nDownload URL:\n{url}"
                
                return [types.TextContent(type="text", text=result)]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Error preparing download: {str(e)}")]
        
        elif name == "list_servers":
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
            
            return [types.TextContent(type="text", text=result)]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        debug_print(f"Error in tool {name}: {e}")
        debug_print(f"Traceback: {traceback.format_exc()}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    """Main entry point for the MCP server."""
    debug_print("Starting erddapy MCP server")
    
    try:
        debug_print("Creating stdio streams")
        async with stdio_server() as (read_stream, write_stream):
            debug_print("stdio streams created successfully")
            
            from mcp.server.models import InitializationOptions
            
            initialization_options = InitializationOptions(
                server_name="erddapy-mcp-server",
                server_version="1.0.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability(listChanged=True)
                )
            )
            
            debug_print(f"Starting server with initialization options: {initialization_options}")
            debug_print("Server is now running and waiting for connections...")
            await app.run(
                read_stream, 
                write_stream, 
                initialization_options
            )
            debug_print("Server run completed")
            
    except ImportError:
        debug_print("InitializationOptions not found, trying simple dict")
        try:
            async with stdio_server() as (read_stream, write_stream):
                debug_print("stdio streams created successfully")
                
                initialization_options = {
                    "server_name": "erddapy-mcp-server",
                    "server_version": "1.0.0"
                }
                
                debug_print("Starting server with simple initialization options")
                await app.run(
                    read_stream, 
                    write_stream, 
                    initialization_options
                )
        except Exception as e:
            debug_print(f"Fallback failed: {e}")
            debug_print(f"Full traceback: {traceback.format_exc()}")
            sys.exit(1)
            
    except Exception as e:
        debug_print(f"Exception in main(): {e}")
        debug_print(f"Full traceback: {traceback.format_exc()}")
        sys.exit(1)

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
