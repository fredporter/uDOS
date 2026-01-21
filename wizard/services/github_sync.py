"""GitHub repository sync service.

Provides safe, policy-aware sync operations (pull/push) for allowed repositories.
Designed for production Wizard server usage:
- Allowlist of repos (default: fredporter/uDOS-dev)
- Branch guard (default: main)
- No force operations; fast-forward only
- Optional push (disabled by default)
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class SyncResult:
    """Structured result for sync operations."""
    success: bool
    action: str
    detail: str
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    repo: Optional[str] = None
    branch: Optional[str] = None


class GitHubSyncService:
    """Safely synchronize a Git repository with GitHub."""

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        allowed_repos: Optional[list[str]] = None,
        default_branch: str = "main",
        push_enabled: bool = False,
        max_retries: int = 2,
    ) -> None:
        self.repo_root = repo_root or Path(__file__).resolve().parents[2]
        self.allowed_repos = set(allowed_repos or ["fredporter/uDOS-dev"])
        self.default_branch = default_branch
        self.push_enabled = push_enabled
        self.max_retries = max_retries

    def handle_webhook(self, event: str, payload: Dict) -> SyncResult:
        """Handle GitHub webhook events relevant to sync.

        Currently acts on push events for the default branch.
        """
        repo = payload.get("repository", {}).get("full_name") or "unknown/unknown"
        if repo not in self.allowed_repos:
            return SyncResult(False, "ignored", f"repo not allowed: {repo}", repo=repo)

        branch = self._extract_branch(event, payload)
        if branch != self.default_branch:
            return SyncResult(False, "ignored", f"branch ignored: {branch}", repo=repo, branch=branch)

        if event == "push":
            return self.sync_pull(repo=repo, branch=branch)

        return SyncResult(False, "ignored", f"event ignored: {event}", repo=repo, branch=branch)

    def sync_pull(self, repo: Optional[str] = None, branch: Optional[str] = None) -> SyncResult:
        """Fetch and fast-forward merge the default branch."""
        repo = repo or self._get_repo_name()
        branch = branch or self.default_branch
        fetch = self._run(["git", "fetch", "origin", branch])
        if fetch["code"] != 0:
            return SyncResult(False, "fetch", "fetch failed", fetch["out"], fetch["err"], repo, branch)

        merge = self._run(["git", "merge", "--ff-only", f"origin/{branch}"])
        if merge["code"] != 0:
            return SyncResult(False, "merge", "fast-forward failed (manual intervention)", merge["out"], merge["err"], repo, branch)

        return SyncResult(True, "pull", "fast-forward applied", merge["out"], merge["err"], repo, branch)

    def sync_push(self, repo: Optional[str] = None, branch: Optional[str] = None) -> SyncResult:
        """Push local branch to origin (fast-forward only). Disabled unless configured."""
        if not self.push_enabled:
            return SyncResult(False, "push", "push disabled by policy")

        repo = repo or self._get_repo_name()
        branch = branch or self.default_branch
        push = self._run(["git", "push", "origin", branch])
        if push["code"] != 0:
            return SyncResult(False, "push", "push failed", push["out"], push["err"], repo, branch)
        return SyncResult(True, "push", "push completed", push["out"], push["err"], repo, branch)

    def status(self) -> SyncResult:
        """Return simple status of local vs origin."""
        branch = self.default_branch
        ahead = self._run(["git", "rev-list", "--left-right", "--count", f"origin/{branch}...{branch}"])
        status = self._run(["git", "status", "--short"])
        detail = f"ahead/behind: {ahead['out'].strip()}" if ahead["code"] == 0 else "unknown"
        return SyncResult(True, "status", detail, status["out"], status["err"], self._get_repo_name(), branch)

    def _extract_branch(self, event: str, payload: Dict) -> str:
        if event == "push":
            ref = payload.get("ref", "")
            if ref.startswith("refs/heads/"):
                return ref.split("/")[-1]
        return "unknown"

    def _get_repo_name(self) -> str:
        try:
            result = self._run(["git", "config", "--get", "remote.origin.url"])
            if result["code"] == 0:
                url = (result["out"] or "").strip()
                if "github.com" in url:
                    parts = url.split("github.com")[-1].strip("/:").split("/")
                    if len(parts) >= 2:
                        owner, repo = parts[0], parts[1].replace(".git", "")
                        return f"{owner}/{repo}"
            return "unknown/unknown"
        except Exception:
            return "unknown/unknown"

    def _run(self, cmd: list[str]) -> Dict[str, str | int | None]:
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            return {
                "code": result.returncode,
                "out": result.stdout,
                "err": result.stderr,
            }
        except subprocess.TimeoutExpired as exc:
            return {"code": 124, "out": None, "err": str(exc)}
        except FileNotFoundError as exc:
            return {"code": 127, "out": None, "err": str(exc)}
        except Exception as exc:  # pragma: no cover
            return {"code": 1, "out": None, "err": str(exc)}


_sync_instance: Optional[GitHubSyncService] = None


def get_github_sync_service(
    *,
    allowed_repo: Optional[str] = None,
    default_branch: Optional[str] = None,
    push_enabled: Optional[bool] = None,
) -> GitHubSyncService:
    """Get (or create) the singleton sync service with config overrides."""
    global _sync_instance
    needs_recreate = False

    if _sync_instance is None:
        needs_recreate = True
    else:
        if allowed_repo and allowed_repo not in _sync_instance.allowed_repos:
            needs_recreate = True
        if default_branch and default_branch != _sync_instance.default_branch:
            needs_recreate = True
        if push_enabled is not None and push_enabled != _sync_instance.push_enabled:
            needs_recreate = True

    if needs_recreate:
        _sync_instance = GitHubSyncService(
            allowed_repos=[allowed_repo] if allowed_repo else None,
            default_branch=default_branch or "main",
            push_enabled=push_enabled if push_enabled is not None else False,
        )

    return _sync_instance
