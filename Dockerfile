# Multi-stage build for Docker Monitor CLI
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash docker-monitor

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/docker-monitor/.local

# Copy application
COPY . .

# Install the application
RUN pip install --no-cache-dir -e . && \
    chown -R docker-monitor:docker-monitor /app

# Switch to non-root user
USER docker-monitor

# Add local bin to PATH
ENV PATH=/home/docker-monitor/.local/bin:$PATH

# Docker socket volume
VOLUME ["/var/run/docker.sock"]

# Entry point
ENTRYPOINT ["docker-monitor"]
CMD ["--help"]