# AI Integration Guide for v1.4.0 Content Generation

## Overview

The v1.4.0 content generation tool (`generate_content_v1_4_0.py`) now integrates with Gemini AI to create high-quality survival guides and technical diagrams.

## Setup

### 1. Get Gemini API Key

Visit [Google AI Studio](https://makersuite.google.com/app/apikey) to get a free API key.

### 2. Configure API Key

```bash
# Method 1: Set via uDOS command (recommended)
🔮 > CONFIG SET GEMINI_API_KEY your_key_here

# Method 2: Edit .env file directly
echo "GEMINI_API_KEY='your_actual_key_here'" >> .env
```

### 3. Verify Setup

```bash
python3 dev/tools/generate_content_v1_4_0.py --category water --count 1 --guides-only
```

You should see:
```
✅ Gemini AI initialized for content generation
```

## Usage Modes

### AI-Powered Mode (Default)

Generates content using Gemini AI:

```bash
# Generate 5 AI-powered water guides
python3 dev/tools/generate_content_v1_4_0.py --category water --count 5

# Generate only diagrams with AI
python3 dev/tools/generate_content_v1_4_0.py --category fire --count 3 --diagrams-only
```

**Features:**
- 800-1200 word comprehensive guides
- Technical SVG diagrams with Polaroid palette
- Practical, survival-focused content
- Automatic formatting and structure
- Rate limiting (0.5s between API calls)

### Placeholder Mode

Use placeholders when no API key or testing structure:

```bash
# Force placeholder mode
python3 dev/tools/generate_content_v1_4_0.py --category shelter --count 10 --no-ai

# Dry run (shows what would be generated)
python3 dev/tools/generate_content_v1_4_0.py --all --dry-run
```

## Content Quality

### AI-Generated Guides

Gemini creates guides with:
- Detailed step-by-step instructions
- Safety warnings and considerations
- Materials lists
- Common mistakes to avoid
- Related topics for cross-referencing
- 800-1200 word target length

### AI-Generated Diagrams

SVG diagrams following:
- Technical-Kinetic style
- Polaroid 8-color palette only
- Clear labels and annotations
- Step-by-step visual process
- 800x600 viewBox standard

## Statistics Tracking

The tool tracks:
- Guides generated
- Diagrams generated
- API calls made
- Errors encountered
- Skipped (already exist)
- Mode (AI-Powered vs Placeholder)

Example output:
```
============================================================
📊 Content Generation Statistics
============================================================
Guides generated:   5
Diagrams generated: 5
API calls:          10
Errors:             0
Skipped (exists):   0
Total:              10
Mode:               AI-Powered
============================================================
```

## Rate Limits & Costs

### Gemini 2.5 Flash (Default Model)

- **Free tier**: 15 requests/minute, 1 million tokens/minute
- **Cost**: Free for development
- **Delay**: 0.5s between requests (built-in)

### Weekly Generation Targets

Week 1: 100 guides + 50 diagrams
- API calls: ~150
- Time: ~75 seconds (with 0.5s delays)
- Cost: $0 (within free tier)

Full v1.4.0: 1000 guides + 500 diagrams
- API calls: ~1,500
- Time: ~12.5 minutes (with delays)
- Cost: $0 (within free tier)

## Troubleshooting

### "Gemini initialization failed"

**Problem**: API key not found

**Solution**:
```bash
# Check .env file
cat .env | grep GEMINI

# Should show:
GEMINI_API_KEY='your_key_here'

# If empty, set it:
🔮 > CONFIG SET GEMINI_API_KEY your_key_here
```

### "Response not valid SVG"

**Problem**: Gemini returned text instead of SVG

**Solution**: Automatic fallback to placeholder. Retry generation:
```bash
rm knowledge/reference/diagrams/category/topic.svg
python3 dev/tools/generate_content_v1_4_0.py --category category --count 1 --diagrams-only
```

### "API rate limit exceeded"

**Problem**: Too many requests

**Solution**: Built-in 0.5s delay should prevent this. If it occurs:
```bash
# Wait 1 minute, then retry
sleep 60
python3 dev/tools/generate_content_v1_4_0.py --category water --count 10
```

## Integration with v1.3.0 GENERATE Commands

The tool uses the same Gemini service as:
- `OK ASK` - AI questions
- `GENERATE` - Script generation
- `READ` - Panel analysis

All share the same API key configuration and rate limits.

## Next Steps

1. ✅ **Week 1**: Generate 20 more guides (80 → 100) with AI
2. 🔄 **Week 2**: Begin quality validation (check word counts, structure)
3. 🔄 **Week 3-4**: Generate remaining 900 guides
4. 🔄 **Phase 2**: Expert review and refinement

## Examples

### Generate Complete Category

```bash
# Water category: 10 guides + 10 diagrams with AI
python3 dev/tools/generate_content_v1_4_0.py --category water --count 10

# Output:
# ✅ Gemini AI initialized
# 📚 Generating 10 guides...
#   ✅ Generated: finding_water_sources.md (1,042 words)
#   ✅ Generated: water_purification_methods.md (967 words)
# ...
```

### Batch Generation

```bash
# Generate first 20 guides for week 1 target
for cat in water fire shelter food; do
  python3 dev/tools/generate_content_v1_4_0.py --category $cat --count 5 --guides-only
done
```

### Quality Check

```bash
# Check word count of AI-generated guide
wc -w knowledge/water/finding_water_sources.md

# Should show: ~800-1200 words
```

---

**Version**: v1.4.0 Phase 1
**Last Updated**: 2025-11-24
**AI Model**: Gemini 2.5 Flash
