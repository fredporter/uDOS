# Memory Folder

**Purpose**: Your personal planet workspace with 4-tier security, mission lifecycle management, and permanent storage for all user-generated content.

---

## v1.5.0: Flattened Structure & Planet System

The `/memory` folder has been reorganized with a **flatter, clearer structure** and renamed "workspace" to "planet":

### Key Changes (v1.5.0)
- ✅ **Flattened hierarchy**: Removed nested `/config`, `/user`, `/templates` folders
- ✅ **Workspace → Planet**: Renamed to align with universe/galaxy/solar system metaphor
- ✅ **Configuration in .env**: User settings moved from user.json to .env
- ✅ **Default role: admin**: All users have write access to /memory by default
- ✅ **Sandbox for drafts**: `/sandbox` is your workspace for development and experiments
- ✅ **Universe data**: Planet system linked to knowledge/system/universe.json (Sol system)

### Current Structure (15 folders)
```
memory/
├── user/                       # 👤 USER DATA FILES
│   ├── USER.UDT                # Command aliases & preferences
│   ├── planets.json            # Multi-planet configurations
│   ├── knowledge.db            # Knowledge search index (SQLite)
│   └── xp.db                   # XP/progression database (SQLite)
│
├── sandbox/                    # 🔧 DRAFTS & DEVELOPMENT
│   ├── drafts/                 # Documents in progress
│   ├── experiments/            # Testing, prototypes, trials
│   ├── tools/                  # Custom scripts
│   └── templates/              # User templates (moved from /templates)
│
├── planet/                     # 🌍 PLANET WORKSPACE (was /workspace)
│   └── [planet-specific files] # Earth, Mars, etc.
│
├── workflow/                   # 📋 MISSION LIFECYCLE
│   ├── active/                 # Current missions
│   ├── completed/              # Finished missions
│   └── archived/               # Historical missions
│
├── private/                    # 🔐 TIER 1: AES-256 encrypted (user-only, 100MB)
├── shared/                     # 🔒 TIER 2: AES-128 encrypted (team, 500MB)
├── groups/                     # 📂 TIER 3: Community knowledge (1GB)
├── public/                     # 🌐 TIER 4: World-readable (5GB)
│
├── logs/                       # All system logs (flat structure - no subdirectories)
│   ├── session_*.log          # Session activity logs
│   ├── *_server.log           # API/extension server logs
│   ├── audit.log, audit.json  # Audit trail
│   ├── bug_reports.jsonl      # User feedback
│   └── *.db                   # Command/file access history
├── sessions/                   # Session history and replays
├── modules/                    # User uCode modules and stdlib
├── barter/                     # Trading system data
├── scenarios/                  # Survival scenarios
├── missions/                   # Mission templates
└── themes/                     # User theme customizations
```

---

## v1.1.2: 4-Tier Memory System

The `/memory` folder implements a **4-tier security architecture** with encryption and access controls:

### Tier 1 - Private 🔐
- **Encryption**: AES-256 with Fernet
- **Access**: User-only (single user)
- **Quota**: 100MB
- **Use**: Sensitive personal data, credentials, private notes
- **Location**: `memory/private/`

### Tier 2 - Shared 🔒
- **Encryption**: AES-128
- **Access**: Team collaboration (trusted users)
- **Quota**: 500MB
- **Use**: Team documents, shared projects, collaboration
- **Location**: `memory/shared/`

### Tier 3 - Community 📂
- **Encryption**: None (plain text)
- **Access**: Group knowledge sharing
- **Quota**: 1GB
- **Use**: Community knowledge, public notes, guides
- **Location**: `memory/community/` or `memory/groups/`

### Tier 4 - Public 🌐
- **Encryption**: None (plain text)
- **Access**: World-readable
- **Quota**: 5GB
- **Use**: Public knowledge base, published content
- **Location**: `memory/public/`

**Commands**:
```bash
memory tier           # Show tier structure
memory encrypt <file> # Encrypt file (moves to Tier 1)
memory decrypt <file> # Decrypt file
file list --tier 1    # List Private tier files
```

---

## The uDOS Way

The `/memory` folder is the **only** location for user file actions. Everything else in uDOS is read-only system content.

### Core Principles

1. **Work in sandbox** - All temporary operations, testing, drafts (sandbox/drafts/, sandbox/experiments/)
2. **Choose your planet** - Switch between Earth, Mars, or other solar system planets (see knowledge/system/universe.json)
3. **Choose security tier** - Select appropriate tier for content sensitivity (private/shared/groups/public)
4. **Commit to workflow** - Move validated work through mission lifecycle (workflow/active → completed → archived)
5. **Never touch /knowledge** - That's read-only system content distributed with uDOS
6. **Default permissions** - All users have admin role with full write access to /memory

### Planet System

Your workspace is organized by **planet** - defaulting to Earth in the Sol system:
- **Current planet**: Stored in `current_planet.json` and `.env` (UDOS_CURRENT_PLANET)
- **Planet data**: `planets.json` for multi-planet configurations
- **Universe reference**: `knowledge/system/universe.json` contains Sol system with all 8 planets
- **Switch planets**: Use planet commands to change your active workspace context

---

## Removed Folders (v1.5.0 Cleanup)

These folders have been **removed or consolidated**:
- ❌ `/config` → Files moved to memory root
- ❌ `/user` → USER.UDT and templates moved to root
- ❌ `/templates` → Moved to `/sandbox/templates`
- ❌ `/workspace` → Renamed to `/planet`
- ❌ `/personal` → Empty, removed (use /sandbox or /private)
- ❌ `/legacy` → Empty, removed (use /workflow/archived)
- ❌ `/system` → Empty, removed
- ❌ `/tests` → Empty, removed (dev tests are in /dev/tests)

---

## Structure (Legacy v1.1.2 - Deprecated)

```
memory/
├── private/             # TIER 1: AES-256 encrypted (user-only, 100MB)
│   └── [encrypted files]
│
├── shared/              # TIER 2: AES-128 encrypted (team, 500MB)
│   └── [encrypted team files]
│
├── community/           # TIER 3: Plain text (group, 1GB)
│   └── [community knowledge]
│
├── public/              # TIER 4: Plain text (world-readable, 5GB)
│   └── [public content]
│
├── sandbox/             # TEMPORARY workspace
│   ├── drafts/          # Documents in development
│   ├── experiments/     # Testing, prototypes, trials
│   └── temp/            # Disposable scratch work
│
├── workflow/            # ACTIVE work (mission lifecycle)
│   ├── active/          # Current missions and milestones
│   │   └── [mission]/
│   │       ├── mission.md         # Mission brief and goals
│   │       ├── milestones/        # Tracked progress checkpoints
│   │       └── resources/         # Working materials
│   ├── completed/       # Finished missions (ready for archive)
│   └── archived/        # Historical missions (reference only)
│
├── legacy/              # PERMANENT outcomes and knowledge
│   ├── outcomes/        # Deliverables, achievements, artifacts
│   ├── learnings/       # Insights, lessons, discoveries
│   └── resources/       # Curated tools, references, templates
│
├── personal/            # Personal content
│   ├── notes/           # Personal notes and journals
│   ├── projects/        # Side projects and experiments
│   ├── research/        # Personal research and studies
│   └── stories/         # Creative writing and narratives
│
├── workspace/           # Organized working areas
│   ├── drafts/          # Documents in progress
│   ├── experiments/     # Testing and trials
│   └── tools/           # User-created scripts and utilities
│
├── tests/               # Test suites (1,062 tests - tracked in git)
├── modules/             # uDOS extension modules
├── themes/              # Custom user themes
├── config/              # User configuration files (RBAC roles, etc.)
├── logs/                # Session logs and history
│
├── missions/            # Legacy mission storage (deprecated - use workflow/)
├── scenarios/           # Game/story scenarios
├── groups/              # User groups and teams (Community tier)
│
├── .metadata/           # System metadata (hidden)
├── knowledge.db         # User knowledge database
├── xp.db                # Experience tracking database
└── README.md            # This file
```

---

## Workflow: The uDOS Way

### Mission → Milestone → Outcome

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MISSION STARTED                                          │
│    Create in: memory/workflow/active/[mission-name]/       │
│    Files:     mission.md (goals, context, success criteria)│
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. MILESTONES TRACKED                                       │
│    Create in: memory/workflow/active/[mission]/milestones/ │
│    Files:     01-research.md, 02-prototype.md, etc.        │
│    Purpose:   Break mission into trackable checkpoints     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. WORK IN SANDBOX                                          │
│    Location:  memory/sandbox/                               │
│    Purpose:   Draft, test, experiment without commitment   │
│    Files:     Temporary, disposable, untracked             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. COMMIT TO MISSION                                        │
│    Move from: memory/sandbox/                               │
│    Move to:   memory/workflow/active/[mission]/resources/  │
│    Action:    Validate, review, commit work                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. MISSION COMPLETED                                        │
│    Move from: memory/workflow/active/[mission]/             │
│    Move to:   memory/workflow/completed/[mission]/         │
│    Action:    Mark mission done, ready for archival        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. EXTRACT LEGACY                                           │
│    Outcomes:  → memory/legacy/outcomes/                     │
│    Learnings: → memory/legacy/learnings/                    │
│    Resources: → memory/legacy/resources/                    │
│    Purpose:   Preserve valuable knowledge beyond mission   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. ARCHIVE MISSION                                          │
│    Move from: memory/workflow/completed/[mission]/         │
│    Move to:   memory/workflow/archived/[mission]/          │
│    Purpose:   Historical reference, long-term storage      │
└─────────────────────────────────────────────────────────────┘
```

---

## Usage Patterns

### Starting New Work

```bash
# Create mission
🔮 > MISSION CREATE "knowledge-reorganization"

# Work in sandbox
🔮 > EDIT memory/sandbox/draft-structure.md

# Test and iterate
🔮 > RUN memory/sandbox/test-script.sh

# When ready, commit to mission
🔮 > COMMIT memory/sandbox/draft-structure.md TO workflow/active/knowledge-reorganization/resources/
```

### Tracking Progress

```bash
# View active missions
🔮 > CATALOG memory/workflow/active/

# Update milestone
🔮 > EDIT memory/workflow/active/knowledge-reorganization/milestones/01-analysis.md

# Mark milestone complete
🔮 > MILESTONE COMPLETE knowledge-reorganization 01-analysis
```

### Completing Missions

```bash
# Mark mission complete
🔮 > MISSION COMPLETE knowledge-reorganization

# Extract outcomes
🔮 > COPY memory/workflow/completed/knowledge-reorganization/final-report.md TO memory/legacy/outcomes/

# Extract learnings
🔮 > COPY memory/workflow/completed/knowledge-reorganization/lessons.md TO memory/legacy/learnings/

# Archive mission
🔮 > MISSION ARCHIVE knowledge-reorganization
```

### Sandbox Workflow

```bash
# Work freely in sandbox
🔮 > EDIT memory/sandbox/idea.md
🔮 > TEST memory/sandbox/prototype.py

# Review sandbox contents
🔮 > CATALOG memory/sandbox/

# Commit validated work
🔮 > EMPTY_SANDBOX  # Reviews and commits to appropriate location

# OR selectively commit
🔮 > COMMIT memory/sandbox/validated-script.py TO memory/workspace/tools/
```

---

## Folder Guidelines

### sandbox/

**Purpose:** Temporary workspace for all draft work, testing, and experiments

**Rules:**
- Nothing here is permanent
- Can be cleared at any time
- Not tracked in git (add to .gitignore if desired)
- Use freely without worry

**Good for:**
- Draft documents
- Testing scripts
- Experimental ideas
- Quick notes
- Disposable work

### workflow/active/

**Purpose:** Current missions with defined goals and tracked progress

**Structure per mission:**
```
workflow/active/[mission-name]/
├── mission.md              # Mission brief (goals, context, success criteria)
├── milestones/             # Tracked checkpoints
│   ├── 01-milestone.md
│   ├── 02-milestone.md
│   └── ...
└── resources/              # Working materials, references, tools
```

**Rules:**
- One folder per mission
- mission.md defines the mission
- milestones/ tracks progress
- resources/ holds working files
- Move to completed/ when done

### workflow/completed/

**Purpose:** Finished missions ready for legacy extraction and archival

**Process:**
1. Mission marked complete
2. Extract outcomes → legacy/outcomes/
3. Extract learnings → legacy/learnings/
4. Extract resources → legacy/resources/
5. Archive entire mission → workflow/archived/

### workflow/archived/

**Purpose:** Historical missions for reference only

**Rules:**
- Read-only reference
- Organized by completion date or category
- Searchable for past work
- Never modified (historical record)

### legacy/outcomes/

**Purpose:** Deliverables, achievements, and artifacts from completed missions

**Examples:**
- Final reports
- Published documents
- Completed tools/scripts
- Finished projects
- Successful implementations

### legacy/learnings/

**Purpose:** Insights, lessons, and discoveries extracted from missions

**Examples:**
- What worked/didn't work
- Key insights
- Mistakes and how to avoid
- Best practices discovered
- Knowledge gained

### legacy/resources/

**Purpose:** Curated tools, templates, and references for future use

**Examples:**
- Reusable scripts
- Document templates
- Reference materials
- Useful patterns
- Tools worth keeping

### personal/

**Purpose:** Personal content not tied to missions

**Subdirs:**
- notes/ - Personal journals, thoughts, ideas
- projects/ - Side projects and experiments
- research/ - Personal studies and research
- stories/ - Creative writing and narratives

**Rules:**
- Moved from knowledge/ (which is read-only system content)
- User-specific content only
- Organize as desired
- Not mission-related

### workspace/

**Purpose:** General organized working areas

**Subdirs:**
- drafts/ - Documents in progress
- experiments/ - Testing and trials
- tools/ - User-created scripts and utilities

**Difference from sandbox:**
- Workspace is organized, committed work
- Sandbox is temporary, disposable
- Move from sandbox → workspace when validated

---

## System vs User Content

### Read-Only (DO NOT EDIT)

```
/knowledge/     # System knowledge library (distributed with uDOS)
/core/          # uDOS system code
/extensions/    # uDOS extensions and plugins
/docs/          # uDOS documentation
/wiki/          # uDOS wiki
```

### User Workspace (YOUR DOMAIN)

```
/memory/        # ALL user-generated content lives here
```

### System Scripts vs User Scripts

**System scripts** (in `/core/utils/`):
- Part of uDOS core functionality
- Maintained by uDOS developers
- Distributed with uDOS releases
- Examples: config_manager.py, generate_world_map.uscript, reorganize_knowledge.sh

**User scripts** (in `/memory/workspace/tools/`):
- Created by you for your workflow
- Personal utilities and automation
- Mission-specific tools
- Experimental scripts

---

## Commands Reference

### Mission Management

```bash
MISSION CREATE <name>           # Start new mission
MISSION LIST                    # Show active missions
MISSION COMPLETE <name>         # Mark mission done
MISSION ARCHIVE <name>          # Archive completed mission
MILESTONE ADD <mission> <name>  # Add milestone to mission
MILESTONE COMPLETE <mission> <milestone>  # Mark milestone done
```

### Sandbox Operations

```bash
EMPTY_SANDBOX                   # Review and commit sandbox work
CATALOG memory/sandbox/         # List sandbox contents
CLEAR_SANDBOX                   # Delete all sandbox files (careful!)
```

### File Operations

```bash
CATALOG memory/                 # List all memory contents
EDIT memory/sandbox/draft.md    # Edit file in sandbox
LOAD memory/legacy/outcome.md   # Load file from legacy
COMMIT <file> TO <destination>  # Move validated work from sandbox
```

---

## Git Tracking

**Tracked:**
- workflow/active/
- workflow/completed/
- workflow/archived/
- legacy/
- personal/
- workspace/
- config/

**Not tracked (recommended .gitignore):**
- sandbox/
- logs/
- .metadata/
- *.db

---

## Best Practices

### The uDOS Way

1. **Always start in sandbox** - Test, draft, experiment freely
2. **Commit when validated** - Move to workflow or workspace when ready
3. **Track missions properly** - Use mission.md and milestones
4. **Extract legacy** - Don't lose valuable learnings in archives
5. **Keep it organized** - Use the folder structure intentionally
6. **Archive completed work** - Keep active/ clean and focused

### Anti-Patterns (Avoid)

❌ Editing files in /knowledge/ (it's read-only)
❌ Skipping sandbox (committing unvalidated work)
❌ Leaving missions in active/ forever (complete or archive them)
❌ Not extracting legacy (losing insights in archived missions)
❌ Creating new top-level folders (use the structure)
❌ Mixing personal and mission content

### Migration Path

**If you have content in wrong places:**

```bash
# Move from knowledge to memory
mv knowledge/personal memory/

# Move system scripts to core
mv scripts/*.py core/utils/

# Move user scripts to workspace
mv my-scripts/* memory/workspace/tools/

# Organize existing work into missions
mkdir memory/workflow/active/my-mission/
mv old-project/* memory/workflow/active/my-mission/resources/
```

---

**Last Updated:** v1.0.21 (November 2024)
**Structure:** Mission lifecycle workflow, sandbox → commit → archive → legacy
**Philosophy:** Everything user-generated lives in /memory. Everything else is read-only.
