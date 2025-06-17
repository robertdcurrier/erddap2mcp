# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that provides tools for searching and accessing ERDDAP (Environmental Research Division's Data Access Program) oceanographic datasets. The server exposes ERDDAP functionality through MCP tools that can be used by AI assistants.

## Architecture

The entire server is implemented in a single file: `erddap_mcp_server.py`

Key components:
- **MCP Server Setup**: Uses the `mcp` library to create a stdio-based server
- **ERDDAP Integration**: Makes HTTP requests to ERDDAP servers using `aiohttp`
- **CSV Parsing**: Parses ERDDAP's CSV responses to extract dataset information
- **Tool Handlers**: Implements three MCP tools for dataset operations

## Development Commands

Since there are no package management files, dependencies must be installed manually:

```bash
# Install required dependencies
pip install mcp aiohttp

# Run the server
python erddap_mcp_server.py

# Make the file executable (if needed)
chmod +x erddap_mcp_server.py
./erddap_mcp_server.py
```

## Available Tools

1. **test_tool**: Simple test tool for verification
2. **search_datasets**: Search ERDDAP datasets by query string
3. **get_dataset_info**: Get detailed metadata for a specific dataset ID

## Debugging

The server includes debug output that goes to stderr. Debug messages are prefixed with "DEBUG:" and can be monitored in MCP client logs.

## Default Configuration

- Default ERDDAP server: `https://gcoos5.geos.tamu.edu/erddap/`
- Server name: `erddap-dataset-server`
- Communication: stdio (standard input/output)

## Important Implementation Details

- All async operations use `aiohttp` with 30-second timeouts
- CSV parsing handles ERDDAP's specific format with proper quote handling
- The server includes fallback initialization for different MCP library versions
- Error handling includes specific timeout and connection error messages