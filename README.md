[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/inventer-dev/mcp-internet-speed-test)](https://archestra.ai/mcp-catalog/inventer-dev__mcp-internet-speed-test)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/inventer-dev-mcp-internet-speed-test-badge.png)](https://mseep.ai/app/inventer-dev-mcp-internet-speed-test)

<a href="https://glama.ai/mcp/servers/@inventer-dev/mcp-internet-speed-test">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@inventer-dev/mcp-internet-speed-test/badge" alt="mcp-internet-speed-test MCP server" />
</a>

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

- **Smart Incremental Testing**: Uses [SpeedOf.Me methodology](#speedofme-testing-methodology) with 8-second threshold for optimal accuracy
- **Download Speed Testing**: Measures bandwidth using files from 128KB to 128MB from GitHub repository (Git LFS)
- **Upload Speed Testing**: Tests upload bandwidth using streaming data from 128KB to 128MB
- **Latency Testing**: Measures network latency using multiple samples, reports minimum value
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
- `mcp[cli]>=1.25.0`: MCP server framework with CLI integration
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
3. `measure_latency`: Measures network latency (in ms) using samples, reports minimum value
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
- **Incremental Approach**: Starts with small files (128KB) and progressively increases (powers of 2)
- **Time-Based Threshold**: Uses configurable sustain_time (1-8 seconds, default: 8). Stops when a sample exceeds the threshold
- **Accuracy Focus**: The speed from the last sample that took ≥ 8 seconds is used as the final measurement
- **Multi-Provider Support**: Tests against geographically distributed endpoints
- **Full methodology**: See [SpeedOf.Me Testing Methodology](#speedofme-testing-methodology)

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
URL: https://media.githubusercontent.com/media/inventer-dev/speed-test-files/main/
File Sizes: 128KB, 256KB, 512KB, 1MB, 2MB, 4MB, 8MB, 16MB, 32MB, 64MB, 128MB
Storage: Git LFS
```

#### Upload Endpoints Priority
1. **Cloudflare Workers** (httpi.dev) - Global distribution, highest priority
2. **HTTPBin** (httpbin.org) - AWS-based, secondary endpoint

#### Supported CDN Locations (150+ POPs)

**Fastly POPs**: MEX, QRO, DFW, LAX, NYC, MIA, LHR, FRA, AMS, CDG, NRT, SIN, SYD, GRU, SCL, BOG, MAD, MIL...

**Cloudflare Centers**: DFW, LAX, SJC, SEA, ORD, MCI, IAD, ATL, MIA, YYZ, LHR, FRA, AMS, CDG, ARN, STO...

**AWS CloudFront**: ATL, BOS, ORD, CMH, DFW, DEN, IAD, LAX, MIA, MSP, JFK, SEA, SJC, AMS, ATH, TXL...

#### Performance Thresholds
- **Test Duration Threshold**: 8.0 seconds (stops when a sample exceeds this)
- **Maximum File Size**: Configurable (default: 128MB)
- **Latency Samples**: 10 measurements, reports minimum (configurable)
- **Jitter Samples**: 5 measurements (configurable)
- **Sustain Time**: 1-8 seconds (configurable, default: 8)

## Troubleshooting

### Common Issues

#### MCP Server Connection
1. **Path Configuration**: Ensure absolute path is used in MCP configuration
2. **Directory Permissions**: Verify read/execute permissions for the project directory
3. **Python Version**: Requires Python 3.12+ with async support
4. **Dependencies**: Install `mcp[cli]` and `httpx` packages

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
├── README.md           # This documentation (includes methodology reference)
├── Dockerfile          # Container configuration
└── pyproject.toml      # Python project configuration
```

### Key Components

#### Configuration Constants
- `GITHUB_MEDIA_URL`: Base URL for test files repository (Git LFS media endpoint)
- `UPLOAD_ENDPOINTS`: Prioritized list of upload test endpoints
- `SIZE_PROGRESSION`: Ordered list of file sizes for incremental testing (powers of 2)
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

# Test duration threshold
DEFAULT_TEST_DURATION = 8.0  # seconds

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
- [SpeedOf.Me](https://speedof.me) team for their incremental testing methodology ([How It Works](https://speedof.me/howitworks.html)). See [methodology reference below](#speedofme-testing-methodology)
- For the official SpeedOf.Me MCP server, see [@speedofme/mcp](https://www.npmjs.com/package/@speedofme/mcp)

---

## SpeedOf.Me Testing Methodology

> **Source:** [SpeedOf.Me — How It Works](https://speedof.me/howitworks.html)
>
> This section preserves the SpeedOf.Me testing methodology as referenced
> by this project. Retrieved on March 8, 2026.

<details>
<summary><strong>Click to expand full methodology</strong></summary>

### Overview

SpeedOf.Me tests an internet connection by downloading and uploading sample
files. It reflects actual browsing and download performance by using a single
HTTP connection and large continuous files — the same way real web content is
delivered.

### Download Test

1. Begin by downloading the **smallest sample size** (128 KB).
2. Measure the download duration in real time.
3. If the download takes **less than 8 seconds**, move to the **next larger
   sample size**.
4. If the download takes **8 seconds or more**, stop the progression.
5. The **final speed measurement** is based on **that last sample** — the one
   that took 8 seconds or more.

### Upload Test

When the download test is complete, a similar incremental process is used to
send data back to the test server:

1. Start with a **small sample** and gradually increase in size.
2. Continue until uploading a sample takes **more than 8 seconds**.
3. The upload speed is based on that final sample.

### Latency & Jitter

- **Latency (ping):** The time it takes for data to travel to the server and
  back. Measured over **10 samples** with the **lowest value reported**.
- **Jitter:** The variation between latency samples. Lower jitter means a more
  stable connection, which is important for video calls and gaming.

### Adaptive Testing Method

To ensure the internet connection is thoroughly tested, bandwidth is measured in
**several passes**. Sample file sizes gradually increase until one takes longer
than 8 seconds to download.

This approach automatically measures connection speeds ranging from very slow
mobile networks (10 Kbps GPRS / 2G) to gigabit fiber connections (1 Gbps or
more).

#### Sample File Sizes

| # | Size   |
|---|--------|
| 1 | 128 KB |
| 2 | 256 KB |
| 3 | 512 KB |
| 4 | 1 MB   |
| 5 | 2 MB   |
| 6 | 4 MB   |
| 7 | 8 MB   |
| 8 | 16 MB  |
| 9 | 32 MB  |
| 10 | 64 MB |
| 11 | 128 MB |

### Test Servers

SpeedOf.Me hosts its sample files on a
[CDN](https://en.wikipedia.org/wiki/Content_delivery_network). It uses servers
called [PoPs](https://en.wikipedia.org/wiki/Points_of_presence) (Points of
Presence) in **106+ cities**. Each PoP may consist of multiple servers and is
located in key regions around the world, near major internet exchange points.

When the test begins, SpeedOf.Me **automatically selects the most reliable and
responsive server**. This may not be the closest one — several factors are taken
into account to determine the best option. CDN technology handles this process
to provide the most accurate and consistent test results.

### Accuracy

Key differences that make this methodology accurate:

1. **Single continuous download** — Downloads large, continuous sample files,
   similar to how web pages or media files are typically delivered. Other speed
   tests use small chunks transferred in parallel and apply adjustments to
   estimate speed.
2. **Multiple global servers** — Uses PoPs in different regions, producing more
   realistic results. Other services often choose the nearest physical server
   (sometimes inside the ISP network), which can give inflated results.
3. **No plugins required** — Tests run directly from the client with no extra
   software.

### How This Project Implements the Methodology

| SpeedOf.Me Concept | Implementation in this project |
|--------------------|-------------------------------|
| Incremental download | `measure_download_speed()` iterates `SIZE_PROGRESSION`, breaks when elapsed ≥ `sustain_time` (default 8 s) |
| Incremental upload | `measure_upload_speed()` streams chunks and breaks when elapsed ≥ `sustain_time` |
| 8-second threshold | Configurable via `sustain_time` parameter (1–8 s, default 8) |
| Latency — 10 samples, min | `measure_latency(samples=10)` reports `min_latency` |
| Jitter — variation | `measure_jitter(samples=5)` reports average deviation from mean |
| CDN with PoPs | Download files served from GitHub via Fastly CDN; upload via Cloudflare Workers |
| Sample file sizes (powers of 2) | 128 KB → 128 MB stored in `inventer-dev/speed-test-files` (Git LFS) |
| Automatic server selection | CDN handles geographic routing; PoP detected from response headers |

</details>