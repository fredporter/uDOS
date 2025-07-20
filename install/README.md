# 🛠️ uDOS Installation & Build System - v1.2

**Centralized installation, build management, and platform-specific installers for uDOS v1.2**

## 📁 Directory Structure

```
install/
├── README.md                          # This documentation  
├── installers/                        # Platform-specific installers (moved from uTemplate)
│   ├── browser-pwa-installer.md       # Progressive Web App installer
│   ├── cloud-installer.md             # Cloud deployment installer
│   ├── docker-installer.md            # Docker containerization
│   ├── macos-vscode-installer.md      # macOS VS Code integration
│   ├── raspberry-pi-installer.md      # Raspberry Pi deployment
│   ├── ubuntu22-installer.md          # Ubuntu 22.04 installer
│   ├── usb-bootable-installer.md      # USB bootable system
│   ├── generate-installer.sh          # Installer generation script
│   └── installers-generated/          # Generated installation scripts
├── build-macos-app.sh                 # macOS app bundle builder
├── prepare-release.sh                 # Release preparation
├── create-clean-distribution.sh       # Clean distribution builder
├── cleanup-root.sh                    # Repository cleanup
├── validate-alpha-v1.0.sh            # Legacy alpha validation
└── validate-comprehensive.sh          # Comprehensive system check
```

## 🎯 Core Installation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `validate-comprehensive.sh` | Full system validation | `./install/validate-comprehensive.sh` |
| `build-macos-app.sh` | macOS app bundle builder | `./install/build-macos-app.sh` |
| `prepare-release.sh` | Release preparation | `./install/prepare-release.sh` |
| `create-clean-distribution.sh` | Clean distribution builder | `./install/create-clean-distribution.sh` |
| `cleanup-root.sh` | Repository cleanup | `./install/cleanup-root.sh` |

## 🌍 Platform-Specific Installers (`installers/`)

**Comprehensive installation templates for multiple platforms and deployment scenarios:**

| Platform | Installer | Description |
|----------|-----------|-------------|
| **🖥️ macOS** | `macos-vscode-installer.md` | Native macOS integration with VS Code |
| **🐧 Linux** | `ubuntu22-installer.md` | Ubuntu 22.04 LTS installation |
| **🌐 Web** | `browser-pwa-installer.md` | Progressive Web App deployment |
| **☁️ Cloud** | `cloud-installer.md` | Cloud platform deployment |
| **🐳 Docker** | `docker-installer.md` | Containerized deployment |
| **🥧 IoT** | `raspberry-pi-installer.md` | Raspberry Pi deployment |
| **💾 Portable** | `usb-bootable-installer.md` | USB bootable system |

### Installer Generation
```bash
# Generate platform-specific installer
./install/installers/generate-installer.sh [platform]

# View generated installers
ls ./install/installers/installers-generated/
```

## 📚 User Documentation

**Installation guides and tutorials have been moved to:**

- **[📦 Quick Start](../docs/installation/quick-start.md)** - 5-minute setup guide
- **[🎮 Getting Started](../docs/installation/getting-started.md)** - Interactive tutorial  
- **[🛠️ Installation Guide](../docs/installation/installation-guide.md)** - Comprehensive setup

## 🎯 Build Process

### Development Validation
```bash
# Validate current development state
./install/validate-comprehensive.sh

# Run alpha v1.0 specific tests
./install/validate-alpha-v1.0.sh
```

### Release Preparation
```bash
# Prepare clean distribution
./install/create-clean-distribution.sh

# Build macOS application bundle
./install/build-macos-app.sh

# Prepare final release package
./install/prepare-release.sh
```

### Repository Maintenance
```bash
# Clean up root directory
./install/cleanup-root.sh
```

---

**For user installation instructions, see the [documentation directory](../docs/installation/)**.
