# 📦 uDOS Installation Documentation

**Complete installation and setup guides for new users**

## 🚀 Quick Routes

### First-Time Users
1. **[⚡ Quick Start](quick-start.md)** - Get running in 5 minutes
2. **[🎮 Getting Started Tutorial](getting-started.md)** - Interactive hands-on learning
3. **[🛠️ Complete Installation Guide](installation-guide.md)** - Advanced setup options

### Installation Methods

#### One-Line Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/fredporter/uDOS/main/install-udos.sh | bash
```

#### Manual Clone & Install
```bash
git clone https://github.com/fredporter/uDOS.git ~/uDOS
cd ~/uDOS && ./install-udos.sh
```

#### Advanced Installation
- See [installation-guide.md](installation-guide.md) for custom setup options
- Docker installation options
- Multi-user environment setup
- Development environment configuration

## 🎯 Post-Installation

After successful installation:

1. **Verify Setup**: `./uCode/check.sh all`
2. **Launch uDOS**: `./start-udos.sh` or use VS Code integration
3. **Follow Tutorial**: Start with [getting-started.md](getting-started.md)
4. **Explore Documentation**: Use `SHOW list` to see all guides

## 🆘 Troubleshooting

### Common Issues

**Permission Errors**
```bash
chmod +x install-udos.sh start-udos.sh
```

**Missing Dependencies**
- The installer will detect and guide you to install requirements
- macOS: Ensure Homebrew is installed
- Linux: Ensure package manager access

**VS Code Integration Problems**
```bash
# Reinstall extension
./extension/install-extension.sh
```

### Getting Help

- **Built-in Help**: Run `HELP` in uDOS shell
- **Community**: [GitHub Discussions](https://github.com/fredporter/uDOS/discussions)  
- **Documentation**: Use `SHOW list` to browse all guides
- **AI Assistant**: Ask Chester for help with `CHESTER "help with installation"`

## 📋 System Requirements

### Minimum Requirements
- **macOS**: 10.14+ (Mojave)
- **Linux**: Ubuntu 18.04+ or equivalent
- **Storage**: 500MB free space
- **Memory**: 4GB RAM recommended

### Recommended Setup
- **VS Code**: Latest version for optimal experience
- **Git**: For updates and version control
- **Terminal**: Modern terminal with Unicode support
- **Internet**: For package installation and updates

---

**Next Steps**: Choose your installation path above and get started! 🌀
