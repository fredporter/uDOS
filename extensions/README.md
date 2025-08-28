# uDOS Extensions System

## 🏗️ **Architecture Overview**

The uDOS extension system provides a clean, cross-platform foundation for extending functionality while maintaining maximum compatibility.

### **Distribution Strategy**

- **`uCORE/extensions/`** - Core essential extensions (ships with uDOS)
- **`extensions/user/`** - User-installed extensions
- **`extensions/platform/`** - Platform-specific shims (when absolutely necessary)
- **`extensions/install/`** - Installation workspace

### **Cross-Platform Core Principles**

✅ **POSIX + Python**: Core logic uses portable shell and Python3
✅ **Avoid GNU-only**: No `sed -r`, prefer `awk` and portable commands
✅ **Single CLI Entry**: All extensions accessible via main `udos` command
✅ **Platform Shims**: Only when unavoidable, isolated to `platform/` directory

## 📁 **Directory Structure**

```
extensions/
├── uCORE/extensions/        # Core essential extensions (ships with uDOS)
│   ├── deployment-manager/
│   │   ├── manifest.json
│   │   ├── deployment-manager.sh
│   │   └── commands/uDATA-commands.json
│   ├── viewport-manager/
│   ├── smart-input/
│   └── registry.json       # uCORE extensions registry
│
├── user/                   # User-installed extensions
│   ├── ai-tools/
│   │   └── gemini-cli/
│   └── registry.json       # User extensions registry
│
├── platform/               # Platform-specific code (minimal)
│   ├── linux/
│   ├── macos/
│   ├── windows/
│   └── universal/          # Cross-platform utilities
│
├── install/                # Installation workspace
│   ├── downloads/          # Downloaded extension packages
│   ├── temp/              # Installation temporary files
│   └── cache/             # Installation cache
│
├── sandbox/                # Extension development
│   ├── dev/               # Development extensions
│   ├── testing/           # Test extensions
│   └── experiments/       # Experimental features
│
├── extension-manager.sh    # Extension management tool
└── registry.json          # Master registry (all extensions)
```

## 🚀 **Extension Management**

### **List Extensions**
```bash
./extensions/extension-manager.sh list           # All extensions
./extensions/extension-manager.sh list core     # uCORE extensions only
./extensions/extension-manager.sh list user     # User extensions only
```

### **Install User Extension**
```bash
./extensions/extension-manager.sh install my-tools /path/to/extension
```

### **Extension Information**
```bash
./extensions/extension-manager.sh info deployment-manager
./extensions/extension-manager.sh info gemini-cli
```

### **Validate Extension**
```bash
./extensions/extension-manager.sh validate /path/to/extension
```

## 📋 **Extension Manifest Format**

Each extension requires a `manifest.json` file in uDATA-compatible format:

```json
{
  "metadata": {
    "name": "extension-name",
    "version": "1.0.0",
    "type": "essential|user",
    "platform": "universal|linux|macos|windows"
  },
  "description": "Extension description",
  "author": "Extension Author",
  "commands": ["COMMAND1", "COMMAND2"],
  "dependencies": {
    "shell": ["required", "shell", "commands"],
    "python": ["required", "python", "modules"]
  },
  "integration": {
    "sandbox": true,
    "workflow": true,
    "backup": false
  },
  "distribution": "core|user",
  "features": ["feature1", "feature2"]
}
```

## 🔧 **Current Extensions**

### **Core Essential Extensions (Ship with uDOS in uCORE)**

#### **deployment-manager**
- **Purpose**: Comprehensive deployment system
- **Commands**: `DEPLOY`, `DEPLOY_DRONE`, `DEPLOY_STANDALONE`, etc.
- **Features**: Multiple installation types, validation, remote deployment

#### **viewport-manager**
- **Purpose**: Window and viewport management
- **Commands**: `VIEWPORT`, `WINDOW`
- **Features**: Multi-mode support, Chromium integration

#### **smart-input**
- **Purpose**: Core uDOS smart input system (unique to uDOS)
- **Commands**: `INPUT`, `INPUT_FORM`, `INPUT_WIZARD`, etc.
- **Features**: Dynamic forms, intelligent suggestions, multi-step wizards

### **User Extensions (Install Separately)**

#### **gemini-cli**
- **Purpose**: Google Gemini AI integration
- **Commands**: `ASSIST`, `COMMAND`
- **Features**: Natural language interface, AI assistance## 🛠️ **Creating Extensions**

### **1. Basic Structure**
```bash
mkdir -p my-extension/{commands,library/{shell,python},templates}
```

### **2. Create Manifest**
```json
{
  "metadata": {"name": "my-extension", "version": "1.0.0", "type": "user", "platform": "universal"},
  "description": "My custom extension",
  "commands": ["MYCMD"],
  "dependencies": {"shell": ["awk"], "python": []},
  "integration": {"sandbox": true, "workflow": false, "backup": false}
}
```

### **3. Implement Commands (uDATA format)**
```json
{
  "metadata": {"version": "1.0.0", "extension": "my-extension", "total_commands": 1}
}
{"command": "MYCMD", "syntax": "[MYCMD*param]", "description": "My command", "category": "custom", "role_access": 30, "examples": ["[MYCMD*test]"], "library": "my-script.sh", "function": "my_function"}
```

### **4. Cross-Platform Shell Library**
```bash
#!/usr/bin/env bash
# Use POSIX-compliant shell code

my_function() {
    local param="$1"

    # Use portable commands
    echo "$param" | awk '{print toupper($0)}'  # Instead of tr

    # Check dependencies
    command -v required_tool >/dev/null 2>&1 || {
        echo "Error: required_tool not found" >&2
        return 1
    }
}
```

### **5. Install Extension**
```bash
./extensions/extension-manager.sh install my-extension /path/to/my-extension
```

## 🔗 **Integration with uDOS**

### **Command Integration**
Extensions automatically integrate with the uDOS command system:
```bash
# Extension commands available in help system
help DEPLOY
help ASSIST

# Commands work from any uDOS interface
[DEPLOY*drone*/tmp/installation]
[ASSIST*"help me debug this script"]
```

### **Sandbox Integration**
Extensions that support sandbox integration:
```bash
sandbox EXTENSION CREATE my-extension
sandbox EXTENSION TEST my-extension
```

### **Workflow Integration**
Extensions can participate in workflow tracking:
```bash
sandbox WORKFLOW MOVE development "Installing new extension"
```

## 🎯 **Benefits**

✅ **Clean Distribution**: Core vs user separation
✅ **Cross-Platform**: POSIX + Python foundation
✅ **Unified Commands**: All extensions use uDATA command format
✅ **Easy Installation**: Simple extension manager
✅ **Development Ready**: Sandbox integration for testing
✅ **Backwards Compatible**: Works with existing uDOS systems

## 🏛️ **Legacy Migration**

Previous extension files have been reorganized:

- **`uSCRIPT/extensions/`** → **`extensions/legacy-udos-extensions/`** (backup)
- **System tools** → **`extensions/core/essential/`**
- **AI tools** → **`extensions/user/ai-tools/`**
- **Development tools** → **`extensions/user/development-tools/`**

## 📚 **Documentation**

- **Extension Development**: See individual extension README files
- **Command Reference**: Use `help <COMMAND>` for any extension command
- **API Documentation**: See `uCORE/README.md` for core integration APIs

---

**The extension system grows through plugins, not core changes.** 🔌
