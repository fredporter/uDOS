# uDOS Knowledge Linking System (v1.0.0.53)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Author:** uDOS Engineering

The uDOS knowledge system uses **self-indexing documents** that declare their own relationships, tags, and locations. No manual index maintenance required - the knowledge graph builds itself from document frontmatter.

---

## Document Schema (.udos.md)

### Complete Frontmatter Specification

```yaml
---
# Identity
id: "kb_survival_fire_001" # Unique document ID
title: "Fire Starting Methods" # Human-readable title
type: guide # guide | checklist | reference | workflow | tutorial
version: "1.2.0" # Semantic version

# Lifecycle
status: published # draft | submitted | published | archived | deprecated
created: "2026-01-01T10:00:00Z" # Creation timestamp
updated: "2026-01-24T10:30:00Z" # Last modification
published: "2026-01-05T12:00:00Z" # When published

# Authorship & Permissions
author:
  id: "user_abc123"
  name: "Alice"
  rank: contributor # novice | contributor | expert | wizard | system

contributors:
  - id: "user_def456"
    name: "Bob"
    contribution: "Added hand drill section"
    date: "2026-01-03"

permissions:
  edit: contributors # author | contributors | experts | wizards | system
  suggest: all # Who can suggest changes
  fork: all # Who can create derivatives

# Quality & Trust
quality:
  score: 4.2 # 0.0 - 5.0 aggregate score
  votes: 47 # Number of ratings
  verified: true # Expert-verified content
  verified_by: "wizard_expert_001" # Who verified
  verified_date: "2026-01-04"

trust:
  citations: 3 # Times cited by other documents
  usage_count: 1250 # Times accessed
  report_count: 0 # Abuse/error reports

# Categorization
tags:
  primary: [survival, fire] # Main topic tags
  secondary: [wilderness, emergency] # Related topics
  skill_level: intermediate # beginner | intermediate | advanced
  time_required: "30min" # Estimated time

categories:
  - survival/fire
  - emergency/warmth
  - skills/primitive

# Linking (Graph Relationships)
links:
  requires: # Prerequisites
    - id: "kb_survival_basics_001"
      title: "Survival Basics"

  related: # Related content
    - id: "kb_survival_shelter_001"
      title: "Building Emergency Shelter"
    - id: "kb_survival_water_001"
      title: "Finding Water"

# Geo-Tagging
location:
  binding: optional # none | optional | required | exclusive
  tiles:
    - coord: "L300:BD14-CG15"
      type: origin
      name: "Author's location"

# Executable Content
executable: true
runtime:
  requires: [core]
  sandbox: true

actions:
  - name: "start_fire_checklist"
    type: checklist
---
```

---

## Document Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT LIFECYCLE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐     ┌───────────┐     ┌───────────┐     ┌──────────┐ │
│  │  DRAFT   │────▶│ SUBMITTED │────▶│ PUBLISHED │────▶│ ARCHIVED │ │
│  └──────────┘     └───────────┘     └───────────┘     └──────────┘ │
│       │                 │                 │                 │       │
│       ▼                 ▼                 ▼                 ▼       │
│   Local only      Community         Global            Historical   │
│   Sandbox         Review            Knowledge         Reference    │
│   No indexing     Pending           Self-indexed      Read-only    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Status Definitions

| Status       | Location                | Indexed         | Editable           | Visible To              |
| ------------ | ----------------------- | --------------- | ------------------ | ----------------------- |
| `draft`      | `memory/drafts/`        | No              | Author only        | Author                  |
| `submitted`  | `memory/contributions/` | No              | Author + Reviewers | Reviewers               |
| `published`  | `knowledge/`            | Yes             | Per permissions    | Everyone                |
| `archived`   | `knowledge/.archive/`   | Historical only | No                 | Everyone                |
| `deprecated` | In-place                | Warns users     | No                 | Everyone (with warning) |

---

## User Ranks & Permissions

### Rank Hierarchy

| Rank          | Trust Level | Permissions                  |
| ------------- | ----------- | ---------------------------- |
| `novice`      | 0-10        | Create drafts, suggest edits |
| `contributor` | 11-50       | Publish personal, vote       |
| `expert`      | 51-100      | Verify content, approve      |
| `wizard`      | 101+        | Full edit, archive, moderate |
| `system`      | ∞           | Core knowledge, system docs  |

---

## Self-Indexing Mechanism

### No Manual Index Required

Documents declare their relationships in frontmatter. The system builds the knowledge graph dynamically:

```python
def build_knowledge_graph():
    graph = KnowledgeGraph()

    for doc in scan_documents("knowledge/**/*.udos.md"):
        meta = parse_frontmatter(doc)

        # Add node
        graph.add_node(
            id=meta.id,
            title=meta.title,
            tags=meta.tags,
            categories=meta.categories,
            quality=meta.quality.score
        )

        # Add edges (relationships)
        for link in meta.links.requires:
            graph.add_edge(meta.id, link.id, type="requires")
        for link in meta.links.related:
            graph.add_edge(meta.id, link.id, type="related")

    return graph
```

### Query Examples

```python
# Find all fire-related documents
results = graph.query(tags__contains="fire")

# Find documents at a location
results = graph.query(location__tile="L300:BD14-CG15")

# Find prerequisites for a document
prereqs = graph.traverse(doc_id, edge_type="requires", direction="out")

# Find documents that cite this one
citations = graph.traverse(doc_id, edge_type="related", direction="in")
```

---

## Quality & Trust System

### Quality Score Components

```python
quality_score = weighted_average(
    user_ratings=0.4,        # Community votes (1-5)
    expert_review=0.3,       # Expert/wizard score
    completeness=0.15,       # Document completeness
    freshness=0.1,           # How recently updated
    citations=0.05           # Referenced by other docs
)
```

### Verification Badges

| Badge                 | Requirement           | Display   |
| --------------------- | --------------------- | --------- |
| ⭐ Community Favorite | Score ≥4.5, votes ≥50 | Gold star |
| ✓ Expert Verified     | Reviewed by expert+   | Checkmark |
| 🏛️ System Official    | System-authored       | Shield    |
| 📍 Location Verified  | GPS-confirmed content | Pin       |
| 🆕 Recently Updated   | Updated <7 days       | "New" tag |

---

## File System Structure

```
uDOS/
├── knowledge/                      # [GLOBAL] Published knowledge
│   ├── survival/
│   │   ├── fire-starting.udos.md   # status: published
│   │   └── water-finding.udos.md
│   ├── medical/
│   │   └── first-aid.udos.md
│   └── .archive/                   # Archived documents
│       └── old-fire-guide.udos.md
│
├── memory/                         # [USER] Local workspace
│   ├── drafts/                     # Work in progress
│   │   └── my-new-guide.udos.md
│   │
│   ├── contributions/              # Submitted for review
│   │   └── improved-fire.udos.md
│   │
│   └── library/                    # Personal knowledge collection
│       ├── imported/               # Forked from global
│       └── original/               # My own creations
```

---

## Related Documentation

- [UDOS-MD-FORMAT.md](UDOS-MD-FORMAT.md) — Executable document format
- [LAYER-ARCHITECTURE.md](LAYER-ARCHITECTURE.md) — Spatial coordinate system
- [DATABASE-ARCHITECTURE.md](DATABASE-ARCHITECTURE.md) — Data indexing
- [../../docs/development-streams.md](../../docs/development-streams.md) — Implementation roadmap

---

**Status:** Active Architecture Standard
**Repository:** https://github.com/fredporter/uDOS
