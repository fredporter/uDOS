"""
Path Constants for uDOS v1.2.12+

Centralized path management to eliminate hardcoding.
Use these constants instead of string literals like "sandbox/", "memory/".

Example:
    from core.utils.paths import PATHS
    
    # ✅ Good
    user_file = PATHS.MEMORY_USER / "USER.UDT"
    
    # ❌ Bad
    user_file = Path("sandbox/user/USER.UDT")
"""

from pathlib import Path
from typing import Dict


class PathConstants:
    """Centralized path constants for uDOS workspace"""
    
    # Root directories
    ROOT = Path(__file__).parent.parent.parent  # Project root
    PROJECT_ROOT = ROOT  # Alias for compatibility
    CORE = ROOT / "core"
    EXTENSIONS = ROOT / "extensions"
    KNOWLEDGE = ROOT / "knowledge"
    MEMORY = ROOT / "memory"
    DEV = ROOT / "dev"
    WIKI = ROOT / "wiki"
    
    # Core subdirectories
    CORE_DATA = CORE / "data"
    CORE_COMMANDS = CORE / "commands"
    CORE_RUNTIME = CORE / "runtime"
    CORE_SERVICES = CORE / "services"
    CORE_UTILS = CORE / "utils"
    
    # Memory subdirectories (v1.2.12 structure)
    MEMORY_UCODE = MEMORY / "ucode"
    MEMORY_UCODE_SCRIPTS = MEMORY_UCODE / "scripts"
    MEMORY_UCODE_TESTS = MEMORY_UCODE / "tests"
    MEMORY_UCODE_SANDBOX = MEMORY_UCODE / "sandbox"
    MEMORY_UCODE_STDLIB = MEMORY_UCODE / "stdlib"
    MEMORY_UCODE_EXAMPLES = MEMORY_UCODE / "examples"
    MEMORY_UCODE_ADVENTURES = MEMORY_UCODE / "adventures"
    
    MEMORY_WORKFLOWS = MEMORY / "workflows"
    MEMORY_WORKFLOWS_MISSIONS = MEMORY_WORKFLOWS / "missions"
    MEMORY_WORKFLOWS_CHECKPOINTS = MEMORY_WORKFLOWS / "checkpoints"
    MEMORY_WORKFLOWS_STATE = MEMORY_WORKFLOWS / "state"
    
    MEMORY_SYSTEM = MEMORY / "system"
    MEMORY_SYSTEM_USER = MEMORY_SYSTEM / "user"
    MEMORY_SYSTEM_THEMES = MEMORY_SYSTEM / "themes"
    
    MEMORY_BANK = MEMORY / "bank"
    MEMORY_BANK_PRIVATE = MEMORY_BANK / "private"
    MEMORY_BANK_BARTER = MEMORY_BANK / "barter"
    
    MEMORY_SHARED = MEMORY / "shared"
    MEMORY_SHARED_PUBLIC = MEMORY_SHARED / "public"
    MEMORY_SHARED_GROUPS = MEMORY_SHARED / "groups"
    MEMORY_SHARED_METADATA = MEMORY_SHARED / "metadata"
    
    MEMORY_LOGS = MEMORY / "logs"
    MEMORY_SESSIONS = MEMORY / "sessions"
    MEMORY_MISSIONS = MEMORY / "missions"
    MEMORY_CHECKLISTS = MEMORY / "checklists"
    MEMORY_DOCS = MEMORY / "docs"
    MEMORY_DRAFTS = MEMORY / "drafts"
    MEMORY_DRAFTS_ASCII = MEMORY_DRAFTS / "ascii"
    MEMORY_DRAFTS_SVG = MEMORY_DRAFTS / "svg"
    MEMORY_DRAFTS_TELETEXT = MEMORY_DRAFTS / "teletext"
    
    # Deprecated paths (for migration/compatibility)
    DEPRECATED_SANDBOX = ROOT / ".archive" / "deprecated-root" / "sandbox-legacy"
    
    # Common file paths
    USER_PROFILE = MEMORY_SYSTEM_USER / "USER.UDT"
    WORKFLOW_CONFIG = MEMORY_WORKFLOWS / "config.json"
    WORKFLOW_STATE = MEMORY_WORKFLOWS / "state" / "current.json"
    CHECKLIST_STATE = MEMORY_SYSTEM_USER / "checklist_state.json"
    WEBHOOKS_CONFIG = MEMORY_SYSTEM / "webhooks.json"
    KNOWLEDGE_GAPS_REPORT = MEMORY_SYSTEM / "knowledge-gaps-report.json"
    KNOWLEDGE_QUALITY_REPORT = MEMORY_SYSTEM / "knowledge-quality-report.json"
    KNOWLEDGE_QUALITY_HISTORY = MEMORY_SYSTEM / "knowledge-quality-history.json"
    KNOWLEDGE_QUALITY_DASHBOARD = MEMORY_SYSTEM / "knowledge-quality-dashboard.html"
    RESOURCE_STATE = MEMORY_BANK / "system" / "resource-state.json"
    
    @classmethod
    def get_writable_dirs(cls) -> set:
        """Get set of directories that are writable by users"""
        return {
            str(cls.MEMORY),
            str(cls.MEMORY_UCODE_SCRIPTS),
            str(cls.MEMORY_UCODE_SANDBOX),
            str(cls.MEMORY_WORKFLOWS),
            str(cls.MEMORY_SYSTEM_USER),
            str(cls.MEMORY_BANK),
            str(cls.MEMORY_SHARED),
            str(cls.MEMORY_LOGS),
            str(cls.MEMORY_DRAFTS),
        }
    
    @classmethod
    def get_workspace_map(cls) -> Dict[str, Dict[str, str]]:
        """Get workspace directory mapping for legacy compatibility"""
        return {
            'memory': {
                'path': str(cls.MEMORY),
                'description': 'User workspace (unified in v1.1.13)'
            },
            'ucode': {
                'path': str(cls.MEMORY_UCODE),
                'description': 'uPY scripts and tests'
            },
            'workflows': {
                'path': str(cls.MEMORY_WORKFLOWS),
                'description': 'Workflow automation'
            },
            'system': {
                'path': str(cls.MEMORY_SYSTEM_USER),
                'description': 'System configuration'
            }
        }


# Global instance for easy importing
PATHS = PathConstants()
