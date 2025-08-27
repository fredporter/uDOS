# {USER-ROLE:title} Interface
**Level {USER-LEVEL:number}** | **{DISPLAY-MODE}** Mode | Session: {SESSION-ID}

---

# uDOS Command Help

## Available Commands for {USER-ROLE:title}

### Core Commands
- **[STATUS]** - Display system status and current configuration
- **[HELP]** - Show available commands (you are here!)
- **[LIST]** - List all system variables
- **[ROLE]** - Display current role information

{#if USER-LEVEL:number >= 40}
### Automation Commands (Level 40+)
- **[WORKFLOW]** - Manage workflows and tasks
- **[SCRIPT]** - Execute automation scripts
{/if}

{#if USER-LEVEL:number >= 60}
### Development Commands (Level 60+)
- **[VARIABLE|GET*name]** - Get variable value
- **[VARIABLE|SET*name*value]** - Set variable value
- **[STORY|LIST]** - List available interactive stories
{/if}

{#if USER-LEVEL:number >= 80}
### Advanced Commands (Level 80+)
- **[SYSTEM]** - System administration commands
- **[EXTENSION]** - Manage system extensions
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
