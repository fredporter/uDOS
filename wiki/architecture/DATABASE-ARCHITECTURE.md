# uDOS Database Architecture v1.0.0

**Date:** 2026-01-07  
**Author:** uDOS System  
**Status:** Active

---

## Overview

uDOS uses a distributed SQLite database architecture with specialized databases
for different domains, all indexed and linked through markdowndb for knowledge
integration.

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
    tasks JSON,                       -- Task items
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

-- File links (markdowndb standard)
CREATE TABLE file_links (
    source TEXT REFERENCES files(_id),
    target TEXT REFERENCES files(_id),
    link_type TEXT,                   -- internal, wiki, external
    PRIMARY KEY (source, target)
);

-- uDOS Extension: Geographic links
CREATE TABLE knowledge_coordinates (
    file_id TEXT PRIMARY KEY REFERENCES files(_id),
    coordinate TEXT,                  -- EARTH-OC-L100-AB34-CD15
    region TEXT,                      -- OC, AS, EU, NA, etc.
    layer INTEGER,                    -- 100 (Earth surface)
    grid_cell TEXT,                   -- AB34
    UNIQUE(coordinate)
);

CREATE INDEX idx_coord_region ON knowledge_coordinates(region);
CREATE INDEX idx_coord_cell ON knowledge_coordinates(grid_cell);

-- uDOS Extension: Category hierarchy
CREATE TABLE knowledge_categories (
    file_id TEXT REFERENCES files(_id),
    category TEXT NOT NULL,           -- survival, tech, code, places
    subcategory TEXT,                 -- water, fire, upy, cities
    PRIMARY KEY (file_id, category)
);

CREATE INDEX idx_category ON knowledge_categories(category);
```

### Categories

| Category | Subcategories | DB Links |
|----------|--------------|----------|
| `survival` | water, fire, shelter, food, medical | - |
| `tech` | devices, firmware, networking | devices.db |
| `code` | upy, typescript, ucode | core.db, scripts.db |
| `places` | cities, planets, landmarks | geography_knowledge_bridge |
| `skills` | tools, navigation, communication | - |
| `reference` | checklists, charts | - |

---

## 2. Core Code Database (core.db)

**Path:** `memory/bank/core.db`  
**Purpose:** Index of uCODE scripts, TypeScript components, and uPY library

### Schema

```sql
-- Script registry
CREATE TABLE scripts (
    script_id TEXT PRIMARY KEY,       -- Auto-generated UUID
    file_path TEXT NOT NULL UNIQUE,   -- Relative path from project root
    name TEXT NOT NULL,               -- Display name
    language TEXT NOT NULL,           -- upy, typescript, python, json
    type TEXT NOT NULL,               -- command, workflow, template, function
    
    -- Metadata
    version TEXT,
    author TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- Content
    frontmatter JSON,                 -- YAML metadata
    variables JSON,                   -- Extracted $variables
    commands JSON,                    -- Commands used
    dependencies JSON,                -- Import/require dependencies
    
    -- Execution info
    execution_count INTEGER DEFAULT 0,
    last_executed TEXT,
    avg_runtime_ms REAL,
    
    -- Documentation
    description TEXT,
    usage TEXT,
    examples JSON
);

CREATE INDEX idx_scripts_language ON scripts(language);
CREATE INDEX idx_scripts_type ON scripts(type);
CREATE INDEX idx_scripts_name ON scripts(name);

-- Script tags
CREATE TABLE script_tags (
    script_id TEXT REFERENCES scripts(script_id),
    tag TEXT NOT NULL,
    PRIMARY KEY (script_id, tag)
);

-- Script dependencies (imports/uses)
CREATE TABLE script_dependencies (
    script_id TEXT REFERENCES scripts(script_id),
    depends_on TEXT,                  -- Module or script path
    dependency_type TEXT,             -- import, require, use
    PRIMARY KEY (script_id, depends_on)
);

-- Knowledge links
CREATE TABLE script_knowledge_links (
    script_id TEXT REFERENCES scripts(script_id),
    knowledge_file_id TEXT,           -- References knowledge.db files._id
    link_type TEXT,                   -- documentation, tutorial, reference
    PRIMARY KEY (script_id, knowledge_file_id)
);

-- uPY Functions
CREATE TABLE upy_functions (
    function_id TEXT PRIMARY KEY,
    script_id TEXT REFERENCES scripts(script_id),
    name TEXT NOT NULL,               -- @FUNCTION_NAME
    params JSON,                      -- Parameter list
    returns TEXT,                     -- Return type hint
    docstring TEXT,
    line_number INTEGER,
    UNIQUE(script_id, name)
);

CREATE INDEX idx_functions_name ON upy_functions(name);

-- TypeScript Components
CREATE TABLE ts_components (
    component_id TEXT PRIMARY KEY,
    script_id TEXT REFERENCES scripts(script_id),
    name TEXT NOT NULL,
    type TEXT,                        -- component, hook, util, store
    exports JSON,                     -- Exported symbols
    props JSON,                       -- Props interface
    line_number INTEGER
);

CREATE INDEX idx_components_type ON ts_components(type);
```

### Script Types

| Type | Language | Location | Example |
|------|----------|----------|---------|
| `command` | upy | `memory/ucode/` | workflow scripts |
| `workflow` | upy | `memory/ucode/adventures/` | mission templates |
| `template` | upy | `memory/templates/` | .udos.md templates |
| `function` | upy | `core/runtime/` | reusable functions |
| `component` | typescript | `app/src/` | Svelte components |
| `handler` | python | `core/commands/` | command handlers |

---

## 3. Contacts Database (contacts.db)

**Path:** `memory/bank/user/contacts.db`  
**Purpose:** BizIntel business contacts with knowledge links

### Schema (Existing + Extensions)

```sql
-- Existing tables from marketing_db.py:
-- businesses, people, business_person_roles, audience, messages
-- social_profiles, enrichment_cache

-- NEW: Knowledge links for businesses
CREATE TABLE business_knowledge_links (
    business_id TEXT REFERENCES businesses(business_id),
    knowledge_file_id TEXT,           -- References knowledge.db
    link_type TEXT,                   -- industry, location, service
    relevance_score REAL,             -- 0.0-1.0
    created_at TEXT,
    PRIMARY KEY (business_id, knowledge_file_id)
);

-- NEW: Industry categories
CREATE TABLE business_industries (
    business_id TEXT REFERENCES businesses(business_id),
    industry TEXT NOT NULL,           -- Tag-based
    is_primary INTEGER DEFAULT 0,
    PRIMARY KEY (business_id, industry)
);

CREATE INDEX idx_industry ON business_industries(industry);

-- NEW: Geographic context
CREATE TABLE business_locations (
    business_id TEXT REFERENCES businesses(business_id),
    coordinate TEXT,                  -- TILE coordinate
    city_guide_path TEXT,             -- /knowledge/places/cities/sydney.md
    region TEXT,
    PRIMARY KEY (business_id)
);
```

---

## 4. Devices Database (devices.db)

**Path:** `memory/bank/wizard/devices.db`  
**Purpose:** Sonic Screwdriver device registry and firmware tracking

### Schema

```sql
-- Device registry
CREATE TABLE devices (
    device_id TEXT PRIMARY KEY,       -- D1, D2, etc.
    tile TEXT NOT NULL,               -- TILE code
    layer INTEGER NOT NULL,           -- 600-650
    type TEXT NOT NULL,               -- node, gateway, sensor, repeater, end_device
    status TEXT NOT NULL,             -- online, offline, connecting, error
    
    -- Hardware
    hardware_model TEXT,
    hardware_revision TEXT,
    mac_address TEXT UNIQUE,
    serial_number TEXT,
    
    -- Firmware
    firmware_version TEXT,
    firmware_status TEXT,             -- current, outdated, incompatible, updating
    firmware_channel TEXT,            -- stable, beta, dev
    last_firmware_update TEXT,
    
    -- Metrics
    signal_strength INTEGER,          -- 0-100
    uptime_hours REAL,
    messages_per_sec INTEGER,
    error_count INTEGER DEFAULT 0,
    
    -- Timestamps
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_devices_tile ON devices(tile);
CREATE INDEX idx_devices_type ON devices(type);
CREATE INDEX idx_devices_status ON devices(status);

-- Device connections (topology)
CREATE TABLE device_connections (
    source_device_id TEXT REFERENCES devices(device_id),
    target_device_id TEXT REFERENCES devices(device_id),
    connection_type TEXT,             -- mesh, gateway, relay
    signal_quality INTEGER,           -- 0-100
    latency_ms INTEGER,
    last_active TEXT,
    PRIMARY KEY (source_device_id, target_device_id)
);

-- Firmware packages
CREATE TABLE firmware_packages (
    package_id TEXT PRIMARY KEY,
    version TEXT NOT NULL,
    channel TEXT NOT NULL,            -- stable, beta, dev
    device_type TEXT NOT NULL,
    file_path TEXT,
    checksum TEXT,
    size_bytes INTEGER,
    release_notes TEXT,
    released_at TEXT NOT NULL,
    UNIQUE(version, device_type, channel)
);

-- Provisioning history
CREATE TABLE provisioning_history (
    provision_id TEXT PRIMARY KEY,
    device_id TEXT REFERENCES devices(device_id),
    firmware_version TEXT,
    status TEXT,                      -- success, failed, partial
    started_at TEXT NOT NULL,
    completed_at TEXT,
    error_message TEXT
);

-- Knowledge links for devices
CREATE TABLE device_knowledge_links (
    device_id TEXT REFERENCES devices(device_id),
    knowledge_file_id TEXT,           -- References knowledge.db
    link_type TEXT,                   -- manual, troubleshooting, firmware
    PRIMARY KEY (device_id, knowledge_file_id)
);
```

---

## 5. Wizard Scripts Database (scripts.db)

**Path:** `memory/bank/wizard/scripts.db`  
**Purpose:** Server-side script library with AI provider integrations

### Schema

```sql
-- Server scripts
CREATE TABLE wizard_scripts (
    script_id TEXT PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL,           -- ai, web, automation, provisioning
    provider TEXT,                    -- anthropic, gemini, openai, local
    
    -- Metadata
    version TEXT,
    author TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- Access control
    requires_api_key INTEGER DEFAULT 0,
    requires_internet INTEGER DEFAULT 1,  -- Most wizard scripts need web
    
    -- Content
    description TEXT,
    input_schema JSON,
    output_schema JSON,
    
    -- Execution
    execution_count INTEGER DEFAULT 0,
    last_executed TEXT,
    avg_runtime_ms REAL,
    error_rate REAL
);

CREATE INDEX idx_wizard_category ON wizard_scripts(category);
CREATE INDEX idx_wizard_provider ON wizard_scripts(provider);

-- AI Provider configurations
CREATE TABLE ai_providers (
    provider_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,               -- llm, image, audio, embedding
    api_endpoint TEXT,
    models JSON,                      -- Available models
    cost_per_1k_tokens REAL,
    is_enabled INTEGER DEFAULT 1,
    last_health_check TEXT,
    status TEXT
);

-- Web tool registry (scraping, API clients)
CREATE TABLE web_tools (
    tool_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,               -- scraper, api_client, webhook
    target_domain TEXT,
    rate_limit_rpm INTEGER,
    last_used TEXT,
    success_rate REAL
);

-- Script knowledge links
CREATE TABLE wizard_knowledge_links (
    script_id TEXT REFERENCES wizard_scripts(script_id),
    knowledge_file_id TEXT,
    link_type TEXT,                   -- documentation, api_reference
    PRIMARY KEY (script_id, knowledge_file_id)
);
```

---

## 6. Cross-Database Linking

### Link Tables

Each database contains a `*_knowledge_links` table that references knowledge.db:

```sql
-- Standard link structure
CREATE TABLE {entity}_knowledge_links (
    {entity}_id TEXT,                 -- Primary entity ID
    knowledge_file_id TEXT,           -- References knowledge.db files._id
    link_type TEXT,                   -- Type of link
    relevance_score REAL,             -- Optional ranking
    created_at TEXT,
    PRIMARY KEY ({entity}_id, knowledge_file_id)
);
```

### Link Types

| Link Type | Description | Example |
|-----------|-------------|---------|
| `documentation` | Primary docs | Script → Tutorial |
| `tutorial` | Learning resource | Device → Setup Guide |
| `reference` | Technical spec | Component → API Docs |
| `troubleshooting` | Problem solving | Device → Debug Guide |
| `location` | Geographic context | Business → City Guide |
| `industry` | Business category | Business → Industry Guide |

---

## 7. Database Manager Service

### Python API

```python
from core.services.database_manager import get_database_manager

db = get_database_manager()

# Query knowledge
results = db.knowledge.search("water purification", tags=["survival"])

# Get scripts by language
upy_scripts = db.core.get_scripts(language="upy", type="workflow")

# Find devices by status
online_devices = db.devices.get_by_status("online")

# Link business to knowledge
db.contacts.link_knowledge(
    business_id="biz-abc123",
    knowledge_file="/knowledge/places/cities/sydney.md",
    link_type="location"
)

# Find related knowledge for device
guides = db.devices.get_knowledge_links("D1", link_type="troubleshooting")
```

### CLI Commands

```bash
# Index knowledge (rebuild from /knowledge)
DB INDEX knowledge

# Search across databases
DB SEARCH "water" --db knowledge,core

# Show database stats
DB STATS

# Export to JSON
DB EXPORT knowledge --format json

# Link entities
DB LINK device:D1 knowledge:/knowledge/tech/meshcore.md troubleshooting
```

---

## 8. markdowndb Integration

### Indexing Knowledge

```javascript
// Build knowledge.db from /knowledge folder
const { MarkdownDB } = require("mddb");

const client = new MarkdownDB({
  client: "sqlite3",
  connection: { filename: "memory/bank/knowledge.db" }
});

await client.init();
await client.indexFolder("knowledge", {
  computedFields: [
    // Extract TILE coordinates from frontmatter
    (fileInfo, ast) => {
      const coord = fileInfo.metadata?.knowledge?.coordinate;
      if (coord) {
        fileInfo.tile_coordinate = coord;
        fileInfo.region = coord.split("-")[1];
      }
    },
    // Extract category from path
    (fileInfo) => {
      const parts = fileInfo.file_path.split("/");
      if (parts.length >= 2) {
        fileInfo.category = parts[1]; // knowledge/survival/... → survival
      }
    }
  ]
});
```

### Query Examples

```sql
-- Find survival guides tagged with 'water'
SELECT f.* FROM files f
JOIN file_tags ft ON f._id = ft.file
WHERE ft.tag = 'water' 
  AND f.file_path LIKE 'knowledge/survival/%';

-- Find code guides for uPY
SELECT * FROM files 
WHERE json_extract(metadata, '$.category') = 'code'
  AND json_extract(metadata, '$.language') = 'upy';

-- Find city guides in Oceania
SELECT f.*, kc.coordinate FROM files f
JOIN knowledge_coordinates kc ON f._id = kc.file_id
WHERE kc.region = 'OC';
```

---

## Related Documentation

- [UDOS-MD-TEMPLATE-SPEC.md](UDOS-MD-TEMPLATE-SPEC.md) - Template format
- [GEOGRAPHY-KNOWLEDGE-SPEC.md](../../knowledge/GEOGRAPHY-KNOWLEDGE-SPEC.md) - Geographic linking
- [BizIntel README](../../wizard/tools/bizintel/README.md) - Contacts system
- [Screwdriver Tools](../../wizard/tools/screwdriver/) - Device provisioning

---

*Version: 1.0.0 | Last Updated: 2026-01-07*
