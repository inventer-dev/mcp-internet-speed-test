[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/inventer-dev-mcp-internet-speed-test-badge.png)](https://mseep.ai/app/inventer-dev-mcp-internet-speed-test)

# MCP Internet Speed Test

## ⚠️ Experimental Version

This is an experimental implementation of a Model Context Protocol (MCP) server for internet speed testing. It allows AI models and agents to measure, analyze, and report network performance metrics through a standardized interface.

## What is MCP?

The Model Context Protocol (MCP) provides a standardized way for Large Language Models (LLMs) to interact with external tools and data sources. Think of it as the "USB-C for AI applications" - a common interface that allows AI systems to access real-world capabilities and information.

## Features

- **Download Speed Testing**: Measure download bandwidth with incremental file sizes
- **Upload Speed Testing**: Measure upload bandwidth with configurable file sizes
- **Latency Testing**: Measure network latency to various servers
- **Jitter Analysis**: Calculate network jitter by analyzing latency variations
- **CDN Server Detection**: Identify which CDN server is serving your tests (Fastly, Cloudflare, AWS)
- **Geographic Location**: Determine the physical location of CDN Points of Presence (POPs)
- **Cache Analysis**: Detect if content is served from cache (HIT) or origin (MISS)
- **Server Information**: Extract detailed server headers and CDN provider information
- **Comprehensive Reporting**: Provide detailed JSON-formatted reports with server metadata

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager (recommended)

### Option 1: Using uvx (Recommended)

The `uvx` command is a convenient way to run Python packages directly without explicit installation:

```bash
# Run the MCP server directly
uvx /path/to/mcp-internet-speed-test
```

### Option 2: Using docker

```bash
# Build the Docker image
docker build -t mcp-internet-speed-test .

# Run the MCP server in a Docker container
docker run -it --rm -v $(pwd):/app -w /app mcp-internet-speed-test
```


## Configuration

To use this MCP server with Claude Desktop or other MCP clients, add it to your MCP configuration file.

### Claude Desktop Configuration

Edit your Claude Desktop MCP configuration file:

```json
{
    "mcpServers": {
        "mcp-internet-speed-test": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/mcp-internet-speed-test",
                "run",
                "main.py"
            ]
        }
    }
}
```

## API Tools

The MCP Internet Speed Test provides the following tools:

### Testing Functions
1. `measure_download_speed`: Measures download bandwidth (in Mbps) with server location info
2. `measure_upload_speed`: Measures upload bandwidth (in Mbps) with server location info
3. `measure_latency`: Measures network latency (in ms) with server location info
4. `measure_jitter`: Measures network jitter by analyzing latency variations with server info
5. `get_server_info`: Get detailed CDN server information for any URL without running speed tests
6. `run_complete_test`: Comprehensive test with all metrics and server metadata

## CDN Server Detection

This speed test now provides detailed information about the CDN servers serving your tests:

### What You Get
- **CDN Provider**: Identifies if you're connecting to Fastly, Cloudflare, or Amazon CloudFront
- **Geographic Location**: Shows the physical location of the server (e.g., "Mexico City, Mexico")
- **POP Code**: Three-letter code identifying the Point of Presence (e.g., "MEX", "QRO", "DFW")
- **Cache Status**: Whether content is served from cache (HIT) or fetched from origin (MISS)
- **Server Headers**: Full HTTP headers including `x-served-by`, `via`, and `x-cache`

### Why This Matters
- **Network Diagnostics**: Understand which server is actually serving your tests
- **Performance Analysis**: Correlate speed results with server proximity
- **CDN Optimization**: Identify if your ISP's routing is optimal
- **Geographic Awareness**: Know if tests are running from your expected region

### Example Server Info Output
```json
{
  "cdn_provider": "Fastly",
  "pop_code": "MEX",
  "pop_location": "Mexico City, Mexico",
  "served_by": "cache-mex4329-MEX",
  "cache_status": "HIT",
  "x_cache": "HIT, HIT"
}
```

### Supported Locations
The system recognizes 50+ Fastly POP locations worldwide including:
- **Americas**: Mexico City, Querétaro, Dallas, Los Angeles, New York, Miami, São Paulo, Santiago
- **Europe**: London, Frankfurt, Amsterdam, Paris, Madrid, Milan, Stockholm
- **Asia-Pacific**: Tokyo, Singapore, Sydney, Hong Kong, Seoul, Mumbai, Bangkok
- **And many more...**

## Troubleshooting

If you're having issues connecting to the MCP server:

1. Make sure the path in your MCP configuration is correct
2. Check that you have the required permissions for the directory
3. Verify Python 3.12+ is installed and in your PATH
4. Ensure the `mcp[cli]` and `httpx` packages are installed

## Development

This is an experimental project and contributions are welcome. To contribute:

1. Open an issue or submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MCP Framework maintainers for standardizing AI tool interactions
- The Model Context Protocol community for documentation and examples