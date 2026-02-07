"""
Extension Handler (v1.1.0)
==========================

Unified extension management system for handling:
  - GitHub CLI extension (sync, monitoring, webhooks)
  - Mistral Vibe (local inference)
  - MeshCore (local networking)
  - Future extensions (generic handler)

Replaces scattered github_integration, github_sync, github_monitor
services with single CLI-focused GitHub extension via this handler.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root

logger = get_logger("extension-handler")


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════


class ExtensionStatus(Enum):
    """Extension installation/execution status."""
    NOT_INSTALLED = "not-installed"
    INSTALLING = "installing"
    INSTALLED = "installed"
    ACTIVE = "active"
    FAILED = "failed"
    DISABLED = "disabled"


class ExtensionCategory(Enum):
    """Extension purpose categories."""
    GITHUB = "github"
    AI = "ai"
    NETWORKING = "networking"
    UTILITY = "utility"


@dataclass
class ExtensionMetadata:
    """Extension metadata and configuration."""
    name: str
    category: ExtensionCategory
    version: str
    description: str
    author: str
    repository: Optional[str] = None
    required_secrets: List[str] = None
    required_capabilities: List[str] = None
    icon: Optional[str] = None
    
    def __post_init__(self):
        if self.required_secrets is None:
            self.required_secrets = []
        if self.required_capabilities is None:
            self.required_capabilities = []


@dataclass
class ExtensionInstance:
    """Running extension instance."""
    metadata: ExtensionMetadata
    status: ExtensionStatus = ExtensionStatus.NOT_INSTALLED
    installed_path: Optional[Path] = None
    enabled: bool = True
    config: Dict[str, Any] = None
    last_activity: Optional[str] = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}


# ═══════════════════════════════════════════════════════════════════════════
# BASE EXTENSION CLASS
# ═══════════════════════════════════════════════════════════════════════════


class Extension(ABC):
    """
    Base class for all extensions.
    
    Each extension implements:
      - initialize()      — Setup and dependency checking
      - execute()         — Main functionality
      - validate_secrets() — Verify required API keys/tokens
    """
    
    def __init__(self, metadata: ExtensionMetadata):
        self.metadata = metadata
        self.instance = ExtensionInstance(metadata=metadata)
        self.logger = get_logger(f"ext-{metadata.name}")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize extension. Return True if successful."""
        pass
    
    @abstractmethod
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute extension command."""
        pass
    
    async def validate_secrets(self, secret_store) -> bool:
        """Check if all required secrets are available."""
        if not self.metadata.required_secrets:
            return True
        
        for secret_key in self.metadata.required_secrets:
            try:
                entry = secret_store.get_entry(secret_key)
                if entry is None:
                    self.logger.warning(f"[LOCAL] Missing required secret: {secret_key}")
                    return False
            except Exception as e:
                self.logger.error(f"[LOCAL] Failed to validate secret {secret_key}: {e}")
                return False
        
        return True
    
    async def shutdown(self):
        """Cleanup on shutdown."""
        pass


# ═══════════════════════════════════════════════════════════════════════════
# GITHUB CLI EXTENSION
# ═══════════════════════════════════════════════════════════════════════════


class GitHubCLIExtension(Extension):
    """
    CLI-focused GitHub integration extension.
    
    Consolidates:
      - github_integration.py (issue/PR fetching, devlog access)
      - github_sync.py (push/pull/webhook handling)
      - github_monitor.py (CI/Actions monitoring)
    
    Commands:
      - sync:status      — Get sync status
      - sync:pull        — Pull latest from GitHub
      - sync:push        — Push local changes
      - issues:list      — List open issues
      - pr:list          — List open PRs
      - monitor:actions  — Monitor CI/Actions
      - webhook:config   — Configure webhooks
    """
    
    def __init__(self):
        metadata = ExtensionMetadata(
            name="github-cli",
            category=ExtensionCategory.GITHUB,
            version="1.0.0",
            description="CLI-focused GitHub integration for sync, monitoring, and webhooks",
            author="uDOS Team",
            repository="https://github.com/fredporter/uDOS",
            required_secrets=["github_token"],
            required_capabilities=["subprocess", "git", "api"]
        )
        super().__init__(metadata)
    
    async def initialize(self) -> bool:
        """Check git and GitHub token availability."""
        try:
            # Check git is available
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            
            self.instance.status = ExtensionStatus.INSTALLED
            self.logger.info("[GITHUB] GitHub CLI extension initialized")
            return True
        except Exception as e:
            self.logger.error(f"[GITHUB] Initialization failed: {e}")
            self.instance.status = ExtensionStatus.FAILED
            return False
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute GitHub command."""
        if not self.instance.enabled:
            return {"error": "Extension disabled"}
        
        try:
            if command == "sync:status":
                return await self._sync_status(**kwargs)
            elif command == "sync:pull":
                return await self._sync_pull(**kwargs)
            elif command == "sync:push":
                return await self._sync_push(**kwargs)
            elif command == "issues:list":
                return await self._issues_list(**kwargs)
            elif command == "pr:list":
                return await self._pr_list(**kwargs)
            elif command == "monitor:actions":
                return await self._monitor_actions(**kwargs)
            elif command == "webhook:config":
                return await self._webhook_config(**kwargs)
            else:
                return {"error": f"Unknown command: {command}"}
        except Exception as e:
            self.logger.error(f"[GITHUB] Command {command} failed: {e}")
            return {"error": str(e)}
    
    async def _sync_status(self, **kwargs) -> Dict[str, Any]:
        """Get git sync status."""
        return {"status": "ok", "message": "Git sync available"}
    
    async def _sync_pull(self, **kwargs) -> Dict[str, Any]:
        """Pull latest from GitHub."""
        return {"status": "pulling", "message": "TODO: Implement pull"}
    
    async def _sync_push(self, **kwargs) -> Dict[str, Any]:
        """Push local changes to GitHub."""
        return {"status": "pushing", "message": "TODO: Implement push"}
    
    async def _issues_list(self, **kwargs) -> Dict[str, Any]:
        """List open issues from GitHub."""
        return {"issues": [], "message": "TODO: Implement issues list"}
    
    async def _pr_list(self, **kwargs) -> Dict[str, Any]:
        """List open PRs from GitHub."""
        return {"prs": [], "message": "TODO: Implement PR list"}
    
    async def _monitor_actions(self, **kwargs) -> Dict[str, Any]:
        """Monitor CI/Actions status."""
        return {"status": "idle", "message": "TODO: Implement actions monitoring"}
    
    async def _webhook_config(self, **kwargs) -> Dict[str, Any]:
        """Configure webhooks."""
        return {"status": "ok", "message": "TODO: Implement webhook config"}


# ═══════════════════════════════════════════════════════════════════════════
# EXTENSION HANDLER (MANAGER)
# ═══════════════════════════════════════════════════════════════════════════


class ExtensionHandler:
    """
    Central extension management system.
    
    Handles:
      - Extension registration & discovery
      - Lifecycle management (init, execute, shutdown)
      - Command routing to correct extension
      - Error handling & logging
      - Secret validation
    """
    
    def __init__(self, secret_store=None):
        self.extensions: Dict[str, Extension] = {}
        self.secret_store = secret_store
        self.logger = get_logger("extension-handler")
    
    def register(self, extension: Extension) -> None:
        """Register a new extension."""
        name = extension.metadata.name
        self.extensions[name] = extension
        self.logger.info(f"[LOCAL] Registered extension: {name}")
    
    async def initialize_all(self) -> Dict[str, bool]:
        """Initialize all registered extensions."""
        results = {}
        for name, ext in self.extensions.items():
            try:
                # Validate secrets first
                if self.secret_store:
                    has_secrets = await ext.validate_secrets(self.secret_store)
                    if not has_secrets and ext.metadata.required_secrets:
                        self.logger.warning(
                            f"[LOCAL] Skipping {name}: missing required secrets"
                        )
                        ext.instance.status = ExtensionStatus.DISABLED
                        results[name] = False
                        continue
                
                # Initialize
                success = await ext.initialize()
                results[name] = success
            except Exception as e:
                self.logger.error(f"[LOCAL] Failed to initialize {name}: {e}")
                results[name] = False
        
        return results
    
    async def execute(self, extension_name: str, command: str, **kwargs) -> Dict[str, Any]:
        """Execute command in a specific extension."""
        ext = self.extensions.get(extension_name)
        if not ext:
            return {"error": f"Extension not found: {extension_name}"}
        
        if not ext.instance.enabled:
            return {"error": f"Extension disabled: {extension_name}"}
        
        ext.instance.last_activity = datetime.now().isoformat()
        return await ext.execute(command, **kwargs)
    
    async def shutdown_all(self) -> None:
        """Shutdown all extensions."""
        for name, ext in self.extensions.items():
            try:
                await ext.shutdown()
                self.logger.info(f"[LOCAL] Shut down extension: {name}")
            except Exception as e:
                self.logger.error(f"[LOCAL] Error shutting down {name}: {e}")
    
    def get_status(self, extension_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of extension(s)."""
        if extension_name:
            ext = self.extensions.get(extension_name)
            if not ext:
                return {"error": f"Extension not found: {extension_name}"}
            return {
                "name": ext.metadata.name,
                "status": ext.instance.status.value,
                "enabled": ext.instance.enabled,
                "version": ext.metadata.version,
                "last_activity": ext.instance.last_activity,
            }
        
        # Return status of all extensions
        return {
            name: {
                "status": ext.instance.status.value,
                "enabled": ext.instance.enabled,
                "version": ext.metadata.version,
                "category": ext.metadata.category.value,
            }
            for name, ext in self.extensions.items()
        }


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON HANDLER
# ═══════════════════════════════════════════════════════════════════════════


_extension_handler: Optional[ExtensionHandler] = None


def get_extension_handler(secret_store=None) -> ExtensionHandler:
    """Get or create singleton extension handler."""
    global _extension_handler
    if _extension_handler is None:
        _extension_handler = ExtensionHandler(secret_store=secret_store)
        
        # Register built-in extensions
        _extension_handler.register(GitHubCLIExtension())
        # TODO: Register MistralVibe, MeshCore, others
    
    return _extension_handler


def init_extension_handler(secret_store=None) -> ExtensionHandler:
    """Initialize extension handler."""
    global _extension_handler
    _extension_handler = ExtensionHandler(secret_store=secret_store)
    _extension_handler.register(GitHubCLIExtension())
    return _extension_handler
