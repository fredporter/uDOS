FROM python:3.11-alpine

LABEL maintainer="Master <master@uos.local>"
LABEL description="uOS - lightweight AI-driven OS shell in Docker"

# Set working directory
WORKDIR /app

# Install required system packages
RUN apk add --no-cache bash curl git tini nano

# Copy everything into /app
COPY . /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment paths
ENV UOS_KNOWLEDGE_DIR=/uKnowledge
ENV UOS_MEMORY_DIR=/uMemory
ENV UOS_CONFIG_DIR=/config

# Create required directories inside container
RUN mkdir -p $UOS_KNOWLEDGE_DIR $UOS_MEMORY_DIR $UOS_CONFIG_DIR

# Use tini as init
ENTRYPOINT ["/sbin/tini", "--"]

# Launch uCode CLI by default
CMD ["bash", "scripts/uCode.sh"]
