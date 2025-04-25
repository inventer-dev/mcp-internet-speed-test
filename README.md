# MCP Internet Speed Test

## ⚠️ Experimental Version

This is an experimental implementation of a Model Context Protocol (MCP) server for internet speed testing. It allows AI models and agents to measure, analyze, and report network performance metrics through a standardized interface.

## What is MCP?

The Model Context Protocol (MCP) provides a standardized way for Large Language Models (LLMs) to interact with external tools and data sources. Think of it as the "USB-C for AI applications" - a common interface that allows AI systems to access real-world capabilities and information.

## Features

- **Download Speed Testing**: Measure download bandwidth
- **Upload Speed Testing**: Measure upload bandwidth with configurable file sizes
- **Latency Testing**: Measure network latency to various servers
- **Jitter Analysis**: Calculate network jitter by analyzing latency variations
- **Comprehensive Reporting**: Provide detailed JSON-formatted reports

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

## Configuration

To use this MCP server with Claude Desktop or other MCP clients, add it to your MCP configuration file.

### Claude Desktop Configuration

Edit your Claude Desktop MCP configuration file:

```json
{
    "mcpServers": {
        "internet-speed-test": {
            "command": "uvx",
            "args": [
                "/path/to/mcp-internet-speed-test"
            ]
        }
    }
}
```

## API Tools

The MCP Internet Speed Test provides the following tools:

1. `measure_download_speed`: Measures download bandwidth (in Mbps)
2. `measure_upload_speed`: Measures upload bandwidth (in Mbps)
3. `measure_latency`: Measures network latency (in ms)
4. `measure_jitter`: Measures network jitter by analyzing latency variations
5. `run_complete_test`: Runs all tests and provides a comprehensive report

## Troubleshooting

If you're having issues connecting to the MCP server:

1. Make sure the path in your MCP configuration is correct
2. Check that you have the required permissions for the directory
3. Verify Python 3.12+ is installed and in your PATH
4. Ensure the `mcp[cli]` and `requests` packages are installed

## Development

This is an experimental project and contributions are welcome. To contribute:

1. Open an issue or submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MCP Framework maintainers for standardizing AI tool interactions
- The Model Context Protocol community for documentation and examples