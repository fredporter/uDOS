FROM python:3.11-alpine

LABEL maintainer="Master <master@uos.local>"
LABEL description="uDOS - lightweight AI-driven OS shell in Docker"

# Set working directory to mounted source
WORKDIR /uDOS

# Install required system packages
RUN apk add --no-cache bash curl git tini tree

# Copy Python requirements if needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV UOS_KNOWLEDGE_DIR=/uKnowledge
ENV UOS_MEMORY_DIR=/uMemory
ENV UOS_CONFIG_DIR=/config

# Create required directories
RUN mkdir -p $UOS_KNOWLEDGE_DIR $UOS_MEMORY_DIR $UOS_CONFIG_DIR

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--"]

# Launch the uCode CLI by default
CMD ["bash", "uCode/uCode.sh"]
