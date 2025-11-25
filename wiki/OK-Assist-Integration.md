# OK Assist Integration Guide

**uDOS v1.4.0** - AI-powered content generation using Google Gemini

> **💡 Quick Start**: Generate content with `OK <task>` or `GENERATE guide <topic>`

---

## Overview

OK Assist is uDOS's AI-powered content generation system, integrated with Google's Gemini API. It creates high-quality survival guides, technical diagrams, and reference materials.

### Features

- ✅ **Content Generation** - Guides, diagrams, checklists
- ✅ **Multi-Format Support** - Markdown, SVG, ASCII, Teletext
- ✅ **Smart Fallback** - Automatically uses placeholders when offline
- ✅ **Rate Limiting** - Prevents API quota issues (0.5s delays)
- ✅ **Quality Validation** - Ensures generated content meets standards
- ✅ **Batch Processing** - Generate multiple items efficiently

---

## Setup

### 1. Get API Key

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get a free Gemini API key.

### 2. Configure OK Assist

**Method 1: Via uDOS command (recommended)**
```bash
./start_udos.sh
CONFIG SET GEMINI_API_KEY your_key_here
```

**Method 2: Edit .env file**
```bash
cd /Users/fredbook/Code/uDOS
echo "GEMINI_API_KEY='your_actual_key_here'" >> .env
```

**Method 3: Environment variable**
```bash
export GEMINI_API_KEY='your_key_here'
./start_udos.sh
```

### 3. Verify Setup

```bash
# Test OK Assist
python3 extensions/core/ok-assist/examples/test_quick.py

# Expected output:
# ✅ OK Assistant initialized for content generation
# ✅ Model: gemini-2.0-flash-exp
# ✅ Rate limiting: 0.5s between calls
```

---

## Usage

### Interactive Commands

```bash
# General AI task
OK create a water purification guide

# Ask a question
OK ASK how to start fire without matches

# Generate specific content
GENERATE guide water/purification
GENERATE diagram fire/triangle
GENERATE checklist emergency/evacuation

# Read content for context
READ water-guide.md
OK ASK summarize this
```

### Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `OK <task>` | General AI task | `OK create shelter guide` |
| `OK ASK <question>` | Ask AI question | `OK ASK how to purify water` |
| `OK DEV <task>` | Development help | `OK DEV explain this code` |
| `READ <file>` | Load content | `READ README.md` |
| `GENERATE guide <topic>` | Create guide | `GENERATE guide water/purification` |
| `GENERATE diagram <topic>` | Create diagram | `GENERATE diagram fire/triangle` |

---

## Content Generation

### Guides

OK Assist creates comprehensive survival guides (800-1200 words):

```bash
# Generate via uDOS command
GENERATE guide water/purification

# Generate via Python script
python dev/tools/generate_content_v1_4_0.py --category water --count 5 --guides-only
```

**Guide Structure:**
- Detailed step-by-step instructions
- Safety warnings and considerations
- Materials lists
- Common mistakes to avoid
- Related topics for cross-referencing
- Proper markdown formatting

**Example Output:**
```markdown
# Water Purification Methods

## Overview
Water purification is essential for survival...

## Methods

### 1. Boiling
Boiling water is the most reliable method...

**Materials Needed:**
- Heat source
- Container
- Time: 1-5 minutes

**Steps:**
1. Collect water source
2. Bring to rolling boil
3. Boil for 1 minute (3 minutes at altitude)
...

## Safety Considerations
- Never drink unpurified water
- Test water clarity first
...
```

### Diagrams

OK Assist generates Technical-Kinetic compliant SVG diagrams:

```bash
# Generate SVG diagram
python dev/tools/generate_svg_diagram.py "water filter 3 stages" water

# Batch generate diagrams
python dev/tools/generate_content_v1_4_0.py --category fire --count 3 --diagrams-only
```

**Diagram Features:**
- Technical-Kinetic style (monochrome + patterns)
- Polaroid 8-color palette
- Clear labels and annotations
- Step-by-step visual process
- 800x600 viewBox (standard)
- Mallard font embedded

### Batch Generation

```bash
# Generate guides and diagrams for category
python dev/tools/generate_content_v1_4_0.py --category water --count 10

# Generate all categories
python dev/tools/generate_content_v1_4_0.py --all

# Dry run (preview without generating)
python dev/tools/generate_content_v1_4_0.py --category shelter --count 5 --dry-run

# Force placeholder mode (no API)
python dev/tools/generate_content_v1_4_0.py --category food --count 5 --no-ai
```

---

## Content Quality

### OK Assist Generated Content

**Guides:**
- 800-1200 word target length
- Practical, survival-focused
- Step-by-step instructions
- Safety warnings included
- Related topics linked
- Proper markdown formatting

**Diagrams:**
- Technical-Kinetic compliance
- Polaroid palette only
- Clear visual hierarchy
- Annotated components
- Standard 800x600 size
- Embedded custom font

### Quality Validation

The system automatically validates:

1. **Content length** - Meets word count targets
2. **Formatting** - Proper markdown structure
3. **Completeness** - All sections present
4. **Style compliance** - Follows uDOS standards
5. **SVG validity** - Well-formed XML for diagrams

---

## Operating Modes

### OK Assist Mode (Default)

Uses Gemini API when key is configured:

```bash
# Check mode
python dev/tools/generate_content_v1_4_0.py --category water --count 1

# Output shows:
# ✅ OK Assistant initialized for content generation
```

**Features:**
- High-quality content
- Natural language understanding
- Context-aware generation
- Multi-format support
- Rate limiting (0.5s delays)

### Placeholder Mode

Automatically activates when no API key:

```bash
# Force placeholder mode
python dev/tools/generate_content_v1_4_0.py --category shelter --count 10 --no-ai
```

**Features:**
- Structure-only content
- Placeholder text
- Proper formatting
- Quick generation
- No API quota usage

**Use cases:**
- Testing structure
- Offline development
- Template creation
- Architecture verification

---

## Rate Limiting

OK Assist implements automatic rate limiting to prevent quota issues:

### Default Delays

- **Between API calls**: 0.5 seconds
- **After rate limit error**: 60 seconds
- **Batch generation**: Automatic pacing

### Configuration

```python
# Adjust delay (in code)
from extensions.core.ok-assist.ok_assistant import OKAssistant

ok = OKAssistant(
    api_key=GEMINI_API_KEY,
    delay_between_calls=0.5  # Seconds between API calls
)
```

### Quota Management

**Free tier limits (Gemini):**
- 60 requests per minute
- 1,500 requests per day
- Input: Free
- Output: Free

**Best practices:**
- Use batch generation with delays
- Monitor quota at [Google Cloud Console](https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas)
- Implement exponential backoff for errors

---

## Error Handling

### Common Errors

**API Key Not Found:**
```
ERROR: GEMINI_API_KEY not found in environment
```

**Solution:**
```bash
# Check .env file
cat .env | grep GEMINI_API_KEY

# Set via command
CONFIG SET GEMINI_API_KEY your_key_here

# Verify
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"
```

**Rate Limit Exceeded:**
```
ERROR: Rate limit exceeded. Please wait.
```

**Solution:**
```bash
# Wait 60 seconds
sleep 60

# Use batch generation (automatic delays)
python dev/tools/generate_content_v1_4_0.py --category water --count 5

# Monitor quota usage
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

**Invalid API Response:**
```
ERROR: Failed to generate content
```

**Solution:**
```bash
# Check API key validity
python extensions/core/ok-assist/examples/test_quick.py

# Try simpler prompt
OK ASK test

# Check logs
cat memory/logs/udos.log | tail -50
```

---

## Statistics Tracking

The content generation tool tracks:

```bash
# Generate with statistics
python dev/tools/generate_content_v1_4_0.py --category water --count 10

# Output:
# ============================================================
# CONTENT GENERATION SUMMARY
# ============================================================
#
# Guides Generated:     10
# Diagrams Generated:   10
# Total API Calls:      20
# Errors:               0
# Skipped (exist):      0
# Mode:                 OK Assist
#
# Time Elapsed:         45.3 seconds
# Average per item:     2.27 seconds
# ============================================================
```

---

## Advanced Usage

### Custom Prompts

```python
from extensions.core.ok-assist.ok_assistant import OKAssistant

ok = OKAssistant(api_key=GEMINI_API_KEY)

# Custom guide generation
guide = ok.generate_guide(
    topic="Advanced water purification",
    category="water",
    complexity="detailed",
    word_count=1500
)

# Custom diagram generation
diagram = ok.generate_diagram(
    description="Solar still construction 8 steps",
    style="technical-kinetic",
    format="svg",
    size="1200x800"
)
```

### Integration with uCODE

```uscript
---
title: Content Generation Workflow
version: 1.0.0
---

# Generate water content
[GENERATE|guide|water/purification]
[GENERATE|diagram|water/filter|format=svg]

# Generate fire content
[GENERATE|guide|fire/starting]
[GENERATE|diagram|fire/triangle|format=svg]

# Validate generated content
[REFRESH|--check|all]
```

### Batch Processing

```bash
# Generate all categories sequentially
for cat in water fire shelter food medical navigation tools communication; do
  python dev/tools/generate_content_v1_4_0.py --category $cat --count 5
  sleep 10  # Pause between categories
done

# Generate from topic list
cat topics.txt | while read topic category; do
  python dev/tools/generate_svg_diagram.py "$topic" "$category"
  sleep 1
done
```

---

## Performance

### Generation Times

**Guides:**
- Simple (500 words): ~3-5 seconds
- Medium (800 words): ~5-8 seconds
- Complex (1200+ words): ~8-12 seconds

**Diagrams:**
- Simple (1-2 elements): ~5-10 seconds
- Medium (3-5 elements): ~10-20 seconds
- Complex (6+ elements): ~20-40 seconds

### Optimization Tips

1. **Batch generation** - More efficient than individual calls
2. **Appropriate delays** - 0.5s prevents rate limiting
3. **Parallel categories** - Generate different categories concurrently
4. **Cache results** - Store generated content for reuse
5. **Dry run first** - Preview before generating

---

## Testing

### Unit Tests

```bash
# Test OK Assist integration
pytest extensions/core/ok-assist/tests/

# Test content generation
pytest dev/tools/tests/test_content_generation.py

# Test SVG generation
pytest dev/tools/tests/test_svg_generator.py
```

### Integration Tests

```bash
# Quick test (requires API key)
python extensions/core/ok-assist/examples/test_quick.py

# Multi-format test
python extensions/core/ok-assist/examples/generate_multi_format.py

# Batch diagram test
python extensions/core/ok-assist/examples/batch_generate_diagrams.py
```

---

## Best Practices

### 1. Specific Descriptions

```bash
# Good - Specific and detailed
GENERATE guide water/purification/boiling-method

# Bad - Too vague
GENERATE guide water
```

### 2. Appropriate Categories

Match content to correct category:

- **Water**: purification, collection, storage
- **Fire**: starting, management, safety
- **Shelter**: construction, materials, weatherproofing
- **Food**: foraging, preservation, preparation
- **Medical**: first aid, procedures, treatments
- **Navigation**: wayfinding, orientation, mapping
- **Tools**: construction, usage, maintenance
- **Communication**: signaling, messaging, protocols

### 3. Rate Limiting

```bash
# Always use delays for batch
python dev/tools/generate_content_v1_4_0.py --category water --count 10

# Monitor quota
# Visit: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

### 4. Version Control

```bash
# Review generated content before committing
git diff knowledge/

# Commit with descriptive message
git add knowledge/water/
git commit -m "Add 10 water purification guides (OK Assist generated)"
```

---

## Troubleshooting

### Content Quality Issues

**Problem:** Generated content is low quality or incomplete

**Solutions:**

```bash
# Use more specific prompts
GENERATE guide water/purification/ceramic-filter-method

# Increase word count target
# Edit: dev/tools/generate_content_v1_4_0.py
# Change: WORD_COUNT_TARGET = 1200

# Regenerate with --force flag
python dev/tools/generate_content_v1_4_0.py --category water --count 1 --force
```

### API Errors

**Problem:** Consistent API failures

**Solutions:**

```bash
# Test API key
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GEMINI_API_KEY'))"

# Test with simple query
python extensions/core/ok-assist/examples/test_quick.py

# Check API status
# Visit: https://status.cloud.google.com/
```

### Performance Issues

**Problem:** Slow generation times

**Solutions:**

```bash
# Use batch mode (more efficient)
python dev/tools/generate_content_v1_4_0.py --all

# Reduce delay (if quota allows)
# Edit: ok_assistant.py
# Change: delay_between_calls=0.3

# Use parallel processing (advanced)
# Generate different categories simultaneously
```

---

## See Also

- [SVG Generator Guide](SVG-Generator-Guide.md)
- [Content Generation Workflow](Content-Generation.md)
- [API Reference](API-Reference.md)
- [Command Reference](Command-Reference.md)

---

**Last Updated**: November 25, 2025
**Version**: v1.4.0
**Maintainer**: @fredporter
**Support**: GitHub Issues or community forum
