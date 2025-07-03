FROM python:3.12-slim

WORKDIR /app

# Install the MCP internet speed test package from PyPI
RUN pip install --no-cache-dir mcp-internet-speed-test

# Command will be provided by smithery.yaml
CMD ["mcp-internet-speed-test"]
