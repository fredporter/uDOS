┌────────────────────────────────────────────────────┐
│         uDOS 4-Tier Memory Architecture            │
└────────────────────────────────────────────────────┘

Memory Tier Overview
════════════════════

┌───────────────────────────────────────────────────┐
│                                                   │
│  TIER 4: KNOWLEDGE BANK (KB)                      │
│  ════════════════════════════════════════════     │
│  Global knowledge library                         │
│  Read-only, curated content                       │
│  500+ guides, 200+ diagrams                       │
│  8 categories, permanent storage                  │
│                                                   │
├───────────────────────────────────────────────────┤
│                                                   │
│  TIER 3: COMMUNITY                                │
│  ══════════════════════                           │
│  Shared across all users                          │
│  Templates, scripts, datasets                     │
│  Collaborative content                            │
│  Modifiable by community                          │
│                                                   │
├───────────────────────────────────────────────────┤
│                                                   │
│  TIER 2: SHARED                                   │
│  ═════════════                                    │
│  Single-user, multi-session                       │
│  Projects, settings, history                      │
│  Persistent across runs                           │
│  User-specific storage                            │
│                                                   │
├───────────────────────────────────────────────────┤
│                                                   │
│  TIER 1: PRIVATE                                  │
│  ═════════════                                    │
│  Current session only                             │
│  Temporary workspace                              │
│  Variables, scratch data                          │
│  Cleared on exit                                  │
│                                                   │
└───────────────────────────────────────────────────┘


Data Flow
═════════

┌─────────┐
│   KB    │  Read-only
└────┬────┘       │
     │            ▼
     │      [GUIDE|KB|topic]
     │            │
     ▼            ▼
┌─────────┐  ┌─────────┐
│COMMUNITY│  │ SHARED  │
└────┬────┘  └────┬────┘
     │            │
     │◄───────────┤ Copy/Import
     │            │
     ├───────────►│ Share/Export
     │            │
     ▼            ▼
┌─────────────────────┐
│      PRIVATE        │
│  Working Memory     │
└─────────────────────┘


Directory Structure
═══════════════════

memory/
├── private/           ← TIER 1
│   ├── session/
│   │   ├── vars.json
│   │   ├── history.log
│   │   └── scratch.txt
│   └── workspace/
│       ├── grid_data.tmp
│       └── calculations.tmp
│
├── shared/            ← TIER 2
│   ├── projects/
│   │   ├── automation/
│   │   └── analysis/
│   ├── settings/
│   │   ├── preferences.json
│   │   └── themes.json
│   └── history/
│       └── commands.log
│
├── community/         ← TIER 3
│   ├── templates/
│   │   ├── scripts/
│   │   └── dashboards/
│   ├── datasets/
│   │   ├── geography/
│   │   └── resources/
│   └── scripts/
│       └── automation/
│
└── knowledge/         ← TIER 4 (KB)
    ├── survival/
    ├── skills/
    ├── productivity/
    ├── well-being/
    ├── environment/
    ├── community/
    ├── tools/
    └── building/


Command Syntax
══════════════

PRIVATE (Tier 1):
┌──────────────────────────────────────┐
│ [PRIVATE|SET|key|value]              │
│ [PRIVATE|GET|key]                    │
│ [PRIVATE|LIST]                       │
│ [PRIVATE|CLEAR]                      │
└──────────────────────────────────────┘

SHARED (Tier 2):
┌──────────────────────────────────────┐
│ [SHARED|SET|key|value]               │
│ [SHARED|GET|key]                     │
│ [SHARED|LIST|category]               │
│ [SHARED|SAVE|filename]               │
└──────────────────────────────────────┘

COMMUNITY (Tier 3):
┌──────────────────────────────────────┐
│ [COMMUNITY|GET|path]                 │
│ [COMMUNITY|COPY|src|dest]            │
│ [COMMUNITY|LIST|category]            │
│ [COMMUNITY|SHARE|file]               │
└──────────────────────────────────────┘

KB (Tier 4):
┌──────────────────────────────────────┐
│ [KB|LIST|category]                   │
│ [KB|SEARCH|keywords]                 │
│ [KB|GET|path]                        │
│ [GUIDE|KB|topic]                     │
└──────────────────────────────────────┘


Persistence Model
═════════════════

┌─────────┬──────────┬──────────┬─────────┐
│  TIER   │ SESSION  │  SAVED   │  WRITE  │
├─────────┼──────────┼──────────┼─────────┤
│ PRIVATE │   Yes    │    No    │   Yes   │
│ SHARED  │   Yes    │   Yes    │   Yes   │
│COMMUNITY│   Yes    │   Yes    │   Yes   │
│   KB    │   Yes    │   Yes    │   No    │
└─────────┴──────────┴──────────┴─────────┘

Lifecycle:

Session Start
│
├─ PRIVATE created (empty)
├─ SHARED loaded (last session)
├─ COMMUNITY available
└─ KB mounted (read-only)
    │
    │ [Working...]
    │ PRIVATE: Temporary calculations
    │ SHARED: Save project progress
    │ COMMUNITY: Import templates
    │ KB: Reference guides
    │
Session End
│
├─ PRIVATE destroyed ✗
├─ SHARED saved ✓
├─ COMMUNITY updated ✓
└─ KB unchanged ✓


Use Case Examples
═════════════════

Daily Automation Script:
┌──────────────────────────────────────┐
│ # Get today's date                   │
│ SET today = [TIME|DATE|YYYY-MM-DD]   │
│                                      │
│ # Load tasks (SHARED tier)           │
│ SET tasks = [SHARED|GET|tasks-$today]│
│                                      │
│ # Process in PRIVATE workspace       │
│ [PRIVATE|SET|current_task|0]         │
│                                      │
│ # Reference KB guide                 │
│ [GUIDE|KB|productivity/gtd]          │
│                                      │
│ # Save results to SHARED             │
│ [SHARED|SET|completed-$today|$done]  │
└──────────────────────────────────────┘

Knowledge Exploration:
┌──────────────────────────────────────┐
│ # Search knowledge base              │
│ [KB|SEARCH|water purification]       │
│                                      │
│ # View guide                         │
│ [GUIDE|KB|survival/water/methods]    │
│                                      │
│ # Copy to personal notes (SHARED)    │
│ [KB|GET|survival/water/methods]      │
│ [SHARED|SET|notes/water|$content]    │
│                                      │
│ # Create custom checklist (PRIVATE)  │
│ [PRIVATE|SET|water_checklist|...]    │
└──────────────────────────────────────┘

Template Sharing:
┌──────────────────────────────────────┐
│ # Create automation (PRIVATE)        │
│ # ... develop script ...             │
│                                      │
│ # Save to SHARED                     │
│ [SHARED|SAVE|my-automation.uscript]  │
│                                      │
│ # Share to COMMUNITY                 │
│ [COMMUNITY|SHARE|my-automation]      │
│                                      │
│ # Others can copy                    │
│ [COMMUNITY|GET|scripts/my-automation]│
└──────────────────────────────────────┘


Memory Limits
═════════════

┌──────────┬──────────┬──────────────┐
│   TIER   │   SIZE   │   LIFETIME   │
├──────────┼──────────┼──────────────┤
│ PRIVATE  │  10 MB   │   Session    │
│ SHARED   │ 100 MB   │  Permanent   │
│COMMUNITY │   1 GB   │  Permanent   │
│   KB     │   5 GB   │  Permanent   │
└──────────┴──────────┴──────────────┘

Auto-cleanup:
  • PRIVATE: Cleared on exit
  • SHARED: Archive after 30 days
  • COMMUNITY: Manual curation
  • KB: Version controlled


Access Patterns
═══════════════

Fast Access (PRIVATE):
┌────────────────────┐
│ [PRIVATE|GET|key]  │ < 1ms
└────────────────────┘

Medium Access (SHARED/COMMUNITY):
┌────────────────────┐
│ [SHARED|GET|key]   │ < 10ms
│ [COMMUNITY|GET|p]  │ < 50ms
└────────────────────┘

Slow Access (KB):
┌────────────────────┐
│ [KB|SEARCH|query]  │ < 100ms
│ [GUIDE|KB|topic]   │ < 200ms
└────────────────────┘


Tier Selection Guide
════════════════════

Use PRIVATE when:
  ✓ Temporary calculations
  ✓ Loop variables
  ✓ Scratch workspace
  ✓ Session-specific data

Use SHARED when:
  ✓ Project files
  ✓ User preferences
  ✓ Command history
  ✓ Progress tracking

Use COMMUNITY when:
  ✓ Sharing templates
  ✓ Collaborative datasets
  ✓ Public scripts
  ✓ Community resources

Use KB when:
  ✓ Reference guides
  ✓ Learning materials
  ✓ Standard procedures
  ✓ Documentation


Data Migration
══════════════

Export from PRIVATE to SHARED:
┌────────────────────────────────────────┐
│ SET value = [PRIVATE|GET|temp_calc]    │
│ [SHARED|SET|saved_calc|$value]         │
└────────────────────────────────────────┘

Import from COMMUNITY to SHARED:
┌────────────────────────────────────────┐
│ SET template = [COMMUNITY|GET|scripts/ │
│                automation/daily.uscript]│
│ [SHARED|SET|my_daily|$template]        │
└────────────────────────────────────────┘

Reference KB in script:
┌────────────────────────────────────────┐
│ # Guide content not copied, just viewed│
│ [GUIDE|KB|skills/programming/loops]    │
│ # But can extract snippets:            │
│ SET example = [KB|GET|..../example.txt]│
│ [PRIVATE|SET|reference|$example]       │
└────────────────────────────────────────┘


Best Practices
══════════════

✓ DO:
  • Start in PRIVATE for experiments
  • Save important work to SHARED
  • Share useful tools to COMMUNITY
  • Reference KB for learning
  • Clean up PRIVATE regularly
  • Version control SHARED projects

✗ DON'T:
  • Store secrets in COMMUNITY
  • Expect PRIVATE to persist
  • Modify KB directly
  • Overload PRIVATE (10MB limit)
  • Duplicate KB content to SHARED


Related Diagrams
════════════════

• File operations   : systems/file-management.txt
• Command flow      : systems/command-pipeline.txt
• Data persistence  : data-structures/storage.txt


Guide References
════════════════

• Memory System     : ../../../knowledge/system/
                      architecture/memory-tiers.md
• KB Organization   : ../../../knowledge/KNOWLEDGE-
                      SYSTEM.md
• Data Management   : ../../../knowledge/skills/
                      productivity/data-management.md


Version: 1.0.21
Created: 2025-11-16
Screen Tier: Medium (40×60)
Format: ASCII Box Drawing
