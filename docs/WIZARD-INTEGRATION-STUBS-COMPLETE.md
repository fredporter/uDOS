# Wizard Integration Handler Stubs - Complete ✅

**Date:** 2026-01-18  
**Status:** Ready for Phase 6 implementation  
**Files Created:** 4 stub handler files

---

## Summary

Created comprehensive stub handler modules for Wizard-owned external integrations. All stubs include:

- ✅ Dataclass schemas for request/response objects
- ✅ Async method signatures with TODO placeholders
- ✅ Docstrings with implementation guidance
- ✅ Security annotations (Wizard-only, never Core/App)
- ✅ SQLite sync capabilities for metadata

---

## Handler Stubs Created

### 1. HubSpot Handler (`wizard/services/hubspot_handler.py`)

**Purpose:** CRM contact management, deduplication, enrichment

**Key Methods:**

- `authenticate()` - API key validation
- `list_contacts()` / `get_contact()` / `create_contact()` / `update_contact()`
- `deduplicate_contacts()` - Find/merge duplicates
- `enrich_contact()` - Data enrichment with external APIs
- `sync_to_sqlite()` - Export contacts to local database

**Configuration:** `wizard/config/ai_keys.json` (api_key)  
**Scope:** Wizard-only (never Core/App)

---

### 2. Notion Handler (`wizard/services/notion_handler.py`)

**Purpose:** Notion API sync, bidirectional updates, conflict resolution

**Key Methods:**

- `authenticate()` - OAuth + API key validation
- `get_page()` / `list_pages()` / `get_blocks()`
- `create_block()` / `update_block()`
- `handle_webhook()` - Incoming Notion changes
- `sync_to_sqlite()` / `push_to_notion()` - Bidirectional
- `detect_conflicts()` - Conflict detection & resolution

**Configuration:** `wizard/config/ai_keys.json` (api_key, webhook_secret)  
**Scope:** Wizard-only (never Core/App)

---

### 3. iCloud Handler (`wizard/services/icloud_handler.py`)

**Purpose:** iCloud backups, device continuity, keychain sync

**Key Methods:**

- `authenticate()` - Apple ID + secure password
- `list_devices()` / `register_device()`
- `list_backups()` / `get_backup()` / `download_backup()`
- `relay_backup_to_device()` - Send backup to connected device
- `enable_continuity()` - Cross-device continuity
- `sync_keychain_to_device()` - Secure keychain sync
- `sync_to_sqlite()` - Backup metadata sync

**Configuration:** `wizard/config/icloud.json` (username, api_key, secure password)  
**Scope:** Wizard-only (never Core/App)

---

### 4. OAuth Handler (`wizard/services/oauth_handler.py`)

**Purpose:** OAuth2 flows, token storage, scoped device access

**Key Methods:**

- `start_auth_flow()` - Generate auth URL
- `handle_callback()` - Exchange code for tokens
- `refresh_token()` - Refresh expired tokens
- `get_device_token()` - Retrieve token for device
- `revoke_token()` - Revoke device access
- `list_authorized_providers()` - List device authorizations
- `request_scoped_token()` - Generate short-lived scoped tokens
- `sync_to_sqlite()` - Export OAuth metadata (no tokens)

**Configuration:** `wizard/config/oauth_providers.json` (provider configs)  
**Scope:** Wizard-only (never Core/App); tokens never sent to device

**Supported Providers:**

- Google, Microsoft, GitHub, Notion, HubSpot, Slack, Apple

---

## Config Updates

### `wizard/config/wizard.json`

Added feature flags for new integrations:

```json
{
  "gmail_relay_enabled": true,
  "ai_gateway_enabled": true,
  "oauth_enabled": false,
  "hubspot_enabled": false,
  "notion_enabled": false,
  "icloud_enabled": false
}
```

---

## Implementation Roadmap (Phase 6+)

### Phase 6A: Core OAuth (2-3 weeks)

- [ ] Implement `OAuthHandler.start_auth_flow()` with PKCE flow
- [ ] Implement `OAuthHandler.handle_callback()` with token exchange
- [ ] Implement `OAuthHandler.refresh_token()`
- [ ] Create `oauth_handler_test.py` (15+ tests)
- [ ] Wire OAuth routes into `wizard/server.py`

### Phase 6B: HubSpot Integration (2 weeks)

- [ ] Implement `HubSpotHandler.authenticate()`
- [ ] Implement contact CRUD operations
- [ ] Implement `deduplicate_contacts()` with fuzzy matching
- [ ] Implement `enrich_contact()` with external APIs
- [ ] Create `hubspot_handler_test.py` (20+ tests)
- [ ] Wire HubSpot routes into `wizard/server.py`

### Phase 6C: Notion Integration (2 weeks)

- [ ] Implement `NotionHandler.authenticate()` (OAuth + API key)
- [ ] Implement page/block CRUD operations
- [ ] Implement `handle_webhook()` for incoming changes
- [ ] Implement bidirectional sync logic
- [ ] Implement conflict detection & resolution
- [ ] Create `notion_handler_test.py` (25+ tests)
- [ ] Wire Notion routes into `wizard/server.py`

### Phase 6D: iCloud Integration (2 weeks)

- [ ] Implement `iCloudHandler.authenticate()` with secure password storage
- [ ] Implement device management
- [ ] Implement backup operations
- [ ] Implement `relay_backup_to_device()` with encryption
- [ ] Implement keychain sync
- [ ] Create `icloud_handler_test.py` (20+ tests)
- [ ] Wire iCloud routes into `wizard/server.py`

---

## Next Steps

1. **Confirm Phase 6 Scope:** Is Phase 6 prioritizing Wizard integration implementation, or TUI features?
   - If **Wizard integration**: Proceed with Phase 6A (OAuth) → 6B-6D (services)
   - If **TUI features**: Defer handler implementation; focus on graphics/teletext prep

2. **If Proceeding with Phase 6A-6D:**
   - Start with OAuth (foundation for all other integrations)
   - Implement one handler per 2-week phase
   - Build comprehensive test suites alongside implementation
   - Wire into server.py routes as each handler completes
   - Test with real provider APIs (sandbox environments)

3. **Configuration Setup:**
   - Create `wizard/config/oauth_providers.template.json` (provider templates)
   - Create `wizard/config/icloud.json` template
   - Document secure credential storage (keyring integration)

4. **Documentation:**
   - Create `wizard/docs/INTEGRATION-HANDLER-GUIDE.md`
   - Add OAuth, HubSpot, Notion, iCloud setup guides
   - Document test procedures for each handler

---

## Security Notes

- **Wizard-only:** All handlers are Wizard-owned; never expose to Core/App
- **Token storage:** Tokens stored only in Wizard (never sent to device)
- **OAuth scopes:** Validate and enforce requested scopes
- **Rate limiting:** Apply to all external API calls
- **Encryption:** All credentials encrypted at rest

---

## Files Summary

| File            | Lines   | Status    |
| --------------- | ------- | --------- |
| HubSpot Handler | 154     | ✅ Stub   |
| Notion Handler  | 164     | ✅ Stub   |
| iCloud Handler  | 163     | ✅ Stub   |
| OAuth Handler   | 240     | ✅ Stub   |
| **Total**       | **721** | **Ready** |

---

**Ready for Phase 6 scope decision. Once confirmed, implementation can begin immediately.**

_Last Updated: 2026-01-18_
