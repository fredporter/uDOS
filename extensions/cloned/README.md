# Cloned Extensions Directory

This directory contains third-party extensions cloned from external repositories. These are **NOT tracked in git** and must be installed locally.

## 📦 Available Extensions

### MeshCore (v1.2.14+ Integration)

**Repository:** https://github.com/meshcore-dev/MeshCore  
**Purpose:** Mesh networking hardware integration, device management, signal propagation

**Installation:**
```bash
cd extensions/cloned/
git clone https://github.com/meshcore-dev/MeshCore.git meshcore
```

**uDOS Integration:**
- `extensions/play/meshcore_integration.py` - Integration framework
- `extensions/play/meshcore_device_manager.py` - Device management
- `extensions/play/meshcore_signal_calculator.py` - Signal analysis

**Used For:**
- Grid rendering with device overlays
- Mesh network simulation
- Signal propagation analysis
- Device provisioning and management

**Status:** Optional dependency (uDOS works without it)

---

### CoreUI Icons (Optional)

**Repository:** https://github.com/coreui/coreui-icons  
**Purpose:** Icon library for UI components

**Installation:**
```bash
cd extensions/cloned/
git clone https://github.com/coreui/coreui-icons.git coreui
```

---

### Micro Editor (Optional)

**Repository:** https://github.com/zyedidia/micro  
**Purpose:** Terminal-based text editor

**Installation:**
```bash
cd extensions/cloned/
git clone https://github.com/zyedidia/micro.git micro
```

---

### Typo (Optional)

**Repository:** https://github.com/rossrobino/typo  
**Purpose:** Typography utilities

**Installation:**
```bash
cd extensions/cloned/
git clone https://github.com/rossrobino/typo.git typo
```

---

## 🔧 Managing Cloned Extensions

**Update All:**
```bash
cd extensions/cloned/
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "Updating $dir..."
        cd "$dir" && git pull && cd ..
    fi
done
```

**Check Status:**
```bash
cd extensions/cloned/
for dir in */; do
    if [ -d "$dir/.git" ]; then
        echo "=== $dir ==="
        cd "$dir" && git status --short && cd ..
    fi
done
```

**Remove Extension:**
```bash
cd extensions/cloned/
rm -rf <extension-name>
```

---

## 📋 Git Configuration

**All cloned extensions are ignored by git:**
- Defined in `.gitignore` line 85: `extensions/cloned/`
- Only `.gitkeep` is tracked to preserve directory structure
- Users install extensions locally as needed

**Why Not Submodules?**
- Keeps uDOS core lean and focused
- Users install only what they need
- Avoids git submodule complexity
- Easier to update extensions independently

---

## 🚀 Extension Development

To develop your own extension:

1. Clone your extension to `extensions/cloned/your-extension/`
2. Create integration code in `extensions/play/` or `extensions/core/`
3. Extensions in `cloned/` are automatically ignored by git
4. Only commit your integration code, not the cloned repo

---

## ℹ️ Notes

- **MeshCore** is actively integrated in v1.2.14+ for mesh networking features
- Other extensions are optional and may be used in future versions
- Check extension repositories for their own documentation and licenses
- Extensions update independently from uDOS core

**Last Updated:** v1.2.21 (December 8, 2025)
