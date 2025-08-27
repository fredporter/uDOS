{#extend base/role-header.md}

# Interactive Variable Collection Form

## Project Setup Variables

### Required Information
Please provide the following information for your project setup:

**Project Name**
Enter a name for your project:
`[INPUT] PROJECT-NAME: {PROJECT-NAME|}`

**Project Type**
Select project type (development, personal, business, research):
`[SELECT] PROJECT-TYPE: {PROJECT-TYPE|development}`

**Workspace Location**
Enter the full path to your workspace:
`[INPUT] WORKSPACE-PATH: {WORKSPACE-PATH|}`

{#if USER-LEVEL:number >= 60}
### Development Options

**Development Mode**
Enable development features (true/false):
`[BOOLEAN] DEV-MODE: {DEV-MODE|false}`

**Debug Level**
Set debug verbosity (minimal, standard, verbose, debug):
`[SELECT] DEBUG-LEVEL: {DEBUG-LEVEL|standard}`
{/if}

### Display Preferences

**UI Theme**
Choose interface theme (polaroid, retro, tropical, pastel):
`[SELECT] UI-THEME: {UI-THEME|polaroid}`

**Grid Size**
Set grid display size (compact, standard, large):
`[SELECT] GRID-SIZE: {GRID-SIZE|standard}`

{#if LOCATION-ENABLED}
### Geographic Settings

**Location Code**
Enter your location code:
`[INPUT] LOCATION-CODE: {LOCATION-CODE|GLOBAL}`

**Timezone**
Set your timezone:
`[INPUT] TIMEZONE: {TIMEZONE|UTC}`
{/if}

## Form Actions

- **[SAVE]** - Save all variables
- **[VALIDATE]** - Check required fields
- **[RESET]** - Reset to defaults
- **[CANCEL]** - Cancel without saving

---
**Instructions**: Fill in the fields above and use [SAVE] to apply changes.
**Required fields**: PROJECT-NAME, PROJECT-TYPE, WORKSPACE-PATH
**Current Role**: {USER-ROLE} (Level {USER-LEVEL:number})
