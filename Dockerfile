FROM python:3.12-slim

LABEL org.opencontainers.image.title="MCP Internet Speed Test"
LABEL org.opencontainers.image.description="MCP server for internet speed testing with network performance metrics"
LABEL org.opencontainers.image.authors="Pedro Cruz <hola@inventer.dev>"
LABEL org.opencontainers.image.source="https://github.com/inventer-dev/mcp-internet-speed-test"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install the MCP internet speed test package from PyPI
RUN pip install --no-cache-dir mcp-internet-speed-test

# MCP servers use stdio transport by default
# For Docker MCP Toolkit compatibility, expose via stdio
CMD ["mcp-internet-speed-test"]
