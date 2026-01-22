"""
Repository Synchronization Service

Manages cloning and pulling of uDOS repositories from GitHub.
Supports configurable sync schedules and status tracking.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import threading

from .client import GitHubClient, GitHubError
from core.services.logging_manager import get_logger

logger = get_logger("github-sync")


class RepoSync:
    """Synchronize repositories from GitHub"""

    def __init__(
        self, client: GitHubClient, library_base: Path = None, config_path: Path = None
    ):
        """
        Initialize repository synchronizer.

        Args:
            client: GitHubClient instance
            library_base: Base path for library/ folder (defaults to library/)
            config_path: Path to repos.yaml config (defaults to wizard/config/repos.yaml)
        """
        self.client = client
        self.library_base = Path(library_base or "library")
        self.config_path = Path(config_path or "wizard/config/repos.yaml")

        # Create status file (anchor to repo root)
        repo_root = Path(__file__).parent.parent.parent.resolve()
        self.status_file = repo_root / "memory" / "logs" / "github-sync-status.json"
        self.status_file.parent.mkdir(parents=True, exist_ok=True)

        self._sync_thread = None
        self._sync_interval = 3600  # 1 hour default
        self._running = False

        logger.info(f"[WIZ] RepoSync initialized: library_base={self.library_base}")

    def load_config(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Load repositories configuration from YAML.

        Expected format:
        ```
        ucode:
          - name: "micro"
            owner: "uDOS"
            repo: "micro"
            path: "library/ucode/micro"
            ref: "main"

        wizard:
          - name: "ollama"
            owner: "ollama"
            repo: "ollama"
            path: "library/wizard/ollama"
            ref: "main"
        ```

        Returns:
            {
                "ucode": [...],
                "wizard": [...]
            }
        """
        try:
            import yaml

            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f)
            return config or {}
        except ImportError:
            logger.error("[WIZ] PyYAML not installed, using JSON fallback")
            return self._load_config_json()
        except FileNotFoundError:
            logger.warning(f"[WIZ] Config not found: {self.config_path}")
            return {}

    def _load_config_json(self) -> Dict[str, List[Dict[str, str]]]:
        """Fallback JSON config loader"""
        json_path = self.config_path.with_suffix(".json")
        try:
            with open(json_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def clone_all(self, tier: str = None) -> Dict[str, Tuple[bool, str]]:
        """
        Clone all repositories from config.

        Args:
            tier: "ucode" or "wizard" (None = all)

        Returns:
            {
                "micro": (True, "Successfully cloned"),
                "ollama": (False, "Repository not found"),
                ...
            }
        """
        config = self.load_config()
        results = {}

        tiers = [tier] if tier else ["ucode", "wizard"]

        for tier_name in tiers:
            repos = config.get(tier_name, [])
            for repo_spec in repos:
                results[repo_spec["name"]] = self._clone_repo(repo_spec)

        self._save_status("clone_all", results)
        return results

    def _clone_repo(self, repo_spec: Dict[str, str]) -> Tuple[bool, str]:
        """Clone single repository"""
        name = repo_spec["name"]
        owner = repo_spec["owner"]
        repo = repo_spec["repo"]
        path = Path(repo_spec["path"])
        ref = repo_spec.get("ref", "main")

        try:
            # Check if already exists
            if path.exists() and (path / ".git").exists():
                logger.info(f"[WIZ] Already cloned: {name}")
                return (True, "Already exists")

            # Clone
            logger.info(f"[WIZ] Cloning {owner}/{repo} → {path}")
            self.client.clone_repo(owner, repo, path, ref)
            return (True, "Successfully cloned")

        except GitHubError as e:
            logger.error(f"[WIZ] Clone failed for {name}: {e}")
            return (False, str(e))

    def pull_all(self, tier: str = None) -> Dict[str, Tuple[bool, str]]:
        """
        Pull latest changes for all repositories.

        Args:
            tier: "ucode" or "wizard" (None = all)

        Returns:
            {
                "micro": (True, "Updated"),
                "ollama": (False, "Not a git repository"),
                ...
            }
        """
        config = self.load_config()
        results = {}

        tiers = [tier] if tier else ["ucode", "wizard"]

        for tier_name in tiers:
            repos = config.get(tier_name, [])
            for repo_spec in repos:
                results[repo_spec["name"]] = self._pull_repo(repo_spec)

        self._save_status("pull_all", results)
        return results

    def _pull_repo(self, repo_spec: Dict[str, str]) -> Tuple[bool, str]:
        """Pull single repository"""
        name = repo_spec["name"]
        path = Path(repo_spec["path"])

        try:
            if not (path / ".git").exists():
                return (False, "Not a git repository")

            logger.info(f"[WIZ] Pulling {name} from {path}")
            self.client.pull_repo(path)
            return (True, "Updated")

        except GitHubError as e:
            logger.error(f"[WIZ] Pull failed for {name}: {e}")
            return (False, str(e))

    def clone_repo(
        self, owner: str, repo: str, destination: Path, ref: str = "main"
    ) -> bool:
        """Clone single repository"""
        return self.client.clone_repo(owner, repo, destination, ref)

    def pull_repo(self, path: Path) -> bool:
        """Pull single repository"""
        return self.client.pull_repo(path)

    def get_sync_status(self) -> Dict[str, any]:
        """Get latest sync status"""
        try:
            with open(self.status_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save_status(self, action: str, results: Dict[str, Tuple[bool, str]]):
        """Save sync status to file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "results": {
                name: {"success": success, "message": message}
                for name, (success, message) in results.items()
            },
            "summary": {
                "total": len(results),
                "succeeded": sum(1 for success, _ in results.values() if success),
                "failed": sum(1 for success, _ in results.values() if not success),
            },
        }

        with open(self.status_file, "w") as f:
            json.dump(status, f, indent=2)

        logger.info(
            f"[WIZ] Sync complete: {status['summary']['succeeded']}/{status['summary']['total']} succeeded"
        )

    def schedule_auto_pull(self, interval: int = 3600):
        """
        Schedule periodic pull in background thread.

        Args:
            interval: Seconds between pulls (default 1 hour)
        """
        self._sync_interval = interval
        self._running = True

        def _pull_loop():
            while self._running:
                try:
                    logger.info("[WIZ] Running scheduled pull...")
                    self.pull_all()
                except Exception as e:
                    logger.error(f"[WIZ] Scheduled pull failed: {e}")

                time.sleep(self._sync_interval)

        self._sync_thread = threading.Thread(target=_pull_loop, daemon=True)
        self._sync_thread.start()
        logger.info(f"[WIZ] Scheduled auto-pull every {interval}s")

    def stop_auto_pull(self):
        """Stop background pull thread"""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=5)
        logger.info("[WIZ] Stopped auto-pull")
