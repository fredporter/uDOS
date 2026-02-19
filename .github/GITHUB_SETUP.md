# GitHub Repository Setup Guide

Guide for setting up Projects, Issues, Pull Requests, and GitHub Wiki wiring on the uDOS public repository.

---

## GitHub Templates

✅ **Already Configured:**

The repository includes:

### Issue Templates
- **Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.md`)
- **Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.md`)
- **Documentation** (`.github/ISSUE_TEMPLATE/documentation.md`)
- **Question** (`.github/ISSUE_TEMPLATE/question.md`)

### Pull Request Template
- **PR Template** (`.github/PULL_REQUEST_TEMPLATE.md`)

### Issue Template Routing
- **Template config/contact links** (`.github/ISSUE_TEMPLATE/config.yml`)

---

## GitHub Wiki Wiring

The repository wiki pages should map to files under `wiki/`:

- `wiki/Home.md` -> Wiki Home
- `wiki/_Sidebar.md` -> left navigation
- `wiki/_Footer.md` -> footer links
- `wiki/README.md` -> local wiki source index

Canonical wiki/spec references:

- `docs/specs/wiki_spec_obsidian.md`
- `docs/specs/README.md`
- `docs/roadmap.md`

---

## Setting Up GitHub Projects

### Option 1: Project Board (Classic)

1. Go to your repository on GitHub
2. Click the **Projects** tab
3. Click **New project**
4. Choose **Board** layout
5. Name it: **uDOS v1.4.3 Development**

**Columns to create:**
- 📋 **Backlog** — Ideas and future work
- 🔜 **To Do** — Ready to work on
- 🚧 **In Progress** — Currently being worked on
- 👀 **Review** — Pending review/testing
- ✅ **Done** — Completed

### Option 2: Projects (Beta/New)

GitHub's new Projects interface offers more flexibility:

1. Go to **Projects** tab
2. Click **New project**
3. Choose **Table** or **Board** view
4. Name it: **uDOS Roadmap**

**Suggested fields:**
- Status (Backlog, Ready, In Progress, Review, Done)
- Priority (Low, Medium, High, Critical)
- Module (Core, Wizard, Dev, Docs)
- Size (Small, Medium, Large)

---

## Organizing Issues

### Labels

Create/use these labels:

**Type:**
- `bug` — Something isn't working
- `enhancement` — New feature or request
- `documentation` — Documentation improvements
- `question` — Further information is requested

**Module:**
- `core` — Core TUI/commands
- `wizard` — Wizard services
- `dev` — Development tools
- `wiki` — Wiki documentation

**Priority:**
- `critical` — Needs immediate attention
- `high` — Important
- `medium` — Normal priority
- `low` — Nice to have

**Status:**
- `good first issue` — Good for newcomers
- `help wanted` — Extra attention needed
- `wontfix` — Will not be worked on
- `duplicate` — Duplicate issue

### Milestones

Create milestones for releases:

- **v1.4.3** — Current stable release
- **v1.5.0** — Next minor release
- **v2.0.0** — Future major release

---

## Issue Management Workflow

### 1. New Issue Created

When someone opens an issue:

1. **Review** the issue description
2. **Add labels** (type, module, priority)
3. **Add to project** if actionable
4. **Respond** to clarify or acknowledge
5. **Assign milestone** if planned

### 2. Working on Issue

When starting work:

1. **Assign** yourself to the issue
2. Move to **In Progress** in project
3. **Create branch**: `git checkout -b fix/issue-123` or `feature/issue-123`
4. **Reference issue** in commits: `fix: Resolve issue #123`

### 3. Completing Issue

When work is done:

1. **Create Pull Request** referencing issue: `Fixes #123`
2. Move to **Review** in project
3. Wait for review and merge
4. Issue automatically closes on merge

---

## Pull Request Workflow

### 1. Creating a PR

Contributors should:

1. Fork the repository
2. Create a feature branch
3. Make changes following [Contribution Process](../docs/CONTRIBUTION-PROCESS.md)
4. Push to their fork
5. Open PR using the template

### 2. Reviewing PRs

Maintainers should:

1. **Review code** for quality and style
2. **Check tests** pass
3. **Test manually** if needed
4. **Request changes** or **Approve**
5. **Merge** when ready

### 3. PR Checklist

Before merging, ensure:

- [ ] Code follows style guide
- [ ] Module boundaries respected
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings/errors
- [ ] Tested on relevant platforms

---

## Automation Ideas

### GitHub Actions

Consider adding workflows for:

1. **Automated Testing**
   ```yaml
   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
         - run: pip install -r requirements.txt
         - run: pytest
   ```

2. **Linting**
   ```yaml
   name: Lint
   on: [push, pull_request]
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - uses: actions/setup-python@v2
         - run: pip install black flake8
         - run: black --check .
         - run: flake8 .
   ```

3. **Auto-label Issues**
   Use GitHub's built-in labeler action

4. **Stale Issue Management**
   Close issues inactive for X days

---

## Community Guidelines

Point contributors to:

- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) — Community standards
- [CONTRIBUTORS.md](CONTRIBUTORS.md) — Contributor list
- [wiki/Contributors.md](wiki/Contributors.md) — How to contribute
- [privacy.md](privacy.md) — Privacy policy
- [disclaimer.md](disclaimer.md) — Usage disclaimer

---

## GitHub Repository Settings

### Recommended Settings

**General:**
- ✅ Enable issues
- ✅ Enable projects
- ✅ Enable wiki (if using GitHub wiki)
- ✅ Enable discussions (optional)

**Branches:**
- Set `main` as default branch
- Enable branch protection:
  - Require pull request reviews
  - Require status checks to pass
  - Require branches to be up to date

**Merge Options:**
- ✅ Allow squash merging (recommended)
- ⚠️ Allow merge commits (optional)
- ⚠️ Allow rebase merging (optional)

---

## Quick Setup Checklist

- [x] Issue templates created
- [x] PR template created
- [x] Code of Conduct added
- [x] Contributors guide added
- [ ] Create GitHub Project board
- [ ] Add labels to repository
- [ ] Create milestones
- [ ] Configure branch protection
- [ ] Set up GitHub Actions (optional)
- [ ] Enable discussions (optional)

---

## Resources

- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [Managing Issues](https://docs.github.com/en/issues/tracking-your-work-with-issues)
- [About Pull Requests](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Next Steps:**

1. Go to GitHub repository settings
2. Create a new Project board
3. Add labels for organization
4. Create v1.4.3 milestone (or next target)
5. Start organizing existing issues!
