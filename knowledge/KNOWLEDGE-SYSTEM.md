# 📚 Knowledge Base - uDOS v1.2

**Purpose**: Offline-first knowledge repository for uDOS system and user content

---

## Directory Structure

```
knowledge/
├── README.md              # This file
├── commands/              # Command usage guides (system)
├── concepts/              # Programming concepts (system)
├── maps/                  # World navigation data (system)
├── faq/                   # Common questions (system)
├── datasets/              # Distributed data sets (system)
└── personal/              # YOUR knowledge (gitignored)
    ├── notes/
    ├── research/
    ├── projects/
    └── cheatsheets/
```

---

## System Knowledge (Tracked)

### `/commands` - Command Reference
Detailed guides for each uDOS command with examples, use cases, and troubleshooting.

**Planned Structure**:
```
commands/
├── EDIT.md
├── OUTPUT.md
├── THEME.md
├── MAP.md
├── ASK.md
└── ...
```

### `/concepts` - Core Concepts
Programming and system design concepts explained in the uDOS context.

**Planned Topics**:
- Command parsing architecture
- uCODE language reference
- Theme system internals
- Variable resolution system
- Extension development

### `/maps` - Navigation Data
World maps for the MAP command NetHack-style navigation system.

**Example**:
```
maps/
├── worldmap.json
├── dungeons/
└── galaxies/
```

### `/datasets` - Offline Data
Distributed data sets that ship with uDOS for offline functionality.

**Examples**:
- City coordinates
- Character templates
- Inventory databases
- Quest structures

### `/faq` - Frequently Asked Questions
Organized Q&A loaded by the offline OK Assisted Task system (data/FAQ.UDO links here).

---

## Personal Knowledge (Gitignored)

### `/personal` - Your Content

This directory is **completely yours** and gitignored by default.

**Suggested Organization**:

```
personal/
├── notes/
│   ├── daily/           # Daily logs
│   ├── meetings/        # Meeting notes
│   └── ideas/           # Brainstorming
├── research/
│   ├── papers/          # Research papers
│   ├── experiments/     # Lab notebooks
│   └── findings/        # Results
├── projects/
│   ├── web-app/
│   ├── data-science/
│   └── game-dev/
└── cheatsheets/
    ├── git.md
    ├── python.md
    └── sql.md
```

---

## Using Knowledge with LEARN Command

**Planned v1.2 Feature** (Priority 3 in ROADMAP.MD):

```bash
# Browse knowledge base
LEARN

# View specific topic
LEARN commands/THEME

# Search knowledge
LEARN SEARCH "theme system"

# View your personal notes
LEARN personal/projects/web-app

# List all in category
LEARN COMMANDS    # Lists all command guides
```

---

## Best Practices

### ✅ DO

- ✅ Organize personal knowledge however works for you
- ✅ Use descriptive filenames (verb-noun: analyze-data.md)
- ✅ Add frontmatter for better searchability
- ✅ Link related articles
- ✅ Keep backups of important notes

### ❌ DON'T

- ❌ Put secrets in tracked knowledge files
- ❌ Modify system knowledge without testing
- ❌ Commit personal/ to git (it's gitignored)
- ❌ Use proprietary formats (stick to .md, .json, .txt)

---

**Knowledge is Power. Offline Knowledge is Freedom.** 📚🔒
