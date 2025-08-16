# 🥧 uDOS Raspberry Pi Installer Template

**Template Version**: v2.0.0  
**Platform**: Raspberry Pi OS  
**Method**: Native ARM Installation  
**User Role**: {{user_role}}  
**Generated**: {{timestamp}}

---

## 🔧 Hardware Configuration

### Raspberry Pi Settings
- **Model**: {{pi_model}} (Pi 4 Model B recommended)
- **RAM**: {{ram_size}}GB minimum
- **Storage**: {{storage_size}}GB microSD card (Class 10)
- **OS Version**: {{os_version}} (Raspberry Pi OS)

### Optional Hardware
- **Display**: {{display_type}} (HDMI/Touchscreen/Headless)
- **Keyboard**: {{keyboard_type}} (USB/Bluetooth)
- **Network**: {{network_type}} (WiFi/Ethernet)
- **Camera**: {{enable_camera}} (Pi Camera Module)

---

## 📦 Raspberry Pi OS Preparation

```bash
#!/bin/bash
# Raspberry Pi OS Setup for uDOS
# Generated from template: {{template_name}}

set -euo pipefail

# Configuration
PI_MODEL="{{pi_model}}"
OS_VERSION="{{os_version}}"
USER_ROLE="{{user_role}}"
INSTALL_DIR="{{install_directory}}"
ENABLE_SSH="{{enable_ssh}}"
ENABLE_VNC="{{enable_vnc}}"
ENABLE_CAMERA="{{enable_camera}}"

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
    clear
    echo -e "${BOLD}${BLUE}"
    figlet -f small "uDOS Pi Setup" 2>/dev/null || echo "🥧 uDOS Raspberry Pi Setup"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Model: $PI_MODEL | OS: $OS_VERSION | Role: $USER_ROLE"
    echo "Generated: {{timestamp}}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${NC}"
}

# Check if running on Raspberry Pi
check_pi_hardware() {
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        log_error "This script must be run on a Raspberry Pi"
        exit 1
    fi
    
    PI_MODEL_DETECTED=$(grep "Model" /proc/cpuinfo | cut -d: -f2 | xargs)
    log_success "Detected: $PI_MODEL_DETECTED"
    
    # Check RAM
    RAM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')
    if [ "$RAM_MB" -lt 2048 ]; then
        log_warning "Low RAM detected: ${RAM_MB}MB. 2GB+ recommended for optimal performance"
    else
        log_success "RAM: ${RAM_MB}MB"
    fi
}

# Update system
update_system() {
    log_info "Updating Raspberry Pi OS..."
    
    sudo apt update && sudo apt upgrade -y
    
    # Install essential packages
    sudo apt install -y \
        curl \
        wget \
        git \
        build-essential \
        cmake \
        pkg-config \
        libjpeg-dev \
        libpng-dev \
        libtiff5-dev \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libfontconfig1-dev \
        libcairo2-dev \
        libgdk-pixbuf2.0-dev \
        libpango1.0-dev \
        libgtk2.0-dev \
        libgtk-3-dev \
        libatlas-base-dev \
        gfortran \
        python3-dev \
        python3-pip \
        figlet \
        tree \
        htop \
        nano \
        vim \
        zsh
    
    log_success "System updated"
}

# Install Node.js for ARM
install_nodejs() {
    log_info "Installing Node.js for ARM..."
    
    # Install NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Verify installation
    node_version=$(node --version)
    npm_version=$(npm --version)
    
    log_success "Node.js $node_version and npm $npm_version installed"
}

# Install VS Code for ARM
install_vscode() {
    log_info "Installing VS Code for ARM64..."
    
    # Download and install VS Code for ARM64
    wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
    sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
    sudo sh -c 'echo "deb [arch=arm64,armhf,amd64 signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
    
    sudo apt update
    sudo apt install -y code
    
    log_success "VS Code installed"
}

# Configure Raspberry Pi specific settings
configure_pi_settings() {
    log_info "Configuring Raspberry Pi settings..."
    
    # Enable SSH if requested
    if [ "$ENABLE_SSH" = "true" ]; then
        sudo systemctl enable ssh
        sudo systemctl start ssh
        log_success "SSH enabled"
    fi
    
    # Enable VNC if requested
    if [ "$ENABLE_VNC" = "true" ]; then
        sudo raspi-config nonint do_vnc 0
        log_success "VNC enabled"
    fi
    
    # Enable camera if requested
    if [ "$ENABLE_CAMERA" = "true" ]; then
        sudo raspi-config nonint do_camera 0
        log_success "Camera enabled"
    fi
    
    # Increase GPU memory split for better performance
    sudo raspi-config nonint do_memory_split 128
    
    # Enable hardware acceleration
    echo 'gpu_mem=128' | sudo tee -a /boot/config.txt
    echo 'dtoverlay=vc4-kms-v3d' | sudo tee -a /boot/config.txt
    
    log_success "Pi settings configured"
}

# Install uDOS
install_udos() {
    log_info "Installing uDOS..."
    
    # Clone repository
    git clone https://github.com/fredporter/uDOS.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    # Make scripts executable
    chmod +x uCode/*.sh
    chmod +x uCode/packages/*.sh
    
    # Install uDOS packages optimized for Pi
    ./uCode/packages/manager-simple.sh install ripgrep
    ./uCode/packages/manager-simple.sh install fd
    ./uCode/packages/manager-simple.sh install bat
    
    # Install glow for markdown
    GLOW_VERSION=$(curl -s https://api.github.com/repos/charmbracelet/glow/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    wget -O /tmp/glow.deb "https://github.com/charmbracelet/glow/releases/download/$GLOW_VERSION/glow_${GLOW_VERSION#v}_linux_arm64.deb"
    sudo dpkg -i /tmp/glow.deb || true
    sudo apt-get install -f -y
    rm /tmp/glow.deb
    
    log_success "uDOS installed"
}

# Setup user configuration
setup_user_config() {
    log_info "Setting up user configuration..."
    
    # Create user config
    mkdir -p "$INSTALL_DIR/uMemory/config"
    cat > "$INSTALL_DIR/uMemory/config/user.json" << EOF
{
    "role": "$USER_ROLE",
    "username": "$(whoami)",
    "hostname": "$(hostname)",
    "install_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "platform": "Raspberry Pi",
    "architecture": "$(uname -m)",
    "os_version": "$OS_VERSION",
    "pi_model": "$PI_MODEL_DETECTED"
}
EOF
    
    # Setup shell aliases
    echo "# uDOS Configuration" >> ~/.bashrc
    echo "export UDOS_HOME=\"$INSTALL_DIR\"" >> ~/.bashrc
    echo "export PATH=\"\$UDOS_HOME/uCode:\$PATH\"" >> ~/.bashrc
    echo "alias ucode=\"\$UDOS_HOME/uCode/ucode.sh\"" >> ~/.bashrc
    echo "alias udos-dashboard=\"\$UDOS_HOME/uCode/dash.sh\"" >> ~/.bashrc
    echo "cd \$UDOS_HOME" >> ~/.bashrc
    
    # Create desktop shortcut
    if [ -d ~/Desktop ]; then
        cat > ~/Desktop/uDOS.desktop << EOF
[Desktop Entry]
Name=uDOS
Comment=uDOS - Markdown-Native Operating System
Exec=code $INSTALL_DIR
Icon=$INSTALL_DIR/extension/icon.svg
Terminal=false
Type=Application
Categories=Development;
EOF
        chmod +x ~/Desktop/uDOS.desktop
    fi
    
    log_success "User configuration completed"
}

# Install Chester AI (if supported)
install_chester() {
    if [ "{{enable_chester}}" = "true" ]; then
        log_info "Installing Chester AI companion..."
        
        cd "$INSTALL_DIR"
        ./uCode/packages/install-gemini.sh
        
        log_success "Chester AI installed"
    fi
}

# Performance optimization for Pi
optimize_performance() {
    log_info "Optimizing performance for Raspberry Pi..."
    
    # Adjust swappiness for better memory management
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    
    # Increase file watcher limits
    echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf
    
    # Optimize I/O scheduler for microSD
    echo 'echo deadline | sudo tee /sys/block/mmcblk0/queue/scheduler' >> ~/.bashrc
    
    # Create systemd service for uDOS auto-start
    if [ "{{enable_autostart}}" = "true" ]; then
        sudo tee /etc/systemd/system/udos.service << EOF
[Unit]
Description=uDOS Startup Service
After=graphical-session.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'cd $INSTALL_DIR && ./uCode/dash.sh build'
User=$(whoami)
Environment=HOME=/home/$(whoami)
Environment=DISPLAY=:0

[Install]
WantedBy=graphical-session.target
EOF
        
        sudo systemctl enable udos.service
        log_success "Auto-start service enabled"
    fi
    
    log_success "Performance optimizations applied"
}

# Create Pi-specific utilities
create_pi_utilities() {
    log_info "Creating Raspberry Pi utilities..."
    
    # CPU temperature monitor
    cat > "$INSTALL_DIR/uCode/pi-temp.sh" << 'EOF'
#!/bin/bash
# Raspberry Pi Temperature Monitor
temp=$(vcgencmd measure_temp | cut -d= -f2 | cut -d\' -f1)
echo "🌡️  CPU Temperature: ${temp}°C"

if (( $(echo "$temp > 70" | bc -l) )); then
    echo "⚠️  High temperature warning!"
fi
EOF
    chmod +x "$INSTALL_DIR/uCode/pi-temp.sh"
    
    # Camera capture utility
    if [ "$ENABLE_CAMERA" = "true" ]; then
        cat > "$INSTALL_DIR/uCode/pi-camera.sh" << 'EOF'
#!/bin/bash
# Raspberry Pi Camera Utility
CAPTURE_DIR="$UDOS_HOME/uMemory/captures"
mkdir -p "$CAPTURE_DIR"

case "${1:-photo}" in
    "photo")
        filename="$CAPTURE_DIR/photo_$(date +%Y%m%d_%H%M%S).jpg"
        raspistill -o "$filename" -q 90
        echo "📸 Photo saved: $filename"
        ;;
    "video")
        duration="${2:-10}"
        filename="$CAPTURE_DIR/video_$(date +%Y%m%d_%H%M%S).h264"
        raspivid -o "$filename" -t "${duration}000"
        echo "🎥 Video saved: $filename"
        ;;
    *)
        echo "Usage: $0 [photo|video] [duration_seconds]"
        ;;
esac
EOF
        chmod +x "$INSTALL_DIR/uCode/pi-camera.sh"
    fi
    
    # GPIO utility for hardware projects
    cat > "$INSTALL_DIR/uCode/pi-gpio.sh" << 'EOF'
#!/bin/bash
# Raspberry Pi GPIO Utility
echo "🔌 GPIO Information:"
echo "Model: $(cat /proc/cpuinfo | grep Model | cut -d: -f2 | xargs)"
echo "GPIO Pins: 40-pin header"
echo ""
echo "Available GPIO tools:"
echo "  gpio readall  - Show all pin states"
echo "  pinout        - Display pinout diagram"
echo ""
echo "Install additional tools:"
echo "  sudo apt install wiringpi python3-gpiozero"
EOF
    chmod +x "$INSTALL_DIR/uCode/pi-gpio.sh"
    
    log_success "Pi utilities created"
}

# Final validation
validate_installation() {
    log_info "Validating installation..."
    
    # Check core components
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/uCode/ucode.sh" ]; then
        log_success "uDOS core files present"
    else
        log_error "uDOS installation incomplete"
        exit 1
    fi
    
    # Check permissions
    if [ -x "$INSTALL_DIR/uCode/ucode.sh" ]; then
        log_success "uCode scripts executable"
    else
        log_error "Script permissions incorrect"
        exit 1
    fi
    
    # Test uDOS startup
    cd "$INSTALL_DIR"
    if ./uCode/ucode.sh --version > /dev/null 2>&1; then
        log_success "uDOS startup test passed"
    else
        log_warning "uDOS startup test failed - check configuration"
    fi
    
    log_success "Installation validation completed"
}

# Show completion summary
show_completion() {
    echo
    log_success "🎉 uDOS installation on Raspberry Pi completed!"
    echo
    echo -e "${BOLD}${GREEN}Installation Summary:${NC}"
    echo "Model: $PI_MODEL_DETECTED"
    echo "RAM: ${RAM_MB}MB"
    echo "Install Directory: $INSTALL_DIR"
    echo "User Role: $USER_ROLE"
    echo
    echo -e "${BOLD}${GREEN}Enabled Features:${NC}"
    [ "$ENABLE_SSH" = "true" ] && echo "✓ SSH Remote Access"
    [ "$ENABLE_VNC" = "true" ] && echo "✓ VNC Desktop Sharing"
    [ "$ENABLE_CAMERA" = "true" ] && echo "✓ Pi Camera Module"
    [ "{{enable_chester}}" = "true" ] && echo "✓ Chester AI Companion"
    [ "{{enable_autostart}}" = "true" ] && echo "✓ Auto-start Service"
    echo
    echo -e "${BOLD}${GREEN}Quick Commands:${NC}"
    echo "Start uDOS:        ucode"
    echo "Dashboard:         udos-dashboard"
    echo "Check temp:        $INSTALL_DIR/uCode/pi-temp.sh"
    [ "$ENABLE_CAMERA" = "true" ] && echo "Take photo:        $INSTALL_DIR/uCode/pi-camera.sh photo"
    echo "GPIO info:         $INSTALL_DIR/uCode/pi-gpio.sh"
    echo
    echo -e "${BOLD}${GREEN}Access Methods:${NC}"
    echo "Local Desktop:     Open VS Code from desktop"
    [ "$ENABLE_SSH" = "true" ] && echo "SSH Access:        ssh $(whoami)@$(hostname -I | awk '{print $1}')"
    [ "$ENABLE_VNC" = "true" ] && echo "VNC Access:        $(hostname -I | awk '{print $1}'):5900"
    echo
    echo -e "${BOLD}${YELLOW}Next Steps:${NC}"
    echo "1. Reboot your Raspberry Pi to apply all settings"
    echo "2. Open VS Code and navigate to $INSTALL_DIR"
    echo "3. Run the dashboard to see system status"
    echo "4. Explore the documentation in the docs folder"
    echo
    echo -e "${BLUE}💡 Pro Tip: Use 'sudo raspi-config' to adjust additional Pi settings${NC}"
}

# Main execution flow
main() {
    print_header
    
    check_pi_hardware
    update_system
    install_nodejs
    install_vscode
    configure_pi_settings
    install_udos
    setup_user_config
    install_chester
    optimize_performance
    create_pi_utilities
    validate_installation
    show_completion
    
    echo
    log_info "Reboot recommended to complete setup"
    read -p "Reboot now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
}

# Error handling
trap 'log_error "Installation failed at line $LINENO"' ERR

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    log_error "Do not run this script as root"
    exit 1
fi

# Run main installation
main "$@"
```

---

## 🖥️ Desktop Environment Integration

### Autostart Desktop File
```desktop
[Desktop Entry]
Type=Application
Name=uDOS
Comment=Start uDOS markdown-native environment
Exec=/bin/bash -c 'cd {{install_directory}} && code .'
Icon={{install_directory}}/extension/icon.svg
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=5
```

### Panel Widget Configuration
```bash
#!/bin/bash
# uDOS Panel Widget for Raspberry Pi Desktop

# Create panel widget for quick access
cat > ~/.config/lxpanel/LXDE-pi/panels/panel << 'EOF'
Plugin {
    type = launchbar
    Config {
        Button {
            id = udos
            image = {{install_directory}}/extension/icon.svg
            tooltip = Launch uDOS
            action = code {{install_directory}}
        }
    }
}
EOF
```

---

## 🔧 Hardware Integration Features

### GPIO Control Integration
```bash
#!/bin/bash
# GPIO Integration for uDOS Projects

# Install GPIO libraries
sudo apt install -y python3-gpiozero python3-rpi.gpio wiringpi

# Create GPIO template for uDOS projects
mkdir -p {{install_directory}}/uTemplate/hardware
cat > {{install_directory}}/uTemplate/hardware/gpio-project.md << 'EOF'
# GPIO Project Template

## Hardware Setup
- **GPIO Pins Used**: {{gpio_pins}}
- **Components**: {{components}}
- **Wiring Diagram**: {{wiring_diagram}}

## Code Implementation
```python
import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup({{pin_number}}, GPIO.OUT)

# Your code here
GPIO.output({{pin_number}}, GPIO.HIGH)
time.sleep(1)
GPIO.output({{pin_number}}, GPIO.LOW)

# Cleanup
GPIO.cleanup()
```

## Safety Notes
- Always check pin assignments
- Use appropriate resistors
- Never exceed 3.3V on GPIO pins
EOF
```

### Camera Integration
```bash
#!/bin/bash
# Pi Camera integration with uDOS

# Create camera capture templates
mkdir -p {{install_directory}}/uMemory/captures
mkdir -p {{install_directory}}/uTemplate/camera

cat > {{install_directory}}/uTemplate/camera/timelapse.md << 'EOF'
# Time-lapse Project

## Configuration
- **Interval**: {{interval_seconds}} seconds
- **Duration**: {{duration_hours}} hours
- **Resolution**: {{resolution}}

## Capture Script
```bash
#!/bin/bash
mkdir -p captures/timelapse_$(date +%Y%m%d)
for i in $(seq 1 {{total_frames}}); do
    raspistill -o captures/timelapse_$(date +%Y%m%d)/frame_$(printf "%05d" $i).jpg -q 90
    sleep {{interval_seconds}}
done

# Create video from frames
ffmpeg -framerate 24 -i captures/timelapse_$(date +%Y%m%d)/frame_%05d.jpg -c:v libx264 -pix_fmt yuv420p timelapse.mp4
```
EOF
```

---

## 📊 Performance Monitoring

### System Monitor Dashboard
```bash
#!/bin/bash
# Pi-specific monitoring for uDOS dashboard

create_pi_monitor() {
    cat > {{install_directory}}/uCode/pi-monitor.sh << 'EOF'
#!/bin/bash
# Raspberry Pi System Monitor

echo "🥧 Raspberry Pi System Status"
echo "=============================="

# CPU Temperature
temp=$(vcgencmd measure_temp | cut -d= -f2)
echo "🌡️  CPU Temperature: $temp"

# CPU Usage
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "💻 CPU Usage: ${cpu_usage}%"

# Memory Usage
memory_info=$(free -h | grep Mem)
echo "🧠 Memory: $memory_info"

# Storage Usage
storage_usage=$(df -h / | tail -1 | awk '{print $5}')
echo "💾 Storage Used: $storage_usage"

# Network Status
if ping -c 1 google.com &> /dev/null; then
    echo "🌐 Network: Connected"
else
    echo "🌐 Network: Disconnected"
fi

# Voltage (important for Pi stability)
voltage=$(vcgencmd measure_volts core | cut -d= -f2)
echo "⚡ Core Voltage: $voltage"

# Throttling status
throttle=$(vcgencmd get_throttled)
if [ "$throttle" = "throttled=0x0" ]; then
    echo "🚀 Throttling: None"
else
    echo "⚠️  Throttling: Detected ($throttle)"
fi
EOF
    chmod +x {{install_directory}}/uCode/pi-monitor.sh
}
```

---

## 🔒 Security Configuration

### SSH Security Setup
```bash
#!/bin/bash
# Secure SSH configuration for Pi

if [ "{{enable_ssh}}" = "true" ]; then
    # Disable password authentication, enable key-based auth
    sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
    sudo sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config
    
    # Generate SSH key pair if not exists
    if [ ! -f ~/.ssh/id_rsa ]; then
        ssh-keygen -t rsa -b 4096 -C "$(whoami)@$(hostname)" -f ~/.ssh/id_rsa -N ""
    fi
    
    # Setup authorized_keys
    mkdir -p ~/.ssh
    touch ~/.ssh/authorized_keys
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    
    sudo systemctl restart ssh
fi
```

### Firewall Configuration
```bash
#!/bin/bash
# Basic firewall setup

sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH if enabled
[ "{{enable_ssh}}" = "true" ] && sudo ufw allow ssh

# Allow VNC if enabled
[ "{{enable_vnc}}" = "true" ] && sudo ufw allow 5900

# Allow VS Code Live Server
sudo ufw allow 3000
sudo ufw allow 5500
```

---

## 📋 Template Variables

### Hardware Configuration
- `{{pi_model}}` - Raspberry Pi model (Pi 4 Model B)
- `{{ram_size}}` - RAM size in GB (4/8)
- `{{storage_size}}` - microSD card size in GB (32/64/128)
- `{{os_version}}` - Raspberry Pi OS version (Bullseye/Bookworm)

### Connectivity Options
- `{{enable_ssh}}` - Enable SSH remote access (true/false)
- `{{enable_vnc}}` - Enable VNC desktop sharing (true/false)
- `{{network_type}}` - Network connection type (WiFi/Ethernet)
- `{{display_type}}` - Display configuration (HDMI/Touchscreen/Headless)

### Hardware Features
- `{{enable_camera}}` - Enable Pi Camera module (true/false)
- `{{enable_autostart}}` - Auto-start uDOS on boot (true/false)
- `{{keyboard_type}}` - Keyboard type (USB/Bluetooth)

---

*This template provides a complete Raspberry Pi installation with hardware-specific optimizations, GPIO integration, camera support, and performance monitoring tailored for the Pi platform.*
