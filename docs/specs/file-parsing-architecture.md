# v1.0.6.0 - File Parsing System Architecture

**Version:** v1.0.6.0  
**Status:** In Planning (Starting 2026-01-17)  
**Mission:** Complete file parsing system for offline-first data workflows  
**Estimated Duration:** 3-4 weeks  
**Target Release Date:** Early February 2026

---

## 🎯 Core Mission

Enable uDOS to ingest, transform, and export data in multiple formats (Markdown, CSV, JSON, YAML, SQL) with a focus on:

- **Offline-first**: All processing local, no cloud required
- **Binder isolation**: Sandboxed workspaces with local database access
- **User-friendly**: Parse human-readable files → structured data → human-readable exports

---

## 📊 System Architecture

### Data Processing Pipeline

```
Input Formats         Parser         SQLite Database      Export/Execute
─────────────────────────────────────────────────────────────────────────
.table.md      →  Markdown Parser  →  Tables (uDOS-table.db)  → .table.md
.csv/.tsv      →  CSV Parser       →  Columns + Data            → FEED RSS
.json/.jsonl   →  JSON Parser      →  Flattened Tables          → .sql
.yaml/.toml    →  YAML Parser      →  Config Objects
.sql           →  SQL Executor     →  Results/Updates
```

### Binder Isolation Model

```
MyBinder/
├── binder.md                  # Optional binder home
├── uDOS-table.db              # Local SQLite database (readonly from app)
├── imports/                   # Source files (CSV, JSON, YAML)
│   ├── contacts.csv
│   ├── settings.yaml
│   └── data.json
├── tables/                    # Exported .table.md files
│   ├── contacts.table.md
│   ├── revenue-summary.table.md
│   └── top-10-cities.table.md
├── scripts/                   # .script.md executables
│   ├── data-cleanup.script.md
│   └── monthly-report.script.md
└── sql/                       # Raw SQL files (optional)
    ├── clean_contacts.sql
    └── generate_summary.sql
```

### API Endpoints (Wizard/Goblin)

**Wizard Server (Port 8765) - v1.0.6.0 Production APIs:**

| Endpoint                  | Method | Purpose                         |
| ------------------------- | ------ | ------------------------------- |
| `/api/v1/parse/table`     | POST   | Parse Markdown table → SQLite   |
| `/api/v1/parse/csv`       | POST   | Import CSV → SQLite             |
| `/api/v1/parse/json`      | POST   | Import JSON → SQLite            |
| `/api/v1/parse/yaml`      | POST   | Import YAML → config/table      |
| `/api/v1/binders/{id}/db` | GET    | Access binder database          |
| `/api/v1/export/table`    | POST   | Export SQLite table → .table.md |
| `/api/v1/execute/sql`     | POST   | Execute SQL script              |
| `/api/v1/feed/generate`   | POST   | Generate RSS from local content |

**Goblin Dev Server (Port 8767) - v1.0.6.0 Experimental:**

```
POST /api/v0/parse/markdown   - Parse .table.md blocks
POST /api/v0/import/csv       - Import CSV with transformation
POST /api/v0/export/markdown  - Export tables as .table.md
```

---

## 📋 12 Core Tasks

### Phase 1: Parsers (Tasks 1-5)

#### Task 1: Markdown Table Parser ✓

**Component:** `core/parsers/markdown_table_parser.py`

**Responsibility:**

- Parse `.table.md` files with frontmatter
- Extract table structure (columns, types)
- Validate data integrity
- Handle multiline cells

**Input Format:**

```markdown
---
table_name: contacts
columns:
  - name: id
    type: integer
    primary_key: true
  - name: email
    type: text
  - name: created_at
    type: datetime
---

| id  | email             | created_at |
| --- | ----------------- | ---------- |
| 1   | alice@example.com | 2026-01-01 |
| 2   | bob@example.com   | 2026-01-02 |
```

**Output:** SQLite table with schema + data

**Implementation Details:**

- frontmatter parsing (metadata)
- Markdown table detection (pipes + dashes)
- Type inference/validation
- Multiline cell handling (escaped newlines)
- Tests: 12+ unit tests

---

#### Task 2: CSV/TSV Importer ✓

**Component:** `core/parsers/csv_importer.py`

**Responsibility:**

- Import CSV/TSV files → SQLite tables
- Auto-detect delimiters, encoding, headers
- Handle quoted fields, escapes, multiline
- Type inference from sample data

**Features:**

- Encoding detection (UTF-8, UTF-16, Latin-1)
- Delimiter auto-detection (comma, tab, semicolon, pipe)
- Header validation and sanitization
- Quoted field handling
- Null value patterns (`NULL`, `N/A`, empty)
- Type detection from data samples

**Input:** CSV/TSV file (any encoding)  
**Output:** SQLite table (inferred types)

**Tests:** 15+ unit tests (various encodings, delimiters, edge cases)

---

#### Task 3: JSON/JSONL Parser ✓

**Component:** `core/parsers/json_importer.py`

**Responsibility:**

- Parse JSON and JSONL files → SQLite tables
- Handle nested objects (flattening strategy)
- Array handling (pivot or expand)
- Type preservation

**Features:**

- Single JSON file (array or objects)
- JSONL (one JSON object per line)
- Nested object flattening (dot notation: `user.name` → `user_name`)
- Array handling:
  - Simple arrays → separate rows
  - Nested arrays → nested table joins
- Type mapping (number, string, boolean, null, object, array)

**Example:**

```json
[
  { "id": 1, "user": { "name": "Alice", "email": "alice@example.com" } },
  { "id": 2, "user": { "name": "Bob", "email": "bob@example.com" } }
]
```

Flattens to:

```
| id | user_name | user_email |
|----|-----------|-----------|
| 1  | Alice     | alice@... |
| 2  | Bob       | bob@...   |
```

**Tests:** 14+ unit tests (nested objects, arrays, mixed types)

---

#### Task 4: YAML/TOML Parser ✓

**Component:** `core/parsers/yaml_importer.py`, `core/parsers/toml_importer.py`

**Responsibility:**

- Parse YAML/TOML configuration → config objects or tables
- Two modes: **structured config** or **data tables**

**YAML Config Mode:**

```yaml
# uDOS-config.yaml
app:
  name: "uDOS"
  version: "1.0.6.0"
  theme: "dark"
services:
  - name: "Wizard"
    port: 8765
  - name: "Goblin"
    port: 8767
```

Maps to: `ConfigObject` with nested access

```python
config.app.name      # "uDOS"
config.services[0].port  # 8765
```

**YAML Data Mode:**

```yaml
contacts:
  - id: 1
    name: "Alice"
    email: "alice@example.com"
  - id: 2
    name: "Bob"
    email: "bob@example.com"
```

Converts to SQLite table `contacts` with 3 columns.

**Tests:** 10+ unit tests (both modes, nesting, arrays)

---

#### Task 5: SQL Script Executor ✓

**Component:** `core/parsers/sql_executor.py`

**Responsibility:**

- Execute SQL scripts within binder context
- Support SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER
- Transaction handling and rollback
- Query result formatting

**Features:**

- Transaction support (begin/commit/rollback)
- Error handling with detailed messages
- Multi-statement support (separated by `;`)
- Result formatting (tables, JSON, CSV export)
- Variable substitution (`?` placeholders)
- Time query tracking (slow queries)

**Example Script:**

```sql
-- clean_contacts.sql
BEGIN TRANSACTION;

-- Remove duplicates
DELETE FROM contacts WHERE id NOT IN (
  SELECT MIN(id) FROM contacts GROUP BY email
);

-- Add created_at if missing
UPDATE contacts SET created_at = datetime('now') WHERE created_at IS NULL;

COMMIT;
```

**Tests:** 12+ unit tests (transactions, errors, results)

---

### Phase 2: Data Export (Task 6)

#### Task 6: Table Export (.table.md) ✓

**Component:** `core/exporters/markdown_table_exporter.py`

**Responsibility:**

- Export SQLite tables → `.table.md` files
- Format with frontmatter metadata
- Preserve data types in comments
- Handle large tables (pagination/summary)

**Output Format:**

```markdown
---
table_name: contacts
source_db: uDOS-table.db
exported_at: 2026-01-17T10:30:00Z
row_count: 150
columns:
  - id (integer, pk)
  - email (text)
  - created_at (datetime)
---

| id  | email             | created_at          |
| --- | ----------------- | ------------------- |
| 1   | alice@example.com | 2026-01-01T00:00:00 |
| 2   | bob@example.com   | 2026-01-02T00:00:00 |
```

**Features:**

- Metadata in frontmatter
- Type annotations in comments
- Truncation for large tables (100 rows + "..." message)
- Special character escaping (pipes, newlines)
- Index/PK indicators
- Data type preservation in export

**Tests:** 10+ unit tests (various types, large tables, special characters)

---

### Phase 3: Binder Structure (Task 7-8)

#### Task 7: Binder Folder Structure ✓

**Component:** `core/binders/binder_manager.py`

**Responsibility:**

- Create and manage isolated binder workspaces
- Initialize database schemas
- Organize imports, tables, scripts directories

**API:**

```python
binder = BinderManager.create("MyBinder")
binder.add_import("contacts.csv")       # → imports/
binder.add_table("contacts_table.md")   # → tables/
binder.add_script("cleanup.script.md")  # → scripts/
binder.get_database()                   # → uDOS-table.db handle
```

**Directory Structure Created:**

```
MyBinder/
├── .binder.json              # Metadata
├── uDOS-table.db             # SQLite database (created)
├── imports/                  # User adds files here
├── tables/                   # Exported .table.md files
├── scripts/                  # .script.md executables
└── README.md                 # Auto-generated guide
```

**Binder Metadata (.binder.json):**

```json
{
  "id": "mybinder-2026-01-17",
  "name": "MyBinder",
  "created_at": "2026-01-17T10:00:00Z",
  "updated_at": "2026-01-17T10:30:00Z",
  "tables": ["contacts", "orders", "products"],
  "imports": ["contacts.csv", "settings.yaml"],
  "scripts": ["cleanup.script.md"],
  "db_version": "1.0.6.0"
}
```

**Tests:** 8+ unit tests (creation, structure, metadata)

---

#### Task 8: Binder-Local DB Context ✓

**Component:** `core/binders/binder_database.py`

**Responsibility:**

- Provide isolated SQLite access within binder
- Relative path resolution within binder scope
- Transaction management
- Query results formatting

**API:**

```python
binder = BinderManager.get("MyBinder")
db = binder.get_database()

# Access tables
contacts = db.query("SELECT * FROM contacts WHERE email LIKE '%@example.com'")

# Import data into binder
db.import_csv("imports/leads.csv")  # Relative to binder

# Export results
db.export_table("contacts", "tables/contacts.table.md")
```

**Features:**

- Relative paths resolved within binder
- Lazy loading (database only opened when accessed)
- Connection pooling
- Automatic schema creation from imports
- Query result caching (optional)
- Concurrent access safe (SQLite WAL mode)

**Tests:** 10+ unit tests (queries, imports, exports, relative paths)

---

### Phase 4: Advanced Features (Tasks 9-10)

#### Task 9: RSS Feed Generation ✓

**Component:** `wizard/services/feed_generator.py` + Core FEED command

**Responsibility:**

- Generate RSS feeds from local content
- Assemble feeds from Markdown documents, logs, events
- Serve via Wizard API endpoint

**FEED Command Syntax:**

```bash
# Generate RSS from recent documents
FEED --sources /binders/news --title "uDOS News" --output feed.xml

# Include multiple sources
FEED --sources /docs --sources /memory/logs --title "All Updates"

# Filter by date range
FEED --sources /docs --since 2026-01-01 --until 2026-01-17

# Auto-serve via Wizard
FEED --serve --port 8765 --path /feeds/main
```

**RSS Feed Structure:**

```xml
<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>uDOS News</title>
    <link>http://localhost:8765</link>
    <description>Generated from local content</description>
    <item>
      <title>v1.0.6.0 Released</title>
      <link>file:///Users/fredbook/Code/uDOS/docs/roadmap.md</link>
      <description>File parsing system now available</description>
      <pubDate>Wed, 17 Jan 2026 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
```

**Features:**

- Auto-extract titles from documents
- Parse dates from frontmatter or filenames
- Markdown → HTML conversion in RSS
- Image/attachment handling
- Custom feeds (filter by tags, dates, authors)
- Auto-refresh intervals

**API Endpoint:**

```bash
GET /api/v1/feeds/list              # List available feeds
POST /api/v1/feeds/generate         # Generate new feed
GET /api/v1/feeds/{id}/rss          # Get RSS XML
```

**Tests:** 10+ unit tests (feed generation, filtering, XML validity)

---

#### Task 10: Table Export (.table.md) - Already Covered (Task 6)

---

### Phase 5: Editor Integration (Tasks 11-12)

#### Task 11: uDOS Language Registration ✓

**Component:** `extensions/vscode/udos-language.json`

**Responsibility:**

- Register `udos` language with VS Code
- Syntax highlighting for code blocks
- Grammar rules and tokenization

**Grammar Definition:**

```json
{
  "name": "uDOS",
  "scopeName": "source.udos",
  "fileTypes": ["udos"],
  "patterns": [
    {
      "name": "keyword.control.udos",
      "match": "\\b(state|set|form|if|else|nav|panel|map)\\b"
    },
    {
      "name": "variable.udos",
      "match": "\\$[a-zA-Z_][a-zA-Z0-9_]*"
    },
    {
      "name": "string.quoted.double.udos",
      "begin": "\"",
      "end": "\"",
      "escapes": "\\\\\\."
    }
  ]
}
```

**Features:**

- Syntax highlighting for runtime blocks
- Variable syntax (`$varname`)
- String literals and escapes
- Nested block indentation
- Comment support

**VS Code Extension Changes:**

```json
{
  "contributes": {
    "languages": [
      {
        "id": "udos",
        "aliases": ["uDOS", "udos"],
        "extensions": ["-ucode.md"],
        "configuration": "language-udos.json"
      }
    ],
    "grammars": [
      {
        "language": "udos",
        "scopeName": "source.udos",
        "path": "./syntaxes/udos.json"
      }
    ]
  }
}
```

**Syntax Highlighting Example:**

```
state             # keyword (blue)
$contacts         # variable (orange)
form              # keyword (blue)
"Email Required"  # string (green)
```

---

#### Task 12: Documentation & Testing ✓

**Component:** `docs/howto/FILE-PARSING-SYSTEM.md` + tests

**Responsibility:**

- Complete integration tests
- User guides and tutorials
- API documentation
- Troubleshooting guide

**Deliverables:**

1. **Integration Test Suite** (`core/tests/test_file_parsing_v1_0_6.py`)
   - 30+ tests covering all parsers
   - End-to-end binder workflows
   - Export/import round-trip validation

2. **User Guide** (`docs/howto/FILE-PARSING-SYSTEM.md`)
   - Quick start with CSV import
   - Binder creation and management
   - Markdown table editing
   - SQL query examples
   - Advanced transformations

3. **API Documentation** (`docs/api/FILE-PARSING-API.md`)
   - Endpoint reference (8 endpoints)
   - Request/response examples
   - Error codes and handling
   - Rate limiting and quotas

4. **Troubleshooting Guide**
   - Common parsing errors
   - Type mismatch handling
   - Large file optimization
   - Performance tuning

5. **Roadmap Update**
   - Mark v1.0.6.0 complete
   - Preview v1.0.7 (Groovebox)
   - Release schedule

---

## 🗺️ Implementation Timeline

| Phase       | Tasks                        | Duration      | Status         |
| ----------- | ---------------------------- | ------------- | -------------- |
| **Setup**   | Architecture, task planning  | 0.5 days      | 🔄 In Progress |
| **Phase 1** | Parsers (5 tasks)            | 10 days       | ⏳ Planned     |
| **Phase 2** | Exporters (1 task)           | 2 days        | ⏳ Planned     |
| **Phase 3** | Binder structure (2 tasks)   | 3 days        | ⏳ Planned     |
| **Phase 4** | Advanced features (2 tasks)  | 4 days        | ⏳ Planned     |
| **Phase 5** | Editor integration (2 tasks) | 2 days        | ⏳ Planned     |
| **Testing** | Integration & docs (1 task)  | 2 days        | ⏳ Planned     |
| **Total**   |                              | **3-4 weeks** |                |

---

## 📊 Success Criteria

✅ **Completion Requirements:**

- [ ] All 12 tasks implemented
- [ ] 50+ unit tests (passing)
- [ ] 30+ integration tests (passing)
- [ ] 0 secrets in repository
- [ ] Comprehensive user documentation
- [ ] API documentation complete
- [ ] Roadmap updated
- [ ] Ready for v1.0.6.0 release

✅ **Performance Targets:**

- CSV import: < 1s for 10,000 rows
- JSON parsing: < 500ms for 100MB
- Table export: < 200ms
- SQL queries: < 100ms (typical)

✅ **Code Quality:**

- 95%+ test coverage
- Docstrings on all public methods
- Type hints throughout
- Clear error messages
- Logging at appropriate levels

---

## 🔗 References

- [app-files-parsing.md](./app-files-parsing.md) - Original spec
- [docs/roadmap.md](../docs/roadmap.md) - Full project roadmap
- [AGENTS.md](../AGENTS.md) - Architecture principles
- [Binder Spec](../library/binders/BINDER-FORMAT.md) - Binder standard

---

**Status:** Setup Complete (2026-01-17)  
**Next Step:** Begin Phase 1 - Implement Markdown Table Parser
