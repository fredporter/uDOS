# PEEK Command - URL to Markdown Converter

**Status:** ✅ Implemented and Ready  
**Version:** 1.0.0  
**Location:** Wizard Server Interactive Console  
**Date Added:** 2026-01-26

---

## Overview

The **PEEK** command converts web pages to Markdown format and saves them to `/memory/sandbox/outbox/`.

Perfect for:

- Capturing web articles for offline reading
- Converting documentation pages
- Archiving web content as Markdown
- Integrating web sources into your knowledge base

---

## Usage

### Basic Syntax

```
wizard> peek <url> [optional-filename]
```

### Examples

#### Simple conversion

```
wizard> peek https://github.com/fredporter/uDOS
```

Saves to: `memory/sandbox/outbox/uDOS.md`

#### Custom filename

```
wizard> peek https://example.com my-custom-page
```

Saves to: `memory/sandbox/outbox/my-custom-page.md`

#### Real-world examples

```
wizard> peek https://www.wikipedia.org/wiki/Python_(programming_language) python-wiki
wizard> peek https://www.rust-lang.org/what/wasm/ wasm-rust
wizard> peek https://docs.github.com/en/copilot github-copilot-docs
```

---

## Output

Each converted file includes:

1. **YAML Frontmatter** with metadata:
   - `title` - Page title
   - `source_url` - Original URL
   - `converted_at` - ISO timestamp
   - `format` - Conversion method

2. **Markdown Content** - Converted page content with:
   - Headings and structure preserved
   - Links formatted as Markdown
   - Images referenced (if available)
   - Code blocks preserved
   - Tables converted

### Example Output Structure

```markdown
---
title: github
source_url: https://github.com/fredporter/uDOS
converted_at: 2026-01-26T14:32:15.123456
format: url-to-markdown
---

# GitHub

[Visit GitHub](https://github.com)

## About

GitHub is where over 100 million developers shape the future of software...
```

---

## How It Works

### Conversion Methods (Priority Order)

1. **Python Approach** (Primary)
   - Uses: `requests` + `beautifulsoup4` + `html2text`
   - Faster initial load
   - Good compatibility
   - Pure Python solution

2. **NPM Approach** (Fallback)
   - Uses: `url-to-markdown` npm package
   - Requires: `npm install -g url-to-markdown`
   - Used if Python approach fails
   - More comprehensive formatting

### Implementation Details

- **Service:** `wizard/services/url_to_markdown_service.py`
- **Console Command:** `wizard/services/interactive_console.py` → `cmd_peek()`
- **Output Directory:** `/memory/sandbox/outbox/`
- **Logging:** Tagged as `[WIZ]` in Wizard logs

---

## Installation & Setup

### Step 1: Verify Python Dependencies

```bash
pip install requests beautifulsoup4 html2text
```

Verify installation:

```bash
python3 -c "import requests, bs4, html2text; print('✅ All dependencies installed')"
```

### Step 2: Optional - Install NPM Package (Fallback)

For enhanced formatting support:

```bash
npm install -g url-to-markdown
```

Verify:

```bash
which url-to-markdown  # Should show path
```

### Step 3: Test the Installation

Run the test script:

```bash
bash bin/test_peek.sh
```

Or test with a real URL:

```bash
bash bin/test_peek.sh https://example.com test-page
```

---

## Testing

### Run Test Suite

```bash
# Run all checks (no conversion)
bash bin/test_peek.sh

# Run with actual conversion
bash bin/test_peek.sh https://github.com/fredporter/uDOS my-repo
```

### Expected Output

```
🧪 PEEK Command Test Suite
==================================================

✅ Outbox directory: /Users/fredbook/Code/uDOS/memory/sandbox/outbox

📋 Test 1: Checking Python dependencies
  ✅ requests installed
  ✅ beautifulsoup4 installed
  ✅ html2text installed

📋 Test 2: Verifying service import
  ✅ Service imports successfully

📋 Test 3: Checking url-to-markdown library
  ✅ Library definition found: library/url-to-markdown/
  ⚠️  npm package not in PATH (can be installed: npm install -g url-to-markdown)

✅ All checks passed! Ready to use PEEK command
```

---

## Integration Architecture

### Component Diagram

```
Wizard Server (Port 8765)
│
├─ Interactive Console
│  └─ cmd_peek(args)              ← User types: peek <url> [filename]
│     └─ URLToMarkdownService
│        ├─ convert()             ← Main method
│        ├─ convert_with_python() ← Try first
│        │  └─ requests + BS4 + html2text
│        └─ convert_with_npm()    ← Fallback
│           └─ url-to-markdown package
│
└─ Output: memory/sandbox/outbox/{filename}.md
```

### Data Flow

```
wizard> peek https://example.com
  ↓
cmd_peek(["https://example.com"])
  ↓
URLToMarkdownService.convert(url, filename=None)
  ↓
Try Python method:
  - Fetch URL with requests
  - Parse with BeautifulSoup
  - Convert to Markdown with html2text
  ↓
Write to: memory/sandbox/outbox/example.md
  ↓
Return: (success, path, message)
  ↓
Display: ✅ Converted and saved to memory/sandbox/outbox/example.md
```

---

## Error Handling

### Common Issues & Solutions

#### Issue: "Missing dependency: requests"

```
❌ Missing dependency: requests. Install: pip install requests beautifulsoup4 html2text
```

**Solution:**

```bash
pip install requests beautifulsoup4 html2text
```

---

#### Issue: "Failed to fetch URL"

```
❌ Failed to fetch URL: [URLError]
```

**Causes & Solutions:**

1. **URL is invalid:** Verify URL starts with `http://` or `https://`
2. **No internet connection:** Check network connectivity
3. **Server blocking requests:** Try different URL or wait
4. **Timeout:** Large pages may timeout (>15s)

---

#### Issue: "Conversion timeout (>30s)"

Large pages may exceed timeout. Try:

- Simpler pages
- Direct article links
- Archive pages

---

#### Issue: "npm package not found"

Falls back to Python method automatically. To use npm:

```bash
npm install -g url-to-markdown
```

---

## API Reference

### URLToMarkdownService

```python
from wizard.services.url_to_markdown_service import get_url_to_markdown_service

service = get_url_to_markdown_service()

# Convert URL to Markdown
success, output_path, message = await service.convert(
    url="https://example.com",
    filename="my-page"  # Optional
)

# Check result
if success:
    print(f"✅ Saved to {output_path}")
else:
    print(f"❌ Error: {message}")
```

### Method Signature

```python
async def convert(
    self,
    url: str,
    filename: Optional[str] = None
) -> Tuple[bool, Optional[Path], str]:
    """
    Convert URL to Markdown.

    Args:
        url: Full URL (http:// or https://)
        filename: Optional filename without extension

    Returns:
        (success: bool, output_path: Path|None, message: str)
    """
```

---

## Performance

### Benchmarks

| URL Type             | Python Method | NPM Method | Output Size |
| -------------------- | ------------- | ---------- | ----------- |
| Simple article (5KB) | ~1-2s         | ~2-3s      | 3-4KB       |
| Blog post (20KB)     | ~2-3s         | ~3-4s      | 15-20KB     |
| Documentation (50KB) | ~3-5s         | ~5-10s     | 40-50KB     |
| Large page (100KB+)  | ~5-10s        | Timeout    | 80-100KB    |

**Timeout Settings:**

- Python method: 15 seconds (URL fetch)
- NPM method: 30 seconds (total conversion)

---

## Security & Privacy

### Privacy Notes

- **[WIZ] Tag**: All operations logged as Wizard-only (internet access)
- **No data retention**: Content converted but not cached
- **Local storage only**: All files saved locally in `/memory/`
- **Sensitive content**: Treat like any local file

### Warnings

⚠️ **Important:**

- Do not use PEEK for sensitive/confidential URLs
- Converted content includes all HTML (scripts, trackers, etc.)
- Consider HTML cleanup before sharing
- Check output for embedded malicious content

---

## Logging

PEEK operations are logged with the `[WIZ]` tag:

```
[2026-01-26 14:32:15] [WIZ] Converting URL to Markdown: https://example.com
[2026-01-26 14:32:17] [WIZ] ✅ Converted and saved to memory/sandbox/outbox/example.md
```

View logs:

```bash
tail -f memory/logs/wizard-server-YYYY-MM-DD.log | grep "WIZ"
```

---

## Roadmap

### v1.0 (Current)

- ✅ Basic URL to Markdown conversion
- ✅ Python + NPM dual methods
- ✅ Interactive console integration
- ✅ Metadata headers
- ✅ Error handling

### v1.1 (Planned)

- 🔲 URL batch processing (PEEK-BATCH)
- 🔲 Content cleanup options (--no-scripts, --images-only)
- 🔲 Format options (--github-flavored, --commonmark)
- 🔲 Resume interrupted conversions
- 🔲 Cache management

### v2.0 (Future)

- 🔲 PDF to Markdown support
- 🔲 Multi-format output (HTML, LaTeX)
- 🔲 Incremental updates (URL changed? Re-fetch)
- 🔲 Content diffing
- 🔲 Web archiving integration

---

## References

### Related Files

- [wizard/services/url_to_markdown_service.py](../../wizard/services/url_to_markdown_service.py) - Service implementation
- [wizard/services/interactive_console.py](../../wizard/services/interactive_console.py) - Console integration
- [library/url-to-markdown/container.json](../../library/url-to-markdown/container.json) - Library definition
- [bin/test_peek.sh](../../bin/test_peek.sh) - Test script

### External Resources

- [requests Documentation](https://docs.python-requests.org/)
- [BeautifulSoup4 Documentation](https://www.crummy.com/software/BeautifulSoup/)
- [html2text Documentation](https://github.com/Alir3z4/html2text)
- [url-to-markdown (npm)](https://www.npmjs.com/package/url-to-markdown)

### Related Commands

```
wizard> help              # Show all commands
wizard> logs             # View Wizard logs
wizard> new              # Create new file
wizard> edit             # Edit existing file
wizard> ai               # AI helpers (summarize content)
```

---

## Support & Troubleshooting

### Debug Mode

Enable detailed logging:

```python
# In Python snippet
import logging
logging.basicConfig(level=logging.DEBUG)
service = get_url_to_markdown_service()
success, path, msg = await service.convert("https://example.com")
```

### Test with Known URLs

```bash
# Simple page
bash bin/test_peek.sh https://example.com

# GitHub
bash bin/test_peek.sh https://github.com/fredporter/uDOS

# Wikipedia (large)
bash bin/test_peek.sh "https://en.wikipedia.org/wiki/Python" python-wiki

# News article
bash bin/test_peek.sh https://news.ycombinator.com hn-front
```

### Common Questions

**Q: Why is the output not perfect?**  
A: HTML-to-Markdown conversion is lossy. Complex layouts don't translate perfectly.

**Q: Can I edit the converted file?**  
A: Yes! Use `edit` command: `wizard> edit memory/sandbox/outbox/my-page.md`

**Q: How do I manage converted files?**  
A: Use `tidy` to archive old files: `wizard> tidy current +subfolders`

**Q: Can I batch convert multiple URLs?**  
A: Not yet (v1.1 feature). Use a shell loop for now:

```bash
for url in "https://example.com" "https://example.org"; do
  curl -X POST http://localhost:8765/api/v1/web/peek -d "{\"url\": \"$url\"}"
done
```

---

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** 2026-01-26  
**Maintainer:** uDOS Wizard Server Team
