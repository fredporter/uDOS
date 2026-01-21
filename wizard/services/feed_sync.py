"""
Unified Feed Sync
=================

Synchronizes feeds (knowledge, notifications, commands) across mesh nodes.

Architecture:
- FeedSyncService manages bidirectional feed sync
- Feeds are treated as append-only logs with deduplication
- Priority items (high priority) sync immediately
- Normal items batch sync periodically

Feed Types:
- knowledge: Knowledge bank articles (full sync)
- notifications: User notifications (ephemeral, TTL-based)
- commands: Command history (optional sync)
- mesh: Mesh network events (auto-generated, no sync)

Version: v1.0.0.0
Date: 2026-01-06
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import threading
import asyncio

from wizard.services.logging_manager import get_logger

logger = get_logger("feed-sync")


class FeedType(Enum):
    """Types of syncable feeds."""

    KNOWLEDGE = "knowledge"
    NOTIFICATIONS = "notifications"
    COMMANDS = "commands"


class SyncPriority(Enum):
    """Sync priority levels."""

    IMMEDIATE = "immediate"  # Sync within seconds
    NORMAL = "normal"  # Batch sync (minutes)
    LOW = "low"  # Opportunistic sync


@dataclass
class FeedItem:
    """A syncable feed item."""

    id: str
    feed_type: FeedType
    title: str
    content: str
    timestamp: str
    priority: SyncPriority = SyncPriority.NORMAL
    source_node: str = ""
    ttl_hours: int = 0  # 0 = permanent
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["feed_type"] = self.feed_type.value
        d["priority"] = self.priority.value
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedItem":
        data["feed_type"] = FeedType(data.get("feed_type", "notifications"))
        data["priority"] = SyncPriority(data.get("priority", "normal"))
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def get_hash(self) -> str:
        """Get content hash for deduplication."""
        content = f"{self.feed_type.value}:{self.title}:{self.content}"
        return hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass
class FeedSyncState:
    """Sync state for a specific feed type."""

    feed_type: FeedType
    last_sync: str = ""
    sync_version: int = 0
    pending_items: List[str] = field(default_factory=list)  # Item IDs

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["feed_type"] = self.feed_type.value
        return d


class FeedSyncService:
    """
    Unified feed synchronization service.

    Manages bidirectional sync of feeds across mesh nodes.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        if hasattr(self, "_initialized"):
            return
        self._initialized = True

        # Storage paths
        self.data_dir = (
            Path(__file__).parent.parent.parent.parent / "memory" / "feed_sync"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Local node ID
        self.local_node_id = self._get_node_id()

        # Feed items (in-memory + persisted)
        self.items: Dict[str, FeedItem] = {}

        # Sync state per feed type
        self.sync_states: Dict[FeedType, FeedSyncState] = {
            ft: FeedSyncState(feed_type=ft) for ft in FeedType
        }

        # Pending outbound items
        self.outbound_queue: List[FeedItem] = []

        # Seen item hashes (deduplication)
        self.seen_hashes: Set[str] = set()

        # Load persisted state
        self._load_state()

        logger.info(f"[FEED] FeedSyncService initialized for node {self.local_node_id}")

    def _get_node_id(self) -> str:
        """Get local node ID."""
        node_file = self.data_dir.parent / "mesh" / "node_id"
        if node_file.exists():
            return node_file.read_text().strip()
        return "unknown"

    def _load_state(self):
        """Load persisted sync state."""
        state_file = self.data_dir / "sync_state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())

                # Load items
                for item_data in data.get("items", []):
                    item = FeedItem.from_dict(item_data)
                    self.items[item.id] = item
                    self.seen_hashes.add(item.get_hash())

                # Load sync states
                for state_data in data.get("sync_states", []):
                    ft = FeedType(state_data.get("feed_type"))
                    self.sync_states[ft] = FeedSyncState(
                        feed_type=ft,
                        last_sync=state_data.get("last_sync", ""),
                        sync_version=state_data.get("sync_version", 0),
                        pending_items=state_data.get("pending_items", []),
                    )

                logger.info(f"[FEED] Loaded {len(self.items)} items from state")
            except Exception as e:
                logger.error(f"[FEED] Failed to load state: {e}")

    def _save_state(self):
        """Persist sync state."""
        state_file = self.data_dir / "sync_state.json"
        try:
            data = {
                "items": [item.to_dict() for item in self.items.values()],
                "sync_states": [state.to_dict() for state in self.sync_states.values()],
                "updated_at": datetime.now().isoformat(),
            }
            state_file.write_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.error(f"[FEED] Failed to save state: {e}")

    # =========================================================================
    # Local Item Management
    # =========================================================================

    def add_item(self, item: FeedItem, sync: bool = True) -> bool:
        """
        Add a feed item locally.

        Args:
            item: Feed item to add
            sync: Whether to queue for sync

        Returns:
            True if item was added (not duplicate)
        """
        # Check for duplicates
        item_hash = item.get_hash()
        if item_hash in self.seen_hashes:
            logger.debug(f"[FEED] Duplicate item ignored: {item.id}")
            return False

        # Set source node
        if not item.source_node:
            item.source_node = self.local_node_id

        # Store
        self.items[item.id] = item
        self.seen_hashes.add(item_hash)

        # Queue for sync
        if sync:
            self.outbound_queue.append(item)

            # Immediate sync for high priority
            if item.priority == SyncPriority.IMMEDIATE:
                asyncio.create_task(self._sync_immediate(item))

        self._save_state()

        logger.info(f"[FEED] Added item: {item.title} ({item.feed_type.value})")
        return True

    def get_items(
        self,
        feed_type: Optional[FeedType] = None,
        limit: int = 50,
        since: Optional[str] = None,
    ) -> List[FeedItem]:
        """
        Get feed items.

        Args:
            feed_type: Filter by type
            limit: Max items to return
            since: Only items after this timestamp

        Returns:
            List of feed items
        """
        items = list(self.items.values())

        # Filter by type
        if feed_type:
            items = [i for i in items if i.feed_type == feed_type]

        # Filter by timestamp
        if since:
            items = [i for i in items if i.timestamp > since]

        # Filter expired items
        now = datetime.now()
        items = [
            i
            for i in items
            if i.ttl_hours == 0
            or datetime.fromisoformat(i.timestamp) + timedelta(hours=i.ttl_hours) > now
        ]

        # Sort by timestamp (newest first)
        items.sort(key=lambda x: x.timestamp, reverse=True)

        return items[:limit]

    def remove_item(self, item_id: str) -> bool:
        """Remove a feed item."""
        if item_id in self.items:
            item = self.items.pop(item_id)
            self._save_state()
            logger.info(f"[FEED] Removed item: {item.title}")
            return True
        return False

    # =========================================================================
    # Sync Operations
    # =========================================================================

    async def _sync_immediate(self, item: FeedItem):
        """Immediately sync a high-priority item."""
        try:
            from extensions.transport.meshcore.sync_bridge import get_sync_transport

            transport = get_sync_transport()

            await transport.broadcast_update(item.id, item.feed_type.value)
            logger.info(f"[FEED] Immediate sync: {item.title}")
        except Exception as e:
            logger.error(f"[FEED] Immediate sync failed: {e}")

    async def sync_outbound(self):
        """Sync pending outbound items to mesh."""
        if not self.outbound_queue:
            return

        # Get items to sync
        items_to_sync = self.outbound_queue.copy()
        self.outbound_queue.clear()

        logger.info(f"[FEED] Syncing {len(items_to_sync)} outbound items")

        try:
            from wizard.services.mesh_sync import get_mesh_sync, SyncItemType

            sync = get_mesh_sync()

            # Register each item with mesh sync
            for item in items_to_sync:
                sync.register_change(
                    f"feed:{item.feed_type.value}:{item.id}",
                    (
                        SyncItemType.NOTIFICATION
                        if item.feed_type == FeedType.NOTIFICATIONS
                        else SyncItemType.KNOWLEDGE
                    ),
                )

            # Update sync state
            for ft in FeedType:
                self.sync_states[ft].last_sync = datetime.now().isoformat()
                self.sync_states[ft].sync_version = sync.global_version

            self._save_state()

        except Exception as e:
            logger.error(f"[FEED] Outbound sync failed: {e}")
            # Re-queue items
            self.outbound_queue.extend(items_to_sync)

    def apply_inbound(self, items: List[Dict[str, Any]]) -> int:
        """
        Apply inbound feed items from mesh sync.

        Args:
            items: Feed items from remote node

        Returns:
            Number of items applied
        """
        applied = 0

        for item_data in items:
            try:
                item = FeedItem.from_dict(item_data)
                if self.add_item(item, sync=False):
                    applied += 1
            except Exception as e:
                logger.error(f"[FEED] Failed to apply inbound item: {e}")

        logger.info(f"[FEED] Applied {applied} inbound items")
        return applied

    def get_delta(self, since_version: int) -> List[FeedItem]:
        """
        Get feed items since a version (for sync response).

        Args:
            since_version: Sync version to get items since

        Returns:
            Items added since that version
        """
        # For now, return all items newer than the oldest sync state
        # A proper implementation would track version per item
        items = []

        for item in self.items.values():
            items.append(item)

        return items

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    def add_notification(
        self,
        title: str,
        content: str,
        priority: str = "normal",
        ttl_hours: int = 24,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeedItem:
        """
        Add a notification to the feed.

        Convenience method for creating notification items.
        """
        import uuid

        item = FeedItem(
            id=str(uuid.uuid4()),
            feed_type=FeedType.NOTIFICATIONS,
            title=title,
            content=content,
            timestamp=datetime.now().isoformat(),
            priority=(
                SyncPriority(priority)
                if priority in [p.value for p in SyncPriority]
                else SyncPriority.NORMAL
            ),
            ttl_hours=ttl_hours,
            metadata=metadata or {},
        )

        self.add_item(item)
        return item

    def add_knowledge_update(self, path: str, title: str, summary: str) -> FeedItem:
        """
        Add a knowledge update notification.

        Called when knowledge content is modified.
        """
        import uuid

        item = FeedItem(
            id=str(uuid.uuid4()),
            feed_type=FeedType.KNOWLEDGE,
            title=f"📚 {title}",
            content=summary,
            timestamp=datetime.now().isoformat(),
            priority=SyncPriority.NORMAL,
            ttl_hours=0,  # Permanent
            metadata={"path": path, "type": "update"},
        )

        self.add_item(item)
        return item


# Singleton accessor
_feed_sync: Optional[FeedSyncService] = None


def get_feed_sync() -> FeedSyncService:
    """Get feed sync service instance."""
    global _feed_sync
    if _feed_sync is None:
        _feed_sync = FeedSyncService()
    return _feed_sync
