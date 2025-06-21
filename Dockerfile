# ┌────────────────────────────────────────────┐
# │         uOS Dockerfile - v1.4.2+           │
# └────────────────────────────────────────────┘

FROM python:3.11-alpine

# Set working directory inside container
WORKDIR /uOS

# Ensure bash, curl, git, nano, tini (process manager) are available
RUN apk add --no-cache bash curl git tini nano

# Copy app source and dependencies
COPY . /uOS
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create persistent volume directories
RUN mkdir -p /uKnowledge /uMemory /config /uMemory/logs/system

# Ensure launch script is executable
RUN chmod +x scripts/launch-uOS.sh

# Default command to run when container starts
CMD ["bash", "scripts/launch-uOS.sh"]
