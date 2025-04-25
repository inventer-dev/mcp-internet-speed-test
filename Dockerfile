FROM python:3.12-slim

WORKDIR /app

# Install uv and uvx
RUN pip install uv && \
    uv pip install --system uvx && \
    uvx setup --skip-ensurepath || true

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv pip install --system --no-cache-dir -e .

# Copy application code
COPY . .

# Command will be provided by smithery.yaml
CMD ["python", "-m", "main"]
