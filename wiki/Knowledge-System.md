# Knowledge System

**Complete guide to the uDOS knowledge bank and architecture (v1.0.20)**

> **💡 Quick Start**: Store personal notes with `KNOWLEDGE ADD 0`, search with `KNOWLEDGE SEARCH`, organize knowledge hierarchically

---

## Table of Contents

1. [Overview](#overview)
2. [4-Tier Knowledge Bank](#4-tier-knowledge-bank)
3. [Knowledge Architecture](#knowledge-architecture)
4. [Commands Reference](#commands-reference)
5. [Content Organization](#content-organization)
6. [Curation Guidelines](#curation-guidelines)

---

## Overview

The uDOS Knowledge System combines a 4-tier encrypted knowledge bank with a thoughtfully architected content organization system. It's designed to maximize the utility and accessibility of information while maintaining privacy and security.

### Design Philosophy

> **Information is only valuable if it can be found, understood, and applied.**

Modern information systems fail at this in three ways:
1. **Too much noise**: Algorithmic feeds optimize for engagement, not value
2. **Poor organization**: Folder structures become unwieldy; search is inadequate
3. **Lack of curation**: No quality filter; quantity over value

**uDOS takes a different approach**: Human-curated, thoughtfully organized, and relentlessly practical.

### Key Features

- **4-Tier Privacy Model** (Personal → Shared → Group → Public)
- **AES-256 Encryption** for Tier 0 (Personal)
- **Anonymous contributions** in Tier 2 (Group)
- **500+ Curated guides** in Tier 3 (Public)
- **Hierarchical organization** based on human needs
- **Full-text search** across all tiers
- **Tag-based organization** for filtering
- **Web GUI** with real-time updates

---

## 4-Tier Knowledge Bank

### The 4-Tier System

| Tier | Icon | Name | Privacy | Author | Use Case |
|:----:|:-----|:-----|:--------|:-------|:---------|
| **0** | 🔒 | **PERSONAL** | Encrypted (AES-256) | You | Private notes, secrets, passwords |
| **1** | 🤝 | **SHARED** | Optional encryption | You | Share with trusted friends/family |
| **2** | 👥 | **GROUP** | Anonymous | Anonymous | Community knowledge, collaborative |
| **3** | 🌍 | **PUBLIC** | Public domain | Curators | Official survival guides (500+) |

#### Tier 0: PERSONAL (Private)
- **Encrypted at rest** with AES-256
- **Master password** required to access
- **Never synced** or shared
- **Perfect for**: Passwords, medical info, personal strategies, sensitive data

#### Tier 1: SHARED (Private Shared)
- **Optional encryption** (your choice)
- **Shareable** with specific people via export
- **Author attribution** (your name)
- **Perfect for**: Family recipes, group plans, trusted circle knowledge

#### Tier 2: GROUP (Community)
- **Anonymous contributions** (no author names)
- **Community moderation** (voting, flagging)
- **Public read access** but controlled write
- **Perfect for**: Community tips, collective wisdom, crowd-sourced guides

#### Tier 3: PUBLIC (Official)
- **Curated by maintainers** (quality controlled)
- **Public domain** knowledge
- **500+ survival guides** covering water, food, shelter, medical, etc.
- **Perfect for**: Official documentation, trusted reference material

### Knowledge Types

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

### Quick Start

#### View Tier System
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

#### Add Knowledge
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

#### Search Knowledge
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
```

---

## Knowledge Architecture

### The Knowledge Hierarchy

#### Top-Level Structure

```
knowledge/
├── survival/          # Immediate human needs
├── productivity/      # Getting things done
├── well-being/        # Mental and physical health
├── skills/            # Building capabilities
├── environment/       # Stewardship and sustainability
└── community/         # Human connection
```

#### Organizing Principle: Maslow's Pyramid Reimagined

```
        ┌─────────────────┐
        │   Community     │  Self-actualization
        ├─────────────────┤
        │   Environment   │  Contribution
        ├─────────────────┤
        │     Skills      │  Competence
        ├─────────────────┤
        │   Well-being    │  Safety & Belonging
        ├─────────────────┤
        │  Productivity   │  Efficiency
        ├─────────────────┤
        │    Survival     │  Basic Needs
        └─────────────────┘
```

**Why this structure?**
- Mirrors human needs hierarchy
- Progresses from essential to aspirational
- Intuitive navigation
- Scales to any amount of content

### Category Deep Dive

#### 1. Survival (Foundation)

**Purpose**: Essential knowledge for basic human needs

**Subcategories**:
```
survival/
├── first-aid/
│   ├── basic-life-support.md
│   ├── wound-care.md
│   ├── fractures-sprains.md
│   └── common-illnesses.md
├── food-water/
│   ├── water-purification.md
│   ├── food-preservation.md
│   ├── foraging.md
│   └── emergency-food-supplies.md
├── shelter/
│   ├── emergency-shelter.md
│   ├── home-repair.md
│   └── weatherproofing.md
└── tools/
    ├── essential-tools.md
    ├── tool-maintenance.md
    └── improvised-tools.md
```

**Content criteria**:
- ✅ Potentially life-saving information
- ✅ Basic needs (food, water, shelter, safety)
- ✅ Emergency preparedness
- ✅ Practical, actionable instructions
- ❌ Extreme/unlikely scenarios
- ❌ Speculation or fear-mongering

#### 2. Productivity (Efficiency)

**Purpose**: Get more done with less effort

**Subcategories**:
```
productivity/
├── time-management/
├── workflows/
├── tools/
└── automation/
```

**Content criteria**:
- ✅ Proven productivity techniques
- ✅ Tool-agnostic principles
- ✅ Measurable improvements
- ❌ Productivity theater
- ❌ Unsustainable "hustle culture"

#### 3. Well-Being (Health & Happiness)

**Purpose**: Mental and physical health maintenance

**Subcategories**:
```
well-being/
├── mental-health/
├── physical-health/
├── relationships/
└── mindfulness/
```

**Content criteria**:
- ✅ Evidence-based techniques
- ✅ Accessible to all (no special equipment)
- ⚠️ Includes "when to seek professional help"
- ❌ Medical diagnosis or treatment
- ❌ Pseudoscience

#### 4. Skills (Building Competence)

**Purpose**: Develop capabilities that increase autonomy

**Subcategories**:
```
skills/
├── programming/
├── writing/
├── art/
└── music/
```

**Content criteria**:
- ✅ Foundational knowledge
- ✅ Progressive learning paths
- ✅ Practical exercises
- ❌ Vendor-specific certifications
- ❌ Obsolete technology

#### 5. Environment (Stewardship)

**Purpose**: Sustainable living and environmental care

**Subcategories**:
```
environment/
├── gardening/
├── conservation/
├── renewable-energy/
└── permaculture/
```

**Content criteria**:
- ✅ Practical sustainability
- ✅ DIY approaches
- ✅ Science-based methods
- ❌ Greenwashing
- ❌ Unrealistic idealism

#### 6. Community (Connection)

**Purpose**: Building healthy human relationships and communities

**Subcategories**:
```
community/
├── collaboration/
├── conflict-resolution/
├── mutual-aid/
└── local-resilience/
```

**Content criteria**:
- ✅ Practical relationship skills
- ✅ Community building techniques
- ❌ Manipulative tactics
- ❌ Pyramid schemes / MLM

---

## Commands Reference

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
```

**Format**: JSON with metadata

---

### KNOWLEDGE IMPORT
Import knowledge from file

**Usage**:
```bash
KNOWLEDGE IMPORT <tier> <filename>
```

---

## Content Organization

### Search and Discovery

#### Multi-Level Search Strategy

**1. Hierarchical Browse**
- Start at category level
- Drill down through subcategories
- Scan README files for overviews

**2. Full-Text Search**
```bash
# Find all mentions of "first aid"
grep -r "first aid" knowledge/

# Search specific category
grep -r "meditation" knowledge/well-being/

# Case-insensitive search
grep -ri "python" knowledge/skills/
```

**3. Tag-Based Search**
Documents include YAML frontmatter with tags:

```yaml
---
title: Water Purification Methods
category: survival
subcategory: food-water
tags: [emergency, water, filtration, survival-basics]
difficulty: beginner
last-updated: 2025-11-14
---
```

Search by tag:
```bash
# Find all beginner-level content
grep -r "difficulty: beginner" knowledge/

# Find all emergency-related content
grep -r "tags:.*emergency" knowledge/
```

### Web GUI

Access the knowledge bank through a web interface:

**URL**: `http://localhost:5001/knowledge.html`

**Features**:
- 📊 **Dashboard** with tier statistics
- 🔍 **Live search** (300ms debounce)
- 🎨 **Color-coded tabs** for each tier
- 🔒 **Privacy indicators** on items
- 👁️ **View count tracking**
- 📱 **Responsive design**
- ⚡ **Real-time updates** via WebSocket

### API Endpoints

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

## Curation Guidelines

### Document Structure Template

```markdown
---
title: [Descriptive Title]
category: [survival|productivity|well-being|skills|environment|community]
subcategory: [specific subcategory]
tags: [tag1, tag2, tag3]
difficulty: [beginner|intermediate|advanced]
time-to-read: [X minutes]
last-updated: [YYYY-MM-DD]
---

# [Document Title]

## Quick Summary
[2-3 sentence overview - what will the reader learn?]

## Prerequisites
[What should reader know beforehand? Link to relevant docs]

## Main Content
[Well-structured sections with clear headings]

## Practical Application
[How to actually use this information]

## Common Mistakes
[Pitfalls to avoid]

## Troubleshooting
[Common problems and solutions]

## Further Reading
- [Related Topic 1](link.md)
- [Related Topic 2](link.md)

## Resources
[External resources, tools, or materials needed]

## Changelog
- 2025-11-14: Initial creation
```

### Writing Principles

**1. Clarity Over Cleverness**
- Use simple language
- Define technical terms
- Provide examples
- Avoid jargon unless necessary

**2. Action Over Theory**
- Focus on "how to"
- Include step-by-step instructions
- Provide practical exercises
- Show real-world applications

**3. Progressive Disclosure**
- Start with basics
- Build complexity gradually
- Use "For more advanced users..." sections
- Link to deeper dives

**4. Completeness**
- Answer obvious questions
- Include troubleshooting
- Mention limitations
- Provide context

**5. Accuracy**
- Cite sources when possible
- Update with new information
- Flag uncertainty
- Encourage critical thinking

### Quality Checklist

**Before Publishing**:
- [ ] Frontmatter complete and accurate
- [ ] Clear title and summary
- [ ] Well-structured content
- [ ] Practical examples included
- [ ] Common mistakes addressed
- [ ] Troubleshooting section
- [ ] Links tested and working
- [ ] Spelling and grammar checked
- [ ] Appropriate difficulty level
- [ ] See Also section with links
- [ ] Sources cited (if applicable)

### Curation Workflow

```
Research → Draft → Review → Publish → Maintain → Archive
```

**1. Research Phase**
- Identify knowledge gaps
- Find authoritative sources
- Evaluate multiple perspectives
- Verify information accuracy

**2. Draft Phase**
- Follow document template
- Write for target audience
- Include examples and exercises
- Add appropriate links

**3. Review Phase**
- Check for accuracy
- Test instructions
- Verify links
- Proofread for clarity

**4. Publish Phase**
- Add to appropriate category
- Update category README
- Add cross-references
- Tag appropriately

**5. Maintain Phase**
- Periodic review (6-12 months)
- Update with new information
- Fix broken links
- Improve based on feedback

**6. Archive Phase**
- Mark as historical/deprecated
- Redirect to updated content
- Preserve for reference

---

## Security

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

## Use Cases

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

## File Locations

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
    ├── productivity/
    ├── well-being/
    ├── skills/
    ├── environment/
    └── community/
```

---

## Testing

Run knowledge system tests:
```bash
pytest memory/tests/test_tier_knowledge.py -v
```

**Expected**: 11/11 passing

---

## Related Documentation

- [Command Reference](Command-Reference.md) - All uDOS commands
- [Philosophy](Philosophy.md) - The uDOS mission and values
- [Philosophy](Philosophy.md) - Complete uDOS manifesto & rationale
- [Content Curation](Content-Curation.md) - Building knowledge commons
- [Getting Started](Getting-Started.md) - Basic usage

---

**Your offline knowledge bank - from private notes to community wisdom.**

**Knowledge System**: Organized for Discovery, Curated for Quality, Designed for Human Flourishing.
