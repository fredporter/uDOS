# Nano Banana Completion Plan - v1.1.7

**Date:** December 1, 2025
**Status:** 🔨 ACTIVE DEVELOPMENT
**Remaining:** 3 tasks, 5-8 hours estimated
**Goal:** Complete Nano Banana PNG→SVG system for v1.1.7 release

---

## Current Status (80% Complete)

### ✅ Completed (5/8 tasks)

1. ✅ Architecture design (500+ line spec)
2. ✅ Gemini Image integration (`generate_image_svg()`)
3. ✅ Vectorization service (potrace + vtracer)
4. ✅ Style guide system (infrastructure)
5. ✅ GENERATE command handler (580 lines)

### ⏳ Remaining (3/8 tasks)

**Task 6: Workflow Integration** (2-3 hours)
**Task 7: Testing Completion** (2-3 hours)
**Task 8: Documentation Polish** (1-2 hours)

---

## Task 6: Workflow Integration (2-3 hours)

### Objective
Create production-ready uCODE workflows for batch SVG generation with quality validation.

### Files to Create/Update

#### 1. Update `sandbox/workflow/content_generation.uscript`
**Status:** EXISTS - needs Nano Banana integration
**Action:** Add GENERATE SVG examples and workflow patterns

**Content:**
```uscript
# Nano Banana SVG Generation Workflow
# Generate high-quality Technical-Kinetic diagrams

SET category "water"
SET topics ["purification", "filtration", "storage", "collection"]

# Generate diagrams for each topic
FOR topic IN $topics
    PRINT "Generating SVG: $category/$topic"
    GENERATE SVG "$category $topic" --style technical-kinetic --type flowchart
    SLEEP 2  # API rate limiting
DONE

PRINT "✅ Batch generation complete"
```

#### 2. Create `sandbox/workflow/examples/nano_banana_quick_start.uscript`
**Status:** NEW
**Action:** Create beginner-friendly workflow

**Content:**
```uscript
# Nano Banana Quick Start - Single SVG Generation
# Demonstrates basic GENERATE SVG usage

PRINT "🎨 Nano Banana Quick Start"
PRINT "Generating water filtration diagram..."

# Generate single SVG
GENERATE SVG "water filtration system" --style technical-kinetic

PRINT "✅ SVG generated in sandbox/drafts/svg/"
PRINT "💡 Try: --pro for higher quality"
PRINT "💡 Try: --strict for validation"
```

#### 3. Create `sandbox/workflow/examples/nano_banana_batch.uscript`
**Status:** NEW
**Action:** Create production batch workflow

**Content:**
```uscript
# Nano Banana Batch Generation - Knowledge Base Diagrams
# Generate SVGs for multiple knowledge categories

SET categories ["water", "fire", "shelter", "food"]
SET success_count 0
SET fail_count 0

PRINT "🎨 Batch SVG Generation Starting..."
PRINT "Categories: $categories"
PRINT ""

FOR category IN $categories
    PRINT "📂 Processing: $category"
    
    # Generate overview diagram
    GENERATE SVG "$category overview" --type architecture --save "$category-overview.svg"
    
    IF $? == 0
        SET success_count ($success_count + 1)
        PRINT "  ✅ Success: $category-overview.svg"
    ELSE
        SET fail_count ($fail_count + 1)
        PRINT "  ❌ Failed: $category-overview.svg"
    ENDIF
    
    SLEEP 2  # Rate limiting
DONE

PRINT ""
PRINT "📊 Batch Generation Complete"
PRINT "  ✅ Successful: $success_count"
PRINT "  ❌ Failed: $fail_count"
```

#### 4. Create `sandbox/workflow/examples/nano_banana_quality_check.uscript`
**Status:** NEW
**Action:** Create quality validation workflow

**Content:**
```uscript
# Nano Banana Quality Check - Validation & Refinement
# Generate with strict validation, retry if needed

SET subject "water purification filter"
SET max_attempts 3
SET attempt 1

PRINT "🎨 Quality-Checked SVG Generation"
PRINT "Subject: $subject"
PRINT "Max attempts: $max_attempts"
PRINT ""

WHILE $attempt <= $max_attempts
    PRINT "Attempt $attempt/$max_attempts..."
    
    # Generate with strict validation
    GENERATE SVG "$subject" --strict --pro
    
    IF $? == 0
        PRINT "✅ Quality check passed!"
        BREAK
    ELSE
        PRINT "⚠️  Validation failed, retrying..."
        SET attempt ($attempt + 1)
        SLEEP 3
    ENDIF
DONE

IF $attempt > $max_attempts
    PRINT "❌ Failed after $max_attempts attempts"
    EXIT 1
ENDIF
```

#### 5. Update Mission Templates
**Files:**
- `sandbox/workflow/templates/knowledge_expansion.mission`
- `sandbox/workflow/mission_templates.uscript`

**Action:** Add Nano Banana generation steps to mission templates

---

## Task 7: Testing Completion (2-3 hours)

### Objective
Verify all components work end-to-end with live API testing and achieve 95% coverage.

### Testing Strategy

#### 1. Live API Testing (requires Gemini key)

**Prerequisites:**
- Valid GEMINI_API_KEY in `.env`
- Gemini API credits available
- Internet connection

**Test Script: `sandbox/tests/live_nano_banana_test.py`**

```python
"""
Live Nano Banana API Test - Requires Gemini Key
Run: pytest sandbox/tests/live_nano_banana_test.py -v -s
"""

import pytest
import os
from pathlib import Path
from core.services.gemini_generator import GeminiGenerator
from core.services.vectorizer import Vectorizer

# Skip if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv('GEMINI_API_KEY'),
    reason="Requires GEMINI_API_KEY in environment"
)

class TestLiveNanoBanana:
    """Live API tests for Nano Banana pipeline."""
    
    def test_generate_simple_png(self):
        """Test basic PNG generation via Nano Banana."""
        gen = GeminiGenerator()
        
        png_bytes, metadata = gen.generate_image_svg(
            "simple water filter diagram",
            style="technical-kinetic",
            diagram_type="flowchart",
            use_pro=False
        )
        
        assert png_bytes is not None
        assert len(png_bytes) > 0
        assert metadata['model'] == 'gemini-2.0-flash-exp'
    
    def test_png_to_svg_pipeline(self):
        """Test complete PNG → SVG pipeline."""
        gen = GeminiGenerator()
        vec = Vectorizer()
        
        # Generate PNG
        png_bytes, metadata = gen.generate_image_svg(
            "fire triangle",
            style="technical-kinetic",
            diagram_type="schematic"
        )
        
        # Vectorize to SVG
        result = vec.vectorize_png(png_bytes, method='potrace')
        
        assert result.svg_content is not None
        assert '<svg' in result.svg_content
        assert result.validation.is_valid
    
    def test_style_guide_loading(self):
        """Test loading of style guide reference images."""
        gen = GeminiGenerator()
        
        references = gen.load_style_guide('technical-kinetic')
        
        # Should work with 0 references (fallback)
        assert isinstance(references, list)
        # If references exist, validate format
        if references:
            assert all(isinstance(ref, bytes) for ref in references)
```

#### 2. Integration Testing

**Test Script: `sandbox/tests/integration_nano_banana_test.py`**

```python
"""
Integration Tests - GENERATE Handler with Mocked Services
Run: pytest sandbox/tests/integration_nano_banana_test.py -v
"""

import pytest
from unittest.mock import Mock, patch
from core.commands.generate_handler import GenerateHandler, handle_generate_command

class TestGenerateIntegration:
    """Integration tests for GENERATE command handler."""
    
    @patch('core.commands.generate_handler.GeminiGenerator')
    @patch('core.commands.generate_handler.Vectorizer')
    def test_full_svg_generation_flow(self, mock_vec, mock_gen):
        """Test complete SVG generation workflow."""
        # Mock PNG generation
        mock_gen.return_value.generate_image_svg.return_value = (
            b'fake_png_data',
            {'model': 'gemini-2.0-flash-exp', 'size': (1200, 900)}
        )
        
        # Mock vectorization
        mock_vec.return_value.vectorize_png.return_value.svg_content = '<svg>test</svg>'
        mock_vec.return_value.vectorize_png.return_value.validation.is_valid = True
        
        # Execute command
        result = handle_generate_command(
            ['SVG', 'test diagram', '--style', 'technical-kinetic'],
            grid=None,
            parser=None
        )
        
        assert 'Success' in result or 'generated' in result.lower()
        assert mock_gen.return_value.generate_image_svg.called
        assert mock_vec.return_value.vectorize_png.called
```

#### 3. Coverage Verification

**Run:**
```bash
cd /Users/fredbook/Code/uDOS
pytest sandbox/tests/test_generate_handler.py \
       sandbox/tests/test_nano_banana_pipeline.py \
       --cov=core/commands/generate_handler \
       --cov=core/services/gemini_generator \
       --cov=core/services/vectorizer \
       --cov-report=html \
       --cov-report=term
```

**Target:** 95% coverage

**Critical Paths:**
- GENERATE SVG command parsing
- PNG generation (with/without style guides)
- Vectorization (potrace + vtracer fallback)
- Validation engine
- Error handling

---

## Task 8: Documentation Polish (1-2 hours)

### Objective
Complete documentation with tutorials, examples, and troubleshooting.

### Documentation Updates

#### 1. Update `wiki/Command-Reference.md`

**Section to Add:**

```markdown
### GENERATE

Generate diagrams, ASCII art, and graphics using AI or offline methods.

#### GENERATE SVG

Generate vector diagrams via Gemini 2.5 Flash Image (Nano Banana).

**Syntax:**
```
GENERATE SVG <description> [options]
```

**Options:**
- `--style <style>` — Visual style (technical-kinetic, hand-illustrative, hybrid)
- `--type <type>` — Diagram type (flowchart, architecture, schematic, etc.)
- `--save <file>` — Save to specific file
- `--pro` — Use Nano Banana Pro (slower, higher quality)
- `--strict` — Enforce strict Technical-Kinetic validation

**Examples:**
```
GENERATE SVG water filter
GENERATE SVG fire triangle --style hand-illustrative
GENERATE SVG shelter design --type architecture --save shelter.svg --pro
```

**Pipeline:** Style Guide → Nano Banana (PNG) → Vectorize → Validate → Save SVG

**See Also:** `wiki/Nano-Banana-Integration.md` for full documentation
```

#### 2. Create Tutorial: `wiki/Tutorial-Nano-Banana.md`

**Content:**
```markdown
# Tutorial: Creating Technical Diagrams with Nano Banana

Learn how to generate high-quality vector diagrams using uDOS's Nano Banana system.

## What You'll Learn
- Generate your first SVG diagram
- Use style guides for consistency
- Batch generate multiple diagrams
- Quality check and validation

## Prerequisites
- Gemini API key configured
- uDOS v1.1.6+ installed
- Basic uCODE knowledge

## Step 1: Your First Diagram (2 minutes)

Generate a simple water filtration diagram:

```bash
GENERATE SVG "water filtration system"
```

**What happens:**
1. System loads Technical-Kinetic style guide
2. Sends prompt to Gemini 2.5 Flash Image (Nano Banana)
3. Receives high-quality monochrome PNG
4. Vectorizes PNG to SVG using potrace
5. Validates Technical-Kinetic compliance
6. Saves SVG to `sandbox/drafts/svg/`

**Output:**
```
🎨 Generating SVG: water filtration system
📸 Nano Banana: Generating PNG...
🔄 Vectorizing: potrace method
✅ Validation: Technical-Kinetic compliant
💾 Saved: sandbox/drafts/svg/water-filtration-system-2025-12-01-1430.svg
```

## Step 2: Customize with Styles (5 minutes)

Try different visual styles:

```bash
# Technical-Kinetic (default) - Clean, precise diagrams
GENERATE SVG "fire triangle" --style technical-kinetic

# Hand-Illustrative - Sketchy, organic look
GENERATE SVG "fire triangle" --style hand-illustrative

# Hybrid - Mix of technical and hand-drawn
GENERATE SVG "fire triangle" --style hybrid
```

## Step 3: Choose Diagram Types (5 minutes)

Different diagram types optimize for specific use cases:

```bash
# Flowchart - Process flows and sequences
GENERATE SVG "water purification process" --type flowchart

# Architecture - System diagrams and structures
GENERATE SVG "shelter design" --type architecture

# Schematic - Technical diagrams with precise geometry
GENERATE SVG "fire triangle chemistry" --type schematic

# Kinetic-Flow - Movement and energy transfer
GENERATE SVG "water cycle" --type kinetic-flow
```

## Step 4: Quality Mode (10 minutes)

Use Pro mode for highest quality:

```bash
# Standard mode (fast, <30s)
GENERATE SVG "solar water heater"

# Pro mode (slower, <60s, higher quality)
GENERATE SVG "solar water heater" --pro
```

## Step 5: Batch Generation (15 minutes)

Create a workflow file: `my_diagrams.uscript`

```uscript
# Generate survival knowledge diagrams
SET topics ["water purification", "fire starting", "shelter building"]

FOR topic IN $topics
    PRINT "Generating: $topic"
    GENERATE SVG "$topic" --type flowchart
    SLEEP 2  # Rate limiting
DONE
```

Run: `uDOS my_diagrams.uscript`

## Step 6: Quality Validation (10 minutes)

Enforce strict Technical-Kinetic compliance:

```bash
# Strict validation mode
GENERATE SVG "complex shelter" --strict

# If validation fails, try Pro mode
GENERATE SVG "complex shelter" --strict --pro
```

## Troubleshooting

**Problem:** "GEMINI_API_KEY not found"
**Solution:** Add `GEMINI_API_KEY=your-key-here` to `.env`

**Problem:** "Vectorization failed"
**Solution:** Install potrace: `brew install potrace` (macOS)

**Problem:** "Validation failed: gradients detected"
**Solution:** Regenerate with `--strict` flag or accept with `--no-strict`

## Next Steps

- Read: `wiki/Nano-Banana-Integration.md` (full documentation)
- Explore: `sandbox/workflow/examples/` (more workflows)
- Create: Custom style guides in `extensions/assets/styles/`
```

#### 3. Expand Troubleshooting in `wiki/Nano-Banana-Integration.md`

**Add section:**

```markdown
## Troubleshooting Guide

### PNG Generation Issues

**Error:** "GEMINI_API_KEY not found"
```python
# Check .env file
GEMINI_API_KEY=your-key-here
```

**Error:** "API quota exceeded"
- Wait for quota reset (usually next billing cycle)
- Use `--no-strict` to reduce regenerations
- Batch process with delays: `SLEEP 2` between calls

**Error:** "PNG extraction failed"
- Check Gemini API status
- Try Pro mode: `--pro`
- Verify internet connection

### Vectorization Issues

**Error:** "potrace not found"
```bash
# macOS
brew install potrace

# Linux (Ubuntu/Debian)
sudo apt-get install potrace

# Fallback to vtracer (Python)
pip install vtracer
```

**Error:** "Vectorization produced invalid SVG"
- Try vtracer method: configure in settings
- Check PNG quality (should be high-res monochrome)
- Regenerate PNG with `--pro`

### Validation Issues

**Warning:** "Gradients detected (not monochrome)"
- Regenerate with explicit monochrome prompt
- Use `--strict` flag for enforcement
- Check style guide images are monochrome

**Warning:** "Stroke width inconsistent"
- Run with `--normalize` (default enabled)
- Check vectorization method (potrace preferred)
- Manually adjust in SVG editor

### Performance Issues

**Problem:** Generation takes >60s
- Standard mode should be <30s
- Pro mode can take <60s (expected)
- Check internet speed and Gemini API latency

**Problem:** High API costs
- Use standard mode (not Pro) when possible
- Batch process efficiently
- Cache/reuse similar diagrams
```

---

## Implementation Timeline

### Session 1 (2-3 hours) - Workflow Integration
- [ ] Update `content_generation.uscript`
- [ ] Create `nano_banana_quick_start.uscript`
- [ ] Create `nano_banana_batch.uscript`
- [ ] Create `nano_banana_quality_check.uscript`
- [ ] Update mission templates

### Session 2 (2-3 hours) - Testing
- [ ] Create `live_nano_banana_test.py`
- [ ] Create `integration_nano_banana_test.py`
- [ ] Run live API tests (requires Gemini key)
- [ ] Verify 95% coverage
- [ ] Fix any discovered issues

### Session 3 (1-2 hours) - Documentation
- [ ] Update `Command-Reference.md`
- [ ] Create `Tutorial-Nano-Banana.md`
- [ ] Expand troubleshooting in `Nano-Banana-Integration.md`
- [ ] Review all wiki docs for consistency
- [ ] Add examples and screenshots

### Session 4 (30 min) - Release
- [ ] Update CHANGELOG.md with v1.1.7 entry
- [ ] Tag release: `git tag v1.1.7`
- [ ] Push to GitHub
- [ ] Update roadmap status

---

## Success Criteria

- [ ] All 3 remaining tasks complete (6/8 → 8/8)
- [ ] Live API tests passing (with Gemini key)
- [ ] 95%+ test coverage achieved
- [ ] Tutorial complete and tested
- [ ] Workflow examples functional
- [ ] Documentation comprehensive
- [ ] v1.1.7 tagged and released

---

## Notes

**Dependencies:**
- Gemini API key required for live testing
- potrace recommended (vtracer fallback)
- Internet connection for API calls

**Optional Enhancements (post-v1.1.7):**
- Style guide reference PNGs (high-quality examples)
- Video tutorial walkthrough
- Integration with mission system
- Batch processing UI

---

**Status:** Ready to begin implementation
**Estimated Total Time:** 5-8 hours across 4 sessions
**Target Completion:** December 2-3, 2025
