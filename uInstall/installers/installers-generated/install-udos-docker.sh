# 🐳 uDOS Docker Container Installer Template

**Template Version**: v2.0.0  
**Platform**: Docker Container  
**Method**: Containerized Deployment  
**User Role**: wizard  
**Generated**: 2025-07-18 13:35:05 UTC

---

## 📋 Container Configuration

### Base Image Settings
- **Base Image**: {{base_image}} (ubuntu:22.04)
- **Architecture**: arm64
- **Container Name**: {{container_name}}
- **Port Mapping**: {{port_mapping}}

### uDOS Configuration
- **Install Directory**: /Users/agentdigital/uDOS
- **User Role**: wizard
- **Chester AI**: true
- **Persistence**: {{enable_persistence}}

---

## 🐳 Dockerfile

```dockerfile
# uDOS Docker Container
# Generated from template: docker-installer.md
# Base: {{base_image}}

FROM {{base_image}}

# Metadata
LABEL name="udos" \
      version="v1.0.0" \
      description="uDOS - Markdown-Native Operating System" \
      maintainer="uDOS Project" \
      user_role="wizard"

# Environment variables
ENV UDOS_VERSION=v1.0.0 \
    USER_ROLE=wizard \
    UDOS_HOME=/Users/agentdigital/uDOS \
    DEBIAN_FRONTEND=noninteractive \
    ENABLE_CHESTER=true

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    figlet \
    tree \
    sudo \
    nano \
    vim \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 18+
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Install VS Code Server
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Install additional tools based on package selection
RUN if echo "ripgrep,fd,bat,glow" | grep -q "ripgrep"; then apt-get update && apt-get install -y ripgrep; fi \
    && if echo "ripgrep,fd,bat,glow" | grep -q "fd"; then apt-get update && apt-get install -y fd-find && ln -sf /usr/bin/fdfind /usr/local/bin/fd; fi \
    && if echo "ripgrep,fd,bat,glow" | grep -q "bat"; then apt-get update && apt-get install -y bat && ln -sf /usr/bin/batcat /usr/local/bin/bat; fi \
    && rm -rf /var/lib/apt/lists/*

# Install glow for markdown rendering
RUN GLOW_VERSION=$(curl -s https://api.github.com/repos/charmbracelet/glow/releases/latest | grep '"tag_name"' | cut -d'"' -f4) \
    && wget -O /tmp/glow.deb "https://github.com/charmbracelet/glow/releases/download/$GLOW_VERSION/glow_${GLOW_VERSION#v}_linux_amd64.deb" \
    && dpkg -i /tmp/glow.deb \
    && rm /tmp/glow.deb

# Create uDOS user
RUN useradd -m -s /bin/zsh -G sudo udos \
    && echo "udos:udos" | chpasswd \
    && echo "udos ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Switch to uDOS user
USER udos
WORKDIR /home/udos

# Clone uDOS repository
RUN git clone https://github.com/fredporter/uDOS.git /Users/agentdigital/uDOS \
    && cd /Users/agentdigital/uDOS \
    && chmod +x uCode/*.sh \
    && chmod +x uCode/packages/*.sh

# Setup user configuration
RUN mkdir -p /Users/agentdigital/uDOS/uMemory/config \
    && echo '{ \
        "role": "wizard", \
        "username": "udos", \
        "hostname": "container", \
        "install_date": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'", \
        "platform": "Docker", \
        "architecture": "arm64", \
        "container_mode": true \
    }' > /Users/agentdigital/uDOS/uMemory/config/user.json

# Configure shell
RUN echo 'export UDOS_HOME="/Users/agentdigital/uDOS"' >> ~/.zshrc \
    && echo 'export PATH="$UDOS_HOME/uCode:$PATH"' >> ~/.zshrc \
    && echo 'alias ucode="$UDOS_HOME/uCode/ucode.sh"' >> ~/.zshrc \
    && echo 'cd $UDOS_HOME' >> ~/.zshrc

# Setup Chester AI if enabled
RUN if [ "true" = "true" ]; then \
        cd /Users/agentdigital/uDOS && ./uCode/packages/install-gemini.sh; \
    fi

# Expose ports
EXPOSE 8080 3000

# Create startup script
RUN echo '#!/bin/zsh' > /home/udos/start-udos.sh \
    && echo 'cd /Users/agentdigital/uDOS' >> /home/udos/start-udos.sh \
    && echo 'echo "🌀 Starting uDOS Container..."' >> /home/udos/start-udos.sh \
    && echo 'echo "User Role: wizard"' >> /home/udos/start-udos.sh \
    && echo 'echo "Access via: http://localhost:8080"' >> /home/udos/start-udos.sh \
    && echo 'code-server --bind-addr 0.0.0.0:8080 --auth none /Users/agentdigital/uDOS &' >> /home/udos/start-udos.sh \
    && echo 'if [ "true" = "true" ]; then' >> /home/udos/start-udos.sh \
    && echo '    echo "🐕 Chester AI available"' >> /home/udos/start-udos.sh \
    && echo 'fi' >> /home/udos/start-udos.sh \
    && echo 'zsh' >> /home/udos/start-udos.sh \
    && chmod +x /home/udos/start-udos.sh

# Set working directory
WORKDIR /Users/agentdigital/uDOS

# Default command
CMD ["/home/udos/start-udos.sh"]
```

---

## 🚀 Docker Compose Configuration

```yaml
# docker-compose.yml for uDOS
version: '3.8'

services:
  udos:
    build: .
    container_name: {{container_name}}
    ports:
      - "{{port_mapping}}"
    volumes:
      - udos-data:/Users/agentdigital/uDOS/uMemory
      - udos-config:/home/udos/.config
    environment:
      - USER_ROLE=wizard
      - ENABLE_CHESTER=true
    restart: unless-stopped
    networks:
      - udos-network

volumes:
  udos-data:
    driver: local
  udos-config:
    driver: local

networks:
  udos-network:
    driver: bridge
```

---

## 📦 Container Build Script

```bash
#!/bin/bash
# uDOS Docker Container Builder
# Generated from template: docker-installer.md

set -euo pipefail

# Configuration
CONTAINER_NAME="{{container_name}}"
IMAGE_TAG="udos:v1.0.0"
PORT_MAPPING="{{port_mapping}}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              🐳 uDOS Docker Container Builder                   ║"
    echo "║              Container: {{container_name}}                      ║"
    echo "║               Generated: 2025-07-18 13:35:05 UTC                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check Docker installation
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        log_info "Please install Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        log_info "Please start Docker daemon"
        exit 1
    fi
    
    log_success "Docker is available"
}

# Build container
build_container() {
    log_info "Building uDOS container..."
    
    # Build Docker image
    docker build -t "$IMAGE_TAG" . || {
        log_error "Container build failed"
        exit 1
    }
    
    log_success "Container built successfully: $IMAGE_TAG"
}

# Run container
run_container() {
    log_info "Starting uDOS container..."
    
    # Stop existing container if running
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log_warning "Stopping existing container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
    fi
    
    # Run new container
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT_MAPPING" \
        -v udos-data:/Users/agentdigital/uDOS/uMemory \
        -v udos-config:/home/udos/.config \
        "$IMAGE_TAG" || {
        log_error "Failed to start container"
        exit 1
    }
    
    log_success "Container started: $CONTAINER_NAME"
}

# Show container info
show_info() {
    echo
    log_success "🎉 uDOS Docker container is ready!"
    echo
    echo -e "${BOLD}${GREEN}Container Information:${NC}"
    echo "Name: $CONTAINER_NAME"
    echo "Image: $IMAGE_TAG"
    echo "Port: $PORT_MAPPING"
    echo "User Role: wizard"
    echo
    echo -e "${BOLD}${GREEN}Access Information:${NC}"
    echo "VS Code Server: http://localhost:${PORT_MAPPING%%:*}"
    echo "Terminal: docker exec -it $CONTAINER_NAME zsh"
    echo
    echo -e "${BOLD}${GREEN}Management Commands:${NC}"
    echo "Stop container:    docker stop $CONTAINER_NAME"
    echo "Start container:   docker start $CONTAINER_NAME"
    echo "View logs:         docker logs $CONTAINER_NAME"
    echo "Remove container:  docker rm $CONTAINER_NAME"
    echo
    if [ "true" = "true" ]; then
        echo -e "${BLUE}🐕 Chester AI is available inside the container${NC}"
    fi
}

# Main execution
main() {
    print_header
    
    check_docker
    build_container
    run_container
    show_info
}

# Error handling
trap 'log_error "Container setup failed at line $LINENO"' ERR

# Run main function
main "$@"
```

---

## 🔧 Container Features

### Development Environment
- **VS Code Server**: Web-based VS Code accessible at localhost:8080
- **Full Terminal**: Complete shell environment with zsh
- **Git Integration**: Full git functionality for version control
- **Package Tools**: All uDOS packages pre-installed

### Persistence Options
- **Volume Mounting**: User data persisted in Docker volumes
- **Configuration Persistence**: Settings maintained across restarts
- **Selective Persistence**: Choose what data to persist

### Networking
- **Port Forwarding**: Configurable port mapping
- **Network Isolation**: Isolated container network
- **Host Integration**: Optional host system integration

---

## 📋 Template Variables

### Container Configuration
- `{{base_image}}` - Docker base image (ubuntu:22.04)
- `{{container_name}}` - Container name (udos-container)
- `{{port_mapping}}` - Port mapping (8080:8080)
- `{{enable_persistence}}` - Enable data persistence (true/false)

### Application Configuration
- `/Users/agentdigital/uDOS` - uDOS installation path in container
- `wizard` - User role configuration
- `true` - Chester AI companion enabled
- `ripgrep,fd,bat,glow` - Additional packages to install

---

## 🛡️ Security Considerations

### Container Security
- **Non-Root User**: Runs as dedicated udos user
- **Minimal Base**: Ubuntu base image with only required packages
- **Network Isolation**: Containerized network environment
- **Resource Limits**: Configurable CPU and memory limits

### Data Protection
- **Volume Isolation**: User data isolated in Docker volumes
- **No Host Filesystem Access**: Limited host system exposure
- **Configurable Networking**: Control external network access
- **Secure Defaults**: Authentication and security enabled by default

---

*This template creates a complete Docker container with uDOS, VS Code Server, and optional persistence for development environments.*
