# Command Cheat Sheet - v1.0.23

**Quick Reference for Command Consolidation & Smart Input**
**Version**: v1.0.23
**Last Updated**: November 17, 2025

---

## 🎯 Unified Commands

### DOCS - Documentation Access

```bash
# Interactive picker
DOCS

# Search across all sources
DOCS git

# Specific source
DOCS --manual git           # Command manual
DOCS --handbook VOL1        # Handbook volume
DOCS --example water        # Code examples

# Old commands (still work)
DOC <file>                  # Alias to DOCS
MANUAL <cmd>                # Alias to DOCS --manual
HANDBOOK <vol>              # Alias to DOCS --handbook
EXAMPLE <name>              # Alias to DOCS --example
```

### LEARN - Learning System

```bash
# Interactive picker
LEARN

# Auto-detect content type
LEARN water-purification    # Finds guide
LEARN knot-types           # Finds diagram

# List content
LEARN --list                # All content
LEARN --list-guides         # Just guides
LEARN --list-diagrams       # Just diagrams

# Old commands (still work)
GUIDE <name>                # Alias to LEARN
DIAGRAM <name>              # Alias to LEARN
```

### MEMORY - Memory Management

```bash
# Interactive tier picker
MEMORY

# Cross-tier search
MEMORY <query>              # Search all accessible tiers

# Specific tier
MEMORY --tier=private <file>
MEMORY --tier=shared <file>
MEMORY --tier=community <file>
MEMORY --tier=public <query>

# Save with smart tier suggestion
MEMORY --save <file>        # Auto-suggests tier based on content

# Old commands (still work)
PRIVATE <file>              # Alias to MEMORY --tier=private
SHARED <file>               # Alias to MEMORY --tier=shared
COMMUNITY <file>            # Alias to MEMORY --tier=community
KB <query>                  # Alias to MEMORY --tier=public
```

---

## ⚡ Built-in Aliases

### Help & Navigation
```bash
?          # HELP
??         # HELP --all
h          # HELP
q          # QUIT
x          # EXIT
cls        # CLEAR
```

### Documentation
```bash
d          # DOCS
doc        # DOCS
m          # DOCS --manual
man        # DOCS --manual
hb         # DOCS --handbook
ex         # DOCS --example
```

### Learning
```bash
learn      # LEARN
guide      # LEARN --guides
diag       # LEARN --diagrams
```

### Memory
```bash
@          # MEMORY
@@         # MEMORY --list
m          # MEMORY (alternative)
priv       # MEMORY --private
share      # MEMORY --shared
comm       # MEMORY --community
kb         # MEMORY --public
```

### File Operations
```bash
l          # LIST
ls         # LIST
cd         # DIRECTORY
pwd        # DIRECTORY --current
e          # EDIT
v          # VIEW
cat        # VIEW
s          # SAVE
w          # SAVE
```

### System
```bash
!          # HISTORY
!!         # HISTORY --last
env        # ENV
set        # SETTINGS
cfg        # CONFIG
stat       # STATUS
```

---

## 🎨 Smart Features

### Fuzzy Matching
```bash
# Typo tolerance (up to 3 chars)
LOAD READMI              # Finds README.md
LOAD road                # Finds ROADMAP.MD
LOAD contribut           # Finds CONTRIBUTING.md

# Abbreviations
LOAD readme              # README.md
LOAD road                # ROADMAP.MD
LOAD contrib             # CONTRIBUTING.md
```

### Custom Aliases
```bash
# Create alias
ALIAS gm "DOCS --manual git"
ALIAS wg "LEARN water-purification"

# Use alias
gm                       # Expands to DOCS --manual git
wg                       # Expands to LEARN water-purification

# List aliases
ALIAS --list

# Remove alias
ALIAS --remove gm

# Export/Import
ALIAS --export aliases.json
ALIAS --import aliases.json
```

### Interactive Pickers
```bash
# Any command without args shows picker
DOCS                     # Pick: Documentation | Manual | Handbook | Examples
LEARN                    # Pick: Guides | Diagrams | Tutorials
MEMORY                   # Pick: Private | Shared | Community | Public

# Navigate with arrow keys
↑/↓                      # Move selection
ENTER                    # Confirm
ESC                      # Cancel
1-9                      # Quick select by number
/                        # Filter/search
```

---

## 📊 Performance Commands

### Profiling
```bash
# Enable profiling
PROFILE --enable

# View stats
PROFILE --stats

# View slowest commands
PROFILE --slowest

# Per-command stats
PROFILE --command DOCS

# Export to JSON
PROFILE --export stats.json
```

### Cache Management
```bash
# View cache stats
CACHE --stats

# Clear cache
CACHE --clear

# Cache report
CACHE --report
```

### Startup Optimization
```bash
# View startup stats
STATS --startup

# Optimization recommendations
STATS --optimize

# Detailed timing
STATS --timing
```

---

## 🐛 Error Handling

### Error Messages with Suggestions
```bash
# File not found
LOAD READMI.md
# → Shows similar files: README.md, READMAP.MD

# Command not found
DOCZ
# → Did you mean: DOCS, DOC?

# Invalid argument
MEMORY --tier=privat
# → Did you mean: private, shared, community, public?

# Permission denied
MEMORY --tier=private other-user-file.txt
# → Explains tier permissions, how to request access
```

---

## 🎯 Common Workflows

### Documentation Workflow
```bash
# Find documentation on a topic
DOCS git                 # Search all sources

# Read specific manual
DOCS --manual git

# Browse handbook
DOCS --handbook VOL1

# View examples
DOCS --example water-purification
```

### Learning Workflow
```bash
# Browse available content
LEARN --list

# Start a guide
LEARN water-purification

# View a diagram
LEARN knot-types

# Continue where you left off
LEARN --continue
```

### Memory Workflow
```bash
# Save with smart tier suggestion
MEMORY --save passwords.txt    # → Suggests: private
MEMORY --save config.json      # → Suggests: shared
MEMORY --save script.sh        # → Suggests: community

# Search across tiers
MEMORY "database config"       # Searches all accessible tiers

# Access specific tier
MEMORY --tier=private --list   # List private files
```

---

## 💡 Pro Tips

### Speed Tips
```bash
# Use short aliases
d                        # Instead of DOCS
m git                    # Instead of DOCS --manual git
@                        # Instead of MEMORY

# Use fuzzy matching
LOAD readme              # Instead of typing full path

# Use recent files
LOAD                     # Shows picker with recent files
```

### Efficiency Tips
```bash
# Create custom aliases for frequent commands
ALIAS gm "DOCS --manual git"
ALIAS sql "DOCS --manual sql"

# Use tab completion (if enabled)
DOC<TAB>                 # Completes to DOCS

# Chain commands
DOCS git && LEARN git-basics
```

### Power User Tips
```bash
# Profile your workflow
PROFILE --enable
# ... use uDOS normally ...
PROFILE --stats          # See which commands are slow

# Optimize startup
STATS --startup
STATS --optimize         # Get recommendations

# Export aliases for backup
ALIAS --export ~/backup/aliases.json
```

---

## 🔍 Search & Filter

### Documentation Search
```bash
# Search all sources
DOCS <query>

# Search specific source
DOCS --manual --search <query>
DOCS --handbook --search <query>

# Filter by relevance
DOCS git --sort=relevance
```

### Memory Search
```bash
# Cross-tier search
MEMORY <query>

# Tier-specific search
MEMORY --tier=private --search <query>

# Filter by type
MEMORY --type=config <query>
MEMORY --type=script <query>
```

---

## 📱 Viewport-Aware

### Compact Mode (Small Screens)
```bash
# Pickers automatically adjust
DOCS                     # Compact picker on small screens

# Minimal output
--compact                # Flag for compact output
```

### Full Mode (Large Screens)
```bash
# Rich pickers with descriptions
DOCS                     # Full picker with details

# Extended output
--verbose                # Flag for detailed output
```

---

## 🆘 Help Commands

```bash
# General help
HELP
?

# Command-specific help
HELP DOCS
HELP LEARN
HELP MEMORY

# Get examples
DOCS --example <command>

# View handbook
DOCS --handbook

# Search help
HELP --search <topic>
```

---

## 🎓 Learning Path

### Beginner
1. Learn basic navigation: `?, HELP, DOCS`
2. Use interactive pickers: `DOCS`, `LEARN`, `MEMORY`
3. Try fuzzy matching: `LOAD readme`

### Intermediate
1. Create custom aliases: `ALIAS`
2. Use specific flags: `DOCS --manual git`
3. Explore memory tiers: `MEMORY --tier=private`

### Advanced
1. Profile performance: `PROFILE --stats`
2. Optimize workflow: `STATS --optimize`
3. Export/import configs: `ALIAS --export`

---

**Print this for quick reference!**
**More details**: `DOCS --handbook v1.0.23-features`

---

**Version**: v1.0.23
**Last Updated**: November 17, 2025
**Maintained By**: uDOS Development Team
