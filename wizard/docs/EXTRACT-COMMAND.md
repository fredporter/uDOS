# EXTRACT Command Documentation

**Version:** 1.0.0
**Status:** Ready (Requires MISTRAL_API_KEY configuration)
**Location:** `wizard/services/pdf_ocr_service.py` + `wizard/services/interactive_console.py`

---

## Overview

The **EXTRACT** command converts PDF files to Markdown using Mistral AI's OCR (Optical Character Recognition) technology. It integrates the [pdf-ocr-obsidian](https://github.com/diegomarzaa/pdf-ocr-obsidian) library into the Wizard Server interactive console.

### Features

- ✅ **Single file extraction** — Extract a specific PDF to Markdown
- ✅ **Batch processing** — Process all PDFs in the inbox folder at once
- ✅ **Image extraction** — Automatically extracts images from PDFs
- ✅ **Wikilink formatting** — Links images using Obsidian `![[image.jpg]]` syntax
- ✅ **Metadata preservation** — Saves YAML frontmatter with extraction details
- ✅ **OCR response caching** — Saves raw OCR response as JSON for reference
- ✅ **Error resilience** — Batch mode continues processing even if one PDF fails

---

## Quick Start

### Prerequisites

1. **Mistral API Key** — Required for OCR processing

   ```bash
   export MISTRAL_API_KEY='sk-...'
   ```

2. **Python Packages** — Installed automatically via `pip install mistralai`

   ```bash
   pip install mistralai
   ```

3. **Directory Structure** — Automatically created by EXTRACT service
   ```
   memory/
   ├── inbox/                 ← Drop PDF files here for batch processing
   └── sandbox/processed/     ← Markdown output saved here
   ```

### Single File Extraction

```bash
wizard> extract invoice.pdf
⏳ Extracting invoice.pdf...
   ✅ Extracted invoice.pdf to memory/sandbox/processed/invoice/output.md
   📄 File: memory/sandbox/processed/invoice/output.md
```

### Batch Processing

Extract all PDFs from the inbox folder:

```bash
wizard> extract
⏳ Processing PDFs from inbox...
   ✅ Processed 3 PDFs
   ✅ invoice.pdf
      📄 memory/sandbox/processed/invoice/output.md
      🖼️  2 images, 5 pages
   ✅ report.pdf
      📄 memory/sandbox/processed/report/output.md
      🖼️  0 images, 12 pages
   ✅ menu.pdf
      📄 memory/sandbox/processed/menu/output.md
      🖼️  8 images, 3 pages
```

### With Full Path

```bash
wizard> extract /path/to/document.pdf
⏳ Extracting /path/to/document.pdf...
   ✅ Extracted document.pdf to memory/sandbox/processed/document/output.md
```

---

## Command Syntax

```
extract [pdf-filename]
extract                    (batch process inbox)
```

### Arguments

| Argument         | Required | Description                                                                                |
| ---------------- | -------- | ------------------------------------------------------------------------------------------ |
| `[pdf-filename]` | No       | Path to PDF file (relative to inbox or absolute). If omitted, processes all PDFs in inbox. |

### Examples

```bash
# Single file from inbox
extract document.pdf

# Single file from absolute path
extract ~/Downloads/invoice.pdf

# Single file from relative path
extract ../../Downloads/report.pdf

# Batch process all PDFs in inbox
extract

# Help (type 'help' at prompt)
help
```

---

## Output Structure

### Single File Extraction

```
memory/sandbox/processed/document-name/
├── output.md              ← Extracted markdown with metadata
├── ocr_response.json      ← Raw OCR response (for debugging)
└── images/
    ├── document-name_img_1.jpeg
    ├── document-name_img_2.jpeg
    └── ...
```

### Markdown Format

```markdown
---
title: document-name
source_file: document.pdf
extracted_at: 2026-01-25T10:30:45.123456
format: pdf-ocr-mistral
image_count: 3
---

Page 1 content here...

---

Page 2 content here...

![[document-name_img_1.jpeg]]

Page 3 content here...
```

### Metadata Fields

| Field          | Description                    |
| -------------- | ------------------------------ |
| `title`        | PDF filename without extension |
| `source_file`  | Original PDF filename          |
| `extracted_at` | ISO 8601 timestamp             |
| `format`       | Always `pdf-ocr-mistral`       |
| `image_count`  | Number of extracted images     |

---

## Architecture

### Service Classes

#### `PDFOCRService` (Main Service)

```python
from wizard.services.pdf_ocr_service import get_pdf_ocr_service

service = get_pdf_ocr_service()

# Single file
success, output_path, message = await service.extract("invoice.pdf")

# Batch processing
success, results, message = await service.extract_batch()
```

**Key Methods:**

| Method                | Purpose                              | Returns                     |
| --------------------- | ------------------------------------ | --------------------------- |
| `extract(pdf_path)`   | Extract single PDF                   | `(bool, Path \| None, str)` |
| `extract_batch()`     | Batch extract inbox                  | `(bool, list[dict], str)`   |
| `_validate_setup()`   | Check Mistral API config             | `(bool, str)`               |
| `_process_pdf_sync()` | Sync OCR processing (runs in thread) | `dict`                      |

#### `WizardConsole` (Command Integration)

```python
# In wizard/services/interactive_console.py
async def cmd_extract(self, args: list) -> None:
    """Extract PDF to Markdown and save to outbox."""
    service = get_pdf_ocr_service()
    # ... command logic ...
```

### Data Flow

```
User Input
   ↓
cmd_extract(args)
   ├─ Single file: extract(args[0])
   └─ Batch mode: extract_batch() if no args
   ↓
_validate_setup()
   ├─ Check MISTRAL_API_KEY
   ├─ Check mistralai package
   └─ Check pdf-ocr library
   ↓
_process_pdf_sync() [runs in thread]
   ├─ Upload PDF to Mistral
   ├─ Call OCR API
   ├─ Extract text + images
   └─ Generate markdown
   ↓
Output Files
   ├─ output.md (markdown)
   ├─ ocr_response.json (metadata)
   └─ images/ (extracted images)
```

### Threading Model

- Console command runs in event loop (async/await)
- PDF processing runs in thread via `asyncio.to_thread()` to avoid blocking
- Mistral API calls execute synchronously in thread
- Results returned to console for display

---

## Configuration

### Environment Variables

| Variable          | Required | Description                                         |
| ----------------- | -------- | --------------------------------------------------- |
| `MISTRAL_API_KEY` | ✅ Yes   | Mistral API key (starts with `sk-`)                 |
| `UDOS_ROOT`       | No       | Override repo root detection (default: auto-detect) |

### Setup Steps

1. **Get Mistral API Key**

   ```bash
   # Visit https://console.mistral.ai/
   # Create API key with OCR document permissions
   ```

2. **Set Environment Variable**

   ```bash
   export MISTRAL_API_KEY='sk-...'

   # Or add to ~/.zshrc / ~/.bashrc
   echo "export MISTRAL_API_KEY='sk-...'" >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Verify Setup**

   ```bash
   bash bin/test_extract.sh
   # Should show: ✅ MISTRAL_API_KEY is set
   ```

4. **Run Wizard Server**
   ```bash
   python wizard/server.py
   # Or via Dev Mode
   ./Launch-Dev-Mode.command
   ```

---

## Error Handling

### Common Errors

**Error:** `MISTRAL_API_KEY not configured (required for OCR)`

- **Cause:** Environment variable not set
- **Fix:** `export MISTRAL_API_KEY='sk-...'`

**Error:** `mistralai package not installed: pip install mistralai`

- **Cause:** Python package missing
- **Fix:** `pip install mistralai`

**Error:** `PDF file not found: document.pdf`

- **Cause:** File doesn't exist at specified path
- **Fix:** Check path and try again: `extract /full/path/to/document.pdf`

**Error:** `File is not a PDF: .txt`

- **Cause:** Wrong file type
- **Fix:** Provide a PDF file

**Error:** `OCR processing error: ...`

- **Cause:** API call failed or invalid PDF
- **Fix:** Check API key, verify PDF is valid, check console logs

### Batch Mode Error Resilience

If one PDF fails during batch processing, the service continues with remaining files:

```
⏳ Processing PDFs from inbox...
   ✅ Processed 2 PDFs, ❌ Failed 1
   ✅ invoice.pdf
   ❌ corrupted.pdf
   ✅ report.pdf
```

---

## Testing

### Run Test Script

```bash
bash bin/test_extract.sh
```

**Test Coverage:**

- ✅ Python3 availability
- ✅ Virtual environment activation
- ✅ Python package imports
- ✅ Mistral API key configuration
- ✅ Directory structure creation
- ✅ Service instantiation
- ✅ Setup validation

### Manual Testing

1. **Place test PDF in inbox**

   ```bash
   cp ~/Downloads/sample.pdf memory/inbox/
   ```

2. **Extract single file**

   ```bash
   wizard> extract sample.pdf
   ```

3. **Check output**

   ```bash
   ls -la memory/sandbox/outbox/sample/
   # Should show: output.md, ocr_response.json, images/
   ```

4. **Verify markdown**
   ```bash
   cat memory/sandbox/outbox/sample/output.md | head -20
   # Should show YAML frontmatter + markdown content
   ```

---

## Performance

### Speed Estimates

| Task               | Time      | Notes                                          |
| ------------------ | --------- | ---------------------------------------------- |
| Single 5-page PDF  | 10-30 sec | Depends on image count and Mistral API latency |
| Single 50-page PDF | 1-2 min   | Larger documents may take longer               |
| Batch 10 PDFs      | 5-10 min  | Sequential processing (can be parallelized)    |

### Optimization Tips

- **Use text-based PDFs** — Faster than scanned documents
- **Monitor API quota** — Mistral charges per page/image
- **Batch process at off-peak times** — May improve latency
- **Check image extraction** — Disable if not needed (future enhancement)

---

## Integration with PEEK

Both PEEK and EXTRACT follow the same pattern:

| Aspect             | PEEK                      | EXTRACT                   |
| ------------------ | ------------------------- | ------------------------- |
| **Input**          | URLs                      | PDFs                      |
| **Service**        | URLToMarkdownService      | PDFOCRService             |
| **Output Path**    | `/memory/sandbox/outbox/` | `/memory/sandbox/outbox/` |
| **Single + Batch** | URL or list               | File or inbox folder      |
| **Command**        | `peek <url>`              | `extract [file.pdf]`      |

---

## Relationship to pdf-ocr-obsidian

The EXTRACT command wraps the [pdf-ocr-obsidian](https://github.com/diegomarzaa/pdf-ocr-obsidian) library:

- **Library Location:** `library/pdf-ocr/` (full source)
- **Service Wrapper:** `wizard/services/pdf_ocr_service.py`
- **Dependencies:** Flask, mistralai, python-dotenv, Werkzeug, gunicorn
- **Model:** Uses Mistral `pixtral-12b-2409` for OCR

---

## Future Enhancements

- [ ] Image extraction toggle (skip images for faster processing)
- [ ] Parallel batch processing (process multiple PDFs simultaneously)
- [ ] OCR language selection (multi-language support)
- [ ] Table extraction and formatting
- [ ] Form field extraction
- [ ] Progress bar for batch operations
- [ ] Cost tracking per document
- [ ] Cache/resume for failed batches

---

## References

- [pdf-ocr-obsidian GitHub](https://github.com/diegomarzaa/pdf-ocr-obsidian)
- [Mistral AI Documentation](https://docs.mistral.ai/)
- [Mistral OCR API](https://docs.mistral.ai/capabilities/vision/)
- [PEEK Command Documentation](PEEK-COMMAND.md)
- [Wizard Server README](README.md)

---

## Files

| File                                     | Purpose                                 |
| ---------------------------------------- | --------------------------------------- |
| `wizard/services/pdf_ocr_service.py`     | Core service implementation (283 lines) |
| `wizard/services/interactive_console.py` | Command integration + help text         |
| `bin/test_extract.sh`                    | Test script (executable)                |
| `wizard/docs/EXTRACT-COMMAND.md`         | This file                               |
| `library/pdf-ocr/`                       | Source library (cloned from GitHub)     |

---

## Support

For issues or questions:

1. Check logs: `memory/logs/wizard-server-YYYY-MM-DD.log`
2. Verify setup: `bash bin/test_extract.sh`
3. Test service directly: See Architecture section above
4. Review PEEK command (similar pattern): `wizard/docs/PEEK-COMMAND.md`

---

_Last Updated: 2026-01-25_
_uDOS Wizard Server v1.1.0.0_
