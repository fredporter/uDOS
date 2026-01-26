# PEEK Command - Quick Start

**Status:** ✅ Ready to use  
**Command:** `PEEK {url} [filename]`  
**Output:** `/memory/sandbox/outbox/{filename}.md`

---

## 3-Minute Setup

### 1. Verify Dependencies

```bash
# Everything needed is already installed:
# ✅ requests
# ✅ beautifulsoup4
# ✅ html2text
```

### 2. Start Wizard Server

```bash
# From uDOS root:
python wizard/server.py
```

You'll see:

```
💬 INTERACTIVE MODE: Type 'help' for commands, 'exit' to shutdown
wizard>
```

### 3. Use PEEK

```bash
wizard> peek https://example.com
```

Output:

```
⏳ Converting https://example.com...
   ✅ Converted and saved to memory/sandbox/outbox/example.md
   📄 File: memory/sandbox/outbox/example.md
```

Done! ✅

---

## Examples

### Convert with auto-detected filename

```bash
wizard> peek https://github.com/fredporter/uDOS
# Saves as: memory/sandbox/outbox/uDOS.md
```

### Convert with custom filename

```bash
wizard> peek https://example.com my-custom-page
# Saves as: memory/sandbox/outbox/my-custom-page.md
```

### Real-world examples

```bash
wizard> peek https://www.python.org/about/gettingstarted/ python-intro
wizard> peek https://docs.github.com/en github-docs
wizard> peek https://www.wikipedia.org/wiki/Markdown markdown-wiki
```

---

## Output Format

Each file has YAML metadata + markdown content:

```markdown
---
title: my-page
source_url: https://example.com
converted_at: 2026-01-26T10:24:43.891912
format: url-to-markdown
---

# Page Title

Page content in Markdown format...
```

---

## Check Output

```bash
# List all converted files
ls -la memory/sandbox/outbox/

# View a specific file
cat memory/sandbox/outbox/example.md

# Edit in Wizard
wizard> edit memory/sandbox/outbox/example.md
```

---

## Help

```bash
wizard> help    # Shows all commands
wizard> peek    # Shows PEEK usage (no args)
```

---

## Troubleshooting

| Issue                 | Solution                                             |
| --------------------- | ---------------------------------------------------- |
| "Missing dependency"  | Run: `pip install requests beautifulsoup4 html2text` |
| "Failed to fetch URL" | Check URL is valid (http:// or https://)             |
| "Conversion timeout"  | Try simpler pages or wait a moment                   |
| File not found        | Check: `ls memory/sandbox/outbox/`                   |

---

## Files Modified/Created

| File                                         | Type        | Purpose                |
| -------------------------------------------- | ----------- | ---------------------- |
| `wizard/services/url_to_markdown_service.py` | 🆕 New      | URL conversion service |
| `wizard/services/interactive_console.py`     | ✏️ Modified | Added PEEK command     |
| `wizard/docs/PEEK-COMMAND.md`                | 🆕 New      | Full documentation     |
| `bin/test_peek.sh`                           | 🆕 New      | Test script            |

---

## Architecture Overview

```
wizard> peek https://example.com
       ↓
InteractiveConsole.cmd_peek()
       ↓
URLToMarkdownService.convert()
       ↓
Try: requests + BeautifulSoup4 + html2text
       ↓
Save: memory/sandbox/outbox/example.md
       ↓
Success! ✅
```

---

**Ready to use!** Type `peek https://example.com` at the wizard> prompt.
