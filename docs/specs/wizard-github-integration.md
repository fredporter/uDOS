# Wizard GitHub Integration Specification

**Version:** 1.0  
**Status:** Specification  
**Date:** 2026-01-14  
**Scope:** Wizard Server GitHub APIs, Repository Sync, CI/CD Integration

---

## Overview

Wizard Server acts as the **orchestration hub** for:

1. **Repository Synchronization** — Clone/pull integrated repos, library repos
2. **CI/CD Workflows** — Run GitHub Actions, publish releases
3. **Plugin Discovery** — Fetch plugin metadata from GitHub
4. **Release Management** — Tag releases, create GitHub Releases, publish artifacts

This specification defines the interface and behavior.

---

## Architecture

```
GitHub.com
    │
    └─── Wizard GitHub Integration
            ├── Client (REST API wrapper)
            ├── Repo Sync (clone/pull)
            ├── Workflow Runner (Actions execution)
            ├── Release Manager (tagging + publishing)
            └── Webhook Handler (push/release events)
            
         Wizard Services
            ├── Plugin Manager (discover plugins)
            ├── Dev Studio (build pipeline)
            └── Plugin Installer (enable/disable)
            
         Local Filesystem
            ├── /library/ucode-integrated/
            ├── /library/wizard-workspace/
            ├── /plugins/
            └── /packages/
```

---

## 1. GitHub Client

### Purpose

Wrapper around GitHub REST API v3 + GraphQL for:
- Repository operations
- Workflow management
- Release publishing
- User/org data

### Location

```python
# wizard/github_integration/client.py
from wizard.github_integration import GitHubClient

client = GitHubClient(token="ghp_xxx", owner="uDOS")
```

### API

#### Repository Operations

```python
class GitHubClient:
    # Clone a repository
    def clone_repo(
        self,
        owner: str,
        repo: str,
        destination: Path,
        ref: str = "main"
    ) -> bool:
        """
        Clone repository to destination.
        
        Args:
            owner: GitHub org/user
            repo: Repository name
            destination: Local path
            ref: Branch/tag/commit (default: main)
        
        Returns:
            True if successful
        
        Raises:
            GitHubError: Network or auth error
            PathError: Destination invalid
        """
        pass
    
    # Pull updates from remote
    def pull_repo(self, local_path: Path) -> bool:
        """
        Pull latest changes from remote.
        
        Assumes git is installed and local_path is a git repo.
        """
        pass
    
    # Check if repo exists
    def repo_exists(self, owner: str, repo: str) -> bool:
        pass
    
    # Get repository metadata
    def get_repo(self, owner: str, repo: str) -> dict:
        """
        Returns:
            {
                "name": "uDOS",
                "full_name": "user/uDOS",
                "description": "...",
                "url": "https://github.com/user/uDOS",
                "default_branch": "main",
                "pushed_at": "2026-01-14T...",
                "size": 12345,
                "stars": 42,
                "topics": ["offline-first", "tinycore"]
            }
        """
        pass
```

#### Workflow Management

```python
    # List workflows in repo
    def list_workflows(self, owner: str, repo: str) -> list:
        """
        Returns:
            [
                {
                    "id": 123,
                    "name": "Tests",
                    "path": ".github/workflows/tests.yml",
                    "state": "active"
                },
                ...
            ]
        """
        pass
    
    # Run a workflow
    def run_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: dict = None
    ) -> str:
        """
        Trigger workflow execution.
        
        Args:
            owner: GitHub org
            repo: Repository
            workflow_id: Workflow name or ID
            ref: Branch/tag to run on
            inputs: Workflow input variables
        
        Returns:
            run_id (for polling)
        
        Raises:
            GitHubError: Workflow not found or cannot run
        """
        pass
    
    # Check workflow run status
    def get_workflow_run(
        self,
        owner: str,
        repo: str,
        run_id: str
    ) -> dict:
        """
        Returns:
            {
                "id": run_id,
                "status": "queued|in_progress|completed",
                "conclusion": "success|failure|neutral|cancelled",
                "created_at": "...",
                "updated_at": "...",
                "artifacts_url": "..."
            }
        """
        pass
    
    # Download workflow artifacts
    def download_artifacts(
        self,
        owner: str,
        repo: str,
        run_id: str,
        destination: Path
    ) -> bool:
        """
        Download all artifacts from a workflow run.
        """
        pass
```

#### Release Management

```python
    # Create a release
    def create_release(
        self,
        owner: str,
        repo: str,
        tag: str,
        name: str = None,
        body: str = None,
        draft: bool = False,
        prerelease: bool = False
    ) -> dict:
        """
        Create a GitHub Release.
        
        Args:
            owner: GitHub org
            repo: Repository
            tag: Git tag (will be created if doesn't exist)
            name: Release name (defaults to tag)
            body: Release notes (markdown)
            draft: If true, release is draft
            prerelease: If true, marked as pre-release
        
        Returns:
            {
                "id": 12345,
                "tag_name": "v1.1.0",
                "name": "Release 1.1.0",
                "url": "https://github.com/.../releases/tag/v1.1.0",
                "upload_url": "https://uploads.github.com/...",
                "assets": []
            }
        """
        pass
    
    # Upload asset to release
    def upload_release_asset(
        self,
        upload_url: str,
        file_path: Path,
        content_type: str = "application/octet-stream"
    ) -> dict:
        """
        Upload a file (TCZ, ISO, binary, etc.) to release.
        
        Args:
            upload_url: From create_release()
            file_path: Local file to upload
            content_type: MIME type
        
        Returns:
            {
                "id": asset_id,
                "name": "uDOS-v1.1.0.tcz",
                "size": 1234567,
                "download_url": "https://..."
            }
        """
        pass
    
    # List releases
    def list_releases(
        self,
        owner: str,
        repo: str,
        prerelease: bool = None
    ) -> list:
        """
        Returns list of releases.
        """
        pass
    
    # Get latest release
    def get_latest_release(self, owner: str, repo: str) -> dict:
        pass
```

#### File Operations

```python
    # Get file contents
    def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str = "main"
    ) -> str:
        """
        Read a file from GitHub.
        """
        pass
    
    # Get repository tree (file listing)
    def get_tree(
        self,
        owner: str,
        repo: str,
        ref: str = "main",
        recursive: bool = False
    ) -> list:
        """
        Returns file tree.
        """
        pass
```

#### Searching & Listing

```python
    # List repositories
    def list_repositories(
        self,
        owner: str,
        per_page: int = 30,
        page: int = 1
    ) -> list:
        """
        List repos in org/user.
        """
        pass
    
    # Search repositories
    def search_repositories(
        self,
        query: str,
        language: str = None,
        sort: str = "stars"
    ) -> list:
        """
        Search GitHub for repositories.
        """
        pass
```

### Configuration

```yaml
# wizard/config/github.yaml
github:
  # Required
  token: ${GITHUB_TOKEN}  # Environment variable
  owner: "uDOS"
  
  # Optional
  base_url: "https://api.github.com"
  timeout: 30
  retry_attempts: 3
  
  # Proxy (for corporate networks)
  proxy: null
```

### Error Handling

```python
class GitHubError(Exception):
    """Base GitHub error"""
    pass

class GitHubAuthError(GitHubError):
    """Invalid token or credentials"""
    pass

class GitHubNotFoundError(GitHubError):
    """Repo/workflow/file not found"""
    pass

class GitHubRateLimitError(GitHubError):
    """Rate limit exceeded"""
    pass

class GitHubNetworkError(GitHubError):
    """Network error"""
    pass
```

---

## 2. Repository Synchronization

### Purpose

Keep local repo copies in sync with GitHub.

### Location

```python
# wizard/github_integration/repo_sync.py
from wizard.github_integration import RepoSync

sync = RepoSync(client=github_client)
```

### Configuration

```yaml
# wizard/config/repos.yaml
repos:
  ucode-integrated:
    - owner: "uDOS"
      repo: "typo"
      destination: "/library/ucode-integrated/typo"
      branch: "main"
      auto_pull: true
      pull_schedule: "0 0 * * *"  # Daily at midnight
      
    - owner: "uDOS"
      repo: "micro"
      destination: "/library/ucode-integrated/micro"
      branch: "main"
      auto_pull: true
      
  wizard-workspace:
    - owner: "openai"
      repo: "gpt-4"
      destination: "/library/wizard-workspace/gpt-4"
      branch: "main"
      auto_pull: true
      
    - owner: "ollama"
      repo: "ollama"
      destination: "/library/wizard-workspace/ollama"
      branch: "main"
      auto_pull: true
```

### API

```python
class RepoSync:
    def __init__(self, client: GitHubClient):
        self.client = client
    
    # Clone all configured repos
    def clone_all(self, config_path: Path) -> dict:
        """
        Clone all repos from configuration.
        
        Returns:
            {
                "success": [("uDOS/typo", "/library/..."), ...],
                "failed": [("uDOS/micro", "Network error"), ...],
                "total": 5,
                "succeeded": 5,
                "failed": 0
            }
        """
        pass
    
    # Pull updates for all repos
    def pull_all(self, config_path: Path) -> dict:
        """
        Pull latest changes for all repos.
        
        Returns same structure as clone_all()
        """
        pass
    
    # Clone a single repo
    def clone_repo(
        self,
        owner: str,
        repo: str,
        destination: Path,
        branch: str = "main"
    ) -> bool:
        """
        Clone single repo.
        """
        pass
    
    # Pull a single repo
    def pull_repo(self, local_path: Path) -> bool:
        """
        Pull single repo.
        """
        pass
    
    # Schedule periodic syncs
    def schedule_auto_pull(
        self,
        config_path: Path,
        interval: str = "0 0 * * *"  # Cron format
    ) -> None:
        """
        Schedule automatic pulls.
        
        Uses APScheduler for background scheduling.
        """
        pass
    
    # Get sync status
    def get_sync_status(self, destination: Path) -> dict:
        """
        Check if local repo is up to date.
        
        Returns:
            {
                "local_commit": "abc123...",
                "remote_commit": "def456...",
                "is_dirty": false,
                "behind_by": 0,
                "last_pull": "2026-01-14T10:00:00Z"
            }
        """
        pass
```

### Logging

All sync operations logged to `memory/logs/github-sync-YYYY-MM-DD.log`:

```
[2026-01-14 10:00:00] [INFO] [SYNC] Cloning uDOS/typo → /library/ucode-integrated/typo
[2026-01-14 10:00:05] [INFO] [SYNC] ✅ typo cloned (1.2 MB, main branch)
[2026-01-14 10:00:05] [INFO] [SYNC] Cloning uDOS/micro → /library/ucode-integrated/micro
[2026-01-14 10:00:08] [ERROR] [SYNC] ❌ micro: Network timeout after 30s
[2026-01-14 10:00:08] [INFO] [SYNC] Summary: 4/5 repos cloned successfully
```

---

## 3. Workflow Runner

### Purpose

Execute GitHub Actions workflows from Wizard, wait for results, download artifacts.

### Location

```python
# wizard/github_integration/workflow_runner.py
from wizard.github_integration import WorkflowRunner

runner = WorkflowRunner(client=github_client)
```

### Use Cases

1. **On Push:** Run tests when code is pushed
2. **Manual Trigger:** `WORKFLOW RUN core/tests`
3. **Release:** `WORKFLOW RUN core/publish`
4. **Nightly:** Auto-run scheduled workflows

### API

```python
class WorkflowRunner:
    def __init__(self, client: GitHubClient):
        self.client = client
    
    # Run a workflow
    def run(
        self,
        owner: str,
        repo: str,
        workflow: str,
        ref: str = "main",
        inputs: dict = None,
        wait: bool = False,
        timeout: int = 3600
    ) -> dict:
        """
        Run a GitHub Actions workflow.
        
        Args:
            owner: GitHub org
            repo: Repository
            workflow: Workflow name or ID
            ref: Branch/tag
            inputs: Workflow input variables
            wait: If true, block until complete
            timeout: Max seconds to wait (if wait=true)
        
        Returns:
            {
                "run_id": 12345,
                "status": "queued|in_progress|completed",
                "html_url": "https://github.com/.../runs/12345",
                "artifacts": [  # if wait=true and complete
                    {
                        "name": "dist",
                        "path": "/tmp/artifacts/dist.zip",
                        "size": 5234123
                    }
                ]
            }
        
        Raises:
            TimeoutError: If wait=true and timeout exceeded
        """
        pass
    
    # Poll workflow status
    def poll_status(
        self,
        owner: str,
        repo: str,
        run_id: str,
        interval: int = 10,
        timeout: int = 3600
    ) -> dict:
        """
        Poll workflow status until completion.
        
        Returns:
            {
                "run_id": run_id,
                "status": "completed",
                "conclusion": "success|failure",
                "created_at": "...",
                "completed_at": "...",
                "duration_seconds": 180,
                "logs_url": "...",
                "artifacts": [...]
            }
        """
        pass
    
    # Get workflow logs
    def get_logs(
        self,
        owner: str,
        repo: str,
        run_id: str
    ) -> str:
        """
        Download workflow logs as text.
        """
        pass
    
    # Download artifacts
    def download_artifacts(
        self,
        owner: str,
        repo: str,
        run_id: str,
        destination: Path,
        artifact_name: str = None
    ) -> list:
        """
        Download all (or named) artifacts from workflow.
        
        Returns:
            List of (file_path, size) tuples
        """
        pass
```

### Example: Test Runner Integration

```python
# wizard/dev_studio/test_runner.py
from wizard.github_integration import WorkflowRunner

class TestRunner:
    def __init__(self, github_client):
        self.runner = WorkflowRunner(github_client)
    
    def run_tests(self, repo: str = "uDOS", wait: bool = True):
        """Run uDOS tests on GitHub."""
        result = self.runner.run(
            owner="uDOS",
            repo=repo,
            workflow="tests",
            ref="main",
            wait=wait,
            timeout=1800  # 30 minutes
        )
        
        if result["status"] == "completed":
            if result["conclusion"] == "success":
                logger.info(f"✅ Tests passed ({result['duration_seconds']}s)")
                return True
            else:
                logger.error(f"❌ Tests failed")
                logs = self.runner.get_logs(
                    "uDOS", repo, result["run_id"]
                )
                print(logs)
                return False
        else:
            logger.info(f"⏳ Tests in progress (run_id={result['run_id']})")
            return None  # Still running
```

---

## 4. Release Manager

### Purpose

Manage versioning, create GitHub Releases, publish artifacts (TCZ, ISO, etc.).

### Location

```python
# wizard/github_integration/release_manager.py
from wizard.github_integration import ReleaseManager

releaser = ReleaseManager(client=github_client)
```

### API

```python
class ReleaseManager:
    def __init__(self, client: GitHubClient):
        self.client = client
    
    # Create a release
    def create_release(
        self,
        owner: str,
        repo: str,
        tag: str,
        version: str = None,
        name: str = None,
        notes: str = None,
        draft: bool = False,
        prerelease: bool = False
    ) -> dict:
        """
        Create a GitHub Release.
        
        Args:
            owner: GitHub org
            repo: Repository
            tag: Version tag (e.g., "v1.1.0")
            version: Component version from version.json (auto-formats tag if provided)
            name: Release name (defaults to tag)
            notes: Release notes in markdown
            draft: If true, release is draft
            prerelease: If true, marked as pre-release
        
        Returns:
            {
                "id": release_id,
                "tag": "v1.1.0",
                "url": "https://github.com/.../releases/tag/v1.1.0",
                "upload_url": "https://uploads.github.com/..."
            }
        """
        pass
    
    # Publish artifacts to release
    def publish_artifacts(
        self,
        upload_url: str,
        artifacts: list,
        signatures: dict = None
    ) -> list:
        """
        Upload multiple artifacts to release.
        
        Args:
            upload_url: From create_release()
            artifacts: [
                {
                    "path": "/path/to/uDOS-v1.1.0.tcz",
                    "content_type": "application/octet-stream"
                },
                {
                    "path": "/path/to/uDOS-v1.1.0.iso",
                    "content_type": "application/octet-stream"
                }
            ]
            signatures: Optional GPG signatures
                {
                    "uDOS-v1.1.0.tcz.sig": "<signature>",
                    ...
                }
        
        Returns:
            List of uploaded asset info dicts
        """
        pass
    
    # Publish a release (move from draft)
    def publish_release(
        self,
        owner: str,
        repo: str,
        release_id: str
    ) -> dict:
        """
        Publish a draft release.
        """
        pass
    
    # Generate release notes from commits
    def generate_release_notes(
        self,
        owner: str,
        repo: str,
        tag: str,
        previous_tag: str = None
    ) -> str:
        """
        Auto-generate release notes from commits.
        
        Returns:
            Markdown formatted release notes
        """
        pass
```

### Example: Full Release Workflow

```python
# wizard/dev_studio/build_pipeline.py
class BuildPipeline:
    def publish_release(self, component: str, version: str):
        """
        1. Build artifacts (TCZ, ISO)
        2. Create GitHub Release
        3. Upload artifacts
        4. Publish release
        """
        
        artifacts = self.build_artifacts(component)
        
        release = self.releaser.create_release(
            owner="uDOS",
            repo="uDOS",
            tag=f"v{version}",
            name=f"uDOS {version}",
            draft=True
        )
        
        self.releaser.publish_artifacts(
            upload_url=release["upload_url"],
            artifacts=[
                {"path": art, "content_type": "application/octet-stream"}
                for art in artifacts
            ]
        )
        
        self.releaser.publish_release(
            "uDOS", "uDOS", release["id"]
        )
        
        logger.info(f"✅ Released {version}")
```

---

## 5. Webhook Handler (Optional, Future)

### Purpose

Receive GitHub webhook events (push, release, pull_request) and trigger local actions.

### Location

```python
# wizard/github_integration/webhook_handler.py
# Registered with wizard/web/app.py (Flask blueprint)
```

### Events Handled

| Event | Action |
|-------|--------|
| `push` → main | Run tests, build, publish |
| `release` | Auto-update local repos |
| `pull_request` | Validate, run tests |

### Configuration

```yaml
# wizard/config/webhooks.yaml
webhooks:
  enabled: true
  secret: ${GITHUB_WEBHOOK_SECRET}
  events:
    - push
    - release
    - pull_request
  
  handlers:
    push:main:
      - action: run_tests
        payload: { repo: "uDOS" }
    
    release:
      - action: sync_release
        payload: {}
```

---

## Security

### Authentication

- GitHub token stored in `wizard/config/.env` (gitignored)
- Token requires minimal permissions:
  - `repo` (for private repos, if needed)
  - `workflow` (for running workflows)
  - `release` (for publishing)

### Validation

- Webhook signatures verified using GitHub secret
- All API calls over HTTPS
- Rate limiting respected (GitHub API v3)

### Logging

- All API calls logged (without credentials)
- Workflow runs logged to `memory/logs/github-workflows-YYYY-MM-DD.log`
- Release publishes logged to `memory/logs/github-releases-YYYY-MM-DD.log`

---

## Testing

### Unit Tests

```python
# wizard/tests/test_github_client.py
import pytest
from unittest.mock import patch, MagicMock
from wizard.github_integration import GitHubClient

@patch('requests.Session.get')
def test_clone_repo(mock_get):
    client = GitHubClient(token="test_token", owner="uDOS")
    result = client.clone_repo("uDOS", "typo", "/tmp/typo", ref="main")
    assert result is True

def test_repo_exists():
    client = GitHubClient(token="test_token", owner="uDOS")
    assert client.repo_exists("uDOS", "uDOS") is True
```

### Integration Tests

```python
# wizard/tests/test_github_integration.py
import pytest
import tempfile
from pathlib import Path
from wizard.github_integration import GitHubClient, RepoSync

@pytest.fixture
def github_client():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        pytest.skip("GITHUB_TOKEN not set")
    return GitHubClient(token=token, owner="uDOS")

def test_clone_and_pull(github_client):
    """Integration test: clone + pull a real repo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dest = Path(tmpdir) / "test-repo"
        
        # Clone
        success = github_client.clone_repo(
            "uDOS", "uDOS", dest, ref="main"
        )
        assert success is True
        assert (dest / ".git").exists()
        
        # Pull
        success = github_client.pull_repo(dest)
        assert success is True
```

---

## Deployment

### Local Development

```bash
cd /path/to/uDOS

# Set GitHub token
export GITHUB_TOKEN="ghp_xxx"

# Activate venv
source .venv/bin/activate

# Test client
python -c "
from wizard.github_integration import GitHubClient
client = GitHubClient(token='$GITHUB_TOKEN', owner='uDOS')
repos = client.list_repositories('uDOS')
print(f'Found {len(repos)} repos')
"
```

### Wizard Server Production

```bash
# In wizard/.env (gitignored)
GITHUB_TOKEN=ghp_xxx
GITHUB_OWNER=uDOS
GITHUB_WEBHOOK_SECRET=whsec_xxx

# Start Wizard
python wizard/server.py
```

---

## Timeline

| Phase | Task | Effort | Owner |
|-------|------|--------|-------|
| **1** | GitHub Client implementation | 4 hrs | Agent |
| **2** | RepoSync implementation | 3 hrs | Agent |
| **3** | WorkflowRunner + tests | 4 hrs | Agent |
| **4** | ReleaseManager implementation | 3 hrs | Agent |
| **5** | Webhook Handler (future) | 4 hrs | Future |

---

## References

- [GitHub REST API v3 Documentation](https://docs.github.com/en/rest)
- [GitHub Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks)
- [ADR-0012: Library & Plugins Reorganization](../decisions/ADR-0012-library-plugins-reorganization.md)
- [Plugin Architecture](plugin-architecture-v1.md)

---

*Last Updated: 2026-01-14*  
*Version: 1.0 Specification*
