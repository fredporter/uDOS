# KNOWLEDGE Commands - 4-Tier Knowledge Bank

Complete guide to the KNOWLEDGE system for storing and sharing survival information (v1.0.20)

---

## 🧠 Overview

The **KNOWLEDGE System** provides a 4-tier encrypted knowledge bank for storing personal notes, sharing with friends, collaborating in communities, and accessing curated survival guides.

### Key Features
- **4-Tier Privacy Model** (Personal → Shared → Group → Public)
- **AES-256 Encryption** for Tier 0 (Personal)
- **Anonymous contributions** in Tier 2 (Group)
- **500+ Curated guides** in Tier 3 (Public)
- **View tracking** and popularity metrics
- **Full-text search** across all tiers
- **Tag-based organization** for filtering
- **Web GUI** with real-time updates

---

## 🎯 The 4-Tier System

| Tier | Icon | Name | Privacy | Author | Use Case |
|:----:|:-----|:-----|:--------|:-------|:---------|
| **0** | 🔒 | **PERSONAL** | Encrypted (AES-256) | You | Private notes, secrets, passwords |
| **1** | 🤝 | **SHARED** | Optional encryption | You | Share with trusted friends/family |
| **2** | 👥 | **GROUP** | Anonymous | Anonymous | Community knowledge, collaborative |
| **3** | 🌍 | **PUBLIC** | Public domain | Curators | Official survival guides (500+) |

### Tier 0: PERSONAL (Private)
- **Encrypted at rest** with AES-256
- **Master password** required to access
- **Never synced** or shared
- **Perfect for**: Passwords, medical info, personal strategies, sensitive data

### Tier 1: SHARED (Private Shared)
- **Optional encryption** (your choice)
- **Shareable** with specific people via export
- **Author attribution** (your name)
- **Perfect for**: Family recipes, group plans, trusted circle knowledge

### Tier 2: GROUP (Community)
- **Anonymous contributions** (no author names)
- **Community moderation** (voting, flagging)
- **Public read access** but controlled write
- **Perfect for**: Community tips, collective wisdom, crowd-sourced guides

### Tier 3: PUBLIC (Official)
- **Curated by maintainers** (quality controlled)
- **Public domain** knowledge
- **500+ survival guides** covering water, food, shelter, medical, etc.
- **Perfect for**: Official documentation, trusted reference material

---

## 📝 Knowledge Types

Each knowledge item has a type for categorization:

1. **survival** - Emergency preparedness, safety protocols
2. **skill** - How-to guides, step-by-step tutorials
3. **recipe** - Food preparation, cooking methods
4. **guide** - Comprehensive instructions
5. **reference** - Quick facts, data tables, lookups
6. **note** - Personal observations, reminders
7. **link** - URL bookmarks, external resources
8. **experience** - Personal stories, lessons learned
9. **tip** - Quick advice, life hacks
10. **warning** - Safety alerts, hazards

---

## 🚀 Quick Start

### View Tier System
```bash
🔮 > KNOWLEDGE TIERS

📊 Knowledge Tiers:
╔════╦═══════════╦═══════════════╦═══════════════════╗
║ #  ║ Name      ║ Privacy       ║ Description       ║
╠════╬═══════════╬═══════════════╬═══════════════════╣
║ 0  ║ PERSONAL  ║ 🔒 Encrypted  ║ Private notes     ║
║ 1  ║ SHARED    ║ 🤝 Optional   ║ Share w/ friends  ║
║ 2  ║ GROUP     ║ 👥 Anonymous  ║ Community         ║
║ 3  ║ PUBLIC    ║ 🌍 Public     ║ Official (500+)   ║
╚════╩═══════════╩═══════════════╩═══════════════════╝
```

### Add Knowledge
```bash
🔮 > KNOWLEDGE ADD 0 survival "Emergency Water Filter"
📝 Enter content (end with '.' on new line):
> Boil water for 3 minutes minimum
> Or use cloth + charcoal + sand layers
> Always test with small amount first
> .

🏷️  Tags (comma-separated):
> water,survival,emergency

✅ Knowledge added to PERSONAL tier
   ID: abc123-def456
   Type: survival
   Tags: water, survival, emergency
```

### Search Knowledge
```bash
🔮 > KNOWLEDGE SEARCH "water purification"

🔍 Search Results (12 items):

[Tier 3 - PUBLIC] 🌍
  📖 Water Purification Methods
     boiling, chemicals, UV, filtration
     Views: 1,247 | Type: guide

[Tier 0 - PERSONAL] 🔒
  📌 My Water Filter Setup
     Personal notes on setup
     Views: 3 | Type: note

[Tier 2 - GROUP] 👥
  💡 Community Water Tips
     Crowd-sourced advice
     Views: 456 | Type: tip

...
```

### View Item
```bash
🔮 > KNOWLEDGE VIEW abc123-def456

╔══════════════════════════════════════════╗
║ Emergency Water Filter                   ║
╠══════════════════════════════════════════╣
║ 🔒 PERSONAL | survival                   ║
║ 👁️  Views: 1 | 📅 2025-11-17            ║
╚══════════════════════════════════════════╝

Boil water for 3 minutes minimum
Or use cloth + charcoal + sand layers
Always test with small amount first

🏷️  Tags: water, survival, emergency

✅ View count incremented
```

---

## 📚 Commands Reference

### KNOWLEDGE ADD
Add new knowledge item

**Usage**:
```bash
KNOWLEDGE ADD <tier> <type> <title>
```

**Interactive prompts**:
1. Enter multi-line content (end with `.` on new line)
2. Enter comma-separated tags

**Examples**:
```bash
# Personal encrypted note
KNOWLEDGE ADD 0 note "Password List"

# Shared recipe
KNOWLEDGE ADD 1 recipe "Grandma's Bread Recipe"

# Community tip
KNOWLEDGE ADD 2 tip "Solar Panel Angle Optimization"

# You cannot directly add to Tier 3 (curators only)
```

---

### KNOWLEDGE SEARCH
Search across all tiers or specific tier

**Usage**:
```bash
KNOWLEDGE SEARCH <query> [--tier N] [--tags tag1,tag2]
```

**Examples**:
```bash
# Search all tiers
KNOWLEDGE SEARCH "solar power"

# Search only public tier
KNOWLEDGE SEARCH "water" --tier 3

# Search with tag filter
KNOWLEDGE SEARCH "food" --tags recipe,cooking

# Combined filters
KNOWLEDGE SEARCH "emergency" --tier 2 --tags survival,medical
```

**Search Features**:
- **Full-text search** (title + content)
- **Case-insensitive**
- **Partial matching**
- **Tag filtering**
- **Tier filtering**
- **Relevance ranking** (view count, recency)

---

### KNOWLEDGE VIEW
View knowledge item (increments view count)

**Usage**:
```bash
KNOWLEDGE VIEW <id>
```

**Example**:
```bash
KNOWLEDGE VIEW abc123-def456
```

**Displays**:
- Title
- Tier and type
- View count
- Date added
- Full content
- Tags

**Privacy**:
- Tier 0 requires master password
- Tier 1/2/3 readable by all

---

### KNOWLEDGE STATS
Get statistics for all tiers

**Usage**:
```bash
KNOWLEDGE STATS
```

**Example Output**:
```bash
🔮 > KNOWLEDGE STATS

📊 Knowledge Bank Statistics:
═══════════════════════════════════════════

Tier 0 - PERSONAL (🔒 Encrypted):
  Items: 47
  Types: note (23), survival (12), reference (8), password (4)
  Most viewed: "Emergency Contacts" (12 views)

Tier 1 - SHARED (🤝 Private):
  Items: 15
  Types: recipe (8), guide (5), tip (2)
  Most viewed: "Family Emergency Plan" (8 views)

Tier 2 - GROUP (👥 Community):
  Items: 234
  Contributors: 45 (anonymous)
  Most viewed: "Solar Panel Setup Guide" (892 views)

Tier 3 - PUBLIC (🌍 Official):
  Items: 512
  Categories: water (45), food (78), shelter (34), medical (67)...
  Most viewed: "Water Purification Methods" (1,247 views)

═══════════════════════════════════════════
Total Items: 808
Total Views: 12,456
```

---

### KNOWLEDGE LIST
List items in a tier

**Usage**:
```bash
KNOWLEDGE LIST <tier> [--type TYPE] [--limit N]
```

**Examples**:
```bash
# List all personal notes
KNOWLEDGE LIST 0

# List public survival guides
KNOWLEDGE LIST 3 --type survival

# List top 10 community items
KNOWLEDGE LIST 2 --limit 10
```

---

### KNOWLEDGE UPDATE
Update existing item (your items only)

**Usage**:
```bash
KNOWLEDGE UPDATE <id>
```

**Prompts for**:
- New content (or keep existing)
- New tags (or keep existing)

**Example**:
```bash
KNOWLEDGE UPDATE abc123-def456
```

**Restrictions**:
- Can only update your own items (Tier 0, 1)
- Cannot update Tier 2 (anonymous)
- Cannot update Tier 3 (curators only)

---

### KNOWLEDGE DELETE
Remove knowledge item (your items only)

**Usage**:
```bash
KNOWLEDGE DELETE <id>
```

**Example**:
```bash
KNOWLEDGE DELETE abc123-def456
✅ Knowledge deleted from PERSONAL tier
```

---

### KNOWLEDGE EXPORT
Export tier to file

**Usage**:
```bash
KNOWLEDGE EXPORT <tier> <filename>
```

**Examples**:
```bash
# Export personal notes (encrypted)
KNOWLEDGE EXPORT 0 my_notes_backup.json

# Export shared knowledge (plaintext)
KNOWLEDGE EXPORT 1 family_knowledge.json

# Export public guides
KNOWLEDGE EXPORT 3 survival_guides.json
```

**Format**: JSON with metadata

---

### KNOWLEDGE IMPORT
Import knowledge from file

**Usage**:
```bash
KNOWLEDGE IMPORT <tier> <filename>
```

**Example**:
```bash
KNOWLEDGE IMPORT 1 family_knowledge.json
✅ Imported 15 items into SHARED tier
```

---

## 🌐 Web GUI

Access the knowledge bank through a web interface:

**URL**: `http://localhost:5001/knowledge.html`

### Features
- 📊 **Dashboard** with tier statistics
- 🔍 **Live search** (300ms debounce)
- 🎨 **Color-coded tabs** for each tier
- 🔒 **Privacy indicators** on items
- 👁️ **View count tracking**
- 📱 **Responsive design**
- ⚡ **Real-time updates** via WebSocket

### Interface Layout
```
╔═══════════════════════════════════════════════╗
║  [🔒 PERSONAL] [🤝 SHARED] [👥 GROUP] [🌍 PUBLIC] ║
╠═══════════════════════════════════════════════╣
║  [Search: _______________] [🔍]               ║
╠═══════════════════════════════════════════════╣
║  📊 Statistics:                               ║
║    Personal: 47 items                         ║
║    Shared: 15 items                           ║
║    Group: 234 items                           ║
║    Public: 512 items                          ║
╠═══════════════════════════════════════════════╣
║  📖 Recent Items:                             ║
║    • Emergency Water Filter (survival)        ║
║    • Solar Panel Setup (guide)                ║
║    • Bread Recipe (recipe)                    ║
╚═══════════════════════════════════════════════╝
```

---

## 🔌 API Endpoints

For integration with other tools:

```http
GET  /api/knowledge/stats                    # Tier statistics
GET  /api/knowledge/search?query=X&tier=N    # Search knowledge
GET  /api/knowledge/view/<id>                # View item
POST /api/knowledge/add                      # Create knowledge
GET  /api/knowledge/tiers                    # List tiers
POST /api/knowledge/update/<id>              # Update item
DELETE /api/knowledge/delete/<id>            # Delete item
```

---

## 🎯 Use Cases

### Personal Survival Notes (Tier 0)
```bash
# Store encrypted emergency info
KNOWLEDGE ADD 0 reference "Emergency Contacts"
> Police: 000
> Poison Info: 13 11 26
> ...

KNOWLEDGE ADD 0 survival "Bug Out Bag Contents"
> Water purification tablets (50)
> Emergency blanket
> ...
```

### Family Knowledge Sharing (Tier 1)
```bash
# Share recipes and plans
KNOWLEDGE ADD 1 recipe "Mom's Sourdough"
KNOWLEDGE ADD 1 guide "Family Emergency Meeting Point"
KNOWLEDGE EXPORT 1 family_backup.json
# Send file to family members
```

### Community Collaboration (Tier 2)
```bash
# Anonymous community tips
KNOWLEDGE ADD 2 tip "Best Solar Panel Angle"
KNOWLEDGE ADD 2 experience "Survived 2024 Floods"
KNOWLEDGE SEARCH "water collection" --tier 2
```

### Reference Guides (Tier 3)
```bash
# Access official guides
KNOWLEDGE SEARCH "first aid" --tier 3
KNOWLEDGE VIEW [public-guide-id]
```

---

## 🔐 Security

### Tier 0 Encryption
- **AES-256-CBC** encryption
- **Master password** derived with PBKDF2
- **Salt** unique per installation
- **IV** unique per knowledge item
- **Encrypted at rest**, decrypted in memory only

### Master Password
Set on first use:
```bash
KNOWLEDGE ADD 0 note "First Item"
🔑 Set master password: ********
🔑 Confirm password: ********
✅ Master password set
```

Change password:
```bash
KNOWLEDGE PASSWORD
🔑 Current password: ********
🔑 New password: ********
🔑 Confirm new password: ********
✅ Password changed, re-encrypting Tier 0...
```

### Best Practices
- **Strong password** (12+ chars, mixed case, symbols)
- **Don't forget** (no recovery mechanism)
- **Regular backups** (encrypted exports)
- **Separate backups** of password (physical, secure location)

---

## 🧪 Testing

Run knowledge system tests:
```bash
pytest memory/tests/test_tier_knowledge.py -v
```

**Expected**: 11/11 passing

---

## 📁 File Locations

```
uDOS/
├── memory/
│   ├── private/              # Tier 0 (encrypted)
│   │   └── knowledge/
│   ├── shared/               # Tier 1
│   │   └── knowledge/
│   ├── groups/               # Tier 2
│   │   └── knowledge/
│   └── public/               # Tier 3
│       └── knowledge/
└── knowledge/                # System knowledge (500+ guides)
    ├── survival/
    ├── skills/
    ├── food/
    └── ...
```

---

## 📚 Related Documentation

- [Command Reference](Command-Reference) - All uDOS commands
- [TILE Commands](TILE-Commands) - Geographic reference data
- [Getting Started](Getting-Started) - Basic usage
- [Knowledge Architecture](Knowledge-Architecture) - System design

---

*Your offline knowledge bank - from private notes to community wisdom.*
