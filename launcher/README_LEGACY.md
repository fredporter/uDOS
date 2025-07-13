# 🐳 Docker Components (Legacy)

This folder contains Docker-based launcher components that are maintained for compatibility but **not recommended** for new installations.

## 🌟 **Recommended Approach**

Use the modern VS Code-integrated workflow:

1. Open uDOS in VS Code: `code ~/uDOS`
2. Use VS Code tasks: `Cmd+Shift+P` → "🌀 Start uDOS"
3. Or use the simple launcher: `./start-udos.sh`

## 🗂️ Legacy Components

- `uDOS.app` - macOS application bundle (auto-generated)
- `build-mac-launcher.sh` - App builder script
- `uDOS_Run.sh` - Shell launcher
- `assets/` - App icons and resources

## 🔧 When to Use Docker/Legacy

- **Containerized environments** (servers, CI/CD)
- **Isolated testing** 
- **Legacy systems** without VS Code support
- **Multi-user shared environments**

## 📦 Docker Usage

If you need Docker support:

```bash
cd ~/uDOS
docker-compose up
```

For the latest setup, see the main README.md and MODERNIZATION.md files.
