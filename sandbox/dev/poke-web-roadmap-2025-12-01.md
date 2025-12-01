# POKE WEB Roadmap - v2.1+

**Date**: December 1, 2025
**Status**: Planning / Design Phase
**Priority**: Medium (after core extension polish)

## Overview

POKE WEB is a planned feature for secure HTTP sharing of uDOS instances, files, and data between users or for remote self-access. It extends the existing POKE TUNNEL functionality to enable collaborative workflows while maintaining uDOS's offline-first philosophy and security requirements.

## Current State (v2.0)

### ✅ Implemented
- **POKE TUNNEL**: Fully functional ngrok/cloudflared integration
  - `POKE TUNNEL OPEN <port>` - Create secure tunnel to local port
  - `POKE TUNNEL CLOSE <id>` - Close tunnel
  - `POKE TUNNEL STATUS` - Show tunnel status
  - `POKE TUNNEL LIST` - List all tunnels
- **Service Shortcuts**: Convenience commands for core extensions
  - `POKE DASHBOARD`, `POKE DESKTOP`, `POKE TERMINAL`, `POKE TELETEXT`
  - `POKE START/STOP/RESTART/LIST/STATUS <service>`

### ⏳ Stub/Incomplete
- **POKE SHARE**: Command stubs exist but no HTTP servers implemented
  - `POKE SHARE FILE <path>` - Returns port number only
  - `POKE SHARE FOLDER <path>` - Returns port number only
  - No actual HTTP file server started
  - No tunnel integration
  - No authentication/authorization

- **POKE GROUP**: Completely unimplemented
  - All commands return "coming soon" message
  - No collaboration infrastructure

## Architecture Decisions

### Extension Scope
**POKE (extensions/cloud/)** is the **single point of access** for all cloud/internet connectivity:
- Tunneling (ngrok, cloudflared)
- Remote access to local services
- File/data sharing via HTTP
- Group collaboration
- Security logging and audit trails

**Why consolidate?**
1. **Security**: One extension to audit, harden, and monitor
2. **Offline-first protection**: Clear boundary between local and remote
3. **Configuration**: Single place for API keys, tokens, settings
4. **Logging**: Unified audit trail for all external access

### Core Extensions Stay Local
**extensions/core/** contains system-critical web interfaces:
- `dashboard/` - NES-themed system monitoring (port 5555)
- `desktop/` - System 7 desktop environment (port 8892)
- `terminal/` - Web terminal (port 8889)
- `teletext/` - Teletext interface (port 9002)
- `mission-control/` - Mission workflow dashboard (port 5000)

These are **localhost-only** by default. POKE TUNNEL can expose them externally when needed.

## v2.1 Roadmap - POKE SHARE Implementation

### Goal
Complete the `POKE SHARE FILE` and `POKE SHARE FOLDER` commands to enable secure HTTP sharing of files and directories.

### Features

#### 1. File Sharing
```bash
POKE SHARE FILE knowledge/water/purification.md --expires 24
```

**Output:**
```
✅ File shared successfully!

🔗 Local URL: http://localhost:8000/purification.md
🌐 Public URL: https://abc123.ngrok.io/purification.md
⏱  Expires: 24 hours (Dec 2, 2025 14:30 UTC)

Share ID: share-f7a3b2c1
Use: POKE SHARE STOP share-f7a3b2c1 to revoke
```

**Requirements:**
- Lightweight HTTP file server (Python `http.server` or Flask)
- Integration with POKE TUNNEL for public access
- Automatic cleanup on expiration
- Share ID tracking for revocation
- Optional password protection
- Content-type detection
- Range request support (for large files)

#### 2. Folder Sharing
```bash
POKE SHARE FOLDER knowledge/water/ --expires 48 --password mysecret
```

**Output:**
```
✅ Folder shared successfully!

🔗 Local URL: http://localhost:8001/
🌐 Public URL: https://xyz789.ngrok.io/
🔒 Password required: mysecret
⏱  Expires: 48 hours (Dec 3, 2025 14:30 UTC)

Share ID: share-d9e4f5a2
Use: POKE SHARE STOP share-d9e4f5a2 to revoke
```

**Requirements:**
- Directory listing with file browser UI
- Password authentication
- Recursive file access
- Download support (individual files or ZIP)
- Optional upload capability (--write flag)
- README.md rendering for documentation

#### 3. Share Management
```bash
POKE SHARE LIST
```

**Output:**
```
📤 ACTIVE SHARES (2)

ID: share-f7a3b2c1
  Type: file
  Path: knowledge/water/purification.md
  URL: https://abc123.ngrok.io/purification.md
  Expires: 23h 45m
  Access: Public
  Hits: 12

ID: share-d9e4f5a2
  Type: folder
  Path: knowledge/water/
  URL: https://xyz789.ngrok.io/
  Expires: 47h 30m
  Access: Password protected
  Hits: 3
```

**Requirements:**
- Active share tracking
- Access statistics (hit count, bandwidth)
- Expiration countdown
- Quick revocation

### Security Requirements

#### Authentication & Authorization
- [ ] Password protection for shares (bcrypt hashing)
- [ ] Token-based access (JWT or similar)
- [ ] IP whitelisting option
- [ ] Rate limiting per share
- [ ] CAPTCHA for public shares (optional)

#### Encryption
- [ ] TLS/HTTPS only (via tunnel providers)
- [ ] Optional file encryption at rest
- [ ] Encrypted share tokens
- [ ] Secure password storage (never plaintext)

#### Validation & Sanitization
- [ ] Path traversal prevention (no `../` access)
- [ ] File type whitelisting (configurable)
- [ ] Maximum file size limits
- [ ] Malware scanning integration (optional, via ClamAV)
- [ ] Content validation (reject executables by default)

#### Audit Logging
- [ ] All share creation logged with timestamp, user, path
- [ ] Access attempts logged (success/failure, IP, user-agent)
- [ ] File download events tracked
- [ ] Expiration and revocation logged
- [ ] Logs stored in `sandbox/logs/poke-share.log`
- [ ] Log rotation (max 10MB, keep 5 files)

#### Abuse Prevention
- [ ] Rate limiting (max 10 shares/hour per user)
- [ ] Bandwidth throttling (max 500MB/hour total)
- [ ] Max concurrent shares (default: 5)
- [ ] Auto-revoke on suspicious activity
- [ ] Blacklist mechanism for abuse IPs

### Implementation Plan

#### Phase 1: Basic File Server (1-2 days)
- [ ] Create `FileShareServer` class in `extensions/cloud/share_server.py`
- [ ] Implement single-file HTTP server with `http.server`
- [ ] Add path validation and sanitization
- [ ] Integrate with `TunnelManager` for public access
- [ ] Implement share tracking (in-memory dict initially)
- [ ] Add expiration timer with auto-cleanup

#### Phase 2: Folder Sharing (2-3 days)
- [ ] Extend server to handle directory listing
- [ ] Create HTML file browser UI (retro NES theme)
- [ ] Add recursive file access
- [ ] Implement ZIP download for bulk exports
- [ ] Add README.md rendering support

#### Phase 3: Security Hardening (3-4 days)
- [ ] Implement password authentication
- [ ] Add JWT token generation for shares
- [ ] Path traversal attack prevention
- [ ] Rate limiting middleware
- [ ] Comprehensive audit logging
- [ ] Security testing (penetration tests)

#### Phase 4: Advanced Features (2-3 days)
- [ ] Upload support for writable shares
- [ ] Access statistics and analytics
- [ ] Share templates (preconfigured settings)
- [ ] QR code generation for shares
- [ ] Email notification on share access (optional)

#### Phase 5: Polish & Documentation (1-2 days)
- [ ] User documentation (wiki/POKE-Share-Guide.md)
- [ ] Developer documentation
- [ ] Example workflows
- [ ] Security best practices guide
- [ ] Integration tests

**Total Estimate**: 9-14 days of focused development

### Testing Strategy

#### Unit Tests (`sandbox/tests/test_poke_share.py`)
```python
def test_share_file_basic()
def test_share_folder_basic()
def test_share_expiration()
def test_share_revocation()
def test_password_protection()
def test_path_traversal_prevention()
def test_rate_limiting()
def test_concurrent_shares()
```

#### Integration Tests
- Share → Tunnel → Access workflow
- Expiration cleanup process
- Multi-user concurrent access
- Bandwidth throttling
- Authentication flows

#### Security Tests
- Path traversal attempts (`../../etc/passwd`)
- SQL injection in passwords
- XSS in file names
- Large file DoS attacks
- Concurrent share flooding

### Configuration

**In `extensions/cloud/extension.json`:**
```json
{
  "share_settings": {
    "default_port_range": [8000, 8099],
    "default_expiration": "24h",
    "max_file_size": "100MB",
    "max_folder_size": "500MB",
    "allowed_file_types": ["*"],
    "blocked_file_types": [".exe", ".sh", ".bat", ".cmd"],
    "enable_upload": false,
    "require_password": false,
    "enable_analytics": true
  }
}
```

**In `core/config.py` (user settings):**
```python
# POKE Share Settings
POKE_MAX_CONCURRENT_SHARES = 5
POKE_DEFAULT_SHARE_LIFETIME = "24h"
POKE_SHARE_REQUIRE_PASSWORD = False
POKE_SHARE_ENABLE_UPLOAD = False
```

### User Experience

#### CLI Workflow
```bash
# Basic file share
uDOS> POKE SHARE FILE knowledge/water/boiling.md
✅ Shared: https://abc123.ngrok.io/boiling.md (expires in 24h)

# Password-protected folder
uDOS> POKE SHARE FOLDER sandbox/docs/ --password mysecret --expires 48
✅ Shared: https://xyz789.ngrok.io/ (password: mysecret, expires in 48h)

# List active shares
uDOS> POKE SHARE LIST
📤 2 active shares...

# Revoke share
uDOS> POKE SHARE STOP share-f7a3b2c1
✅ Share revoked
```

#### Web UI (Future)
- Dashboard widget showing active shares
- Click to copy share URLs
- One-click revocation
- Analytics graphs (hits, bandwidth)

## v2.2+ Roadmap - POKE GROUP Collaboration

### Goal
Enable multi-user collaboration on missions, knowledge documents, and projects through real-time sync and group workspaces.

### Features (High-Level)

#### 1. Group Creation & Management
```bash
POKE GROUP CREATE water-experts --private
POKE GROUP INVITE alice water-experts
POKE GROUP JOIN water-experts
POKE GROUP LIST
```

#### 2. Shared Workspaces
- Collaborative editing of markdown files
- Shared mission progress tracking
- Group chat/messaging
- File synchronization

#### 3. Real-Time Sync
- WebSocket-based updates
- Operational Transformation (OT) for conflict resolution
- Presence indicators (who's online)
- Activity feeds

### Security Requirements
- Invitation-only groups
- Role-based access (owner, editor, viewer)
- End-to-end encryption for group data
- Group audit logs
- Member authentication

**Estimate**: 4-6 weeks of development (complex feature)

## Migration & Compatibility

### v2.0 → v2.1 Transition
- **No breaking changes** for existing POKE TUNNEL commands
- **Service shortcuts unchanged** (POKE DASHBOARD, etc.)
- **New commands** (POKE SHARE) are additive
- **Config migration** automatic (sensible defaults)

### User Communication
- Announce POKE WEB in release notes
- Security best practices guide
- Example use cases (knowledge sharing, remote access)
- Migration guide for users with custom scripts

## Success Metrics

### v2.1 Goals
- [ ] 100% of POKE SHARE commands functional
- [ ] Zero security vulnerabilities (penetration tested)
- [ ] Comprehensive test coverage (>90%)
- [ ] User documentation complete
- [ ] Performance: Share creation <2s, access <500ms
- [ ] Stability: 24h+ uptime for long-lived shares

### Acceptance Criteria
- User can share a file and access it via tunnel
- User can share a folder with directory listing
- Password protection works correctly
- Shares auto-expire and clean up
- Rate limiting prevents abuse
- Audit logs capture all activity
- No path traversal vulnerabilities

## Open Questions

1. **Storage**: Should shared file metadata persist across uDOS restarts?
   - **Proposal**: Save to `sandbox/user/shares.json` for persistence

2. **Bandwidth**: Should we implement bandwidth monitoring per share?
   - **Proposal**: Track via middleware, show in POKE SHARE LIST

3. **Mobile**: Should shares have mobile-optimized UI?
   - **Proposal**: Yes, responsive design for file browser

4. **Analytics**: How detailed should access logs be?
   - **Proposal**: IP, timestamp, user-agent, bytes transferred

5. **Cleanup**: When should expired shares be purged from disk?
   - **Proposal**: Daily cron job at midnight + on-demand via POKE SHARE CLEAN

## Dependencies

### External
- `pyngrok` (already required for POKE TUNNEL)
- `flask` or `http.server` (Python stdlib sufficient initially)
- `bcrypt` (password hashing)
- `PyJWT` (token generation, optional)

### Internal
- `core.services.logging_manager` (audit logs)
- `extensions.cloud.tunnel_manager` (integration)
- `core.config` (settings management)

## Related Documentation

- [POKE Extension README](../../extensions/cloud/README.md)
- [Tunnel Management](../../extensions/cloud/tunnel_manager.py)
- [Security Best Practices](../../wiki/Security-Guide.md) (TODO)
- [Developers Guide - Extensions](../../wiki/Developers-Guide.md)

## Changelog

- **2025-12-01**: Initial roadmap created
- **2025-12-01**: Architecture decisions documented
- **2025-12-01**: v2.1 implementation plan outlined

---

**Next Steps**:
1. Review and approve roadmap with team
2. Create GitHub issues for Phase 1 tasks
3. Set up `sandbox/tests/test_poke_share.py` skeleton
4. Begin Phase 1 implementation (basic file server)
