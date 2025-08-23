# 🚀 uDOS QuickStart Guide v1.3.3

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
3. **Role Selection**: Choose your access level (Ghost → Wizard)
4. **Interface Launch**: Opens Terminal or VS Code based on availability

### 🎭 **Role-Based Access**
- **👻 Ghost** (Level 10) - Demo & Evaluation
- **⚰️ Tomb** (Level 20) - Archive Management  
- **🤖 Drone** (Level 40) - Task Automation
- **👹 Imp** (Level 60) - Development Tools
- **🔮 Sorcerer** (Level 80) - Advanced User
- **🧙‍♂️ Wizard** (Level 100) - Full Development Access

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
- **uMEMORY/** → User memory & workspace (missions, notes, personal archive)
- **uKNOWLEDGE/** → Shared knowledge base and references
- **dev/** → Development environment (tools, notes, VS Code integration)
- **docs/** → Documentation system (guides, standards, technical references)
- **extensions/** → Extension framework (core/user separation)
- **sandbox/** → User's active workspace (tasks, experiments, daily activity)
- **uNETWORK/** → Server endpoints, middleware, and network configs

### **How They Work Together**

```
User (sandbox/)
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
   Output → User
```

### **Step-by-Step Flow**

1. **User Input**: Begin in `sandbox/` with commands or tasks
2. **Core Processing**: `uCORE/` handles system operations and routing
3. **Script Execution**: `uSCRIPT/` manages multi-language script execution
4. **Data Management**: `uMEMORY/` stores user workspace and archive
5. **Knowledge Access**: `uKNOWLEDGE/` provides shared references
6. **Extension Layer**: Role-based capabilities and extensions enhance processing
7. **Output**: Results returned to user in `sandbox/` workspace

---

## 🎮 **Launch Modes**

### 🖥️ **Terminal Mode (Default)**
- Native terminal interface with uDOS command system
- Full command-line access to all system functions
- Role-based command availability
- Real-time status and logging

### 🧙‍♂️ **VS Code Development Mode** (Wizard Role)
- Complete integrated development environment
- Git integration and version control
- Pre-configured tasks and debugging
- Extension marketplace access
- Dual terminal/GUI workflow

### 🌐 **Server Mode** (Advanced)
- Web-based interface via uNETWORK server
- Multi-user capability
- Remote access and collaboration
- Browser-based file management

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
# Enable development features:
export UDOS_DEV_MODE="true"
# Access additional debugging and development tools
```

---

## 📚 **Next Steps**

### **Learn More**
- **📖 Full Documentation**: `docs/README.md`
- **🔧 Development Guide**: `dev/README.md`  
- **🎭 Role Capabilities**: `docs/User-Role-Capabilities.md`
- **🌐 Server Setup**: `uNETWORK/server/README.md`

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

**uDOS is now ready to use on your system.**

- ✅ Cross-platform compatibility verified
- ✅ Dependencies automatically managed  
- ✅ Role-based access configured
- ✅ Development environment available

**Start exploring the universal device operating system!** 🚀

---

**uDOS v1.3.3** - Universal Device Operating System  
*Simple one-click launchers for any platform*
