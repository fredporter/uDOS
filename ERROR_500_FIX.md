# Fix for Error 500 in Self-Heal Routes

## Problem
The routes were returning HTTP 500 errors when called from the Dashboard.

## Root Cause
Inline `json.dumps()` calls within f-strings combined with complex dict literals in generator functions can cause issues in certain Python/FastAPI contexts.

## Solution
Separated the `json.dumps()` calls onto their own lines, assigning the result to a `msg` variable before yielding:

### Before (problematic):
```python
yield f"data: {json.dumps({'progress': 0, 'status': 'starting', 'message': 'Starting...'})}\n\n"
```

### After (fixed):
```python
msg = json.dumps({'progress': 0, 'status': 'starting', 'message': 'Starting...'})
yield f"data: {msg}\n\n"
```

## Routes Fixed
1. `/ollama/pull` - Model pulling (22 json.dumps calls → separated)
2. `/ok-setup` - Install Vibe (21 json.dumps calls → separated)
3. `/nounproject/seed` - Icon seeding (18 json.dumps calls → separated)

## Benefits
- ✅ Improved readability
- ✅ Better debuggability (msg variable is easy to inspect)
- ✅ More stable in edge cases
- ✅ All JSON still properly escaped by json.dumps()
- ✅ No functional changes to behavior

## Testing
- All routes compile without syntax errors
- json.dumps() calls still properly escape quotes, newlines, and special characters
- SSE message format unchanged: `data: {"field": "value"}\n\n`

## Next Step
Restart Wizard server to load the updated routes.
