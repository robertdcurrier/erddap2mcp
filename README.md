# ERDDAP MCP Server

Access oceanographic and environmental data from ERDDAP servers worldwide directly through Claude, ChatGPT, or any MCP-compatible AI assistant.

## What is this?

This MCP (Model Context Protocol) server provides seamless access to ERDDAP (Environmental Research Division's Data Access Program) servers, allowing AI assistants to search, discover, and retrieve scientific datasets. ERDDAP is a data server that gives you a simple, consistent way to download subsets of scientific datasets in common file formats and make graphs and maps.

## Credits

- **ERDDAP** was developed by Bob Simons at NOAA's Environmental Research Division. Learn more at the [ERDDAP website](https://coastwatch.pfeg.noaa.gov/erddap/information.html).
- **erddapy** is the official Python client for ERDDAP, developed by [Filipe Fernandes](https://github.com/ocefpaf) and the IOOS community. Visit the [erddapy documentation](https://ioos.github.io/erddapy/).

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone https://github.com/robertdcurrier/erddap2mcp.git
cd erddap2mcp
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

That's it! No additional configuration needed.

### Integration with AI Assistants

#### Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "erddap": {
      "command": "python",
      "args": ["/path/to/erddap2mcp/erddapy_mcp_server.py"]
    }
  }
}
```

#### Cline (VS Code Extension)

Add to your VS Code settings.json:

```json
{
  "cline.mcpServers": {
    "erddap": {
      "command": "python",
      "args": ["/path/to/erddap2mcp/erddapy_mcp_server.py"]
    }
  }
}
```

#### Other MCP Clients

For any MCP-compatible client, use:
- Command: `python /path/to/erddap2mcp/erddapy_mcp_server.py`
- Protocol: stdio

## Usage Examples

### List Available ERDDAP Servers

**You:** Show me available ERDDAP servers

**Assistant:** I'll use the list_servers tool to show you the available ERDDAP servers.

Here are some well-known ERDDAP servers you can access:

- **NOAA CoastWatch** (https://coastwatch.pfeg.noaa.gov/erddap) - Provides satellite and in-situ oceanographic data from NOAA
- **IOOS ERDDAP** (https://erddap.ioos.us/erddap) - The Integrated Ocean Observing System's data server
- **Marine Institute Ireland** (https://erddap.marine.ie/erddap) - Irish marine and oceanographic data
- **ONC ERDDAP** (https://data.oceannetworks.ca/erddap) - Ocean Networks Canada's data server
- **GCOOS ERDDAP** (https://gcoos5.geos.tamu.edu/erddap) - Gulf of Mexico Coastal Ocean Observing System
- **EMODnet Physics** (https://erddap.emodnet-physics.eu/erddap) - European Marine Observation and Data Network

### Search for Datasets

**You:** Search the GCOOS ERDDAP server for datasets created by Bob Currier

**Assistant:** I'll search the GCOOS ERDDAP server for datasets created by Bob Currier.

I found 26 datasets on the GCOOS ERDDAP server that are associated with Bob Currier. Here are the first 10:

- Stommel-20200813T1200
- usf-sam-20190527T1200
- usf-sam-20210331T0000
- usf-sam-20210512T0000
- Reveille-20180627T1500
- Sverdrup-20180509T1742
- Sverdrup-20190926T0000
- Sverdrup-20200925T1200
- mote-dora-20210113T1200
- mote-dora-20210318T1200

These appear to be glider datasets based on the naming convention.

### Analyze Data

**You:** Get the average sea water temperature for the dataset mote-dora-20210318T1200

**Assistant:** Based on the data from the mote-dora-20210318T1200 dataset, the average sea water temperature is **21.09°C**.

The dataset contains 30,405 total measurements, with 7,197 valid temperature readings. The temperature ranges from a minimum of 20.51°C to a maximum of 21.58°C, with a standard deviation of 0.26°C, indicating relatively stable temperature conditions during this glider deployment.

## Available Tools

| Tool | Description | Example Use |
|------|-------------|-------------|
| `list_servers` | Show well-known ERDDAP servers | "Show me available ERDDAP servers" |
| `search_datasets` | Search for datasets by keyword | "Find temperature datasets on IOOS ERDDAP" |
| `get_dataset_info` | Get detailed metadata about a dataset | "Tell me about dataset jplMURSST41" |
| `get_dataset_variables` | List all variables in a dataset | "What variables are in this dataset?" |
| `get_var_by_attr` | Find variables by attributes | "Find variables with units of meters" |
| `get_search_url` | Generate a search URL | "Create a search URL for salinity data" |
| `get_info_url` | Generate an info URL | "Generate the metadata URL for this dataset" |
| `get_download_url` | Generate a download URL | "Create a download URL with these constraints" |
| `to_pandas` | Download and preview data | "Show me the temperature data from January 2024" |
| `download_file` | Prepare file download | "Download this data as NetCDF" |

## Standalone NetCDF Download Tool

In addition to the MCP server, this repository includes `erddap_download_nc.py`, a standalone command-line tool for efficiently downloading NetCDF files from ERDDAP servers. This tool is particularly useful for downloading large collections of files from datasets you've discovered using the MCP server.

### Features

- Downloads NetCDF files directly from ERDDAP's files endpoint
- Tracks previously downloaded files to avoid re-downloads
- Supports file pattern matching (e.g., `*24hr*.nc`)
- Uses HTTP compression for 3-10x faster downloads
- No dependency on erddapy library
- Colorful progress indicators and logging

### Usage

```bash
# Download all NC files from a dataset
python erddap_download_nc.py dataset_id

# Download to specific directory
python erddap_download_nc.py dataset_id -o /path/to/data

# Download only files matching a pattern
python erddap_download_nc.py dataset_id --pattern "*24hr*.nc"

# Use a different ERDDAP server
python erddap_download_nc.py dataset_id --server https://coastwatch.pfeg.noaa.gov/erddap

# Force re-download of all files
python erddap_download_nc.py dataset_id --force

# Enable verbose logging
python erddap_download_nc.py dataset_id -v
```

### Example Workflow

1. Use the MCP server through your AI assistant to discover datasets:
   ```
   You: Search IOOS GDAC for glider datasets from Rutgers
   Assistant: I found dataset ru38-20250414T1500...
   ```

2. Use the standalone tool to download the data:
   ```bash
   python erddap_download_nc.py ru38-20250414T1500 -o ./glider_data
   ```

The tool will download all NetCDF files, show progress, and skip any files already downloaded in previous runs.

**Note**: In the future, this download functionality will be integrated directly into the MCP server, allowing you to request downloads through the chat interface. For now, it's available as a standalone tool for batch downloads.

## Tips for Best Results

1. **Start with search**: Use `search_datasets` to find relevant datasets
2. **Check metadata**: Use `get_dataset_info` to understand what's available
3. **Use constraints**: Limit data requests with time/space constraints to avoid timeouts
4. **Specify protocol**: Use "griddap" for gridded data (satellite/model) and "tabledap" for tabular data (buoys/stations)

## Common Use Cases

- **Climate Research**: Access historical temperature, salinity, and current data
- **Marine Biology**: Find chlorophyll concentrations and ocean color data
- **Coastal Management**: Monitor sea level, wave heights, and coastal conditions
- **Fisheries**: Access environmental data for fisheries management
- **Education**: Explore real oceanographic data for teaching and learning

## Troubleshooting

- **Timeouts**: Reduce the spatial/temporal extent of your data request
- **Protocol errors**: Make sure to specify the correct protocol (tabledap vs griddap)
- **Server availability**: Some ERDDAP servers may be temporarily unavailable

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is open source and available under the MIT License.