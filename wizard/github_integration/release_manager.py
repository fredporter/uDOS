"""
GitHub Release Manager

Publish releases and manage distribution artifacts (TCZ, ISO, etc).
Supports semantic versioning, changelog generation, and multi-file uploads.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from .client import GitHubClient, GitHubError
from core.services.logging_service import get_logger

logger = get_logger("github-releases")


class ReleaseManager:
    """Manage GitHub releases and artifacts"""

    def __init__(
        self,
        client: GitHubClient,
        owner: str = None,
        artifact_types: Dict[str, str] = None,
    ):
        """
        Initialize release manager.

        Args:
            client: GitHubClient instance
            owner: Default GitHub owner
            artifact_types: Map of artifact name → MIME type
                Defaults: {"tcz": "application/x-tcz", "iso": "application/x-iso"}
        """
        self.client = client
        self.owner = owner or client.owner

        self.artifact_types = artifact_types or {
            "tcz": "application/x-tcz",
            "iso": "application/x-iso",
            "tar.gz": "application/gzip",
            "zip": "application/zip",
        }

    def list_releases(
        self, repo: str, prerelease: bool = None, limit: int = 20
    ) -> List[Dict[str, any]]:
        """
        List releases.

        Args:
            repo: Repository name
            prerelease: Filter by pre-release status
            limit: Max releases to return

        Returns:
            List of release dicts
        """
        try:
            releases = self.client.list_releases(
                self.owner, repo, prerelease=prerelease
            )
            return releases[:limit]
        except GitHubError as e:
            logger.error(f"[WIZ] Failed to list releases: {e}")
            return []

    def get_latest_release(self, repo: str) -> Optional[Dict[str, any]]:
        """Get latest release"""
        try:
            return self.client.get_latest_release(self.owner, repo)
        except GitHubError as e:
            logger.error(f"[WIZ] Failed to get latest release: {e}")
            return None

    def create_release(
        self,
        repo: str,
        tag: str,
        name: str = None,
        body: str = None,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Optional[Dict[str, any]]:
        """
        Create release.

        Args:
            repo: Repository name
            tag: Git tag (e.g., "v1.1.0")
            name: Release name (defaults to tag)
            body: Release notes (markdown)
            draft: If True, release is draft
            prerelease: If True, marked as pre-release

        Returns:
            Release dict with upload_url, or None on error
        """
        try:
            logger.info(f"[WIZ] Creating release {tag} for {self.owner}/{repo}")

            release = self.client.create_release(
                self.owner,
                repo,
                tag,
                name=name or tag,
                body=body or f"Release {tag}",
                draft=draft,
                prerelease=prerelease,
            )

            logger.info(f"[WIZ] Created release: {release.get('html_url')}")
            return release

        except GitHubError as e:
            logger.error(f"[WIZ] Failed to create release: {e}")
            return None

    def publish_release(
        self,
        repo: str,
        tag: str,
        name: str = None,
        body: str = None,
        prerelease: bool = False,
    ) -> Optional[Dict[str, any]]:
        """
        Publish release (non-draft).

        Args:
            repo: Repository name
            tag: Git tag
            name: Release name
            body: Release notes
            prerelease: If True, marked as pre-release

        Returns:
            Release dict or None on error
        """
        return self.create_release(
            repo, tag, name=name, body=body, draft=False, prerelease=prerelease
        )

    def upload_artifacts(
        self, repo: str, tag: str, artifacts: List[Path], force_create: bool = False
    ) -> Dict[str, Tuple[bool, str]]:
        """
        Upload multiple artifacts to release.

        Args:
            repo: Repository name
            tag: Git tag
            artifacts: List of file paths
            force_create: Create release if doesn't exist

        Returns:
            {
                "core-v1.0.0.tar.gz": (True, "https://github.com/.../download/..."),
                "app-v1.0.0.iso": (False, "File not found"),
                ...
            }
        """
        # Get release or create
        release = self._get_or_create_release(repo, tag, force_create)
        if not release:
            return {
                str(a.name): (False, "Could not get/create release") for a in artifacts
            }

        upload_url = release.get("upload_url")
        results = {}

        for artifact_path in artifacts:
            artifact_path = Path(artifact_path)
            results[artifact_path.name] = self._upload_artifact(
                upload_url, artifact_path
            )

        return results

    def _get_or_create_release(
        self, repo: str, tag: str, force_create: bool = False
    ) -> Optional[Dict[str, any]]:
        """Get release by tag or create if force_create=True"""
        releases = self.list_releases(repo, limit=100)

        # Find existing release
        for release in releases:
            if release.get("tag_name") == tag:
                return release

        # Create if not found
        if force_create:
            logger.info(f"[WIZ] Release not found, creating {tag}")
            return self.create_release(repo, tag)

        return None

    def _upload_artifact(
        self, upload_url: str, artifact_path: Path
    ) -> Tuple[bool, str]:
        """Upload single artifact"""
        artifact_path = Path(artifact_path)

        if not artifact_path.exists():
            return (False, "File not found")

        try:
            # Determine MIME type
            content_type = self._get_content_type(artifact_path)

            logger.info(f"[WIZ] Uploading {artifact_path.name}")

            asset = self.client.upload_release_asset(
                upload_url, artifact_path, content_type=content_type
            )

            download_url = asset.get("browser_download_url")
            logger.info(f"[WIZ] Uploaded: {download_url}")
            return (True, download_url)

        except GitHubError as e:
            logger.error(f"[WIZ] Upload failed: {e}")
            return (False, str(e))

    def _get_content_type(self, file_path: Path) -> str:
        """Determine MIME type from filename"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lstrip(".")

        # Check full suffix first (e.g., tar.gz)
        if file_path.name.endswith(".tar.gz"):
            return self.artifact_types.get("tar.gz", "application/gzip")

        # Check single suffix
        return self.artifact_types.get(suffix, "application/octet-stream")

    def generate_changelog(
        self, repo: str, from_tag: str = None, to_tag: str = "HEAD"
    ) -> str:
        """
        Generate changelog between tags using git commits.

        Args:
            repo: Repository name
            from_tag: Starting tag (defaults to previous release)
            to_tag: Ending tag (defaults to HEAD)

        Returns:
            Markdown changelog
        """
        try:
            import subprocess

            # Find previous release if not specified
            if not from_tag:
                releases = self.list_releases(repo, limit=100)
                if len(releases) > 1:
                    from_tag = releases[1].get("tag_name")  # Second most recent
                else:
                    return "No previous releases found"

            # Get git log between tags
            log_cmd = subprocess.run(
                ["git", "log", f"{from_tag}..{to_tag}", "--oneline"],
                capture_output=True,
                text=True,
                cwd=Path("."),
            )

            if log_cmd.returncode != 0:
                return f"Error: {log_cmd.stderr}"

            # Format as markdown
            lines = log_cmd.stdout.strip().split("\n")
            changelog = "## Changes\n\n"

            for line in lines:
                if line:
                    # Parse commit hash and message
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        commit_hash, message = parts
                        changelog += f"- {message} ([{commit_hash[:7]}](https://github.com/{self.owner}/{repo}/commit/{commit_hash}))\n"

            return changelog or "No commits found"

        except Exception as e:
            logger.error(f"[WIZ] Failed to generate changelog: {e}")
            return f"Error generating changelog: {e}"

    def publish_with_changelog(
        self,
        repo: str,
        tag: str,
        name: str = None,
        from_tag: str = None,
        artifacts: List[Path] = None,
        prerelease: bool = False,
    ) -> Tuple[bool, str]:
        """
        Publish release with auto-generated changelog and artifacts.

        Args:
            repo: Repository name
            tag: Git tag
            name: Release name
            from_tag: Previous tag for changelog
            artifacts: List of artifact files
            prerelease: If True, mark as pre-release

        Returns:
            (success: bool, message: str)
        """
        try:
            # Generate changelog
            changelog = self.generate_changelog(repo, from_tag=from_tag, to_tag=tag)

            # Create release
            release = self.publish_release(
                repo, tag, name=name or tag, body=changelog, prerelease=prerelease
            )

            if not release:
                return (False, "Failed to create release")

            # Upload artifacts
            if artifacts:
                results = self.upload_artifacts(
                    repo, tag, artifacts, force_create=False
                )
                failed = [k for k, (success, _) in results.items() if not success]
                if failed:
                    return (False, f"Failed to upload: {', '.join(failed)}")

            url = release.get("html_url")
            return (True, f"Published: {url}")

        except Exception as e:
            logger.error(f"[WIZ] Publish failed: {e}")
            return (False, str(e))
