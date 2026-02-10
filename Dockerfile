# uDOS Wizard Server - Multi-stage Docker build
# Build: docker build -t udos-wizard .
# Run:   docker run -p 8765:8765 -v ./memory:/memory udos-wizard

# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies (cached layer)
COPY pyproject.toml ./
COPY core/_version.py core/
COPY core/version.json core/
RUN pip install --no-cache-dir ".[wizard]"

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash udos

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy application source
COPY core/ ./core/
COPY wizard/ ./wizard/
COPY extensions/ ./extensions/
COPY knowledge/ ./knowledge/
COPY version.json ./

# Create mount points
RUN mkdir -p /memory /library && chown udos:udos /memory /library

# Set default environment
ENV VAULT_ROOT=/memory/vault
ENV WIZARD_HOST=0.0.0.0
ENV WIZARD_PORT=8765

EXPOSE 8765

USER udos

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8765/health || exit 1

CMD ["python", "-m", "wizard.server", "--host", "0.0.0.0", "--port", "8765"]
