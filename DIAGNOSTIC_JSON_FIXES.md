#!/usr/bin/env python3
"""
Diagnostic report for Wizard + Ollama + Noun Project SSE JSON fixes
=====================================================================

ISSUES FOUND AND FIXED:
"""

fixes = """
1. ❌ ISSUE: json.dumps() not used in SSE routes
   └─ CAUSE: Manual string formatting with backslash escaping
   └─ IMPACT: Strings with quotes/newlines broken JSON parsing
   └─ FILES: wizard/routes/self_heal_routes.py

   FIXED ROUTES:
   ✅ /ollama/pull (lines 220-275)
      - Now uses: json.dumps({'progress': progress, 'status': status, 'message': text})
      - Properly escapes: quotes, newlines, unicode

   ✅ /ok-setup (lines 374-430)
      - Now uses: json.dumps({'progress': p, 'status': s, 'message': m})
      - Removed unused import: "import json as json_lib"
      - Final summary uses json.dumps()

   ✅ /nounproject/seed (lines 438-540)
      - Now uses: json.dumps({'progress': p, 'status': s, 'message': m})
      - Removed unused import: "import json as json_lib"
      - Final summary uses json.dumps()

2. ❌ ISSUE: Mixed json/json_lib imports
   └─ CAUSE: Some routes imported "json as json_lib" but used json.dumps() without alias
   └─ IMPACT: NameError on json_lib.dumps() calls

   FIXED:
   ✅ ok-setup: Removed "import json as json_lib"
      - Uses top-level json module (line 10)
   ✅ nounproject/seed: Removed "import json as json_lib"
      - Uses top-level json module (line 10)

3. ✅ VERIFIED: Dashboard SSE parsing is correct
   └─ Location: wizard/dashboard/src/routes/Config.svelte (lines 300-380)
   └─ Logic: Extracts JSON after "data: " prefix
   └─ Handles: parse errors gracefully with console.warn()

TEST: JSON Format Compliance
=============================
The fix ensures all SSE messages follow this format:

  data: {"progress": 0, "status": "starting", "message": "..."}
  <empty line>

Each field is properly escaped by json.dumps(), which:
  ✅ Escapes quotes: " → \"
  ✅ Escapes newlines: \n → \\n
  ✅ Escapes backslashes: \\ → \\\\
  ✅ Escapes unicode: properly encoded as \\uXXXX

ROOT CAUSE ANALYSIS:
====================

Error: "JSON.parse: unexpected end of data at line 1 column 1"

This error occurs when JSON.parse() receives:
  1. Empty string ("")
  2. Malformed JSON ("data: " without JSON)
  3. Unescaped special characters in strings

BEFORE FIX:
-----------
yield f"data: {{\"progress\": {progress}, \"message\": \"{line_text}\"}}"
                                                          ^^^^^^^^^
                                                   No escaping!
If line_text = 'error: "timeout"', this produces:
  data: {"progress": 50, "message": "error: "timeout""}
                                                    ^^ breaks JSON!

AFTER FIX:
----------
yield f"data: {json.dumps({'progress': progress, 'message': line_text})}"
json.dumps() automatically escapes all strings:
  data: {"progress": 50, "message": "error: \\"timeout\\""}
                                                    ^^^^ valid!

DEPLOYMENT STEPS:
=================

1. ✅ File Changes: wizard/routes/self_heal_routes.py
   - All three SSE routes now use json.dumps()
   - All imports are consistent
   - No syntax errors

2. 📋 NEXT: Restart Wizard server
   - Kill old process: pkill -f "wizard.server"
   - Start new process: python -m wizard.server --port 9XXX

3. 📋 NEXT: Test in Dashboard
   - Open Dashboard at http://localhost:9XXX
   - Click "INSTALL VIBE"
   - Verify progress updates correctly
   - No JSON.parse errors in console
   - Check completion message shows

4. 📋 NEXT: Test Noun Project seeding (if credentials available)
   - Click "SEED ICONS"
   - Verify streaming messages appear
   - No JSON.parse errors

5. 📋 NEXT: Test Ollama pull (if installed)
   - Click "PULL MODEL"
   - Verify progress bar updates
   - No JSON.parse errors

VERIFICATION CHECKLIST:
=======================
□ Wizard server started without errors
□ Dashboard connects to server
□ INSTALL VIBE starts and shows progress
□ Progress bar updates in real-time
□ Completion message displays correctly
□ No JSON.parse errors in browser console
□ Noun Project seeding works (if available)
□ Ollama model pull works (if available)

FILES MODIFIED:
===============
1. wizard/routes/self_heal_routes.py (3 routes fixed)
   - Removed 2 unused json imports
   - Updated all SSE yields to use json.dumps()
   - Fixed total errors: 5

2. wizard/dashboard/src/routes/Config.svelte
   - Already configured to parse json.dumps() output
   - No changes needed in this session

REFERENCES:
===========
- JSON SSE Format: https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events
- Server-Sent Events: Each message is "data: <JSON>\\n\\n"
- json.dumps() handles all escaping automatically
"""

print(fixes)
