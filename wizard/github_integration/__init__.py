"""
Wizard GitHub Integration

Provides GitHub API client, repository synchronization, workflow management,
and release publishing for uDOS.

Classes:
    GitHubClient - REST API wrapper for GitHub operations
    RepoSync - Repository cloning and updating
    WorkflowRunner - CI/CD workflow execution
    ReleaseManager - GitHub release publishing

Usage:
    from wizard.github_integration import GitHubClient
    client = GitHubClient(token="ghp_xxx", owner="uDOS")
    repos = client.list_repositories("uDOS")
"""

from .client import GitHubClient
from .repo_sync import RepoSync
from .workflow_runner import WorkflowRunner
from .release_manager import ReleaseManager
from .plugin_discovery import PluginDiscovery, PluginMetadata

__all__ = [
    "GitHubClient",
    "RepoSync",
    "WorkflowRunner",
    "ReleaseManager",
    "PluginDiscovery",
    "PluginMetadata",
]

__version__ = "1.0.0"
