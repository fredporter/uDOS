"""
Groovebox Pack Manager - Wizard Server Service
===============================================

Manages sound pack distribution for the Groovebox extension:
- Pack validation and indexing
- Storage and retrieval
- Version tracking
- Download statistics

Part of uDOS Wizard Server v1.0.1.4+

Directory Structure:
  wizard/catalog/groovebox/
  ├── index.json              # Pack catalog index
  ├── packs/
  │   ├── 808-classic-v1.0.0.tar.gz
  │   ├── 303-acid-v1.0.0.tar.gz
  │   └── ...
  └── uploads/                # Pending review
      └── ...
"""

import json
import tarfile
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

from wizard.services.logging_api import get_logger

logger = get_logger("wizard-pack-manager")


@dataclass
class PackMetadata:
    """Sound pack metadata."""

    id: str
    name: str
    version: str
    author: str
    description: str
    license: str
    instruments: int
    size_bytes: int
    checksum: str
    tags: List[str] = field(default_factory=list)
    downloads: int = 0
    created: str = ""
    updated: str = ""
    verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PackMetadata":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class PackManager:
    """
    Wizard Server pack manager for Groovebox sound distribution.

    Features:
    - Pack catalog indexing
    - Upload validation
    - Download serving
    - Statistics tracking
    """

    def __init__(self, catalog_root: Optional[Path] = None):
        """
        Initialize pack manager.

        Args:
            catalog_root: Root path for catalog storage
        """
        self.root = (
            catalog_root or Path(__file__).parent.parent / "catalog" / "groovebox"
        )
        self.packs_dir = self.root / "packs"
        self.uploads_dir = self.root / "uploads"
        self.index_path = self.root / "index.json"

        # Ensure directories
        self._ensure_directories()

        # Load index
        self._index: Dict[str, PackMetadata] = {}
        self._load_index()

        logger.info(f"[WIZ] PackManager initialized: {self.root}")

    def _ensure_directories(self):
        """Create required directories."""
        for path in [self.packs_dir, self.uploads_dir]:
            path.mkdir(parents=True, exist_ok=True)

    def _load_index(self):
        """Load pack index from disk."""
        if self.index_path.exists():
            try:
                data = json.loads(self.index_path.read_text())
                self._index = {
                    k: PackMetadata.from_dict(v)
                    for k, v in data.get("packs", {}).items()
                }
                logger.info(f"[WIZ] Loaded {len(self._index)} packs from index")
            except Exception as e:
                logger.error(f"[WIZ] Failed to load index: {e}")
                self._index = {}
        else:
            self._index = {}
            self._save_index()

    def _save_index(self):
        """Save pack index to disk."""
        data = {
            "version": "1.0.0",
            "updated": datetime.now().isoformat(),
            "packs": {k: v.to_dict() for k, v in self._index.items()},
        }
        self.index_path.write_text(json.dumps(data, indent=2))

    # === Catalog Operations ===

    def list_packs(
        self, tag: Optional[str] = None, verified_only: bool = False
    ) -> List[PackMetadata]:
        """
        List available packs.

        Args:
            tag: Filter by tag
            verified_only: Only show verified packs

        Returns:
            List of pack metadata
        """
        packs = list(self._index.values())

        if tag:
            packs = [p for p in packs if tag.lower() in [t.lower() for t in p.tags]]

        if verified_only:
            packs = [p for p in packs if p.verified]

        # Sort by downloads (popularity)
        packs.sort(key=lambda p: p.downloads, reverse=True)

        return packs

    def get_pack(self, pack_id: str) -> Optional[PackMetadata]:
        """Get pack metadata by ID."""
        return self._index.get(pack_id)

    def search_packs(self, query: str) -> List[PackMetadata]:
        """
        Search packs by name, description, or tags.

        Args:
            query: Search query

        Returns:
            Matching packs
        """
        query_lower = query.lower()
        results = []

        for pack in self._index.values():
            if (
                query_lower in pack.name.lower()
                or query_lower in pack.description.lower()
                or any(query_lower in t.lower() for t in pack.tags)
            ):
                results.append(pack)

        return results

    # === Download Operations ===

    def get_pack_path(self, pack_id: str) -> Optional[Path]:
        """
        Get filesystem path to pack archive.

        Args:
            pack_id: Pack identifier

        Returns:
            Path to .tar.gz file or None
        """
        pack = self._index.get(pack_id)
        if not pack:
            return None

        archive_name = f"{pack_id}-v{pack.version}.tar.gz"
        path = self.packs_dir / archive_name

        return path if path.exists() else None

    def record_download(self, pack_id: str):
        """Record a download for statistics."""
        if pack_id in self._index:
            self._index[pack_id].downloads += 1
            self._save_index()

    # === Upload Operations ===

    def validate_pack(self, archive_path: Path) -> Tuple[bool, str, Optional[Dict]]:
        """
        Validate an uploaded pack archive.

        Args:
            archive_path: Path to .tar.gz file

        Returns:
            (valid, message, manifest_data)
        """
        if not archive_path.exists():
            return False, "File not found", None

        if not archive_path.suffix == ".gz":
            return False, "Must be .tar.gz archive", None

        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                # Check for manifest
                manifest_member = None
                for member in tar.getmembers():
                    if member.name.endswith("manifest.json"):
                        manifest_member = member
                        break

                if not manifest_member:
                    return False, "Missing manifest.json", None

                # Extract and parse manifest
                f = tar.extractfile(manifest_member)
                if not f:
                    return False, "Cannot read manifest.json", None

                manifest = json.loads(f.read().decode("utf-8"))

                # Validate required fields
                required = ["id", "name", "version", "author", "license", "instruments"]
                missing = [k for k in required if k not in manifest]
                if missing:
                    return False, f"Missing fields: {missing}", None

                # Check for samples directory
                has_samples = any(
                    "samples/" in m.name and m.isfile() for m in tar.getmembers()
                )
                if not has_samples:
                    return False, "No samples found in archive", None

                return True, "Valid pack", manifest

        except tarfile.ReadError:
            return False, "Invalid tar.gz archive", None
        except json.JSONDecodeError:
            return False, "Invalid manifest.json", None
        except Exception as e:
            return False, f"Validation error: {e}", None

    def add_pack(
        self, archive_path: Path, manifest: Dict[str, Any], verified: bool = False
    ) -> Tuple[bool, str]:
        """
        Add a validated pack to the catalog.

        Args:
            archive_path: Path to validated archive
            manifest: Pack manifest data
            verified: Whether pack is verified

        Returns:
            (success, message)
        """
        pack_id = manifest["id"]
        version = manifest["version"]

        # Check for duplicates
        if pack_id in self._index:
            existing = self._index[pack_id]
            if existing.version == version:
                return False, f"Pack {pack_id} v{version} already exists"

        # Calculate checksum
        checksum = hashlib.sha256(archive_path.read_bytes()).hexdigest()[:16]

        # Move to packs directory
        archive_name = f"{pack_id}-v{version}.tar.gz"
        dest_path = self.packs_dir / archive_name
        shutil.copy2(archive_path, dest_path)

        # Create metadata
        metadata = PackMetadata(
            id=pack_id,
            name=manifest["name"],
            version=version,
            author=manifest["author"],
            description=manifest.get("description", ""),
            license=manifest["license"],
            instruments=len(manifest.get("instruments", {})),
            size_bytes=dest_path.stat().st_size,
            checksum=checksum,
            tags=manifest.get("tags", []),
            downloads=0,
            created=datetime.now().isoformat(),
            updated=datetime.now().isoformat(),
            verified=verified,
        )

        self._index[pack_id] = metadata
        self._save_index()

        logger.info(f"[WIZ] Added pack: {pack_id} v{version}")
        return True, f"Added {pack_id} v{version}"

    def remove_pack(self, pack_id: str) -> Tuple[bool, str]:
        """
        Remove a pack from the catalog.

        Args:
            pack_id: Pack identifier

        Returns:
            (success, message)
        """
        if pack_id not in self._index:
            return False, f"Pack not found: {pack_id}"

        pack = self._index[pack_id]
        archive_name = f"{pack_id}-v{pack.version}.tar.gz"
        archive_path = self.packs_dir / archive_name

        # Remove file
        if archive_path.exists():
            archive_path.unlink()

        # Remove from index
        del self._index[pack_id]
        self._save_index()

        logger.info(f"[WIZ] Removed pack: {pack_id}")
        return True, f"Removed {pack_id}"

    # === Statistics ===

    def get_stats(self) -> Dict[str, Any]:
        """Get catalog statistics."""
        total_downloads = sum(p.downloads for p in self._index.values())
        total_size = sum(p.size_bytes for p in self._index.values())

        return {
            "total_packs": len(self._index),
            "verified_packs": sum(1 for p in self._index.values() if p.verified),
            "total_downloads": total_downloads,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "tags": self._get_all_tags(),
        }

    def _get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for pack in self._index.values():
            tags.update(pack.tags)
        return sorted(tags)


# Singleton instance
_pack_manager: Optional[PackManager] = None


def get_pack_manager() -> PackManager:
    """Get or create pack manager singleton."""
    global _pack_manager
    if _pack_manager is None:
        _pack_manager = PackManager()
    return _pack_manager


# === Built-in Packs ===


def create_builtin_catalog():
    """
    Create built-in pack entries (metadata only).

    These represent packs that ship with uDOS or are
    generated from the Groovebox engine.
    """
    manager = get_pack_manager()

    # 808 Classic (built-in)
    if "808-classic" not in manager._index:
        manager._index["808-classic"] = PackMetadata(
            id="808-classic",
            name="808 Classic",
            version="1.0.0",
            author="uDOS",
            description="Classic TR-808 drum machine sounds. The essential foundation for any beat.",
            license="CC0",
            instruments=8,
            size_bytes=0,  # Built-in, no download
            checksum="builtin",
            tags=["drums", "808", "classic", "builtin"],
            downloads=0,
            created="2026-01-01T00:00:00",
            updated="2026-01-01T00:00:00",
            verified=True,
        )
        manager._save_index()
        logger.info("[WIZ] Created built-in 808-classic entry")


if __name__ == "__main__":
    # Test
    manager = PackManager(Path("/tmp/test_catalog"))
    create_builtin_catalog()

    print("Pack Manager Test")
    print("=" * 40)
    print(f"Packs: {len(manager.list_packs())}")
    print(f"Stats: {manager.get_stats()}")
