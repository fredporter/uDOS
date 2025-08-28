# uGET User Setup

**Type**: Interactive Form
**Version**: v1.0.4.1
**Purpose**: Complete user setup and system configuration
**Generated**: [timestamp]
**Integration**: uCORE GET/POST commands

> **Template ID**: user-setup
> **Output Format**: User profile, system configuration, sandbox identity
> **Auto-Run**: When sandbox/user.md is missing

---

## 🎭 Welcome to uDOS v1.0.4.1

[setup:intro]
Welcome to uDOS v1.0.4.1! This setup wizard will configure your development environment, create your user profile, and establish system preferences.

Your identity (username/password) will be stored in sandbox/, while your profile and preferences are stored in uMEMORY/.
[/setup:intro]

---

## 👤 User Identity

[get:username]
question: Enter your username
type: text
required: true
validation: alphanumeric,min:3,max:20
default: [system:user]
help: Unique identifier for this uDOS installation
[/get:username]

[get:display_name]
question: Your full name or display name
type: text
required: true
default: [get:username]
help: Name shown in templates and generated documents
[/get:display_name]

[get:email]
question: Email address (optional)
type: email
required: false
default: ""
help: Used for notifications and template generation
[/get:email]

---

## 🌍 Location & Time

[get:timezone]
question: Select your timezone
type: timezone_lookup
required: true
default: [system:timezone]
help: Used for timestamps and location-aware features
[/get:timezone]

[get:location]
question: Your primary location
type: location_lookup
required: true
default: [timezone:city]
help: City or region for file naming and geographic features
[/get:location]

---

## 🎯 Role & Development

[get:role]
question: Choose your default role
type: choice
options: ["Ghost", "Tomb", "Crypt", "Drone", "Knight", "Imp", "Sorcerer", "Wizard"]
required: true
default: "Wizard"
help: Ghost=demo, Tomb=basic, Crypt=secure, Drone=auto, Knight=ops, Imp=dev, Sorcerer=admin, Wizard=full
[/get:role]

[get:development_mode]
question: Enable development features?
type: boolean
required: true
default: true
help: Enables advanced features, debugging, and development tools
[/get:development_mode]

---

## ⚙️ System Preferences

[get:theme]
question: Choose interface theme
type: choice
options: ["Polaroid", "Retro-Unicorn", "Nostalgia", "Tropical-Sunrise", "Pastel-Power", "Arcade-Pastels", "Grayscale", "Solar-Punk"]
required: true
default: "Polaroid"
help: Terminal color palette (8 complete schemes available)
[/get:theme]

[get:auto_backup]
question: Enable automatic backup?
type: boolean
required: true
default: true
help: Automatically backs up uMEMORY data during operations
[/get:auto_backup]

[get:logging_level]
question: Choose logging level
type: choice
options: ["INFO", "DEBUG", "WARNING", "ERROR"]
required: true
default: "INFO"
help: Controls detail level of system logging
[/get:logging_level]

---

## 📦 Optional Features

[get:install_packages]
question: Install recommended packages?
type: boolean
required: true
default: true
help: Installs ripgrep, fd, bat, jq, fzf for enhanced functionality
[/get:install_packages]

[get:vscode_integration]
question: Setup VS Code integration?
type: boolean
required: true
default: true
help: Configures VS Code workspace and tasks
[/get:vscode_integration]

[get:git_integration]
question: Setup Git integration?
type: boolean
required: true
default: true
help: Configures Git for version control
[/get:git_integration]

---

## 🔄 Processing & Output

[process:setup_data]
setup_timestamp = [timestamp]
setup_date = [date:iso]
user_id = [get:username] | lowercase | alphanumeric
grid_code = [get:location] | lookup:grid_code
timezone_offset = [get:timezone] | lookup:offset
uhex_location = [get:location] | lookup:uhex
created_timestamp = [date:iso]
[/process:setup_data]

[output:sandbox_user]
file: sandbox/user.md
content: |
# User Profile

name: [get:display_name]
username: [get:username]
email: [get:email]
role: [get:role]
location: [get:location]
timezone: [get:timezone]
theme: [get:theme]
created: [process:setup_date]
last_login: [process:setup_date]
user_id: [process:user_id]
development_mode: [get:development_mode]
auto_backup: [get:auto_backup]
logging_level: [get:logging_level]
[/output:sandbox_user]

[output:user_profile]
file: uMEMORY/user/profile-[process:user_id].md
content: |
# uDOS User Profile

**Name**: [get:display_name]
**Username**: [get:username]
**User ID**: [process:user_id]
**Created**: [process:setup_date]
**Version**: v1.0.4.1

## Identity & Contact
- **Display Name**: [get:display_name]
- **Email**: [get:email]
- **Location**: [get:location]
- **Timezone**: [get:timezone]

## System Configuration
- **Default Role**: [get:role]
- **Theme**: [get:theme]
- **Development Mode**: [get:development_mode]
- **Auto Backup**: [get:auto_backup]
- **Logging Level**: [get:logging_level]

## Features Enabled
- **Package Installation**: [get:install_packages]
- **VS Code Integration**: [get:vscode_integration]
- **Git Integration**: [get:git_integration]

## File Organization
- **User ID**: [process:user_id]
- **Grid Code**: [process:grid_code]
- **Timezone Offset**: [process:timezone_offset]
- **uHEX Location**: [process:uhex_location]

---

*Profile generated by uDOS v1.0.4.1 setup system*
[/output:user_profile]

[output:system_environment]
file: uMEMORY/system/environment-[process:user_id].sh
content: |
#!/bin/bash
# uDOS System Environment Variables
# Generated: [process:setup_date]
# User: [get:username] ([process:user_id])

# User Identity
export UDOS_USERNAME="[get:username]"
export UDOS_USER_ID="[process:user_id]"
export UDOS_DISPLAY_NAME="[get:display_name]"
export UDOS_EMAIL="[get:email]"

# Location & Time
export UDOS_LOCATION="[get:location]"
export UDOS_TIMEZONE="[get:timezone]"
export UDOS_GRID_CODE="[process:grid_code]"
export UDOS_UHEX_LOCATION="[process:uhex_location]"
export UDOS_TIMEZONE_OFFSET="[process:timezone_offset]"

# System Configuration
export UDOS_ROLE="[get:role]"
export UDOS_THEME="[get:theme]"
export UDOS_DEVELOPMENT_MODE="[get:development_mode]"
export UDOS_AUTO_BACKUP="[get:auto_backup]"
export UDOS_LOGGING_LEVEL="[get:logging_level]"

# Feature Flags
export UDOS_INSTALL_PACKAGES="[get:install_packages]"
export UDOS_VSCODE_INTEGRATION="[get:vscode_integration]"
export UDOS_GIT_INTEGRATION="[get:git_integration]"

# System Metadata
export UDOS_VERSION="v1.0.4.1"
export UDOS_SETUP_TIMESTAMP="[process:setup_timestamp]"
export UDOS_CREATED="[process:setup_date]"

# Path Configuration
export UDOS_HOME="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export UDOS_MEMORY="$UDOS_HOME/uMEMORY"
export UDOS_SANDBOX="$UDOS_HOME/sandbox"
export UDOS_CORE="$UDOS_HOME/uCORE"
[/output:system_environment]

[output:welcome_mission]
file: uMEMORY/user/missions/welcome-[process:user_id].md
content: |
# 🎯 Welcome to uDOS v1.0.4.1

**Mission**: Get started with uDOS
**User**: [get:display_name] ([get:username])
**Role**: [get:role]
**Created**: [process:setup_date]
**Location**: [get:location]

## Mission Objectives
Complete your uDOS setup and learn the essential commands.

## Getting Started Tasks
- [ ] **Test System**: Run `ucode check all` to validate installation
- [ ] **Explore Commands**: Try `ucode help` to see available commands
- [ ] **View Profile**: Run `ucode get user name` to test data retrieval
- [ ] **Create Log Entry**: Use `ucode log write INFO "First login"`
- [ ] **List Templates**: Run `ucode template list` to see available templates
- [ ] **Check Geographic Data**: Try `ucode map stats` to see geographic system

## Advanced Tasks (Role: [get:role])
- [ ] **Generate Tree**: Run `ucode tree` to see system structure
- [ ] **Create Backup**: Use `ucode backup create initial`
- [ ] **Process Template**: Try `ucode template process` with a template
- [ ] **Test Geographic Search**: Use `ucode map find [get:location]`

## Your Configuration
- **Role**: [get:role] (Access Level: [get:role])
- **Theme**: [get:theme] color palette
- **Development Mode**: [get:development_mode]
- **Location**: [get:location] ([get:timezone])

## Resources
- **Documentation**: `/docs/` folder
- **Templates**: `ucode template list`
- **Help System**: `ucode help <command>`
- **System Status**: `ucode check all`

Welcome to the uDOS ecosystem! Your foundational development environment is ready.

---

*Mission generated by uDOS v1.0.4.1 setup system*
[/output:welcome_mission]

---

## 🚀 Post-Setup Actions

[post:setup_actions]
1. Source environment variables
2. Create user directories in uMEMORY
3. Initialize role-specific configurations
4. Install packages (if enabled)
5. Setup VS Code workspace (if enabled)
6. Configure Git (if enabled)
7. Create initial backup
8. Generate system logs
9. Display setup summary
[/post:setup_actions]

---

*uDOS v1.0.4.1 Complete User Setup System*
