# Migration Guide: ASSISTANT → MAKE

**Version:** v1.2.0 MAKE Consolidation
**Migration Difficulty:** Easy (15 minutes)
**Last Updated:** December 3, 2025

Complete guide to migrating from deprecated `ASSISTANT`/`OK ASK` commands to the new `MAKE DO` system.

---

## 🚨 Why Migrate?

The `ASSISTANT` and `OK ASK` commands are **deprecated** as of v1.2.0 and will be removed in v1.3.0.

### Benefits of MAKE DO

✅ **90%+ queries answered offline** (completely free)
✅ **Cost tracking and rate limiting** (predictable API costs)
✅ **Better knowledge bank integration** (166+ survival guides)
✅ **Confidence-based fallback** (smart online/offline switching)
✅ **Generation history** (REDO last query with modifications)
✅ **API monitoring** (budgets, alerts, statistics)
✅ **Workflow variables** (control via $MAKE.*, $API.*, $PROMPT.*)

### What You Lose

❌ None - `MAKE DO` is a superset of ASSISTANT functionality

---

## 📝 Command Mapping

### Basic Query

**Old:**
```upy
ASSISTANT ASK how do I purify water?
OK ASK what's the best fire starting method?
```

**New:**
```upy
MAKE DO how do I purify water?
MAKE DO what's the best fire starting method?
```

**Result:** Same answer, but 90%+ chance it's offline (free)

---

### Follow-Up Questions

**Old:**
```upy
ASSISTANT ASK how do I build a shelter?
ASSISTANT ASK what about in the desert?
```

**New:**
```upy
MAKE DO how do I build a shelter?
MAKE REDO in the desert
```

**Result:** REDO reuses context, faster than new query

---

### Clearing History

**Old:**
```upy
OK CLEAR
```

**New:**
```upy
MAKE CLEAR
```

---

### Status/Statistics

**Old:**
```upy
OK STATUS
```

**New:**
```upy
MAKE STATUS
```

**Result:** Much more detailed stats (offline/online split, costs, rate limits)

---

## 🔧 Advanced Features

### Force Offline Mode

**New capability** - Guarantee free answer (no API calls):

```upy
MAKE DO --mode offline water purification methods
```

**Use Case:** Cost-sensitive environments, offline operation

---

### Force Online Mode

**New capability** - Force Gemini even if offline available:

```upy
MAKE DO --mode online detailed analysis of water chemistry
```

**Use Case:** Need maximum accuracy for complex questions

---

### Retry with Modifications

**New capability** - Refine answers without retyping:

```upy
MAKE DO fire starting methods
MAKE REDO without matches or lighters
MAKE REDO in wet conditions
```

**Use Case:** Iterative refinement, exploring variations

---

## 🎯 Workflow Variables

**New in v1.2.0** - Control generation behavior via variables:

### PROMPT.* Variables (Control AI Behavior)

```upy
# Set custom system prompt
SET PROMPT.SYSTEM "You are a wilderness survival expert with 20 years experience"
MAKE DO water sources in desert

# Set response tone
SET PROMPT.TONE technical
MAKE DO water filtration physics

# Set detail level
SET PROMPT.COMPLEXITY simple
MAKE DO how to start fire
```

### MAKE.* Variables (Control Generation Mode)

```upy
# Force offline-only mode
SET MAKE.MODE offline
MAKE DO fire starting

# Set priority for rate limiting
SET MAKE.PRIORITY high
MAKE DO emergency water purification

# Set response style
SET MAKE.STYLE concise
MAKE DO shelter types
```

### API.* Variables (Monitor Costs)

```upy
# Check budget before expensive query
GET API.BUDGET_REMAINING
# Output: 0.9988

# Conditional generation based on budget
IF $API.BUDGET_PERCENT < 80 THEN
  MAKE DO complex multi-part query
ELSE
  MAKE DO --mode offline simple query
ENDIF

# Monitor service availability
IF $API.GEMINI_AVAILABLE THEN
  MAKE DO detailed analysis
ELSE
  MAKE DO --mode offline basic answer
ENDIF
```

---

## 📊 Comparison Table

| Feature | ASSISTANT/OK ASK | MAKE DO | Notes |
|---------|------------------|-------------|-------|
| **Basic Q&A** | ✅ | ✅ | Same functionality |
| **Offline-first** | ❌ | ✅ | 90%+ free answers |
| **Cost tracking** | ❌ | ✅ | Per-request costs |
| **Rate limiting** | ❌ | ✅ | Prevents overuse |
| **Budget enforcement** | ❌ | ✅ | $1/day default |
| **Generation history** | ❌ | ✅ | Last 100 queries |
| **REDO command** | ❌ | ✅ | Retry with mods |
| **Mode control** | ❌ | ✅ | offline/online/auto |
| **Workflow variables** | ❌ | ✅ | 28 variables |
| **API monitoring** | ❌ | ✅ | Live stats |
| **Knowledge bank** | ⚠️ Limited | ✅ | Full integration |
| **Confidence scoring** | ❌ | ✅ | Shows reliability |
| **Source attribution** | ❌ | ✅ | Cites guides |

---

## 🚀 Migration Steps

### Step 1: Update Scripts (2 minutes)

**Find and replace in your .upy scripts:**

```bash
# In terminal (from uDOS root)
find memory/ -name "*.upy" -exec sed -i '' 's/ASSISTANT ASK/MAKE DO/g' {} \;
find memory/ -name "*.upy" -exec sed -i '' 's/OK ASK/MAKE DO/g' {} \;
find memory/ -name "*.upy" -exec sed -i '' 's/OK CLEAR/MAKE CLEAR/g' {} \;
find memory/ -name "*.upy" -exec sed -i '' 's/OK STATUS/MAKE STATUS/g' {} \;
```

**Or manually:** Search your scripts for `ASSISTANT` and `OK ASK`, replace with `MAKE DO`

---

### Step 2: Test Key Workflows (5 minutes)

Test your most-used workflows to verify they work:

```upy
# Test basic query
MAKE DO water purification

# Test with workflow
RUN memory/workflows/missions/knowledge-expansion.upy

# Check statistics
MAKE STATUS
```

---

### Step 3: Configure API Monitoring (Optional, 5 minutes)

Set your preferred budget limits:

```upy
# Set daily budget (default: $1.00)
CONFIG api_budget_daily 0.50

# Set hourly budget (default: $0.10)
CONFIG api_budget_hourly 0.05

# Set rate limit (default: 2 req/sec)
CONFIG api_rate_limit 1.0
```

---

### Step 4: Optimize for Offline (Optional, 3 minutes)

Force offline mode for cost-sensitive workflows:

```upy
# In your workflow script
SET MAKE.MODE offline

# All subsequent MAKE DO commands will be offline-only
MAKE DO fire methods
MAKE DO water sources
MAKE DO shelter types
```

---

## ⚠️ Breaking Changes

### Removed Features

1. **OK DEV** - Removed (was GitHub Copilot CLI, unrelated to AI generation)
   - **Migration:** Use GitHub Copilot Chat directly in VS Code

2. **ASSISTANT HISTORY** - Replaced by `MAKE STATUS`
   - **Migration:** Use `MAKE STATUS` for detailed history/stats

### Changed Behavior

1. **Default is offline-first** (was online-only)
   - **Impact:** Faster responses, zero cost for 90%+ queries
   - **Fix:** None needed, better behavior

2. **Confidence thresholds** (new feature)
   - **Impact:** Low-confidence offline answers may fall back to Gemini
   - **Fix:** Set `MAKE.MODE offline` to prevent fallback

---

## 🧪 Testing Checklist

After migrating, verify these scenarios work:

- [ ] Basic query: `MAKE DO how do I purify water?`
- [ ] Retry query: `MAKE REDO in emergency situations`
- [ ] Status check: `MAKE STATUS`
- [ ] History clear: `MAKE CLEAR`
- [ ] Offline mode: `MAKE DO --mode offline fire starting`
- [ ] Workflow integration: `RUN memory/workflows/missions/test.upy`
- [ ] Variable access: `GET MAKE.TOTAL_REQUESTS`
- [ ] Budget check: `GET API.BUDGET_REMAINING`

---

## 💡 Best Practices

### 1. Start with Offline

Default to offline mode in workflows:

```upy
# At start of workflow
SET MAKE.MODE offline

# Your queries here (all offline)
MAKE DO query 1
MAKE DO query 2
```

### 2. Use REDO for Refinement

Instead of repeating queries, refine with REDO:

```upy
# First query
MAKE DO water purification methods

# Refine (reuses context, faster)
MAKE REDO using only natural materials
MAKE REDO in tropical environments
```

### 3. Monitor Budget

Check budget before expensive operations:

```upy
# Check before batch generation
GET API.BUDGET_REMAINING

# Conditional based on budget
IF $API.BUDGET_PERCENT < 50 THEN
  # Proceed with online queries
  MAKE DO complex analysis
ELSE
  # Use offline fallback
  LOG "Budget low, using offline mode"
  SET MAKE.MODE offline
ENDIF
```

### 4. Set Prompts Once

Configure prompts at workflow start:

```upy
# Configure once
SET PROMPT.SYSTEM "Expert wilderness survival instructor"
SET PROMPT.TONE professional
SET PROMPT.COMPLEXITY detailed

# All queries inherit settings
MAKE DO query 1
MAKE DO query 2
```

---

## 📚 Additional Resources

- [MAKE Command Reference](Command-Reference.md#generate)
- [Workflow Variables Guide](Workflows.md#variables)
- [API Monitoring Guide](API-Monitoring.md)
- [v1.2.0 Design Document](../dev/roadmap/v1.2.0-generate-consolidation.md)

---

## 🆘 Troubleshooting

### "Command not found: MAKE DO"

**Cause:** Using older version (< v1.2.0)
**Fix:** Update to v1.2.0 or later

### "Offline confidence too low"

**Cause:** Query not in knowledge bank, Gemini not configured
**Fix:**
1. Rephrase query with more specific keywords
2. Or configure Gemini: Add `GEMINI_API_KEY` to `.env`

### "Rate limit exceeded"

**Cause:** Too many API requests per second
**Fix:**
1. Wait 1 second
2. Or set `MAKE.MODE offline`
3. Or increase rate limit: `CONFIG api_rate_limit 5.0`

### "Budget limit exceeded"

**Cause:** Daily/hourly API budget spent
**Fix:**
1. Use offline mode: `MAKE DO --mode offline`
2. Or increase budget: `CONFIG api_budget_daily 2.0`
3. Or wait for next period

---

## 📞 Support

Having issues with migration?

1. **Check logs:** `memory/logs/dev.log`
2. **Test setup:** `MAKE STATUS`
3. **Report bug:** [GitHub Issues](https://github.com/fredporter/uDOS/issues)

---

**Last Updated:** December 3, 2025 (v1.2.0)
