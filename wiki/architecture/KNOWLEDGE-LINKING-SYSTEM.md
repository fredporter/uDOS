# uDOS Knowledge Linking System (v1.0.0.52)

## Overview

The uDOS knowledge system uses **self-indexing documents** that declare their own relationships, tags, and locations. No manual index maintenance required - the knowledge graph builds itself from document frontmatter.

---

## Document Schema (.udos.md)

### Complete Frontmatter Specification

```yaml
---
# ═══════════════════════════════════════════════════════════════════
# IDENTITY
# ═══════════════════════════════════════════════════════════════════
id: "kb_survival_fire_001"           # Unique document ID (auto-generated if omitted)
title: "Fire Starting Methods"        # Human-readable title
type: guide                           # guide | checklist | reference | workflow | tutorial
version: "1.2.0"                      # Semantic version of this document

# ═══════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════════
status: published                     # draft | submitted | published | archived | deprecated
created: "2026-01-01T10:00:00Z"       # Creation timestamp
updated: "2026-01-06T14:30:00Z"       # Last modification
published: "2026-01-05T12:00:00Z"     # When published to global knowledge

# ═══════════════════════════════════════════════════════════════════
# AUTHORSHIP & PERMISSIONS
# ═══════════════════════════════════════════════════════════════════
author:
  id: "user_abc123"                   # Author's unique ID
  name: "Alice"                       # Display name
  rank: contributor                   # novice | contributor | expert | wizard | system
  
contributors:                         # Additional contributors (wiki-style)
  - id: "user_def456"
    name: "Bob"
    contribution: "Added hand drill section"
    date: "2026-01-03"
    
permissions:
  edit: contributors                  # author | contributors | experts | wizards | system
  suggest: all                        # Who can suggest changes
  fork: all                           # Who can create derivatives

# ═══════════════════════════════════════════════════════════════════
# QUALITY & TRUST
# ═══════════════════════════════════════════════════════════════════
quality:
  score: 4.2                          # 0.0 - 5.0 aggregate score
  votes: 47                           # Number of ratings
  verified: true                      # Expert-verified content
  verified_by: "wizard_expert_001"    # Who verified
  verified_date: "2026-01-04"
  
trust:
  citations: 3                        # Times cited by other documents
  usage_count: 1250                   # Times accessed
  report_count: 0                     # Abuse/error reports

# ═══════════════════════════════════════════════════════════════════
# CATEGORIZATION (Self-Indexing Tags)
# ═══════════════════════════════════════════════════════════════════
tags:
  primary: [survival, fire]           # Main topic tags
  secondary: [wilderness, emergency]  # Related topics
  skill_level: intermediate           # beginner | intermediate | advanced | expert
  time_required: "30min"              # Estimated time to complete/read
  
categories:                           # Hierarchical categories (auto-index)
  - survival/fire
  - emergency/warmth
  - skills/primitive

# ═══════════════════════════════════════════════════════════════════
# LINKING (Graph Relationships)
# ═══════════════════════════════════════════════════════════════════
links:
  requires:                           # Prerequisites (must read first)
    - id: "kb_survival_basics_001"
      title: "Survival Basics"
      
  related:                            # Related content (see also)
    - id: "kb_survival_shelter_001"
      title: "Building Emergency Shelter"
    - id: "kb_survival_water_001"
      title: "Finding Water"
      
  extends:                            # This extends/builds on
    - id: "kb_survival_fire_intro"
      title: "Introduction to Fire"
      
  supersedes:                         # This replaces older content
    - id: "kb_fire_old_001"
      deprecated: true
      
  children:                           # Sub-documents (sections)
    - id: "kb_survival_fire_001_friction"
      title: "Friction Methods"
    - id: "kb_survival_fire_001_spark"
      title: "Spark Methods"

# ═══════════════════════════════════════════════════════════════════
# GEO-TAGGING (Location Binding)
# ═══════════════════════════════════════════════════════════════════
location:
  binding: optional                   # none | optional | required | exclusive
  
  tiles:                              # Linked tile coordinates
    - coord: "L300:BD14-CG15"
      type: origin                    # origin | relevant | waypoint
      name: "Author's location"
      
    - coord: "L300:AA10-BT21"
      type: relevant
      name: "Known fire-starting area"
      
  regions:                            # Broader area relevance
    - name: "Northern Hemisphere"
      relevance: high
    - name: "Tropical"
      relevance: low
      note: "Different techniques needed"

# ═══════════════════════════════════════════════════════════════════
# EXECUTABLE CONTENT
# ═══════════════════════════════════════════════════════════════════
executable: true                      # Contains runnable code blocks
runtime:
  requires: [core]                    # Required extensions
  sandbox: true                       # Run in sandbox mode
  
actions:                              # Defined actions in document
  - name: "start_fire_checklist"
    type: checklist
  - name: "calculate_materials"
    type: script

# ═══════════════════════════════════════════════════════════════════
# OVERLAY HINTS
# ═══════════════════════════════════════════════════════════════════
overlay:
  include_in:                         # Suggest for these overlays
    - "emergency_kit"
    - "wilderness_survival"
    - "camping_basics"
  exclude_from:                       # Don't show in these contexts
    - "urban_only"
    - "beginner_safe"
---

# Fire Starting Methods

Document content here...
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
│       │                 │                 │                 │       │
│       ▼                 ▼                 ▼                 ▼       │
│   Local only      Community         Global            Historical   │
│   Sandbox         Review            Knowledge         Reference    │
│   No indexing     Pending           Self-indexed      Read-only    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Status Definitions

| Status | Location | Indexed | Editable | Visible To |
|--------|----------|---------|----------|------------|
| `draft` | `memory/drafts/` | No | Author only | Author |
| `submitted` | `memory/contributions/` | No | Author + Reviewers | Reviewers |
| `published` | `knowledge/` | Yes (global) | Per permissions | Everyone |
| `archived` | `knowledge/.archive/` | Historical only | No | Everyone |
| `deprecated` | In-place | Warns users | No | Everyone (with warning) |

### Lifecycle Transitions

```python
# Draft → Submitted
SUBMIT document.udos.md
# Requires: status=draft, author validation

# Submitted → Published (requires approval)
APPROVE document.udos.md
# Requires: wizard/expert permission, quality threshold met

# Published → Archived
ARCHIVE document.udos.md
# Requires: wizard permission or superseded by newer

# Any → Deprecated
DEPRECATE document.udos.md SUPERSEDED_BY new_document.udos.md
# Adds warning, updates links
```

---

## User Ranks & Permissions

### Rank Hierarchy

| Rank | Trust Level | Permissions |
|------|-------------|-------------|
| `novice` | 0-10 | Create drafts, suggest edits |
| `contributor` | 11-50 | Publish to personal overlay, vote |
| `expert` | 51-100 | Verify content, approve submissions |
| `wizard` | 101+ | Full edit, archive, moderate |
| `system` | ∞ | Core knowledge, system documents |

### Trust Score Calculation

```python
trust_score = (
    (documents_published * 5) +
    (edits_accepted * 2) +
    (quality_votes_received * 0.5) +
    (citations_received * 3) -
    (reports_against * 10)
)
```

### Permission Matrix

| Action | Novice | Contributor | Expert | Wizard | System |
|--------|--------|-------------|--------|--------|--------|
| Create draft | ✅ | ✅ | ✅ | ✅ | ✅ |
| Submit for review | ✅ | ✅ | ✅ | ✅ | ✅ |
| Publish to personal | ❌ | ✅ | ✅ | ✅ | ✅ |
| Publish to global | ❌ | ❌ | ✅ | ✅ | ✅ |
| Approve submissions | ❌ | ❌ | ✅ | ✅ | ✅ |
| Edit published | ❌ | ❌ | Own | All | All |
| Archive/deprecate | ❌ | ❌ | ❌ | ✅ | ✅ |
| Verify content | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## Self-Indexing Mechanism

### No Manual Index Required

Documents declare their relationships in frontmatter. The system builds the knowledge graph dynamically:

```python
# On startup or document change:
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
            location=meta.location,
            quality=meta.quality.score
        )
        
        # Add edges (relationships)
        for link in meta.links.requires:
            graph.add_edge(meta.id, link.id, type="requires")
        for link in meta.links.related:
            graph.add_edge(meta.id, link.id, type="related")
        for link in meta.links.extends:
            graph.add_edge(meta.id, link.id, type="extends")
            
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

# Find path between topics
path = graph.shortest_path("kb_basics_001", "kb_advanced_001")
```

### Automatic Back-Links

When document A links to document B, B automatically knows A links to it:

```python
# In document A:
links:
  related:
    - id: "document_b"

# System automatically provides to document B:
linked_from:
  - id: "document_a"
    link_type: related
```

---

## User Overlays

### Overlay Definition

Users can create custom views of knowledge:

```yaml
# memory/overlays/my_survival_kit.overlay.yaml
---
name: "My Survival Kit"
description: "Custom survival knowledge collection"
author: "user_abc123"
created: "2026-01-06"

# What to include
include:
  # Specific documents
  documents:
    - "kb_survival_fire_001"
    - "kb_survival_water_001"
    - "kb_medical_firstaid_001"
    
  # By category
  categories:
    - "survival/*"
    - "medical/emergency"
    
  # By tag
  tags:
    any: [wilderness, emergency]
    all: [practical]
    
  # By location
  locations:
    tiles: ["L300:BD14-*"]  # Wildcard matching
    regions: ["Northern Hemisphere"]
    
  # By quality
  quality:
    min_score: 3.5
    verified_only: false

# What to exclude
exclude:
  # Exclude global knowledge base
  global_knowledge: false  # true = personal only
  
  # Specific exclusions
  documents:
    - "kb_urban_survival_001"  # Not relevant to me
    
  tags:
    any: [urban, tropical]
    
  # Skill level filter
  skill_level:
    below: beginner  # Hide too-basic content
    above: expert    # Hide too-advanced content

# Custom organization
structure:
  # Custom categories within overlay
  sections:
    - name: "Priority Knowledge"
      filter: { quality: { min_score: 4.5 } }
    - name: "Location Specific"
      filter: { location: { binding: required } }
    - name: "Quick Reference"
      filter: { type: checklist }

# Sorting preferences
sort:
  primary: quality.score
  direction: desc
  secondary: updated
---
```

### Overlay Operations

```bash
# Create overlay
OVERLAY NEW "My Camping Guide"

# Add document to overlay
OVERLAY ADD "My Camping Guide" kb_camping_001

# Remove document
OVERLAY REMOVE "My Camping Guide" kb_urban_001

# Apply overlay (filter knowledge view)
OVERLAY APPLY "My Camping Guide"

# Clear overlay (show all)
OVERLAY CLEAR

# List overlays
OVERLAY LIST

# Export overlay as standalone collection
OVERLAY EXPORT "My Camping Guide" ./my_guide/
```

### System Overlays (Pre-defined)

| Overlay | Description |
|---------|-------------|
| `@all` | Everything (no filter) |
| `@global` | Global knowledge only |
| `@personal` | User's documents only |
| `@drafts` | Work in progress |
| `@nearby` | Location-relevant content |
| `@emergency` | Critical survival info |
| `@offline` | Cached for offline use |

---

## Geo-Tagged Knowledge

### Location Binding Types

| Binding | Description | Example |
|---------|-------------|---------|
| `none` | No location relevance | General programming guide |
| `optional` | Location enhances but not required | Weather patterns |
| `required` | Must be at location to access | Local trail guide |
| `exclusive` | Only visible at exact location | Hidden cache info |

### Location-Based Discovery

```python
# When user is at L300:BD14-CG15-BT21
def discover_knowledge(user_location):
    # Find documents tagged for this location
    local = graph.query(
        location__tiles__contains=user_location,
        status="published"
    )
    
    # Find documents for broader region
    regional = graph.query(
        location__regions__contains=get_region(user_location),
        status="published"
    )
    
    # Respect binding restrictions
    accessible = []
    for doc in local + regional:
        if doc.location.binding == "exclusive":
            if exact_match(doc.location.tiles, user_location):
                accessible.append(doc)
        elif doc.location.binding == "required":
            if within_range(doc.location.tiles, user_location, radius=5):
                accessible.append(doc)
        else:
            accessible.append(doc)
            
    return accessible
```

### Publishing at Location

```bash
# Publish document geo-tagged to current location
PUBLISH fire-guide.udos.md AT CURRENT

# Publish at specific coordinates
PUBLISH fire-guide.udos.md AT L300:BD14-CG15

# Publish with location binding
PUBLISH fire-guide.udos.md AT L300:BD14-CG15 BINDING required
```

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
│       └── old-fire-guide.udos.md  # status: archived
│
├── memory/                         # [USER] Local workspace
│   ├── drafts/                     # Work in progress
│   │   └── my-new-guide.udos.md    # status: draft
│   │
│   ├── contributions/              # Submitted for review
│   │   └── improved-fire.udos.md   # status: submitted
│   │
│   ├── overlays/                   # Custom views
│   │   ├── my_survival.overlay.yaml
│   │   └── camping_trip.overlay.yaml
│   │
│   ├── library/                    # Personal knowledge collection
│   │   ├── imported/               # Forked from global
│   │   │   └── fire-custom.udos.md # My modified version
│   │   └── original/               # My own creations
│   │       └── local-plants.udos.md
│   │
│   └── cache/                      # Indexed data (auto-generated)
│       ├── graph.json              # Knowledge graph cache
│       └── tags.json               # Tag index cache
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

### Rating Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      QUALITY RATING FLOW                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  User reads document                                                │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────────┐                                                │
│  │ Rate 1-5 stars  │ ←── Optional comment                          │
│  └─────────────────┘                                                │
│         │                                                           │
│         ▼                                                           │
│  Aggregate score updated                                            │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────────────────────────────────┐                        │
│  │ If score < 2.0 for 30 days:            │                        │
│  │   → Flag for review                     │                        │
│  │ If score > 4.5 with 50+ votes:         │                        │
│  │   → Mark as "Community Favorite"        │                        │
│  └─────────────────────────────────────────┘                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Verification Badges

| Badge | Requirement | Display |
|-------|-------------|---------|
| ⭐ Community Favorite | Score ≥4.5, votes ≥50 | Gold star |
| ✓ Expert Verified | Reviewed by expert+ | Checkmark |
| 🏛️ System Official | System-authored | Shield |
| 📍 Location Verified | GPS-confirmed content | Pin |
| 🆕 Recently Updated | Updated <7 days | "New" tag |

---

## Implementation Notes

### Document ID Generation

```python
def generate_doc_id(title: str, category: str) -> str:
    """Generate unique document ID."""
    slug = slugify(title)[:30]
    cat_prefix = category.split("/")[0][:10]
    timestamp = int(time.time())
    random_suffix = secrets.token_hex(3)
    return f"kb_{cat_prefix}_{slug}_{random_suffix}"
    
# Example: kb_survival_fire_starting_a1b2c3
```

### Graph Cache Invalidation

```python
# Cache invalidates when:
# 1. Document added/removed
# 2. Document frontmatter changed
# 3. Manual refresh requested

def on_document_change(doc_path: str, change_type: str):
    if change_type in ["create", "delete", "modify_frontmatter"]:
        invalidate_cache()
        rebuild_graph_async()
```

### Query Performance

- Tag queries: O(1) with tag index
- Category queries: O(log n) with B-tree
- Location queries: O(log n) with spatial index
- Full-text: O(n) but cached results

---

*Document Version: 1.0.0.52*
*Last Updated: 2026-01-06*
