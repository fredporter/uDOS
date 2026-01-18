# GitHub Integration Quick Reference

## Installation & Setup

### 1. Ensure GitHub Token is Available
```bash
# Add to ~/.zshrc or ~/.bash_profile
export GITHUB_TOKEN="github_pat_xxxxx"

# Or in Python
import os
os.environ["GITHUB_TOKEN"] = "github_pat_xxxxx"
```

### 2. Import the Module
```python
from wizard.github_integration import (
    GitHubClient,
    RepoSync,
    WorkflowRunner,
    ReleaseManager
)
```

---

## Common Operations

### Clone All Repositories
```python
from wizard.github_integration import GitHubClient, RepoSync

client = GitHubClient()
sync = RepoSync(client)

# Clone ucode (shipping) repositories
results = sync.clone_all(tier="ucode")

# Check results
for repo, (success, msg) in results.items():
    status = "✅" if success else "❌"
    print(f"{status} {repo}: {msg}")
```

### Pull Latest Updates
```python
# Pull all repositories
results = sync.pull_all()

# Pull specific tier
results = sync.pull_all(tier="wizard")

# Get sync status
status = sync.get_sync_status()
print(f"Synced: {status['summary']['timestamp']}")
```

### Start Background Auto-Pull
```python
# Pull every hour
sync.schedule_auto_pull(interval=3600)

# ... later ...
sync.stop_auto_pull()
```

### List Available Workflows
```python
from wizard.github_integration import WorkflowRunner

runner = WorkflowRunner(client)
workflows = runner.list_workflows("micro")

for wf in workflows:
    print(f"[{wf['id']}] {wf['name']} ({wf['state']})")
```

### Trigger and Monitor Workflow
```python
# Trigger tests workflow
run_id = runner.run("micro", "tests")
print(f"Started run: {run_id}")

# Poll until completion
success = runner.poll_until_complete(
    "micro",
    run_id,
    timeout=1800,  # 30 minutes
    poll_interval=30  # Check every 30 seconds
)

if success:
    # Download artifacts
    artifacts = runner.download_artifacts("micro", run_id)
    print(f"Downloaded: {artifacts}")
else:
    print("Workflow failed!")
```

### Create and Publish Release
```python
from wizard.github_integration import ReleaseManager
from pathlib import Path

rm = ReleaseManager(client)

# Simple release
release = rm.create_release(
    "micro",
    "v1.2.0",
    name="Release 1.2.0",
    body="## New Features\n- Feature 1\n- Feature 2"
)
print(f"Created: {release['html_url']}")
```

### Publish with Changelog
```python
# Auto-generate changelog and upload artifacts
success, msg = rm.publish_with_changelog(
    "micro",
    "v1.2.0",
    from_tag="v1.1.0",
    artifacts=[
        Path("dist/micro-v1.2.0.tcz"),
        Path("dist/micro-v1.2.0.iso")
    ]
)
print(msg)
```

### Upload Artifacts to Existing Release
```python
results = rm.upload_artifacts(
    "micro",
    "v1.2.0",
    [
        Path("dist/micro-v1.2.0.tar.gz"),
        Path("dist/micro-v1.2.0.zip")
    ]
)

for filename, (success, url) in results.items():
    if success:
        print(f"✅ {filename}: {url}")
    else:
        print(f"❌ {filename}: {url}")
```

---

## Error Handling

```python
from wizard.github_integration.client import (
    GitHubError,
    GitHubAuthError,
    GitHubNotFoundError,
    GitHubRateLimitError,
    GitHubNetworkError
)

try:
    client = GitHubClient()
    sync = RepoSync(client)
    sync.clone_all()
    
except GitHubAuthError:
    print("❌ Invalid or missing GitHub token")
    print("Set GITHUB_TOKEN environment variable")
    
except GitHubRateLimitError:
    print("❌ Rate limited by GitHub API")
    print("Wait 1 hour or use authenticated token for higher limits")
    
except GitHubNetworkError as e:
    print(f"❌ Network error: {e}")
    print("Check internet connectivity")
    
except GitHubNotFoundError as e:
    print(f"❌ Resource not found: {e}")
    
except GitHubError as e:
    print(f"❌ GitHub API error: {e}")
```

---

## Configuration

### Repository List (`wizard/config/repos.yaml`)

Format:
```yaml
ucode:
  - name: "repo-name"
    owner: "github-org"
    repo: "repo-name"
    path: "library/ucode/repo-name"
    ref: "main"

wizard:
  - name: "repo-name"
    owner: "github-org"
    repo: "repo-name"
    path: "library/wizard/repo-name"
    ref: "main"
```

**Notes:**
- `ucode/` = shipping, production repositories
- `wizard/` = development, experimental repositories
- `ref` = git branch/tag to check out

### Client Configuration

```python
client = GitHubClient(
    token="github_pat_xxx",       # GitHub token (or env var)
    owner="uDOS",                 # Default owner (can override per call)
    base_url="https://api.github.com",  # GitHub API URL
    timeout=30,                   # Request timeout (seconds)
    retry_attempts=3              # Retries for failed requests
)
```

---

## Testing

### Run Unit Tests
```bash
cd /Users/fredbook/Code/uDOS

# Run all GitHub integration tests
pytest wizard/github_integration/test_github_integration.py -v

# Run specific test class
pytest wizard/github_integration/test_github_integration.py::TestGitHubClient -v

# Run specific test
pytest wizard/github_integration/test_github_integration.py::TestGitHubClient::test_init_with_token -v

# Quick run (no verbose)
pytest wizard/github_integration/test_github_integration.py -q
```

### Test Results
```
29 passed in 3.07s

✅ GitHubClient (14 tests)
✅ RepoSync (4 tests)
✅ WorkflowRunner (8 tests)
✅ ReleaseManager (3 tests)
```

---

## Logging & Debugging

### Check Sync Status
```python
sync = RepoSync(client)
status = sync.get_sync_status()

print(f"Last sync: {status['timestamp']}")
print(f"Action: {status['action']}")
print(f"Results: {status['summary']}")

# View detailed results
for repo, result in status['results'].items():
    print(f"{repo}: {result}")
```

### View Logs
```bash
# Real-time logs
tail -f memory/logs/github-sync-YYYY-MM-DD.log

# Last 50 lines
tail -50 memory/logs/github-sync-YYYY-MM-DD.log

# Search for errors
grep "ERROR\|FAILED" memory/logs/github-sync-*.log
```

---

## Integration with uDOS Commands

### Future REPAIR Integration
```bash
# Automatic sync on repair
REPAIR --pull    # Will use GitHub sync to pull all repos

# Full repair with upgrade
REPAIR --upgrade-all  # Includes GitHub integration
```

### Future GITHUB Commands
```bash
# List available workflows
GITHUB WORKFLOWS list micro

# Trigger workflow
GITHUB WORKFLOW run micro tests --wait

# Create release
GITHUB RELEASE publish micro v1.2.0 --changelog

# Sync repositories
GITHUB SYNC pull wizard
GITHUB SYNC clone ucode
```

---

## Performance Tips

1. **Use Shallow Clones**: Default clone uses `--depth 1` for speed
2. **Configure Poll Intervals**: Adjust `poll_interval` for workflow polling
3. **Batch Operations**: Use `clone_all()` instead of individual clones
4. **Scheduled Syncing**: Use `schedule_auto_pull()` to sync in background
5. **Rate Limiting**: Authenticated tokens have 5000 req/hour vs 60 for unauthenticated

---

## Troubleshooting

### "Invalid GitHub token"
```bash
# Verify token is set
echo $GITHUB_TOKEN

# Check token permissions
# Token needs: repo, workflow, read:packages

# Generate new token: https://github.com/settings/tokens
```

### "Rate limit exceeded"
```python
# Check rate limit status
# GitHub API v3: 5000 req/hour (authenticated)
# Implement exponential backoff (already built-in)

# Solution: wait 1 hour or upgrade plan
```

### "Network error"
```bash
# Check internet connectivity
ping github.com

# Check GitHub status
# https://www.githubstatus.com/

# Verify firewall/proxy settings
```

### "Repository not found"
```python
# Verify repo exists
client.repo_exists("owner", "repo")  # Returns True/False

# Check owner and repo name
# Case-sensitive!
```

---

## Examples

See also:
- [Phase 2 Complete Documentation](../docs/devlog/2026-01-phase-2-complete.md)
- [GitHub Integration Spec](../docs/specs/wizard-github-integration.md)
- [Test Suite](../wizard/github_integration/test_github_integration.py)

---

*Last Updated: 2026-01-14*  
*GitHub Integration Module v1.0.0*
