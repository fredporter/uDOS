# 📚 uDOS User Manual

**Version**: 1.0 Production  
**Last Updated**: July 18, 2025  
**Target Audience**: End users, developers, system administrators

---

## 🎯 Quick Start Guide

### Installation & Setup
1. **Install uDOS**: Run `./install-udos.sh` from the repository
2. **Launch System**: Use `./start-udos.sh` or the VS Code task "🌀 Start uDOS"
3. **Complete Setup**: Follow the interactive user setup process
4. **Verify Installation**: Run `CHECK SETUP` to validate all components

### First Commands
```bash
# Check system status
CHECK SETUP

# View your identity
IDENTITY

# Generate dashboard
DASH

# Get help
HELP
```

---

## 🏗️ Core System Architecture

### User Role System
uDOS implements a NetHack-inspired role system with four distinct user types:

- **🧙 Wizard**: Full system access, installation management, user creation
- **🔮 Sorcerer**: Advanced user with development privileges  
- **👻 Ghost**: Standard user with basic system access
- **😈 Imp**: Limited user with restricted permissions

### Directory Structure
```
uDOS/
├── uCode/           # Command center and system scripts
├── uMemory/         # User data and state (gitignored for privacy)
├── uTemplate/       # System templates and datasets
├── uScript/         # Automation scripts and utilities
├── package/         # Package management system
├── docs/           # Centralized documentation
└── extension/      # VS Code extension
```

---

## 🌀 uCode Shell Commands

### System Management

#### **CHECK** - System Validation & Information
```bash
CHECK SETUP          # Run full environment validation
CHECK TIME           # View/set timezone with dataset integration
CHECK TIMEZONE       # Enhanced timezone management
CHECK LOCATION       # View/set location with dataset integration
CHECK USER           # Template-driven user setup
CHECK IDENTITY       # Display current user identity
CHECK STATS          # Generate dashboard statistics
CHECK MAP            # Show current region information
CHECK DATASETS       # Show dataset statistics
CHECK TEMPLATES      # List available templates
```

#### **DASH** - Dashboard Generation
```bash
DASH                 # Generate standard dashboard
DASH enhanced        # Generate enhanced ASCII dashboard
DASH live            # Start interactive live dashboard
DASH stats           # Show dashboard statistics only
DASH export          # Export dashboard data as JSON
```

#### **IDENTITY** - User Management
```bash
IDENTITY             # Display current user identity
SETUP                # Run interactive user setup
```

### File & Data Management

#### **TREE** - Directory Structure
```bash
TREE                 # Generate clean file tree (production ready)
LIST [directory]     # List directory contents with filtering
```

#### **LOG** - Activity Logging
```bash
LOG                  # Interactive logging (mission/milestone/legacy)
RECENT               # Show recent moves (last 10)
```

#### **SEARCH** - Fast Text Search
```bash
SEARCH <pattern>     # Fast text search using ripgrep
```

### Template & Data Processing

#### **TEMPLATE** - Template Management
```bash
TEMPLATE list        # List available templates
TEMPLATE generate    # Generate content from templates
TEMPLATE validate    # Validate template system
```

#### **JSON** - Data Processing
```bash
JSON search <term>   # Search JSON datasets
JSON stats           # Show dataset statistics
JSON validate        # Validate JSON processor
```

#### **MAP** - Geographic Information
```bash
MAP GENERATE         # Generate full world map
MAP REGION <name>    # Show regional map (e.g., MAP REGION Europe)
MAP CITY <coords>    # Get city info (e.g., MAP CITY AX14)
MAP SHOW             # Display current region
MAP INFO             # Show map system information
```

### Script Execution

#### **RUN** - Script Execution
```bash
RUN <script-name>    # Execute uScript from system directories
```

#### **VB Commands** - Visual Basic Style Programming
```bash
DIM <variable>       # Declare variables
SET <var> = <value>  # Assign values
PRINT <expression>   # Output text
IF <condition>       # Conditional execution
FOR <loop>           # Loop structures
SUB <name>           # Define subroutines
CALL <subroutine>    # Call subroutines
```

### System Control

#### **System Management**
```bash
RESTART              # Restart uDOS shell
REBOOT               # Reboot entire system (with confirmation)
DESTROY              # Delete data (sandbox/memory/complete reset)
SYNC                 # Sync dashboard data
DEBUG                # Show debug information
VALIDATE             # Validate template-dataset integration
```

#### **Exit Commands**
```bash
EXIT                 # Exit uDOS shell
QUIT                 # Exit uDOS shell
BYE                  # Exit uDOS shell
```

---

## 🎮 VS Code Integration

### Available Tasks
Access via `Cmd+Shift+P` → "Tasks: Run Task"

#### Core System Tasks
- **🌀 Start uDOS** - Launch uDOS shell in VS Code terminal
- **🔍 Check uDOS Setup** - Run comprehensive system validation
- **📊 Generate Dashboard** - Create project dashboard
- **📺 Live Dashboard** - Start interactive live dashboard

#### Package Management Tasks
- **📦 Install All Packages** - Install all essential packages
- **🔍 Search with ripgrep** - Fast text search across workspace
- **🔍 Find files with fd** - Fast file finder
- **📄 View with bat** - Syntax-highlighted file viewing
- **📖 View markdown with glow** - Beautiful markdown rendering

#### AI & Companion Tasks
- **🤖 Install Gemini CLI** - Install AI assistant
- **🧠 Start Gemini Companion** - Launch AI assistance
- **🐕 Start Chester** - Start Wizard's Assistant
- **🎯 Initialize Chester** - Set up Chester AI companion

#### Development Tasks
- **📝 Create New Mission** - Generate mission from template
- **🌳 Generate File Tree** - Create project structure overview
- **✅ Validate Installation** - Comprehensive system validation
- **🔍 Quick Installation Check** - Fast validation check

### Extension Features
The uDOS VS Code extension provides:
- **uScript Language Support** - Syntax highlighting and IntelliSense
- **Command Integration** - Direct access to uDOS commands
- **Template System** - Quick template insertion and generation
- **User Role Awareness** - Respect permission levels
- **Chester AI Integration** - Seamless AI companion functionality

---

## 📦 Package System

### Available Packages

#### Text Editors
- **nano** - Simple command-line editor (auto-install)
- **micro** - Modern terminal editor (auto-install)  
- **helix** - Modal editor with LSP support (optional)

#### Utilities
- **ripgrep** - Ultra-fast text search (auto-install)
- **fd** - Fast file finder (auto-install)
- **bat** - Syntax-highlighted file viewer (auto-install)
- **glow** - Terminal markdown renderer (auto-install)
- **fzf** - Fuzzy finder for interactive selection (auto-install)
- **jq** - JSON processor (auto-install)

#### Development Tools
- **VS Code Extension** - Complete IDE integration (auto-install)
- **Gemini CLI** - AI assistant integration (optional)

### Package Management Commands
```bash
# Installation handled automatically during startup
# Individual packages can be installed via installation scripts:
./uCode/packages/install-<package>.sh
```

---

## 🤖 AI Companion System

### Chester - The Wizard's Assistant
Chester is your dedicated AI companion with small dog personality traits:

#### Features
- **Helpful Nature** - Always ready to assist with uDOS tasks
- **Technical Expertise** - Deep knowledge of uDOS architecture
- **Personality-Driven** - Loyal, energetic, and friendly interactions
- **Development Focused** - Specialized in uDOS workflows

#### Using Chester
```bash
# Via VS Code Tasks
🐕 Start Chester (Wizard's Assistant)
🎯 Initialize Chester

# Via Command Line
./uCode/companion-system.sh chester
./uCode/companion-system.sh init-chester
```

### Gemini CLI Integration
```bash
# Install Gemini CLI
./uCode/packages/install-gemini.sh

# Start Gemini companion
./uCode/companion-system.sh gemini

# Direct usage
gemini "Help me with uDOS development"
```

---

## 🔧 Advanced Features

### Shortcode System
Execute commands using shortcode syntax:
```bash
[run:script-name]        # Execute script
[bash:command]           # Run bash command
[check:setup]           # Run system check
```

### Template Integration
- **Dynamic Content Generation** - Templates with variable substitution
- **Dataset Integration** - Location, timezone, and terrain data
- **User Setup Templates** - Enhanced user configuration
- **Mission Templates** - Standardized project structures

### Error Handling
- **Comprehensive Logging** - All errors logged to uMemory/logs/errors
- **Error Context** - Detailed error information with context
- **Recovery Suggestions** - Intelligent error recovery recommendations

### Privacy & Security
- **Single-User Enforcement** - One installation per user
- **Data Isolation** - All user data in gitignored uMemory directory
- **Device Binding** - Installation tied to specific hardware
- **Permission Matrix** - Role-based access control

---

## 🔍 Troubleshooting

### Common Issues

#### System Validation Failures
```bash
CHECK SETUP              # Run comprehensive validation
DEBUG                    # Show detailed system information
VALIDATE                 # Validate template-dataset integration
```

#### Package Issues
```bash
# Check package installation status
./uCode/packages/manager-simple.sh list

# Reinstall packages
./uCode/packages/manager-simple.sh install-all
```

#### Identity Problems
```bash
SETUP                    # Reinitialize user setup
IDENTITY                 # Check current identity
DESTROY sandbox          # Reset sandbox only (preserves data)
```

### Validation Commands
```bash
# Quick validation
./uCode/validate-installation.sh quick

# Full validation  
./uCode/validate-installation.sh full

# Alpha validation
./uCode/validate-alpha.sh
```

---

## 📊 System Monitoring

### Dashboard Features
- **Real-time Statistics** - Live system metrics
- **Mission Tracking** - Progress monitoring
- **Resource Usage** - System resource information
- **Error Monitoring** - Recent error tracking
- **Package Status** - Installation and health status

### Logging System
- **Move Logs** - All commands logged with timestamps
- **Error Logs** - Comprehensive error tracking
- **System Logs** - System events and status changes
- **Mission Logs** - Project-specific activity tracking

---

## 🎯 Best Practices

### Daily Workflow
1. **Start with Dashboard** - `DASH` to see system status
2. **Check Recent Activity** - `RECENT` to review recent moves
3. **Use Templates** - Leverage template system for consistency
4. **Monitor Errors** - Regular `DEBUG` checks for issues
5. **Backup Important Data** - User data auto-backed up in uMemory

### Development Workflow
1. **Use VS Code Tasks** - Leverage pre-configured tasks
2. **Chester Integration** - Use AI assistant for guidance
3. **Template-Driven Development** - Use templates for consistency
4. **Regular Validation** - `CHECK SETUP` before major changes
5. **Error Monitoring** - Watch error logs during development

### Security Best Practices
1. **Single User Principle** - Never share installations
2. **Regular Validation** - Monitor system integrity
3. **Privacy Awareness** - Understand data isolation features
4. **Role Compliance** - Respect permission boundaries
5. **Backup Strategies** - Understand backup and recovery options

---

*This manual covers uDOS v1.0 production features. For advanced topics and development guides, see the technical documentation in `docs/roadmap/`.*
