# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides tools for searching and accessing ERDDAP (Environmental Research Division's Data Access Program) oceanographic datasets. The server exposes ERDDAP functionality through MCP tools that can be used by AI assistants.

## Architecture

The main server is implemented in: `erddapy_mcp_server.py`

Key components:
- **MCP Server Setup**: Uses the `mcp` library to create a stdio-based server
- **ERDDAP Integration**: Uses the official `erddapy` Python client library
- **Data Processing**: Handles pandas DataFrames for data analysis and preview
- **Tool Handlers**: Implements 10+ MCP tools for comprehensive ERDDAP access

## Development Commands

Install dependencies:
```bash
# Install required dependencies
pip install erddapy mcp pandas

# Run the server
python erddapy_mcp_server.py
```

## Available Tools

### Discovery Tools
1. **list_servers**: Show well-known ERDDAP servers
2. **search_datasets**: Search ERDDAP datasets by query string
3. **get_dataset_info**: Get detailed metadata for a specific dataset ID
4. **get_dataset_variables**: List all variables and their attributes
5. **get_var_by_attr**: Find variables by specific attributes

### URL Generation Tools
6. **get_search_url**: Generate search URLs
7. **get_info_url**: Generate dataset info URLs
8. **get_download_url**: Generate download URLs with constraints

### Data Access Tools
9. **to_pandas**: Download data and return as pandas DataFrame preview
10. **download_file**: Prepare downloads in various formats (CSV, NetCDF, JSON, etc.)

## Important Parameters

Most tools accept these common parameters:
- `server_url`: ERDDAP server URL (defaults to NOAA CoastWatch)
- `protocol`: Either "tabledap" (tabular data) or "griddap" (gridded data)
- `dataset_id`: The dataset identifier
- `variables`: List of variables to retrieve
- `constraints`: Dictionary of constraints (e.g., time/space bounds)

## Debugging

The server includes debug output that goes to stderr. Debug messages are prefixed with "DEBUG:" and can be monitored in MCP client logs.

## Default Configuration

- Default ERDDAP server: `https://coastwatch.pfeg.noaa.gov/erddap`
- Server name: `erddapy-mcp-server`
- Communication: stdio (standard input/output)
- Protocol default: `tabledap` (use `griddap` for gridded datasets)

## Important Implementation Details

- Uses erddapy library for all ERDDAP interactions
- Maintains ERDDAP instance cache for performance
- Handles both tabledap and griddap protocols
- Includes griddap_initialize() for proper gridded data handling
- Error handling includes timeouts and meaningful error messages
- Data previews include summary statistics for quick analysis