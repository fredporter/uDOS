# uDOS Scripts

Repository maintenance and development scripts.

## Available Scripts

### `deploy_wiki.sh`
Deploys wiki content from `/wiki` to the GitHub wiki repository.

**Usage:**
```bash
./memory/scripts/deploy_wiki.sh ["Commit message"]
```

**What it does:**
1. Clones/updates the `uDOS.wiki` repository
2. Copies all `.md` files from `wiki/` to `uDOS.wiki/`
3. Commits and pushes changes to GitHub

**Example:**
```bash
./memory/scripts/deploy_wiki.sh "Add Style Guide to wiki"
```

---

## Adding New Scripts

Place maintainer/developer scripts here that:
- Are version controlled (committed to repo)
- Are used for repository maintenance
- Are shared across developers
- Are not session-specific or user-specific

For user/session-specific scripts, use `/sandbox/`.
