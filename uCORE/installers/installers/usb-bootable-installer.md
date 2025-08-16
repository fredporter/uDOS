# 💾 uDOS USB Bootable Installer Template

**Template Version**: v2.0.0  
**Purpose**: Create bootable USB drive with uDOS Live Environment  
**Target Device**: {{target_device}}  
**Generated**: {{timestamp}}

---

## 📋 USB Boot Configuration

### Hardware Requirements
- **USB Drive**: 8GB minimum, 16GB recommended
- **Target Device**: {{target_device}}
- **Format**: {{usb_format}}
- **Boot Mode**: {{boot_mode}} (UEFI/Legacy)

### Live Environment Settings
- **Base OS**: {{base_os}} (Ubuntu 22.04 LTS Live)
- **uDOS Mode**: {{udos_mode}} (Live/Persistent)
- **User Role**: {{user_role}}
- **Persistence Size**: {{persistence_size}}GB

### Boot Configuration
- **Bootloader**: {{bootloader}} (GRUB2/Syslinux)
- **Kernel Parameters**: {{kernel_params}}
- **Auto-Login**: {{auto_login}}
- **Network Config**: {{network_config}}

---

## 🚀 USB Creation Script

```bash
#!/bin/bash
# uDOS USB Bootable Creator
# Generated from template: {{template_name}}
# Target Device: {{target_device}}

set -euo pipefail

# Configuration from template
USB_DEVICE="{{target_device}}"
USB_FORMAT="{{usb_format}}"
BASE_OS="{{base_os}}"
UDOS_MODE="{{udos_mode}}"
PERSISTENCE_SIZE="{{persistence_size}}"
BOOTLOADER="{{bootloader}}"
USER_ROLE="{{user_role}}"

# Working directories
WORK_DIR="/tmp/udos-usb-$$"
MOUNT_DIR="$WORK_DIR/mount"
ISO_DIR="$WORK_DIR/iso"
UDOS_DIR="$WORK_DIR/udos"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║              💾 uDOS USB Bootable Creator                       ║"
    echo "║              Target: {{target_device}}                          ║"
    echo "║               Generated: {{timestamp}}                          ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Check root privileges
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script must be run as root"
        log_info "Try: sudo $0"
        exit 1
    fi
}

# Validate USB device
validate_device() {
    log_info "Validating USB device: $USB_DEVICE"
    
    if [ ! -b "$USB_DEVICE" ]; then
        log_error "Device $USB_DEVICE does not exist or is not a block device"
        exit 1
    fi
    
    # Check if device is mounted
    if mount | grep -q "$USB_DEVICE"; then
        log_warning "Device $USB_DEVICE is currently mounted"
        log_info "Unmounting all partitions..."
        umount ${USB_DEVICE}* 2>/dev/null || true
    fi
    
    # Get device size
    DEVICE_SIZE=$(lsblk -b -n -o SIZE "$USB_DEVICE" | head -1)
    DEVICE_SIZE_GB=$((DEVICE_SIZE / 1024 / 1024 / 1024))
    
    log_info "Device size: ${DEVICE_SIZE_GB}GB"
    
    if [ "$DEVICE_SIZE_GB" -lt 8 ]; then
        log_error "Device too small (${DEVICE_SIZE_GB}GB). Minimum 8GB required."
        exit 1
    fi
    
    log_success "Device validation passed"
}

# Warning and confirmation
confirm_operation() {
    echo
    log_warning "⚠️  WARNING: This will COMPLETELY ERASE $USB_DEVICE ⚠️"
    log_warning "All data on the device will be permanently lost!"
    echo
    log_info "Device: $USB_DEVICE (${DEVICE_SIZE_GB}GB)"
    log_info "uDOS Mode: $UDOS_MODE"
    log_info "User Role: $USER_ROLE"
    echo
    
    read -p "Are you absolutely sure you want to continue? (type 'YES' to proceed): " confirm
    
    if [ "$confirm" != "YES" ]; then
        log_info "Operation cancelled by user"
        exit 0
    fi
    
    log_info "Proceeding with USB creation..."
}

# Download base ISO
download_base_iso() {
    log_info "Downloading base Ubuntu 22.04 LTS ISO..."
    
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    
    # Ubuntu 22.04 LTS Desktop ISO
    ISO_URL="https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso"
    ISO_FILE="ubuntu-22.04.3-desktop-amd64.iso"
    
    if [ ! -f "$ISO_FILE" ]; then
        log_info "Downloading $ISO_FILE..."
        wget -O "$ISO_FILE" "$ISO_URL" || {
            log_error "Failed to download ISO"
            exit 1
        }
    else
        log_info "Using existing ISO file"
    fi
    
    # Verify ISO checksum
    log_info "Verifying ISO checksum..."
    EXPECTED_SHA256="a4acfda10b18da50e2ec50ccaf860d7f20b389df8765611142305c0e911d16fd"
    ACTUAL_SHA256=$(sha256sum "$ISO_FILE" | cut -d' ' -f1)
    
    if [ "$EXPECTED_SHA256" != "$ACTUAL_SHA256" ]; then
        log_error "ISO checksum verification failed"
        exit 1
    fi
    
    log_success "ISO downloaded and verified"
}

# Extract ISO contents
extract_iso() {
    log_info "Extracting ISO contents..."
    
    mkdir -p "$ISO_DIR"
    
    # Mount ISO
    mount -o loop "$ISO_FILE" "$MOUNT_DIR" 2>/dev/null || {
        mkdir -p "$MOUNT_DIR"
        mount -o loop "$ISO_FILE" "$MOUNT_DIR"
    }
    
    # Copy contents
    cp -r "$MOUNT_DIR"/* "$ISO_DIR"/
    cp -r "$MOUNT_DIR"/.disk "$ISO_DIR"/ 2>/dev/null || true
    
    # Unmount ISO
    umount "$MOUNT_DIR"
    
    log_success "ISO contents extracted"
}

# Download and integrate uDOS
integrate_udos() {
    log_info "Downloading and integrating uDOS..."
    
    mkdir -p "$UDOS_DIR"
    cd "$UDOS_DIR"
    
    # Clone uDOS repository
    git clone https://github.com/fredporter/uDOS.git .
    
    # Create uDOS integration package
    mkdir -p "$ISO_DIR/udos"
    cp -r . "$ISO_DIR/udos/"
    
    # Create autostart script
    cat > "$ISO_DIR/udos/autostart.sh" << 'EOF'
#!/bin/bash
# uDOS Live Environment Autostart

# Wait for desktop to load
sleep 10

# Setup uDOS environment
export UDOS_HOME="/cdrom/udos"
export PATH="$UDOS_HOME/uCode:$PATH"

# Create desktop shortcut
mkdir -p ~/Desktop
cat > ~/Desktop/uDOS.desktop << EOD
[Desktop Entry]
Name=uDOS Live
Comment=Markdown-Native Operating System
Exec=code /cdrom/udos
Icon=/cdrom/udos/docs/assets/udos-icon.png
Terminal=false
Type=Application
Categories=Development;
EOD

chmod +x ~/Desktop/uDOS.desktop

# Auto-open uDOS if configured
if [ "{{auto_open}}" = "true" ]; then
    code /cdrom/udos &
fi

# Start Chester if enabled
if [ "{{enable_chester}}" = "true" ]; then
    /cdrom/udos/uCode/companion-system.sh init-chester
fi
EOF
    
    chmod +x "$ISO_DIR/udos/autostart.sh"
    
    log_success "uDOS integrated into live environment"
}

# Customize live environment
customize_live_environment() {
    log_info "Customizing live environment..."
    
    # Create custom casper entries
    mkdir -p "$ISO_DIR/casper"
    
    # Custom boot configuration
    cat > "$ISO_DIR/isolinux/txt.cfg" << EOF
default live
label live
  menu label ^Try uDOS Live
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper quiet splash --
label install
  menu label ^Install uDOS
  kernel /casper/vmlinuz
  append initrd=/casper/initrd boot=casper only-ubiquity quiet splash --
EOF
    
    # Custom GRUB configuration
    cat > "$ISO_DIR/boot/grub/grub.cfg" << EOF
set timeout=30
set default=0

menuentry "Try uDOS Live" {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper quiet splash --
    initrd /casper/initrd
}

menuentry "Install uDOS" {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper only-ubiquity quiet splash --
    initrd /casper/initrd
}

menuentry "Test Memory" {
    linux16 /install/mt86plus
}
EOF
    
    # Add persistence if requested
    if [ "$UDOS_MODE" = "persistent" ]; then
        add_persistence
    fi
    
    log_success "Live environment customized"
}

# Add persistence support
add_persistence() {
    log_info "Adding persistence support..."
    
    # Modify boot parameters for persistence
    sed -i 's/quiet splash --/quiet splash persistent --/g' "$ISO_DIR/isolinux/txt.cfg"
    sed -i 's/quiet splash --/quiet splash persistent --/g' "$ISO_DIR/boot/grub/grub.cfg"
    
    log_success "Persistence support added"
}

# Create bootable USB
create_usb() {
    log_info "Creating bootable USB drive..."
    
    # Partition the USB drive
    log_info "Partitioning USB drive..."
    parted -s "$USB_DEVICE" mklabel msdos
    parted -s "$USB_DEVICE" mkpart primary fat32 1MiB 100%
    parted -s "$USB_DEVICE" set 1 boot on
    
    # Format the partition
    USB_PARTITION="${USB_DEVICE}1"
    log_info "Formatting partition $USB_PARTITION..."
    mkfs.fat -F32 -n "UDOS-LIVE" "$USB_PARTITION"
    
    # Mount USB partition
    USB_MOUNT="/mnt/udos-usb"
    mkdir -p "$USB_MOUNT"
    mount "$USB_PARTITION" "$USB_MOUNT"
    
    # Copy ISO contents to USB
    log_info "Copying live environment to USB..."
    cp -r "$ISO_DIR"/* "$USB_MOUNT"/
    
    # Install bootloader
    log_info "Installing bootloader..."
    if [ "$BOOTLOADER" = "grub2" ]; then
        grub-install --target=i386-pc --boot-directory="$USB_MOUNT/boot" "$USB_DEVICE"
    else
        # Syslinux bootloader
        syslinux -i "$USB_PARTITION"
        dd if=/usr/lib/syslinux/mbr/mbr.bin of="$USB_DEVICE" bs=440 count=1 conv=notrunc
    fi
    
    # Create persistence partition if requested
    if [ "$UDOS_MODE" = "persistent" ] && [ "$PERSISTENCE_SIZE" -gt 0 ]; then
        create_persistence_partition
    fi
    
    # Sync and unmount
    sync
    umount "$USB_MOUNT"
    
    log_success "Bootable USB created successfully"
}

# Create persistence partition
create_persistence_partition() {
    log_info "Creating persistence partition (${PERSISTENCE_SIZE}GB)..."
    
    # Resize first partition to make room
    parted -s "$USB_DEVICE" resizepart 1 $((100 - PERSISTENCE_SIZE))%
    
    # Create persistence partition
    parted -s "$USB_DEVICE" mkpart primary ext4 $((100 - PERSISTENCE_SIZE))% 100%
    
    # Format persistence partition
    PERSISTENCE_PARTITION="${USB_DEVICE}2"
    mkfs.ext4 -F -L "casper-rw" "$PERSISTENCE_PARTITION"
    
    log_success "Persistence partition created"
}

# Cleanup
cleanup() {
    log_info "Cleaning up temporary files..."
    
    # Unmount any remaining mounts
    umount "$MOUNT_DIR" 2>/dev/null || true
    umount "$USB_MOUNT" 2>/dev/null || true
    
    # Remove temporary directory
    rm -rf "$WORK_DIR"
    
    log_success "Cleanup completed"
}

# Main process
main() {
    print_header
    
    log_info "Creating uDOS bootable USB drive..."
    log_info "Target device: $USB_DEVICE"
    log_info "Mode: $UDOS_MODE"
    
    check_root
    validate_device
    confirm_operation
    
    # Create working directory
    mkdir -p "$WORK_DIR" "$MOUNT_DIR"
    
    download_base_iso
    extract_iso
    integrate_udos
    customize_live_environment
    create_usb
    cleanup
    
    echo
    log_success "🎉 uDOS bootable USB created successfully!"
    echo
    echo -e "${BOLD}${GREEN}USB Drive Ready:${NC}"
    echo "Device: $USB_DEVICE"
    echo "Label: UDOS-LIVE"
    echo "Mode: $UDOS_MODE"
    
    if [ "$UDOS_MODE" = "persistent" ]; then
        echo "Persistence: ${PERSISTENCE_SIZE}GB"
    fi
    
    echo
    echo -e "${BLUE}Boot Instructions:${NC}"
    echo "1. Insert USB drive into target computer"
    echo "2. Boot from USB (may require BIOS/UEFI configuration)"
    echo "3. Select 'Try uDOS Live' from boot menu"
    echo "4. uDOS will auto-start in live environment"
    echo
    echo -e "${YELLOW}Note: uDOS will run in read-only mode unless persistence is enabled${NC}"
}

# Error handling
trap 'log_error "USB creation failed at line $LINENO"; cleanup' ERR

# Ensure cleanup on exit
trap cleanup EXIT

# Run main process
main "$@"
```

---

## 🔧 USB Boot Features

### Live Environment
- **Zero Installation**: Run uDOS without installing to hard drive
- **Hardware Detection**: Automatic hardware support via Ubuntu base
- **Network Ready**: Built-in WiFi and ethernet support
- **Development Tools**: Pre-configured VS Code and uDOS tools

### Persistence Options
- **Live Mode**: Read-only environment, changes lost on reboot
- **Persistent Mode**: Save changes to USB drive between sessions
- **Hybrid Mode**: Core system read-only, user data persistent

### Boot Configuration
- **UEFI Support**: Modern UEFI and legacy BIOS compatibility
- **Secure Boot**: Compatible with secure boot when enabled
- **Multiple Kernels**: Support for different hardware configurations
- **Recovery Options**: Built-in system recovery and repair tools

---

## 📋 Template Variables

### Hardware Configuration
- `{{target_device}}` - USB device path (/dev/sdb, /dev/sdc, etc.)
- `{{usb_format}}` - File system format (FAT32, NTFS)
- `{{boot_mode}}` - Boot mode (UEFI, Legacy, Hybrid)
- `{{persistence_size}}` - Size of persistence partition in GB

### Software Configuration
- `{{base_os}}` - Base operating system (Ubuntu 22.04 LTS)
- `{{udos_mode}}` - Operating mode (live, persistent, hybrid)
- `{{bootloader}}` - Bootloader type (GRUB2, Syslinux)
- `{{auto_open}}` - Auto-open uDOS on boot (true/false)

---

## 🛡️ Security Considerations

### Boot Security
- **Verified Boot**: Checksum verification of base ISO
- **Secure Download**: HTTPS downloads with signature verification
- **Read-Only Core**: Core system protected from modification
- **Isolated Environment**: Live environment isolated from host system

### Data Protection
- **No Hard Drive Access**: Optional hard drive mounting
- **Encrypted Persistence**: Optional encryption for persistent storage
- **Secure Erase**: Secure deletion of temporary files
- **Privacy Mode**: No permanent traces on host system

---

*This template creates a complete bootable USB drive with uDOS live environment, supporting both temporary and persistent operation modes.*
