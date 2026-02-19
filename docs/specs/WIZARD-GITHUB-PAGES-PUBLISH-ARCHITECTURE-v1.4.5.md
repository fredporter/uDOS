# Wizard GitHub Pages Web Publishing Architecture v1.4.5

**Status:** Specification (v1.4.5 dev round)
**Owner:** Wizard Server + uDOS Core
**Target Release:** 2026-04-30

---

## Vision

Replace the monorepo concept with a **user-controlled web publishing workflow** where uDOS users publish their vault, binders, and workspace content directly to **GitHub Pages** using **Jekyll** as the static site builder. This enables:

- **User Ownership:** Each user controls their own GitHub repo and domain
- **No Central Platform:** No uDOS-hosted monorepo or central hub
- **Jekyll Integration:** Leverage Jekyll for markdown rendering, site generation, theming
- **Persistent Sync:** GitHub Actions workflows auto-sync vault updates to published site
- **Standards-Based:** Uses GitHub-native APIs and Jekyll conventions

---

## Architecture

### Publishing Workflow

```
User Vault (local)
    ↓
Wizard `PUBLISH` command
    ↓
Validate + Stage (git clone user's GitHub repo)
    ↓
Prepare Jekyll Project (frontmatter → Jekyll content, assets)
    ↓
Push to GitHub (user's repo, dedicated branch: `gh-pages-content`)
    ↓
GitHub Actions (Jekyll build)
    ↓
GitHub Pages (user's domain: `username.github.io` or custom domain)
```

### Key Components

#### 1. User GitHub Repo Setup (One-Time)

**Prerequisites:**
- User GitHub account (free tier sufficient)
- Public repo for vault content: `{username}/vault-publish` (or custom name)
- GitHub Pages enabled (settings → Pages → Source: GitHub Actions)
- Personal Access Token (PAT) saved in Wizard secrets

**Wizard Setup Flow:**
```
WIZARD github setup
    → Prompt GitHub username
    → Prompt repo name (default: `vault-publish`)
    → Prompt custom domain (optional: example.com, or {username}.github.io)
    → Generate Jekyll config template
    → Create local git remote in Wizard
    → Store GitHub PAT in encrypted `wizard/secrets/` config
    → Validate repo access (test push to throwaway branch)
```

#### 2. Jekyll Site Template

Wizard provides a minimal Jekyll site template at `distribution/jekyll-site-template/`:

```
jekyll-site-template/
    _config.yml              # Jekyll config (title, baseurl, theme)
    GemFile                  # Ruby dependencies (jekyll, plugins)
    .github/workflows/
        build.yml            # Automated Jekyll build + GitHub Pages deploy
    assets/
        css/
            style.css        # Base theme stylesheet
        js/
            search.js        # Client-side vault search
    _layouts/
        default.html         # Base layout
        vault.html           # Vault index layout
        binder.html          # Binder layout
        page.html            # Generic content page
    _includes/
        nav.html             # Navigation sidebar
        toc.html             # Table of contents
        footer.html          # Footer
        search-box.html      # Search box
    .gitignore               # Exclude Gemfile.lock, _site/, etc.
```

#### 3. Content Staging Pipeline

When user runs `PUBLISH --github`:

1. **Clone Repo:** Wizard clones user's GitHub repo (branch: `main`)
2. **Prepare Content:**
   - Walk vault file tree (`memory/vault/`, `memory/binders/`, etc.)
   - Extract frontmatter from `.md` files
   - Convert uDOS-specific blocks (grid maps, diagrams) to Jekyll-compatible Markdown
   - Copy media assets to Jekyll `assets/` folder
3. **Generate Index:**
   - Build vault index page (`index.md`) with binder/workspace TOC
   - Generate search index JSON for client-side search
4. **Commit + Push:**
   - Add content to git: `git add .`
   - Commit: `git commit -m "Published vault at $(date)"`
   - Push to `main`: `git push origin main`
5. **GitHub Actions Trigger:**
   - GitHub Actions detects push
   - Runs Jekyll build workflow
   - Deploys to GitHub Pages
   - User's site live at `{username}.github.io` (or custom domain)

#### 4. GitHub Actions Workflow (`.github/workflows/build.yml`)

```yaml
name: Jekyll Build & Deploy

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      # Checkout repo
      - uses: actions/checkout@v4

      # Setup Ruby + Jekyll
      - uses: ruby/setup-ruby@v1
        with:
          ruby-version: 3.2
          bundler-cache: true

      # Build site
      - name: Build with Jekyll
        run: bundle exec jekyll build

      # Upload artifact
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: _site

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

#### 5. Syncing Updates

**Soft Sync Mode** (Default):
- User publishes vault updates locally via `PUBLISH --github --soft`
- Wizard stages changes, commits, pushes to `main`
- GitHub Actions auto-builds and deploys
- Next sync picks up new changes

**Hard Sync Mode** (Reset):
- `PUBLISH --github --hard` clears remote, re-uploads entire vault
- Useful if remote state corrupted or user wants fresh start

**Continuous Integration** (Optional):
- Set ZenHub/GitHub Issues integration to auto-publish on release/milestone
- Trigger via GitHub Actions webhook

#### 6. Content Type Support

| Content Type | Handling | Jekyll Support |
|--------------|----------|---|
| Markdown (`.md`) | Native, extracted frontmatter | ✅ Full |
| Binders | Index page + nested content | ✅ Full |
| Grid Maps | ASCII render + image fallback | ✅ Markdown block |
| Diagrams (Mermaid) | Embed as iframe or image | ⚠️ Plugin required |
| Images/Media | Copy to `assets/`, rewrite paths | ✅ Full |
| Code Snippets | Syntax highlight via Jekyll | ✅ Full (Rouge) |
| Obsidian Vault Links (`[[]]`) | Convert to relative links | ✅ Post-process |
| YAML Frontmatter | Parsed → Jekyll default | ✅ Full |
| Custom Schemas | Render as JSON-LD metadata | ⚠️ Manual theme |

---

## Deprecation: Monorepo Concept

### Old Approach (Pre-v1.4.5)
- Central uDOS monorepo `/releases/` folder
- Centralized publish provider
- Users depend on uDOS infrastructure

### New Approach (v1.4.5+)
- **No monorepo:** Each user owns their GitHub repo
- **Decentralized:** GitHub Pages + Jekyll as standard
- **User-controlled:** Users manage domain, theme, sync
- **Standards-based:** Leverage GitHub/Jekyll ecosystem

### Migration Path

1. **Existing monorepo users:**
   - `PUBLISH --export` exports vault to local Jekyll dir
   - User creates GitHub repo from template
   - `PUBLISH --github --import` migrates existing content
   - Old monorepo folder deprecated (archive, mark readonly)

2. **New users:**
   - `WIZARD github setup` guides full GitHub + Jekyll setup
   - Direct publish to user's repo, no intermediate steps

3. **Backward Compatibility:**
   - Legacy monorepo routes return deprecation warning
   - Monorepo provider remains but is hidden from UI default
   - Timeline: Phase out by v1.5.0

---

## Wizard GUI Integration

### New Dashboard Panels

#### Publish Panel (`#/publish`)
```
┌─ Publish Status ─────────────────────┐
│ GitHub Repo:     vault-publish       │
│ GitHub Pages:    example.github.io   │
│ Last Sync:       2026-02-20 14:30    │
│ Sync Status:     ✅ OK (3 items)     │
│                                      │
│ [🔄 Sync Now]  [⚙ Settings]         │
└──────────────────────────────────────┘
```

#### GitHub Setup Panel (`#/publish/github`)
```
┌─ GitHub Setup ───────────────────────┐
│ Status: ❌ Not Configured            │
│                                      │
│ GitHub Username:                     │
│ [________________]                   │
│                                      │
│ Repo Name:                           │
│ [vault-publish_____________]         │
│                                      │
│ GitHub Pages URL:                    │
│ https://example.github.io            │
│ [________________]                   │
│                                      │
│ Personal Access Token (readonly):    │
│ ●●●●●●●●●●●● (configured)           │
│                                      │
│ [🔗 Connect GitHub]  [Test]          │
└──────────────────────────────────────┘
```

#### Sync History Panel
```
┌─ Recent Syncs ───────────────────────┐
│ 2026-02-20 14:30  ✅  3 items        │
│ 2026-02-20 13:00  ✅  5 items        │
│ 2026-02-20 10:30  ⚠️  Partial (1 err)│
│ 2026-02-19 22:00  ✅  12 items       │
│                                      │
│ [View Log]  [Clear History]          │
└──────────────────────────────────────┘
```

### New uCLI Commands

```bash
# GitHub Setup
WIZARD github setup              # Interactive GitHub config
WIZARD github status             # Check GitHub integration status
WIZARD github validate           # Test repo access + PAT

# Publishing
PUBLISH --github                 # Soft sync to GitHub Pages
PUBLISH --github --hard          # Hard reset (full re-upload)
PUBLISH --github --export        # Export to local Jekyll dir (no push)
PUBLISH --github --list          # List recent syncs
PUBLISH --github --view          # Open published site in browser

# Configuration
PUBLISH --config github          # Edit GitHub settings
PUBLISH --config jekyll          # Edit Jekyll theme config
```

---

## Config Schema

### `wizard/config/github-publish.json`

```json
{
  "enabled": true,
  "github": {
    "username": "fredbook",
    "repo_name": "vault-publish",
    "repo_url": "https://github.com/fredbook/vault-publish",
    "branch": "main",
    "pat_secret_key": "github_pat_xxxx",
    "pages_url": "https://example.github.io"
  },
  "jekyll": {
    "site_title": "Fred's Vault",
    "site_tagline": "A knowledge garden",
    "theme": "minima",
    "base_url": "",
    "include_search": true,
    "include_toc": true
  },
  "sync": {
    "mode": "soft",
    "auto_commit_message": "Published vault at {timestamp}",
    "include_patterns": [
      "**/*.md",
      "media/**/*"
    ],
    "exclude_patterns": [
      "**/.DS_Store",
      "**/__pycache__/**",
      ".obsidian/**"
    ]
  },
  "last_sync": {
    "timestamp": "2026-02-20T14:30:00Z",
    "items_synced": 42,
    "status": "success",
    "commit_hash": "abc123def456"
  }
}
```

### `distribution/jekyll-site-template/_config.yml`

```yaml
# Jekyll Site Config
title: "Fred's Vault"
tagline: "A knowledge garden"
description: "Personal vault and workspace content"
author:
  name: Fred Book
  email: user@example.com

# Pages Config
pages_url: "https://example.github.io"
baseurl: ""

# Theme
theme: minima
plugins:
  - jekyll-feed
  - jekyll-seo-tag
  - jekyll-gist

# Vault-specific
vault:
  include_search: true
  include_toc: true
  search_placeholder: "Search vault..."

# Markdown
markdown: kramdown
highlighter: rouge

# Permalinks
permalink: /:categories/:year/:month/:day/:title/
```

---

## Implementation Strategy

### Phase 1: GitHub Setup & Config (Week 1-2)
- [ ] Implement `WIZARD github setup` interactive flow
- [ ] Create GitHub PAT storage + validation
- [ ] Add GitHub repo clone/access tests
- [ ] Wire GitHub UI panels in dashboard

### Phase 2: Content Staging & Conversion (Week 3-4)
- [ ] Implement vault → Jekyll markdown conversion
- [ ] Build Jekyll site template (`distribution/jekyll-site-template/`)
- [ ] Create git commit + push logic
- [ ] Implement sync history tracking

### Phase 3: GitHub Actions Integration (Week 5)
- [ ] Create `.github/workflows/build.yml` template
- [ ] Test Jekyll build via GitHub Actions
- [ ] Verify GitHub Pages deployment
- [ ] Add rollback mechanism for failed builds

### Phase 4: Wizard GUI Integration (Week 6)
- [ ] Implement publish status panel
- [ ] Implement GitHub setup panel
- [ ] Add sync history / monitoring
- [ ] Wire `PUBLISH --github` uCLI command

### Phase 5: Testing & Documentation (Week 7)
- [ ] E2E tests: setup → sync → pages
- [ ] Performance tests: large vault sync
- [ ] Documentation: user guide + troubleshooting
- [ ] Migration guide for monorepo users

---

## Success Criteria

- ✅ Any uDOS user can publish vault to GitHub Pages in <5 minutes (setup + first sync)
- ✅ Soft sync latency <30 seconds for typical vault (50-100 files)
- ✅ Synced content renders correctly on GitHub Pages (90%+ test coverage)
- ✅ GitHub Actions workflow is reliable (>99% success rate)
- ✅ User can customize Jekyll theme without Wizard intervention
- ✅ User can own/control domain (custom domain or `{username}.github.io`)
- ✅ All existing monorepo functionality migrated or deprecated

---

## Edge Cases & Mitigation

| Case | Mitigation |
|------|-----------|
| **User loses GitHub PAT** | WIZARD validates before push; prompt for re-auth if expired |
| **GitHub Pages build fails** | GitHub Actions sends error email; Wizard checks build status + surfaces error in dashboard |
| **Large vault (>5000 files)** | Implement chunked sync; show progress bar; allow partial sync |
| **Merge conflicts** | Implement conflict resolution UI; pull before push; handle CONFLICT status |
| **Custom domain setup** | Provide step-by-step CNAME guide in setup flow |
| **Jekyll theme conflicts** | Ship minimal theme by default; document theme customization |
| **Obsidian vault links** | Post-process markdown to convert `[[file]]` → relative links |

---

## References

- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [Jekyll Official Docs](https://jekyllrb.com/)
- [Jekyll Remote Theme Plugin](https://github.com/benbalter/jekyll-remote-theme)
- [GitHub Actions for Pages](https://github.com/actions/deploy-pages)
