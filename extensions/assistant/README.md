# AI Assistant Extension

**Status:** Active (Deprecated)
**Version:** 1.0.0
**Category:** AI / Service
**Requires:** API Key (GEMINI_API_KEY)

---

## ⚠️ Deprecation Notice

**ASSISTANT commands are deprecated as of v1.2.0**

**Migration Path:**
- `ASSISTANT ASK <query>` → `GENERATE DO <query>`
- `OK ASK <query>` → `GENERATE DO <query>`

**Removal:** v2.0.0 (estimated Q2 2025)

See: [Migration Guide](../../wiki/Migration-Guide-Assistant-to-Generate.md)

---

## Overview

AI-powered assistance using Google Gemini API. Provides conversational AI, code analysis, command explanations, and debugging help.

**Note:** This is an **optional extension**. uDOS works fully offline without this extension using the built-in offline AI engine.

## Features

- **Conversational AI** - Ask questions, get answers
- **Code Analysis** - Analyze code for bugs and improvements
- **Command Explanations** - Explain uDOS/shell commands
- **Script Generation** - Generate .upy scripts from descriptions
- **Error Debugging** - Help debug error messages
- **Knowledge Integration** - Enhanced with local knowledge bank
- **Offline Fallback** - Falls back to offline AI if unavailable
- **Usage Tracking** - Monitor API usage and costs
- **Cost Monitoring** - Track spending and set budgets

## Installation

### 1. Install Dependencies

```bash
pip install google-generativeai
```

### 2. Get API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy the key

### 3. Configure uDOS

Add to `.env` file:

```bash
GEMINI_API_KEY=your_key_here
```

### 4. Test Installation

```
ASSISTANT STATUS
```

## Commands

### ASSISTANT ASK (Deprecated)

**Replacement:** `GENERATE DO`

Ask Gemini AI a question.

```
ASSISTANT ASK <question>
```

**Examples:**
```
ASSISTANT ASK how do I purify water?
ASSISTANT ASK what's the best shelter for desert?
ASSISTANT ASK explain grid system
```

**Migration:**
```
# Old (deprecated)
ASSISTANT ASK how do I purify water?

# New (v1.2.0+)
GENERATE DO how do I purify water?
```

### ASSISTANT CLEAR

Clear conversation history.

```
ASSISTANT CLEAR
```

### ASSISTANT STATUS

Show assistant status and usage statistics.

```
ASSISTANT STATUS
```

**Output:**
- Model version
- Uptime
- Total requests
- Token usage (input/output)
- Total cost
- Cost per request
- Conversation history size

## Configuration

### Default Settings

```json
{
  "model": "gemini-2.5-flash",
  "temperature": 0.7,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "conversation_history_limit": 100
}
```

### Rate Limiting

```json
{
  "requests_per_minute": 60,
  "requests_per_day": 1440
}
```

### Cost Tracking

```json
{
  "input_cost_per_million": 0.075,
  "output_cost_per_million": 0.30,
  "daily_budget_usd": 1.0,
  "warn_at_percent": 80
}
```

**Current Pricing (Dec 2024):**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens
- Average query: $0.0001 - $0.001

## Integration

### Offline AI Engine

The assistant integrates with uDOS's offline AI engine for hybrid intelligence:

1. **Offline First** - Tries local knowledge bank first
2. **Smart Fallback** - Uses Gemini if offline confidence < 50%
3. **Context Enhancement** - Provides knowledge bank results to Gemini
4. **Graceful Degradation** - Works without API key (offline only)

### Knowledge Bank

Automatically includes relevant knowledge bank context:

- Searches 166+ survival guides
- Provides top 3 results to Gemini
- Cites sources in responses
- Enhances accuracy for survival topics

### User Memory

Tracks user preferences and query history:

- Last 100 queries with timestamps
- Confidence scores
- Token usage per query
- Cost tracking

## Usage Examples

### Basic Question

```
ASSISTANT ASK how do I start a fire with wet wood?
```

**Output:**
```
🤖 Gemini AI:
📚 Enhanced with 2 knowledge bank items

To start a fire with wet wood:

1. Gather tinder - dry materials (bark, grass)
2. Split wet wood to expose dry interior
3. Build teepee structure with driest wood
4. Use feather sticks for better ignition
5. Gradually add larger pieces as fire grows

Key tips:
- Dead standing wood is drier than ground wood
- Birch bark ignites even when wet
- Maintain good airflow
- Have patience - wet wood takes 2-3x longer

Sources: knowledge/fire/starting.md, knowledge/fire/wet-conditions.md
```

### Code Analysis

```
ASSISTANT ASK analyze this Python function for bugs
```

### Command Explanation

```
ASSISTANT ASK what does CATALOG --tree do?
```

### Script Generation

```
ASSISTANT ASK generate a script that lists all water guides
```

## Troubleshooting

### "Gemini service not available"

**Cause:** No API key or invalid key

**Solution:**
1. Check `.env` has `GEMINI_API_KEY=...`
2. Verify key is valid at https://makersuite.google.com
3. Try: `ASSISTANT STATUS`

**Offline Alternative:**
```
GENERATE DO <your question>
```

### High Costs

**Monitor usage:**
```
ASSISTANT STATUS
```

**Reduce costs:**
1. Use `GENERATE DO` (offline-first, 90%+ queries free)
2. Clear history regularly: `ASSISTANT CLEAR`
3. Set daily budget in config

### Rate Limiting

**Error:** "Too many requests"

**Solution:**
1. Wait 1 minute
2. Check `requests_per_minute` config
3. Use offline AI for simple queries

## Migration to GENERATE

**Timeline:**
- v1.2.0 (Dec 2024): ASSISTANT deprecated, GENERATE introduced
- v1.3.0 (Q1 2025): Deprecation warnings shown
- v2.0.0 (Q2 2025): ASSISTANT commands removed

**Command Mapping:**

| Old Command | New Command | Notes |
|------------|-------------|-------|
| `ASSISTANT ASK <q>` | `GENERATE DO <q>` | Offline-first |
| `OK ASK <q>` | `GENERATE DO <q>` | Same behavior |
| `ASSISTANT CLEAR` | `GENERATE CLEAR` | Clears history |
| `ASSISTANT STATUS` | `GENERATE STATUS` | API usage |

**Migration Steps:**

1. **Update Scripts** - Replace ASSISTANT with GENERATE in .upy files
2. **Test Offline** - Verify GENERATE DO works without API key
3. **Update Documentation** - Update guides and workflows
4. **Remove Dependencies** - Uninstall google-generativeai if not needed

**Benefits of GENERATE:**
- ✅ Offline-first (90%+ queries free)
- ✅ Knowledge bank integration
- ✅ Unified command structure
- ✅ Smart API fallback
- ✅ Cost tracking and budgets
- ✅ Priority queue support

## API Reference

### GeminiService Class

```python
from extensions.assistant import get_gemini_service

# Get service instance
gemini = get_gemini_service(config_manager=config)

# Check availability
if gemini.is_available:
    # Ask question
    response = gemini.ask("how do I purify water?")

    # With context
    response = gemini.ask("explain this", context={
        'workspace': 'memory',
        'files': ['guide.md'],
        'local_knowledge': kb_results
    })

    # Get status
    status = gemini.get_status()

    # Clear history
    gemini.clear_history()
```

### AssistantHandler Class

```python
from extensions.assistant.handler import get_assistant_handler

# Get handler instance
handler = get_assistant_handler(config_manager=config)

# Handle command
result = handler.handle('ASSISTANT', ['ASK', 'how', 'do', 'I', 'purify', 'water?'])
```

## Security

- **API Key Storage:** Environment variable only (`.env`)
- **Audit Logging:** All requests logged
- **Usage Tracking:** Token and cost monitoring
- **Rate Limiting:** Built-in request throttling
- **Cost Alerts:** Warns at 80% of daily budget

## Performance

**Average Response Times:**
- Simple query: 500-1000ms
- Complex query: 1000-2000ms
- Code analysis: 1500-3000ms

**Token Usage:**
- Simple query: 100-500 tokens
- Complex query: 500-2000 tokens
- Code analysis: 1000-5000 tokens

**Cost Estimates:**
- Simple query: $0.0001 - $0.0003
- Complex query: $0.0003 - $0.001
- 100 queries/day: ~$0.05/day ($1.50/month)

## Support

**Documentation:**
- [Command Reference](../../wiki/Command-Reference.md)
- [Migration Guide](../../wiki/Migration-Guide-Assistant-to-Generate.md)
- [Troubleshooting](../../wiki/Troubleshooting-Complete.md)

**Issues:**
- GitHub: https://github.com/fredporter/uDOS/issues
- Deprecated features: Use GENERATE commands instead

---

**Version History:**

- **1.0.0** (Dec 2024) - Migrated from core to extensions
  - Moved from `core/commands/assistant_handler.py`
  - Added deprecation notices
  - Lazy loading for optional dependency
  - Graceful degradation without API key

**Previous versions:** See `extensions/core/ok_assistant/` (legacy)
