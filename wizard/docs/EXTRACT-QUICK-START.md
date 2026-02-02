# EXTRACT Command Quick Start

**Extract PDFs to Markdown using Mistral OCR**

---

## 3-Minute Setup

### 1. Get Mistral API Key

```bash
# Visit https://console.mistral.ai/
# Create API key for OCR (needs "Document Upload" permission)
```

### 2. Set Environment Variable

```bash
export MISTRAL_API_KEY='sk-...'
```

### 3. Test Setup

```bash
bash bin/test_extract.sh
```

Should show: ✅ MISTRAL_API_KEY is set

---

## Usage

### Single File

```bash
wizard> extract invoice.pdf
```

### Batch (All PDFs in inbox)

```bash
wizard> extract
```

### Absolute Path

```bash
wizard> extract ~/Downloads/document.pdf
```

---

## Input/Output

| Direction  | Location                 | Description                              |
| ---------- | ------------------------ | ---------------------------------------- |
| **Input**  | `memory/inbox/`          | Drop PDF files here for batch processing |
| **Output** | `memory/sandbox/processed/` | Markdown + images saved here          |

---

## Output Format

```
processed/
├── document-name/
    ├── output.md          ← Markdown with YAML metadata
    ├── ocr_response.json  ← Raw OCR response
    └── images/
        ├── document-name_img_1.jpeg
        └── document-name_img_2.jpeg
```

**Markdown Format:**

```markdown
---
title: document-name
source_file: document.pdf
extracted_at: 2026-01-25T10:30:45
format: pdf-ocr-mistral
image_count: 2
---

Page 1 content...

---

Page 2 content with images:

![[document-name_img_1.jpeg]]
```

---

## Examples

### Extract Invoice

```bash
wizard> extract invoice.pdf
⏳ Extracting invoice.pdf...
     ✅ Extracted invoice.pdf to memory/sandbox/processed/invoice/output.md
     📄 File: memory/sandbox/processed/invoice/output.md
```

### Batch Process 3 PDFs

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

---

## Common Issues

| Problem                           | Solution                                  |
| --------------------------------- | ----------------------------------------- |
| `MISTRAL_API_KEY not configured`  | `export MISTRAL_API_KEY='sk-...'`         |
| `mistralai package not installed` | `pip install mistralai`                   |
| `PDF file not found`              | Check path: `extract /full/path/file.pdf` |
| `File is not a PDF`               | Provide a `.pdf` file                     |

---

## Architecture

```
wizard> extract invoice.pdf
         ↓
    cmd_extract(args)
         ↓
    PDFOCRService.extract("invoice.pdf")
         ↓
    _validate_setup()
    (Check MISTRAL_API_KEY & packages)
         ↓
    _process_pdf_sync() [in thread]
    (Upload → OCR → Extract images → Generate markdown)
         ↓
    Output Files
    ├── output.md
    ├── ocr_response.json
    └── images/
```

---

## Files

| Path                                     | Purpose                  |
| ---------------------------------------- | ------------------------ |
| `wizard/services/pdf_ocr_service.py`     | Core service (283 lines) |
| `wizard/services/interactive_console.py` | Command integration      |
| `bin/test_extract.sh`                    | Test script              |
| `library/pdf-ocr/`                       | Source library           |

---

## Full Documentation

See: [EXTRACT-COMMAND.md](EXTRACT-COMMAND.md)

---

_Last Updated: 2026-01-25_
