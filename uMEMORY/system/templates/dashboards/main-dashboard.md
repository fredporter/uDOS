{#extend base/role-header.md}

# 🎛️ uDOS System Dashboard

*Last Updated: {TIMESTAMP} | System Status: {SYSTEM-STATUS:title}*

## 👤 User Profile

```
┌─ User: {USER-ROLE:title} (Level {USER-LEVEL}) ─────────────────┐
│ Display Mode: {DISPLAY-MODE|CLI}                              │
│ Session ID:   {SESSION-ID|new-session}                        │
│ Permissions:  {USER-CAPABILITIES|Standard Access}             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Project Context

```
┌─ Current Project ─────────────────────────────────────────────┐
│ Name:      {PROJECT-NAME|⚠️  No Project Set}                  │
│ Type:      {PROJECT-TYPE|Not Specified}                       │
│ Workspace: {WORKSPACE-PATH|Not Set}                           │
│ Status:    {PROJECT-STATUS|Unknown}                           │
└─────────────────────────────────────────────────────────────┘
```

{#if DEV-MODE:boolean}
## 🧠 Development Environment **ACTIVE**

```
┌─ Development Configuration ───────────────────────────────────┐
│ Debug Level:      {DEBUG-LEVEL|Standard}                      │
│ Script Environment: {SCRIPT-ENV|Production}                   │
│ Self-Healing:     {SELF-HEALING-STATUS|Enabled}               │
│ Template Engine:  {TEMPLATE-ENGINE-STATUS|Loaded}             │
└─────────────────────────────────────────────────────────────┘
```
{/if}

## ⚙️ System Configuration

```
┌─ Interface Settings ──────────────────────────────────────────┐
│ Theme:         {UI-THEME|Default}                              │
│ Resolution:    {MAX-RESOLUTION|Auto-Detect}                   │
│ Grid Size:     {GRID-SIZE|Standard}                           │
│ Color Palette: {COLOR-PALETTE|Polaroid}                       │
│ Font System:   {FONT-SYSTEM|System Default}                   │
└─────────────────────────────────────────────────────────────┘
```

## 🌍 Geographic & Network Context

```
┌─ Location Services ───────────────────────────────────────────┐
│ Location:    {LOCATION-CODE|GLOBAL}                           │
│ Tile Code:   {TILE-CODE|Not Set}                              │
│ Timezone:    {TIMEZONE|UTC}                                   │
│ Network:     {NETWORK-STATUS|Connected}                       │
└─────────────────────────────────────────────────────────────┘
```

{#if SYSTEM-STATUS == "needs-healing"}
## ⚠️ System Alerts

```
┌─ ACTION REQUIRED ─────────────────────────────────────────────┐
│ 🎲 Dependencies need healing! Run: [SYSTEM|HEAL]              │
│ 🔧 Some components may not function properly                  │
└─────────────────────────────────────────────────────────────┘
```
{/if}

{#if USER-LEVEL:number >= 40}
## 🚀 Quick Actions Available

### 📋 System Management
- **[STATUS]** - Refresh this dashboard
- **[SYSTEM|HEAL]** - Run dependency self-healing
- **[LIST]** - View all system variables

{#if USER-LEVEL:number >= 60}
### 🎨 Template & Variable Operations
- **[TEMPLATE|LIST]** - Show available templates
- **[VARIABLE|EXPORT]** - Export variables to environment
- **[GET|{any-variable}]** - Query specific variable values
{/if}

{#if USER-LEVEL:number >= 80}
### 🛠️ Advanced Operations
- **[DEV|MODE]** - Enter development mode
- **[EXTENSION|LIST]** - Show installed extensions
- **[BACKUP|CREATE]** - Create system backup
{/if}
{/if}

---
*💡 Use [HELP] for complete command reference or [HELP|COMPLETE] for detailed documentation*
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
