{#extend base/role-header.md}

# uDOS System Dashboard

## Quick Status

### User Information
| Field | Value |
|-------|-------|
| **Role** | {USER-ROLE} |
| **Level** | {USER-LEVEL:number} |
| **Display Mode** | {DISPLAY-MODE} |
| **Session** | {SESSION-ID} |

### Project Context
| Field | Value |
|-------|-------|
| **Project Name** | {PROJECT-NAME|No Project Set} |
| **Project Type** | {PROJECT-TYPE|Not Specified} |
| **Workspace** | {WORKSPACE-PATH|Not Set} |

{#if DEV-MODE}
### Development Environment
| Field | Value |
|-------|-------|
| **Development Mode** | **ACTIVE** |
| **Debug Level** | {DEBUG-LEVEL} |
| **Script Environment** | {SCRIPT-ENV} |
{/if}

### System Configuration
| Field | Value |
|-------|-------|
| **Theme** | {UI-THEME|Default} |
| **Max Resolution** | {MAX-RESOLUTION|Auto} |
| **Grid Size** | {GRID-SIZE|Standard} |
| **Color Palette** | {COLOR-PALETTE|Polaroid} |

### Geographic Context
| Field | Value |
|-------|-------|
| **Location** | {LOCATION-CODE|GLOBAL} |
| **Tile Code** | {TILE-CODE|Not Set} |
| **Timezone** | {TIMEZONE|UTC} |

{#if USER-LEVEL:number >= 60}
## Available Actions

### Variable Management
- [VARIABLE|GET*name] - Get variable value
- [VARIABLE|SET*name*value] - Set variable value
- [LIST] - Show all variables

### Story System
- [STORY|LIST] - List available stories
- [STORY|RUN*name] - Execute interactive story
{/if}

{#if USER-LEVEL:number >= 80}
### System Administration
- [SYSTEM|STATUS] - Detailed system status
- [EXTENSION|LIST] - Show installed extensions
- [WORKFLOW|STATUS] - Check workflow status
{/if}

{#if USER-LEVEL:number >= 100}
### Development Tools
- [DEV|TOGGLE] - Toggle development mode
- [ASSIST|ENTER] - Enter AI assistance mode
- [BUILD|STATUS] - Check build system
{/if}

## Recent Activity
*Session started: {SESSION-START-TIME|Unknown}*
*Last command: {LAST-COMMAND|None}*

---
**Status**: [SUCCESS] Dashboard generated successfully
**Generated**: {CURRENT-TIME|Now} | **Mode**: {DISPLAY-MODE}
