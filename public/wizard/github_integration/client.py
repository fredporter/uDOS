"""
GitHub REST API Client

Wrapper around GitHub REST API v3 for:
- Repository operations
- Workflow management
- Release publishing
- File operations
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from urllib.parse import urljoin
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout, ConnectionError

from core.services.logging_manager import get_logger

logger = get_logger("github-client")


class GitHubError(Exception):
    """Base GitHub API error"""

    pass


class GitHubAuthError(GitHubError):
    """Authentication/authorization error"""

    pass


class GitHubNotFoundError(GitHubError):
    """Resource not found"""

    pass


class GitHubRateLimitError(GitHubError):
    """Rate limit exceeded"""

    pass


class GitHubNetworkError(GitHubError):
    """Network connectivity error"""

    pass


class GitHubClient:
    """GitHub REST API v3 client with authentication support"""

    def __init__(
        self,
        token: str = None,
        owner: str = "uDOS",
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        retry_attempts: int = 3,
    ):
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token (or env: GITHUB_TOKEN)
            owner: Default GitHub organization/user
            base_url: GitHub API base URL
            timeout: Request timeout in seconds
            retry_attempts: Number of retries for failed requests

        Raises:
            GitHubAuthError: If no token provided or token invalid
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if not self.token:
            raise GitHubAuthError(
                "GitHub token required. Set GITHUB_TOKEN env var or pass token parameter."
            )

        self.owner = owner
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retry_attempts = retry_attempts

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {self.token}",
                "User-Agent": "uDOS-Wizard/1.0",
            }
        )

        logger.info(f"[WIZ] GitHub client initialized for owner={owner}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to GitHub API with retries.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments passed to requests

        Returns:
            Response JSON as dict

        Raises:
            GitHubAuthError: 401/403 responses
            GitHubNotFoundError: 404 responses
            GitHubRateLimitError: 429 responses
            GitHubNetworkError: Network errors
            GitHubError: Other API errors
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))

        for attempt in range(self.retry_attempts):
            try:
                response = self.session.request(
                    method, url, timeout=self.timeout, **kwargs
                )

                # Check for auth errors
                if response.status_code == 401:
                    raise GitHubAuthError("Invalid GitHub token")
                elif response.status_code == 403:
                    if "rate limit" in response.text.lower():
                        raise GitHubRateLimitError("GitHub API rate limit exceeded")
                    raise GitHubAuthError("Access forbidden (insufficient permissions)")

                # Check for not found
                if response.status_code == 404:
                    raise GitHubNotFoundError(f"Resource not found: {endpoint}")

                # Check for rate limit
                if response.status_code == 429:
                    raise GitHubRateLimitError("Rate limit exceeded")

                # Successful response
                response.raise_for_status()

                if response.status_code == 204:  # No content
                    return {}

                return response.json() if response.text else {}

            except (Timeout, ConnectionError) as e:
                if attempt == self.retry_attempts - 1:
                    raise GitHubNetworkError(
                        f"Network error after {self.retry_attempts} retries: {e}"
                    )
                logger.warning(
                    f"[WIZ] Network error (attempt {attempt + 1}), retrying..."
                )
                continue

            except GitHubError:
                raise  # Re-raise known GitHub errors

            except RequestException as e:
                raise GitHubError(f"GitHub API error: {e}")

        return {}

    # ========== Repository Operations ==========

    def repo_exists(self, owner: str, repo: str) -> bool:
        """Check if repository exists"""
        try:
            self._make_request("GET", f"/repos/{owner}/{repo}")
            return True
        except GitHubNotFoundError:
            return False

    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository metadata.

        Returns:
            {
                "name": "uDOS",
                "full_name": "owner/uDOS",
                "description": "...",
                "html_url": "https://github.com/...",
                "default_branch": "main",
                "pushed_at": "2026-01-14T...",
                "size": 12345,
                "stargazers_count": 42,
                "topics": ["offline-first", "tinycore"]
            }
        """
        data = self._make_request("GET", f"/repos/{owner}/{repo}")
        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "html_url": data.get("html_url"),
            "default_branch": data.get("default_branch"),
            "pushed_at": data.get("pushed_at"),
            "size": data.get("size"),
            "stargazers_count": data.get("stargazers_count"),
            "topics": data.get("topics", []),
        }

    def list_repositories(
        self, owner: str = None, per_page: int = 30, page: int = 1
    ) -> List[Dict[str, Any]]:
        """
        List repositories for org/user.

        Args:
            owner: GitHub org/user (defaults to self.owner)
            per_page: Results per page (max 100)
            page: Page number (1-indexed)

        Returns:
            List of repo dicts
        """
        owner = owner or self.owner
        data = self._make_request(
            "GET",
            f"/users/{owner}/repos",
            params={
                "per_page": min(per_page, 100),
                "page": page,
                "sort": "updated",
                "direction": "desc",
            },
        )
        return data if isinstance(data, list) else []

    def clone_repo(
        self, owner: str, repo: str, destination: Path, ref: str = "main"
    ) -> bool:
        """
        Clone repository using git (requires git installed).

        Args:
            owner: GitHub org
            repo: Repository name
            destination: Local path
            ref: Branch/tag/commit

        Returns:
            True if successful

        Raises:
            GitHubNetworkError: Network error
        """
        import subprocess

        url = f"https://github.com/{owner}/{repo}.git"
        destination = Path(destination)

        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    ref,
                    url,
                    str(destination),
                ],
                check=True,
                capture_output=True,
                timeout=300,  # 5 minutes
            )
            logger.info(f"[WIZ] Cloned {owner}/{repo} to {destination}")
            return True

        except FileNotFoundError:
            raise GitHubError("git not installed or not in PATH")
        except subprocess.CalledProcessError as e:
            logger.error(f"[WIZ] Clone failed: {e.stderr.decode()}")
            raise GitHubNetworkError(f"Failed to clone {owner}/{repo}")
        except subprocess.TimeoutExpired:
            raise GitHubNetworkError(f"Clone timeout for {owner}/{repo}")

    def pull_repo(self, local_path: Path) -> bool:
        """
        Pull latest changes from remote (requires git).

        Args:
            local_path: Local repository path

        Returns:
            True if successful
        """
        import subprocess

        local_path = Path(local_path)
        if not (local_path / ".git").exists():
            raise GitHubError(f"Not a git repository: {local_path}")

        try:
            subprocess.run(
                ["git", "-C", str(local_path), "pull", "--depth", "1"],
                check=True,
                capture_output=True,
                timeout=300,
            )
            logger.info(f"[WIZ] Pulled {local_path}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"[WIZ] Pull failed: {e.stderr.decode()}")
            raise GitHubNetworkError(f"Failed to pull {local_path}")
        except subprocess.TimeoutExpired:
            raise GitHubNetworkError(f"Pull timeout for {local_path}")

    # ========== Workflow Operations ==========

    def list_workflows(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """
        List GitHub Actions workflows.

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
        data = self._make_request("GET", f"/repos/{owner}/{repo}/actions/workflows")
        workflows = []
        for item in data.get("workflows", []):
            workflows.append(
                {
                    "id": item.get("id"),
                    "name": item.get("name"),
                    "path": item.get("path"),
                    "state": item.get("state"),
                }
            )
        return workflows

    def run_workflow(
        self,
        owner: str,
        repo: str,
        workflow_id: str,
        ref: str = "main",
        inputs: Dict[str, str] = None,
    ) -> str:
        """
        Trigger workflow execution.

        Args:
            owner: GitHub org
            repo: Repository
            workflow_id: Workflow name or ID
            ref: Branch/tag
            inputs: Workflow input variables

        Returns:
            run_id for polling

        Raises:
            GitHubError: Workflow not found or cannot run
        """
        payload = {
            "ref": ref,
        }
        if inputs:
            payload["inputs"] = inputs

        data = self._make_request(
            "POST",
            f"/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
            json=payload,
        )

        # GitHub returns 204 No Content on success
        # We need to fetch the latest run
        logger.info(f"[WIZ] Triggered workflow {workflow_id} on {owner}/{repo}")

        # Get latest run ID (may take a moment to appear)
        import time

        time.sleep(1)  # Wait for workflow to be created

        runs = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/actions/runs",
            params={
                "workflow_id": workflow_id,
                "event": "workflow_dispatch",
                "status": "queued",
                "per_page": 1,
            },
        )

        if runs.get("workflow_runs"):
            return str(runs["workflow_runs"][0]["id"])

        raise GitHubError(f"Could not find run for workflow {workflow_id}")

    def get_workflow_run(self, owner: str, repo: str, run_id: str) -> Dict[str, Any]:
        """
        Get workflow run status.

        Returns:
            {
                "id": run_id,
                "status": "queued|in_progress|completed",
                "conclusion": "success|failure|neutral|cancelled|...",
                "created_at": "...",
                "updated_at": "...",
                "html_url": "...",
                "artifacts_url": "..."
            }
        """
        data = self._make_request("GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}")
        return {
            "id": data.get("id"),
            "status": data.get("status"),
            "conclusion": data.get("conclusion"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "html_url": data.get("html_url"),
            "artifacts_url": data.get("artifacts_url"),
        }

    def download_artifacts(
        self, owner: str, repo: str, run_id: str, destination: Path
    ) -> List[str]:
        """
        Download all artifacts from workflow run.

        Args:
            owner: GitHub org
            repo: Repository
            run_id: Workflow run ID
            destination: Local directory

        Returns:
            List of downloaded file paths
        """
        import zipfile
        import io

        destination = Path(destination)
        destination.mkdir(parents=True, exist_ok=True)

        # Get artifacts
        data = self._make_request(
            "GET", f"/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
        )

        downloaded = []
        for artifact in data.get("artifacts", []):
            if artifact.get("expired"):
                logger.warning(f"[WIZ] Artifact {artifact['name']} expired")
                continue

            # Download artifact zip
            url = artifact.get("archive_download_url")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # Extract zip
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                zf.extractall(destination / artifact["name"])
                downloaded.append(str(destination / artifact["name"]))

            logger.info(f"[WIZ] Downloaded artifact: {artifact['name']}")

        return downloaded

    # ========== Release Operations ==========

    def create_release(
        self,
        owner: str,
        repo: str,
        tag: str,
        name: str = None,
        body: str = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a GitHub Release.

        Args:
            owner: GitHub org
            repo: Repository
            tag: Git tag
            name: Release name (defaults to tag)
            body: Release notes (markdown)
            draft: If true, release is draft
            prerelease: If true, marked as pre-release

        Returns:
            {
                "id": release_id,
                "tag_name": "v1.1.0",
                "name": "Release 1.1.0",
                "html_url": "https://github.com/.../releases/tag/v1.1.0",
                "upload_url": "https://uploads.github.com/...",
                "assets": []
            }
        """
        payload = {
            "tag_name": tag,
            "name": name or tag,
            "body": body or "",
            "draft": draft,
            "prerelease": prerelease,
        }

        data = self._make_request(
            "POST", f"/repos/{owner}/{repo}/releases", json=payload
        )

        return {
            "id": data.get("id"),
            "tag_name": data.get("tag_name"),
            "name": data.get("name"),
            "html_url": data.get("html_url"),
            "upload_url": data.get("upload_url"),
            "assets": data.get("assets", []),
        }

    def upload_release_asset(
        self,
        upload_url: str,
        file_path: Path,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, Any]:
        """
        Upload asset to release.

        Args:
            upload_url: From create_release()
            file_path: Local file
            content_type: MIME type

        Returns:
            {
                "id": asset_id,
                "name": "file.tcz",
                "size": 1234567,
                "browser_download_url": "https://..."
            }
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise GitHubError(f"File not found: {file_path}")

        # Clean up upload URL template
        upload_url = upload_url.replace("{?name,label}", "")

        with open(file_path, "rb") as f:
            data = self._make_request(
                "POST",
                upload_url,
                params={"name": file_path.name},
                headers={"Content-Type": content_type},
                data=f.read(),
            )

        return {
            "id": data.get("id"),
            "name": data.get("name"),
            "size": data.get("size"),
            "browser_download_url": data.get("browser_download_url"),
        }

    def list_releases(
        self, owner: str, repo: str, prerelease: bool = None
    ) -> List[Dict[str, Any]]:
        """List releases for repository"""
        data = self._make_request("GET", f"/repos/{owner}/{repo}/releases")
        releases = []
        for item in data if isinstance(data, list) else []:
            if prerelease is not None and item.get("prerelease") != prerelease:
                continue
            releases.append(
                {
                    "id": item.get("id"),
                    "tag_name": item.get("tag_name"),
                    "name": item.get("name"),
                    "html_url": item.get("html_url"),
                    "prerelease": item.get("prerelease"),
                    "created_at": item.get("created_at"),
                }
            )
        return releases

    def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get latest release"""
        data = self._make_request("GET", f"/repos/{owner}/{repo}/releases/latest")
        return {
            "id": data.get("id"),
            "tag_name": data.get("tag_name"),
            "name": data.get("name"),
            "html_url": data.get("html_url"),
            "created_at": data.get("created_at"),
        }

    # ========== File Operations ==========

    def get_file_content(
        self, owner: str, repo: str, path: str, ref: str = "main"
    ) -> str:
        """
        Get file contents from repository.

        Args:
            owner: GitHub org
            repo: Repository
            path: File path
            ref: Branch/tag/commit

        Returns:
            File contents as string
        """
        import base64

        data = self._make_request(
            "GET", f"/repos/{owner}/{repo}/contents/{path}", params={"ref": ref}
        )

        if data.get("encoding") == "base64":
            return base64.b64decode(data.get("content", "")).decode("utf-8")

        return data.get("content", "")

    def get_tree(
        self, owner: str, repo: str, ref: str = "main", recursive: bool = False
    ) -> List[Dict[str, Any]]:
        """Get repository file tree"""
        data = self._make_request(
            "GET",
            f"/repos/{owner}/{repo}/git/trees/{ref}",
            params={"recursive": "1" if recursive else "0"},
        )

        tree = []
        for item in data.get("tree", []):
            tree.append(
                {
                    "path": item.get("path"),
                    "type": item.get("type"),  # blob or tree
                    "size": item.get("size"),
                    "url": item.get("url"),
                }
            )
        return tree
