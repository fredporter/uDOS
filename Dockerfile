FROM python:3.11-alpine

LABEL maintainer="Master <master@uos.local>"
LABEL description="uOS - lightweight AI-driven OS shell in Docker"

# Set working directory
WORKDIR /app

# Install required system packages
RUN apk add --no-cache bash curl git tini

# Copy Python requirements if needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY ./src /app/src

# Set environment variables
ENV UOS_KNOWLEDGE_DIR=/uKnowledge
ENV UOS_CONFIG_DIR=/config

# Create required directories
RUN mkdir -p $UOS_KNOWLEDGE_DIR $UOS_CONFIG_DIR

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--"]

# Launch the uShell CLI by default
CMD ["bash", "./src/uCode.sh"]
