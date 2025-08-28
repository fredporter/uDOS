# 🎛️ uDOS System Dashboard

*Last Updated: {TIMESTAMP} | System Status: {SYSTEM-STATUS}*

## 👤 User Profile

```
┌─ User: {USER-ROLE} (Level {USER-LEVEL}) ─────────────────────┐
│ Session ID:   active-session                                │
│ Permissions:  Role-Based Access                             │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 System Status

```
┌─ Current System State ────────────────────────────────────────┐
│ Status:        {SYSTEM-STATUS}                               │
│ Dependencies:  {DEPENDENCY-STATUS|Checking...}              │
│ Self-Healing:  {SELF-HEALING-STATUS|Available}              │
│ Templates:     {TEMPLATE-STATUS|Available}                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Available Actions

### 📋 Core Commands
- **[HELP]** - Show command reference  
- **[TEMPLATE|LIST]** - Show available templates
- **[LIST]** - View all system variables
- **[STATUS]** - Refresh this dashboard

### 🎨 Template System  
- **[TEMPLATE|RENDER*help]** - Render help template
- **[TEMPLATE|VARIABLES]** - Show template variables
- **[TEMPLATE|STATUS]** - Show template system status

### 🛠️ System Management
- **[SYSTEM|HEAL]** - Run dependency self-healing  
- **[GET|variable]** - Query variable values
- **[SET|variable*value]** - Set variable values

---
*💡 Use [HELP] for complete command reference*
*🎯 Template System Integration: Active*
