"""
GitHub Service - Unified GitHub Integration for Wizard
=======================================================

Consolidates GitHub CLI integration, Actions monitoring, and repository sync
into a single service with clear module boundaries.

Modules:
  - Integration: GitHub CLI for issues, PRs, and repo data
  - Monitor: Actions workflow monitoring and self-healing
  - Sync: Safe repository synchronization

Version: 2.0.0 (consolidated from github_integration.py, github_monitor.py, github_sync.py)
"""

from __future__ import annotations

import asyncio
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.github-service")


# ============================================================
# Data Models
# ============================================================

@dataclass
class WorkflowRun:
    """GitHub Actions workflow run information."""
    id: int
    name: str
    status: str  # queued, in_progress, completed
    conclusion: Optional[str]  # success, failure, cancelled, skipped
    html_url: str
    created_at: str
    updated_at: str
    head_branch: str
    head_sha: str


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


# ============================================================
# GitHub Service (Main Class)
# ============================================================

class GitHubService:
    """Unified GitHub service with integration, monitoring, and sync."""

    def __init__(
        self,
        repo_path: Optional[Path] = None,
        allowed_repos: Optional[List[str]] = None,
        default_branch: str = "main",
        push_enabled: bool = False,
    ):
        """Initialize GitHub service.
        
        Args:
            repo_path: Path to repository (defaults to repo root)
            allowed_repos: List of allowed repos for sync (e.g., ['fredporter/uDOS-dev'])
            default_branch: Default branch for operations (default: 'main')
            push_enabled: Enable push operations (default: False - read-only)
        """
        repo_root = get_repo_root()
        self.repo_path = Path(repo_path or repo_root).absolute()
        self.allowed_repos = set(allowed_repos or ["fredporter/uDOS-dev"])
        self.default_branch = default_branch
        self.push_enabled = push_enabled
        
        # Integration state
        self.gh_available = False
        self.gh_error_message = None
        self._check_gh_cli()
        
        # Monitor state
        self.workflow_history: List[WorkflowRun] = []
        self.failure_patterns: Dict[str, int] = {}

    # ============================================================
    # Integration Module (GitHub CLI)
    # ============================================================

    def _check_gh_cli(self) -> None:
        """Check if GitHub CLI is installed and authenticated (non-fatal)."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                self.gh_error_message = "GitHub CLI not authenticated. Run: gh auth login"
                logger.warning(f"[WIZ] {self.gh_error_message}")
                return
            self.gh_available = True
            logger.info("[WIZ] GitHub CLI authenticated and ready")
        except FileNotFoundError:
            self.gh_error_message = "GitHub CLI not installed. Install: brew install gh"
            logger.warning(f"[WIZ] {self.gh_error_message}")

    def _run_gh(self, args: List[str]) -> Dict[str, Any]:
        """Run GitHub CLI command (requires availability check)."""
        if not self.gh_available:
            raise RuntimeError(self.gh_error_message or "GitHub CLI not available")
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout else {}

    def get_issues(self, state: str = "open") -> List[Dict[str, Any]]:
        """Get GitHub issues (requires GitHub CLI)."""
        return self._run_gh(
            [
                "issue",
                "list",
                "--state",
                state,
                "--json",
                "number,title,state,labels,createdAt,updatedAt,author",
            ]
        )

    def get_pull_requests(self, state: str = "open") -> List[Dict[str, Any]]:
        """Get GitHub pull requests (requires GitHub CLI)."""
        return self._run_gh(
            [
                "pr",
                "list",
                "--state",
                state,
                "--json",
                "number,title,state,createdAt,updatedAt,author,mergeable",
            ]
        )

    def create_issue(
        self, title: str, body: str, labels: List[str] = None
    ) -> Dict[str, Any]:
        """Create a GitHub issue."""
        args = ["issue", "create", "--title", title, "--body", body]
        if labels:
            args.extend(["--label", ",".join(labels)])
        return self._run_gh(args)

    def get_devlog(self, month: Optional[str] = None) -> str:
        """Get devlog for specified month (defaults to current)."""
        month = month or datetime.now().strftime("%Y-%m")
        devlog_path = self.repo_path / "docs" / "devlog" / f"{month}.md"
        if not devlog_path.exists():
            return f"# Devlog {month}\n\nNo entries yet."
        return devlog_path.read_text()

    def get_roadmap(self) -> str:
        """Get project roadmap."""
        return (self.repo_path / "docs" / "ROADMAP.md").read_text()

    def get_copilot_instructions(self) -> str:
        """Get Copilot instructions."""
        return (self.repo_path / ".github" / "copilot-instructions.md").read_text()

    def get_agents_doc(self) -> str:
        """Get AGENTS.md documentation."""
        return (self.repo_path / "docs" / "AGENTS.md").read_text()

    def search_logs(self, log_type: str = "debug", lines: int = 50) -> str:
        """Search recent logs."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.repo_path / "memory" / "logs" / f"{log_type}-{today}.log"
        if not log_file.exists():
            return f"No {log_type} log for {today}"
        result = subprocess.run(
            ["tail", "-n", str(lines), str(log_file)],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout

    def get_repo_info(self) -> Dict[str, Any]:
        """Get repository information."""
        return self._run_gh(
            ["repo", "view", "--json", "name,owner,description,url,defaultBranchRef"]
        )

    # ============================================================
    # Monitor Module (GitHub Actions)
    # ============================================================

    async def handle_webhook(self, event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming GitHub webhook.
        
        Routes to appropriate handler based on event type:
        - workflow_run: Actions monitoring
        - push: Repository sync
        """
        if event == "workflow_run":
            return await self._handle_workflow_run(payload)
        elif event == "push":
            repo = payload.get("repository", {}).get("full_name") or "unknown/unknown"
            branch = self._extract_branch(event, payload)
            return self.sync_pull(repo=repo, branch=branch).__dict__
        elif event == "ping":
            return {"status": "ok", "message": "Webhook receiver active"}
        else:
            return {"status": "ignored", "message": f"Unknown event type: {event}"}

    async def _handle_workflow_run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle workflow_run event."""
        action = payload.get("action")
        workflow_run = payload.get("workflow_run", {})
        
        run_info = WorkflowRun(
            id=workflow_run.get("id"),
            name=workflow_run.get("name"),
            status=workflow_run.get("status"),
            conclusion=workflow_run.get("conclusion"),
            html_url=workflow_run.get("html_url"),
            created_at=workflow_run.get("created_at"),
            updated_at=workflow_run.get("updated_at"),
            head_branch=workflow_run.get("head_branch"),
            head_sha=workflow_run.get("head_sha"),
        )
        
        self.workflow_history.append(run_info)
        
        logger.info(f"[WIZ] GitHub Actions: {run_info.name} - {run_info.status}/{run_info.conclusion or 'in progress'}")
        
        if action == "completed":
            if run_info.conclusion == "failure":
                return await self._handle_workflow_failure(run_info)
            elif run_info.conclusion == "success":
                logger.info(f"[WIZ] Workflow completed successfully: {run_info.name}")
                return {"status": "success", "action": "none"}
        
        return {"status": "acknowledged"}

    async def _handle_workflow_failure(self, run_info: WorkflowRun) -> Dict[str, Any]:
        """Handle workflow failure with self-healing logic."""
        logger.warning(f"[WIZ] Workflow failed: {run_info.name} - analyzing...")
        
        failure_reason = await self._get_failure_reason(run_info)
        pattern_key = f"{run_info.name}:{failure_reason}"
        self.failure_patterns[pattern_key] = self.failure_patterns.get(pattern_key, 0) + 1
        
        # Check for transient failures (network, timeout)
        if failure_reason in {"timeout", "network_error", "connection_error"}:
            logger.info("[WIZ] Detected transient failure - attempting auto-retry...")
            retry_result = await self._retry_workflow(run_info)
            return {"status": "failure", "action": "auto_retry", "result": retry_result}
        
        # Check for fixable patterns
        fix_result = await self._attempt_auto_fix(run_info, failure_reason)
        if fix_result["fixed"]:
            return {"status": "failure", "action": "auto_fix", "result": fix_result}
        
        logger.warning(f"[WIZ] Manual intervention required for {run_info.name}: {failure_reason}")
        return {
            "status": "failure",
            "action": "notify",
            "reason": failure_reason,
            "url": run_info.html_url
        }

    async def _get_failure_reason(self, run_info: WorkflowRun) -> str:
        """Analyze workflow failure to determine root cause."""
        try:
            result = subprocess.run(
                ["gh", "run", "view", str(run_info.id), "--repo", self._get_repo_name()],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                if "test" in output and "failed" in output:
                    return "test_failure"
                elif "build" in output and "failed" in output:
                    return "build_failure"
                elif "timeout" in output:
                    return "timeout"
                elif "network" in output or "connection" in output:
                    return "network_error"
                return "unknown"
            return "cli_error"
        except Exception as e:
            logger.error(f"[WIZ] Error analyzing failure: {e}")
            return "unknown"

    async def _retry_workflow(self, run_info: WorkflowRun) -> Dict[str, Any]:
        """Retry failed workflow using GitHub CLI."""
        try:
            result = subprocess.run(
                ["gh", "run", "rerun", str(run_info.id), "--repo", self._get_repo_name()],
                capture_output=True,
                text=True,
                timeout=30,
            )
            
            if result.returncode == 0:
                logger.info(f"[WIZ] Workflow re-triggered: {run_info.name}")
                return {"success": True, "message": "Workflow re-triggered"}
            else:
                error = result.stderr or "Unknown error"
                logger.error(f"[WIZ] Failed to retry workflow: {error}")
                return {"success": False, "error": error}
        except Exception as e:
            logger.error(f"[WIZ] Error retrying workflow: {e}")
            return {"success": False, "error": str(e)}

    async def _attempt_auto_fix(self, run_info: WorkflowRun, failure_reason: str) -> Dict[str, Any]:
        """Attempt automatic fixes for known failure patterns."""
        if failure_reason == "test_failure":
            pattern_key = f"{run_info.name}:{failure_reason}"
            count = self.failure_patterns.get(pattern_key, 0)
            if count <= 2:  # Retry flaky tests up to 2 times
                logger.info("[WIZ] Test failure detected - auto-retrying (flaky test suspected)")
                retry_result = await self._retry_workflow(run_info)
                return {"fixed": retry_result["success"], "method": "retry", **retry_result}
        
        return {"fixed": False, "reason": "No auto-fix available"}

    async def get_recent_runs(self, limit: int = 10) -> List[WorkflowRun]:
        """Get recent workflow runs."""
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--repo", self._get_repo_name(), "--limit", str(limit), 
                 "--json", "databaseId,name,status,conclusion,url,createdAt,updatedAt,headBranch,headSha"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            
            if result.returncode == 0:
                runs_data = json.loads(result.stdout)
                return [
                    WorkflowRun(
                        id=run["databaseId"],
                        name=run["name"],
                        status=run["status"],
                        conclusion=run.get("conclusion"),
                        html_url=run["url"],
                        created_at=run["createdAt"],
                        updated_at=run["updatedAt"],
                        head_branch=run["headBranch"],
                        head_sha=run["headSha"],
                    )
                    for run in runs_data
                ]
            return []
        except Exception as e:
            logger.error(f"[WIZ] Error getting recent runs: {e}")
            return []

    # ============================================================
    # Sync Module (Repository Sync)
    # ============================================================

    def sync_pull(self, repo: Optional[str] = None, branch: Optional[str] = None) -> SyncResult:
        """Fetch and fast-forward merge the default branch."""
        repo = repo or self._get_repo_name()
        branch = branch or self.default_branch
        
        if repo not in self.allowed_repos:
            return SyncResult(False, "ignored", f"repo not allowed: {repo}", repo=repo)
        
        fetch = self._run_git(["git", "fetch", "origin", branch])
        if fetch["code"] != 0:
            return SyncResult(False, "fetch", "fetch failed", fetch["out"], fetch["err"], repo, branch)

        merge = self._run_git(["git", "merge", "--ff-only", f"origin/{branch}"])
        if merge["code"] != 0:
            return SyncResult(False, "merge", "fast-forward failed (manual intervention)", merge["out"], merge["err"], repo, branch)

        logger.info(f"[WIZ] Synced {repo}/{branch} successfully")
        return SyncResult(True, "pull", "fast-forward applied", merge["out"], merge["err"], repo, branch)

    def sync_push(self, repo: Optional[str] = None, branch: Optional[str] = None) -> SyncResult:
        """Push local branch to origin (requires push_enabled=True)."""
        if not self.push_enabled:
            return SyncResult(False, "push", "push disabled by policy")

        repo = repo or self._get_repo_name()
        branch = branch or self.default_branch
        
        if repo not in self.allowed_repos:
            return SyncResult(False, "ignored", f"repo not allowed: {repo}", repo=repo)
        
        push = self._run_git(["git", "push", "origin", branch])
        if push["code"] != 0:
            return SyncResult(False, "push", "push failed", push["out"], push["err"], repo, branch)
        
        logger.info(f"[WIZ] Pushed {repo}/{branch} successfully")
        return SyncResult(True, "push", "push completed", push["out"], push["err"], repo, branch)

    def sync_status(self) -> SyncResult:
        """Get sync status (ahead/behind origin)."""
        branch = self.default_branch
        ahead = self._run_git(["git", "rev-list", "--left-right", "--count", f"origin/{branch}...{branch}"])
        status = self._run_git(["git", "status", "--short"])
        detail = f"ahead/behind: {ahead['out'].strip()}" if ahead["code"] == 0 else "unknown"
        return SyncResult(True, "status", detail, status["out"], status["err"], self._get_repo_name(), branch)

    # ============================================================
    # Utility Methods
    # ============================================================

    def _get_repo_name(self) -> str:
        """Get GitHub repository name from git config."""
        try:
            result = self._run_git(["git", "config", "--get", "remote.origin.url"])
            if result["code"] == 0:
                url = (result["out"] or "").strip()
                if "github.com" in url:
                    parts = url.split("github.com")[-1].strip("/:").split("/")
                    if len(parts) >= 2:
                        owner = parts[0]
                        repo = parts[1].replace(".git", "")
                        return f"{owner}/{repo}"
            return "unknown/unknown"
        except Exception:
            return "unknown/unknown"

    def _extract_branch(self, event: str, payload: Dict) -> str:
        """Extract branch name from webhook payload."""
        if event == "push":
            ref = payload.get("ref", "")
            if ref.startswith("refs/heads/"):
                return ref.split("/")[-1]
        return "unknown"

    def _run_git(self, cmd: List[str]) -> Dict[str, Any]:
        """Run git command safely."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
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
        except Exception as exc:
            return {"code": 1, "out": None, "err": str(exc)}


# ============================================================
# Singleton Access
# ============================================================

_github_service: Optional[GitHubService] = None


def get_github_service(
    repo_path: Optional[Path] = None,
    allowed_repos: Optional[List[str]] = None,
    default_branch: str = "main",
    push_enabled: bool = False,
) -> GitHubService:
    """Get or create singleton GitHub service."""
    global _github_service
    if _github_service is None:
        _github_service = GitHubService(
            repo_path=repo_path,
            allowed_repos=allowed_repos,
            default_branch=default_branch,
            push_enabled=push_enabled,
        )
    return _github_service
