{#extend base/role-header.md}

# 🧙‍♂️ uDOS Command Help - {USER-ROLE:title} Level {USER-LEVEL}

*System Status: {SYSTEM-STATUS:title} | Last Updated: {TIMESTAMP}*

## 🎯 Available Commands for {USER-ROLE:title}

### � Native CLI Commands (Simplified)
Use these natural commands without brackets:
- **status** - Display system dashboard  
- **role** - Show current role information
- **help** - Show this help reference
- **list** - List all system variables
- **heal** - Run self-healing system check
- **assist enter** - Activate ASSIST mode
- **template list** - Show available templates
- **template render [name]** - Render specific template

### 📋 Core Commands (Traditional uCODE syntax)
- **[STATUS]** - Display system status and current configuration
- **[HELP]** - Show available commands (you are here!)  
- **[HELP|COMPLETE]** - Show complete command reference
- **[LIST]** - List all system variables organized by scope
- **[ROLE]** - Display current role information and capabilities

### 🔧 Variable Management
- **[GET|variable]** - Get variable value with details
- **[SET|variable*value]** - Set variable value with confirmation  
- **[LIST]** - Show all available variables by scope

{#if USER-LEVEL:number >= 20}
### 📖 Story System (Level 20+)
- **[STORY|LIST]** - List available interactive stories
- **[STORY|RUN*name]** - Execute interactive configuration stories
{/if}

{#if USER-LEVEL:number >= 40}
### ⚡ Automation Commands (Level 40+)
- **[WORKFLOW]** - Manage workflows and tasks
- **[SCRIPT]** - Execute automation scripts
- **[ASSIST|ENTER]** - Enter development ASSIST mode
- **[ASSIST|EXIT]** - Exit ASSIST mode
{/if}

{#if USER-LEVEL:number >= 60}
### 🎨 Template System (Level 60+)
- **[TEMPLATE|LIST]** - List available templates
- **[TEMPLATE|RENDER*name]** - Render template with current variables
- **[VARIABLE|EXPORT]** - Export variables to environment
{/if}

{#if USER-LEVEL:number >= 80}
### 🛠️ Advanced Commands (Level 80+)
- **[SYSTEM|STATUS]** - Detailed system diagnostics
- **[SYSTEM|HEAL]** - Run self-healing dependency check
- **[EXTENSION]** - Manage system extensions
- **[DEV|MODE]** - Enter development mode
{/if}

{#if USER-LEVEL:number >= 100}
### 🧙‍♂️ Wizard Commands (Level 100)
- **[DEV|BUILD]** - Build and deploy system components
- **[BACKUP|CREATE]** - Create system backups
- **[RESTORE|FROM*backup]** - Restore from backup
- **[ROLE|FORCE*role]** - Force role change (administrative)
{/if}

{#if USER-LEVEL:number >= 100}
### Wizard Commands (Level 100)
- **[DEV]** - Development mode toggle
- **[ASSIST]** - AI development assistance
- **[BUILD]** - System build operations
{/if}

## Usage Examples

### Variable Management
```
[VARIABLE|GET*USER-ROLE]
[VARIABLE|SET*PROJECT-NAME*MyProject]
[LIST]
```

{#if DEV-MODE}
### Development Mode Active
```
[DEV|STATUS]
[ASSIST|ENTER]
[BUILD|TEST]
```
{/if}

## Current Configuration
- **Role**: {USER-ROLE} (Level {USER-LEVEL:number})
- **Display Mode**: {DISPLAY-MODE}
- **Project**: {PROJECT-NAME|No Project Set}
- **Development Mode**: {DEV-MODE|Disabled}

{#if DETAIL-LEVEL == "verbose"}
## System Information
- **Session ID**: {SESSION-ID}
- **Workspace**: {WORKSPACE-PATH|Not Set}
- **Location**: {LOCATION-CODE|GLOBAL}
- **Timezone**: {TIMEZONE|UTC}
{/if}

---
*Type **[HELP|command]** for specific command help*
*Use **[STATUS]** to see current system state*
