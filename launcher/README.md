# uDOS Launcher

This directory builds a clickable macOS `.app` for launching `uDOS`.

## 🔧 Files

- `uDOS_Run.sh` – Launch script embedded inside the `.app`
- `build-mac-launcher.sh` – CLI tool to build the app bundle
- `Run Launcher Builder.command` – GUI double-click builder
- `assets/diamonds.icns` – macOS icon (you must add this yourself)

## 🚀 Build Instructions

### GUI:
Double-click:
```bash
Run Launcher Builder.command
```

### Terminal:
```bash
cd launcher
chmod +x build-mac-launcher.sh
./build-mac-launcher.sh
```

## ✅ Result

A fully working `uDOS.app` will be created with your custom icon.

## 📁 .gitignore suggestion

```bash
/uDOS.app/
```
