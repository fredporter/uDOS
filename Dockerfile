FROM python:3.11-alpine

LABEL maintainer="Master <master@uos.local>"
LABEL description="uOS - lightweight AI-driven OS shell in Docker"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache bash curl git tini nano

# Copy full uOS repo contents
COPY . /app

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Set uOS environment variables
ENV UOS_MEMORY_DIR=/uMemory
ENV UOS_KNOWLEDGE_DIR=/uKnowledge
ENV UOS_CONFIG_DIR=/config

# Create required uOS directories
RUN mkdir -p $UOS_MEMORY_DIR $UOS_KNOWLEDGE_DIR $UOS_CONFIG_DIR

# Use Tini as init system to handle signals properly
ENTRYPOINT ["/sbin/tini", "--"]

# Default command: launch uCode shell
CMD ["bash", "./scripts/uCode.sh"]
