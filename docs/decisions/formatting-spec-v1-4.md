Here’s a **comprehensive plan** for integrating the `.compost` subfolder for versioning, and adding **Marp MD slide formatting** and **advanced table/grid conversion** to your processing pipeline. This will ensure **universal formatting**, **version control**, and **multi-format output** (standard MD + Marp slides).

---

## **1. `.compost` Subfolder: Versioning & Archival**
### **Purpose**
- Store **previous versions** of processed files (MD/JSON) as they evolve.
- Act as a **hidden/archival-elastic-trash-backup** for recovery or audit trails.
- Use **timestamped filenames** for easy tracking.

### **Structure**
```
vault/
├── .compost/
│   ├── [timestamp]_[original_filename].md
│   ├── [timestamp]_[original_filename].json
│   └── ...
├── @binders/
├── @user/
└── ...
```

### **Rules**
- **Trigger:** Every time a file is processed/updated, save the **previous version** to `.compost`.
- **Naming:**
  - Format: `[YYYYMMDD_HHMMSS]_[original_filename].[ext]`
  - Example: `20260220_143022_meeting_notes.md`
- **Retention:**
  - Keep last **10 versions** by default (configurable).
  - Older versions are **compressed** (e.g., `.zip`) or moved to cold storage.

**Example (Python):**
```python
import os
import shutil
from datetime import datetime

def archive_to_compost(original_path, vault_path):
    compost_path = os.path.join(vault_path, ".compost")
    os.makedirs(compost_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(original_path)
    archive_name = f"{timestamp}_{filename}"
    shutil.copy2(original_path, os.path.join(compost_path, archive_name))
    # Keep only last 10 versions
    versions = sorted(os.listdir(compost_path), reverse=True)
    for old_version in versions[10:]:
        os.remove(os.path.join(compost_path, old_version))
```

---

## **2. Marp MD Slide Formatting**
### **Goal**
Convert standard MD to **Marp-compatible slide decks** with:
- **Slide breaks** (`---`).
- **Slide-specific metadata** (e.g., `class: lead`).
- **Optimized content layout** (headers, lists, images, tables).

### **Processing Rules**
#### **A. Slide Breaks**
- **Trigger:** Major headers (`#`, `##`) or explicit `<!-- slide -->` comments.
- **Output:** Insert `---` between slides.

**Example:**
```markdown
# Slide 1
Content for slide 1.

---
# Slide 2
Content for slide 2.
```

#### **B. Metadata**
- Add Marp directives at the top:
  ```markdown
  ---
  marp: true
  theme: default
  class: lead
  ---
  ```

#### **C. Content Adaptation**
| MD Element       | Marp Slide Rule                                                                 | Example Output                     |
|------------------|---------------------------------------------------------------------------------|------------------------------------|
| Headers          | `#` → Slide title; `##` → Sub-slide.                                             | `# Welcome` → Slide title.         |
| Lists             | Preserve as-is; use fragments (`<!-- _class: fragment -->`) for animations.     | `- Item 1` → Bullet point.         |
| Images            | Center-align; add `<!-- _class: invert -->` for dark mode.                      | `![image](url)` → Centered image.  |
| Tables            | Convert to grid layout; use `<!-- _class: smaller -->` for compact tables.      | See table section below.          |
| Code Blocks       | Add `<!-- _class: code -->` for syntax highlighting.                            | ```python\nprint("Hello")```      |

**Example (Marp MD):**
```markdown
---
marp: true
theme: default
---

# Project Update
**Speaker:** Jane Doe

---
## Tasks
- Review timeline <!-- _class: fragment -->
- Send feedback <!-- _class: fragment -->

---
## Budget Table
<!-- _class: smaller -->

| Item   | Cost  |
|--------|-------|
| Design | $1000 |
| Dev    | $2000 |
```

---

## **3. Advanced Table/Grid Conversion**
### **Goal**
Convert **MD tables** and **HTML grids** into:
- **Standard MD tables** (for notes).
- **Marp-optimized grids** (for slides).
- **JSON arrays** (for structured data).

### **Processing Rules**
#### **A. MD Tables → Marp Grids**
- **Input:**
  ```markdown
  | Name  | Role      |
  |-------|-----------|
  | Alice | Designer  |
  | Bob   | Developer |
  ```
- **Output (Marp):**
  ```markdown
  <!-- _class: smaller -->
  | Name  | Role      |
  |-------|-----------|
  | Alice | Designer  |
  | Bob   | Developer |
  ```

#### **B. HTML Tables → MD/JSON**
- **Input (HTML):**
  ```html
  <table>
    <tr><th>Name</th><th>Role</th></tr>
    <tr><td>Alice</td><td>Designer</td></tr>
  </table>
  ```
- **Output (MD):**
  ```markdown
  | Name  | Role    |
  |-------|---------|
  | Alice | Designer|
  ```
- **Output (JSON):**
  ```json
  {
    "table": {
      "headers": ["Name", "Role"],
      "rows": [
        ["Alice", "Designer"],
        ["Bob", "Developer"]
      ]
    }
  }
  ```

**Example (Python):**
```python
import pandas as pd
from bs4 import BeautifulSoup

def html_table_to_md(html):
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    df = pd.read_html(str(table))[0]
    return df.to_markdown(index=False)

def md_table_to_json(md_table):
    lines = md_table.split("\n")
    headers = [h.strip() for h in lines[0].split("|") if h.strip()]
    rows = [[c.strip() for c in line.split("|") if c.strip()] for line in lines[2:]]
    return {"headers": headers, "rows": rows}
```

---

## **4. Integrated Workflow**
### **Step-by-Step Pipeline**
1. **Input:** MD/HTML file (e.g., `notes.md`).
2. **Preprocess:**
   - Clean text (remove noise, normalize encoding).
   - Archive previous version to `.compost`.
3. **Parse:**
   - Extract headers, lists, tables, links.
4. **Transform:**
   - Generate **standard MD** and **Marp MD** versions.
   - Convert tables to MD/JSON.
5. **Output:**
   - Save standard MD to original path.
   - Save Marp MD to `vault/@binders/[project]/slides/[filename].marp.md`.
   - Save JSON to `vault/@binders/[project]/data/[filename].json`.
6. **Postprocess:**
   - Link to `moves.json`/`contacts.json` if actionable.
   - Validate output.

**Example:**
```
vault/
├── .compost/
│   └── 20260220_143022_notes.md
├── @binders/
│   └── project_x/
│       ├── notes.md          # Standard MD
│       ├── slides/
│       │   └── notes.marp.md # Marp slides
│       └── data/
│           └── notes.json    # Structured data
└── ...
```

---

## **5. Edge Cases & Validation**
| Case                          | Rule                                                                 |
|-------------------------------|----------------------------------------------------------------------|
| **Nested lists**              | Indent with 4 spaces (MD) or use fragments (Marp).                  |
| **Multi-line cells in tables**| Use `<br>` (HTML) or split into multiple rows (MD).                 |
| **Missing headers in tables** | Auto-generate headers (e.g., "Column 1", "Column 2").               |
| **Empty slides**              | Skip or add placeholder (e.g., `# [Empty Slide]`).                   |
| **Duplicate versions**       | Overwrite `.compost` entry if timestamp collides (unlikely).         |

---

## **6. Tools & Libraries**
| Task                     | Tool/Library               | Notes                                  |
|--------------------------|----------------------------|----------------------------------------|
| Versioning               | `shutil`, `os`, `datetime` | Handle file archival.                  |
| MD ↔ Marp                | Custom scripts             | Add slide breaks/metadata.             |
| HTML → MD/JSON           | `BeautifulSoup`, `pandas`  | Parse tables, clean HTML.              |
| Table Processing         | `tabulate`, `json`         | Convert to MD/JSON.                    |
| Validation               | `jsonschema`, `pytest`     | Ensure output consistency.             |

---

## **7. Example Script (MD → Marp + JSON)**
```python
import os
import re
import json
from datetime import datetime

def md_to_marp(md_content):
    # Add Marp metadata
    marp_content = "---\nmarp: true\ntheme: default\n---\n\n"
    # Split slides on # headers
    slides = re.split(r'\n# ', md_content)
    for i, slide in enumerate(slides):
        if i > 0:
            marp_content += "# " + slide + "\n---\n"
        else:
            marp_content += slide + "\n"
    return marp_content

def md_to_json(md_content):
    data = {"content": md_content}
    # Extract tables, lists, etc. (simplified)
    return json.dumps(data, indent=2)

def process_file(filepath, vault_path):
    # 1. Archive to .compost
    archive_to_compost(filepath, vault_path)
    # 2. Read and convert
    with open(filepath, "r") as f:
        md_content = f.read()
    marp_content = md_to_marp(md_content)
    json_content = md_to_json(md_content)
    # 3. Save outputs
    base = os.path.splitext(filepath)[0]
    with open(f"{base}.marp.md", "w") as f:
        f.write(marp_content)
    with open(f"{base}.json", "w") as f:
        f.write(json_content)

# Usage
process_file("vault/@binders/project_x/notes.md", "vault")
```

---

## **8. Implementation Status (uDOS v1.4.4)**

### **Completed (2026-02-21)**
- [x] `.compost` archival system implemented in `core/services/spatial_filesystem.py`
- [x] Automatic versioning with timestamp-based filenames
- [x] Retention policy (keep last 10 versions)
- [x] Marp conversion implemented in `core/services/formatting_service.py`
- [x] Table extraction and JSON conversion implemented
- [x] Vibe skill integration: `process_and_format_document()`

### **In Progress**
- [ ] HTML table parsing and conversion
- [ ] Advanced nested list handling in Marp slides
- [ ] Slide metadata customization (themes, classes)
- [ ] Validation framework for edge cases

### **Next Steps**
1. **Expand format support** for literary/book content formatting.
2. **Develop the complete Marp conversion** with complex MD support (nested lists, code blocks).
3. **Integrate HTML table processing** using BeautifulSoup and pandas.
4. **Add comprehensive validation** for edge cases (empty slides, malformed tables).
5. **Document the workflow** for Obsidian/uDOS integration with examples.

---

## **1. Expanded Format Support**
### **A. Literary/Book/Content Formatting**
**Goal:** Structure long-form content (books, articles, reports) with clear hierarchies for sections, chapters, and paragraphs.

#### **Rules:**
- **Top-Level:** `# Chapter` or `# Section`
- **Sub-Level:** `## Subsection`, `### Paragraph`
- **Metadata:** Frontmatter for author, date, tags.
- **Blockquotes:** For quotes, notes, or asides.
- **Footnotes:** `[^1]` syntax for references.

**Example (MD):**
```markdown
---
title: "The Great Project"
author: "Fred Porter"
date: "2026-02-20"
tags: ["guide", "workflow"]
---

# Chapter 1: Introduction
## Background
This section covers the history and context.

### Key Points
- Point 1
- Point 2

> "This is a critical insight."
> — Expert, 2026

[^1]: Reference to source.
```

---

### **B. Paragraph/Subheading Hierarchies**
**Goal:** Ensure readability and logical flow for both linear and non-linear content.

#### **Rules:**
- **Paragraphs:** Separated by blank lines.
- **Subheadings:** `##`, `###`, `####` for nested topics.
- **Inline Formatting:** **Bold**, *italics*, `code`, ~~strikethrough~~.
- **Lists:** `- ` for bullets, `1. ` for numbered.

**Example:**
```markdown
## Core Concepts
### Definition
This is a **key term** in *italics*.

#### Example
1. Step 1
2. Step 2

- Bullet point 1
- Bullet point 2
```

---

### **C. ucode STORY Format**
**Goal:** Create **interactive, advancable slides** (like Marp) with **Typeform-style input fields** (e.g., text inputs, multiple choice, buttons).

#### **Rules:**
- **Slide Breaks:** `---` (same as Marp).
- **Input Fields:**
  - `<!-- input:text -->` for text input.
  - `<!-- input:choice -->` for multiple choice.
  - `<!-- input:button -->` for navigation.
- **Metadata:** Define input types and validation.
- **State Management:** Track user responses (optional JSON output).

**Example (ucode STORY):**
```markdown
---
ucode: true
type: story
---

# Welcome
<!-- input:text -->
Enter your name: [__________]

---
# Choose Your Path
<!-- input:choice -->
- [ ] Option A
- [ ] Option B

---
# Confirmation
<!-- input:button -->
[Next](#)

---
# Summary
Your choices:
- Name: {{input1}}
- Path: {{input2}}
```

---

## **2. Processing Pipeline Updates**
### **A. Input Detection**
- Detect format based on:
  - Frontmatter (`---` block).
  - Special comments (`<!-- input:text -->`).
  - File extension (`.story.md`, `.book.md`).

### **B. Conversion Rules**
| Input Type          | Output Format          | Transformation Rules                                                                 |
|---------------------|------------------------|--------------------------------------------------------------------------------------|
| Literary MD         | Standard MD/JSON       | Preserve hierarchy, metadata, and footnotes.                                         |
| Paragraph/Subheading| Standard MD/Marp       | Ensure heading levels are consistent; convert to slides if needed.                   |
| ucode STORY         | Interactive MD/JSON    | Parse input fields; generate interactive JSON for apps.                              |
| HTML                | All of the above       | Convert to MD first, then apply format-specific rules.                               |

---

### **C. `.compost` Versioning**
- Archive **all versions** of all formats (`.md`, `.story.md`, `.json`).
- Use **timestamp + format suffix**:
  - `20260220_143022_notes.md`
  - `20260220_143022_notes.story.md`
  - `20260220_143022_notes.json`

---

## **3. ucode STORY: Technical Deep Dive**
### **A. Input Field Syntax**
| Field Type       | Syntax                     | Example Output (MD)               | JSON Representation                          |
|------------------|----------------------------|------------------------------------|---------------------------------------------|
| Text Input       | `<!-- input:text -->`      | `Enter your name: [__________]`   | `"type": "text", "prompt": "Enter your name"` |
| Multiple Choice   | `<!-- input:choice -->`    | `- [ ] Option A`                  | `"type": "choice", "options": ["A", "B"]`     |
| Button           | `<!-- input:button -->`    | `[Next](#)`                       | `"type": "button", "label": "Next"`          |

### **B. State Management**
- **User responses** are stored in a **JSON object**:
  ```json
  {
    "responses": {
      "slide1": {"input1": "Fred"},
      "slide2": {"input2": "Option A"}
    }
  }
  ```
- **Integration:** Link to `moves.json` for task tracking.

---

### **C. Example: ucode STORY → JSON**
**Input (MD):**
```markdown
---
ucode: true
type: story
---

# Welcome
<!-- input:text -->
What’s your project name? [__________]

---
# Next Steps
<!-- input:choice -->
- [ ] Start now
- [ ] Schedule for later
```

**Output (JSON):**
```json
{
  "type": "story",
  "slides": [
    {
      "title": "Welcome",
      "inputs": [
        {
          "type": "text",
          "prompt": "What’s your project name?",
          "id": "input1"
        }
      ]
    },
    {
      "title": "Next Steps",
      "inputs": [
        {
          "type": "choice",
          "options": ["Start now", "Schedule for later"],
          "id": "input2"
        }
      ]
    }
  ]
}
```

---

## **4. Integration with Obsidian/uDOS**
### **A. File Structure**
```
vault/
├── .compost/
├── @binders/
│   └── project_x/
│       ├── content/
│       │   ├── book.md          # Literary format
│       │   ├── slides.story.md  # ucode STORY
│       │   └── data.json         # Structured data
│       ├── moves.json           # Tasks
│       └── contacts.json        # Linked contacts
└── @user/
```

### **B. Workflow**
1. **Input:** User uploads/creates a file (MD, HTML, etc.).
2. **Detect Format:** Check frontmatter/comments.
3. **Process:**
   - Clean → Parse → Transform → Validate.
4. **Output:**
   - Save to appropriate format (`.md`, `.story.md`, `.json`).
   - Archive previous version to `.compost`.
5. **Link:**
   - Update `moves.json`/`contacts.json` if actionable.

---

## **5. Tools & Libraries**
| Task                     | Tool/Library          | Notes                                  |
|--------------------------|-----------------------|----------------------------------------|
| Format Detection         | Custom regex/frontmatter parser | Detect `ucode`, `marp`, etc.          |
| MD ↔ ucode STORY         | Custom scripts        | Handle input fields and state.         |
| HTML → Literary MD       | `BeautifulSoup`       | Clean and structure long-form content.|
| Versioning               | `shutil`, `os`        | Archive to `.compost`.                |
| JSON State Management    | `json`, `uuid`         | Track user inputs.                    |

---

## **6. Example Script: Format Conversion**
```python
import os
import re
import json
from datetime import datetime

def detect_format(content):
    if "ucode: true" in content:
        return "story"
    elif "# " in content and "\n---" in content:
        return "marp"
    elif re.search(r'^\s*# ', content, re.MULTILINE):
        return "literary"
    else:
        return "standard"

def convert_to_story(md_content):
    story_content = "---\nucode: true\ntype: story\n---\n\n"
    slides = re.split(r'\n---', md_content)
    for slide in slides:
        story_content += f"{slide}\n---\n"
    return story_content

def process_file(filepath, vault_path):
    with open(filepath, "r") as f:
        content = f.read()
    format_type = detect_format(content)
    if format_type == "story":
        output = convert_to_story(content)
    elif format_type == "marp":
        output = content  # Already in slide format
    else:
        output = f"---{content}"  # Add frontmatter for literary
    # Save and archive
    base, ext = os.path.splitext(filepath)
    output_path = f"{base}.{format_type}.md"
    with open(output_path, "w") as f:
        f.write(output)
    archive_to_compost(filepath, vault_path)

# Usage
process_file("vault/@binders/project_x/notes.md", "vault")
```

---

## **7. Next Steps**
1. **Prototype the format detector** and test with sample files.
2. **Develop ucode STORY parser** and JSON generator.
3. **Integrate with `.compost`** for versioning.
4. **Test edge cases** (nested inputs, malformed MD).
5. **Document templates** for literary, paragraph, and ucode formats.

---

## **1. Supported Import Formats**
| Format   | Open-Source Tool/Library       | Output Targets                     | Notes                                  |
|----------|--------------------------------|------------------------------------|----------------------------------------|
| **DOCX** | `python-docx`, `pandoc`        | MD, JSON, ucode STORY              | Preserve headings, lists, tables.      |
| **XLSX** | `openpyxl`, `pandas`           | MD tables, JSON arrays             | Convert sheets to tables/data.         |
| **PDF**  | `pdfplumber`, `PyPDF2`, `pandoc` | MD, JSON (text/images as links)    | Extract text, tables, and metadata.   |
| **PPTX** | `python-pptx`, `pandoc`        | Marp MD, ucode STORY, JSON         | Slides → Marp/ucode slides.            |
| **EPUB** | `ebooklib`, `pandoc`           | Literary MD, JSON                  | Chapters → MD sections.                |
| **HTML** | `BeautifulSoup`, `pandoc`      | MD, JSON, ucode STORY              | Clean and structure content.          |

---

## **2. Import Pipeline**
### **A. Overview**
1. **Detect Format:** Check file extension or MIME type.
2. **Preprocess:** Clean and normalize raw content.
3. **Convert:** Use format-specific tools to extract structured data.
4. **Transform:** Map to your target formats (MD/JSON/ucode STORY).
5. **Postprocess:** Validate, link to uDOS workflows, and archive to `.compost`.

### **B. Flowchart**
```
Input File (DOCX/PPTX/PDF/...)
       ↓
Detect Format → Preprocess → Convert → Transform → Postprocess
       ↓
Output: MD/JSON/ucode STORY + .compost versioning
```

---

## **3. Format-Specific Rules**
### **A. DOCX → MD/JSON/ucode STORY**
**Tools:** `python-docx`, `pandoc`
**Rules:**
- **Headings:** `Heading 1` → `#`, `Heading 2` → `##`, etc.
- **Lists:** Convert to `- ` or `1.`.
- **Tables:** Convert to MD tables or JSON arrays.
- **Images:** Save to `vault/@binders/[project]/assets/` and link in MD.
- **Metadata:** Extract author, date, title from doc properties.

**Example (Python):**
```python
from docx import Document
import json

def docx_to_md(docx_path):
    doc = Document(docx_path)
    md_content = ""
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            level = int(para.style.name.split(' ')[1])
            md_content += f"{'#' * level} {para.text}\n\n"
        else:
            md_content += f"{para.text}\n\n"
    return md_content

def docx_to_json(docx_path):
    doc = Document(docx_path)
    data = {"content": []}
    for para in doc.paragraphs:
        data["content"].append({
            "type": "paragraph" if not para.style.name.startswith('Heading') else "heading",
            "text": para.text,
            "level": int(para.style.name.split(' ')[1]) if para.style.name.startswith('Heading') else None
        })
    return json.dumps(data, indent=2)
```

---

### **B. XLSX → MD/JSON**
**Tools:** `openpyxl`, `pandas`
**Rules:**
- **Sheets:** Each sheet → MD table or JSON array.
- **Headers:** First row → table headers.
- **Formulas:** Evaluate and include as values.

**Example:**
```python
import pandas as pd

def xlsx_to_md(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name=None)
    md_content = ""
    for sheet_name, sheet in df.items():
        md_content += f"## {sheet_name}\n\n"
        md_content += sheet.to_markdown() + "\n\n"
    return md_content

def xlsx_to_json(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name=None)
    return json.dumps({sheet: df[sheet].to_dict(orient="records") for sheet in df})
```

---

### **C. PDF → MD/JSON**
**Tools:** `pdfplumber`, `PyPDF2`, `pandoc`
**Rules:**
- **Text:** Extract and structure by headings/paragraphs.
- **Tables:** Convert to MD tables or JSON.
- **Images:** Save to `assets/` and link in MD.
- **Metadata:** Extract title, author, date.

**Example:**
```python
import pdfplumber

def pdf_to_md(pdf_path):
    md_content = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            tables = page.extract_tables()
            md_content += f"{text}\n\n"
            for table in tables:
                md_content += "| " + " | ".join(table[0]) + " |\n"
                md_content += "| " + " | ".join(["---"] * len(table[0])) + " |\n"
                for row in table[1:]:
                    md_content += "| " + " | ".join(row) + " |\n"
    return md_content
```

---

### **D. PPTX → Marp/ucode STORY/JSON**
**Tools:** `python-pptx`, `pandoc`
**Rules:**
- **Slides:** Each slide → Marp slide (`---`).
- **Text:** Preserve headings, lists, and bullet points.
- **Images:** Save to `assets/` and link.
- **Notes:** Add as speaker notes in Marp (`<!-- _class: notes -->`).

**Example:**
```python
from pptx import Presentation

def pptx_to_marp(pptx_path):
    prs = Presentation(pptx_path)
    marp_content = "---\nmarp: true\n---\n\n"
    for slide in prs.slides:
        marp_content += f"# {slide.shapes.title.text if slide.shapes.title else 'Slide'}\n\n"
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                marp_content += f"{shape.text}\n\n"
        marp_content += "---\n\n"
    return marp_content
```

---

### **E. EPUB → Literary MD/JSON**
**Tools:** `ebooklib`, `pandoc`
**Rules:**
- **Chapters:** Each chapter → `# Chapter` in MD.
- **Metadata:** Extract title, author, publisher.
- **Images:** Save to `assets/` and link.

**Example:**
```python
from ebooklib import epub

def epub_to_md(epub_path):
    book = epub.read_epub(epub_path)
    md_content = f"# {book.get_metadata('DC', 'title')[0][0]}\n\n"
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            md_content += f"## {item.get_name()}\n\n{item.get_content().decode('utf-8')}\n\n"
    return md_content
```

---

## **4. Universal Postprocessing**
### **A. Cleanup**
- **Normalize:** Encoding, line breaks, whitespace.
- **Remove Noise:** Page numbers, footers, boilerplate.
- **Standardize:** Dates, names, links.

### **B. Transformation**
- **MD:** Apply literary/paragraph/subheading rules.
- **JSON:** Structure data hierarchically.
- **ucode STORY:** Add interactive fields if applicable.

### **C. `.compost` Versioning**
- Archive **original file** and **processed output** to `.compost`.
- Example:
  ```
  .compost/
  ├── 20260220_143022_input.docx
  ├── 20260220_143022_output.md
  └── 20260220_143022_output.json
  ```

---

## **5. Integration with uDOS**
### **A. File Structure**
```
vault/
├── .compost/
├── @binders/
│   └── project_x/
│       ├── imports/
│       │   ├── input.docx
│       │   ├── output.md
│       │   └── output.json
│       ├── moves.json
│       └── contacts.json
└── @user/
```

### **B. Workflow**
1. **Upload/Import:** User adds `input.docx` to `vault/@binders/project_x/imports/`.
2. **Process:**
   - Convert to MD/JSON/ucode STORY.
   - Extract tasks/contacts → update `moves.json`/`contacts.json`.
3. **Archive:** Save to `.compost`.
4. **Notify:** Log success/failure in `moves.json`.

---

## **6. Error Handling & Edge Cases**
| Case                          | Solution                                                                 |
|-------------------------------|--------------------------------------------------------------------------|
| Corrupt files                 | Skip and log error in `moves.json`.                                     |
| Unsupported formats           | Notify user; suggest manual conversion.                                |
| Complex tables (merged cells) | Flatten or split into multiple tables.                                 |
| Non-text elements (e.g., PDF forms) | Extract as images/links; flag for manual review.                |
| Large files                   | Process in chunks; archive intermediate versions.                     |

---

## **7. Open-Source Translators**
### **A. Pandoc**
- **Use Case:** Universal document converter (DOCX, PPTX, EPUB, HTML → MD).
- **Command:**
  ```bash
  pandoc input.docx -o output.md
  pandoc input.pptx --slide-level=2 -o slides.marp.md
  ```
- **Integration:** Call from Python using `subprocess`.

### **B. LibreOffice (Headless)**
- **Use Case:** Convert DOCX/XLSX/PPTX to MD/ODT/CSV.
- **Command:**
  ```bash
  libreoffice --headless --convert-to md input.docx
  ```

### **C. Custom Scripts**
- Use the Python examples above for fine-grained control.

---

## **8. Example: Full Import Script**
```python
import os
import shutil
from datetime import datetime
from docx import Document
import pdfplumber
import json

def import_file(filepath, vault_path):
    # 1. Archive original to .compost
    compost_path = os.path.join(vault_path, ".compost")
    os.makedirs(compost_path, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(filepath, os.path.join(compost_path, f"{timestamp}_{os.path.basename(filepath)}"))

    # 2. Detect format and process
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".docx":
        md_content = docx_to_md(filepath)
        json_content = docx_to_json(filepath)
    elif ext == ".pdf":
        md_content = pdf_to_md(filepath)
        json_content = json.dumps({"content": md_content.split("\n")})
    elif ext == ".pptx":
        md_content = pptx_to_marp(filepath)
        json_content = json.dumps({"slides": md_content.split("---\n")})
    else:
        raise ValueError(f"Unsupported format: {ext}")

    # 3. Save outputs
    base = os.path.splitext(filepath)[0]
    with open(f"{base}.md", "w") as f:
        f.write(md_content)
    with open(f"{base}.json", "w") as f:
        f.write(json_content)

    # 4. Archive outputs to .compost
    for output_ext in [".md", ".json"]:
        output_path = f"{base}{output_ext}"
        shutil.copy2(output_path, os.path.join(compost_path, f"{timestamp}_{os.path.basename(output_path)}"))

# Usage
import_file("vault/@binders/project_x/imports/input.docx", "vault")
```

---

## **9. Next Steps**
1. **Prototype the import script** for one format (e.g., DOCX).
2. **Test with real-world files** (e.g., project reports, slides).
3. **Integrate with uDOS workflows** (auto-update `moves.json`).
4. **Document templates** for each format (e.g., "How to import PPTX").
5. **Optimize for large files** (streaming, chunking).
