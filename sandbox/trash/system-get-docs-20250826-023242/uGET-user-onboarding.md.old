# uGET User Onboarding

**Type**: Interactive Form
**Version**: v1.3.3
**Purpose**: Initial user setup and system configuration
**Generated**: [timestamp]
**Location**: uMEMORY/system/get/

> **Category**: System Setup
> **Output**: User profile, system configuration
> **Integration**: uMEMORY/user/, sandbox/identity/

---

## 🎭 Welcome to uDOS v1.3.3

[setup:intro]
Welcome to uDOS v1.3.3! This setup wizard will configure your personal development environment, create your user profile, and establish system preferences.

All configuration data will be stored in uMEMORY with your identity kept secure in the sandbox.
[/setup:intro]

---

## 👤 User Identity

[get:username]
question: Enter your username
type: text
required: true
validation: alphanumeric,min:3,max:20
default: [system:user]
help: Unique identifier stored in sandbox identity file
[/get:username]

[get:user_password]
question: Enter password (optional)
type: password
required: false
validation: min:8
default: ""
help: Optional password for local authentication - stored in sandbox only
[/get:user_password]

[get:display_name]
question: Your display name
type: text
required: true
default: [get:username]
help: Name shown in uDOS interface and generated documents
[/get:display_name]

---

## 🌍 Location & Time

[get:user_timezone]
question: Select your timezone
type: timezone_lookup
dataset: get:timezones
required: true
default: [system:timezone]
help: Used for timestamps and location-aware features
[/get:user_timezone]

[get:user_location]
question: Select your location
type: location_lookup
dataset: get:cities
dependent: [get:user_timezone]
required: true
help: Primary location for file naming and regional features
[/get:user_location]

---

## ⚙️ System Preferences

[get:user_theme]
question: Choose interface theme
type: choice
options: ["default", "dark", "light", "auto"]
required: true
default: "default"
help: Controls terminal colors and VS Code integration
[/get:user_theme]

[get:debug_mode]
question: Enable debug mode?
type: boolean
required: true
default: false
help: Shows detailed system information and error traces
[/get:debug_mode]

[get:auto_backup]
question: Enable automatic backup?
type: boolean
required: true
default: true
help: Automatically backs up uMEMORY data during operations
[/get:auto_backup]

[get:chester_enabled]
question: Enable Chester AI companion?
type: boolean
required: true
default: true
help: Chester provides intelligent assistance and development support
[/get:chester_enabled]

---

## 🎯 Development Configuration

[get:default_role]
question: Choose your default user role
type: choice
options: ["wizard", "sorcerer", "ghost", "drone", "imp"]
required: true
default: "wizard"
help: wizard=full access, sorcerer=advanced dev, ghost=standard, drone=limited, imp=basic
[/get:default_role]

[get:auto_packages]
question: Auto-install recommended packages?
type: boolean
required: true
default: true
help: Installs ripgrep, fd, bat, glow, fzf, jq automatically
[/get:auto_packages]

[get:vscode_extension]
question: Install uDOS VS Code extension?
type: boolean
required: true
default: true
help: Provides syntax highlighting, tasks, and IDE integration
[/get:vscode_extension]

[get:dashboard_updates]
question: Enable dashboard auto-refresh?
type: boolean
required: true
default: true
help: Automatically refreshes system dashboard data
[/get:dashboard_updates]

---

## � Processing & Configuration

[process:variables]
setup_timestamp = [timestamp]
setup_date = [date:iso]
user_id = [get:username] | lowercase | alphanumeric_only
grid_code = [get:user_location] | lookup:grid_code
timezone_code = [get:user_timezone] | lookup:tz_code
uhome_path = [system:home]/uDOS
umemory_path = [uhome_path]/uMEMORY
[/process:variables]

[output:user_identity]
file: sandbox/identity/user_auth.md
content: |
# uDOS User Identity

**Username**: [get:username]
**User ID**: [process:user_id]
**Password**: [conditional:get:user_password != ""][PROTECTED][/conditional][conditional:get:user_password == ""][NONE][/conditional]
**Created**: [process:setup_date]
**Installation Type**: Single-User Bound
**Authentication**: Local Only

---

*Sandbox identity file - contains only username and password for local authentication*
[/output:user_identity]

[output:user_profile]
file: uMEMORY/user/profile.md
content: |
# User Profile: [get:display_name]

**Display Name**: [get:display_name]
**User ID**: [process:user_id]
**Created**: [process:setup_date]
**Version**: v1.3.3

## Location & Time
- **Location**: [get:user_location]
- **Timezone**: [get:user_timezone]
- **Grid Code**: [process:grid_code]
- **TZ Code**: [process:timezone_code]

## System Preferences
- **Theme**: [get:user_theme]
- **Debug Mode**: [get:debug_mode]
- **Auto Backup**: [get:auto_backup]
- **Chester AI**: [get:chester_enabled]
- **Dashboard Updates**: [get:dashboard_updates]

## Development Configuration
- **Default Role**: [get:default_role]
- **Auto Install Packages**: [get:auto_packages]
- **VS Code Extension**: [get:vscode_extension]

## System Paths
- **uDOS Home**: [process:uhome_path]
- **User Memory**: [process:umemory_path]

---

*User profile generated by uDOS v1.3.3 onboarding system*
[/output:user_profile]

[output:system_config]
file: uMEMORY/config/system-environment.sh
content: |
#!/bin/bash
# uDOS System Configuration Variables
# Generated: [process:setup_date]

# User Identity
export UDOS_USERNAME="[get:username]"
export UDOS_USER_ID="[process:user_id]"
export UDOS_DISPLAY_NAME="[get:display_name]"

# Location & Time
export UDOS_LOCATION="[get:user_location]"
export UDOS_TIMEZONE="[get:user_timezone]"
export UDOS_GRID_CODE="[process:grid_code]"
export UDOS_TZ_CODE="[process:timezone_code]"

# System Preferences
export UDOS_THEME="[get:user_theme]"
export UDOS_DEBUG_MODE="[get:debug_mode]"
export UDOS_AUTO_BACKUP="[get:auto_backup]"
export UDOS_CHESTER_ENABLED="[get:chester_enabled]"
export UDOS_DASHBOARD_UPDATES="[get:dashboard_updates]"

# Development Configuration
export UDOS_DEFAULT_ROLE="[get:default_role]"
export UDOS_AUTO_PACKAGES="[get:auto_packages]"
export UDOS_VSCODE_EXTENSION="[get:vscode_extension]"

# System Paths
export UDOS_HOME="[process:uhome_path]"
export UDOS_MEMORY="[process:umemory_path]"
export UDOS_SETUP_TIMESTAMP="[process:setup_timestamp]"

# System Configuration
export UDOS_VERSION="v1.3.3"
export UDOS_INSTALLATION_TYPE="single_user_bound"
export UDOS_FILE_NAMING="timestamp_location_function"
[/output:system_config]

[output:welcome_mission]
file: uMEMORY/missions/[process:setup_timestamp]-welcome-mission.md
template: uDOT-mission-brief.md
variables:
  mission_name: "Welcome to uDOS v1.3.3"
  mission_description: "Get familiar with your new uDOS development environment"
  mission_priority: "high"
  mission_status: "active"
[/output:welcome_mission]

---

## 🎯 Next Steps

[post:actions]
1. Validate system installation
2. Initialize user directories
3. Install optional packages (if enabled)
4. Configure VS Code extension (if enabled)
5. Start Chester AI companion (if enabled)
6. Generate welcome mission
7. Display setup summary
[/post:actions]

---

*uDOS v1.3.3 User Onboarding - Interactive Setup System*

### 👤 Identity Information

[INPUT_USERNAME]
Question: Enter your username (required)
Variable: $USERNAME
Validation: required,alphanumeric
Default: $USER
Help: Stored in sandbox identity file with password for single-user installation
[/INPUT_USERNAME]

[INPUT_PASSWORD]
Question: Enter your password (blank for none)
Variable: $PASSWORD
Validation: optional,text
Default:
Help: Stored with username in sandbox identity file only
[/INPUT_PASSWORD]

### 🌍 Location

[INPUT_TIMEZONE]
Question: Confirm time
Select your timezone dataset (check current time / select from dataset)
Variable: $TIMEZONE
Validation: required,timezone, can't be blank
Default: $SYSTEM_TIMEZONE
Help: Auto-detected from system first
[/INPUT_TIMEZONE]


### 🌍 Location - pull from dataset based on Timezone

[INPUT_LOCATION]
Question: Enter your location
Variable: $LOCATION
Validation: required,alpha
Default: Dataset timezone city name
Help: Used for timezone and location-aware features, can be overwritten, can't be blank
[/INPUT_LOCATION]



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

[INPUT_OK_COMPANION]
Question: Enable Chester OK companion?
Variable: $OK_COMPANION_ENABLED
Validation: required,boolean
Options: true,false
Default: true
Help: Chester provides intelligent assistance and development support
[/INPUT_OK_COMPANION]

### 🎯 Development Preferences

[INPUT_DEFAULT_ROLE]
Question: Choose your default user role
Variable: $DEFAULT_ROLE
Validation: required,options
Options: wizard,sorcerer,ghost,drone,imp
Default: wizard
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
    $LOCATION_DATA = $(jq -r ".[] | select(.code==\"$LOCATION_CODE\")" "$UHOME_PATH/uTemplate/datasets/cityMap.json")
    $CITY_NAME = $(echo "$LOCATION_DATA" | jq -r '.CITY // empty')
    $COUNTRY_CODE = $(echo "$LOCATION_DATA" | jq -r '.COUNTRY // empty')
    $COORDINATES = $(echo "$LOCATION_DATA" | jq -r '.LAT, .LON | tostring' | paste -sd ',' -)
    $GRID_CODE = $(echo "$LOCATION_DATA" | jq -r '.TILE // empty')
fi

# Timezone to grid code and timezone code lookup for file naming
if [[ -n "$TIMEZONE" ]]; then
    $TIMEZONE_MATCH_DATA = $(jq -r ".[] | select(.TIMEZONE==\"$TIMEZONE\" or .TIMEZONE | test(\"$TIMEZONE\"; \"i\"))" "$UHOME_PATH/uTemplate/datasets/cityMap.json" | head -1)
    if [[ -n "$TIMEZONE_MATCH_DATA" && "$TIMEZONE_MATCH_DATA" != "null" ]]; then
        $GRID_CODE = $(echo "$TIMEZONE_MATCH_DATA" | jq -r '.TILE // empty')
        $TZ_CODE = $(echo "$TIMEZONE_MATCH_DATA" | jq -r '.TIMEZONE // empty')
    fi
fi

# Default values if none found
if [[ -z "$GRID_CODE" ]]; then
    $GRID_CODE = "XX00"
fi

if [[ -z "$TZ_CODE" ]]; then
    $TZ_CODE = "UNK"
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

## Location & Time
$( [[ -n "$CITY_NAME" ]] && echo "- **Location**: $CITY_NAME ($LOCATION_CODE)" )
$( [[ -n "$COUNTRY_CODE" ]] && echo "- **Country**: $COUNTRY_CODE" )
- **Timezone**: $TIMEZONE
$( [[ -n "$COORDINATES" ]] && echo "- **Coordinates**: $COORDINATES" )

## System Preferences
- **Theme**: $THEME
- **Debug Mode**: $DEBUG_MODE
- **Auto Backup**: $AUTO_BACKUP
- **OK Companion**: $OK_COMPANION_ENABLED
- **Auto Install Packages**: $AUTO_INSTALL_PACKAGES
- **VS Code Extension**: $VSCODE_EXTENSION

## System Paths
- **uDOS Home**: $UHOME_PATH
- **User Memory**: $UMEMORY_PATH
- **Setup Timestamp**: $SETUP_TIMESTAMP

## File Structure
- **Identity**: Sandbox only (username + password)
- **Data Files**: Timestamp/location based naming
- **Organization**: Flat, chronological/spatial structure
- **Installation**: Single-user bound

---

*Identity generated by uDOS Template System v2.0*
[/OUTPUT_USER_IDENTITY]

[OUTPUT_CONFIG_VARS]
# uDOS System Configuration Variables
# Generated: $SETUP_DATE

# User Identity (username and password stored in sandbox only)
export UDOS_USERNAME="$USERNAME"
export UDOS_USER_ID="$USER_ID"

# Location & Time (file naming basis)
export UDOS_LOCATION_CODE="$LOCATION_CODE"
export UDOS_CITY_NAME="$CITY_NAME"
export UDOS_COUNTRY_CODE="$COUNTRY_CODE"
export UDOS_TIMEZONE="$TIMEZONE"
export UDOS_COORDINATES="$COORDINATES"
export UDOS_GRID_CODE="$GRID_CODE"
export UDOS_TZ_CODE="$TZ_CODE"

# System Preferences
export UDOS_THEME="$THEME"
export UDOS_DEBUG_MODE="$DEBUG_MODE"
export UDOS_AUTO_BACKUP="$AUTO_BACKUP"
export UDOS_OK_COMPANION="$OK_COMPANION_ENABLED"
export UDOS_AUTO_PACKAGES="$AUTO_INSTALL_PACKAGES"
export UDOS_VSCODE_EXTENSION="$VSCODE_EXTENSION"
export UDOS_DEFAULT_ROLE="$DEFAULT_ROLE"

# System Paths
export UDOS_HOME="$UHOME_PATH"
export UDOS_MEMORY="$UMEMORY_PATH"
export UDOS_SETUP_TIMESTAMP="$SETUP_TIMESTAMP"

# File Organization
export UDOS_FILE_NAMING_PATTERN="timestamp-time-seconds-grid-tz"
export UDOS_DATA_STRUCTURE="flat_chronological_spatial"
export UDOS_INSTALLATION_TYPE="single_user_bound"
[/OUTPUT_CONFIG_VARS]

[OUTPUT_SANDBOX_IDENTITY]
# uDOS Sandbox Identity - Username and Password Only
# File: sandbox/identity/user_auth.md
# Generated: $SETUP_DATE

**Username**: $USERNAME
**User ID**: $USER_ID
$( [[ -n "$PASSWORD" ]] && echo "**Password**: [PROTECTED]" || echo "**Password**: [NONE]" )

**Created**: $SETUP_DATE
**Installation Type**: Single-User Bound
**Authentication**: Local Only

---

*Sandbox identity file - contains only username and password for local authentication*
[/OUTPUT_SANDBOX_IDENTITY]

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
$( [[ "$OK_COMPANION_ENABLED" == "true" ]] && echo "- [ ] **Meet Chester**: Start OK companion with \`ucode CHESTER start\`" )
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
4. **File Creation**: Save outputs to appropriate locations

### File Organization Structure
- **Sandbox Identity**: `sandbox/identity/user_auth.md` (username + password only)
- **System Data**: Files named by `timestamp_location_function.ext`
- **Directory Structure**: Flat, chronological and spatial organization
- **Data Separation**: Username kept separate from other user data
- **Installation Binding**: Single-user per installation

### Integration Points
- **uCode**: Variables passed to shell environment
- **uScript**: Configuration accessible via environment variables
- **Templates**: User variables available for future template processing
- **Datasets**: Location data automatically integrated from cityMap.json
- **File Naming**: Timestamp and location-based for all non-identity files

### File Naming Convention Examples
- `20250719-143022-59-AA24-EST-user-preferences.json`
- `20250719-143022-59-AA24-EST-system-config.sh`
- `20250719-143022-59-AA24-EST-first-mission.md`
- `sandbox/identity/user_auth.md` (exception - identity only)
