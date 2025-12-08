# Tutorial: Nano Banana Quick Start

**Version:** v1.2.21
**Duration:** 15-20 minutes
**Prerequisites:** GEMINI_API_KEY configured
**Last Updated:** December 8, 2025

## What You'll Learn

By the end of this tutorial, you'll be able to:
- ✅ Generate your first PNG→SVG diagram
- ✅ Understand style and type options
- ✅ Use command-line flags effectively
- ✅ Create batch workflows with uCODE
- ✅ Troubleshoot common issues

---

## What is Nano Banana?

**Nano Banana** is the internal codename for **Gemini 2.5 Flash Image**, Google's image generation model that is "INSANE at generating LINE ART".

The uDOS **Nano Banana Integration** uses this model to generate high-quality monochrome PNG diagrams, then converts them to editable SVG files using a sophisticated vectorization pipeline.

**Pipeline Overview:**
```
Your Description → Nano Banana (PNG) → Vectorize → Validate → SVG File
```

**Why it's awesome:**
- 🎨 Professional Technical-Kinetic style
- ⚡ Fast generation (15-20 seconds typical)
- 📐 Perfect for knowledge base diagrams
- ✏️ Fully editable SVG output
- 🔄 Batch automation ready

---

## Step 1: Check Prerequisites

### Verify Gemini API Key

Open your `.env` file and confirm you have:
```bash
GEMINI_API_KEY=your_api_key_here
```

**Don't have a key?**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` in uDOS root directory

### Verify Vectorizers

Check if you have potrace or vtracer installed:

```bash
# Check potrace (recommended)
which potrace

# Check vtracer (fallback)
python -c "import vtracer; print('✅ vtracer installed')"
```

**Need to install?**
```bash
# macOS
brew install potrace

# Ubuntu/Debian
sudo apt install potrace

# Python fallback (any OS)
pip install vtracer>=0.6.0
```

### Test uDOS Connection

Start uDOS and verify it loads:
```bash
./start_udos.sh
```

You should see the splash screen with version **v1.1.7**.

---

## Step 2: Generate Your First Diagram

Let's start simple with a water filter diagram.

### Basic Generation

```
🔮 > GENERATE SVG water filter
```

**What happens:**
1. ⏳ Loads technical-kinetic style guide (~5-10 reference images)
2. ⏳ Sends request to Nano Banana
3. ⏳ Generates PNG (15-20 seconds)
4. ⏳ Vectorizes PNG→SVG with potrace
5. ✅ Validates Technical-Kinetic compliance
6. 💾 Saves to `memory/drafts/svg/water-filter-technical-kinetic-20251201-143022.svg`

**Expected Output:**
```
✅ SVG diagram generated: water filter
   Style: technical-kinetic
   Type: flowchart
   Vectorizer: potrace
   Time: 18.3s
   Saved: memory/drafts/svg/water-filter-technical-kinetic-20251201-143022.svg
   Validation: ✅ Technical-Kinetic compliant

🔧 Next Steps:
   - Edit: open -a 'Inkscape' memory/drafts/svg/water-filter-*.svg
   - Regenerate: GENERATE SVG water filter --style hand-illustrative
   - Refine: GENERATE SVG water filter --pro --strict
```

### View Your Diagram

Open the generated SVG in your favorite editor:

**macOS:**
```bash
open -a 'Inkscape' memory/drafts/svg/water-filter-*.svg
# or
open memory/drafts/svg/water-filter-*.svg  # Preview
```

**Linux:**
```bash
inkscape memory/drafts/svg/water-filter-*.svg
# or
xdg-open memory/drafts/svg/water-filter-*.svg
```

**Windows:**
```bash
start inkscape memory/drafts/svg/water-filter-*.svg
```

---

## Step 3: Explore Styles

Nano Banana supports 3 visual styles. Let's try them all.

### Technical-Kinetic (Default)

Clean, geometric, MCM-inspired:
```
🔮 > GENERATE SVG fire triangle --style technical-kinetic
```

**Characteristics:**
- Perfect geometric shapes
- 2-3px consistent strokes
- Curved conduits (not straight lines)
- Monochrome only (black/white)
- MCM geometry aesthetic

### Hand-Illustrative

Organic, hand-drawn feel:
```
🔮 > GENERATE SVG fire triangle --style hand-illustrative
```

**Characteristics:**
- Natural, organic lines
- Hand-drawn aesthetic
- Slightly irregular strokes
- Warm, approachable feel
- Educational materials

### Hybrid

Mix of technical and hand-drawn:
```
🔮 > GENERATE SVG fire triangle --style hybrid
```

**Characteristics:**
- Combines precision and warmth
- Technical accuracy with organic feel
- Versatile for various applications

---

## Step 4: Choose Diagram Types

Different subjects work best with different diagram types.

### Flowchart (Default)

**Best for:** Processes, decision trees, sequential steps
```
🔮 > GENERATE SVG water purification process --type flowchart
```

**Features:**
- Curved conduits
- Decision diamonds
- Process rectangles
- Flow direction indicators

### Architecture

**Best for:** System architecture, structures, component relationships
```
🔮 > GENERATE SVG shelter frame structure --type architecture
```

**Features:**
- Perfect geometric shapes
- Modular components
- Clean connections
- Hierarchical layout

### Kinetic Flow

**Best for:** Mechanical systems, motion, energy flow
```
🔮 > GENERATE SVG hand crank water pump --type kinetic-flow
```

**Features:**
- Gears and cogs
- Levers and pivots
- Motion arrows
- Mechanical linkages

### Schematic

**Best for:** Technical schematics, wiring, circuit-like layouts
```
🔮 > GENERATE SVG solar still system --type schematic
```

**Features:**
- Symbolic representations
- Connection points
- Technical annotations
- Grid-based layout

---

## Step 5: Use Advanced Options

### Pro Mode (Slower, Higher Quality)

Use Nano Banana Pro for multi-turn refinement:
```
🔮 > GENERATE SVG complex gear mechanism --pro
```

**When to use:**
- Complex mechanical diagrams
- High-detail requirements
- Publication-quality output
- Time not critical (30-45s vs 15-20s)

### Strict Validation

Enforce strict Technical-Kinetic compliance:
```
🔮 > GENERATE SVG water filter --strict
```

**What it does:**
- Blocks warnings (not just errors)
- Enforces perfect monochrome
- No gradient/filter/pattern tolerance
- Maximum aesthetic purity

**Standard vs Strict:**
| Mode | Speed | Tolerance | Use Case |
|------|-------|-----------|----------|
| Standard | Fast | Accepts warnings | Rapid iteration |
| Strict | Same | Blocks warnings | Final publication |

### Custom Filenames

Save with a specific name:
```
🔮 > GENERATE SVG water filter --save my-filter.svg
```

Output: `memory/drafts/svg/my-filter.svg`

### Combine All Options

```
🔮 > GENERATE SVG water purification system --style technical-kinetic --type flowchart --pro --strict --save water-system.svg
```

---

## Step 6: Batch Generation Workflow

Create a uCODE script for batch generation.

### Create Workflow File

Create `memory/workflows/missions/my_batch.upy`:

```upy
---
title: "My First Batch Generation"
description: "Generate multiple survival diagrams"
version: "1.0.0"
author: "Your Name"
---

# My Batch Generation Workflow

PRINT "Starting batch generation..."
PRINT "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Generate 3 diagrams
GENERATE SVG water purification filter
SLEEP 3

GENERATE SVG fire triangle --style hand-illustrative
SLEEP 3

GENERATE SVG shelter frame --type architecture
SLEEP 3

PRINT "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PRINT "✅ Batch complete! Check memory/drafts/svg/"
```

### Run Your Workflow

```
🔮 > RUN "memory/workflows/missions/my_batch.upy"
```

**Output:**
```
🚀 Executing script: my_batch.upy
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Starting batch generation...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ SVG diagram generated: water purification filter
   [... output ...]
✅ SVG diagram generated: fire triangle
   [... output ...]
✅ SVG diagram generated: shelter frame
   [... output ...]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Batch complete! Check memory/drafts/svg/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Script completed
```

### Use Example Workflows

uDOS includes 4 example workflows in `memory/ucode/examples/`:

1. **nano_banana_quick_start.upy** - Beginner tutorial (this guide!)
2. **nano_banana_batch.upy** - Batch generation with tracking
3. **nano_banana_quality_check.upy** - Quality validation + retry logic
4. **nano_banana_styles_demo.upy** - All style/type combinations

Run any example:
```
🔮 > RUN "memory/ucode/examples/nano_banana_batch.upy"
```

---

## Step 7: Troubleshooting

### Problem: "GEMINI_API_KEY not found"

**Solution:**
```bash
# Edit .env file
nano .env

# Add this line:
GEMINI_API_KEY=your_key_here

# Save and restart uDOS
./start_udos.sh
```

### Problem: "Failed to vectorize PNG"

**Solution:**
```bash
# Install potrace (recommended)
brew install potrace  # macOS
sudo apt install potrace  # Linux

# OR install vtracer (Python fallback)
pip install vtracer>=0.6.0
```

### Problem: "Validation failed (strict mode)"

**Cause:** Generated SVG has warnings (not errors)

**Solutions:**
1. Remove `--strict` flag (accept warnings):
   ```
   GENERATE SVG water filter
   ```

2. Try different style:
   ```
   GENERATE SVG water filter --style hand-illustrative
   ```

3. Use Pro mode for better quality:
   ```
   GENERATE SVG water filter --pro
   ```

### Problem: Generation takes >30 seconds

**Causes:**
- Using `--pro` mode (30-45s typical)
- Network latency
- API throttling

**Solutions:**
1. Use standard mode (remove `--pro`)
2. Check network speed
3. Add 3-5 second delays between batch requests

### Problem: "Rate limit exceeded"

**Solution:**
```bash
# Add delays between requests
GENERATE SVG diagram1
SLEEP 5
GENERATE SVG diagram2
SLEEP 5
GENERATE SVG diagram3
```

---

## Step 8: Best Practices

### Subject Descriptions

**✅ Good:**
- "water purification filter" (specific, clear)
- "fire triangle with labels" (descriptive)
- "shelter frame structure cross-section" (detailed)

**❌ Avoid:**
- "thing" (too vague)
- "make me a really cool diagram of a super complex water purification system with multiple stages and filters and pumps and stuff" (too long, unfocused)
- Single words like "water" (too broad)

**Optimal Length:** 3-7 words

### Style Selection

| Subject | Recommended Style |
|---------|------------------|
| Technical diagrams | technical-kinetic |
| Educational materials | hand-illustrative |
| Versatile/unknown | hybrid |
| Publication | technical-kinetic + --strict |

### Type Selection

| Subject | Recommended Type |
|---------|-----------------|
| Processes, steps | flowchart |
| Structures, systems | architecture |
| Mechanical, motion | kinetic-flow |
| Technical specs | schematic |

### Batch Generation Tips

1. **Add delays:** 3-5 seconds between requests
2. **Track progress:** Use PRINT statements
3. **Error handling:** Check output for ✅ vs ❌
4. **Save logs:** Redirect output to file

```upy
# Good batch workflow
FOR $topic IN ["water", "fire", "shelter"]
  PRINT "Generating: $topic"
  GENERATE SVG $topic --no-preview
  SLEEP 3
DONE
```

---

## Step 9: Edit Your SVGs

### Recommended Editors

**Inkscape** (Free, cross-platform):
```bash
brew install inkscape  # macOS
sudo apt install inkscape  # Linux
```

**Adobe Illustrator** (Professional):
- Import SVG directly
- Full editing capabilities

**VS Code** (Code editing):
- Install "SVG" extension
- Live preview while editing

### Common Edits

1. **Adjust stroke width:**
   - Select all paths
   - Set stroke to 2-3px
   - Ensure uniform width

2. **Add labels:**
   - Use sans-serif font
   - Keep text simple
   - Maintain monochrome

3. **Refine paths:**
   - Simplify complex curves
   - Clean up artifacts
   - Optimize node count

4. **Export variations:**
   - PNG for web (optimize size)
   - PDF for print (embed fonts)
   - SVG for editing (keep original)

---

## Next Steps

### Explore More Features

1. **Create custom style guides** - See [Nano Banana Integration Guide](Nano-Banana-Integration#custom-style-guides)
2. **Build complex workflows** - See `memory/ucode/examples/`
3. **Integrate with missions** - See [Workflows Guide](Workflows)
4. **Generate ASCII alternatives** - `GENERATE ASCII <description>`

### Join the Community

- **GitHub Issues:** Report bugs, request features
- **Discussions:** Share your workflows and diagrams
- **Wiki Contributions:** Improve documentation

### Learning Resources

- **[Nano Banana Integration Guide](Nano-Banana-Integration)** - Deep dive into pipeline
- **[Command Reference](Command-Reference)** - All GENERATE options
- **[uCODE Workflows](Workflows)** - Automation guide
- **[Content Generation](Content-Generation)** - Complete generation system

---

## Summary

You've learned how to:
- ✅ Generate PNG→SVG diagrams with Nano Banana
- ✅ Choose appropriate styles (technical-kinetic, hand-illustrative, hybrid)
- ✅ Select diagram types (flowchart, architecture, kinetic-flow, schematic)
- ✅ Use command options (--pro, --strict, --save, --style, --type)
- ✅ Create batch workflows with uCODE
- ✅ Troubleshoot common issues
- ✅ Edit SVGs in external tools

**Next:** Start generating diagrams for your knowledge base!

```
🔮 > GENERATE SVG your amazing idea --style technical-kinetic
```

---

## Quick Reference Card

### Essential Commands
```bash
# Basic generation
GENERATE SVG <description>

# With style
GENERATE SVG <description> --style hand-illustrative

# With type
GENERATE SVG <description> --type architecture

# Pro mode
GENERATE SVG <description> --pro

# Strict validation
GENERATE SVG <description> --strict

# Custom filename
GENERATE SVG <description> --save myfile.svg

# Full options
GENERATE SVG <description> --style technical-kinetic --type flowchart --pro --strict --save file.svg
```

### Styles
- `technical-kinetic` (default) - MCM geometry, precise
- `hand-illustrative` - Organic, hand-drawn
- `hybrid` - Mix of both

### Types
- `flowchart` (default) - Processes, flows
- `architecture` - Structures, systems
- `kinetic-flow` - Mechanical, motion
- `schematic` - Technical specs

### Workflow Template
```upy
---
title: "Your Workflow"
description: "Description here"
---

PRINT "Starting generation..."

GENERATE SVG topic1 --style technical-kinetic
SLEEP 3

GENERATE SVG topic2 --style hand-illustrative
SLEEP 3

PRINT "✅ Complete!"
```

---

**Tutorial Version:** 1.1.7
**Last Updated:** December 1, 2025
**Duration:** 15-20 minutes
**Next:** [Nano Banana Integration Guide](Nano-Banana-Integration)
