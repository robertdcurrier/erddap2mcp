# ERDDAP MCP Server

A Model Context Protocol (MCP) server that provides tools for searching and accessing ERDDAP (Environmental Research Division's Data Access Program) oceanographic datasets. This server enables AI assistants to interact with ERDDAP servers to discover and retrieve scientific data.

## Overview

ERDDAP is a data server that gives you a simple, consistent way to download subsets of scientific datasets in common file formats and make graphs and maps. This MCP server acts as a bridge between AI assistants and ERDDAP servers, allowing them to:

- Search for datasets using keywords
- Retrieve detailed metadata about specific datasets
- Access information about variables, time ranges, and geographic coverage

## Features

- **Dataset Search**: Search ERDDAP catalogs using keywords
- **Dataset Information**: Get comprehensive metadata about specific datasets
- **Async Operations**: Built with asyncio for efficient concurrent operations
- **Error Handling**: Robust error handling with timeouts and descriptive error messages
- **Debug Logging**: Comprehensive debug output for troubleshooting

## Requirements

- Python 3.7+
- `mcp` - Model Context Protocol SDK
- `aiohttp` - Asynchronous HTTP client library

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd erddap_mcp
```

2. Install dependencies:
```bash
pip install mcp aiohttp
```

3. Make the server executable:
```bash
chmod +x erddap_mcp_server.py
```

## Usage

### Running the Server

Run the server directly:
```bash
python erddap_mcp_server.py
```

Or as an executable:
```bash
./erddap_mcp_server.py
```

The server communicates via stdio (standard input/output) using the MCP protocol.

### Connecting to an MCP Client

This server is designed to be used with MCP-compatible AI assistants. Configure your MCP client to connect to this server using stdio transport.

## Available Tools

### 1. test_tool
A simple test tool for verifying the server connection.

**Parameters:**
- `message` (string, required): Test message to echo back

**Example:**
```json
{
  "name": "test_tool",
  "arguments": {
    "message": "Hello, ERDDAP!"
  }
}
```

### 2. search_datasets
Search ERDDAP datasets using keywords.

**Parameters:**
- `query` (string, required): Search keywords
- `server_url` (string, optional): ERDDAP server URL (defaults to GCOOS server)

**Example:**
```json
{
  "name": "search_datasets",
  "arguments": {
    "query": "temperature gulf of mexico",
    "server_url": "https://gcoos5.geos.tamu.edu/erddap/"
  }
}
```

**Returns:** Formatted list of matching datasets with IDs, titles, and summaries.

### 3. get_dataset_info
Get detailed information about a specific dataset.

**Parameters:**
- `dataset_id` (string, required): The ERDDAP dataset ID
- `server_url` (string, optional): ERDDAP server URL (defaults to GCOOS server)

**Example:**
```json
{
  "name": "get_dataset_info",
  "arguments": {
    "dataset_id": "tabs_b_salinity"
  }
}
```

**Returns:** Comprehensive dataset information including:
- Title and summary
- Institution and creator information
- Time coverage (start/end dates)
- Geographic coverage (bounding box)
- Available variables with units
- Platform and instrument details

## Code Structure

### Main Components

1. **Debug Printing**
   ```python
   def debug_print(msg):
   ```
   Outputs debug messages to stderr for monitoring in MCP client logs.

2. **ERDDAP Search Function**
   ```python
   async def search_erddap_datasets(query: str, server_url: str) -> str:
   ```
   - Constructs ERDDAP search API URL
   - Sends GET request with search parameters
   - Handles timeouts and errors
   - Returns parsed search results

3. **Search Results Parser**
   ```python
   def parse_erddap_search_results(csv_content: str, query: str) -> str:
   ```
   - Parses CSV response from ERDDAP search
   - Extracts dataset IDs, titles, and summaries
   - Formats results for readable output

4. **Dataset Info Function**
   ```python
   async def get_dataset_info(dataset_id: str, server_url: str) -> str:
   ```
   - Retrieves detailed dataset metadata
   - Handles API requests and errors
   - Returns formatted dataset information

5. **Dataset Info Parser**
   ```python
   def parse_dataset_info_NEW(csv_content: str, dataset_id: str) -> str:
   ```
   - Parses complex CSV structure with dataset attributes
   - Extracts global attributes and variable information
   - Formats data with emojis and markdown for readability

6. **MCP Server Setup**
   - Creates server instance with name "erddap-dataset-server"
   - Registers available tools with schemas
   - Handles tool invocations
   - Manages stdio communication

### Error Handling

The server includes comprehensive error handling:
- **Timeout errors**: 30-second timeout for all HTTP requests
- **HTTP errors**: Handles non-200 status codes
- **Connection errors**: Catches and reports connection failures
- **Parsing errors**: Handles malformed CSV responses
- **MCP errors**: Fallback initialization for different MCP versions

## Configuration

Default settings:
- **Server Name**: `erddap-dataset-server`
- **Server Version**: `2.0.0`
- **Default ERDDAP Server**: `https://gcoos5.geos.tamu.edu/erddap/`
- **Search Results Limit**: 10 items per page
- **HTTP Timeout**: 30 seconds

## ERDDAP Servers

This server can work with any ERDDAP installation. Some popular public ERDDAP servers:

- **GCOOS** (default): https://gcoos5.geos.tamu.edu/erddap/
- **NOAA CoastWatch**: https://coastwatch.pfeg.noaa.gov/erddap/
- **IOOS**: https://erddap.ioos.us/erddap/
- **Marine Institute Ireland**: https://erddap.marine.ie/erddap/

## Development

### Debug Mode

Debug messages are automatically output to stderr and will appear in MCP client logs. Look for lines prefixed with "DEBUG:".

### Extending the Server

To add new ERDDAP tools:

1. Create an async function for the ERDDAP operation
2. Add a parser function if needed for response processing
3. Register the tool in `handle_list_tools()`
4. Add the implementation in `handle_call_tool()`

### Testing

Test the server by running it and sending MCP protocol messages via stdin, or use an MCP-compatible client.

## Troubleshooting

1. **Server won't start**: Check Python version (3.7+) and ensure dependencies are installed
2. **Connection errors**: Verify the ERDDAP server URL is accessible
3. **No results**: Try different search terms or check the ERDDAP server's data catalog
4. **Timeout errors**: Some ERDDAP servers may be slow; consider implementing retry logic

## License

[Add license information here]

## Contributing

[Add contributing guidelines here]

## Acknowledgments

- ERDDAP is developed by NOAA's Environmental Research Division
- MCP (Model Context Protocol) is developed by Anthropic
- Default server provided by GCOOS (Gulf of Mexico Coastal Ocean Observing System)# erddap2mcp
# erddap2mcp
# erddap2mcp
