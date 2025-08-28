# uDOS CLI Server System

## 🎯 **Purpose**

Enhanced CLI-only interface specifically designed for **GHOST** and **TOMB** roles who operate without UI/omni view and need terminal-only access with proper role-based restrictions.

## 👻 **Supported Roles**

### **GHOST (Level 10)**
- **Access**: Minimal read-only access
- **Commands**: Demo scripts only
- **Grid Limit**: 40x16 display
- **Use Case**: Demonstrations, limited exploration

### **🪦 TOMB (Level 20)**
- **Access**: Basic storage manager
- **Commands**: Archive scripts, file operations
- **Grid Limit**: 40x16 display
- **Use Case**: File archival, basic storage management

## 🚀 **Components**

### **1. Enhanced CLI Server** (`uCORE/system/server/cli_server.py`)
- **Role Detection**: Automatic role detection from `uMEMORY/user/installation.md`
- **Command Loading**: Loads uDATA commands from core + extensions
- **Access Control**: Role-based command access restrictions
- **Interactive Mode**: Full interactive CLI experience
- **Command Mode**: Direct command execution

### **2. CLI Launcher** (`uCORE/launcher/cli-only.sh`)
- **Role Validation**: Ensures only GHOST/TOMB roles use CLI launcher
- **Banner Display**: Shows role information and limitations
- **Color Output**: Terminal-friendly colored output
- **Command Routing**: Routes to enhanced CLI server

### **3. Launch Server** (`uCORE/system/server/launch_server.py`)
- **Auto-Detection**: Detects role and routes to appropriate server
- **CLI Routing**: GHOST/TOMB → CLI server
- **UI Routing**: CRYPT+ → UI server

## 📋 **Available Commands**

### **Built-in CLI Commands**
- **`HELP`** - Show available commands and help
- **`STATUS`** - Show CLI server status and role info
- **`COMMANDS`** - List all available commands for current role
- **`INFO`** - Show system information

### **Extension Commands**
Commands from extensions are automatically loaded and filtered by role access level:
- **Core Extensions**: deployment-manager, smart-input
- **User Extensions**: gemini-cli, smart-input (if access level permits)

## 🔧 **Usage**

### **Interactive Mode**
```bash
# Start interactive CLI session
./uCORE/launcher/cli-only.sh

# Or directly
python3 uCORE/system/server/cli_server.py
```

**Interactive Session:**
```
uDOS> help
Available commands for role 'ghost':
  HELP - Show help information
  STATUS - Show system status
  COMMANDS - List available commands

uDOS> status
uDOS CLI Server Status:
Role: ghost
Commands loaded: 4
Extensions directory: /Users/agentdigital/uDOS/extensions
Max grid: 40x16

uDOS> exit
Goodbye!
```

### **Direct Command Mode**
```bash
# Execute single command
./uCORE/launcher/cli-only.sh HELP
./uCORE/launcher/cli-only.sh STATUS

# Or with parameters
python3 uCORE/system/server/cli_server.py "[HELP*STATUS]"
```

### **Role Auto-Detection**
```bash
# Server automatically detects role and applies restrictions
python3 uCORE/system/server/launch_server.py

# For GHOST/TOMB: Launches CLI server
# For CRYPT+: Launches UI server
```

## 🔒 **Security & Access Control**

### **Role-Based Restrictions**
- Commands filtered by `role_access` level in uDATA format
- GHOST (10): Only commands with `role_access <= 10`
- TOMB (20): Only commands with `role_access <= 20`

### **Environment Isolation**
```bash
UDOS_MODE=cli          # CLI-only mode
UDOS_ROLE=ghost        # Current role
UDOS_UI=false          # No UI access
UDOS_MAX_GRID=40x16    # Grid limitations
```

### **Command Validation**
- All commands checked against role permissions
- Extension commands automatically filtered
- Access denied messages for restricted commands

## 📁 **File Structure**

```
uCORE/
├── system/
│   └── server/
│       ├── cli_server.py          # Enhanced CLI server
│       └── launch_server.py       # Role detection and routing
├── launcher/
│   └── cli-only.sh           # CLI-only launcher script
└── ...

extensions/
├── core/essential/*/commands/  # Core extension commands
├── user/*/commands/           # User extension commands
└── ...

uMEMORY/
├── system/uDATA-commands.json # Core uDOS commands
└── user/installation.md      # Role configuration
```

## 🎯 **Integration with Extensions**

### **Command Loading**
- Automatically discovers `uDATA-commands.json` files in extensions
- Merges core and extension commands
- Applies role-based filtering

### **Extension Support**
```json
{
  "command": "ARCHIVE",
  "syntax": "[ARCHIVE*path*type]",
  "description": "Archive files",
  "role_access": 20,
  "category": "storage"
}
```

### **Library Integration**
- Supports both shell and Python library functions
- Automatic library discovery in extension directories
- Cross-platform execution with proper error handling

## 🚀 **Benefits for GHOST/TOMB Roles**

### **✅ Advantages**
- **No UI Overhead**: Pure terminal interface, maximum performance
- **Role-Appropriate**: Commands filtered to role capabilities
- **Extension Support**: Access to approved extension functionality
- **Interactive**: Full CLI experience with help and status
- **Secure**: Proper access control and environment isolation

### **✅ Use Cases**
- **GHOST**: Demonstrations, system exploration, limited testing
- **TOMB**: File archival, basic storage operations, data management
- **Remote Access**: Perfect for SSH/terminal-only access
- **Automation**: CLI commands can be scripted and automated

## 🔄 **Command Processing Flow**

1. **Input**: User types command (interactive) or passes argument (direct)
2. **Parse**: Command parsed from `[COMMAND*params]` or `COMMAND` format
3. **Validate**: Check role access level against command requirements
4. **Route**:
   - Built-in commands → Direct execution
   - Extension commands → Library/script execution
   - Unknown commands → Error message
5. **Execute**: Run with proper environment and error handling
6. **Output**: Display results in terminal-friendly format

## 📚 **Examples**

### **GHOST Role Session**
```bash
./uCORE/launcher/cli-only.sh

┌─────────────────────────────────────────────┐
│              uDOS CLI Server                │
│          Text-Only Interface               │
├─────────────────────────────────────────────┤
│ Role: GHOST                                 │
├─────────────────────────────────────────────┤
│ Commands: help, status, commands            │
│ Type 'exit' to quit                        │
└─────────────────────────────────────────────┘

GHOST Role (Level 10):
• Minimal read-only access
• Demo scripts only
• Limited to 40x16 display
• Suitable for demonstrations

uDOS> help
Available commands for role 'ghost':
  HELP - Show help information
  STATUS - Show system status
  COMMANDS - List available commands
```

### **TOMB Role with Archive Command**
```bash
uDOS> help ARCHIVE
Command: ARCHIVE
Syntax: [ARCHIVE*path*type]
Description: Archive files and directories
Examples:
  [ARCHIVE*/tmp/data*tar.gz]
  [ARCHIVE*/logs*zip]

uDOS> [ARCHIVE*/tmp/test*tar.gz]
Archiving /tmp/test to /tmp/test.tar.gz...
Archive created successfully.
```

## ✅ **Status: COMPLETE**

The CLI server system provides a complete terminal-only interface for GHOST and TOMB roles with:
- Enhanced role-based command processing
- Extension integration
- Interactive and direct command modes
- Proper security and access control
- Clean terminal interface with helpful feedback

**Perfect for CLI-only operations without UI overhead!** 💻
