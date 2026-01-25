"""
Mesh Sync Service
=================

Handles synchronization between Wizard Server and mesh devices.

Features:
- Knowledge sync (bidirectional)
- Configuration sync
- Feed distribution
- Conflict resolution

Sync Protocol:
1. Device sends sync request with version vector
2. Wizard calculates delta (changes since device's version)
3. Wizard sends delta to device
4. Device applies delta and sends acknowledgment
5. Wizard updates device's sync version

Version: v1.0.0.0
Date: 2026-01-06
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading

from wizard.services.logging_manager import get_logger

logger = get_logger("wizard-mesh-sync")

# Paths
WIZARD_DATA = Path(__file__).parent.parent.parent / "memory" / "wizard"
SYNC_STATE_FILE = WIZARD_DATA / "sync_state.json"
KNOWLEDGE_ROOT = Path(__file__).parent.parent.parent / "knowledge"


class SyncItemType(Enum):
    """Types of syncable items."""

    KNOWLEDGE = "knowledge"
    CONFIG = "config"
    FEED = "feed"
    NOTIFICATION = "notification"


@dataclass
class SyncItem:
    """Item to be synced."""

    id: str
    type: SyncItemType
    path: str
    version: int
    hash: str
    modified_at: str
    data: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        return d


@dataclass
class SyncDelta:
    """Changes to sync to a device."""

    from_version: int
    to_version: int
    items: List[SyncItem]
    deleted_ids: List[str]
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from_version": self.from_version,
            "to_version": self.to_version,
            "items": [i.to_dict() for i in self.items],
            "deleted_ids": self.deleted_ids,
            "timestamp": self.timestamp,
        }


class MeshSyncService:
    """
    Mesh synchronization service.

    Manages bidirectional sync between Wizard and devices.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Ensure data directory
        WIZARD_DATA.mkdir(parents=True, exist_ok=True)

        # Global sync version (increments on any change)
        self.global_version: int = 0

        # Track item versions
        self.item_versions: Dict[str, int] = {}

        # Deleted items (tracked for sync)
        self.deleted_items: Set[str] = set()

        # Load state
        self._load_state()

        logger.info(
            f"[MESH] MeshSyncService initialized at version {self.global_version}"
        )

    def _load_state(self):
        """Load sync state from disk."""
        if SYNC_STATE_FILE.exists():
            try:
                with open(SYNC_STATE_FILE) as f:
                    data = json.load(f)
                    self.global_version = data.get("global_version", 0)
                    self.item_versions = data.get("item_versions", {})
                    self.deleted_items = set(data.get("deleted_items", []))
            except Exception as e:
                logger.error(f"[MESH] Failed to load sync state: {e}")

    def _save_state(self):
        """Save sync state to disk."""
        try:
            data = {
                "global_version": self.global_version,
                "item_versions": self.item_versions,
                "deleted_items": list(self.deleted_items),
                "updated_at": datetime.now().isoformat(),
            }
            with open(SYNC_STATE_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"[MESH] Failed to save sync state: {e}")

    # =========================================================================
    # Sync Operations
    # =========================================================================

    def get_delta(
        self, device_version: int, item_types: Optional[List[SyncItemType]] = None
    ) -> SyncDelta:
        """
        Calculate delta of changes since device's version.

        Args:
            device_version: Device's last sync version
            item_types: Types of items to include (default: all)

        Returns:
            SyncDelta with changes
        """
        items = []
        deleted = []

        # Get items modified since device_version
        for item_id, version in self.item_versions.items():
            if version > device_version:
                item = self._get_item(item_id)
                if item:
                    if item_types is None or item.type in item_types:
                        items.append(item)

        # Get deletions since device_version
        for item_id in self.deleted_items:
            # TODO: Track deletion version
            deleted.append(item_id)

        delta = SyncDelta(
            from_version=device_version,
            to_version=self.global_version,
            items=items,
            deleted_ids=deleted,
            timestamp=datetime.now().isoformat(),
        )

        logger.info(
            f"[MESH] Delta calculated: {len(items)} items, {len(deleted)} deletions"
        )

        return delta

    def apply_from_device(self, device_id: str, items: List[Dict[str, Any]]) -> int:
        """
        Apply changes received from a device.

        Args:
            device_id: ID of device sending changes
            items: List of items to apply

        Returns:
            New global version after applying changes
        """
        applied = 0

        for item_data in items:
            item_id = item_data.get("id")
            item_type = SyncItemType(item_data.get("type", "knowledge"))

            # Apply based on type
            if item_type == SyncItemType.KNOWLEDGE:
                if self._apply_knowledge_item(item_data):
                    applied += 1
            elif item_type == SyncItemType.NOTIFICATION:
                if self._apply_notification(item_data):
                    applied += 1

        if applied > 0:
            self.global_version += 1
            self._save_state()
            logger.info(
                f"[MESH] Applied {applied} items from {device_id}, new version: {self.global_version}"
            )

        return self.global_version

    def register_change(self, item_id: str, item_type: SyncItemType):
        """
        Register a local change for sync.

        Call this when content is modified locally.
        """
        self.global_version += 1
        self.item_versions[item_id] = self.global_version
        self._save_state()

        logger.debug(
            f"[MESH] Registered change: {item_id} at version {self.global_version}"
        )

    def register_deletion(self, item_id: str):
        """Register item deletion for sync."""
        self.global_version += 1
        self.deleted_items.add(item_id)
        if item_id in self.item_versions:
            del self.item_versions[item_id]
        self._save_state()

        logger.debug(f"[MESH] Registered deletion: {item_id}")

    # =========================================================================
    # Item Retrieval
    # =========================================================================

    def _get_item(self, item_id: str) -> Optional[SyncItem]:
        """Get sync item by ID."""
        # Parse item ID to determine type and path
        if item_id.startswith("knowledge:"):
            return self._get_knowledge_item(item_id)
        elif item_id.startswith("config:"):
            return self._get_config_item(item_id)
        return None

    def _get_knowledge_item(self, item_id: str) -> Optional[SyncItem]:
        """Get knowledge item for sync."""
        # item_id format: knowledge:category/topic
        path_part = item_id.replace("knowledge:", "")
        file_path = KNOWLEDGE_ROOT / f"{path_part}.md"

        if not file_path.exists():
            return None

        content = file_path.read_text()
        content_hash = hashlib.md5(content.encode()).hexdigest()

        return SyncItem(
            id=item_id,
            type=SyncItemType.KNOWLEDGE,
            path=str(file_path.relative_to(KNOWLEDGE_ROOT)),
            version=self.item_versions.get(item_id, 0),
            hash=content_hash,
            modified_at=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            data=content,
        )

    def _get_config_item(self, item_id: str) -> Optional[SyncItem]:
        """Get config item for sync."""
        # TODO: Implement config sync
        return None

    # =========================================================================
    # Apply Items
    # =========================================================================

    def _apply_knowledge_item(self, item_data: Dict[str, Any]) -> bool:
        """Apply knowledge item from device."""
        path = item_data.get("path")
        content = item_data.get("data")

        if not path or not content:
            return False

        file_path = self._safe_knowledge_path(path)
        if not file_path:
            logger.warning(f"[MESH] Rejected unsafe knowledge path: {path}")
            return False

        # Check for conflicts
        if file_path.exists():
            existing = file_path.read_text()
            existing_hash = hashlib.md5(existing.encode()).hexdigest()
            incoming_hash = item_data.get("hash")

            if existing_hash != incoming_hash:
                # Conflict - for now, newer wins
                # TODO: Implement proper conflict resolution
                logger.warning(f"[MESH] Conflict detected for {path}")

        # Write content
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        # Update version tracking
        item_id = f"knowledge:{path.replace('.md', '')}"
        self.item_versions[item_id] = self.global_version

        return True

    def _safe_knowledge_path(self, rel_path: str) -> Optional[Path]:
        """Validate and resolve a knowledge path safely."""
        if not rel_path or rel_path.startswith(("/", "\\")):
            return None
        if ".." in rel_path.split("/"):
            return None
        if not rel_path.endswith(".md"):
            return None
        base = KNOWLEDGE_ROOT.resolve()
        target = (KNOWLEDGE_ROOT / rel_path).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            return None
        return target

    def _apply_notification(self, item_data: Dict[str, Any]) -> bool:
        """Apply notification from device."""
        # TODO: Store in notification system
        return True

    # =========================================================================
    # Knowledge Scanning
    # =========================================================================

    def scan_knowledge(self) -> List[str]:
        """
        Scan knowledge directory and register all items.

        Call on startup to ensure all knowledge is tracked.
        """
        items = []

        for md_file in KNOWLEDGE_ROOT.rglob("*.md"):
            rel_path = md_file.relative_to(KNOWLEDGE_ROOT)
            item_id = f"knowledge:{str(rel_path).replace('.md', '')}"

            if item_id not in self.item_versions:
                self.item_versions[item_id] = self.global_version
                items.append(item_id)

        if items:
            self._save_state()
            logger.info(f"[MESH] Scanned {len(items)} new knowledge items")

        return items


# Singleton accessor
_mesh_sync: Optional[MeshSyncService] = None


def get_mesh_sync() -> MeshSyncService:
    """Get mesh sync service instance."""
    global _mesh_sync
    if _mesh_sync is None:
        _mesh_sync = MeshSyncService()
    return _mesh_sync
