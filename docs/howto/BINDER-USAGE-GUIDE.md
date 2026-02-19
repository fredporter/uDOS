# Binder System Usage Guide

**Version:** v1.0.6.0 Phase 3
**Status:** Complete
**Components:** BinderConfig, BinderValidator, BinderDatabase, BinderFeed

---

## Quick Start

### 1. Create a Binder

```bash
mkdir MyBinder
cd MyBinder

# Create folder structure
mkdir imports tables scripts

# Create empty database
touch uDOS-table.db

# Create config (optional - auto-generated if missing)
cat > .binder-config << 'EOF'
{
  "name": "My Research Binder",
  "version": "1.0.0",
  "created_at": "2026-01-17T10:00:00Z",
  "author": "Your Name",
  "description": "Research notes and data",
  "tags": ["research", "data"]
}
EOF
```

### 2. Load and Validate

```python
from pathlib import Path
from core.binder import load_binder_config, BinderValidator

# Load configuration
binder_path = Path("./MyBinder")
config = load_binder_config(binder_path)
print(f"Loaded: {config.name} v{config.version}")

# Validate structure
report = BinderValidator.validate(binder_path)
if report.is_valid:
    print("✓ Binder structure valid")
else:
    print(f"✗ Issues found: {len(report.issues)}")
    for issue in report.issues:
        print(f"  [{issue.severity.value}] {issue.message}")
```

### 3. Database Operations

```python
from core.binder import BinderDatabase

# Open database context
with BinderDatabase(binder_path) as db:
    # Create table
    db.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT
        )
    """)

    # Insert data
    db.execute(
        "INSERT INTO items (name, category) VALUES (?, ?)",
        ("Sample Item", "research")
    )

    # Query data
    results = db.query("SELECT * FROM items")
    for row in results:
        print(f"{row['name']}: {row['category']}")
```

### 4. Generate RSS Feed

```python
from core.binder import BinderFeed

# Create markdown files with frontmatter
(binder_path / "article1.md").write_text("""---
title: First Article
date: 2026-01-15
author: Alice
tags: [research]
---

# First Article

Content here.
""")

# Generate feed
feed = BinderFeed(binder_path, base_url="https://example.com/binders")
items = feed.scan_files()
print(f"Found {len(items)} articles")

# Save RSS
rss_xml = feed.generate_rss()
feed.save_feed(binder_path / "feed.xml", rss_xml)

# Save JSON Feed
json_feed = feed.generate_json()
import json
(binder_path / "feed.json").write_text(json.dumps(json_feed, indent=2))
```

---

## Complete Example

```python
#!/usr/bin/env python3
"""Complete binder workflow example"""

from pathlib import Path
from datetime import datetime
from core.binder import (
    BinderConfig,
    load_binder_config,
    save_binder_config,
    BinderValidator,
    BinderDatabase,
    BinderFeed
)

def create_research_binder():
    """Create and populate a research binder"""

    # 1. Setup paths
    binder_path = Path("./ResearchBinder")
    binder_path.mkdir(exist_ok=True)
    (binder_path / "imports").mkdir(exist_ok=True)
    (binder_path / "tables").mkdir(exist_ok=True)

    # 2. Create configuration
    config = BinderConfig(
        name="Research Binder",
        version="1.0.0",
        created_at=datetime.now(),
        author="Dr. Smith",
        description="Climate research data and notes",
        tags=["research", "climate", "data"]
    )
    save_binder_config(config, binder_path)

    # 3. Initialize database
    with BinderDatabase(binder_path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                date TEXT,
                result REAL
            )
        """)

        db.execute("""
            INSERT INTO experiments (name, date, result) VALUES
            ('Experiment A', '2026-01-10', 23.5),
            ('Experiment B', '2026-01-12', 24.1),
            ('Experiment C', '2026-01-15', 23.8)
        """)

    # 4. Add research notes
    (binder_path / "note1.md").write_text("""---
title: Initial Findings
date: 2026-01-10
author: Dr. Smith
tags: [experiment, findings]
---

# Initial Findings

Our first experiment showed promising results...
""")

    (binder_path / "note2.md").write_text("""---
title: Follow-up Analysis
date: 2026-01-15
author: Dr. Smith
tags: [analysis, results]
---

# Follow-up Analysis

Further analysis revealed...
""")

    # 5. Validate structure
    report = BinderValidator.validate(binder_path)
    print(f"Validation: {'✓ Valid' if report.is_valid else '✗ Invalid'}")

    # 6. Query database
    with BinderDatabase(binder_path) as db:
        results = db.query("""
            SELECT name, date, result
            FROM experiments
            ORDER BY date DESC
        """)
        print(f"\nExperiments ({len(results)}):")
        for row in results:
            print(f"  {row['name']}: {row['result']} ({row['date']})")

    # 7. Generate feed
    feed = BinderFeed(binder_path, base_url="https://research.example.com")
    items = feed.scan_files()
    print(f"\nArticles ({len(items)}):")
    for item in items:
        print(f"  {item.title} by {item.author or 'Unknown'}")

    # Save feeds
    rss = feed.generate_rss()
    feed.save_feed(binder_path / "feed.xml", rss)

    json_feed = feed.generate_json()
    import json
    (binder_path / "feed.json").write_text(json.dumps(json_feed, indent=2))

    print(f"\n✓ Binder created at: {binder_path}")
    print(f"✓ Database: {binder_path / 'uDOS-table.db'}")
    print(f"✓ RSS feed: {binder_path / 'feed.xml'}")
    print(f"✓ JSON feed: {binder_path / 'feed.json'}")

if __name__ == "__main__":
    create_research_binder()
```

---

## API Reference

### BinderConfig

```python
@dataclass
class BinderConfig:
    name: str                    # Binder display name
    version: str                 # Semantic version
    created_at: datetime         # Creation timestamp
    author: Optional[str]        # Author name
    description: Optional[str]   # Description
    tags: List[str]              # Organization tags
    path: Optional[Path]         # Set during load

# Functions
load_binder_config(binder_path: Path) -> BinderConfig
save_binder_config(config: BinderConfig, binder_path: Optional[Path]) -> Path
```

### BinderValidator

```python
class BinderValidator:
    @staticmethod
    def validate(binder_path: Path) -> ValidationReport

@dataclass
class ValidationReport:
    is_valid: bool
    binder_path: Path
    issues: List[ValidationIssue]

    def has_critical() -> bool
    def has_warnings() -> bool
    def summary() -> str
```

### BinderDatabase

```python
class BinderDatabase:
    def __init__(self, binder_path: Path, mode: AccessMode = AccessMode.READ_WRITE)

    # Context manager
    def __enter__() -> BinderDatabase
    def __exit__(exc_type, exc_val, exc_tb)

    # Query methods
    def query(sql: str, params: Optional[tuple]) -> List[Dict[str, Any]]
    def execute(sql: str, params: Optional[tuple]) -> int

    # Utility methods
    def table_exists(table_name: str) -> bool
    def get_schema(table_name: str) -> List[Dict]
    def list_tables() -> List[str]

class AccessMode(Enum):
    READ_ONLY = "readonly"    # SELECT only
    READ_WRITE = "readwrite"  # + INSERT, UPDATE, DELETE
    FULL = "full"             # + CREATE, DROP, ALTER
```

### BinderFeed

```python
class BinderFeed:
    def __init__(self, binder_path: Path, base_url: Optional[str] = None)

    # Scan and generate
    def scan_files(pattern: str = "*.md") -> List[FeedItem]
    def generate_rss(items: Optional[List[FeedItem]]) -> str
    def generate_json(items: Optional[List[FeedItem]]) -> Dict

    # Save feeds
    def save_feed(output_path: Path, content: str, format: FeedFormat)

@dataclass
class FeedItem:
    title: str
    url: str
    content_preview: str
    date: datetime
    author: Optional[str]
    tags: List[str]
    guid: str

class FeedFormat(Enum):
    RSS_2_0 = "rss"
    JSON_FEED = "json"
```

---

## Common Patterns

### Pattern 1: Import CSV Data

```python
with BinderDatabase(binder_path) as db:
    # Create table from CSV structure
    db.execute("""
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category TEXT,
            phone TEXT
        )
    """)

    # Import from CSV
    import csv
    csv_path = binder_path / "imports" / "items.csv"
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.execute(
                "INSERT INTO items (name, category, phone) VALUES (?, ?, ?)",
                (row['name'], row['category'], row['phone'])
            )
```

### Pattern 2: Export to Markdown Table

```python
with BinderDatabase(binder_path) as db:
    results = db.query("SELECT * FROM items ORDER BY name")

    # Generate markdown table
    md_lines = ["# Items\n", "| Name | Category | Phone |", "|------|----------|-------|"]
    for row in results:
        md_lines.append(f"| {row['name']} | {row['category']} | {row['phone']} |")

    # Save to tables folder
    (binder_path / "tables" / "items.table.md").write_text("\n".join(md_lines))
```

### Pattern 3: Update Config

```python
# Load existing config
config = load_binder_config(binder_path)

# Modify fields
config.description = "Updated description"
config.tags.append("new-tag")

# Save changes
save_binder_config(config, binder_path)
```

### Pattern 4: Feed with Custom Sorting

```python
feed = BinderFeed(binder_path)

# Scan and customize
items = feed.scan_files()

# Filter and sort
research_items = [item for item in items if "research" in item.tags]
research_items.sort(key=lambda x: x.title)  # Sort by title instead of date

# Generate custom feed
rss_xml = feed.generate_rss(items=research_items)
```

---

## Troubleshooting

### Issue: "Binder path does not exist"
**Solution:** Ensure folder exists: `Path("./MyBinder").mkdir(exist_ok=True)`

### Issue: "Missing required file: uDOS-table.db"
**Solution:** Create empty database: `(binder_path / "uDOS-table.db").touch()`

### Issue: "Invalid binder config file"
**Solution:** Delete `.binder-config` to auto-generate, or fix JSON syntax

### Issue: "No items in feed"
**Solution:** Ensure markdown files have valid YAML frontmatter with `title` field

### Issue: "Database is locked"
**Solution:** Close all connections before opening new ones, or use `AccessMode.READ_ONLY`

---

## Performance Notes

**Based on benchmarks** (M1/M2 Mac, Python 3.12):

- **Feed Scanning:** 100 markdown files in < 1 second
- **RSS Generation:** 100 items in < 0.5 seconds
- **JSON Generation:** 100 items in < 0.5 seconds
- **Database Queries:** 1000 rows in < 0.1 seconds

**Recommendations:**
- Use `AccessMode.READ_ONLY` when possible (faster)
- Batch database insertions (use transactions)
- Cache feed results when displaying multiple times
- Use indexes on frequently queried columns

---

## See Also

- Integration Tests: `core/tests/test_binder_integration_v1_0_6.py`
- Unit Tests: `core/tests/test_binder_*.py`
- Phase 3 Documentation: `docs/devlog/2026-01-17-phase-3-*.md`
- Roadmap: `docs/roadmap.md`

---

**Last Updated:** 2026-01-17
**Author:** uDOS Team
