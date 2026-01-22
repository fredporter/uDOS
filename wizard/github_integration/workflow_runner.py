"""
GitHub Actions Workflow Runner

Trigger and monitor GitHub Actions workflows.
Supports polling, log retrieval, and artifact downloads.
"""

import time
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum

from .client import GitHubClient, GitHubError
from core.services.logging_manager import get_logger

logger = get_logger("github-workflows")


class WorkflowStatus(Enum):
    """Workflow run status"""

    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNKNOWN = "unknown"


class WorkflowConclusion(Enum):
    """Workflow run conclusion"""

    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"
    ACTION_REQUIRED = "action_required"
    UNKNOWN = "unknown"


class WorkflowRunner:
    """Run and monitor GitHub Actions workflows"""

    def __init__(self, client: GitHubClient, owner: str = None):
        """
        Initialize workflow runner.

        Args:
            client: GitHubClient instance
            owner: Default GitHub owner (defaults to client.owner)
        """
        self.client = client
        self.owner = owner or client.owner

    def list_workflows(self, repo: str) -> List[Dict[str, str]]:
        """
        List available workflows.

        Returns:
            [
                {
                    "id": "123",
                    "name": "Tests",
                    "path": ".github/workflows/tests.yml",
                    "state": "active"
                },
                ...
            ]
        """
        try:
            workflows = self.client.list_workflows(self.owner, repo)
            logger.info(
                f"[WIZ] Found {len(workflows)} workflows in {self.owner}/{repo}"
            )
            return workflows
        except GitHubError as e:
            logger.error(f"[WIZ] Failed to list workflows: {e}")
            return []

    def run(
        self,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: Dict[str, str] = None,
        wait: bool = False,
        timeout: int = 3600,
        poll_interval: int = 30,
    ) -> Optional[str]:
        """
        Trigger workflow execution.

        Args:
            repo: Repository name
            workflow_id: Workflow name or ID
            ref: Branch/tag/commit
            inputs: Workflow input variables
            wait: If True, block until completion
            timeout: Max seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            run_id if successful, None otherwise
        """
        try:
            logger.info(
                f"[WIZ] Triggering workflow {workflow_id} on {self.owner}/{repo}@{ref}"
            )

            run_id = self.client.run_workflow(
                self.owner, repo, workflow_id, ref=ref, inputs=inputs
            )

            logger.info(f"[WIZ] Started run: {run_id}")

            if wait:
                self.poll_until_complete(
                    repo, run_id, timeout=timeout, poll_interval=poll_interval
                )

            return run_id

        except GitHubError as e:
            logger.error(f"[WIZ] Failed to run workflow: {e}")
            return None

    def get_status(self, repo: str, run_id: str) -> Dict[str, any]:
        """
        Get current workflow run status.

        Returns:
            {
                "id": run_id,
                "status": "queued|in_progress|completed",
                "conclusion": "success|failure|...",
                "created_at": "2026-01-14T...",
                "updated_at": "2026-01-14T...",
                "html_url": "https://github.com/...",
                "artifacts_url": "..."
            }
        """
        try:
            return self.client.get_workflow_run(self.owner, repo, run_id)
        except GitHubError as e:
            logger.error(f"[WIZ] Failed to get workflow status: {e}")
            return {}

    def is_complete(self, repo: str, run_id: str) -> bool:
        """Check if workflow run completed"""
        status = self.get_status(repo, run_id)
        return status.get("status") == WorkflowStatus.COMPLETED.value

    def is_successful(self, repo: str, run_id: str) -> bool:
        """Check if workflow run succeeded"""
        status = self.get_status(repo, run_id)
        return (
            status.get("status") == WorkflowStatus.COMPLETED.value
            and status.get("conclusion") == WorkflowConclusion.SUCCESS.value
        )

    def poll_until_complete(
        self,
        repo: str,
        run_id: str,
        timeout: int = 3600,
        poll_interval: int = 30,
        callback: Callable[[Dict], None] = None,
    ) -> bool:
        """
        Poll workflow status until completion or timeout.

        Args:
            repo: Repository name
            run_id: Workflow run ID
            timeout: Max seconds to wait
            poll_interval: Seconds between checks
            callback: Function called on each status update

        Returns:
            True if successful, False if failed or timeout
        """
        start_time = datetime.now()
        deadline = start_time + timedelta(seconds=timeout)

        logger.info(f"[WIZ] Polling workflow run {run_id} (timeout: {timeout}s)")

        while datetime.now() < deadline:
            status = self.get_status(repo, run_id)

            if not status:
                logger.warning("[WIZ] Could not fetch status, retrying...")
                time.sleep(poll_interval)
                continue

            if callback:
                callback(status)

            # Check completion
            if status.get("status") == WorkflowStatus.COMPLETED.value:
                conclusion = status.get("conclusion")
                elapsed = (datetime.now() - start_time).total_seconds()

                if conclusion == WorkflowConclusion.SUCCESS.value:
                    logger.info(f"[WIZ] Workflow succeeded in {elapsed:.0f}s")
                    return True
                else:
                    logger.error(f"[WIZ] Workflow failed: {conclusion}")
                    return False

            # Still running
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(
                f"[WIZ] Workflow {status.get('status')} ({elapsed:.0f}s elapsed)"
            )

            time.sleep(poll_interval)

        # Timeout
        logger.error(f"[WIZ] Workflow polling timeout ({timeout}s)")
        return False

    def get_logs(self, repo: str, run_id: str) -> Optional[str]:
        """
        Get workflow run logs.

        Note: GitHub API doesn't provide direct log access. This would require
        using the artifacts endpoint or GitHub CLI.

        Returns:
            Log contents (if available) or None
        """
        logger.warning("[WIZ] get_logs() not yet implemented - use GitHub UI")
        return None

    def download_artifacts(
        self, repo: str, run_id: str, destination: Path = None
    ) -> List[str]:
        """
        Download all artifacts from workflow run.

        Args:
            repo: Repository name
            run_id: Workflow run ID
            destination: Local path (defaults to memory/artifacts/{run_id})

        Returns:
            List of downloaded file paths
        """
        if not destination:
            # Anchor to repo root
            repo_root = Path(__file__).parent.parent.parent.resolve()
            destination = repo_root / "memory" / "artifacts" / str(run_id)

        try:
            logger.info(f"[WIZ] Downloading artifacts from run {run_id}")
            files = self.client.download_artifacts(
                self.owner, repo, run_id, destination
            )
            logger.info(f"[WIZ] Downloaded {len(files)} artifact(s)")
            return files
        except GitHubError as e:
            logger.error(f"[WIZ] Failed to download artifacts: {e}")
            return []

    def cancel_run(self, repo: str, run_id: str) -> bool:
        """
        Cancel running workflow (requires additional API implementation).

        Note: Not yet implemented in GitHubClient
        """
        logger.warning("[WIZ] cancel_run() not yet implemented")
        return False

    def rerun(self, repo: str, run_id: str) -> Optional[str]:
        """
        Rerun failed workflow (requires additional API implementation).

        Note: Not yet implemented in GitHubClient
        """
        logger.warning("[WIZ] rerun() not yet implemented")
        return None
