# Round 2 Progress Session - 2025-12-02

## Completed Work

### 1. STORY Command Integration (Complete)

**Files Modified:**
- `core/uDOS_commands.py` - Registered STORY handler in main command loop
- `core/commands/story_handler.py` - Refactored to match command handler pattern

**Changes:**
- Changed `handle()` signature from `handle(args) -> bool` to `handle(command, params) -> str`
- Removed all `self.output.print()` calls
- All methods now return strings instead of booleans
- Properly integrated with StoryHandler components dict

**Test Results:**
- ✅ STORY LIST - Discovers 4 adventures (fire_quest, water_quest, shelter_quest, first-steps)
- ✅ STORY HELP - Displays full command reference
- ✅ Handler initialization successful

**Git Commit:** `b34675c1` - Round 2: STORY command integration

---

### 2. .upy Adventure Format Specification (Complete)

**File Created:**
- `core/docs/upy-adventure-format.md` (540 lines)

**Documentation Includes:**

#### Core Keywords (13 total):
1. **CHOICE/OPTION** - Present player choices with jump targets
2. **LABEL** - Define jump destinations
3. **BRANCH** - Unconditional jumps
4. **ROLL** - Dice rolls for skill checks (1d20, 2d6, etc.)
5. **IF/ENDIF** - Conditional branching
6. **FLAG** - Story state tracking
7. **XP** - Experience point awards
8. **HP** - Health modification
9. **STAMINA** - Energy modification
10. **GIVE** - Add items to inventory
11. **TAKE** - Remove items from inventory
12. **PRINT** - Display narrative text
13. **SET** - Variable assignment

#### Integration Points:
- ScenarioEngine: Event execution
- SPRITE: Character stats (HP, XP, Level)
- OBJECT: Inventory system
- XPService: Experience/leveling
- SurvivalService: Hunger/thirst/health

#### Examples Provided:
- Standard D20 skill check pattern
- Diamond branching (converge after split)
- Loop prevention with counters
- Complete mini-adventure (Lost in the Woods)

#### Best Practices:
- LABEL naming: `UPPER-CASE-WITH-DASHES`
- Flag naming: `lowercase_with_underscores`
- Skill check tiers (critical/success/partial/failure)
- Comment documentation

**Git Commit:** `cfa21322` - Round 2: .upy adventure format specification

---

## Existing Adventures Discovered

During testing, found 3 pre-existing .upy adventures in `sandbox/ucode/adventures/`:

1. **fire_quest.upy** (13,013 bytes, 572 lines)
   - Build fire using primitive methods
   - Complex branching with skill checks
   - Demonstrates friction fire, flint/steel, battery, lens methods

2. **water_quest.upy** (13,804 bytes, 585 lines)
   - Find and purify water in wilderness
   - Multiple search paths (tracks, vegetation, sounds, dew)
   - Water purification methods

3. **shelter_quest.upy** (11,523 bytes)
   - Build shelter for survival
   - Similar structure to fire/water quests

All 3 quests already use the .upy format with CHOICE/OPTION/BRANCH/LABEL/ROLL/IF keywords!

---

## Current Round 2 Status

### Completed (40%):
- [x] STORY command design
- [x] STORY handler implementation
- [x] Command loop integration
- [x] Handler refactoring (string returns)
- [x] .upy format specification
- [x] Documentation (core/docs/)

### In Progress:
- [ ] .upy parser implementation (next)
- [ ] Convert first-steps.json → first-steps.upy
- [ ] SPRITE integration (auto-create character, display stats)
- [ ] OBJECT integration (inventory sync)

### Pending:
- [ ] Create 2-3 more adventures
- [ ] Integration tests (25+ tests)
- [ ] Wiki documentation (Adventure-Scripting.md)
- [ ] Test in main uDOS loop

---

## Next Steps

### Immediate (Next 1-2 hours):

1. **Implement .upy Parser**
   - File: `core/services/game/upy_adventure_parser.py`
   - Tokenize .upy scripts
   - Convert to ScenarioEngine event format
   - Handle CHOICE/ROLL/IF/BRANCH/LABEL
   - Validate syntax and label references

2. **Convert first-steps.json → first-steps.upy**
   - Use as test case for parser
   - Validate parser output
   - Compare with existing fire/water/shelter quests

3. **Test Parser**
   - Parse fire_quest.upy (existing)
   - Parse water_quest.upy (existing)
   - Parse first-steps.upy (converted)
   - Validate event structure

### Short-Term (Next 2-3 hours):

4. **SPRITE Integration**
   - Auto-create player sprite on STORY START
   - Update sprite stats during adventure (HP, XP, stamina)
   - Display sprite stats in STORY STATUS
   - Use sprite_handler from Round 1

5. **OBJECT Integration**
   - Sync adventure items with OBJECT system
   - GIVE/TAKE commands update inventory
   - Display inventory in STORY STATUS
   - Use object_handler from Round 1

6. **Integration Tests**
   - Test STORY START with .upy files
   - Test CHOICE selection and branching
   - Test ROLL mechanics
   - Test stat updates (XP, HP, inventory)
   - Test save/load persistence

---

## Architecture Notes

### ScenarioEngine Event Format

The parser needs to convert .upy to this format:

```python
{
    "type": "narrative" | "choice" | "skill_check" | "end",
    "content": "Text to display",
    "choices": [
        {
            "text": "Choice 1",
            "next_event": "event_id_2"
        }
    ],
    "effects": [
        {
            "type": "stat_change" | "item_give" | "xp_award" | "effect_add",
            "target": "thirst" | "hp" | "xp",
            "value": -10 | 50 | "water_bottle"
        }
    ],
    "conditions": [
        {
            "type": "flag" | "stat" | "item",
            "key": "found_water",
            "operator": "==",
            "value": true
        }
    ]
}
```

### Parser Components

1. **Lexer** - Tokenize .upy into commands
2. **Parser** - Build AST (Abstract Syntax Tree)
3. **Validator** - Check label references, syntax
4. **Converter** - Transform to ScenarioEngine events
5. **Executor** - Feed events to ScenarioEngine

---

## Git Commits Today

1. `3af4ff5c` - Round 2: STORY command foundation (+906 lines)
2. `b34675c1` - Round 2: STORY command integration (+101, -123 lines)
3. `cfa21322` - Round 2: .upy adventure format specification (+540 lines)

**Total:** 3 commits, ~1,424 lines added/modified

---

## Round 2 Completion Estimate

Based on remaining work:

- **Current:** 40% complete
- **After parser:** 55% complete (+15%)
- **After SPRITE/OBJECT:** 70% complete (+15%)
- **After tests:** 85% complete (+15%)
- **After wiki docs:** 100% complete (+15%)

**Estimated Total Time:** 8-10 hours
**Time Spent:** ~3 hours
**Remaining:** ~5-7 hours

---

*Session Date: 2025-12-02*
*Status: Round 2 foundation solid, parser implementation next*
