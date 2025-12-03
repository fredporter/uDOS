# Running Knowledge Expansion Workflow - Quick Start Guide

**Date:** December 3, 2025  
**Workflow:** `memory/workflows/missions/knowledge-expansion.upy`  
**Status:** ⚠️  **NOT YET EXECUTABLE** - Dependencies incomplete

---

## Current Status

### ✅ What's Complete

1. **Workflow File** - `knowledge-expansion.upy` (1,352 lines)
   - 6 phases fully designed
   - Variable system integrated
   - Checkpoint system included
   - Documentation complete

2. **Knowledge Topics List** - `core/data/knowledge_topics.json`
   - 100 topics across 6 categories
   - Priority rankings (critical, high, medium, low)
   - Word count targets
   - Descriptions and difficulty ratings

3. **STORY Handler** - `core/commands/story_handler.py`
   - Adventure system complete
   - State management working
   - Ready for .upy execution

### ❌ What's Missing (Blockers)

1. **GENERATE GUIDE command** - Not yet implemented
   - Workflow calls `GENERATE GUIDE <topic>` on line ~350
   - This command doesn't exist yet
   - **BLOCKER**: Can't generate content without this

2. **DOCS REVIEW command** - Not yet implemented
   - Workflow calls `DOCS REVIEW <file>` on line ~580
   - 4-dimension quality scoring not available
   - **BLOCKER**: Can't validate quality without this

3. **DOCS REGEN command** - Not yet implemented
   - Workflow calls `DOCS REGEN <file>` for low-scoring articles
   - **BLOCKER**: Can't improve content without this

4. **uCODE Interpreter** - Partial implementation
   - .upy parser exists for adventures (extensions/play/services/game_mechanics/upy_adventure_parser.py)
   - No general-purpose .upy executor in core
   - **BLOCKER**: Can't run workflow scripts

---

## How to Run (Once Dependencies Complete)

### Option 1: Via uDOS Interactive Mode

```bash
# Start uDOS
./start_udos.sh

# In uDOS shell
🔮 > WORKFLOW RUN knowledge-expansion.upy water
```

### Option 2: Direct Execution

```bash
# Assuming uCODE interpreter exists
./start_udos.sh memory/workflows/missions/knowledge-expansion.upy water
```

### Option 3: Python Direct Call

```python
from core.interpreters.ucode import UCODEInterpreter

interpreter = UCODEInterpreter()
result = interpreter.execute_file("memory/workflows/missions/knowledge-expansion.upy", args=["water"])
print(result)
```

---

## What You CAN Do Right Now

### 1. Test STORY Handler (Working!)

```bash
./start_udos.sh

🔮 > STORY LIST
🔮 > STORY HELP
```

### 2. Explore Workflow Structure

```bash
🔮 > CAT memory/workflows/missions/knowledge-expansion.upy
```

### 3. Check Knowledge Topics

```bash
🔮 > CAT core/data/knowledge_topics.json
```

### 4. Manual Content Generation (Workaround)

**Until GENERATE GUIDE is implemented, you can:**

1. **Use ASK command** (requires GEMINI_API_KEY):
   ```bash
   🔮 > ASK "Generate a comprehensive survival guide on water purification methods"
   ```

2. **Create guides manually**:
   ```bash
   🔮 > EDIT knowledge/water/ceramic-filters.md
   ```

3. **Use external tools** and import:
   - Write content in your editor
   - Save to `knowledge/<category>/`
   - Use uDOS file commands to organize

---

## Dependency Resolution Plan

### Priority 1: GENERATE GUIDE Command (Critical)

**What it needs to do:**
```
GENERATE GUIDE <topic> [--category <cat>] [--style <style>]

Example:
  GENERATE GUIDE "ceramic water filters" --category water --style technical
```

**Implementation path:**
1. Use existing `generate_handler.py` as base
2. Add `GUIDE` subcommand
3. Integrate with:
   - Knowledge bank templates
   - Gemini API (for content generation)
   - Markdown formatting
4. Output to: `memory/workflows/state/generated/<topic>.md`

**Estimated Time:** 2-3 days

### Priority 2: DOCS REVIEW Command (Critical)

**What it needs to do:**
```
DOCS REVIEW <file> [--threshold <score>]

Returns:
{
  "file": "ceramic-filters.md",
  "scores": {
    "completeness": 90,
    "clarity": 85,
    "accuracy": 88,
    "usefulness": 92
  },
  "overall": 88.75,
  "passed": true,
  "issues": [],
  "suggestions": []
}
```

**Implementation path:**
1. Create `docs_review_handler.py`
2. Implement 4-dimension scoring:
   - Completeness: Section coverage, word count
   - Clarity: Readability, structure
   - Accuracy: Fact-checking (basic)
   - Usefulness: Practical value
3. JSON output for workflow consumption

**Estimated Time:** 3-4 days

### Priority 3: DOCS REGEN Command (High)

**What it needs to do:**
```
DOCS REGEN <file> [--focus <dimension>]

Example:
  DOCS REGEN ceramic-filters.md --focus clarity
```

**Implementation path:**
1. Load existing content
2. Identify weak areas from DOCS REVIEW
3. Call Gemini to regenerate specific sections
4. Preserve good sections, replace weak ones
5. Save improved version

**Estimated Time:** 2-3 days

### Priority 4: uCODE Interpreter (Medium)

**What it needs to do:**
- Parse .upy files
- Execute commands sequentially
- Handle variables ($MISSION.*, $WORKFLOW.*, etc.)
- Support control flow (IF, WHILE, FOR)
- Integrate with command system

**Implementation path:**
1. Extend existing upy_adventure_parser.py
2. Create general-purpose executor
3. Variable resolution system
4. Command dispatching to handlers

**Estimated Time:** 4-5 days

---

## Total Timeline to Full Execution

**Fast Track (3 weeks):**
- Week 1: GENERATE GUIDE + DOCS REVIEW
- Week 2: DOCS REGEN + uCODE interpreter
- Week 3: Integration testing + bug fixes

**Conservative (4-5 weeks):**
- Include comprehensive testing
- Full documentation
- Edge case handling
- Performance optimization

---

## Alternative: Simplified Manual Workflow

**Until automation is ready, you can follow this manual process:**

### Week 1: Water Category

1. **Gap Analysis** (Manual)
   ```bash
   # Check what exists
   ls -la knowledge/water/
   
   # Compare to topics list
   cat core/data/knowledge_topics.json | grep "water"
   ```

2. **Content Generation** (Manual via ASK)
   ```bash
   🔮 > ASK "Generate comprehensive guide: ceramic water filters"
   🔮 > SAVE memory/workflows/state/ceramic-filters.md
   ```

3. **Quality Review** (Manual)
   - Read the generated content
   - Check completeness
   - Verify accuracy
   - Edit as needed

4. **Move to Knowledge Bank** (Manual)
   ```bash
   🔮 > COPY memory/workflows/state/ceramic-filters.md knowledge/water/
   ```

5. **Git Commit** (Manual)
   ```bash
   git add knowledge/water/ceramic-filters.md
   git commit -m "docs(water): Add ceramic water filters guide"
   git push
   ```

**Repeat for each topic...**

---

## Recommended Approach: Start with Move 3

**Given current state, I recommend:**

1. **Complete Move 3 first** (Adventure Scripts)
   - Water Quest .upy adventure
   - Fire Temple .upy adventure
   - Shelter Challenge .upy adventure
   - This will validate .upy execution
   - Story handler already works

2. **Then implement GENERATE consolidation** (your original request)
   - Offline-first AI engine
   - GENERATE GUIDE command
   - Gemini as extension
   - This enables knowledge-expansion.upy

3. **Finally, run knowledge expansion**
   - All dependencies met
   - Full automation working
   - Can generate 100+ guides systematically

---

## Next Actions

### If you want to test workflow execution NOW:
1. Manually create placeholder commands:
   ```bash
   # Create stub GENERATE GUIDE that echoes
   # Create stub DOCS REVIEW that returns mock scores
   # Test .upy execution with minimal dependencies
   ```

### If you want full automation:
1. Complete GENERATE consolidation (your request)
2. Implement GENERATE GUIDE, DOCS REVIEW, DOCS REGEN
3. Then run knowledge-expansion.upy

### If you want immediate value:
1. Use manual workflow (see above)
2. Generate 1-2 guides manually
3. Build automation incrementally

---

## My Recommendation

**Start with GENERATE consolidation** (what you asked for):

1. ✅ **Today**: Design architecture (DONE - see `2025-12-03-generate-consolidation-design.md`)

2. **Tomorrow**: Enhance offline.py
   - Better knowledge bank synthesis
   - FAQ integration
   - Template system

3. **Next 2-3 days**: Create unified GENERATE handler
   - GENERATE DO (default)
   - GENERATE GUIDE (content creation)
   - GENERATE SVG (via Banana)
   - GENERATE REDO (retry)

4. **Following week**: Move Gemini to extension
   - Extract from core
   - Create extension structure
   - Test optional loading

5. **Final week**: Workflow integration
   - Add $PROMPT.* variables
   - Add $API.* variables
   - Test knowledge-expansion.upy

**Total: 2-3 weeks to fully working system**

---

## Summary

**You CANNOT run knowledge-expansion.upy right now** because:
- ❌ GENERATE GUIDE command doesn't exist
- ❌ DOCS REVIEW command doesn't exist
- ❌ DOCS REGEN command doesn't exist
- ❌ General .upy interpreter incomplete

**You CAN:**
- ✅ Review workflow structure
- ✅ Check knowledge topics list
- ✅ Test STORY handler (complete)
- ✅ Generate content manually via ASK
- ✅ Start GENERATE consolidation work

**Best path forward:**
1. Complete GENERATE consolidation (2-3 weeks)
2. This implements all missing commands
3. Then knowledge-expansion.upy will work
4. Automated guide generation unlocked

Would you like me to:
- **A) Continue with GENERATE consolidation** (implement offline-first AI, unified commands)
- **B) Create stub commands** (so you can test workflow execution now)
- **C) Focus on Move 3** (adventure scripts, validate .upy system)
- **D) Something else?**
