# uDOS v1.4.6 Packaging & Distribution Architecture

**Status:** Specification (v1.4.6 dev round)
**Owner:** uDOS Build/Release Team
**Milestone:** Round 6 (Packaging & Distribution Hardening) → Gate to v1.4.7 Stable

---

## Vision

Transform uDOS from a monolithic repository into a **consumable distribution system** with **production-grade hardening**:

- **Multi-variant packaging:** Core-only, Wizard-full, Sonic-standalone, Dev-complete
- **Local library ecosystem:** Versioned packages with dependency resolution, updates, sharing
- **Hardened Docker:** Health checks, lifecycle management, security scanning, backup/restore
- **Standalone Sonic:** Bootable ISO without Wizard dependency; integration bridge for Wizard hosts
- **Decentralized distribution:** No central monorepository; packages distributed via GitHub Releases, package registries, local libraries
- **Security & Compliance:** Third-party security audit, penetration testing, SBOM generation, secrets management
- **Performance & Observability:** Baseline metrics, load testing, centralized logging, distributed tracing, alerting
- **Backup & Recovery:** Automated backups, disaster recovery, upgrade rollback, data retention policies
- **Advanced Testing:** Chaos engineering, fuzzing, contract testing, compatibility matrix

**This round establishes the foundation for v1.4.7 Stable Release.**

---

## Package Architecture

### Package Variants

#### 1. `udos-core-slim` (Core Runtime Only)
**Use Case:** Lightweight local installation (Mac/Linux dev machines)

```
udos-core-slim-v1.4.6/
  core/                           # Stdlib-only Python runtime
  bin/
    ucli                          # Terminal entry point
    uDOS.py                      # Main executable
  docs/                           # Documentation
  themes/genre/                   # TUI themes (no Wizard GUI themes)
  README.md
  version.json                    # {"version": "1.4.6", "variant": "core-slim"}
  INSTALLATION.md
  requirements.txt                # Stdlib-only (empty or ecosystem)
```

**Install Size:** ~50 MB (no containers)
**Dependencies:** Python 3.8+, bash
**Installation:** Direct download or `brew tap fredbook/udos && brew install udos-core-slim`

#### 2. `udos-wizard-full` (Core + Wizard + Docker)
**Use Case:** Full-featured local installation (Wizard GUI + containers)

```
udos-wizard-full-v1.4.6/
  core/                           # Core runtime
  wizard/                         # Wizard server + GUI
    requirements.txt
    web/                          # Dashboard frontend (Svelte compiled)
    routes/                       # API routes
    mcp/                          # MCP server (stdio transport)
  venv/                           # Shared Python venv (root-level snapshot)
  docker-compose.yml              # Full service stack
  distribution/
    jekyll-site-template/         # GitHub Pages template
    local-library-catalog.json    # Library registry
  bin/
    ucli
    uDOS.py
    wizard-server
  README.md
  version.json                    # {"version": "1.4.6", "variant": "wizard-full"}
  INSTALLATION.md
  DOCKER-OPERATIONS.md
  LIBRARY-MANAGEMENT.md
```

**Install Size:** ~500 MB (with Docker images layered)
**Dependencies:** Python 3.11+, Docker, Docker Compose, Node.js (optional, for GUI dev)
**Installation:** `brew install udos-wizard-full` or direct download + `chmod +x uDOS.py && ./uDOS.py wizard start`

#### 3. `udos-sonic-iso` (Standalone Bootable ISO)
**Use Case:** Bootable USB media for system installation/recovery (no Wizard)

```
udos-sonic-v1.4.6.iso            # UEFI + MBR bootable ISO
  ~1.2 GB, contains:
    - Alpine Linux minimal kernel
    - Core uDOS TUI runtime
    - System installer script
    - Hardware detection utilities
    - Network bootstrap tools

Documentation:
  SONIC-STANDALONE.md             # Boot, install, recovery
  SONIC-HARDWARE-SUPPORT.md       # CPU, disk, GPU support matrix
```

**Install Size:** 1.2 GB ISO (bootable)
**Requirements:** USB drive (≥2GB), UEFI or BIOS firmware, internet for full install
**Installation:** WriteToUSB, `dd`, Balena Etcher, or Sonic installer script

#### 4. `udos-dev-complete` (Full Dev Environment)
**Use Case:** Complete development stack (Core + Wizard + Sonic + /dev)

```
udos-dev-complete-v1.4.6/
  core/                           # Core + TS runtime + examples
  wizard/                         # Wizard + dev extensions
  sonic/                          # Sonic + build tools
  dev/                            # Development tools, test harnesses
  / + everything from wizard-full
```

**Install Size:** ~1 GB
**Dependencies:** Full dev toolchain (Rust, Go, Node.js, Python 3.11, Docker, GCC, Make)
**Installation:** Developers clone git repo configured per [INSTALLATION-DEV.md](../INSTALLATION-DEV.md)

### Release Manifest

**`releases/v1.4.6-manifest.json`:**

```json
{
  "version": "1.4.6",
  "release_milestone": "round-6-complete",
  "variants": [
    {
      "name": "core-slim",
      "filename": "udos-core-slim-v1.4.6.tar.gz",
      "size_bytes": 52428800,
      "checksum_sha256": "abc123def456...",
      "checksum_sha512": "xyz789...",
      "gpg_signature": "-----BEGIN PGP SIGNATURE-----...",
      "platforms": ["macos-amd64", "macos-arm64", "linux-amd64", "linux-arm64"],
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-core-slim-v1.4.6.tar.gz",
      "minimum_python": "3.8"
    },
    {
      "name": "wizard-full",
      "filename": "udos-wizard-full-v1.4.6.tar.gz",
      "size_bytes": 524288000,
      "checksum_sha256": "def456abc123...",
      "platforms": ["macos-amd64", "macos-arm64", "linux-amd64"],
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-wizard-full-v1.4.6.tar.gz",
      "minimum_python": "3.11",
      "requires_docker": true
    },
    {
      "name": "sonic-iso",
      "filename": "udos-sonic-v1.4.6.iso",
      "size_bytes": 1258291200,
      "checksum_sha256": "ghi789jkl012...",
      "gpg_signature": "-----BEGIN PGP SIGNATURE-----...",
      "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-sonic-v1.4.6.iso",
      "bootable": true,
      "uefi_supported": true,
      "bios_fallback": true
    }
  ],
  "sbom": {
    "format": "cyclonedx",
    "url": "https://github.com/fredbook/uDOS/releases/download/v1.4.6/udos-v1.4.6-sbom.json"
  },
  "release_notes": "https://github.com/fredbook/uDOS/releases/tag/v1.4.6"
}
```

---

## Local Library System

### Library Catalog Schema

**`distribution/local-library-catalog.json`:**

```json
{
  "catalog_version": "1.0",
  "last_updated_milestone": "v1.4.6-round-6",
  "libraries": [
    {
      "id": "lib-grid-extensions",
      "namespace": "@uDOS/grid-extensions",
      "name": "Grid Extensions",
      "version": "1.2.3",
      "description": "Enhanced grid rendering and pathfinding utilities",
      "author": "fredbook",
      "license": "MIT",
      "homepage": "https://github.com/fredbook/lib-grid-extensions",
      "repository": {
        "type": "git",
        "url": "https://github.com/fredbook/lib-grid-extensions"
      },
      "downloads": 1250,
      "rating": 4.8,
      "dependencies": {
        "@uDOS/core": "^1.4.0"
      },
      "entry_point": "lib/grid_extensions/__init__.py",
      "install_path": "library/grid-extensions",
      "tags": ["grid", "spatial", "pathfinding"],
      "checksums": {
        "sha256": "abc123def456...",
        "sha512": "xyz789..."
      },
      "installed": {
        "milestone": "v1.4.6-round-6",
        "version": "1.2.3"
      }
    }
  ]
}
```

### Library Manager Commands

```bash
# Search and Info
LIBRARY search <query>                      # Search catalog
LIBRARY info <name>[@version]               # Show library details + dependencies
LIBRARY list                                # List installed libraries
LIBRARY list --available                    # List available libraries in catalog

# Install/Update
LIBRARY install <name>[@version]            # Install specific version (default: latest)
LIBRARY install <name>@~1.2                 # Semantic version constraint
LIBRARY install ./custom-lib.udos-package   # Install from archive
LIBRARY update <name>                       # Update to latest compatible
LIBRARY update --all                        # Update all installed libraries
LIBRARY check-updates                       # Show available updates

# Management
LIBRARY uninstall <name>                    # Remove library
LIBRARY rollback <name> --to <version>      # Downgrade to specific version
LIBRARY config <name> --edit                # Edit library config (JSON)
LIBRARY config <name> --show                # Show library configuration

# Publishing/Sharing
LIBRARY pack <name> [--output ./lib.udos-package]  # Export as distributable
LIBRARY share <name> --github               # Publish to GitHub registry
LIBRARY sync                                # Pull latest catalog from registry
```

### Library Package Format (`.udos-package`)

Distributable library archive (tar.gz + metadata):

```
lib-grid-extensions-v1.2.3.udos-package
  ├── manifest.json                # Library metadata + checksums
  ├── lib/
  │   └── grid_extensions/
  │       ├── __init__.py
  │       ├── grid.py
  │       └── pathfinder.py
  ├── docs/
  │   └── README.md
  ├── examples/
  │   └── pathfinding-demo.py
  └── requirements.txt              # Library dependencies
```

**Manifest:**
```json
{
  "id": "lib-grid-extensions",
  "version": "1.2.3",
  "name": "Grid Extensions",
  "author": "fredbook",
  "license": "MIT",
  "entry_point": "lib/grid_extensions/__init__.py",
  "install_path": "library/grid-extensions",
  "dependencies": {
    "@uDOS/core": "^1.4.0"
  },
  "checksums": {
    "sha256": "abc123def456..."
  }
}
```

### Dependency Resolution

Library manager implements:

1. **Semantic Versioning:** `^1.4.0` (≥1.4.0, <2.0.0), `~1.4.3` (≥1.4.3, <1.5.0)
2. **Circular Dependency Detection:** Warn if A→B→A, block install
3. **Version Conflict Resolution:** If B requires `^1.2` and C requires `~1.4`, error if mismatch
4. **Transitive Dependencies:** Auto-install dependencies of dependencies
5. **Lockfile:** `library/lock.json` pins exact versions (reproducible installs)

---

## Docker Container Hardening

### Health Checks

**All services in `docker-compose.yml` include:**

```yaml
services:
  wizard:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    restart_policy:
      condition: on-failure
      delay: 5s
      max_retries: 5
      window: 120s
```

**Health Check Contract:**
- `GET /api/health` returns `{"status": "healthy"}` if ready
- Interval: 30s, timeout: 10s
- Auto-restart on unhealthy (exponential backoff, max 5 retries)

### Lifecycle Management

**`docker/lifecycle-manager.py`:**

```python
class ContainerLifecycleManager:
  # Startup sequence enforcement
  def startup(self):
    # 1. Start dependency services first
    # 2. Wait for health checks to pass
    # 3. Mark service ready only when deps healthy
    # 4. Log startup event to audit trail
    pass

  # Graceful shutdown
  def shutdown(self):
    # 1. Send SIGTERM to all containers
    # 2. Wait 30s for graceful shutdown
    # 3. Force SIGKILL if timeout
    # 4. Log shutdown event with exit codes
    pass

  # Recovery from failure
  def recover(self, failed_service):
    # 1. Identify failed service
    # 2. Check logs for error patterns
    # 3. Attempt recovery (restart, reset state)
    # 4. Alert user if recovery fails
    pass
```

### Network Isolation

**Custom Docker Network (`udos-network`):**

```yaml
networks:
  udos-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

services:
  wizard:
    networks:
      - udos-network
    # Only accessible to other containers on udos-network
    # No direct port exposure unless explicitly mapped
```

### Volume Security

**Hardened Mounts:**

```yaml
services:
  wizard:
    volumes:
      - wizard-vault:/vault:rw         # Read-write vault data
      - wizard-config:/config:ro       # Read-only config
      - wizard-logs:/logs:rw           # Write-only logs
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
```

### Image Security

1. **Vulnerability Scanning:** Trivy scans all images at build time
2. **Minimal Base Images:** Alpine Linux where possible; distroless for prod
3. **Image Signing:** Sign images with GPG, verify in compose
4. **No Root:** Containers run as non-root user (UID 1000+)

---

## Wizard Admin Dashboard Page Audit

### Overview

The Wizard admin dashboard requires comprehensive audit covering page inventory, functionality verification, duplication analysis, and hardening. This section defines the audit scope and deliverables.

### Phase 1: Page Inventory & Mapping

**Deliverable:** Complete page inventory with dependency graph

| Page | Route | Status | Purpose | Dependencies | Duplicates |
|------|-------|--------|---------|--------------|-----------|
| Dashboard Home | `/#/dashboard` | [working/broken/incomplete] | System overview, status cards | — | — |
| System Health | `/#/system/health` | — | Container health, resource usage | `/api/health` | — |
| Configuration | `/#/config` | — | Wizard config editor (JSON) | `/api/config` | — |
| Library Manager | `/#/library` | — | Local library browser, install, update | `/api/library` | — |
| Docker Services | `/#/system/docker` | — | Container status, logs, controls | `/api/docker` | — |
| User Management | `/#/users` | — | Admin users, roles, permissions | `/api/users` | — |
| Audit Logs | `/#/audit-logs` | — | API request history, errors, access logs | `/api/audit-logs` | — |
| Extensions | `/#/extensions` | — | Installed extensions, enable/disable | `/api/extensions` | — |
| Settings | `/#/settings` | — | Admin preferences (theme, language, etc) | `/api/settings` | — |
| ... | ... | ... | ... | ... | ... |

**Audit Tasks:**
- [ ] List all routes in `wizard/routes/` and `wizard/web/src/` (identify any missing/extra)
- [ ] Count total pages (expected: 15-25 main pages)
- [ ] Identify orphaned routes (reachable via URL but no navigation link)
- [ ] Map page dependency graph (draw DAG: which pages call which APIs, reference which other pages)
- [ ] Identify duplicate pages by functionality (e.g., two "library" pages, two "config" pages)
- [ ] Check for duplicate navigation entries (same page listed in multiple nav menus)
- [ ] Document page load times (baseline metric for performance audit)

### Phase 2: Page Functionality Audit

**Deliverable:** Functionality verification matrix with test results

**For each page, verify:**

1. **Page Load:**
   - [ ] HTTP 200 response with no 404/500 errors
   - [ ] Page renders in <2 seconds (on modern hardware)
   - [ ] No console errors (JavaScript errors, unhandled promises)
   - [ ] No missing assets (images, CSS, fonts load successfully)
   - [ ] Graceful degradation if optional features unavailable (e.g., Docker not running)

2. **Interactive Elements:**
   - [ ] All buttons are clickable and functional
   - [ ] All links navigate to correct destinations
   - [ ] Dropdowns/selects open and show options
   - [ ] Modals open and close correctly
   - [ ] Accordions expand/collapse
   - [ ] Tabs switch content correctly

3. **Forms & Input Validation:**
   - [ ] Required fields show validation errors if empty
   - [ ] Input formats validated (email, numbers, JSON, etc)
   - [ ] Submit button disabled until form valid
   - [ ] Error messages are clear and actionable
   - [ ] Success messages confirm actions completed

4. **Data Binding & State:**
   - [ ] Form inputs update underlying model on change
   - [ ] Model updates refresh display in real-time
   - [ ] No stale data displayed after updates
   - [ ] Undo/redo works if supported

5. **CRUD Operations:**
   - [ ] Create: new items can be added (e.g., new user, new library)
   - [ ] Read: existing items display correctly with all fields
   - [ ] Update: edits persist after save
   - [ ] Delete: items can be removed with confirmation
   - [ ] Bulk operations work if supported

6. **Search & Filter:**
   - [ ] Search returns correct results
   - [ ] Filters apply and exclude correctly
   - [ ] Search is case-insensitive if expected
   - [ ] Results update in real-time as user types

7. **Real-time Updates:**
   - [ ] WebSocket/polling updates work (if used)
   - [ ] Server-sent updates display without page reload
   - [ ] No duplicate updates in list (check for duplicate event handling)

8. **Error Handling:**
   - [ ] Network errors show user-friendly messages (not stack traces)
   - [ ] Timeout errors are handled gracefully
   - [ ] Retry logic works if implemented
   - [ ] Offline state is handled clearly

### Phase 3: Duplication Audit

**Deliverable:** Duplication inventory with consolidation recommendations

**Check for:**

1. **Duplicate Page Designs:**
   - [ ] Pages with identical layouts (same sections, same styling)
   - [ ] Multiple admin pages with same visual structure
   - [ ] Example: two different "settings" pages, two "status" pages
   - **Action:** Consolidate into single canonical page

2. **Duplicate Forms:**
   - [ ] Same form repeated on multiple pages (e.g., library search)
   - [ ] Similar form structures (config, user create, library create)
   - **Action:** Extract into reusable form component library

3. **Duplicate CSS:**
   - [ ] Unused CSS rules (audit with coverage tools)
   - [ ] Duplicate selectors defining same styles
   - [ ] Similar color/spacing across pages (consolidate into design tokens)
   - **Action:** Extract into shared stylesheet, use CSS variables

4. **Duplicate API Endpoints:**
   - [ ] Endpoints that return same data (e.g., `/api/config` and `/api/settings`)
   - [ ] Endpoints with same logic, different paths (e.g., `/api/user/{id}` and `/api/users/{id}`)
   - **Action:** Consolidate into single endpoint with clear semantics

5. **Duplicate State Management:**
   - [ ] Multiple stores tracking same data (e.g., `userStore` and `accountStore`)
   - [ ] State duplicated across components (prop drilling instead of store)
   - **Action:** Consolidate into single store, use proper state management pattern

6. **Duplicate Components:**
   - [ ] Button styles repeated in multiple components
   - [ ] Table layouts repeated for different data types
   - [ ] Modal patterns used identically in different contexts
   - **Action:** Create reusable component library (Button, Table, Modal, Form, etc)

**Duplication Report Template:**

```
### Duplicate: [Name]
- **Type:** [Page/Form/CSS/API/Component]
- **Locations:** [List of files/routes]
- **Functionality:** [What it does]
- **Impact:** [Code size or maintenance burden]
- **Recommendation:** Consolidate into [single location]
- **Effort Estimate:** [hours to consolidate]
```

### Phase 4: Security Hardening

**Deliverable:** Security audit report with CVE/vulnerability list and remediation plan

1. **Input Validation Audit:**
   - [ ] All form inputs sanitized before sending to server
   - [ ] File uploads validated (type, size, content)
   - [ ] URL parameters validated (no path traversal)
   - [ ] JSON parsing handles invalid JSON gracefully

2. **Output Encoding:**
   - [ ] User-generated content HTML-encoded (prevent XSS)
   - [ ] API responses rendered safely
   - [ ] No `dangerouslySetInnerHTML` or equivalent without sanitization

3. **Authentication & Authorization:**
   - [ ] Session tokens stored securely (httpOnly cookies preferred)
   - [ ] Token refresh works without user noticing
   - [ ] Session timeout enforced
   - [ ] Buttons/features hidden if user lacks permission
   - [ ] API checks permissions server-side (not just client-side)

4. **CSRF Protection:**
   - [ ] Forms include CSRF tokens
   - [ ] State-changing requests (POST/PUT/DELETE) require token
   - [ ] SameSite cookie attribute set correctly

5. **API Security:**
   - [ ] Rate limiting prevents brute force (max requests per minute)
   - [ ] Error messages don't leak sensitive info (e.g., "user not found" vs "invalid credentials")
   - [ ] API validates all inputs server-side
   - [ ] API responses filtered (no unnecessary data leakage)

### Phase 5: Penetration Testing

**Deliverable:** Penetration test report with proof-of-concept exploits (if found)

**Manual Testing:**
- [ ] Attempt XSS injection in form fields
- [ ] Attempt SQL injection via search/filter
- [ ] Attempt command injection in text areas
- [ ] Attempt CSRF via form submission from external site
- [ ] Attempt privilege escalation (demoted user tries to access admin page)
- [ ] Attempt session hijacking (steal session token from URL/cookie)
- [ ] Attempt brute force (rapid login attempts)

**Automated Scanning:**
- [ ] Run OWASP ZAP on all admin pages
- [ ] Run Burp Suite Community on all APIs
- [ ] Review scan findings and confirm true positives vs false positives
- [ ] Document any CVEs with CVSS scores

### Phase 6: Accessibility & UX

**Deliverable:** WCAG 2.1 AA compliance checklist with remediation plan

1. **Keyboard Navigation:**
   - [ ] All interactive elements reachable via Tab key
   - [ ] Tab order is logical (top-to-bottom, left-to-right)
   - [ ] Focus indicator visible on all elements
   - [ ] Escape key closes modals/menus
   - [ ] Enter key submits forms

2. **Screen Reader Support:**
   - [ ] All images have alt text
   - [ ] Form labels properly associated with inputs
   - [ ] Page structure uses semantic HTML (headings, landmarks)
   - [ ] ARIA labels/roles used correctly
   - [ ] Tables have proper headers

3. **Visual Accessibility:**
   - [ ] Text contrast ratio ≥4.5:1 for normal text
   - [ ] Text contrast ratio ≥3:1 for large text
   - [ ] No information conveyed by color alone (use icons/labels)
   - [ ] Focus indicators visible (not hidden by CSS)

4. **Responsive Design:**
   - [ ] Pages render correctly at 320px width (mobile)
   - [ ] Pages render correctly at 768px width (tablet)
   - [ ] Pages render correctly at 1440px width (desktop)
   - [ ] No horizontal scrolling at any breakpoint
   - [ ] Touch targets ≥44x44px (mobile-friendly)

5. **Browser Compatibility:**
   - [ ] Chrome (latest 2 versions)
   - [ ] Firefox (latest 2 versions)
   - [ ] Safari (latest 2 versions)
   - [ ] Edge (latest 2 versions)

### Phase 7: Performance Testing

**Deliverable:** Performance profile with optimization recommendations

**Metrics to measure:**

1. **Page Load Time:**
   - [ ] Time to First Contentful Paint (FCP)
   - [ ] Time to Largest Contentful Paint (LCP)
   - [ ] Cumulative Layout Shift (CLS)
   - [ ] First Input Delay (FID)
   - Target: <2 seconds LCP, <0.1 CLS

2. **Runtime Performance:**
   - [ ] Frame rate when scrolling lists (target: 60 fps)
   - [ ] Response time to button clicks (target: <100ms)
   - [ ] Real-time update latency (target: <500ms)

3. **Memory Usage:**
   - [ ] Baseline memory (page first load)
   - [ ] Memory after 100 interactions
   - [ ] Memory after 8 hours of continuous operation
   - Target: No growth >10% over baseline

4. **Network Usage:**
   - [ ] Total payload size (gzipped)
   - [ ] Number of requests
   - [ ] Largest individual requests
   - Target: <1 MB total, <30 requests

**Tools:**
- Chrome DevTools Lighthouse
- WebPageTest
- k6 load testing
- Memory profiling (Chrome DevTools)

### Phase 8: Documentation & Report

**Deliverables:**

1. **Page Inventory Spreadsheet:**
   - All pages, routes, statuses, dependencies, duplicates
   - Cross-referenced with test results from Phase 2

2. **Duplication Report:**
   - List of all duplicates found with consolidation recommendations
   - Effort estimates for each consolidation task
   - Prioritized list (highest impact first)

3. **Security Audit Report:**
   - Findings by category (XSS, CSRF, auth, injection, etc)
   - Risk levels (critical, high, medium, low)
   - Remediation steps for each finding
   - Timeline for fixes

4. **Accessibility Report:**
   - WCAG 2.1 AA compliance status (% compliant)
   - List of non-compliant elements with fixes
   - Accessibility roadmap for future work

5. **Performance Report:**
   - Current metrics vs targets
   - Identified bottlenecks
   - Optimization recommendations (code splitting, lazy loading, caching, etc)
   - Timeline for performance improvements

6. **WIZARD-ADMIN-SECURITY.md:**
   - Wizard admin security architecture
   - Attack surface analysis
   - Threat model and mitigations
   - Session management details
   - Authentication/authorization flows
   - Rate limiting policies
   - CSRF protection details
   - Data validation strategies

7. **WIZARD-ADMIN-ONBOARDING.md:**
   - How to set up Wizard admin securely
   - Password best practices
   - 2FA setup (if applicable)
   - Role-based access control setup
   - Common admin workflows
   - Troubleshooting guide

8. **Refactoring Roadmap:**
   - Prioritized list of consolidations
   - Effort estimates
   - Dependencies between tasks
   - Release timeline

---

## MCP Server Integration

### Wizard MCP Server Architecture

**Purpose:** Expose Wizard capabilities to VSCode Copilot and other MCP clients via stdio transport.

**Location:** `wizard/mcp/mcp_server.py`

**Protocol:** Model Context Protocol (MCP) stdio transport

#### MCP Server Components

```
wizard/mcp/
  mcp_server.py                   # Main MCP stdio server
  tools/
    command_tool.py               # Execute uDOS commands via MCP
    state_tool.py                 # Query game state
    config_tool.py                # Manage configuration
  resources/
    game_state.py                 # Expose current game state as resource
    command_history.py            # Command execution history
  schemas/
    tool_schemas.json             # JSON schemas for MCP tools
  tests/
    test_mcp_lifecycle.py         # Server startup/shutdown tests
    test_tool_execution.py        # Tool execution tests
    test_vscode_integration.py    # VSCode integration E2E tests
```

#### MCP Tools Exposed

| Tool Name | Description | Parameters | Auth Required |
|-----------|-------------|------------|---------------|
| `execute_command` | Run uDOS command | `command: str`, `args: dict` | Yes |
| `query_state` | Get current game state | `scope: str` | No |
| `get_config` | Read configuration | `key: str` | No |
| `set_config` | Update configuration | `key: str`, `value: any` | Yes |
| `list_extensions` | List installed extensions | None | No |
| `library_search` | Search library catalog | `query: str` | No |

#### VSCode Integration

**Configuration:** `.vscode/mcp.json` (auto-generated on install)

```json
{
  "mcpServers": {
    "udos-wizard": {
      "command": "/Users/fredbook/Code/uDOS/.venv-mcp/bin/python",
      "args": ["/Users/fredbook/Code/uDOS/wizard/mcp/mcp_server.py"],
      "transport": "stdio",
      "env": {
        "UDOS_HOME": "/Users/fredbook/Code/uDOS",
        "WIZARD_PORT_FILE": "/Users/fredbook/Code/uDOS/wizard/.wizard-port"
      }
    }
  }
}
```

**Copilot Integration Flow:**

1. **Startup:** VSCode launches MCP server via stdio
2. **Discovery:** MCP server announces available tools/resources
3. **Tool Invocation:** Copilot calls tools via MCP protocol
4. **Command Execution:** MCP server routes to Wizard → Core
5. **Response:** Results streamed back through stdio
6. **Shutdown:** MCP server receives SIGTERM, graceful cleanup

#### Hardening Requirements

**Security:**

- ✅ **Input Validation:** All MCP tool parameters validated against JSON schemas
- ✅ **Command Injection Prevention:** Whitelist allowed commands; sanitize all user input
- ✅ **Authorization:** Token-based auth for write operations (config changes, command execution)
- ✅ **Rate Limiting:** Max 100 requests/minute per client to prevent abuse
- ✅ **Audit Logging:** All MCP requests logged with timestamp, client ID, tool name, params

**Reliability:**

- ✅ **Graceful Degradation:** If Wizard unavailable, MCP server returns error (not crash)
- ✅ **Timeout Handling:** All Wizard calls timeout after 30s; return error to client
- ✅ **Error Messages:** Sanitized errors (no stack traces exposed to MCP clients)
- ✅ **Health Check:** MCP server exposes `/health` endpoint for monitoring
- ✅ **Process Management:** Clean shutdown on SIGTERM/SIGINT; no zombie processes

**Performance:**

- ✅ **Response Time:** 95th percentile <500ms for read operations
- ✅ **Memory Usage:** <100 MB resident memory under normal load
- ✅ **Connection Pooling:** Reuse Wizard HTTP connections (no reconnect per request)
- ✅ **Caching:** Cache static resources (config schemas, tool definitions) for 5 minutes

#### Testing Strategy

**Unit Tests:** `wizard/mcp/tests/`

```python
# test_mcp_lifecycle.py
def test_server_startup_stdio():
    """Test MCP server starts and announces tools via stdio"""
    proc = subprocess.Popen([...], stdin=PIPE, stdout=PIPE)
    # Verify initialization message
    # Verify tool list announcement
    # Clean shutdown

def test_graceful_shutdown():
    """Test SIGTERM triggers clean shutdown"""
    # Start server
    # Send SIGTERM
    # Verify exit code 0
    # Verify no orphaned processes

# test_tool_execution.py
def test_execute_command_success():
    """Test valid command execution"""
    # Mock Wizard response
    # Call execute_command tool
    # Verify response matches schema

def test_execute_command_injection_blocked():
    """Test command injection prevention"""
    # Attempt shell metacharacters in command
    # Verify request rejected

def test_rate_limiting():
    """Test rate limiter blocks excessive requests"""
    # Make 101 requests rapidly
    # Verify 101st request gets 429 Too Many Requests
```

**Integration Tests:** `wizard/mcp/tests/integration/`

```python
# test_vscode_integration.py
def test_copilot_tool_discovery():
    """Test VSCode can discover MCP tools"""
    # Launch MCP server via VSCode extension API
    # Query available tools
    # Verify all expected tools present

def test_copilot_command_execution_e2e():
    """Test end-to-end command execution via Copilot"""
    # Copilot invokes execute_command
    # MCP server routes to Wizard
    # Wizard executes in Core
    # Response returns to Copilot
    # Verify result matches expectation

def test_wizard_unavailable_fallback():
    """Test MCP server handles Wizard downtime"""
    # Stop Wizard service
    # Attempt execute_command via MCP
    # Verify graceful error returned (not crash)
```

**E2E Tests:** Run via `WIZARD test --mcp`

1. Start Wizard services (`WIZARD start`)
2. Launch MCP server
3. Connect VSCode Copilot client (simulated)
4. Execute all MCP tools with valid/invalid inputs
5. Verify audit logs written correctly
6. Verify no memory leaks (monitor RSS over 100 iterations)
7. Graceful shutdown test

**Performance Tests:** `wizard/mcp/tests/perf/`

```bash
# Load test: 1000 requests over 10 seconds
python wizard/mcp/tests/perf/load_test.py --requests 1000 --duration 10

# Expected:
# - 95th percentile: <500ms
# - Error rate: <1%
# - Memory growth: <10 MB
```

#### CI/CD Integration

**GitHub Actions:** `.github/workflows/mcp-tests.yml`

```yaml
name: MCP Server Tests

on:
  push:
    paths:
      - 'wizard/mcp/**'
  pull_request:

jobs:
  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r wizard/mcp/requirements.txt
      - name: Run unit tests
        run: pytest wizard/mcp/tests/ -v --cov=wizard/mcp
      - name: Run integration tests
        run: pytest wizard/mcp/tests/integration/ -v
      - name: Security scan
        run: bandit -r wizard/mcp/ -ll
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

#### Monitoring & Observability

**Metrics Collected:**

- Request count per tool (Prometheus counter)
- Request latency histogram (P50, P95, P99)
- Error rate by error type
- Active connections gauge
- Memory usage (RSS, VMS)

**Logs:**

```json
{
  "timestamp": "<ISO-8601-timestamp>",
  "level": "INFO",
  "component": "mcp_server",
  "event": "tool_invocation",
  "tool": "execute_command",
  "client_id": "vscode-copilot-abc123",
  "duration_ms": 245,
  "status": "success"
}
```

**Alerts:**

- Error rate >5% over 5 minutes → Slack notification
- P95 latency >1s over 5 minutes → Warning
- Memory usage >200 MB → Critical alert

---

## Security & Compliance Hardening

### P5 -- Security Audit & Penetration Testing

**Goal:** Comprehensive security hardening before Stable Release

- [ ] **Security Audit**
  - [ ] Third-party security audit of Core + Wizard + MCP server
  - [ ] Penetration testing on Wizard HTTP endpoints
  - [ ] Code security scanning (Bandit for Python, ESLint security plugins)
  - [ ] Dependency vulnerability scanning (pip-audit, npm audit, Trivy)
  - [ ] Secrets scanning (no credentials in git history)
  - [ ] Supply chain security audit (verify all dependencies)

- [ ] **SBOM Generation & Artifact Provenance**
  - [ ] Auto-generate SBOM in CycloneDX format for all releases
  - [ ] Include all Python deps (requirements.txt), JS deps (package.json), Docker images
  - [ ] Sign SBOM artifacts with GPG
  - [ ] Publish SBOM with release artifacts
  - [ ] Generate SLSA provenance for build reproducibility

- [ ] **Compliance Documentation**
  - [ ] License inventory (all dependencies + license types)
  - [ ] Attribution file generation (NOTICE.txt)
  - [ ] Privacy policy (if cloud services involved)
  - [ ] Terms of service (if publishing enabled)
  - [ ] GDPR compliance check (if EU users)
  - [ ] Export compliance (check for cryptography restrictions)

- [ ] **Secrets Management**
  - [ ] Document secrets rotation procedures (GitHub PAT, API keys)
  - [ ] Implement secrets vault integration (optional: 1Password, HashiCorp Vault)
  - [ ] Add secrets expiry warnings in SETUP/CONFIG commands
  - [ ] Encrypt sensitive config files at rest
  - [ ] Add secrets detection pre-commit hooks

### P6 -- Performance Baselines & Load Testing

**Goal:** Establish performance budgets and regression detection

- [ ] **Core Command Benchmarks**
  - [ ] Baseline all P0 commands (HEALTH, VERIFY, DRAW, PLACE, BINDER, RUN, PLAY)
  - [ ] Performance budget: p95 <100ms for read operations, <500ms for writes
  - [ ] CI gate: fail if any command regresses >20% from baseline
  - [ ] Generate benchmark report per release (markdown table + graphs)
  - [ ] Store benchmark history in `memory/system/benchmarks/`

- [ ] **Wizard Service Load Tests**
  - [ ] Load test HTTP server: 1000 concurrent users
  - [ ] Load test MCP server: 100 req/sec sustained for 10 minutes
  - [ ] Load test file picker: 100k+ files in vault
  - [ ] Load test GitHub Pages sync: 10k+ markdown files
  - [ ] Identify bottlenecks and optimize (caching, indexing, query optimization)

- [ ] **Memory & Resource Tests**
  - [ ] Long-running soak test (24 hours, monitor RSS growth)
  - [ ] Detect memory leaks (valgrind for Python extensions if any)
  - [ ] Resource limits enforcement (ulimit, cgroups in Docker)
  - [ ] Test graceful degradation under memory pressure
  - [ ] Profile CPU usage patterns under realistic load

- [ ] **Regression Detection**
  - [ ] Automated benchmark comparison in CI (current vs baseline)
  - [ ] Performance dashboard in Wizard GUI (`#/system/performance`)
  - [ ] Alert on >20% regression in any metric
  - [ ] Track performance trends over releases

### P7 -- System-Wide Observability

**Goal:** Production-ready monitoring and debugging

- [ ] **Centralized Logging**
  - [ ] Structured logging format (JSON) for all components
  - [ ] Log aggregation: file-based + optional remote (syslog, Loki)
  - [ ] Log rotation policies (max 7 days, 100MB per file)
  - [ ] LOGS command enhancement: filter by component, level, time range, search
  - [ ] Correlation IDs for cross-service request tracking

- [ ] **Metrics & Alerting**
  - [ ] Prometheus metrics for Core (command latency, error rate, cache hits)
  - [ ] Prometheus metrics for Wizard (HTTP requests, active connections, queue depth)
  - [ ] Prometheus metrics for Docker (container health, resource usage)
  - [ ] Pre-configured Grafana dashboards (optional, exported as JSON)
  - [ ] Alert rules: error rate >5%, memory >80%, disk >90%, container unhealthy
  - [ ] Wire alerts to HEALTH command output

- [ ] **Distributed Tracing** (optional, nice-to-have)
  - [ ] OpenTelemetry integration for cross-service requests
  - [ ] Trace uCODE → Shell → VIBE dispatch chain
  - [ ] Trace Wizard → Core API calls
  - [ ] Trace MCP requests end-to-end
  - [ ] Visualize traces in Jaeger (optional)

- [ ] **Health Dashboard**
  - [ ] Real-time system health in Wizard GUI (`#/system/health`)
  - [ ] Show all metrics: CPU, memory, disk, network, container status
  - [ ] Show recent errors and warnings
  - [ ] Show performance trends (last 24h, 7d, 30d)

### P8 -- Backup, Recovery & Business Continuity

**Goal:** Zero data loss, rapid recovery

- [ ] **Automated Backups**
  - [ ] `BACKUP create` command: snapshot vault + memory + config
  - [ ] `BACKUP restore <snapshot>` command
  - [ ] Scheduled backups (daily, weekly, monthly retention)
  - [ ] Backup verification (test restore in sandbox)
  - [ ] Backup encryption (optional, GPG-encrypted archives)
  - [ ] Incremental backups (delta-only after first full backup)

- [ ] **Disaster Recovery Procedures**
  - [ ] Document full system recovery from backup
  - [ ] Document partial recovery (vault only, config only)
  - [ ] Test recovery on clean system (DR drill)
  - [ ] Recovery time objective (RTO): <1 hour
  - [ ] Recovery point objective (RPO): last backup (ideally <24h)
  - [ ] Create disaster recovery runbook

- [ ] **Upgrade Rollback**
  - [ ] Pre-upgrade snapshot automation (auto-backup before upgrade)
  - [ ] Rollback script: `REPAIR rollback --to v1.4.5`
  - [ ] Test failed upgrade → rollback → retry workflow
  - [ ] Version history tracking (what versions were installed when)
  - [ ] Preserve user data across rollback

- [ ] **Data Retention & Archival**
  - [ ] Define retention policies (logs: 7d, backups: 30d, archives: 1y)
  - [ ] Automatic archival of old data
  - [ ] Compression for archived data
  - [ ] Document data deletion procedures (GDPR right to erasure)

### P9 -- Advanced Testing

**Goal:** Production-grade reliability

- [ ] **Chaos Engineering**
  - [ ] Network partition tests (Wizard ↔ Core connection loss)
  - [ ] Disk full simulation (test graceful degradation)
  - [ ] Memory pressure tests (OOM handling)
  - [ ] Container crash recovery tests (auto-restart verification)
  - [ ] Clock skew tests (time synchronization issues)

- [ ] **Fuzzing**
  - [ ] Fuzz test all command parsers (invalid syntax, edge cases)
  - [ ] Fuzz test MCP tool parameters
  - [ ] Fuzz test file path inputs (path traversal, special chars)
  - [ ] Fuzz test configuration files (invalid JSON/YAML)
  - [ ] Fuzz test network inputs (malformed HTTP, WebSocket frames)

- [ ] **Contract Testing**
  - [ ] Pact tests for Wizard → Core API
  - [ ] MCP protocol contract tests (Copilot compatibility)
  - [ ] Docker Compose contract tests (service dependencies)
  - [ ] Library package format contract tests

- [ ] **Compatibility Testing**
  - [ ] Test on Python 3.8, 3.9, 3.10, 3.11, 3.12
  - [ ] Test on macOS Intel, macOS ARM, Ubuntu 20.04, 22.04, 24.04
  - [ ] Test with different Docker versions
  - [ ] Test with different shell environments (bash, zsh, fish)

---

## Sonic Standalone Integration

### Sonic ISO Build Pipeline

**`sonic/build-iso.sh`:**

```bash
# 1. Create minimal Alpine rootfs
# 2. Add Core uDOS TUI runtime
# 3. Add installer script
# 4. Build UEFI/MBR bootable image
# 5. Sign image (GPG)
# 6. Generate checksums
```

**Output:** `builds/udos-sonic-v1.4.6.iso` (1.2 GB)

### Boot Modes

| Boot Mode | Use Case | Hardware | Boot Time |
|-----------|----------|----------|-----------|
| **UEFI** | Modern laptops/desktops (>2012) | x86_64, ARM64 | ~8s |
| **BIOS** | Older systems, VMs | x86_64 | ~10s |
| **TFTP/PXE** | Network install | Any networked | Variable |

### Sonic → Wizard Bridge

**How Booted Sonic Connects to Wizard Host:**

1. **Discovery Phase:**
   - Sonic detects Wizard services on LAN (mDNS/Bonjour)
   - Wizard broadcasts `_udos-wizard._tcp` service
   - Sonic resolves host, obtains SSH public key

2. **Auth Phase:**
   - Sonic challenges host with random nonce
   - Host signs with private key
   - Sonic verifies signature

3. **Command Execution:**
   - User runs command in Sonic TUI: `SSH> run-command my-command`
   - SSH tunnel established to Wizard host
   - Command routed to Wizard → Core execution
   - Results streamed back to Sonic

4. **State Sync:**
   - Sonic syncs game state to Wizard (via SSH)
   - Wizard manages persistent state
   - Sonic shutdown doesn't lose progress

### Sonic Update Mechanism

**`SONIC update`:**

```bash
# 1. Check GitHub releases for newer ISO
# 2. Download new ISO (bg transfer if >500MB)
# 3. Verify checksum + GPG signature
# 4. Apply binary delta (only download differences)
# 5. Offer user to reboot and boot from new ISO
```

---

## Build & Release Automation

### GitHub Actions Release Workflow

**`.github/workflows/release.yml`:**

```yaml
name: Release Build

on:
  push:
    tags:
      - 'v1.4.*'

jobs:
  build-matrix:
    runs-on: ${{ matrix.runner }}
    strategy:
      matrix:
        runner: [macos-latest, ubuntu-latest]
        variant: [core-slim, wizard-full]
    steps:
      - uses: actions/checkout@v4
      - name: Build variant
        run: python bin/build-release.py --variant ${{ matrix.variant }}
      - name: Sign artifact
        run: gpg --detach-sign built/${{ matrix.variant }}.tar.gz
      - name: Upload to releases
        uses: softprops/action-gh-release@v1
        with:
          files: built/**
          draft: false
```

### Artifact Signing

**GPG workflow:**

```bash
# Build artifacts
python bin/build-release.py --variant core-slim

# Sign with release key
gpg --default-key releases@udos.dev --detach-sign udos-core-slim-v1.4.6.tar.gz

# Verify signature (CI)
gpg --verify udos-core-slim-v1.4.6.tar.gz.sig udos-core-slim-v1.4.6.tar.gz
```

---

## Success Criteria

✅ **Packaging:** All 4 variants build successfully on macOS and Linux
✅ **Install:** Any variant installable in <5 minutes on clean system
✅ **Libraries:** Library install/update/rollback <30 seconds per library
✅ **Docker:** All containers healthy, auto-restart on failure (>99% uptime)
✅ **Sonic:** Boots on 5+ diverse hardware targets; Wizard bridge latency <200ms
✅ **Security:** No CVEs in Docker images; all artifacts signed and verified
✅ **Tests:** E2E coverage for all 4 variants + upgrade paths (v1.4.3 → v1.4.6)
✅ **MCP Server:** All unit tests pass; VSCode integration E2E tests pass; <500ms P95 latency
✅ **MCP Hardening:** Input validation 100% coverage; rate limiting enforced; audit logs complete
✅ **MCP Monitoring:** Metrics exported to Prometheus; error rate <1%; no memory leaks
✅ **Wizard Admin Audit:** Security hardening complete (XSS/CSRF/injection prevention); penetration testing passed; accessibility WCAG 2.1 AA compliant; performance <2s load time
✅ **Security Audit (P5):** Third-party security audit passed; SBOM generated for all releases; no secrets in git history; compliance documented
✅ **Performance Baselines (P6):** All P0 commands meet performance budget; load tests passed; no memory leaks; regression detection operational
✅ **Observability (P7):** Structured logging operational; Prometheus metrics exported; alerts configured; health dashboard functional
✅ **Backup & Recovery (P8):** Automated backups working; disaster recovery tested; upgrade rollback functional; RTO <1hr, RPO <24hr
✅ **Advanced Testing (P9):** Chaos tests passed; fuzzing completed; contract tests passing; compatibility matrix validated
✅ **Documentation:** Installation guides for all platforms, library docs, Docker ops manual, MCP integration guide, Wizard admin security guide, DR runbook, SBOM published

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Specification](https://github.com/compose-spec/compose-spec)
- [Semantic Versioning](https://semver.org/)
- [Trivy Vulnerability Scanner](https://github.com/aquasecurity/trivy)
- [UEFI Specification](https://uefi.org/specifications)
