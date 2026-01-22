"""
GitHub Integration Service for Wizard Server

Provides GitHub CLI integration for repo context, issues, PRs, and logs.
"""

import subprocess
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from wizard.services.logging_manager import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("wizard.github-integration")


class GitHubIntegration:
    """GitHub CLI integration for Wizard."""

    def __init__(self, repo_path: str = None):
        repo_root = get_repo_root()
        self.repo_path = Path(repo_path or repo_root).absolute()
        self.available = False
        self.error_message = None
        self._check_gh_cli()

    def _check_gh_cli(self) -> None:
        """Check if GitHub CLI is installed and authenticated (non-fatal)."""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True, check=False
            )
            if result.returncode != 0:
                self.error_message = "GitHub CLI not authenticated. Run: gh auth login"
                logger.warning(f"[WIZ] {self.error_message}")
                return
            self.available = True
            logger.info("[WIZ] GitHub CLI authenticated and ready")
        except FileNotFoundError:
            self.error_message = "GitHub CLI not installed. Install: brew install gh"
            logger.warning(f"[WIZ] {self.error_message}")
            return

    def _run_gh(self, args: List[str]) -> Dict[str, Any]:
        """Run GitHub CLI command (requires availability check)."""
        if not self.available:
            raise RuntimeError(
                self.error_message or "GitHub CLI not available"
            )
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout else {}

    def sync_repo(self) -> Dict[str, str]:
        """Sync repository (git operations don't require GitHub CLI)."""
        subprocess.run(
            ["git", "fetch", "origin"],
            cwd=self.repo_path,
            check=True,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.repo_path,
            check=True,
        )
        has_changes = bool(result.stdout.strip())
        return {
            "synced": not has_changes,
            "has_local_changes": has_changes,
            "timestamp": datetime.now().isoformat(),
        }

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
        args = ["issue", "create", "--title", title, "--body", body]
        if labels:
            args.extend(["--label", ",".join(labels)])
        return self._run_gh(args)

    def get_devlog(self, month: Optional[str] = None) -> str:
        month = month or datetime.now().strftime("%Y-%m")
        devlog_path = self.repo_path / "docs" / "devlog" / f"{month}.md"
        if not devlog_path.exists():
            return f"# Devlog {month}\n\nNo entries yet."
        return devlog_path.read_text()

    def get_roadmap(self) -> str:
        return (self.repo_path / "docs" / "roadmap.md").read_text()

    def get_copilot_instructions(self) -> str:
        return (self.repo_path / ".github" / "copilot-instructions.md").read_text()

    def get_agents_doc(self) -> str:
        return (self.repo_path / "AGENTS.md").read_text()

    def search_logs(self, log_type: str = "debug", lines: int = 50) -> str:
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
        return self._run_gh(
            ["repo", "view", "--json", "name,owner,description,url,defaultBranchRef"]
        )
