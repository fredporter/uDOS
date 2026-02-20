---
title: Command Examples & Workflows
description: Practical examples for uDOS core commands
version: 1.0.0
---

# uDOS Command Workflows & Examples

Quick reference for common command patterns and workflows.

---

## Navigation & Movement

### MAP - View world map
```bash
MAP                    # Show current map with player position
MAP LIST              # List available locations
MAP SHOW <location>   # Show specific location details
```

### ANCHOR - Manage map markers
```bash
ANCHOR LIST                          # Show saved anchors
ANCHOR ADD <name> <description>      # Create new anchor at current location
ANCHOR GOTO <name>                   # Fast travel to anchor
ANCHOR DELETE <name>                 # Remove anchor
```

### GOTO - Navigation shortcut
```bash
GOTO <location>          # Navigate to location by name/ID
GOTO LAST               # Go to previous location
GOTO HOME               # Go to spawn/home location
```

### FIND - Search locations
```bash
FIND <keyword>          # Search for locations matching keyword
FIND <keyword> --near   # Find nearby locations
FIND --tags <tag>       # Find by tag
```

### PANEL - Display map panel
```bash
PANEL                   # Show current panel
PANEL EDIT             # Customize panel layout
```

### GRID - Data visualization
```bash
GRID CALENDAR --input memory/system/grid-calendar-sample.json
GRID TABLE --input memory/system/grid-table-sample.json
GRID SCHEDULE --input memory/system/grid-schedule-sample.json
GRID MAP --input memory/system/grid-overlays-sample.json
GRID WORKFLOW --input memory/system/grid-workflow-sample.json
GRID DASHBOARD         # Custom dashboard view
```

---

## File & Content Management

### READ - Read file content
```bash
READ <file.md>                    # Display file content
READ <file> --lines 50            # Show last 50 lines
READ memory/system/config.json   # Read JSON config files
```

### FILE - File picker & operations
```bash
FILE                   # Open file browser/picker
FILE LIST <dir>       # List directory contents
FILE WATCH <path>     # Monitor file for changes
```

### FILE NEW - Create new file
```bash
FILE NEW <name>              # Create file in /memory
FILE NEW --template story    # Create from template
```

### FILE EDIT - Edit file
```bash
FILE EDIT <file.md>          # Open in editor
FILE EDIT --line 42          # Jump to specific line
```

### STORY - Story/narrative mode
```bash
STORY <file.md>                 # Read story file with formatting
STORY LIST                      # List available stories
STORY NEW <name>                # Create new story
STORY PARSE <file>              # Parse story structure
```

### PLACE - Workspace file placement
```bash
PLACE                           # Interactive workspace picker
PLACE <workspace> <file>       # Place file in workspace
PLACE --default <workspace>    # Set default workspace
```

### LIBRARY - Shared content management
```bash
LIBRARY LIST                    # List available libraries
LIBRARY SEARCH <keyword>        # Search library content
LIBRARY IMPORT <source>         # Import library package
LIBRARY STATUS                  # Check library sync status
```

### BINDER - Content compilation
```bash
BINDER LIST                     # Show available binders
BINDER SELECT <name>           # Choose binder
BINDER BUILD                   # Compile binder contents
BINDER EXPORT --format pdf     # Export binder
```

---

## Script & Automation

### RUN - General script execution
```bash
RUN <script.md>                  # Execute uDOS script
RUN --ts <file> <section>       # Run TypeScript section
RUN DATA LIST                   # List data definitions
RUN DATA VALIDATE <id>         # Validate data schema
```

### SCRIPT - System script runner
```bash
SCRIPT RUN <name>              # Execute system script
SCRIPT LIST                    # List available scripts
SCRIPT NEW <name>              # Create new script
```

### SCHEDULER - Task scheduling
```bash
SCHEDULER LIST                 # Show scheduled tasks
SCHEDULER ADD <name> <command> # Create recurring task
SCHEDULER RUN <name>           # Execute scheduled task
SCHEDULER DELETE <name>        # Remove task
```

### RULE - Conditional automation
```bash
RULE LIST                                    # Show automation rules
RULE ADD --condition "game.level > 5" \
         --action "SPAWN boss_entity"        # Create IF/THEN rule
RULE TEST <rule_id>                         # Test rule
RULE DELETE <rule_id>                       # Remove rule
```

---

## Data & State Management

### BAG - Inventory management
```bash
BAG                    # Show inventory
BAG ADD <item>         # Add item
BAG REMOVE <item>      # Remove item
BAG SEARCH <keyword>   # Find items
```

### GRAB - Pickup/loot
```bash
GRAB <item>           # Pick up item from ground
GRAB --nearby         # Show available items
GRAB --verbose        # Show details
```

### SPAWN - Entity creation
```bash
SPAWN <entity_type> <name>    # Create entity
SPAWN NPC villain             # Spawn NPC
SPAWN ITEM sword              # Create item
```

### SAVE - Save game state
```bash
SAVE                        # Quick save
SAVE <name>                 # Named save
SAVE --backup               # Save with auto-backup
```

### LOAD - Load game state
```bash
LOAD                        # Load latest save
LOAD <name>                 # Load named save
LOAD --list                 # Show savefiles
```

### MIGRATE - Data migration
```bash
MIGRATE                          # Check migration status
MIGRATE --from v1.2 --to v1.3   # Migrate data format
MIGRATE VALIDATE                 # Verify migration
```

---

## System Administration

### HEALTH - System health check
```bash
HEALTH                # Quick health check
HEALTH --full         # Detailed diagnostics
HEALTH --json         # JSON output
```

### VERIFY - Deeper system verification
```bash
VERIFY                     # Verify all systems
VERIFY --services          # Check service health
VERIFY --database          # Check database integrity
```

### REPAIR - System repair
```bash
REPAIR                # Attempt automatic repairs
REPAIR --dry-run      # Show what would be repaired
REPAIR --deep         # Full system reconstruction
```

### LOGS - View system logs
```bash
LOGS                          # Show recent logs
LOGS --level ERROR            # Filter by level
LOGS TAIL --lines 50         # Last 50 lines
LOGS SEARCH <keyword>         # Search logs
```

### BACKUP - Create backup
```bash
BACKUP                 # Create backup snapshot
BACKUP --scope game   # Backup game data only
BACKUP --scope all    # Full system backup
```

### RESTORE - Restore from backup
```bash
RESTORE                    # Restore latest backup
RESTORE <timestamp>       # Restore specific version
RESTORE --list           # Show available backups
```

### TIDY - Soft cleanup
```bash
TIDY                     # Clean temporary files
TIDY --scope cache       # Clean specific scope
TIDY --dry-run          # Preview changes
```

### CLEAN - More aggressive cleanup
```bash
CLEAN                    # Deeper cleanup
CLEAN --history          # Remove history/logs
CLEAN --dry-run         # Preview changes
```

### COMPOST - Archive old data
```bash
COMPOST                              # Archive old backups
COMPOST --before "2025-12-31"       # Archive before date
COMPOST LIST                         # Show archived items
```

### DESTROY - Full system reset
```bash
DESTROY                  # Full system wipe (DANGEROUS!)
DESTROY --confirm        # Proceed with confirmation
DESTROY --keep data      # Preserve data folder
```

---

## Development & Extension

### DEV - Development mode
```bash
DEV                    # Toggle dev mode
DEV STATUS             # Check dev mode status
DEV LOGS               # Show dev mode logs
DEV HEALTH             # Dev mode health check
DEV RESTART            # Restart dev services
DEV CLEAR              # Clear caches
```

### DRAW - ASCII visualization
```bash
DRAW PAT LIST                          # List patterns
DRAW PAT <pattern-name>               # Show pattern
DRAW PAT TEXT "<text>"               # Pattern from text
DRAW PAT CYCLE                        # Cycle through patterns
DRAW MD <mode>                        # Markdown diagram mode
DRAW --save <file.md> <mode>         # Save diagram
```

### VIEWPORT - Display measurement
```bash
VIEWPORT                              # Show current viewport size
VIEWPORT SHOW                         # Display details
VIEWPORT MEASURE                      # Get dimensions
```

### SEED - Framework initialization
```bash
SEED                   # Show seed status
SEED INSTALL          # Install framework seed data
SEED STATUS           # Check installation
SEED HELP             # Seed instructions
```

---

## Music & Media

### MUSIC - Songscribe/Groovebox integration
```bash
MUSIC LIST                     # Show patterns
MUSIC SHOW <pattern>           # Show pattern details
MUSIC PLAY <pattern>           # Play pattern
MUSIC EXPORT <pattern>         # Export pattern
MUSIC TRANSCRIBE <file>        # Transcribe audio
```

---

## User & Authentication

### USER - User profile management
```bash
USER                      # Show current user
USER PROFILE              # Edit profile
USER ROLE                 # Show/change role
USER PERMISSIONS          # Show permissions
```

### TOKEN - Token generation
```bash
TOKEN                     # Show current token
TOKEN GENERATE            # Create new token
TOKEN REVOKE             # Invalidate token
```

### UID - User identity
```bash
UID                   # Show current UID
UID VALIDATE          # Verify UID
```

### GHOST - Ghost mode
```bash
GHOST                 # Toggle ghost mode
GHOST STATUS          # Check ghost mode
GHOST POLICY          # Show ghost policy
```

---

## System Management

### WIZARD - Wizard server control
```bash
WIZARD                      # Show Wizard menu
WIZARD START               # Start Wizard server
WIZARD STOP                # Stop Wizard server
WIZARD STATUS              # Check Wizard health
WIZARD RESET               # Reset Wizard keystore
WIZARD REBUILD             # Rebuild dashboard
```

### CONFIG - Configuration management
```bash
CONFIG                     # Show config menu
CONFIG SHOW               # Display current config
CONFIG SET <key> <value>  # Set config value
CONFIG RESET              # Reset to defaults
```

### EMPIRE - Extension management
```bash
EMPIRE STATUS             # Check Empire extension
EMPIRE START              # Start Empire API
EMPIRE STOP               # Stop Empire API
```

### SETUP - System setup
```bash
SETUP                     # Interactive setup wizard
SETUP --profile <name>   # Setup specific profile
```

### SONIC - USB builder management
```bash
SONIC STATUS              # Show Sonic status
SONIC SYNC                # Sync Sonic database
SONIC PLAN [options]      # Plan USB build
SONIC RUN [options]       # Execute USB build
```

### NPC - NPC management
```bash
NPC LIST                  # Show NPCs
NPC SPAWN <name>         # Create NPC
NPC EDIT <id>            # Edit NPC
```

### SEND/TALK - NPC dialogue
```bash
SEND <npc_id> <message>  # Send message to NPC
TELL <npc_id>            # Describe NPC
```

### PLAY - Gameplay control
```bash
PLAY                      # Show play options
PLAY STATUS              # Game status
PLAY CLAIM               # Claim achievements
PLAY TOYBOX SET <profile> # Change gameplay profile
```

### UNDO - Undo actions
```bash
UNDO                     # Undo last action
UNDO --list              # Show undo history
```

### REBOOT - System restart
```bash
REBOOT                   # Soft restart
REBOOT --hard            # Hard restart
```

---

## Quick Reference

### Essential Commands
```bash
# Navigation
MAP                    # Where am I?
GOTO <location>      # Go somewhere
FIND <keyword>       # Search

# Gameplay
BAG                  # My inventory
GRAB <item>         # Pick up item
PLAY                # Game status

# System
HEALTH              # System health
HELP                # Get help
STATUS              # General status
```

### Common Workflows

**Backing up and exploring:**
```bash
BACKUP                   # Create save point
MAP LIST                # Explore locations
GOTO <new_location>    # Navigate
SAVE game_exploration  # Save progress
```

**Development iteration:**
```bash
DEV                      # Enable dev mode
RUN script.md           # Test script
VERIFY                  # Check system
DEV RESTART             # Reload services
```

**Maintenance:**
```bash
HEALTH --full           # Check health
VERIFY                  # Verify systems
REPAIR --dry-run        # See issues
REPAIR                  # Fix issues
BACKUP                  # Save state
```
