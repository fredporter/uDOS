# CI/CD Pipeline Documentation

**Version:** 1.0.0  
**Component:** Wizard Server  
**Date:** 2026-01-14

---

## Overview

The uDOS CI/CD pipeline automates build orchestration, testing, releases, and artifact distribution using GitHub Actions workflows orchestrated by the Wizard Server.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Wizard Server TUI                         │
│  Commands: BUILD, TEST, RELEASE, ARTIFACTS, GITHUB           │
└──────────────┬───────────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────────┐
│                      CICDManager                             │
│  • Build orchestration                                       │
│  • Test execution                                            │
│  • Release management                                        │
│  • Artifact management                                       │
└──────────────┬───────────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────────┐
│                   WorkflowRunner                             │
│  • Trigger GitHub Actions workflows                          │
│  • Monitor workflow status                                   │
│  • Download artifacts                                        │
└──────────────┬───────────────────────────────────────────────┘
               │
               ↓
┌──────────────────────────────────────────────────────────────┐
│                  GitHub Actions                              │
│  • test.yml        - Test suite execution                    │
│  • build-core.yml  - Core package build                      │
│  • build-app.yml   - App (Tauri) build                       │
│  • build-wizard.yml - Wizard package build                   │
│  • build-api.yml   - API extension build                     │
│  • build-transport.yml - Transport extension build           │
│  • build-all.yml   - Build all components                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. CICDManager

Located: `wizard/github_integration/cicd_manager.py`

**Responsibilities:**
- Build orchestration for all components (Core, App, Wizard, API, Transport)
- Test suite execution
- Release creation and artifact publishing
- Build artifact management and storage

**Key Methods:**
- `build(target, branch, wait)` - Trigger build for target
- `build_all(branch)` - Build all components
- `run_tests(target, branch)` - Execute test suite
- `create_release(version, build_id)` - Create GitHub release
- `list_artifacts(build_id)` - List build artifacts
- `export_state(filepath)` - Export CI/CD state
- `import_state(filepath)` - Import CI/CD state

### 2. GitHub Actions Workflows

Located: `.github/workflows/`

#### Test Workflow (`test.yml`)

**Triggers:**
- Manual dispatch with target selection
- Push to main/develop branches
- Pull requests to main/develop

**Jobs:**
- `test-core` - Core Python tests with coverage
- `test-wizard` - Wizard Server tests
- `test-api` - API extension tests
- `test-app` - App (Tauri/Svelte) tests

**Outputs:**
- Test results with coverage reports
- Codecov integration

#### Build Workflows

Each component has its own build workflow:

**build-core.yml:**
- Python package building
- Tarball creation with version
- Artifact upload (retention: 30 days)

**build-app.yml:**
- Tauri DMG build (macOS)
- App bundle creation
- Code signing (with secrets)

**build-wizard.yml:**
- Wizard Server package
- Tarball with dependencies

**build-api.yml / build-transport.yml:**
- Extension package builds
- Version-tagged tarballs

**build-all.yml:**
- Orchestrates all builds
- Parallel execution
- Unified status summary

### 3. Wizard TUI Commands

Located: `wizard/wizard_tui.py`

**Available Commands:**

```
BUILD <target> [branch]   - Trigger build
  Targets: core, app, wizard, api, transport, all
  Example: BUILD core main
           BUILD all develop

TEST <target> [branch]    - Run test suite
  Targets: core, app, wizard, api, all
  Example: TEST all
           TEST core main

RELEASE <version> [build] - Create release
  Example: RELEASE v1.0.2.0
           RELEASE v1.0.2.0 20260114_120000

ARTIFACTS <command>       - Manage artifacts
  Commands: LIST          - List all artifacts
            INFO <id>     - Show build info
  Example: ARTIFACTS LIST
           ARTIFACTS INFO 20260114_120000

GITHUB <command>          - GitHub integration
  Commands: STATUS        - Connection status
            REPOS         - List repositories
            WORKFLOWS     - List workflows
  Example: GITHUB STATUS
```

---

## Usage

### 1. Build a Component

```bash
# Start Wizard TUI
./wizard/launch_wizard_tui.sh

# Trigger build
BUILD core main
```

**Output:**
```
🏗️ Building core from main...

✅ Build triggered: 20260114_120000
Target: core
Branch: main
Workflow Run ID: 12345678
Status: running

Check status with: ARTIFACTS LIST
```

### 2. Run Tests

```bash
# Run all tests
TEST all

# Run specific component tests
TEST core main
```

**Output:**
```
🧪 Running tests for all...

✅ Tests started: 20260114_120100
Target: all
Branch: main
Workflow Run ID: 12345679
Status: running
```

### 3. List Artifacts

```bash
ARTIFACTS LIST
```

**Output:**
```
📦 BUILD ARTIFACTS

Build ID         Artifact                  Size       Created
───────────────  ────────────────────────  ─────────  ──────────
20260114_120000  core-v1.1.0.0.tar.gz       2.34 MB  2026-01-14
20260114_115900  app-v1.0.3.0-macos.dmg    45.67 MB  2026-01-14
20260114_115800  wizard-v1.1.0.0.tar.gz     1.56 MB  2026-01-14
```

### 4. Check Build Info

```bash
ARTIFACTS INFO 20260114_120000
```

**Output:**
```
🏗️  BUILD INFO: 20260114_120000

Target: core
Branch: main
Status: success
Started: 2026-01-14T12:00:00
Completed: 2026-01-14T12:02:30

Artifacts:
  - core-v1.1.0.0.tar.gz
```

### 5. Create Release

```bash
# Create draft release
RELEASE v1.0.2.0 20260114_120000
```

**Output:**
```
📦 Creating release v1.0.2.0...

✅ Release created: v1.0.2.0
Release ID: 12345
Tag: v1.0.2.0
URL: https://github.com/fredpook/uDOS/releases/v1.0.2.0
Status: Draft (publish when ready)
```

### 6. Check GitHub Status

```bash
GITHUB STATUS
```

**Output:**
```
🐙 GITHUB STATUS

User: fredpook
Name: Fred Porter
Token: ✅ Valid
Rate Limit: 4850/5000
```

---

## Programmatic Usage

### Python API

```python
from wizard.github_integration.cicd_manager import CICDManager, BuildTarget
from wizard.github_integration.client import GitHubClient

# Initialize
client = GitHubClient(token="ghp_xxxx")
cicd = CICDManager(client, "fredpook", "uDOS")

# Trigger build
result = cicd.build(BuildTarget.CORE, branch="main", wait=True)
print(f"Build status: {result['status']}")

# Run tests
test_result = cicd.run_tests(BuildTarget.ALL, wait=True)
print(f"Tests: {test_result['tests_passed']} passed, {test_result['tests_failed']} failed")

# Create release
release = cicd.create_release("v1.0.2.0", draft=True)
print(f"Release URL: {release['url']}")

# List artifacts
artifacts = cicd.list_artifacts()
for artifact in artifacts:
    print(f"{artifact['name']} - {artifact['size'] / (1024*1024):.2f} MB")
```

---

## Configuration

### Environment Variables

```bash
# GitHub token (required)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Optional configuration
export GITHUB_OWNER="fredpook"
export GITHUB_REPO="uDOS"
export ARTIFACTS_DIR="distribution/builds"
```

### Secrets (GitHub Actions)

Required secrets in repository settings:

```
GITHUB_TOKEN          - GitHub API token
TAURI_PRIVATE_KEY     - Tauri code signing key (for app builds)
TAURI_KEY_PASSWORD    - Tauri key password
CODECOV_TOKEN         - Codecov API token (optional)
```

---

## Build Artifacts

### Storage

Artifacts are stored in:
```
distribution/builds/
  ├── 20260114_120000/
  │   ├── core-v1.1.0.0.tar.gz
  │   └── core-v1.1.0.0-py3-none-any.whl
  ├── 20260114_120100/
  │   ├── app-v1.0.3.0-macos.dmg
  │   └── app-v1.0.3.0-macos.app.tar.gz
  └── ...
```

### Naming Convention

```
{component}-v{version}.{extension}

Examples:
- core-v1.1.0.0.tar.gz
- app-v1.0.3.0-macos.dmg
- wizard-v1.1.0.0.tar.gz
- api-v1.1.0.0.tar.gz
- transport-v1.0.1.0.tar.gz
```

### Retention

- GitHub Actions artifacts: 30 days
- Local artifacts: Unlimited (manual cleanup)

---

## Testing

### Test Suite

Located: `wizard/github_integration/test_cicd_manager.py`

**Coverage:**
- 27 comprehensive tests
- 100% pass rate
- All major functionality covered

**Test Categories:**
1. Initialization (4 tests)
2. Build orchestration (8 tests)
3. Test execution (3 tests)
4. Release creation (3 tests)
5. Artifact management (4 tests)
6. Utilities (3 tests)
7. State management (2 tests)

**Run Tests:**
```bash
pytest wizard/github_integration/test_cicd_manager.py -v
```

---

## Error Handling

### Common Issues

**1. GitHub Token Invalid**
```
❌ GitHub connection failed: Unauthorized
```
**Solution:** Check `GITHUB_TOKEN` environment variable

**2. Workflow Trigger Failed**
```
❌ Build failed: Failed to trigger workflow
```
**Solution:** Verify workflow file exists and is enabled

**3. Build Not Found**
```
❌ Build not found: 20260114_120000
```
**Solution:** Check build ID with `ARTIFACTS LIST`

**4. Rate Limit Exceeded**
```
❌ GitHub API rate limit exceeded
```
**Solution:** Wait for rate limit reset or use authenticated token

---

## Monitoring

### Build Status

Check build status via:
1. Wizard TUI: `ARTIFACTS INFO <build_id>`
2. GitHub Actions UI: https://github.com/{owner}/{repo}/actions
3. Programmatic: `cicd.get_build_status(build_id)`

### Logs

- GitHub Actions logs: Available in workflow run
- Local logs: `memory/logs/wizard-server-YYYY-MM-DD.log`
- CI/CD events logged with `[WIZ]` tag

---

## Best Practices

### 1. Build Management

- Always specify branch explicitly
- Use `wait=False` for long builds
- Check artifacts before creating releases

### 2. Testing

- Run tests before merging to main
- Use specific targets for faster feedback
- Review coverage reports

### 3. Releases

- Create draft releases first
- Verify artifacts before publishing
- Use semantic versioning

### 4. Artifact Cleanup

- Remove old artifacts periodically
- Keep successful release artifacts
- Use `cicd.export_state()` for backups

---

## Troubleshooting

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### State Export/Import

Backup CI/CD state:
```python
cicd.export_state(Path("cicd-state-backup.json"))
cicd.import_state(Path("cicd-state-backup.json"))
```

### Workflow Debugging

Check workflow status:
```bash
GITHUB STATUS
```

View workflow runs:
```bash
# Via GitHub CLI
gh run list --repo fredpook/uDOS

# View specific run
gh run view <run_id> --repo fredpook/uDOS
```

---

## Future Enhancements

- Automated versioning based on git tags
- Multi-platform builds (Linux, Windows)
- Container image builds
- Automated changelog generation
- Deployment automation
- Performance metrics tracking

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Tauri Build Documentation](https://tauri.app/v1/guides/building/)
- [uDOS Roadmap](../docs/roadmap.md)
- [Wizard Server Documentation](README.md)

---

*Last Updated: 2026-01-14*  
*Version: 1.0.0*
