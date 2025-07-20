# ☁️ uDOS Cloud Instance Installer Template

**Template Version**: v2.0.0  
**Platform**: Cloud Infrastructure  
**Method**: Cloud Instance Deployment  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 🌐 Cloud Configuration

### Provider Settings
- **Cloud Provider**: {{cloud_provider}} (AWS/GCP/Azure/DigitalOcean)
- **Region**: {{cloud_region}}
- **Instance Type**: {{instance_type}}
- **Storage**: {{storage_type}} ({{storage_size}}GB)

### Network Configuration
- **VPC/Network**: {{vpc_name}}
- **Subnet**: {{subnet_name}}
- **Security Group**: {{security_group}}
- **Load Balancer**: {{enable_load_balancer}}

---

## 🚀 Terraform Infrastructure as Code

```hcl
# Terraform configuration for uDOS cloud deployment
# Generated from template: {{template_name}}

terraform {
  required_version = ">= 1.0"
  required_providers {
    {{#if aws}}
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    {{/if}}
    {{#if gcp}}
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    {{/if}}
    {{#if azure}}
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
    {{/if}}
    {{#if digitalocean}}
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
    {{/if}}
  }
}

# Provider configuration
{{#if aws}}
provider "aws" {
  region = "{{cloud_region}}"
  
  default_tags {
    tags = {
      Project     = "uDOS"
      Environment = "{{environment}}"
      Owner       = "{{user_role}}"
      ManagedBy   = "Terraform"
    }
  }
}
{{/if}}

{{#if gcp}}
provider "google" {
  project = "{{gcp_project_id}}"
  region  = "{{cloud_region}}"
}
{{/if}}

{{#if azure}}
provider "azurerm" {
  features {}
}
{{/if}}

{{#if digitalocean}}
provider "digitalocean" {
  token = var.do_token
}
{{/if}}

# Variables
variable "environment" {
  description = "Environment name"
  type        = string
  default     = "{{environment}}"
}

variable "user_role" {
  description = "uDOS user role"
  type        = string
  default     = "{{user_role}}"
}

variable "enable_chester" {
  description = "Enable Chester AI companion"
  type        = bool
  default     = {{enable_chester}}
}

variable "domain_name" {
  description = "Domain name for uDOS instance"
  type        = string
  default     = "{{domain_name}}"
}

{{#if aws}}
# AWS Resources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical
  
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_vpc" "udos_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "uDOS-VPC"
  }
}

resource "aws_internet_gateway" "udos_igw" {
  vpc_id = aws_vpc.udos_vpc.id
  
  tags = {
    Name = "uDOS-IGW"
  }
}

resource "aws_subnet" "udos_subnet" {
  vpc_id                  = aws_vpc.udos_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true
  
  tags = {
    Name = "uDOS-Subnet"
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_route_table" "udos_rt" {
  vpc_id = aws_vpc.udos_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.udos_igw.id
  }
  
  tags = {
    Name = "uDOS-RT"
  }
}

resource "aws_route_table_association" "udos_rta" {
  subnet_id      = aws_subnet.udos_subnet.id
  route_table_id = aws_route_table.udos_rt.id
}

resource "aws_security_group" "udos_sg" {
  name_prefix = "udos-sg"
  vpc_id      = aws_vpc.udos_vpc.id
  
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    description = "VS Code Server"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "uDOS-SecurityGroup"
  }
}

resource "aws_instance" "udos_instance" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = "{{instance_type}}"
  key_name              = aws_key_pair.udos_key.key_name
  vpc_security_group_ids = [aws_security_group.udos_sg.id]
  subnet_id             = aws_subnet.udos_subnet.id
  
  root_block_device {
    volume_type = "{{storage_type}}"
    volume_size = {{storage_size}}
    encrypted   = true
  }
  
  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    user_role      = var.user_role
    enable_chester = var.enable_chester
    domain_name    = var.domain_name
  }))
  
  tags = {
    Name = "uDOS-Instance"
  }
}

resource "aws_key_pair" "udos_key" {
  key_name   = "udos-key-{{user_role}}"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "aws_eip" "udos_eip" {
  instance = aws_instance.udos_instance.id
  domain   = "vpc"
  
  tags = {
    Name = "uDOS-EIP"
  }
}
{{/if}}

{{#if gcp}}
# GCP Resources
resource "google_compute_network" "udos_network" {
  name                    = "udos-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "udos_subnet" {
  name          = "udos-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "{{cloud_region}}"
  network       = google_compute_network.udos_network.id
}

resource "google_compute_firewall" "udos_firewall" {
  name    = "udos-firewall"
  network = google_compute_network.udos_network.name
  
  allow {
    protocol = "tcp"
    ports    = ["22", "80", "443", "8080"]
  }
  
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["udos"]
}

resource "google_compute_instance" "udos_instance" {
  name         = "udos-instance"
  machine_type = "{{instance_type}}"
  zone         = "{{cloud_region}}-a"
  
  tags = ["udos"]
  
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = {{storage_size}}
      type  = "{{storage_type}}"
    }
  }
  
  network_interface {
    network    = google_compute_network.udos_network.name
    subnetwork = google_compute_subnetwork.udos_subnet.name
    
    access_config {
      // Ephemeral public IP
    }
  }
  
  metadata_startup_script = templatefile("${path.module}/user-data.sh", {
    user_role      = var.user_role
    enable_chester = var.enable_chester
    domain_name    = var.domain_name
  })
  
  metadata = {
    ssh-keys = "ubuntu:${file("~/.ssh/id_rsa.pub")}"
  }
}
{{/if}}

{{#if azure}}
# Azure Resources
resource "azurerm_resource_group" "udos_rg" {
  name     = "udos-rg"
  location = "{{cloud_region}}"
}

resource "azurerm_virtual_network" "udos_vnet" {
  name                = "udos-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.udos_rg.location
  resource_group_name = azurerm_resource_group.udos_rg.name
}

resource "azurerm_subnet" "udos_subnet" {
  name                 = "udos-subnet"
  resource_group_name  = azurerm_resource_group.udos_rg.name
  virtual_network_name = azurerm_virtual_network.udos_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_public_ip" "udos_pip" {
  name                = "udos-pip"
  resource_group_name = azurerm_resource_group.udos_rg.name
  location            = azurerm_resource_group.udos_rg.location
  allocation_method   = "Static"
}

resource "azurerm_network_security_group" "udos_nsg" {
  name                = "udos-nsg"
  location            = azurerm_resource_group.udos_rg.location
  resource_group_name = azurerm_resource_group.udos_rg.name
  
  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "HTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "HTTPS"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  
  security_rule {
    name                       = "VSCode"
    priority                   = 1004
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "udos_nic" {
  name                = "udos-nic"
  location            = azurerm_resource_group.udos_rg.location
  resource_group_name = azurerm_resource_group.udos_rg.name
  
  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.udos_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.udos_pip.id
  }
}

resource "azurerm_network_interface_security_group_association" "udos_nsg_assoc" {
  network_interface_id      = azurerm_network_interface.udos_nic.id
  network_security_group_id = azurerm_network_security_group.udos_nsg.id
}

resource "azurerm_linux_virtual_machine" "udos_vm" {
  name                = "udos-vm"
  resource_group_name = azurerm_resource_group.udos_rg.name
  location            = azurerm_resource_group.udos_rg.location
  size                = "{{instance_type}}"
  admin_username      = "ubuntu"
  
  disable_password_authentication = true
  
  network_interface_ids = [
    azurerm_network_interface.udos_nic.id,
  ]
  
  admin_ssh_key {
    username   = "ubuntu"
    public_key = file("~/.ssh/id_rsa.pub")
  }
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "{{storage_type}}"
    disk_size_gb         = {{storage_size}}
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }
  
  custom_data = base64encode(templatefile("${path.module}/user-data.sh", {
    user_role      = var.user_role
    enable_chester = var.enable_chester
    domain_name    = var.domain_name
  }))
}
{{/if}}

{{#if digitalocean}}
# DigitalOcean Resources
resource "digitalocean_vpc" "udos_vpc" {
  name     = "udos-vpc"
  region   = "{{cloud_region}}"
  ip_range = "10.0.0.0/16"
}

resource "digitalocean_droplet" "udos_droplet" {
  image    = "ubuntu-22-04-x64"
  name     = "udos-droplet"
  region   = "{{cloud_region}}"
  size     = "{{instance_type}}"
  vpc_uuid = digitalocean_vpc.udos_vpc.id
  
  ssh_keys = [
    digitalocean_ssh_key.udos_key.fingerprint
  ]
  
  user_data = templatefile("${path.module}/user-data.sh", {
    user_role      = var.user_role
    enable_chester = var.enable_chester
    domain_name    = var.domain_name
  })
  
  tags = ["udos"]
}

resource "digitalocean_ssh_key" "udos_key" {
  name       = "uDOS Key"
  public_key = file("~/.ssh/id_rsa.pub")
}

resource "digitalocean_firewall" "udos_firewall" {
  name = "udos-firewall"
  
  droplet_ids = [digitalocean_droplet.udos_droplet.id]
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "22"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "80"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "443"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  inbound_rule {
    protocol         = "tcp"
    port_range       = "8080"
    source_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "tcp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "udp"
    port_range            = "1-65535"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
  
  outbound_rule {
    protocol              = "icmp"
    destination_addresses = ["0.0.0.0/0", "::/0"]
  }
}
{{/if}}

# Outputs
output "instance_public_ip" {
  description = "Public IP address of the uDOS instance"
  value       = {{#if aws}}aws_eip.udos_eip.public_ip{{/if}}{{#if gcp}}google_compute_instance.udos_instance.network_interface[0].access_config[0].nat_ip{{/if}}{{#if azure}}azurerm_public_ip.udos_pip.ip_address{{/if}}{{#if digitalocean}}digitalocean_droplet.udos_droplet.ipv4_address{{/if}}
}

output "ssh_connection" {
  description = "SSH connection command"
  value       = "ssh ubuntu@${{{#if aws}}aws_eip.udos_eip.public_ip{{/if}}{{#if gcp}}google_compute_instance.udos_instance.network_interface[0].access_config[0].nat_ip{{/if}}{{#if azure}}azurerm_public_ip.udos_pip.ip_address{{/if}}{{#if digitalocean}}digitalocean_droplet.udos_droplet.ipv4_address{{/if}}}"
}

output "vscode_url" {
  description = "VS Code Server URL"
  value       = "http://${{{#if aws}}aws_eip.udos_eip.public_ip{{/if}}{{#if gcp}}google_compute_instance.udos_instance.network_interface[0].access_config[0].nat_ip{{/if}}{{#if azure}}azurerm_public_ip.udos_pip.ip_address{{/if}}{{#if digitalocean}}digitalocean_droplet.udos_droplet.ipv4_address{{/if}}}:8080"
}
```

---

## 📜 Cloud Init User Data Script

```bash
#!/bin/bash
# Cloud-init script for uDOS installation
# Generated from template: {{template_name}}

set -euo pipefail

# Configuration from Terraform
USER_ROLE="${user_role}"
ENABLE_CHESTER="${enable_chester}"
DOMAIN_NAME="${domain_name}"
INSTALL_DIR="/home/ubuntu/uDOS"

# Logging
exec > >(tee /var/log/udos-setup.log)
exec 2>&1

log_info() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1"; }
log_error() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1"; }

log_info "Starting uDOS cloud instance setup..."

# Wait for system to be ready
sleep 30

# Update system
log_info "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required packages
log_info "Installing required packages..."
apt-get install -y \
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
    htop \
    nano \
    vim \
    zsh \
    unzip \
    jq

# Install Node.js 18
log_info "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install code-server (VS Code in browser)
log_info "Installing code-server..."
curl -fsSL https://code-server.dev/install.sh | sh

# Install additional tools
log_info "Installing additional tools..."

# Install ripgrep
RIPGREP_VERSION=$(curl -s https://api.github.com/repos/BurntSushi/ripgrep/releases/latest | jq -r '.tag_name')
wget -O /tmp/ripgrep.deb "https://github.com/BurntSushi/ripgrep/releases/download/$RIPGREP_VERSION/ripgrep_${RIPGREP_VERSION#v}_amd64.deb"
dpkg -i /tmp/ripgrep.deb
rm /tmp/ripgrep.deb

# Install fd
apt-get install -y fd-find
ln -sf /usr/bin/fdfind /usr/local/bin/fd

# Install bat
apt-get install -y bat
ln -sf /usr/bin/batcat /usr/local/bin/bat

# Install glow
GLOW_VERSION=$(curl -s https://api.github.com/repos/charmbracelet/glow/releases/latest | jq -r '.tag_name')
wget -O /tmp/glow.deb "https://github.com/charmbracelet/glow/releases/download/$GLOW_VERSION/glow_${GLOW_VERSION#v}_linux_amd64.deb"
dpkg -i /tmp/glow.deb
rm /tmp/glow.deb

# Setup ubuntu user
log_info "Setting up ubuntu user..."
usermod -s /bin/zsh ubuntu
mkdir -p /home/ubuntu/.ssh
chown ubuntu:ubuntu /home/ubuntu/.ssh
chmod 700 /home/ubuntu/.ssh

# Clone uDOS repository
log_info "Cloning uDOS repository..."
sudo -u ubuntu git clone https://github.com/fredporter/uDOS.git "$INSTALL_DIR"
chown -R ubuntu:ubuntu "$INSTALL_DIR"

# Make scripts executable
chmod +x "$INSTALL_DIR"/uCode/*.sh
chmod +x "$INSTALL_DIR"/uCode/packages/*.sh

# Setup user configuration
log_info "Setting up user configuration..."
sudo -u ubuntu mkdir -p "$INSTALL_DIR/uMemory/config"
cat > "$INSTALL_DIR/uMemory/config/user.json" << EOF
{
    "role": "$USER_ROLE",
    "username": "ubuntu",
    "hostname": "$(hostname)",
    "install_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "platform": "Cloud",
    "cloud_provider": "{{cloud_provider}}",
    "instance_type": "{{instance_type}}",
    "region": "{{cloud_region}}"
}
EOF
chown ubuntu:ubuntu "$INSTALL_DIR/uMemory/config/user.json"

# Configure shell
log_info "Configuring shell environment..."
cat >> /home/ubuntu/.zshrc << EOF
# uDOS Configuration
export UDOS_HOME="$INSTALL_DIR"
export PATH="\$UDOS_HOME/uCode:\$PATH"
alias ucode="\$UDOS_HOME/uCode/ucode.sh"
alias udos-dashboard="\$UDOS_HOME/uCode/dash.sh"
cd \$UDOS_HOME

# Welcome message
echo "🌀 Welcome to uDOS Cloud Instance"
echo "Instance: {{cloud_provider}} {{instance_type}} in {{cloud_region}}"
echo "Role: $USER_ROLE"
echo ""
echo "Quick commands:"
echo "  ucode           - Start uDOS shell"
echo "  udos-dashboard  - Generate dashboard"
EOF

# Install Chester AI if enabled
if [ "$ENABLE_CHESTER" = "true" ]; then
    log_info "Installing Chester AI..."
    cd "$INSTALL_DIR"
    sudo -u ubuntu ./uCode/packages/install-gemini.sh
fi

# Configure code-server
log_info "Configuring code-server..."
sudo -u ubuntu mkdir -p /home/ubuntu/.config/code-server
cat > /home/ubuntu/.config/code-server/config.yaml << EOF
bind-addr: 0.0.0.0:8080
auth: password
password: udos-{{user_role}}
cert: false
EOF
chown ubuntu:ubuntu /home/ubuntu/.config/code-server/config.yaml

# Create systemd service for code-server
cat > /etc/systemd/system/code-server.service << EOF
[Unit]
Description=code-server
After=network.target

[Service]
Type=exec
ExecStart=/usr/bin/code-server --bind-addr 0.0.0.0:8080 --auth password $INSTALL_DIR
Restart=always
User=ubuntu
Environment=HOME=/home/ubuntu

[Install]
WantedBy=multi-user.target
EOF

# Enable and start code-server
systemctl daemon-reload
systemctl enable code-server
systemctl start code-server

# Configure nginx reverse proxy if domain is provided
if [ -n "$DOMAIN_NAME" ] && [ "$DOMAIN_NAME" != "localhost" ]; then
    log_info "Setting up nginx reverse proxy..."
    apt-get install -y nginx certbot python3-certbot-nginx
    
    cat > /etc/nginx/sites-available/udos << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/udos /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl reload nginx
    
    # Get SSL certificate
    certbot --nginx -d "$DOMAIN_NAME" --non-interactive --agree-tos -m admin@"$DOMAIN_NAME"
fi

# Create startup script
cat > /home/ubuntu/start-udos-dashboard.sh << 'EOF'
#!/bin/bash
cd $UDOS_HOME
./uCode/dash.sh build
echo "Dashboard available at: http://$(curl -s ifconfig.me):8080"
EOF
chmod +x /home/ubuntu/start-udos-dashboard.sh
chown ubuntu:ubuntu /home/ubuntu/start-udos-dashboard.sh

# Final validation
log_info "Validating installation..."
if [ -f "$INSTALL_DIR/uCode/ucode.sh" ] && [ -x "$INSTALL_DIR/uCode/ucode.sh" ]; then
    log_info "uDOS installation successful"
else
    log_error "uDOS installation failed"
    exit 1
fi

# Get public IP for output
PUBLIC_IP=$(curl -s ifconfig.me)

log_info "uDOS cloud setup completed!"
log_info "Access VS Code at: http://$PUBLIC_IP:8080"
log_info "Default password: udos-$USER_ROLE"
log_info "SSH: ssh ubuntu@$PUBLIC_IP"

# Create completion marker
touch /var/log/udos-setup-complete
```

---

## 🚀 Deployment Script

```bash
#!/bin/bash
# Cloud deployment script for uDOS
# Generated from template: {{template_name}}

set -euo pipefail

# Configuration
CLOUD_PROVIDER="{{cloud_provider}}"
REGION="{{cloud_region}}"
INSTANCE_TYPE="{{instance_type}}"
USER_ROLE="{{user_role}}"
ENABLE_CHESTER="{{enable_chester}}"
DOMAIN_NAME="{{domain_name}}"

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
    echo "║              ☁️  uDOS Cloud Deployment Tool                     ║"
    echo "║              Provider: $CLOUD_PROVIDER                          ║"
    echo "║              Generated: {{timestamp}}                           ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed"
        log_info "Install from: https://www.terraform.io/downloads"
        exit 1
    fi
    
    # Check SSH key
    if [ ! -f ~/.ssh/id_rsa.pub ]; then
        log_warning "SSH public key not found. Generating..."
        ssh-keygen -t rsa -b 4096 -C "udos@$CLOUD_PROVIDER" -f ~/.ssh/id_rsa -N ""
    fi
    
    # Check cloud CLI
    case "$CLOUD_PROVIDER" in
        aws)
            if ! command -v aws &> /dev/null; then
                log_error "AWS CLI not installed"
                exit 1
            fi
            ;;
        gcp)
            if ! command -v gcloud &> /dev/null; then
                log_error "Google Cloud CLI not installed"
                exit 1
            fi
            ;;
        azure)
            if ! command -v az &> /dev/null; then
                log_error "Azure CLI not installed"
                exit 1
            fi
            ;;
        digitalocean)
            if ! command -v doctl &> /dev/null; then
                log_warning "DigitalOcean CLI not installed (optional)"
            fi
            ;;
    esac
    
    log_success "Prerequisites checked"
}

# Initialize Terraform
init_terraform() {
    log_info "Initializing Terraform..."
    
    terraform init
    terraform validate
    
    log_success "Terraform initialized"
}

# Plan deployment
plan_deployment() {
    log_info "Planning deployment..."
    
    terraform plan \
        -var="user_role=$USER_ROLE" \
        -var="enable_chester=$ENABLE_CHESTER" \
        -var="domain_name=$DOMAIN_NAME" \
        -out=tfplan
    
    echo
    log_warning "Review the plan above. Continue with deployment?"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled"
        exit 0
    fi
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    terraform apply tfplan
    
    log_success "Infrastructure deployed"
}

# Wait for instance to be ready
wait_for_instance() {
    log_info "Waiting for instance to be ready..."
    
    # Get instance IP
    INSTANCE_IP=$(terraform output -raw instance_public_ip)
    
    # Wait for SSH to be available
    for i in {1..30}; do
        if ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no ubuntu@"$INSTANCE_IP" exit 2>/dev/null; then
            log_success "Instance is ready"
            return 0
        fi
        echo -n "."
        sleep 10
    done
    
    log_error "Instance did not become ready in time"
    exit 1
}

# Show deployment info
show_deployment_info() {
    echo
    log_success "🎉 uDOS cloud deployment completed!"
    echo
    
    INSTANCE_IP=$(terraform output -raw instance_public_ip)
    SSH_COMMAND=$(terraform output -raw ssh_connection)
    VSCODE_URL=$(terraform output -raw vscode_url)
    
    echo -e "${BOLD}${GREEN}Deployment Information:${NC}"
    echo "Provider: $CLOUD_PROVIDER"
    echo "Region: $REGION"
    echo "Instance Type: $INSTANCE_TYPE"
    echo "Public IP: $INSTANCE_IP"
    echo "User Role: $USER_ROLE"
    echo
    echo -e "${BOLD}${GREEN}Access Information:${NC}"
    echo "SSH Command: $SSH_COMMAND"
    echo "VS Code URL: $VSCODE_URL"
    echo "Password: udos-$USER_ROLE"
    echo
    if [ -n "$DOMAIN_NAME" ] && [ "$DOMAIN_NAME" != "localhost" ]; then
        echo "Domain: https://$DOMAIN_NAME"
    fi
    echo
    echo -e "${BOLD}${GREEN}Management Commands:${NC}"
    echo "View status: terraform show"
    echo "Destroy: terraform destroy"
    echo "SSH access: $SSH_COMMAND"
    echo
    if [ "$ENABLE_CHESTER" = "true" ]; then
        echo -e "${BLUE}🐕 Chester AI is available on the instance${NC}"
    fi
}

# Cleanup on error
cleanup() {
    if [ -f tfplan ]; then
        rm tfplan
    fi
}

# Main execution
main() {
    print_header
    
    check_prerequisites
    init_terraform
    plan_deployment
    deploy_infrastructure
    wait_for_instance
    show_deployment_info
}

# Error handling
trap cleanup ERR
trap cleanup EXIT

# Run main function
main "$@"
```

---

## 📋 Template Variables

### Cloud Provider Configuration
- `{{cloud_provider}}` - Cloud provider (aws/gcp/azure/digitalocean)
- `{{cloud_region}}` - Deployment region
- `{{instance_type}}` - Instance/VM size
- `{{environment}}` - Environment name (dev/staging/prod)

### Network Configuration
- `{{vpc_name}}` - VPC/Network name
- `{{subnet_name}}` - Subnet name
- `{{security_group}}` - Security group name
- `{{domain_name}}` - Custom domain (optional)

### Storage Configuration
- `{{storage_type}}` - Storage type (gp3/pd-ssd/premium_lrs)
- `{{storage_size}}` - Storage size in GB
- `{{enable_backup}}` - Enable automated backups (true/false)

### Application Configuration
- `{{user_role}}` - uDOS user role
- `{{enable_chester}}` - Chester AI companion (true/false)
- `{{enable_load_balancer}}` - Load balancer (true/false)

---

*This template provides complete Infrastructure as Code deployment for uDOS across major cloud providers with Terraform, automated setup scripts, and full configuration management.*
