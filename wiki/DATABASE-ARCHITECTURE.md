# uDOS Database Architecture (v1.0.1.0)

**Last Updated:** 2026-01-24
**Status:** Active Standard
**Author:** uDOS Engineering

uDOS uses a distributed SQLite database architecture with specialized databases for different domains, all indexed and linked through markdowndb for knowledge integration.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        uDOS DATABASE ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  /memory/bank/                                                           │
│  ├── knowledge.db        ← markdowndb index of /knowledge (240+ guides) │
│  ├── core.db             ← uCODE scripts, TypeScript, uPY library       │
│  ├── user/                                                               │
│  │   ├── contacts.db     ← BizIntel contacts & businesses               │
│  │   ├── missions.db     ← User missions & progress                     │
│  │   └── preferences.db  ← User settings                                 │
│  └── wizard/                                                             │
│      ├── scripts.db      ← Wizard server script library                 │
│      └── devices.db      ← Sonic Screwdriver device registry            │
│                                                                          │
│  Cross-linking via:                                                      │
│  - knowledge_links table in each DB                                      │
│  - TILE coordinates for geographic context                               │
│  - Tag-based categorization                                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Knowledge Database (knowledge.db)

**Path:** `memory/bank/knowledge.db`
**Source:** markdowndb index of `/knowledge/`
**Purpose:** Fast search and query of survival guides

### Schema

```sql
-- Core file index (markdowndb standard)
CREATE TABLE files (
    _id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    url_path TEXT,
    extension TEXT,
    metadata JSON,                    -- YAML frontmatter
    tags JSON,                        -- Extracted tags
    links JSON,                       -- Internal links
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX idx_files_path ON files(file_path);
CREATE INDEX idx_files_url ON files(url_path);

-- File tags (markdowndb standard)
CREATE TABLE file_tags (
    file TEXT REFERENCES files(_id),
    tag TEXT NOT NULL,
    PRIMARY KEY (file, tag)
);

CREATE INDEX idx_tags_tag ON file_tags(tag);

-- Geographic coordinates
CREATE TABLE knowledge_coordinates (
    file_id TEXT PRIMARY KEY REFERENCES files(_id),
    coordinate TEXT,
    region TEXT,
    layer INTEGER,
    grid_cell TEXT
);

CREATE INDEX idx_coord_region ON knowledge_coordinates(region);
```

### Categories

| Category   | Content                             | DB Links   |
| ---------- | ----------------------------------- | ---------- |
| `survival` | Water, fire, shelter, food, medical | -          |
| `tech`     | Devices, firmware, networking       | devices.db |
| `code`     | uPY, TypeScript, uCode              | core.db    |
| `places`   | Cities, planets, landmarks          | Geographic |
| `skills`   | Tools, navigation, communication    | -          |

---

## 2. Core Code Database (core.db)

**Path:** `memory/bank/core.db`
**Purpose:** Index of uCODE scripts, TypeScript components, and uPY library

### Schema

```sql
-- Script registry
CREATE TABLE scripts (
    script_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    language TEXT NOT NULL,           -- upy, typescript, python, json
    type TEXT NOT NULL,               -- command, workflow, template, function
    version TEXT,
    author TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_scripts_language ON scripts(language);
CREATE INDEX idx_scripts_type ON scripts(type);

-- uPY Functions
CREATE TABLE upy_functions (
    function_id TEXT PRIMARY KEY,
    script_id TEXT REFERENCES scripts(script_id),
    name TEXT NOT NULL
);

-- Knowledge links
CREATE TABLE script_knowledge_links (
    script_id TEXT REFERENCES scripts(script_id),
    knowledge_file_id TEXT,
    link_type TEXT,
    PRIMARY KEY (script_id, knowledge_file_id)
);
```

### Script Types

| Type        | Language   | Location                   | Example            |
| ----------- | ---------- | -------------------------- | ------------------ |
| `command`   | uPY        | `memory/bank/scripts/`     | Workflow scripts   |
| `workflow`  | uPY        | `memory/sandbox/adventures/` | Mission templates  |
| `template`  | uPY        | `memory/templates/`        | .udos.md templates |
| `function`  | uPY        | `core/runtime/`            | Reusable functions |
| `component` | TypeScript | `app/`                 | Svelte components  |
| `handler`   | Python     | `core/commands/`           | Command handlers   |

---

## 3. Cross-Database Linking

### Link Tables

Each database contains a `*_knowledge_links` table:

```sql
CREATE TABLE {entity}_knowledge_links (
    {entity}_id TEXT,
    knowledge_file_id TEXT,
    link_type TEXT,
    relevance_score REAL,
    created_at TEXT,
    PRIMARY KEY ({entity}_id, knowledge_file_id)
);
```

### Link Types

| Link Type       | Description        | Example                   |
| --------------- | ------------------ | ------------------------- |
| `documentation` | Primary docs       | Script → Tutorial         |
| `tutorial`      | Learning resource  | Device → Setup Guide      |
| `reference`     | Technical spec     | Component → API Docs      |
| `location`      | Geographic context | Business → City Guide     |
| `industry`      | Business category  | Business → Industry Guide |

---

## Related Documentation

- [UDOS-MD-FORMAT.md](UDOS-MD-FORMAT.md) — Executable document format
- [KNOWLEDGE-LINKING-SYSTEM.md](KNOWLEDGE-LINKING-SYSTEM.md) — Self-indexing documents
- [../../docs/development-streams.md](../../docs/development-streams.md) — Implementation roadmap

---

**Status:** Active Architecture Standard
**Repository:** https://github.com/fredporter/uDOS
