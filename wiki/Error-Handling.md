# Error Handling System

**Version:** v1.2.22  
**Status:** Production Ready

The Error Handling System provides intelligent error capture, pattern learning, and AI-powered fix suggestions with complete privacy protection.

## Overview

uDOS v1.2.22 introduces a comprehensive error handling system with three main components:

1. **Error Interceptor** - Captures errors with full context
2. **Pattern Learner** - Learns from errors locally (no cloud sync)
3. **OK FIX** - AI-powered fix suggestions using learned patterns

## Privacy First

🔒 **All data stays local:**
- No telemetry or cloud sync
- Usernames sanitized to `<USER>`
- Absolute paths sanitized (e.g., `/Users/john/` → `<USER>/`)
- API keys (20+ chars) sanitized to `<KEY>`
- Emails sanitized to `<EMAIL>`
- IP addresses sanitized to `<IP>`

You can inspect or delete patterns anytime via `PATTERNS STATUS` and `PATTERNS CLEAR`.

## Commands

### OK FIX - Intelligent Error Resolution

Get AI-powered fix suggestions for errors:

```bash
# Fix latest error
OK FIX

# Fix specific error by signature
OK FIX #39a383e5

# Show OK assistant status
OK STATUS
```

**Example Output:**
```
╔══════════════════════════════════════════════════════════╗
║               OK FIX - Error Analysis                    ║
╚══════════════════════════════════════════════════════════╝

🔍 Error: ImportError
   Message: No module named 'foo'
   Signature: #39a383e5bd5cb580
   Timestamp: 2025-12-12 14:30:45

📚 Learned Fixes (from previous occurrences):
   1. pip install foo (✅ 85% success rate)
   2. Check requirements.txt
   3. Verify virtual environment is activated

🤖 AI Analysis (via Gemini)...

Root Cause:
The module 'foo' is not installed in your Python environment.

Fix Steps:
1. Activate virtual environment: source .venv/bin/activate
2. Install package: pip install foo
3. Verify: python -c "import foo"

Prevention:
Add 'foo' to requirements.txt to prevent future issues.

Next Steps:
  • Try suggested fix and use: OK FIX WORKED (or FAILED)
  • View full error: ERROR SHOW #39a383e5
  • Enter debug mode: DEV MODE
```

### PATTERNS - Pattern Management

Manage learned error patterns:

```bash
# Show statistics
PATTERNS STATUS

# Export patterns to JSON
PATTERNS EXPORT [filename]

# Clear all patterns (requires confirmation)
PATTERNS CLEAR
```

**PATTERNS STATUS Output:**
```
📚 Error Pattern Learning Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Patterns: 15
Total Occurrences: 47
Patterns with Fixes: 12
Average Success Rate: 78.3%

🔒 Privacy:
  • All data stored locally only
  • Usernames, paths, and keys are sanitized
  • No telemetry or cloud sync
  • Data location: memory/bank/system/error_patterns.json

Recent Patterns:
  • ImportError (#39a383e5): 8x, 3 fixes
  • FileNotFoundError (#5a2b1c4d): 5x, 2 fixes
  • ValueError (#7f3e8a9b): 12x, 5 fixes
  • KeyError (#2d6c9e1f): 4x, 1 fix
  • AttributeError (#8b4f7a3c): 18x, 1 fix

Commands:
  • PATTERNS CLEAR - Clear all patterns
  • PATTERNS EXPORT - Export to JSON
  • OK FIX - Get fix suggestions for errors
```

### ERROR - Error Context Management

View and manage error history:

```bash
# Show recent errors
ERROR HISTORY

# Show full error details
ERROR SHOW #<signature>

# Clear error history (requires confirmation)
ERROR CLEAR
```

**ERROR HISTORY Output:**
```
🔍 Recent Error History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 🟡 ImportError (#39a383e5)
   No module named 'foo'...
   Time: 2025-12-12 14:30:45

2. 🟢 FileNotFoundError (#5a2b1c4d)
   [Errno 2] No such file or directory: 'data.json'...
   Time: 2025-12-12 14:25:12

3. 🔴 ValueError (#7f3e8a9b)
   invalid literal for int() with base 10: 'abc'...
   Time: 2025-12-12 14:20:33

Commands:
  • ERROR SHOW #<signature> - View full error details
  • OK FIX #<signature> - Get fix suggestions
  • ERROR CLEAR - Clear error history
```

**Severity Indicators:**
- 🟢 LOW - Minor issues, informational
- 🟡 MEDIUM - Warnings, should be addressed
- 🔴 HIGH - Errors, need attention
- 🔴 CRITICAL - Severe errors, immediate action required

## Architecture

### Error Interceptor

Wraps command execution with intelligent error handling:

```python
from core.services.error_interceptor import ErrorInterceptor

interceptor = ErrorInterceptor(config)

# Wrap command execution
result, error = interceptor.intercept(command_func, *args, **kwargs)

if error:
    # Show theme-aware prompt:
    # 1. Retry
    # 2. Get OK Help (AI-powered fix)
    # 3. Enter DEV MODE
    # 4. Continue
    action = interceptor.prompt_user(error_context)
```

### Error Context

Captured for every error:

- Error type (ImportError, FileNotFoundError, etc.)
- Error message
- Stack trace (sanitized)
- Command that triggered the error
- Timestamp
- Environment (theme, location, git status)
- Severity level (LOW, MEDIUM, HIGH, CRITICAL)
- Unique signature (SHA256 hash of sanitized error)

### Pattern Learner

Learns from errors with privacy protection:

```python
from core.services.pattern_learner import get_pattern_learner

learner = get_pattern_learner()

# Record error
signature = learner.record_error(
    error_type="ImportError",
    error_text="No module named 'foo'"
)

# Get suggestions
suggestions = learner.suggest_fix(
    error_type="ImportError",
    error_text="No module named 'foo'"
)
# Returns: ["pip install foo", "Check requirements.txt"]

# Record fix result
learner.record_fix_result(
    signature=signature,
    success=True,
    fix_description="pip install foo"
)
# Updates success rate with exponential moving average
```

### Storage

**Error Contexts:** `memory/logs/error_contexts/`
- Filename format: `YYYYMMDD_HHMMSS_{signature}.json`
- Retention: 7-day rolling + 20 critical/high + 5 per signature
- Monthly archives: Gzipped to `memory/logs/error_contexts/archives/`

**Error Patterns:** `memory/bank/system/error_patterns.json`
- LOCAL ONLY - never transmitted
- Privacy-sanitized data only
- User can inspect/delete anytime

## Workflow Integration

### Automatic Recording

Errors are automatically recorded when:
1. Command execution fails
2. uPY script throws exception
3. System detects critical state

No manual intervention required.

### Fix Learning

When you successfully fix an error:
1. System records the fix
2. Updates success rate (exponential moving average)
3. Prioritizes proven fixes in future suggestions

### AI Integration

OK FIX uses Gemini AI (if available) for:
- Root cause analysis
- Step-by-step fix instructions
- Prevention tips

**Graceful Degradation:**
- Without Gemini API key: Shows learned patterns only
- With Gemini: Combines learned patterns + AI analysis

## Configuration

Set Gemini API key in `.env`:

```bash
GEMINI_API_KEY=your_api_key_here
```

Configure OK assistant settings via:
```bash
CONFIG
# Navigate to [OK] tab
```

## Best Practices

### 1. Review Patterns Regularly

```bash
PATTERNS STATUS
```

Check your error patterns monthly to identify recurring issues.

### 2. Export for Backup

```bash
PATTERNS EXPORT my-patterns.json
```

Keep backups of learned patterns (stored in `memory/docs/`).

### 3. Clear Old Patterns

```bash
PATTERNS CLEAR
```

Clear patterns when switching projects or after major refactoring.

### 4. Use Signatures

```bash
ERROR HISTORY
OK FIX #39a383e5
```

Reference specific errors by their signature for targeted help.

### 5. Record Successes

After fixing an error manually, document it:
- The system will learn from successful fixes
- Helps build better suggestions for similar errors

## Privacy Guarantees

✅ **What's Sanitized:**
- Usernames in paths
- Absolute file paths
- API keys and tokens (20+ characters)
- Email addresses
- IP addresses

✅ **What's Stored:**
- Error type (e.g., "ImportError")
- Sanitized error message
- Sanitized stack trace
- Fix descriptions (user-provided)
- Success rates (numeric)
- Timestamps

❌ **What's NEVER Stored:**
- Your username
- File contents
- API keys or passwords
- Personal information
- Telemetry data

❌ **What's NEVER Transmitted:**
- Error patterns (local only)
- Error contexts (local only)
- Fix history (local only)

**Only Gemini API calls send data** (if you use OK FIX with Gemini), and only sanitized error info is sent.

## Troubleshooting

### "No recent errors found"

You need an error to occur first:
1. Run a command that fails
2. Then use `OK FIX`

### "Gemini API not available"

Set your API key:
```bash
echo "GEMINI_API_KEY=your_key" >> .env
```

Or use OK FIX without Gemini (shows learned patterns only).

### "Pattern file contains sensitive data"

This shouldn't happen. If it does:
1. Run `PATTERNS CLEAR` to delete patterns
2. Report the issue via GitHub
3. Check sanitization in `core/services/pattern_learner.py`

### Clear specific error

```bash
# View recent errors
ERROR HISTORY

# Clear all errors (use with caution)
ERROR CLEAR
```

## Technical Details

### Signature Generation

Errors are identified by SHA256 hash:

```python
signature = hashlib.sha256(
    f"{error_type}:{sanitized_message}:{sanitized_stack}"
    .encode('utf-8')
).hexdigest()[:16]  # First 16 chars
```

This creates consistent identifiers for similar errors.

### Success Rate Calculation

Uses exponential moving average:

```python
alpha = 0.3  # Weight for new observations
new_rate = alpha * (1.0 if success else 0.0) + (1 - alpha) * old_rate
```

Recent fixes have more influence than old ones.

### Fuzzy Matching

Suggests fixes for similar errors using word overlap:

```python
similarity = len(words1 & words2) / len(words1 | words2)
threshold = 0.3  # 30% similarity minimum
```

## See Also

- [Role Management](Role-Management.md) - Permission levels for error handling
- [DEV MODE Guide](DEV-MODE-GUIDE.md) - Advanced debugging
- [OK Assistant Guide](OK-Assistant-Guide.md) - AI-powered assistance
- [Architecture](Architecture.md) - System design overview

## Version History

- **v1.2.22** (Dec 2025) - Initial release with full privacy protection
  - Error interceptor middleware
  - Pattern learning system
  - OK FIX command
  - PATTERNS and ERROR commands
  - Integration tests passing (6/6 ✅)
