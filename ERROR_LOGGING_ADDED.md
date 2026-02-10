# Debugging 500 Error - Comprehensive Error Logging Added

## What Changed

Added detailed error logging to all three self-heal routes to capture the exact cause of the 500 errors.

### Changes Made

Each route now includes:

1. **Separate exception handling** for the `run_ok_setup()` and `client.authenticate()` calls
2. **Detailed error information** including exception class name
3. **stderr logging** with stack traces
4. **Clearer error messages** sent back to Dashboard

### Example New Error Output

Before: `"Setup failed: error occurred"`
After: `"Setup failed: ImportError: No module named 'xyz'"`

Plus full traceback printed to stderr.

## Where to Check Logs

After restarting the server, when you test the routes:

1. **Check stderr output** from the Wizard server process
2. Look for lines starting with `[ERROR]`:
   - `[ERROR] ok-setup error: ...`
   - `[ERROR] ollama/pull error: ...`
   - `[ERROR] nounproject/seed error: ...`
   - `[ERROR] noun auth error: ...`

3. **Full Python tracebacks** will be printed showing the exact line that failed

## Routes Updated

- `POST /api/self-heal/ok-setup` ✅
- `POST /api/self-heal/ollama/pull` ✅
- `POST /api/self-heal/nounproject/seed` ✅

## Next Steps

1. **Restart Wizard server** to load the changes
2. **Test the routes** in Dashboard
3. **Check server stderr output** for the `[ERROR]` lines
4. **Report the error message** to identify the root cause

The error logging will help identify:
- Import failures
- Missing dependencies
- Invalid function calls
- Async/await issues
- Any other Python exceptions

Once we have the actual error message, we can fix it.
