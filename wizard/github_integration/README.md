# GitHub Integration

Wizard owns GitHub integration for the v1.5 `@dev` workspace.

Use `dev/docs/features/GITHUB-INTEGRATION.md` as the contributor-facing contract. This folder contains the implementation for the Wizard-managed GitHub control plane, not the public workspace policy.

## v1.5 Rules

- GitHub sync for Dev Mode is scoped to the tracked `@dev` payload.
- Tokens and webhook secrets must be stored through Wizard-managed secrets.
- Local-only `@dev` working areas are not part of the public sync contract.
- `vibe` remains contributor tooling inside the active Dev Mode lane.

## Control Plane

Wizard exposes GitHub integration through `/api/dev/*` endpoints:

- `GET /api/dev/github/status`
- `GET /api/dev/github/pat-status`
- `POST /api/dev/github/pat`
- `DELETE /api/dev/github/pat`
- `GET /api/dev/webhook/github-secret-status`
- `POST /api/dev/webhook/github-secret`

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
