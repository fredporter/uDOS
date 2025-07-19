# 🚀 uDOS Quick Start Installation Guide

**Get uDOS running in under 5 minutes**

## 📦 Prerequisites

- **macOS** 10.14+ or **Linux** (Ubuntu 20.04+)
- **VS Code** (recommended for optimal experience)
- **Git** (for installation)
- **Bash** shell environment

## ⚡ Quick Install

### Option 1: One-Line Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/fredporter/uDOS/main/install-udos.sh | bash
```

### Option 2: Manual Clone & Install
```bash
# Clone the repository
git clone https://github.com/fredporter/uDOS.git ~/uDOS
cd ~/uDOS

# Run installer
./install-udos.sh
```

## 🌀 First Launch

After installation:

```bash
# Navigate to uDOS directory
cd ~/uDOS

# Launch uDOS
./start-udos.sh
```

**VS Code Users** (Recommended):
```bash
code ~/uDOS
# Then use Cmd+Shift+P → "🌀 Start uDOS"
```

## ✅ Verify Installation

Run the comprehensive system check:
```bash
./uCode/check.sh all
```

You should see:
- ✅ All core systems operational
- ✅ VS Code integration active
- ✅ Package system ready
- ✅ Documentation accessible

## 🎯 Next Steps

1. **[📖 Read the User Manual](../user/manual.md)** - Learn all commands and features
2. **[🎮 Try the Interactive Tutorial](getting-started.md)** - Hands-on learning
3. **[🧙‍♂️ Meet Chester](../user/chester.md)** - Your AI companion guide

## 🆘 Troubleshooting

**Common Issues:**

### Permission Denied
```bash
chmod +x install-udos.sh
chmod +x start-udos.sh
```

### Missing Dependencies
The installer will check and guide you to install missing requirements.

### VS Code Integration Not Working
```bash
./extension/install-extension.sh
```

---

**Need Help?** Join our [GitHub Discussions](https://github.com/fredporter/uDOS/discussions) or check the [full installation guide](installation-guide.md).
