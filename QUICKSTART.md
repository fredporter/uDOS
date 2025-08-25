# 🚀 uDOS QuickStart Guide v1.4.0

**Get up and running with uDOS in under 5 minutes on any platform**

## ⚡ **Quick Launch (All Platforms)**

### 1️⃣ **Clone Repository**
```bash
git clone https://github.com/fredporter/uDOS.git
cd uDOS
```

### 2️⃣ **Choose Your Platform Launcher**

#### 🍎 **macOS**
```bash
# Double-click or run:
open "Launch-uDOS-macOS.command"
```

#### 🪟 **Windows**
```bash
# Double-click or run:
"Launch-uDOS-Windows.bat"
```

#### 🐧 **Ubuntu 22+**
```bash
# Make executable and run:
chmod +x "Launch-uDOS-Ubuntu.sh"
./Launch-uDOS-Ubuntu.sh
```

### 3️⃣ **You're Ready!**
uDOS will automatically:
- Detect dependencies and install if needed
- Start the appropriate interface for your system
- Provide role-based access options

---

## 🎯 **What Happens Next?**

### 🔄 **First Launch**
1. **Platform Detection**: Automatically detects your OS and requirements
2. **Dependency Check**: Installs missing dependencies (Python3, Git, etc.)
3. **Three-Mode Display**: Choose CLI Terminal, Desktop App, or Web Export
4. **Role Selection**: Choose your access level (Ghost → Wizard)
5. **Development Environment**: Access to /dev folder (Wizard + DEV mode only)

### 🎭 **Role-Based Access**
- **👻 Ghost** (Level 10) - CLI Terminal only, demo access
- **⚰️ Tomb** (Level 20) - CLI Terminal, archive management
- **🤖 Drone** (Level 40) - All modes, task automation, desktop app access
- **👹 Imp** (Level 60) - Development tools, sandbox workspace
- **🔮 Sorcerer** (Level 80) - Advanced features, memory management
- **🧙‍♂️ Wizard** (Level 100) - Full access, /dev environment, core development

---

## 🛠️ **Platform Requirements**

### 🍎 **macOS**
- **Version**: macOS 10.15+ (Catalina or later)
- **Built-in**: Terminal, basic shell tools
- **Auto-detected**: Python3, VS Code
- **Optional**: VS Code for enhanced development

### 🪟 **Windows**
- **Version**: Windows 10+
- **Required**: Git for Windows (with Git Bash) OR WSL
- **Download Git**: https://git-scm.com/download/win
- **Desktop App**: Native Tauri application for DRONE+ roles
- **Auto-detected**: VS Code, Python3

### 🐧 **Ubuntu 22+**
- **Version**: Ubuntu 22.04+
- **Auto-installed**: bash, python3, git, curl
- **Requires**: sudo access for dependency installation
- **Native**: Shell integration

---

## 🏗️ **System Overview**

### **Core Directories**

- **uCORE/** → Core system & utilities (shell, datasets, templates, installers)
- **uSCRIPT/** → Script management system (multi-language engines, libraries, registry)
- **uMEMORY/** → User memory & permanent data archive (user/, role/, templates/)
- **uKNOWLEDGE/** → Shared knowledge base and references
- **sandbox/** → Active workspace for all logging, sessions, and flushable work
- **dev/** → Core development environment (wizard role + DEV mode only)
- **docs/** → Documentation system (guides, standards, technical references)
- **extensions/** → Extension framework (core/user separation)
- **uNETWORK/** → Server endpoints, middleware, and three-mode display system

### **How They Work Together**

```
User (sandbox/ - active workspace)
      |
      v
+-----------+      +-----------+
|   uCORE   | ---> | uSCRIPT   |
+-----------+      +-----------+
      |                  |
      v                  v
  +--------+        +-----------+
  | uMEMORY|        |uKNOWLEDGE |
  +--------+        +-----------+
      |
      v
+-------------------------+
|    Extensions &         |
|   Role Capabilities     |
+-------------------------+
      |
      v
   Three-Mode Display → User
   (CLI/Desktop/Web)
```

### **Step-by-Step Flow**

1. **User Input**: Begin in `sandbox/` with commands or tasks
2. **Core Processing**: `uCORE/` handles system operations and routing
3. **Script Execution**: `uSCRIPT/` manages multi-language script execution
4. **Active Work**: All logging and session data flows through `sandbox/`
5. **Data Archive**: Important data filed from `sandbox/` to `uMEMORY/`
6. **Knowledge Access**: `uKNOWLEDGE/` provides shared references
7. **Extension Layer**: Role-based capabilities and extensions enhance processing
8. **Three-Mode Output**: Results delivered via CLI Terminal, Desktop App, or Web Export

---

## 🎮 **Display Modes**

### 🖥️ **CLI Terminal Mode** (All Roles)
- Native terminal interface with uDOS command system
- Full command-line access to role-appropriate functions
- Real-time logging in sandbox/logs/
- Available on all platforms and roles

### 🖼️ **Desktop Application Mode** (DRONE+ Roles)
- Native Tauri desktop application
- System tray integration and window management
- Enhanced file browser and visual interfaces
- Cross-platform native app experience

### 🌐 **Web Export Mode** (DRONE+ Roles)
- Browser-based interface via uNETWORK server
- Remote access and collaboration capabilities
- Share dashboards and terminals
- Real-time WebSocket communication

### 🧙‍♂️ **Development Mode** (Wizard + DEV Only)
- Full VS Code integration with /dev environment
- Core system development and debugging
- Git integration and extension development
- Protected development workspace

---

## 🚨 **Common Issues & Solutions**

### 🍎 **macOS**

#### **"Cannot be opened because it is from an unidentified developer"**
```bash
# Right-click launcher → Open → Open anyway
# Or manually allow:
chmod +x "Launch-uDOS-macOS.command"
```

#### **VS Code Not Detected**
```bash
# Install VS Code command line tools:
# Open VS Code → Cmd+Shift+P → "Shell Command: Install 'code' command in PATH"
```

### 🪟 **Windows**

#### **"'bash' is not recognized"**
```bash
# Install Git for Windows (includes Git Bash):
# Download: https://git-scm.com/download/win
# Or install WSL: wsl --install
```

#### **Permission Denied**
```cmd
# Run Command Prompt as Administrator
# Right-click launcher → "Run as administrator"
```

### 🐧 **Ubuntu**

#### **Missing Dependencies**
```bash
# Launcher auto-installs, but if issues:
sudo apt update
sudo apt install python3 python3-pip git bash curl
```

#### **Permission Issues**
```bash
chmod +x "Launch-uDOS-Ubuntu.sh"
# For sudo issues during dependency install:
sudo visudo  # Add your user to sudoers if needed
```

---

## 🔧 **Advanced Configuration**

### **Custom Installation Path**
```bash
# Default: ~/uDOS or current directory
# To specify custom path:
export UDOS_ROOT="/path/to/your/udos"
```

### **Role Override**
```bash
# Force specific role on launch:
export UDOS_CURRENT_ROLE="wizard"
./Launch-uDOS-[platform].[ext]
```

### **Development Mode**
```bash
# Enable development features (Wizard role required):
export UDOS_DEV_MODE="true"
# Access /dev environment for core development
# Full VS Code integration and build tools
```

---

## 📚 **Next Steps**

### **Learn More**
- **📖 Full Documentation**: `docs/README.md`
- **🔧 Development Guide**: `dev/README.md` (Wizard + DEV mode)
- **🎭 Role Capabilities**: `docs/User-Role-Capabilities.md`
- **🌐 Three-Mode Display**: `uNETWORK/server/README.md`
- **🗃️ Data Architecture**: `sandbox/STRUCTURE.md` and `uMEMORY/README.md`

### **Get Help**
- **💬 Community**: GitHub Discussions
- **🐛 Issues**: GitHub Issues
- **📧 Support**: Check README.md for contact info

### **Contribute**
- **🤝 Contributing**: See CONTRIBUTING.md
- **🔀 Fork & PR**: Standard GitHub workflow
- **📝 Documentation**: Help improve guides

---

## 🎉 **You're All Set!**

**uDOS v1.4.0 is now ready to use on your system.**

- ✅ Cross-platform compatibility verified
- ✅ Dependencies automatically managed
- ✅ Three-mode display system available
- ✅ Role-based access configured
- ✅ Sandbox workspace for active work
- ✅ Development environment available (Wizard + DEV mode)

**Start exploring the universal device operating system with organized data architecture!** 🚀

---

**uDOS v1.4.0** - Universal Device Operating System
*Three-mode display system with clean data separation*
