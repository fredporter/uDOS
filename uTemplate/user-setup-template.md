# 🎭 uDOS User Setup Interface

**Template**: User Setup Data Collection  
**Version**: 2.0 - Template System Integration  
**Format**: uTemplate with shortcodes and variables

---

## 📋 Setup Questions

[SETUP_INTRO]
Welcome to uDOS v1.0! Let's set up your personal development environment.
This setup will create your user profile and configure system preferences.
[/SETUP_INTRO]

### 👤 Identity Information

[INPUT_USERNAME]
Question: Enter your username (required)
Variable: $USERNAME
Validation: required,alphanumeric
Default: $USER
[/INPUT_USERNAME]

[INPUT_FULLNAME]
Question: Enter your full name (optional)
Variable: $FULL_NAME
Validation: optional,text
Default: 
[/INPUT_FULLNAME]

[INPUT_EMAIL]
Question: Enter your email address (optional)
Variable: $EMAIL
Validation: optional,email
Default: 
[/INPUT_EMAIL]

### 🌍 Location & Time

[INPUT_LOCATION]
Question: Enter your location code (3-letter city code, e.g., NYC, LON, TOK)
Variable: $LOCATION_CODE
Validation: optional,alpha,3
Default: 
Help: Used for timezone and location-aware features
[/INPUT_LOCATION]

[INPUT_TIMEZONE]
Question: Enter your timezone (e.g., America/New_York, Europe/London)
Variable: $TIMEZONE
Validation: optional,timezone
Default: $SYSTEM_TIMEZONE
Help: Auto-detected from system if not specified
[/INPUT_TIMEZONE]

### ⚙️ System Preferences

[INPUT_THEME]
Question: Choose your theme preference
Variable: $THEME
Validation: required,options
Options: default,dark,light,auto
Default: default
Help: Controls terminal colors and VS Code integration
[/INPUT_THEME]

[INPUT_DEBUG_MODE]
Question: Enable debug mode for detailed logging?
Variable: $DEBUG_MODE
Validation: required,boolean
Options: true,false
Default: false
Help: Shows detailed system information and error traces
[/INPUT_DEBUG_MODE]

[INPUT_AUTO_BACKUP]
Question: Enable automatic backup of user data?
Variable: $AUTO_BACKUP
Validation: required,boolean
Options: true,false
Default: true
Help: Automatically backs up uMemory data during system operations
[/INPUT_AUTO_BACKUP]

[INPUT_AI_COMPANION]
Question: Enable Chester AI companion?
Variable: $AI_COMPANION_ENABLED
Validation: required,boolean
Options: true,false
Default: true
Help: Chester provides intelligent assistance and development support
[/INPUT_AI_COMPANION]

### 🎯 Development Preferences

[INPUT_DEFAULT_ROLE]
Question: Choose your default user role
Variable: $DEFAULT_ROLE
Validation: required,options
Options: wizard,sorcerer,ghost,imp
Default: ghost
Help: wizard=full access, sorcerer=advanced dev, ghost=standard, imp=basic
[/INPUT_DEFAULT_ROLE]

[INPUT_AUTO_PACKAGES]
Question: Automatically install recommended packages?
Variable: $AUTO_INSTALL_PACKAGES
Validation: required,boolean
Options: true,false
Default: true
Help: Installs ripgrep, fd, bat, glow, fzf, jq automatically
[/INPUT_AUTO_PACKAGES]

[INPUT_VSCODE_INTEGRATION]
Question: Install uDOS VS Code extension?
Variable: $VSCODE_EXTENSION
Validation: required,boolean
Options: true,false
Default: true
Help: Provides syntax highlighting, tasks, and IDE integration
[/INPUT_VSCODE_INTEGRATION]

---

## 🔄 Variable Processing

[PROCESS_VARIABLES]
# System variable generation
$SETUP_DATE = $(date '+%Y-%m-%d %H:%M:%S')
$SETUP_TIMESTAMP = $(date '+%s')
$USER_ID = $(echo "$USERNAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
$SYSTEM_TIMEZONE = $(timedatectl show --property=Timezone --value 2>/dev/null || date +%Z)
$UHOME_PATH = $HOME/uDOS
$UMEMORY_PATH = $UHOME_PATH/uMemory

# Location data lookup if location code provided
if [[ -n "$LOCATION_CODE" ]]; then
    $LOCATION_DATA = $(jq -r ".cities[] | select(.code==\"$LOCATION_CODE\")" "$UHOME_PATH/uTemplate/datasets/cityMap.json")
    $CITY_NAME = $(echo "$LOCATION_DATA" | jq -r '.name // empty')
    $COUNTRY_CODE = $(echo "$LOCATION_DATA" | jq -r '.country // empty')
    $COORDINATES = $(echo "$LOCATION_DATA" | jq -r '.coordinates // empty')
fi

# Timezone validation and setting
if [[ -z "$TIMEZONE" ]]; then
    $TIMEZONE = $SYSTEM_TIMEZONE
fi
[/PROCESS_VARIABLES]

---

## 📄 Output Templates

[OUTPUT_USER_IDENTITY]
# uDOS User Identity - Generated from Template

**Username**: $USERNAME
**User ID**: $USER_ID
**Created**: $SETUP_DATE
**Version**: v1.0.0
**Architecture**: Single-User Installation

## Profile Information
- **Role**: $DEFAULT_ROLE
- **Setup**: Complete
$( [[ -n "$FULL_NAME" ]] && echo "- **Full Name**: $FULL_NAME" )
$( [[ -n "$EMAIL" ]] && echo "- **Email**: $EMAIL" )

## Location & Time
$( [[ -n "$CITY_NAME" ]] && echo "- **Location**: $CITY_NAME ($LOCATION_CODE)" )
$( [[ -n "$COUNTRY_CODE" ]] && echo "- **Country**: $COUNTRY_CODE" )
- **Timezone**: $TIMEZONE
$( [[ -n "$COORDINATES" ]] && echo "- **Coordinates**: $COORDINATES" )

## System Preferences
- **Theme**: $THEME
- **Debug Mode**: $DEBUG_MODE
- **Auto Backup**: $AUTO_BACKUP
- **AI Companion**: $AI_COMPANION_ENABLED
- **Auto Install Packages**: $AUTO_INSTALL_PACKAGES
- **VS Code Extension**: $VSCODE_EXTENSION

## System Paths
- **uDOS Home**: $UHOME_PATH
- **User Memory**: $UMEMORY_PATH
- **Setup Timestamp**: $SETUP_TIMESTAMP

---

*Identity generated by uDOS Template System v2.0*
[/OUTPUT_USER_IDENTITY]

[OUTPUT_CONFIG_VARS]
# uDOS System Configuration Variables
# Generated: $SETUP_DATE

# User Identity
export UDOS_USERNAME="$USERNAME"
export UDOS_USER_ID="$USER_ID"
export UDOS_FULL_NAME="$FULL_NAME"
export UDOS_EMAIL="$EMAIL"

# Location & Time
export UDOS_LOCATION_CODE="$LOCATION_CODE"
export UDOS_CITY_NAME="$CITY_NAME"
export UDOS_COUNTRY_CODE="$COUNTRY_CODE"
export UDOS_TIMEZONE="$TIMEZONE"
export UDOS_COORDINATES="$COORDINATES"

# System Preferences
export UDOS_THEME="$THEME"
export UDOS_DEBUG_MODE="$DEBUG_MODE"
export UDOS_AUTO_BACKUP="$AUTO_BACKUP"
export UDOS_AI_COMPANION="$AI_COMPANION_ENABLED"
export UDOS_AUTO_PACKAGES="$AUTO_INSTALL_PACKAGES"
export UDOS_VSCODE_EXTENSION="$VSCODE_EXTENSION"
export UDOS_DEFAULT_ROLE="$DEFAULT_ROLE"

# System Paths
export UDOS_HOME="$UHOME_PATH"
export UDOS_MEMORY="$UMEMORY_PATH"
export UDOS_SETUP_TIMESTAMP="$SETUP_TIMESTAMP"
[/OUTPUT_CONFIG_VARS]

[OUTPUT_FIRST_MISSION]
# 🎯 Welcome to uDOS v1.0!

**Mission**: First Steps with uDOS  
**User**: $USERNAME ($USER_ID)  
**Created**: $SETUP_DATE  
**Location**: $( [[ -n "$CITY_NAME" ]] && echo "$CITY_NAME" || echo "Unknown" )

## Mission Objective
Get familiar with your new uDOS development environment and complete initial setup validation.

## Tasks
- [ ] **Verify Installation**: Run `ucode CHECK all` to validate system
- [ ] **Explore Commands**: Try `ucode HELP` to see available commands
- [ ] **Test Dashboard**: Run `ucode DASH live` for real-time monitoring
$( [[ "$AI_COMPANION_ENABLED" == "true" ]] && echo "- [ ] **Meet Chester**: Start AI companion with \`ucode CHESTER start\`" )
$( [[ "$VSCODE_EXTENSION" == "true" ]] && echo "- [ ] **VS Code Setup**: Open project in VS Code and explore tasks" )
- [ ] **Create Project**: Use `ucode STRUCTURE build` to create first project
- [ ] **Template Test**: Try `ucode TEMPLATE process` to test template system

## Resources
- **User Manual**: `docs/user-manual.md`
- **Command Reference**: `docs/command-reference.md`
- **Feature Guide**: `docs/feature-guide.md`

## User Configuration
- **Default Role**: $DEFAULT_ROLE
- **Theme**: $THEME
- **Debug Mode**: $( [[ "$DEBUG_MODE" == "true" ]] && echo "Enabled" || echo "Disabled" )

---

*Welcome to the uDOS ecosystem! Your journey begins now.*
[/OUTPUT_FIRST_MISSION]

---

## 🔧 Template Processing Instructions

This template uses the uDOS standard format:
- **[SHORTCODE]** blocks define interactive elements
- **$VARIABLES** store and process data
- **Conditional blocks** use `$( [[ condition ]] && echo "content" )`
- **Dataset integration** via `jq` queries to JSON datasets

### Processing Flow
1. **Input Collection**: Process each [INPUT_*] block interactively
2. **Variable Processing**: Execute [PROCESS_VARIABLES] block
3. **Output Generation**: Render [OUTPUT_*] blocks with variable substitution
4. **File Creation**: Save outputs to appropriate uMemory locations

### Integration Points
- **uCode**: Variables passed to shell environment
- **uScript**: Configuration accessible via environment variables
- **Templates**: User variables available for future template processing
- **Datasets**: Location data automatically integrated from cityMap.json
