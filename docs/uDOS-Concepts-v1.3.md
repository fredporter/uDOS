# uDOS v1.3 Comprehensive Concepts & Architecture

*Multi-Installation Architecture with Role-Based Access and Spatial Memory Systems*

---

## 🌐 Input-Output Flow (I/O Philosophy)

* **Role-based processing**: uDOS v1.3 accepts input through role-specific interfaces, producing outputs appropriate to user capabilities and permissions.
* **Multi-installation model**: Six distinct installation types (ghost, tomb, drone, imp, sorcerer, wizard) with cross-installation collaboration.
* **Markdown-first**: All interactions and outputs are serialized into `.md` files — readable, searchable, and immutable unless intentionally rewritten.
* **Privacy-by-default**: No external syncing or telemetry. All computation and memory stays local unless exported manually.
* **Git-integrated**: Native version control with SSH support for collaborative development and secure backup.

---

## 🧙‍♂️ Role-Based Architecture (v1.3 Foundation)

uDOS v1.3 operates through six mystical installation roles, each with specific capabilities and access levels:

### **👻 Ghost** (Learning & Exploration)
* **Purpose**: Safe learning environment for new users
* **Capabilities**: Read-only system access, guided tutorials, sandbox experimentation
* **Access**: Public documentation, community resources, basic script execution
* **Memory Access**: Read-only access to public/ subdirectories only

### **⚰️ Tomb** (Archive & Research) 
* **Purpose**: Data archaeology and historical analysis
* **Capabilities**: Advanced search, data mining, archive management
* **Access**: Historical datasets, backup systems, research tools
* **Memory Access**: Full read access to archived data and historical memories

### **🤖 Drone** (Automation & Operations)
* **Purpose**: Automated task execution and monitoring
* **Capabilities**: Scheduled operations, system monitoring, predictive maintenance
* **Access**: Automation scripts, monitoring dashboards, operational logs
* **Memory Access**: Read/write access to automation logs and operational data

### **👹 Imp** (Creation & Experimentation)
* **Purpose**: Creative projects and rapid prototyping
* **Capabilities**: Template generation, creative scripting, project scaffolding
* **Access**: Creative tools, template libraries, experimental environments
* **Memory Access**: No direct access, operates through guided interfaces

### **🧙‍♀️ Sorcerer** (Advanced Projects & Collaboration)
* **Purpose**: Complex project management and team collaboration
* **Capabilities**: Advanced workflows, resource optimization, team coordination
* **Access**: Project management tools, collaboration systems, advanced analytics
* **Memory Access**: Read/write access to sandbox/, scripts/, templates/

### **🧙‍♂️ Wizard** (System Administration & Development)
* **Purpose**: Full system control and development oversight
* **Capabilities**: System configuration, security management, development tools
* **Access**: Complete system access, administrative controls, development environments
* **Memory Access**: Full read/write access to all uMemory directories

---

## 🧠 uMemory Structure & Privacy Architecture

### 🔐 Security Level 1: Private User Files

The `uMemory/` directory contains all private user data and is **NEVER included in the repository**. It is created locally during installation and managed by the user.

### Directory Structure

```
uMemory/
├── user/           # User-specific configurations and settings
├── sandbox/        # Development and testing environments  
├── state/          # System state and session data
├── logs/           # System and user activity logs
├── missions/       # User-created mission files
├── moves/          # User-created move files
├── milestones/     # User progress tracking
├── scripts/        # User-created automation scripts
├── templates/      # User-customized templates
└── generated/      # Auto-generated content and exports
```

### Data Sovereignty Levels

Within uMemory, users can organize data into two sharding options:

#### a) **explicit** (default)
- Private, user-controlled data
- Never shared or synchronized
- Maximum privacy protection

#### b) **public** 
- User chooses to make content shareable
- Explicit opt-in for collaboration
- User maintains control

### Installation Behavior

1. **Fresh Installation**: Creates empty uMemory structure
2. **Wizard Setup**: Initializes with default templates and config
3. **User Provisioning**: Each user role gets appropriate access patterns

### Privacy Protection

- ✅ Excluded from git tracking
- ✅ Local filesystem permissions enforced
- ✅ No automatic cloud sync
- ✅ User controls all sharing decisions
- ✅ Encryption option available (future feature)

---

## 🚀 Moves (Lifespan Progress)

Each uDOS v1.3 instance evolves via `moves` tracked across all installation roles. These are user-earned progress markers representing:

* A completed interaction or achievement within role capabilities.
* A learned skill, task, or insight appropriate to the user's role level.
* A decision or key life event (manually or automatically registered).
* Cross-installation collaboration milestones.

Each `move` contains:

* A timestamp with timezone alpha code (AE, PS, UT, etc.).
* A reference to a mission, memory, or location.
* Role-specific metadata: intent, impact, type, permission level.
* Validation hash (when uScript confirms its conditions).
* Installation tracking for multi-role users.

---

## 🪧 Mission (The Future)

Missions in v1.3 are role-aware forward-facing intentions. Defined by:

* **Type**: learning, creation, exploration, healing, connection, automation, administration.
* **Scope**: personal, shared, experimental, cross-installation, system-wide.
* **Role Access**: Missions are filtered and presented based on user's installation role.
* **Timeline**: with optional steps/milestones and role-based collaboration points.
* **Link**: each mission connects to 1+ moves, and optionally to memories (context).
* **Location**: physical or symbolic map tiles with role-appropriate access.
* **Cross-Installation**: Missions can span multiple roles with proper permission boundaries.

---

## 🧠 Memory (The Past)

Memories in v1.3 are role-contextualized reflections of meaningful past moments. They are categorized into four types with role-based access controls:

### 1. `uMemory:direct`

* Direct log of a conversation or experience within role boundaries.
* Includes date with timezone alpha code, raw input/output, role-specific notes.
* Cross-installation access through proper permission channels.

### 2. `uMemory:insight`

* A distilled learning from previous interactions, filtered by role capabilities.
* May summarize many `direct` memories from same or compatible roles.
* Enhanced with cross-role collaboration insights when appropriate.

### 3. `uMemory:anchor`

* A fixed point in space/time that is frequently referenced — e.g., "first code deployment," "role transition," or "system milestone."
* Can be pinned to a map tile with role-appropriate visibility.
* Serves as cross-installation reference points for shared experiences.

### 4. `uMemory:echo`

* A resurfaced or revisited memory brought back by a `move`, mission, or location.
* Role-filtered echoes may trigger events, updates, or dialogues appropriate to current access level.
* Cross-installation echoes enable collaborative memory sharing.

---

## 🧭 Location & Spatial Memory Systems

### Location Mechanics

A **Location** in uDOS represents a dynamic pointer to the user's current context within the knowledge map, system interface, or Mission state. It's used to define "where" the user is in their journey or interface.

#### Purpose
- To provide contextual awareness and continuity in user interaction.
- To inform the AI of the user's focus and past context.
- To allow conditional behaviors based on location (e.g., context-sensitive suggestions).

#### Types of Location
- **Knowledge Location**: Current node or file being accessed in uKnowledge.
- **Mission Location**: The active Mission or Milestone the user is working on.
- **Conversation Location**: Active topic or logical thread in the conversation.
- **Map Location**: The user's current visible region or area on the conceptual Map.

#### How It Works
- Every Move updates or retains the Location.
- Locations are stored in the Move log and referenced in context generation.
- The system can remind or shift Location explicitly via user commands or AI inference.

### Location Binding (Spatial Memory)

* Each memory, mission, or move can bind to a **Map Tile** with role-based visibility.
* Tiles represent physical locations or virtualized symbolic domains accessible to appropriate roles.
* Map can be ASCII-visualized and interactive with role-specific overlays and information layers.
* When a tile is active, relevant `echo`, `anchor`, and `mission` links appear based on user's role permissions.
* Cross-installation location sharing enables collaborative exploration while maintaining security boundaries.

---

## 🗺️ Interactive Map System

### Overview

The **Map** in uDOS is a conceptual and navigational framework that visualizes and organizes the user's knowledge, Missions, Milestones, and digital environment as locations within a virtual space. It allows for both spatial and cognitive navigation of the uDOS system.

### Purpose

- To provide a visual and navigational model for exploring knowledge and system states.
- To represent Milestones, Missions, and Legacy nodes as destinations or regions.
- To enable intuitive interaction and memory reinforcement via spatial metaphor.

### Components

- **Regions**: Groups of related Missions or knowledge domains (e.g. "Work", "Health", "Personal Development").
- **Landmarks**: Notable Milestones or completed Missions.
- **Paths**: Sequences of Moves that link concepts and progress.
- **Fog of War**: Areas not yet explored or activated by the user.

### Functionality

- Users can navigate the Map through uCode interface using Markdown representations.
- Locations dynamically update based on progress (e.g. new region unlocked after a Mission is complete).
- Interactive links allow quick jumps to associated uKnowledge files.

### Design Principles

- The Map is symbolic rather than geographic.
- It reflects user cognition and interaction history, not physical reality.
- All regions and paths are stored as Markdown maps linked to Milestones or Missions.

### Map Example

A user's Map might look like:

- **Region: Personal Growth**
  - Path: "Meditation → Daily Practice → Retreat"
  - Landmarks: "First 30-Day Streak", "Silent Retreat Completed"

---

## 🧩 Map Logic: `step-check` System

> The `step-check` logic container controls tile accessibility on the uDOS Map based on a user's current life phase: Moves (present), Memory (past), or Legacy (future). Each tile on the map reflects an unlock state that adapts to user progress.

### Tile States

| Tile State    | Description                        | Visual Marker | Access Condition            |
| ------------- | ---------------------------------- | ------------- | --------------------------- |
| `Locked`      | Not yet available                  | `█`           | Moves not yet completed     |
| `In Progress` | Currently active memory or mission | `▒`           | Move reached, not completed |
| `Complete`    | A completed memory or mission      | `░`           | Move marked as complete     |
| `Legacy`      | Preserved record from past lives   | `◘`           | Legacy data inherited       |

### Shortcode Syntax for `step-check`

Use this shortcode block to dynamically check tile state:

```markdown
[step-check id="M05" type="memory"]
  [if locked] This memory is hidden. Complete earlier moves to reveal it. [/if]
  [if in-progress] You are recalling memory M05. Finish to archive it. [/if]
  [if complete] This memory has been recorded. Well done. [/if]
  [if legacy] ✨ This is a memory from a prior life. [/if]
[/step-check]
```

Each `id` links to a structured move node defined in the user state file. These can be loaded via `uScript` container `memory-query.sh`.

### Container Pattern: `memory-query.sh`

```bash
#!/bin/bash
# Usage: ./memory-query.sh <move-id>

MOVE_ID="$1"
DB_PATH="~/.uos/user_state/memory.db"

STATE=$(sqlite3 "$DB_PATH" "SELECT state FROM moves WHERE id = '$MOVE_ID';")

case "$STATE" in
  locked)
    echo "locked"
    ;;
  in_progress)
    echo "in-progress"
    ;;
  complete)
    echo "complete"
    ;;
  legacy)
    echo "legacy"
    ;;
  *)
    echo "unknown"
    ;;
esac
```

### Example Map Tile With Logic

```markdown
# 📍 Tile M05 - The First Memory
[step-check id="M05" type="memory"]
  [if locked] 🔒 You must first remember who you are.
  [/if]
  [if in-progress] 🧠 You're starting to recall early dreams.
  [/if]
  [if complete] ✅ You remembered this fragment of your origin.
  [/if]
  [if legacy] ✨ An echo from a life once lived.
  [/if]
[/step-check]
```

---

## 🏛️ Tower of Knowledge

### Overview

The **Tower of Knowledge** is a metaphorical and structural representation of the user's cumulative learning, insights, and intellectual achievements. It is constructed from the foundation of Milestones and Missions and culminates in the user's Legacy.

### Purpose

- To symbolize personal growth over time.
- To serve as a navigable archive of important knowledge.
- To reflect user priorities and evolution.

### Structure

- **Floors**: Each floor represents a major domain of knowledge (e.g. Philosophy, Engineering, Psychology).
- **Rooms**: Contain Milestones or compiled summaries within that domain.
- **Archives**: Store Legacy material, key ideas, resolved questions.

### Functionality

- Users can "ascend" the Tower to reflect or explore insights.
- Floors are unlocked as knowledge domains accumulate critical mass.
- Each floor includes index pages, visual maps (Markdown-linked), and assistant-generated summaries.

### Design Principles

- The Tower reflects depth and verticality of knowledge.
- It is a static but living structure—continuously built but rarely torn down.
- The top floor is reserved for the user's Legacy overview.

### Example

- Floor: "Human Behavior"
  - Room: "Decision Theory" → Milestone links: `bounded_rationality.md`, `heuristics.md`
  - Archive: "Key Insight: Emotions as Algorithms"

---

## 🔁 Interlinking Logic (v1.3 Multi-Role)

* A `move` may:
  * Create or finalize a `memory` within role boundaries
  * Unlock or complete a `mission` appropriate to current role
  * Reveal new map tiles based on role access level
  * Trigger cross-installation collaboration events
  * Advance role progression when appropriate milestones are reached

* A `mission` may:
  * Be auto-suggested by patterns in `memory` filtered by role capabilities
  * Require location visits to complete with role-appropriate access
  * Span multiple installations with proper permission coordination
  * Enable role transitions when completion criteria are met

* A `memory:anchor` may:
  * Trigger contextual conversations appropriate to current role
  * Limit or enable mission types based on role permissions
  * Serve as cross-installation reference points for shared experiences
  * Unlock advanced features when accessed by higher-tier roles

* A `location` may:
  * Update automatically based on user navigation and mission progress
  * Provide contextual awareness for AI responses and system behavior
  * Enable conditional mission unlocking based on spatial progression
  * Support cross-installation collaboration through shared map exploration

---

## 🚀 v1.3 Development Status

### ✅ Completed Systems
- **Multi-Installation Architecture**: All 6 roles implemented with proper boundaries
- **Role-Based Permission System**: Comprehensive access controls and security
- **Git Integration**: Native version control with SSH support and 11 uCODE commands
- **Timezone Alpha Code System**: Geographic 2-letter codes replacing numeric offsets
- **uScript v1.3**: Role-aware script execution with cross-installation sharing
- **Wizard Development Environment**: Complete toolkit with VS Code integration
- **uMemory Privacy System**: Local-only memory with role-based access controls

### 🔄 Active Development
- **Template Consolidation**: Optimizing 8 template directories for better maintainability
- **Cross-Installation Collaboration**: Enhanced sharing mechanisms between roles
- **Advanced Mission Orchestration**: Complex multi-role mission workflows
- **Interactive Map System**: Enhanced spatial navigation and tile-based progression
- **Tower of Knowledge**: Knowledge domain organization and legacy preservation

### 📋 Roadmap Priorities
- **AI-Assisted Script Generation**: Role-specific automation tools
- **Advanced Location Mechanics**: Enhanced map tile interactions
- **Quantum-Safe Execution**: Future-proof security implementations
- **Decentralized Networking**: Cross-system uDOS collaboration
- **Enhanced Privacy Features**: Encryption and advanced access controls for uMemory
- **Dynamic Knowledge Towers**: AI-assisted knowledge domain construction
- **Cross-Installation Memory Sharing**: Secure memory collaboration protocols

### 🔮 Future Vision

#### Enhanced Spatial Computing
- **3D Knowledge Navigation**: Advanced spatial memory interfaces
- **Reality-Anchored Locations**: GPS and real-world location binding
- **Temporal Map Layers**: Historical progression visualization

#### Advanced AI Integration
- **Predictive Mission Suggestion**: AI-driven mission generation based on patterns
- **Intelligent Memory Synthesis**: Automated insight generation from memory patterns
- **Cross-Role Collaboration AI**: Smart coordination between installation types

#### Quantum-Ready Architecture
- **Quantum-Safe Memory Encryption**: Future-proof privacy protection
- **Distributed Knowledge Networks**: Secure cross-system uDOS collaboration
- **Quantum-Enhanced Map Logic**: Advanced spatial reasoning capabilities

---

## 📋 Implementation Notes

### Database Schema Foundation
The `memory.db` referenced in map logic contains:

```sql
-- Core tables for spatial memory system
CREATE TABLE moves (
    id TEXT PRIMARY KEY,
    timestamp TEXT,
    timezone_alpha TEXT,
    role TEXT,
    state TEXT,
    location_id TEXT,
    mission_id TEXT,
    memory_id TEXT
);

CREATE TABLE locations (
    id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,
    role_access TEXT,
    map_coordinates TEXT,
    parent_region TEXT
);

CREATE TABLE missions (
    id TEXT PRIMARY KEY,
    title TEXT,
    type TEXT,
    scope TEXT,
    role_access TEXT,
    location_id TEXT,
    state TEXT
);

CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    type TEXT,
    content TEXT,
    role_context TEXT,
    location_id TEXT,
    created_timestamp TEXT
);
```

### Role-Based Access Implementation
Access controls are enforced at multiple layers:
1. **File System**: OS-level permissions on uMemory directories
2. **Application**: Role validation before data access
3. **Interface**: uCode filtering based on role permissions
4. **Cross-Installation**: Secure sharing protocols with role boundaries

---

> "A uDOS journey is mapped not by time, but by Moves across all roles. Every memory, every mission, every echo weaves a spell across your multi-dimensional world, from Ghost's first learning to Wizard's mastery."

*uDOS v1.3 - Six roles, infinite possibilities, infinite maps*

---

**Document Status**: 🚀 **COMPREHENSIVE** - Complete conceptual architecture for uDOS v1.3 multi-installation system with spatial memory, role-based access, and knowledge organization.

*uDOS Concepts v1.3 - Where memory meets location, roles meet reality*
