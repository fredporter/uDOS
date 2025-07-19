# 🛠️ uDOS Installation Scripts

**Centralized installation and build management for uDOS v1.0**

## 📁 Script Directory

| Script | Purpose | Usage |
|--------|---------|-------|
| `validate-alpha-v1.0.sh` | Alpha v1.0 validation | `./install/validate-alpha-v1.0.sh` |
| `validate-comprehensive.sh` | Comprehensive system check | `./install/validate-comprehensive.sh` |
| `build-macos-app.sh` | macOS app bundle builder | `./install/build-macos-app.sh` |
| `prepare-release.sh` | Release preparation | `./install/prepare-release.sh` |
| `create-clean-distribution.sh` | Clean distribution builder | `./install/create-clean-distribution.sh` |
| `cleanup-root.sh` | Repository cleanup | `./install/cleanup-root.sh` |

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
