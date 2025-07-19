# 🎮 uDOS Command Reference

**Complete reference for all uDOS commands and VS Code tasks**  
**Version**: 1.0 Production  
**Last Updated**: July 18, 2025

---

## 🌀 uCode Shell Commands

### System Information & Validation

#### `CHECK` - System Validation & Information
**Purpose**: Comprehensive system validation and information retrieval

| Command | Description | Example |
|---------|-------------|---------|
| `CHECK SETUP` | Run full environment validation | `CHECK SETUP` |
| `CHECK TIME` | View/set timezone with dataset integration | `CHECK TIME` |
| `CHECK TIMEZONE [coords]` | Enhanced timezone management | `CHECK TIMEZONE AX14` |
| `CHECK LOCATION [query]` | View/set location with dataset integration | `CHECK LOCATION London` |
| `CHECK USER` | Launch template-driven user setup | `CHECK USER` |
| `CHECK IDENTITY` | Display current user identity | `CHECK IDENTITY` |
| `CHECK STATS` | Generate dashboard statistics | `CHECK STATS` |
| `CHECK MAP` | Show current region information | `CHECK MAP` |
| `CHECK DATASETS` | Show dataset statistics | `CHECK DATASETS` |
| `CHECK TEMPLATES` | List available templates | `CHECK TEMPLATES` |

**Examples**:
```bash
# Basic system check
CHECK SETUP

# Location with dataset lookup
CHECK LOCATION "New York"

# Timezone by coordinates
CHECK TIMEZONE AX14
```

#### `IDENTITY` - User Identity Management
**Purpose**: Display and manage user identity information

```bash
IDENTITY                 # Show current user identity
```

#### `DEBUG` - System Debug Information
**Purpose**: Display comprehensive system debug information

```bash
DEBUG                    # Show debug information including:
                        # - System status
                        # - Directory status  
                        # - Template system status
                        # - Dataset status
                        # - Recent errors
```

### Dashboard & Monitoring

#### `DASH` - Dashboard Generation
**Purpose**: Generate and display system dashboard with various options

| Command | Description | Output |
|---------|-------------|--------|
| `DASH` | Generate standard dashboard | Standard dashboard display |
| `DASH enhanced` | Generate enhanced ASCII dashboard | ASCII art dashboard |
| `DASH live` | Start interactive live dashboard | Real-time updating dashboard |
| `DASH stats` | Show dashboard statistics only | Statistics summary |
| `DASH export` | Export dashboard data as JSON | JSON formatted data |

**Examples**:
```bash
# Standard dashboard
DASH

# Live updating dashboard
DASH live

# Export data for processing
DASH export
```

#### `SYNC` - Dashboard Synchronization
**Purpose**: Synchronize dashboard data

```bash
SYNC                     # Sync dashboard data
```

### File & Directory Management

#### `TREE` - Directory Structure
**Purpose**: Generate clean file tree showing project structure

```bash
TREE                     # Generate production-ready file tree
                        # Filters out: node_modules, .git, build artifacts
                        # Shows: Clean project structure
```

#### `LIST` - Directory Listing
**Purpose**: List directory contents with intelligent filtering

| Command | Description | Example |
|---------|-------------|---------|
| `LIST` | List current directory (filtered) | `LIST` |
| `LIST <directory>` | List specific directory | `LIST ./uMemory` |

**Features**:
- Filters out system folders (node_modules, .git, etc.)
- Shows up to 3 levels deep
- Uses tree command when available

#### `SEARCH` - Fast Text Search
**Purpose**: Fast text search using ripgrep

```bash
SEARCH <pattern>         # Search for pattern across uDOS
SEARCH "TODO"           # Find all TODO items
SEARCH "function.*main" # Regex search for functions
```

**Requirements**: ripgrep package (auto-installed)

### Activity & Logging

#### `LOG` - Activity Logging
**Purpose**: Interactive logging of missions, milestones, and legacy items

```bash
LOG                      # Interactive logging prompt
                        # Options: mission, milestone, legacy
```

**Workflow**:
1. Run `LOG` command
2. Choose log type (mission/milestone/legacy)
3. System logs entry with timestamp

#### `RECENT` - Recent Activity
**Purpose**: Display recent moves and activity

```bash
RECENT                   # Show last 10 moves from today's log
```

### Data Processing & Templates

#### `TEMPLATE` - Template Management
**Purpose**: Comprehensive template system management

| Command | Description | Example |
|---------|-------------|---------|
| `TEMPLATE list` | List available templates | `TEMPLATE list` |
| `TEMPLATE generate <type> <vars>` | Generate from template | `TEMPLATE generate mission vars.json` |
| `TEMPLATE validate` | Validate template system | `TEMPLATE validate` |

#### `JSON` - Data Processing
**Purpose**: JSON dataset processing and manipulation

| Command | Description | Example |
|---------|-------------|---------|
| `JSON search <term>` | Search JSON datasets | `JSON search "London"` |
| `JSON stats` | Show dataset statistics | `JSON stats` |
| `JSON validate` | Validate JSON processor | `JSON validate` |

#### `DATASET` / `DATA` - Dataset Management
**Purpose**: Alias for JSON commands

```bash
DATASET search <term>    # Same as JSON search
DATA stats              # Same as JSON stats
```

#### `GEN` / `GENERATE` - Content Generation
**Purpose**: Alias for template generation

```bash
GEN <type> <vars>       # Same as TEMPLATE generate
GENERATE mission vars   # Generate mission from template
```

### Geographic & Map System

#### `MAP` - Geographic Information System
**Purpose**: Comprehensive map and location management

| Command | Description | Example | Output |
|---------|-------------|---------|--------|
| `MAP GENERATE` | Generate full world map | `MAP GENERATE` | Complete world map file |
| `MAP REGION <name>` | Show regional map | `MAP REGION Europe` | Cities in specified region |
| `MAP CITY <coords>` | Get city information | `MAP CITY AX14` | Detailed city information |
| `MAP SHOW` | Display current region | `MAP SHOW` | Current location overview |
| `MAP INFO` | Show map system info | `MAP INFO` | System specifications |

**Map Specifications**:
- **Resolution**: 120×60 tiles (7,200 total)
- **Coordinates**: Letter-Letter-Number-Number format (e.g., AX14)
- **Columns**: A-DU (120 columns)
- **Rows**: 01-60 (60 rows)

**Examples**:
```bash
# Generate complete world map
MAP GENERATE

# Look up specific city
MAP CITY AX14

# Show European cities
MAP REGION Europe
```

### Script Execution

#### `RUN` - Script Execution
**Purpose**: Execute uScript files from system directories

```bash
RUN <script-name>       # Execute script from:
                       # - uScript/system/
                       # - uScript/utilities/
                       # - uMemory/scripts/
```

**Script Locations**:
- `uScript/system/` - System scripts
- `uScript/utilities/` - Utility scripts  
- `uMemory/scripts/` - User scripts

#### Visual Basic Commands
**Purpose**: Visual Basic-style programming interface

| Command | Syntax | Description | Example |
|---------|--------|-------------|---------|
| `DIM` | `DIM <variable>` | Declare variables | `DIM username` |
| `SET` | `SET <var> = <value>` | Assign values | `SET username = "john"` |
| `PRINT` | `PRINT <expression>` | Output text | `PRINT "Hello " + username` |
| `INPUT` | `INPUT <prompt>, <var>` | Get user input | `INPUT "Name:", username` |
| `IF` | `IF <condition> THEN` | Conditional execution | `IF username = "admin" THEN` |
| `FOR` | `FOR <var> = <start> TO <end>` | Loop structures | `FOR i = 1 TO 10` |
| `SUB` | `SUB <name>()` | Define subroutines | `SUB CalculateTotal()` |
| `CALL` | `CALL <subroutine>` | Call subroutines | `CALL CalculateTotal` |
| `REM` | `REM <comment>` | Comments | `REM This is a comment` |

### Advanced Features

#### `SHORTCODE` - Shortcode Management
**Purpose**: Manage and execute shortcode commands

| Command | Description | Example |
|---------|-------------|---------|
| `SHORTCODE list` | List available shortcodes | `SHORTCODE list` |
| `[run:script]` | Execute script via shortcode | `[run:backup]` |
| `[bash:command]` | Execute bash command | `[bash:ls -la]` |
| `[check:setup]` | Run system check | `[check:setup]` |

#### `ERROR` - Error Management
**Purpose**: Error handling and reporting

```bash
ERROR <subcommand>      # Error handling commands
                       # Managed by error-handler.sh
```

#### `CONTAINER` - Container Management
**Purpose**: Container system management (if available)

```bash
CONTAINER <subcommand>  # Container management
                       # Managed by bash-container.sh
```

### System Control

#### `SETUP` - User Setup
**Purpose**: Launch enhanced template-driven user setup

```bash
SETUP                   # Interactive user setup with:
                       # - Username configuration
                       # - Location setup (dataset-integrated)
                       # - Timezone setup (dataset-integrated)
                       # - Preferences configuration
                       # - Template integration
```

#### `VALIDATE` - System Validation
**Purpose**: Validate template-dataset integration

```bash
VALIDATE                # Validate:
                       # - Template system
                       # - Dataset system
                       # - Integration status
```

#### System Restart & Reset

| Command | Description | Confirmation | Data Impact |
|---------|-------------|--------------|-------------|
| `RESTART` | Restart uDOS shell | None | None |
| `REBOOT` | Reboot entire system | Required | None |
| `DESTROY` | Delete data | Interactive menu | Variable |

**DESTROY Options**:
- **A) Sandbox only** - Remove sandbox data only
- **B) Sandbox + Memory** - Remove sandbox and memory data
- **C) Complete system reset** - Full system reset

#### Exit Commands

```bash
EXIT                    # Exit uDOS shell gracefully
QUIT                    # Exit uDOS shell gracefully  
BYE                     # Exit uDOS shell gracefully
```

---

## 🎮 VS Code Tasks Reference

**Access**: `Cmd+Shift+P` → "Tasks: Run Task"

### Core System Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 🌀 Start uDOS | `shell: 🌀 Start uDOS` | Launch uDOS shell in VS Code terminal | build |
| 🔍 Check uDOS Setup | `shell: 🔍 Check uDOS Setup` | Run comprehensive system validation | test |
| 📊 Generate Dashboard | `shell: 📊 Generate Dashboard` | Create project dashboard | build |
| 📺 Live Dashboard | `shell: 📺 Live Dashboard` | Start interactive live dashboard | build |

### Package Management Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 📦 Install All Packages | `shell: 📦 Install All Packages` | Install all essential packages | build |
| 🔍 Search with ripgrep | `shell: 🔍 Search with ripgrep` | Fast text search across workspace | test |
| 🔍 Find files with fd | `shell: 🔍 Find files with fd` | Fast file finding | test |
| 📄 View with bat | `shell: 📄 View with bat` | Syntax-highlighted file viewing | test |
| 📖 View markdown with glow | `shell: 📖 View markdown with glow` | Beautiful markdown rendering | test |

### AI & Companion Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 🤖 Install Gemini CLI | `shell: 🤖 Install Gemini CLI` | Install Google Gemini CLI | build |
| 🧠 Start Gemini Companion | `shell: 🧠 Start Gemini Companion` | Start Gemini CLI with uDOS context | build |
| 🐕 Start Chester | `shell: 🐕 Start Chester (Wizard's Assistant)` | Start Chester, your dedicated assistant | build |
| 🎯 Initialize Chester | `shell: 🎯 Initialize Chester` | Initialize Chester with personality | build |

### Development Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 📝 Create New Mission | `shell: 📝 Create New Mission` | Generate new mission from template | build |
| 🌳 Generate File Tree | `shell: 🌳 Generate File Tree` | Create project structure overview | build |
| ✅ Validate Installation | `shell: ✅ Validate Installation` | Comprehensive validation of uDOS | test |
| 🔍 Quick Installation Check | `shell: 🔍 Quick Installation Check` | Quick validation of core components | test |

### Extension Development Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 🎯 Compile VS Code Extension | `shell: 🎯 Compile VS Code Extension` | Compile TypeScript extension | build |
| 📦 Install Extension Dependencies | `shell: 📦 Install Extension Dependencies` | Install extension dependencies | build |

### Maintenance Tasks

| Task | ID | Description | Group |
|------|----|-----------| ------|
| 🧹 Clean uDOS (Destroy) | `shell: 🧹 Clean uDOS (Destroy)` | Clean uDOS system | build |
| 🏗️ Reorganize uDOS | `shell: 🏗️ Reorganize uDOS` | Migrate to new architecture | build |

---

## 🔧 Advanced Command Usage

### Command Chaining
```bash
# Multiple commands in sequence
CHECK SETUP && DASH && RECENT

# Conditional execution
CHECK SETUP || DEBUG
```

### Variable Usage (VB Commands)
```bash
DIM project_name
SET project_name = "MyProject"
PRINT "Working on: " + project_name
```

### Template Integration
```bash
# Generate content with templates
TEMPLATE generate mission project-vars.json

# List available templates
TEMPLATE list

# Validate template system
TEMPLATE validate
```

### Dataset Queries
```bash
# Search locations
JSON search "London"

# Get statistics
JSON stats

# Find timezone by coordinates
CHECK TIMEZONE AX14
```

### Map Commands
```bash
# Complete map generation
MAP GENERATE

# Regional focus
MAP REGION "North America"

# Specific location lookup
MAP CITY "BF23"

# Current status
MAP SHOW
```

---

## 🔍 Command Categories

### **Information Commands**
`CHECK`, `IDENTITY`, `DEBUG`, `RECENT`, `MAP INFO`

### **Action Commands**  
`DASH`, `LOG`, `RUN`, `SETUP`, `VALIDATE`

### **Data Commands**
`SEARCH`, `JSON`, `TEMPLATE`, `MAP`

### **System Commands**
`RESTART`, `REBOOT`, `DESTROY`, `SYNC`

### **Navigation Commands**
`TREE`, `LIST`, `MAP SHOW`

### **Development Commands**
`VB commands`, `SHORTCODE`, `CONTAINER`, `ERROR`

---

## 💡 Pro Tips

### Efficiency
- Use **VS Code tasks** for common operations
- Leverage **shortcode syntax** for quick commands
- Use **Chester AI** for guidance and assistance
- **Template system** for consistent content generation

### Monitoring
- Regular `CHECK SETUP` for system health
- `DEBUG` for troubleshooting issues  
- `RECENT` to review activity
- `DASH live` for real-time monitoring

### Development
- **VB commands** for scripting and automation
- **Template system** for consistent development
- **Package system** for tool integration
- **Error handling** for robust development

---

*Complete command reference for uDOS v1.0 production system. For detailed examples and tutorials, see the User Manual.*
