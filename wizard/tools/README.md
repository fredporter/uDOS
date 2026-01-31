# Wizard Tools Directory

**Purpose:** Utilities and standalone scripts for Wizard server operations

---

## Production Tools (Keep in wizard/tools/)

### Secret Management
- **`secret_store_cli.py`** — CLI for managing secrets tomb
- **`check_secrets_tomb.py`** — Verify secrets tomb integrity
- **`reset_secrets_tomb.py`** — Reset/reinitialize secrets tomb

### Cloud Services (⚠️ Cloud-Only)
- **`web_proxy.py`** — HTTP proxy for web requests
- **`web_scraper.py`** — Web content extraction (violates core offline-first; Wizard-only)

### Library & Package Management
- **`library_cli.py`** — Library container management
- **`package_builder.py`** — TCZ package building for TinyCore Linux

### Development Utilities
- **`apk_keygen.py`** — APK signing key generation
- **`image_teletext.py`** — Teletext rendering utilities

### GitHub Integration
- **`github_dev.py`** — GitHub development utilities (plugin factory, repo operations)

### Legacy Scripts
- **`quick_fix_setup_sync.sh`** — Setup sync quick-fix script

---

## Cloud-Only Warning

**`web_scraper.py`** and **`web_proxy.py`** violate Core's offline-first principle. These tools:
- ✅ Are **Wizard-only** (never in Core/App)
- ✅ Require explicit cloud connectivity
- ⚠️  Should log `[CLOUD]` transport tags
- ⚠️  Must respect robots.txt and rate limits

---

## Tool Consolidation Recommendations

### Secret Store Utilities
Current: 3 separate files (`secret_store_cli.py`, `check_secrets_tomb.py`, `reset_secrets_tomb.py`)

**Suggested:** Consolidate into single `secrets_manager.py` with subcommands:
```bash
python -m wizard.tools.secrets_manager check
python -m wizard.tools.secrets_manager reset
python -m wizard.tools.secrets_manager list
```

### Package Tools
Current: `package_builder.py`, `apk_keygen.py` are separate

**Consider:** Create unified `package_tools.py` for distribution packaging

---

## Usage Examples

### Secret Store CLI
```bash
# Check secrets tomb status
python wizard/tools/check_secrets_tomb.py

# Reset secrets (CAUTION)
python wizard/tools/reset_secrets_tomb.py

# Manage secrets via CLI
python wizard/tools/secret_store_cli.py get GEMINI_API_KEY
python wizard/tools/secret_store_cli.py set OPENAI_KEY "sk-..."
```

### Web Scraper (Cloud-Only)
```bash
# Extract article to markdown
python wizard/tools/web_scraper.py https://example.com/article

# Scrape with specific pipeline
python wizard/tools/web_scraper.py --pipeline markdown https://docs.example.com
```

### Library CLI
```bash
# List containers
python wizard/tools/library_cli.py list

# Add container
python wizard/tools/library_cli.py add ./myproject
```

### Package Builder
```bash
# Build specific package
python wizard/tools/package_builder.py build core

# Build all packages
python wizard/tools/package_builder.py build all

# Create distribution bundle
python wizard/tools/package_builder.py bundle minimal
```

---

## Development vs Production

| Tool | Production | Development | Notes |
|------|-----------|-------------|-------|
| secret_store_cli.py | ✅ | ✅ | Core infrastructure |
| check_secrets_tomb.py | ✅ | ✅ | Health check utility |
| reset_secrets_tomb.py | ⚠️ | ✅ | Destructive - use with caution |
| web_proxy.py | ✅ | ✅ | Cloud-only, runtime |
| web_scraper.py | ✅ | ✅ | Cloud-only, on-demand |
| library_cli.py | ✅ | ✅ | Container management |
| package_builder.py | 🔧 | ✅ | Build-time only |
| apk_keygen.py | 🔧 | ✅ | Build-time only |
| image_teletext.py | ✅ | ✅ | Rendering utility |
| github_dev.py | 🔧 | ✅ | Development workflow |
| quick_fix_setup_sync.sh | ❌ | ✅ | Legacy/temporary |

**Legend:**
- ✅ Active use
- 🔧 Build/setup only
- ⚠️ Destructive operation
- ❌ Legacy/deprecated

---

## Migration Recommendations

1. **Consolidate secret utilities** → Single `secrets_manager.py` with subcommands
2. **Move build tools to dev/** → `package_builder.py`, `apk_keygen.py`, `github_dev.py`
3. **Archive legacy scripts** → `quick_fix_setup_sync.sh` to `.archive/`
4. **Document cloud-only tools** → Add `[CLOUD]` logging to `web_scraper.py` and `web_proxy.py`

---

_Last updated: 2026-01-31_
_Review after public release stabilization_
