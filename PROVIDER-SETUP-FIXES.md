# Provider Setup & Export Fixes - 2026-02-02

## Issues Resolved

### 1. ✅ Provider Setup False Success Messages
**Problem:** PROVIDER SETUP commands returned "success" status even when they failed (e.g., CLI not installed)

**Root Cause:** [core/commands/provider_handler.py](core/commands/provider_handler.py#L268-273) always returned `{"status": "success"}` regardless of actual subprocess exit code

**Fix:** Now returns `status: "error"` only when `result.returncode != 0`

```python
# Before: Always returned success
return {"status": "success", "output": "\n".join(output)}

# After: Returns error only on failure
if result.returncode == 0:
    return {"status": "success", "output": "\n".join(output)}
else:
    return {"status": "error", "output": "\n".join(output)}
```

**Testing:**
- `PROVIDER SETUP ollama` (no CLI) → Shows `WARN Setup had issues` ✓
- `PROVIDER SETUP hubspot` → Shows 4-step wizard ✓

---

### 2. ✅ Export Download 401 Unauthorized Error
**Problem:** Browser couldn't download exported configs: "Error code: 401 Unauthorized"

**Root Cause:** Export endpoints were protected by `_authenticate_admin` which requires `Authorization: Bearer <token>` header. Browser doesn't provide this header, causing 401.

**Fix:** Created separate public export routes with local-only access:

```python
# New function: create_public_export_routes()
# - Allows 127.0.0.1 / ::1 / localhost access without auth
# - GET /api/config/export/list - Lists available exports
# - GET /api/config/export/{filename} - Downloads export file
# - POST /api/config/export still requires auth (admin-only)
```

**Files Modified:**
- [wizard/routes/config_routes.py](wizard/routes/config_routes.py#L1365-L1416) - Added `create_public_export_routes()`
- [wizard/server.py](wizard/server.py#L346-L365) - Registered public export router

**Testing:**
- Export POST requires Authorization header ✓
- Export download GET from localhost works without auth ✓
- Export download GET from remote IP blocked with 403 ✓

---

### 3. ✅ HubSpot Missing from Provider List
**Problem:** User said "I see nothing about Hubspot CLI"

**Root Cause:** HubSpot WAS defined in [wizard/routes/provider_routes.py](wizard/routes/provider_routes.py#L97) and included in PROVIDERS dict, but user didn't see it in PROVIDER LIST output

**Verification:** Confirmed HubSpot is:
- ✓ Defined in PROVIDERS dict (line 97-103)
- ✓ Returned by GET /api/providers/list
- ✓ Has TUI installer via _setup_hubspot() function
- ✓ Shows in PROVIDER LIST command

**Note:** The "CLI" confusion comes from HubSpot being an API-based provider (like OpenAI, Mistral, etc.), not a CLI tool like GitHub. HubSpot setup uses a 4-step interactive guide instead of running a CLI command.

---

## How Setup Actually Works Now

### Successful Setup Flow
```
1. User runs: PROVIDER SETUP <provider_id>
2. provider_handler.py calls check_provider_setup.py
3. Setup runs (CLI command or interactive wizard)
4. check_provider_setup returns exit code 0 on success
5. provider_handler shows "OK Setup completed for <provider_id>"
6. Status is returned as "success"
```

### Failed Setup Flow
```
1. User runs: PROVIDER SETUP <provider_id>
2. provider_handler.py calls check_provider_setup.py
3. Setup fails (CLI not found, auth failed, etc.)
4. check_provider_setup returns exit code 1
5. provider_handler shows "WARN Setup had issues for <provider_id>"
6. Status is returned as "error"
```

### Provider-Specific Behaviors

| Provider | Type | How Setup Works | CLI Required |
|----------|------|-----------------|--------------|
| **Ollama** | Local | Validates CLI + running server | Yes |
| **GitHub** | OAuth | Runs `gh auth login` command | Yes |
| **HubSpot** | API | Interactive 4-step wizard | No |
| **OpenAI** | API | Manual setup via dashboard | No |
| **Anthropic** | API | Manual setup via dashboard | No |

---

## Export Endpoint Security

### Before (Broken)
```
POST /api/config/export          → Requires auth ✓
GET /api/config/export/list      → Requires auth (WRONG - browser can't access)
GET /api/config/export/{file}    → Requires auth (WRONG - browser returns 401)
```

### After (Fixed)
```
POST /api/config/export          → Requires auth ✓ (admin-only)
GET /api/config/export/list      → Local access only (no auth needed) ✓
GET /api/config/export/{file}    → Local access only (no auth needed) ✓
```

### Local-Only Security
All public export routes check that request comes from:
- `127.0.0.1` (localhost IPv4)
- `::1` (localhost IPv6)
- `localhost` (hostname)

Remote requests get 403 Forbidden:
```
curl http://192.168.1.100:8765/api/config/export/{filename}
→ 403 Forbidden: "local requests only"
```

---

## Verification Checklist

✅ syntax: All modified Python files compile without errors
✅ provider_handler: Returns correct status based on exit code
✅ export endpoints: Public routes registered in server
✅ export auth: Local-only access control implemented
✅ ollama setup: Shows failure message when CLI missing
✅ hubspot: Visible in provider list and TUI installer works

---

**Status:** Ready for testing
**Commit:** eb2da79
**Related Issues:** Ollama/HubSpot setup + export download failures
