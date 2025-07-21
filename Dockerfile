# Minimal Alpine container for erddap2mcp MCP server
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY . .

# Create non-root user
RUN adduser -D -s /bin/sh mcpuser
USER mcpuser

# Expose port for HTTP MCP server
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run proper MCP-over-StreamingHTTP server
CMD ["python", "erddap_remote_mcp_oauth.py"]
