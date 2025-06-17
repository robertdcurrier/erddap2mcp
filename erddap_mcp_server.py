#!/usr/bin/env python3

import asyncio
import sys
import traceback
import aiohttp
import urllib.parse
import csv
import io
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp import types

def debug_print(msg):
    """Print debug info to stderr so it shows up in MCP logs."""
    print(f"DEBUG: {msg}", file=sys.stderr, flush=True)

async def search_erddap_datasets(query: str, server_url: str) -> str:
    """Search ERDDAP datasets using the search API."""
    try:
        # Clean up server URL
        if not server_url.endswith('/'):
            server_url += '/'
        
        # Build search URL
        search_url = f"{server_url}search/index.csv"
        params = {
            'page': '1',
            'itemsPerPage': '10',  # Limit results for readability
            'searchFor': query
        }
        
        debug_print(f"Searching ERDDAP: {search_url} with query: {query}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, params=params, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    return parse_erddap_search_results(content, query)
                else:
                    return f"Error: ERDDAP server returned status {response.status}"
                    
    except asyncio.TimeoutError:
        return f"Error: Timeout connecting to ERDDAP server at {server_url}"
    except Exception as e:
        debug_print(f"ERDDAP search error: {e}")
        return f"Error searching ERDDAP: {str(e)}"

def parse_erddap_search_results(csv_content: str, query: str) -> str:
    """Parse ERDDAP CSV search results into readable format."""
    lines = csv_content.strip().split('\n')
    
    if len(lines) < 2:
        return f"No datasets found matching '{query}'"
    
    # Skip header line
    results = []
    for line in lines[1:]:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 6:
                dataset_id = parts[0].strip('"')
                title = parts[1].strip('"')
                summary = parts[2].strip('"')[:100] + "..." if len(parts[2]) > 100 else parts[2].strip('"')
                
                results.append(f"• {dataset_id}: {title}\n  {summary}")
    
    if not results:
        return f"No datasets found matching '{query}'"
    
    return f"Found {len(results)} datasets matching '{query}':\n\n" + "\n\n".join(results)

async def get_dataset_info(dataset_id: str, server_url: str) -> str:
    """Get detailed information about a specific ERDDAP dataset."""
    try:
        # Clean up server URL
        if not server_url.endswith('/'):
            server_url += '/'
        
        # Build dataset info URL
        info_url = f"{server_url}info/{dataset_id}/index.csv"
        
        debug_print(f"Getting dataset info: {info_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(info_url, timeout=30) as response:
                if response.status == 200:
                    content = await response.text()
                    return parse_dataset_info_NEW(content, dataset_id)
                else:
                    return f"Error: Could not get info for dataset '{dataset_id}' (status {response.status})"
                    
    except asyncio.TimeoutError:
        return f"Error: Timeout getting info for dataset '{dataset_id}'"
    except Exception as e:
        debug_print(f"Dataset info error: {e}")
        return f"Error getting dataset info: {str(e)}"

def parse_dataset_info_NEW(csv_content: str, dataset_id: str) -> str:
    """Parse ERDDAP dataset info CSV - NEW VERSION."""
    lines = csv_content.strip().split('\n')
    
    if len(lines) < 2:
        return f"No information found for dataset '{dataset_id}'"
    
    # Parse CSV structure: Row Type,Variable Name,Attribute Name,Data Type,Value
    global_attrs = {}
    variable_info = {}
    
    # Use proper CSV parsing
    csv_reader = csv.reader(lines)
    header = next(csv_reader)  # Skip header
    
    for row in csv_reader:
        if len(row) >= 5:
            row_type, var_name, attr_name, data_type, value = row[0], row[1], row[2], row[3], row[4]
            
            if row_type == "attribute" and var_name == "NC_GLOBAL":
                global_attrs[attr_name] = value
            elif row_type == "variable" and var_name:
                if var_name not in variable_info:
                    variable_info[var_name] = {}
            elif row_type == "attribute" and var_name:
                if var_name not in variable_info:
                    variable_info[var_name] = {}
                variable_info[var_name][attr_name] = value
    
    # Format the output
    result = f"🌊 Dataset: {dataset_id}\n\n"
    
    # Show key metadata
    if global_attrs:
        result += "📋 **Dataset Information:**\n"
        
        # Show title
        if 'title' in global_attrs:
            result += f"**Title:** {global_attrs['title']}\n\n"
        
        # Show summary
        if 'summary' in global_attrs:
            summary = global_attrs['summary']
            if len(summary) > 300:
                summary = summary[:300] + "..."
            result += f"**Summary:** {summary}\n\n"
        
        # Show institution and creator
        if 'institution' in global_attrs:
            result += f"**Institution:** {global_attrs['institution']}\n"
        if 'creator_name' in global_attrs:
            result += f"**Creator:** {global_attrs['creator_name']}\n"
        if 'publisher_name' in global_attrs:
            result += f"**Publisher:** {global_attrs['publisher_name']}\n"
        
        # Show platform and instrument
        if 'platform' in global_attrs:
            result += f"**Platform:** {global_attrs['platform']}\n"
        if 'instrument' in global_attrs:
            result += f"**Instrument:** {global_attrs['instrument']}\n"
        
        # Show time coverage
        if 'time_coverage_start' in global_attrs:
            result += f"**Time Start:** {global_attrs['time_coverage_start']}\n"
        if 'time_coverage_end' in global_attrs:
            result += f"**Time End:** {global_attrs['time_coverage_end']}\n"
        
        # Show geographic coverage
        if all(k in global_attrs for k in ['geospatial_lat_min', 'geospatial_lat_max', 'geospatial_lon_min', 'geospatial_lon_max']):
            result += f"**Location:** {global_attrs['geospatial_lat_min']}°N to {global_attrs['geospatial_lat_max']}°N, "
            result += f"{global_attrs['geospatial_lon_min']}°E to {global_attrs['geospatial_lon_max']}°E\n"
        
        result += "\n"
    
    # Show variables
    if variable_info:
        result += f"🔬 **Variables ({len(variable_info)}):**\n"
        for var_name, var_attrs in list(variable_info.items())[:15]:
            long_name = var_attrs.get('long_name', var_name)
            units = var_attrs.get('units', '')
            result += f"• **{var_name}**: {long_name}"
            if units and units not in ['1', '']:
                result += f" ({units})"
            result += "\n"
        
        if len(variable_info) > 15:
            result += f"• ... and {len(variable_info) - 15} more variables\n"
    
    return result

# Create the server instance with NEW name to force refresh
app = Server("erddap-dataset-server")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    debug_print("NEW VERSION: list_tools called!")
    return [
        types.Tool(
            name="test_tool",
            description="A simple test tool",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Test message"}
                },
                "required": ["message"]
            }
        ),
        types.Tool(
            name="search_datasets",
            description="Search ERDDAP datasets",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://gcoos5.geos.tamu.edu/erddap/"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_dataset_info",
            description="Get detailed information about a specific ERDDAP dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {"type": "string", "description": "Dataset ID"},
                    "server_url": {"type": "string", "description": "ERDDAP server URL", "default": "https://gcoos5.geos.tamu.edu/erddap/"}
                },
                "required": ["dataset_id"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    debug_print(f"NEW VERSION: call_tool called with name={name}, args={arguments}")
    
    if name == "test_tool":
        message = arguments.get("message", "No message provided")
        return [types.TextContent(
            type="text",
            text=f"NEW VERSION Test tool received: {message}"
        )]
    elif name == "search_datasets":
        query = arguments.get("query", "")
        server_url = arguments.get("server_url", "https://gcoos5.geos.tamu.edu/erddap/")
        
        result = await search_erddap_datasets(query, server_url)
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    elif name == "get_dataset_info":
        dataset_id = arguments.get("dataset_id", "")
        server_url = arguments.get("server_url", "https://gcoos5.geos.tamu.edu/erddap/")
        
        result = await get_dataset_info(dataset_id, server_url)
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point for the MCP server."""
    debug_print("NEW VERSION: Starting main() function")
    
    try:
        debug_print("Creating stdio streams")
        async with stdio_server() as (read_stream, write_stream):
            debug_print("stdio streams created successfully")
            
            from mcp.server.models import InitializationOptions
            
            initialization_options = InitializationOptions(
                server_name="erddap-dataset-server",
                server_version="2.0.0",
                capabilities=types.ServerCapabilities(
                    tools=types.ToolsCapability(listChanged=True)
                )
            )
            
            debug_print(f"Starting server with initialization options: {initialization_options}")
            debug_print("NEW VERSION Server is now running and waiting for connections...")
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
                    "server_name": "erddap-dataset-server",
                    "server_version": "2.0.0"
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
    debug_print("NEW VERSION: Script starting")
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