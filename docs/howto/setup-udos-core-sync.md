# Setup uDOS-core Sync — GitHub Actions Configuration

**Status:** ⚠️ Not Syncing (Secrets Not Configured)  
**Last Updated:** 2026-01-18  
**Audience:** Repository maintainers

---

## Problem

The GitHub Actions workflow `.github/workflows/sync-public.yml` is configured to automatically sync the private `fredporter/uDOS-dev` repository to the public `fredporter/uDOS-core` mirror, but **the required secrets are not configured** in GitHub repository settings.

**Current State:**

- ❌ Workflow exists and is enabled
- ❌ Secrets `PUBLIC_REPO` and `PUBLIC_TOKEN` are missing
- ❌ Manual syncing required or workflow is skipped

**Workflow Trigger:**

- Automatic: On every push to `main` branch
- Manual: Via GitHub Actions "Run workflow" button

---

## What Gets Synced

### Included in Public Mirror

```
/public/          → Wizard, Extensions, Knowledge, Library
/core/            → TypeScript runtime
/docs/            → Engineering documentation (public)
LICENSE*          → License files
README.md         → Auto-generated public README
```

### Excluded from Public Mirror

```
/app/             → Tauri app (separate repo)
/app-beta/        → Beta app (separate repo)
/memory/          → User data (gitignored)
/wizard/server.py → Contains secrets/config
/.github/         → CI configs (avoid workflow loops)
/.dev/            → Dev files (gitignored)
/.archive/        → Archived content (gitignored)
```

---

## Solution: Configure GitHub Secrets

### Step 1: Create GitHub PAT (Personal Access Token)

1. Go to GitHub Settings → [Developer settings → Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. **Token settings:**
   - **Token name:** `uDOS-Core-Sync`
   - **Expiration:** 90 days or longer
   - **Scopes:** Check only `repo` (full control of private repositories)
   - **Click:** "Generate token"
4. **Copy the token immediately** (you won't see it again)

### Step 2: Add Secrets to Private Repo (fredporter/uDOS-dev)

1. Go to [fredporter/uDOS-dev → Settings → Secrets and variables → Actions](https://github.com/fredporter/uDOS-dev/settings/secrets/actions)
2. Click "New repository secret"
3. **Add first secret:**
   - **Name:** `PUBLIC_REPO`
   - **Value:** `fredporter/uDOS-core`
   - Click "Add secret"
4. **Add second secret:**
   - **Name:** `PUBLIC_TOKEN`
   - **Value:** (paste the PAT token from Step 1)
   - Click "Add secret"

**Verify:** Both secrets should now appear in the Secrets list (values hidden)

### Step 3: Test the Sync

Option A: **Push to main** (automatic trigger)

```bash
cd ~/uDOS
git push origin main
```

The workflow will automatically trigger and sync.

Option B: **Manual trigger** (via GitHub UI)

1. Go to [fredporter/uDOS-dev → Actions](https://github.com/fredporter/uDOS-dev/actions)
2. Click "Sync Public Mirror" workflow
3. Click "Run workflow"
4. Select branch: `main`
5. Click "Run workflow"

### Step 4: Verify Sync

1. Go to [fredporter/uDOS-core → Actions](https://github.com/fredporter/uDOS-core/actions)
2. Check for new workflow runs
3. Verify the pushed content appears in the public repo

---

## What Happens During Sync

### Workflow Steps

```mermaid
graph LR
    A["Push to private<br/>fredporter/uDOS-dev"] -->|trigger| B["sync-public.yml"]
    B -->|rsync| C["Prepare mirror/<br/>with /public, /core, /docs"]
    C -->|generate| D["README.md<br/>public-facing"]
    D -->|push -f| E["fredporter/uDOS-core<br/>main branch"]
    E -->|complete| F["✅ Synced"]
```

### Files Synced

1. **Source:** Private repo files
   - `public/` → Everything public-facing
   - `core/` → TypeScript runtime (excludes `__pycache__`, `*.pyc`, `node_modules`)
   - `docs/` → All documentation
   - `LICENSE*` → License files

2. **Generated:**
   - `README.md` → Auto-generated with links to docs and components
   - Git metadata removed (clean history)

3. **Destination:** Public repo (`main` branch)
   - Force push (overwrites public repo each time)
   - All history from private repo is NOT preserved
   - Public repo is just a mirror, not a full history

---

## Workflow File Reference

**Location:** `.github/workflows/sync-public.yml`

**Key sections:**

```yaml
on:
  push:
    branches: [main] # Trigger on main branch push
  workflow_dispatch: # Manual trigger available

env:
  PUBLIC_REPO: ${{ secrets.PUBLIC_REPO }} # Set in repo settings
  PUBLIC_TOKEN: ${{ secrets.PUBLIC_TOKEN }} # Set in repo settings


# Copy /public/, /core/, /docs/ to mirror/
# Generate README.md
# Force push to public repo
```

---

## Troubleshooting

### Workflow Doesn't Run

**Check:**

1. Is the workflow enabled? Go to Actions tab → "Sync Public Mirror" → Check "Status"
2. Did the push actually go to `main` branch?
   ```bash
   git branch -a
   git log --oneline -5
   ```

### Secrets Not Found Error

**In workflow logs, you might see:**

```
⚠️  Skipping sync: PUBLIC_REPO or PUBLIC_TOKEN not configured
```

**Fix:**

- Verify secrets are in repo settings (Settings → Secrets → Actions)
- Check secret names match exactly: `PUBLIC_REPO`, `PUBLIC_TOKEN`
- Wait 10-15 seconds after adding secrets (caching)

### Permission Denied on Push

**Error:**

```
fatal: could not read Password for 'https://github.com': No such file or directory
```

**Fix:**

- Ensure `PUBLIC_TOKEN` is a valid GitHub PAT
- Verify PAT has `repo` scope
- Check PAT hasn't expired

### Workflow Hangs

**Usually caused by:**

- Large files being synced (especially in `public/library/`)
- Network timeout

**Solution:**

- Exclude large files in `.github/workflows/sync-public.yml`
- Manually trigger again

---

## Manual Sync (If Workflow Fails)

If the automated workflow isn't working, sync manually:

```bash
#!/bin/bash
# Sync private repo content to public repo

PRIVATE_REPO="~/uDOS"
PUBLIC_REPO_URL="https://github.com/fredporter/uDOS-core.git"
PUBLIC_TOKEN="your_github_pat_here"
TEMP_DIR="/tmp/uDOS-core-sync"

# 1. Prepare mirror directory
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 2. Copy content
rsync -av --delete --exclude='.git' --exclude='.DS_Store' --exclude='node_modules' \
  "$PRIVATE_REPO/public/" "$TEMP_DIR/"

rsync -av --exclude='__pycache__' --exclude='*.pyc' --exclude='node_modules' \
  "$PRIVATE_REPO/core/" "$TEMP_DIR/core/"

rsync -av "$PRIVATE_REPO/docs/" "$TEMP_DIR/docs/"

cp "$PRIVATE_REPO/LICENSE"* "$TEMP_DIR/" 2>/dev/null || true

# 3. Generate README
cat > "$TEMP_DIR/README.md" << 'EOF'
# uDOS Core - Public Mirror
...
EOF

# 4. Push to public repo
cd "$TEMP_DIR"
git init
git config user.name "Your Name"
git add -A
git commit -m "Sync from private repo: public/, core/, docs/, LICENSE"
git remote add origin "https://x-access-token:${PUBLIC_TOKEN}@github.com/fredporter/uDOS-core.git"
git push -f origin main

echo "✅ Sync complete!"
```

Save as `bin/sync-public.sh` and run:

```bash
chmod +x bin/sync-public.sh
PUBLIC_TOKEN="your_pat_here" ./bin/sync-public.sh
```

---

## Security Notes

⚠️ **Important:**

1. **Never commit PAT to git** — Stored in GitHub Secrets only
2. **PAT scope: `repo` only** — Sufficient for public repo access
3. **PAT expiration** — Set to 90 days, will need renewal
4. **Rotate PAT periodically** — Delete old ones from GitHub Settings

---

## Next Steps

1. ✅ Create GitHub PAT (scope: `repo`)
2. ✅ Add `PUBLIC_REPO` secret: `fredporter/uDOS-core`
3. ✅ Add `PUBLIC_TOKEN` secret: (paste PAT)
4. ✅ Test sync by pushing to `main` or manual trigger
5. ✅ Verify content appears in `fredporter/uDOS-core`

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub PAT Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Sync Workflow](.github/workflows/sync-public.yml)
- [Public/Private Sync Plan](./public-private-sync.md)

---

_Last tested: 2026-01-18_  
_Workflow status: Configured (awaiting secrets)_
