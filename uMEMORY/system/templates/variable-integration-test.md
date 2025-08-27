# uDOS Variable System Integration Test
# Template demonstrating variable substitution and sharing

## System Information
- **User Role**: {USER-ROLE}
- **User Level**: {USER-LEVEL}
- **Display Mode**: {DISPLAY-MODE}
- **Detail Level**: {DETAIL-LEVEL}

## Project Context
- **Project Name**: {PROJECT-NAME|No Project Set}
- **Project Type**: {PROJECT-TYPE}
- **Workspace Path**: {WORKSPACE-PATH|Not Set}

## Geographic Context
- **Tile Code**: {TILE-CODE}
- **Location Code**: {LOCATION-CODE|GLOBAL}
- **Timezone**: {TIMEZONE|UTC}

## Development Context
{#if DEV-MODE}
### Development Mode Active
- **Debug Level**: {DEBUG-LEVEL}
- **Script Environment**: {SCRIPT-ENV}
{/if}

## Display Configuration
- **Theme**: {UI-THEME}
- **Max Resolution**: {MAX-RESOLUTION}
- **Grid Size**: {GRID-SIZE}

## System Configuration
- **Data Source**: {DATA-SOURCE}
- **Backup Enabled**: {BACKUP-ENABLED}
- **Log Retention**: {LOG-RETENTION} days

---

*This template demonstrates how uDOS system variables are shared across:*
- ✅ **Commands/Functions**: Via variable-manager.sh
- ✅ **uSCRIPTs**: Via udos_variables Python library
- ✅ **Templates**: Via {VARIABLE} substitution syntax
- ✅ **Environment**: Auto-exported with UDOS_ prefix

*All variables are centrally managed in `uMEMORY/system/variables/`*
