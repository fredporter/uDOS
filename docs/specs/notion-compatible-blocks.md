# Notion-Compatible Block Architecture

**Purpose:** Design uDOS markdown blocks to align with Notion's block API for seamless sync  
**Scope:** Move 1 (Notion Integration) and beyond  
**Status:** Specification  
**Date:** 2026-01-15  
**See Also:** [Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md) | [TypeScript Runtime Standards](typescript-runtime-database-standards.md)

---

## Overview

Notion has ~30+ block types (see [Notion Block Reference](https://developers.notion.com/reference/block)). We're designing uDOS runtime blocks to map cleanly to Notion's structure for bidirectional sync.

**Core Insight:** Markdown code fence language tags → Notion block types

This specification covers the design. For implementation details including DB binding and variable metadata, see [Move 1: Runtime Blocks + Notion Sync](move-1-runtime-blocks-notion-sync.md).

---

## Block Type Mapping

### Standard Markdown → Notion Blocks

| Markdown                | Notion Type          | uDOS Block            | Example                     |
| ----------------------- | -------------------- | --------------------- | --------------------------- |
| `# Heading`             | `heading_1`          | `### H1: Title`       | `# My Page`                 |
| `## Heading`            | `heading_2`          | `### H2: Section`     | `## Introduction`           |
| `### Heading`           | `heading_3`          | `### H3: Subsection`  | `### Details`               |
| `> Quote`               | `quote`              | `### QUOTE: Text`     | `> Famous quote`            |
| `- Item`                | `bulleted_list_item` | `### LIST: Items`     | `- First\n- Second`         |
| `1. Item`               | `numbered_list_item` | `### NUMLIST: Items`  | `1. First\n2. Second`       |
| `- [ ] Item`            | `to_do`              | `### TODO: Items`     | `- [ ] Task`                |
| `[Text](URL)`           | `bookmark` (Notion)  | `### LINK: URL`       | `[GitHub](https://...)`     |
| `\`code\``              | `code` (inline)      | Rich text annotation  | `\`const x = 1\``           |
| `\`\`\`js\n...\n\`\`\`` | `code` (block)       | `### CODE: Lang\n...` | ` ```js\nconst x = 1\n``` ` |
| `![Alt](URL)`           | `image`              | `### IMAGE: URL`      | `![desc](img.png)`          |
| Regular text            | `paragraph`          | `### PARA: Text`      | Prose paragraphs            |
| `---`                   | `divider`            | `### DIVIDER`         | Horizontal rule             |

### uDOS Runtime Blocks (Executable)

| Block Type | Notion Mapping            | Purpose             | Syntax                        |
| ---------- | ------------------------- | ------------------- | ----------------------------- |
| **STATE**  | `code` + metadata         | Declare variables   | `\`\`\`state name: type\n...` |
| **SET**    | `code` + metadata         | Assign values       | `\`\`\`set var = expr`        |
| **FORM**   | `code` + metadata         | Collect input       | `\`\`\`form fields...`        |
| **IF**     | `toggle` (collapsible)    | Conditional block   | `\`\`\`if condition\n...`     |
| **NAV**    | `callout` (link metadata) | Navigation/buttons  | `\`\`\`nav [[Chapter]]`       |
| **PANEL**  | `column_list` + `column`s | Multi-column layout | `\`\`\`panel cols=2\n...`     |
| **MAP**    | `table` (data grid)       | Data transformation | `\`\`\`map data...`           |

---

## Markdown Syntax Examples

### 1. Basic Markdown (Notion-Compatible)

```markdown
# Project Overview

This is a paragraph with **bold** and _italic_ text.

## Section One

> This is a blockquote, like Notion's quote block

- Bulleted item 1
- Bulleted item 2

1. Numbered item 1
2. Numbered item 2

- [ ] Todo item 1
- [x] Completed item 1

[Link text](https://example.com)

![Image alt](https://example.com/img.png)

---
```

### 2. Runtime Blocks (Executable)

#### STATE - Declare Variables

````markdown
```state
name: string = "Alice"
age: number = 30
active: boolean = true
items: string[] = ["apple", "banana"]
```
````

````

Maps to Notion `code` block with special metadata:
```json
{
  "type": "code",
  "code": {
    "language": "typescript",
    "rich_text": [{ "text": { "content": "name: string = \"Alice\"\nage: number = 30\n..." } }],
    "caption": [{ "text": { "content": "[uDOS Runtime: STATE]" } }]
  }
}
````

#### SET - Assign Values

````markdown
```set
name = "Bob"
age = age + 1
items = [...items, "cherry"]
```
````

````

Maps to Notion `code` block with assignment metadata.

#### FORM - Collect User Input

```markdown
```form
name: string @required
email: string @email
category: "work" | "personal" | "hobby" @select
subscribe: boolean @checkbox
````

````

Maps to Notion with embedded form metadata (interactive in Goblin, becomes form in Notion).

#### IF - Conditional Logic (Toggle in Notion)

```markdown
```if age >= 18
  You are an adult.

  ## Adult-Only Content

  Details here...
````

````

Maps to Notion `toggle` block (collapsible heading):
```json
{
  "type": "heading_2",
  "heading_2": {
    "rich_text": [{ "text": { "content": "if age >= 18" } }],
    "is_toggleable": true
  },
  "children": [...]
}
````

#### NAV - Navigation/Links

````markdown
```nav
[← Previous Chapter](../chapter-1)
[Next Chapter →](../chapter-3)
[[Jump to Section]]
```
````

````

Maps to Notion `callout` with button metadata:
```json
{
  "type": "callout",
  "callout": {
    "rich_text": [{ "text": { "content": "← Previous | Next →" } }],
    "icon": { "emoji": "🧭" }
  }
}
````

#### PANEL - Multi-Column Layout

````markdown
```panel cols=2
Column 1 content here

---

Column 2 content here
```
````

````

Maps to Notion `column_list` with `column` children:
```json
{
  "type": "column_list",
  "column_list": {},
  "children": [
    { "type": "column", "column": { "width_ratio": 0.5 }, "children": [...] },
    { "type": "column", "column": { "width_ratio": 0.5 }, "children": [...] }
  ]
}
````

#### MAP - Data Transformation

````markdown
```map
input: items
transform: item.toUpperCase()
output: uppercase_items
```
````

````

Maps to Notion `table` with data transformation metadata.

---

## Implementation Strategy

### Phase 1: Markdown ↔ Notion Sync (Move 1)

1. **Parse uDOS Markdown** → Extract blocks + metadata
2. **Transform to Notion Blocks** → Map to Notion API structure
3. **Notion Webhook** → Receive block updates
4. **Transform Back to Markdown** → Update local .md files
5. **SQLite Queue** → Handle conflicts, retry failures

### Phase 2: Runtime Execution (Move 2)

1. **Parse Runtime Blocks** → Extract state, form, if conditions
2. **Execute in Sandbox** → Python runtime (Goblin server)
3. **Update State** → Variables, objects, arrays
4. **Render Output** → Updated markdown with results

### Phase 3: Mobile TypeScript Runtime (v1.0.3.0)

1. **Parse Runtime Blocks** → Extract executable code
2. **Execute in TypeScript Sandbox** → Native iOS/iPadOS
3. **Offline State** → SQLite storage
4. **Sync with Desktop** → MeshCore when online

---

## Notion Sync Details

### Block to Notion Conversion

**Example: uDOS Form Block → Notion**

Input markdown:
```markdown
```form
name: string @required
email: string @email
````

````

Notion API payload:
```json
{
  "object": "block",
  "type": "code",
  "code": {
    "language": "typescript",
    "rich_text": [
      { "type": "text", "text": { "content": "// uDOS Form Block\nname: string @required\nemail: string @email" } }
    ],
    "caption": [
      { "type": "text", "text": { "content": "[uDOS:FORM] Collect user data" } }
    ]
  }
}
````

### Notion to Markdown Conversion

**Example: Notion Paragraph + Code → uDOS**

Notion blocks:

```json
[
  {
    "type": "paragraph",
    "paragraph": { "rich_text": [{ "text": { "content": "User data:" } }] }
  },
  {
    "type": "code",
    "code": {
      "language": "json",
      "rich_text": [
        {
          "text": {
            "content": "{ \"name\": \"Alice\", \"email\": \"alice@example.com\" }"
          }
        }
      ]
    }
  }
]
```

Markdown output:

````markdown
User data:

```json
{ "name": "Alice", "email": "alice@example.com" }
```
````

````

---

## Schema for Goblin Dev Server

### NotionSyncService

```python
# dev/goblin/services/notion_sync_service.py

class BlockMapping:
    """Maps uDOS markdown blocks ↔ Notion API blocks"""

    markdown_to_notion: Dict[str, str] = {
        "state": "code",      # Special metadata
        "set": "code",        # Special metadata
        "form": "code",       # Special metadata
        "if": "toggle",       # is_toggleable=true
        "nav": "callout",     # Button metadata
        "panel": "column_list",
        "map": "table",
    }

    def parse_umarkdown(self, content: str) -> List[Block]:
        """Extract blocks from uDOS markdown"""
        pass

    def to_notion_blocks(self, blocks: List[Block]) -> List[Dict]:
        """Convert uDOS blocks to Notion API format"""
        pass

    def from_notion_blocks(self, notion_blocks: List[Dict]) -> str:
        """Convert Notion blocks back to markdown"""
        pass

class NotionSyncService:
    """Handle Notion webhooks and bidirectional sync"""

    async def handle_webhook(self, payload: Dict) -> None:
        """Process incoming Notion page changes"""
        pass

    async def sync_page_to_notion(self, page_id: str, content: str) -> None:
        """Upload markdown content to Notion page"""
        pass

    async def sync_page_from_notion(self, page_id: str) -> str:
        """Download page from Notion, return markdown"""
        pass

    async def resolve_conflict(self, local: str, notion: str) -> str:
        """Merge conflicting changes"""
        pass
````

---

## Benefits

✅ **Notion Compatibility** — Move 1 data syncs bidirectionally  
✅ **Familiar Structure** — Notion users recognize block types  
✅ **Future-Proof** — Easily map new block types as Notion adds them  
✅ **Clean Separation** — Standard markdown vs executable blocks  
✅ **Mobile Ready** — TypeScript runtime executes same blocks offline

---

## References

- [Notion Block API](https://developers.notion.com/reference/block)
- [Rich Text Objects](https://developers.notion.com/reference/rich-text)
- [Move 1 Plan](../roadmap.md#move-1-notion-sync-integration-python-based)
- [Goblin Dev Server](../../dev/goblin/README.md)

---

_This specification ensures uDOS markdown blocks are Notion-native from the start._
