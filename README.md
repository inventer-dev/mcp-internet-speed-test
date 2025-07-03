[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/inventer-dev-mcp-internet-speed-test-badge.png)](https://mseep.ai/app/inventer-dev-mcp-internet-speed-test)

[![smithery badge](https://smithery.ai/badge/@inventer-dev/mcp-internet-speed-test)](https://smithery.ai/server/@inventer-dev/mcp-internet-speed-test)

# MCP Internet Speed Test

An implementation of a Model Context Protocol (MCP) for internet speed testing. It allows AI models and agents to measure, analyze, and report network performance metrics through a standardized interface.

**📦 Available on PyPI:** https://pypi.org/project/mcp-internet-speed-test/

**🚀 Quick Start:**
```bash
pip install mcp-internet-speed-test
mcp-internet-speed-test
```

## What is MCP?

The Model Context Protocol (MCP) provides a standardized way for Large Language Models (LLMs) to interact with external tools and data sources. Think of it as the "USB-C for AI applications" - a common interface that allows AI systems to access real-world capabilities and information.

## Features

- **Smart Incremental Testing**: Uses SpeedOf.Me methodology with 8-second threshold for optimal accuracy
- **Download Speed Testing**: Measures bandwidth using files from 128KB to 100MB from GitHub repository
- **Upload Speed Testing**: Tests upload bandwidth using generated data from 128KB to 100MB
- **Latency Testing**: Measures network latency with detailed server location information
- **Jitter Analysis**: Calculates network stability using multiple latency samples (default: 5)
- **Multi-CDN Support**: Detects and provides info for Fastly, Cloudflare, and AWS CloudFront
- **Geographic Location**: Maps POP codes to physical locations (50+ locations worldwide)
- **Cache Analysis**: Detects HIT/MISS status and cache headers
- **Server Metadata**: Extracts detailed CDN headers including `x-served-by`, `via`, `x-cache`
- **Comprehensive Testing**: Single function to run all tests with complete metrics

## Installation

### Prerequisites

- Python 3.12 or higher (required for async support)
- pip or [uv](https://github.com/astral-sh/uv) package manager

### Option 1: Install from PyPI with pip (Recommended)

```bash
# Install the package globally
pip install mcp-internet-speed-test

# Run the MCP server
mcp-internet-speed-test
```

### Option 2: Install from PyPI with uv

```bash
# Install the package globally
uv add mcp-internet-speed-test

# Or run directly without installing
uvx mcp-internet-speed-test
```

### Option 3: Using docker

```bash
# Build the Docker image
docker build -t mcp-internet-speed-test .

# Run the MCP server in a Docker container
docker run -it --rm -v $(pwd):/app -w /app mcp-internet-speed-test
```

### Option 4: Development/Local Installation

If you want to contribute or modify the code:

```bash
# Clone the repository
git clone https://github.com/inventer-dev/mcp-internet-speed-test.git
cd mcp-internet-speed-test

# Install in development mode
pip install -e .

# Or using uv
uv sync
uv run python -m mcp_internet_speed_test.main
```

### Dependencies

The package automatically installs these dependencies:
- `mcp[cli]>=1.6.0`: MCP server framework with CLI integration
- `httpx>=0.27.0`: Async HTTP client for speed tests


## Configuration

To use this MCP server with Claude Desktop or other MCP clients, add it to your MCP configuration file.

### Claude Desktop Configuration

Edit your Claude Desktop MCP configuration file:

#### Option 1: Using pip installed package (Recommended)

```json
{
    "mcpServers": {
        "mcp-internet-speed-test": {
            "command": "mcp-internet-speed-test"
        }
    }
}
```

#### Option 2: Using uvx

```json
{
    "mcpServers": {
        "mcp-internet-speed-test": {
            "command": "uvx",
            "args": ["mcp-internet-speed-test"]
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

### Technical Implementation

#### Smart Testing Methodology
- **Incremental Approach**: Starts with small files (128KB) and progressively increases
- **Time-Based Optimization**: Uses 8-second base threshold + 4-second additional buffer
- **Accuracy Focus**: Selects optimal file size that provides reliable measurements
- **Multi-Provider Support**: Tests against geographically distributed endpoints

#### CDN Detection Capabilities
- **Fastly**: Detects POP codes and maps to 50+ global locations
- **Cloudflare**: Identifies data centers and geographic regions
- **AWS CloudFront**: Recognizes edge locations across continents
- **Header Analysis**: Parses `x-served-by`, `via`, `x-cache`, and custom CDN headers

### Why This Matters
- **Network Diagnostics**: Understand which server is actually serving your tests
- **Performance Analysis**: Correlate speed results with server proximity
- **CDN Optimization**: Identify if your ISP's routing is optimal
- **Geographic Awareness**: Know if tests are running from your expected region
- **Troubleshooting**: Identify routing issues and CDN misconfigurations

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

### Technical Configuration

#### Default Test Files Repository
```
GitHub Repository: inventer-dev/speed-test-files
Branch: main
File Sizes: 128KB, 256KB, 512KB, 1MB, 2MB, 5MB, 10MB, 20MB, 40MB, 50MB, 100MB
```

#### Upload Endpoints Priority
1. **Cloudflare Workers** (httpi.dev) - Global distribution, highest priority
2. **HTTPBin** (httpbin.org) - AWS-based, secondary endpoint

#### Supported CDN Locations (150+ POPs)

**Fastly POPs**: MEX, QRO, DFW, LAX, NYC, MIA, LHR, FRA, AMS, CDG, NRT, SIN, SYD, GRU, SCL, BOG, MAD, MIL...

**Cloudflare Centers**: DFW, LAX, SJC, SEA, ORD, MCI, IAD, ATL, MIA, YYZ, LHR, FRA, AMS, CDG, ARN, STO...

**AWS CloudFront**: ATL, BOS, ORD, CMH, DFW, DEN, IAD, LAX, MIA, MSP, JFK, SEA, SJC, AMS, ATH, TXL...

#### Performance Thresholds
- **Base Test Duration**: 8.0 seconds
- **Additional Buffer**: 4.0 seconds
- **Maximum File Size**: Configurable (default: 100MB)
- **Jitter Samples**: 5 measurements (configurable)

## Troubleshooting

### Common Issues

#### MCP Server Connection
1. **Path Configuration**: Ensure absolute path is used in MCP configuration
2. **Directory Permissions**: Verify read/execute permissions for the project directory
3. **Python Version**: Requires Python 3.12+ with async support
4. **Dependencies**: Install `fastmcp` and `httpx` packages

#### Speed Test Issues
1. **GitHub Repository Access**: Ensure `inventer-dev/speed-test-files` is accessible
2. **Firewall/Proxy**: Check if corporate firewalls block test endpoints
3. **CDN Routing**: Some ISPs may route differently to CDNs
4. **Network Stability**: Jitter tests require stable connections

#### Performance Considerations
- **File Size Limits**: Large files (>50MB) may timeout on slow connections
- **Upload Endpoints**: If primary endpoint fails, fallback is automatic
- **Geographic Accuracy**: POP detection depends on CDN header consistency

## Development

### Project Structure
```
mcp-internet-speed-test/
├── mcp_internet_speed_test/  # Main package directory
│   ├── __init__.py      # Package initialization
│   └── main.py          # MCP server implementation
├── README.md           # This documentation
├── Dockerfile          # Container configuration
└── pyproject.toml      # Python project configuration
```

### Key Components

#### Configuration Constants
- `GITHUB_RAW_URL`: Base URL for test files repository
- `UPLOAD_ENDPOINTS`: Prioritized list of upload test endpoints
- `SIZE_PROGRESSION`: Ordered list of file sizes for incremental testing
- `*_POP_LOCATIONS`: Mappings of CDN codes to geographic locations

#### Core Functions
- `extract_server_info()`: Parses HTTP headers to identify CDN providers
- `measure_*()`: Individual test functions for different metrics
- `run_complete_test()`: Orchestrates comprehensive testing suite

### Configuration Customization

You can customize the following in `mcp_internet_speed_test/main.py` if you clone the repository:
```python
# GitHub repository settings
GITHUB_USERNAME = "your-username"
GITHUB_REPO = "your-speed-test-files"
GITHUB_BRANCH = "main"

# Test duration thresholds
BASE_TEST_DURATION = 8.0  # seconds
ADDITIONAL_TEST_DURATION = 4.0  # seconds

# Default endpoints
DEFAULT_UPLOAD_URL = "your-upload-endpoint"
DEFAULT_LATENCY_URL = "your-latency-endpoint"
```

### Contributing

This is an experimental project and contributions are welcome:

1. **Issues**: Report bugs or request features
2. **Pull Requests**: Submit code improvements
3. **Documentation**: Help improve this README
4. **Testing**: Test with different network conditions and CDNs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- MCP Framework maintainers for standardizing AI tool interactions
- The Model Context Protocol community for documentation and examples