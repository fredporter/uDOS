# Workspace Transferability Guide
**Version:** 1.0
**Status:** Active
**Last Updated:** 2026-02-24

---

## Quick Answer: YES, uDOS is Fully Transferable Between Machines

The workspace is designed to be portable. Here's what you need to know when switching machines.

---

## What's Safe to Transfer (Committed to Git)

✅ **These are included in the git repo:**
- Source code (`vibe/`, `core/`, `wizard/`, `library/`)
- Documentation (`docs/`, `wiki/`)
- Configuration templates (`.env.example`, `wizard/config/`)
- Build scripts (`bin/`, `scripts/`)
- Tests and fixtures
- Package management (`pyproject.toml`, `uv.lock`)

```bash
# Clone on new machine:
git clone <repo-url>
cd uDOS
```

---

## What's Machine-Specific (NOT Transferred)

❌ **These are gitignored and auto-generated per machine:**

| Item | Location | Auto-Create? | Notes |
|------|----------|--------------|-------|
| `.env` | repo root | ✅ Setup story | User identity + paths |
| `venv/` | repo root | ✅ ./bin/setup or uv sync | Python virtual environment |
| `memory/` | repo root | ✅ SETUP story | Runtime data, vault seeding |
| `secrets.tomb` | `wizard/` | ✅ SETUP story | Encrypted secret store |
| `wizard/config/wizard.json` | wizard/ | ✅ Repair wizard | Server configuration |
| `node_modules/` | core/ | ✅ npm install | Grid runtime dependencies |
| `.compost/` | repo root | – | Auto-cleanup archive |
| `.vibe/` | repo root | ✅ Repairs | Vibe runtime config |

**Bottom Line:** None of these block transferability. They regenerate automatically.

---

## Transfer Checklist (For Switching Machines)

### On Source Machine
```bash
# 1. Commit any work
git status
git add .
git commit -m "work in progress"

# 2. Push to remote
git push origin

# 3. (Optional) Back up local config
cp .env .env.backup.$(date +%Y%m%d)
```

### On New Machine

```bash
# 1. Clone the repo
git clone <repo-url> uDOS
cd uDOS

# 2. Install dependencies (one-time)
./bin/install-udos-vibe.sh         # Full setup
# or
./bin/install-udos-vibe.sh --core  # Core only

# 3. Run SETUP story to generate .env
python uDOS.py
# Select: SETUP

# 4. Start using it
vibe
```

**Time Required:** 5-10 minutes (depends on internet speed for downloads)

---

## Transferring Your Configuration

### If You Want to Keep the Same .env

For the same user identity and Ollama settings:

```bash
# On machine A: Back up your .env
cp .env .env.backup

# Transfer the backup to machine B:
# Option 1: Git (if you're okay with committing it temporarily)
git add .env.backup
git commit -m "backup config for transfer"
git push

# Option 2: Manual copy
scp user@machine-a:/path/to/.env.backup .

# On machine B: Restore it
cp .env.backup .env

# Update dynamic paths in .env if needed
nano .env  # Update UDOS_ROOT if path changed
```

### If You DON'T Transfer .env

Just run the SETUP story again on the new machine—it's fast and regenerates everything correctly.

---

## API Keys & Secrets Transfer

### ⚠️ IMPORTANT: Don't Transfer secrets.tomb Directly

The `secrets.tomb` is encrypted with a machine-local `WIZARD_KEY`. **Don't copy it between machines.**

**Instead:**

```bash
# On Machine A: Get the WIZARD_KEY
echo $WIZARD_KEY
# Copy output (e.g., "kJAtsfYmfYpY3Nf8EfcD7DvvMi9zhAPu0NLRS3X3LYN...")

# On Machine B: Set it before transferring secrets
export WIZARD_KEY="kJAtsfYmfYpY3Nf8EfcD7DvvMi9zhAPu0NLRS3X3LYN..."

# Now transfer secrets.tomb
scp user@machine-a:/path/to/wizard/secrets.tomb ./wizard/

# Verify it unlocks
uv run wizard/tools/check_secrets_tomb.py
```

**OR (Safer):** Re-add API keys via Wizard dashboard on new machine:
```bash
WIZARD start
# Settings > Integrations > Add Secret
# Re-add your Mistral, GitHub, etc. keys
```

---

## Environment Variables to Check

After cloning on a new machine, verify these are set:

```bash
# Should be in .env (auto-created by SETUP)
echo $UDOS_ROOT
echo $USER_NAME
echo $WIZARD_KEY

# Should be auto-detected or set by installer
echo $OS_TYPE
echo $UDOS_TIMEZONE
echo $UDOS_LOCATION
```

If any are missing, run SETUP again:
```bash
python uDOS.py
# Select: SETUP
```

---

## Troubleshooting Transfers

### "Module not found" errors
**Cause:** Venv not synced
**Fix:**
```bash
uv sync --group dev
# or
./bin/setup-vibe.sh
```

### ".env file not found"
**Cause:** .env was gitignored (correct behavior)
**Fix:**
```bash
cp .env.example .env
python uDOS.py  # Run SETUP
```

### "Secret store is locked"
**Cause:** WIZARD_KEY mismatch between machines
**Fix:**
```bash
# Option A: Use key from source machine
export WIZARD_KEY="<key-from-source>"

# Option B: Reset secrets (destructive)
uv run wizard/tools/reset_secrets_tomb.py
```

### "Network detection failed"
**Cause:** Vibe can't reach network checks
**Fix:**
```bash
# This is non-blocking, but verify network:
ping -c 1 8.8.8.8

# Continue anyway, offline mode works fine
vibe
```

### Different Python version
**Cause:** pyenv/asdf differences between machines
**Fix:**
```bash
# uv handles this, but verify:
uv --version
python --version  # Should be 3.12+

# If wrong version, sync to .python-version:
echo "3.12.0" > .python-version
uv sync
```

---

## Git Status After Transfer

After transferring and running SETUP on new machine:

```bash
git status
# Should show only .gitignored files as untracked:
# - .env
# - venv/
# - memory/
# - node_modules/
# - .pytest_cache/
# etc.

# If it shows source files as modified:
git checkout -- <file>  # Restore
```

All source code should be **unchanged** between machines.

---

## Performance Tips

### First Setup (Full Install)
```bash
# Takes ~5-10 minutes with good internet
./bin/install-udos-vibe.sh
```

### Cloning Large Repo
On slower connections, use:
```bash
git clone --depth 1 <repo-url>  # Faster, shallow clone
```

### Syncing Dependencies
```bash
# Fast sync (uses lockfile)
uv sync

# Slower, fresh dependencies
uv sync --refresh
```

---

## One-Liner Transfer Setup

For quick machine switches with same user config:

```bash
# On source:
git add . && git commit -m "transfer" && git push

# On dest:
git clone <url> && cd uDOS-vibe && \
  ./bin/install-udos-vibe.sh --update && \
  cp .env.backup .env 2>/dev/null || python uDOS.py && \
  vibe
```

---

## References

- [QUICK-START.md](../../QUICK-START.md) — Installation overview
- [INSTALLATION.md](../INSTALLATION.md) — Detailed install guide
- [docs/howto/SETUP-SECRETS.md](SETUP-SECRETS.md) — Secret management
- [docs/devlog/2026-02-24-security-audit.md](../devlog/2026-02-24-security-audit.md) — Security context

---

## Summary

✅ **uDOS-vibe is designed to be portable**
- Source code is in git
- Configuration auto-regenerates per machine
- Secrets are encrypted locally
- No machine-specific paths committed

**Transfer Time:** ~5-10 minutes for full install, <1 minute if keeping .env

**Next Time:** Just `git pull` and start coding!

