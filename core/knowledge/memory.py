"""
Memory Manager Service - v1.0.20
Unified interface for 4-Tier Memory System

Tier 1: Private   - Personal encrypted data (never shared)
Tier 2: Shared    - Explicitly shared with trusted contacts
Tier 3: Groups    - Community knowledge pools
Tier 4: Public    - Global knowledge bank (read-only)

Author: uDOS Development Team
Version: 1.0.20
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta


class MemoryTier(Enum):
    """Memory tier levels with privacy characteristics"""
    PRIVATE = "private"     # Tier 1: Never shared, encrypted
    SHARED = "shared"       # Tier 2: Explicitly shared
    GROUPS = "groups"       # Tier 3: Community knowledge
    PUBLIC = "public"       # Tier 4: Global knowledge bank


class PermissionLevel(Enum):
    """Permission levels for shared content"""
    NONE = "none"
    READ = "read"
    EDIT = "edit"
    FULL = "full"


class MemoryManager:
    """
    Unified interface for all 4 memory tiers

    Responsibilities:
    - Tier isolation and access control
    - Cross-tier search (respecting permissions)
    - Memory statistics and health
    - Backup and recovery coordination
    """

    def __init__(self, base_path: str = None):
        """
        Initialize MemoryManager

        Args:
            base_path: Base directory for memory system (defaults to ./memory)
        """
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), '..', '..', 'memory')

        self.base_path = Path(base_path).resolve()
        self.tiers = {
            MemoryTier.PRIVATE: self.base_path / 'private',
            MemoryTier.SHARED: self.base_path / 'shared',
            MemoryTier.GROUPS: self.base_path / 'groups',
            MemoryTier.PUBLIC: self.base_path / 'public'
        }

        # Ensure all tier directories exist
        for tier_path in self.tiers.values():
            tier_path.mkdir(parents=True, exist_ok=True)

        # Initialize metadata stores
        self.metadata_dir = self.base_path / '.metadata'
        self.metadata_dir.mkdir(exist_ok=True)

        # Access control lists
        self.acl_file = self.metadata_dir / 'access_control.json'
        self.acl = self._load_acl()

    def _load_acl(self) -> Dict:
        """Load access control list"""
        if self.acl_file.exists():
            with open(self.acl_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_acl(self):
        """Save access control list"""
        with open(self.acl_file, 'w') as f:
            json.dump(self.acl, f, indent=2)

    def get_tier_path(self, tier: MemoryTier) -> Path:
        """Get base path for a memory tier"""
        return self.tiers[tier]

    def check_tier_access(self, tier: MemoryTier, user_id: str = "owner") -> bool:
        """
        Check if user has access to a tier

        Args:
            tier: Memory tier to check
            user_id: User identifier (defaults to device owner)

        Returns:
            True if access granted, False otherwise
        """
        # Tier 1 (Private): Owner only
        if tier == MemoryTier.PRIVATE:
            return user_id == "owner"

        # Tier 4 (Public): Read access for all
        if tier == MemoryTier.PUBLIC:
            return True

        # Tier 2 (Shared) and Tier 3 (Groups): Check ACL
        tier_acl = self.acl.get(tier.value, {})
        return user_id in tier_acl or user_id == "owner"

    def get_tier_stats(self, tier: MemoryTier) -> Dict[str, Any]:
        """
        Get statistics for a memory tier

        Returns:
            Dictionary with tier statistics
        """
        tier_path = self.get_tier_path(tier)

        if not tier_path.exists():
            return {
                'tier': tier.value,
                'exists': False,
                'file_count': 0,
                'total_size': 0,
                'last_modified': None
            }

        file_count = 0
        total_size = 0
        last_modified = None

        for root, dirs, files in os.walk(tier_path):
            # Skip .gitignore and README.md
            files = [f for f in files if f not in ['.gitignore', 'README.md']]
            file_count += len(files)

            for file in files:
                file_path = Path(root) / file
                try:
                    stat = file_path.stat()
                    total_size += stat.st_size
                    file_time = datetime.fromtimestamp(stat.st_mtime)
                    if last_modified is None or file_time > last_modified:
                        last_modified = file_time
                except (OSError, IOError):
                    continue

        return {
            'tier': tier.value,
            'exists': True,
            'file_count': file_count,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'last_modified': last_modified.isoformat() if last_modified else None
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all memory tiers"""
        stats = {
            'timestamp': datetime.now().isoformat(),
            'base_path': str(self.base_path),
            'tiers': {}
        }

        total_files = 0
        total_size = 0

        for tier in MemoryTier:
            tier_stats = self.get_tier_stats(tier)
            stats['tiers'][tier.value] = tier_stats
            total_files += tier_stats['file_count']
            total_size += tier_stats['total_size']

        stats['total_files'] = total_files
        stats['total_size'] = total_size
        stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)

        return stats

    def search_tier(self, tier: MemoryTier, query: str,
                   file_pattern: str = "*.md") -> List[Dict[str, Any]]:
        """
        Search for files in a specific tier

        Args:
            tier: Memory tier to search
            query: Search query (filename or content)
            file_pattern: Glob pattern for files to search

        Returns:
            List of matching file dictionaries
        """
        tier_path = self.get_tier_path(tier)
        results = []

        if not tier_path.exists():
            return results

        # Search by filename
        for file_path in tier_path.rglob(file_pattern):
            if file_path.name in ['.gitignore', 'README.md']:
                continue

            rel_path = file_path.relative_to(tier_path)

            # Check if query matches filename
            if query.lower() in file_path.name.lower():
                results.append({
                    'tier': tier.value,
                    'path': str(rel_path),
                    'full_path': str(file_path),
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })

        return results

    def search_all_tiers(self, query: str, user_id: str = "owner",
                        file_pattern: str = "*.md") -> Dict[str, List[Dict]]:
        """
        Search across all accessible tiers

        Args:
            query: Search query
            user_id: User performing search
            file_pattern: File pattern to match

        Returns:
            Dictionary mapping tier names to search results
        """
        results = {}

        for tier in MemoryTier:
            # Check access
            if not self.check_tier_access(tier, user_id):
                results[tier.value] = {
                    'access': False,
                    'results': []
                }
                continue

            # Search tier
            tier_results = self.search_tier(tier, query, file_pattern)
            results[tier.value] = {
                'access': True,
                'results': tier_results,
                'count': len(tier_results)
            }

        return results

    def verify_tier_integrity(self, tier: MemoryTier) -> Dict[str, Any]:
        """
        Verify integrity of a memory tier

        Returns:
            Dictionary with verification results
        """
        tier_path = self.get_tier_path(tier)

        issues = []

        # Check if tier exists
        if not tier_path.exists():
            issues.append(f"Tier directory missing: {tier_path}")

        # Check for README
        readme = tier_path / 'README.md'
        if not readme.exists():
            issues.append(f"README.md missing in {tier.value}")

        # Check for .gitignore
        gitignore = tier_path / '.gitignore'
        if not gitignore.exists():
            issues.append(f".gitignore missing in {tier.value}")

        return {
            'tier': tier.value,
            'healthy': len(issues) == 0,
            'issues': issues,
            'checked_at': datetime.now().isoformat()
        }

    def verify_all_tiers(self) -> Dict[str, Any]:
        """Verify integrity of all memory tiers"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': True,
            'tiers': {}
        }

        for tier in MemoryTier:
            tier_health = self.verify_tier_integrity(tier)
            results['tiers'][tier.value] = tier_health
            if not tier_health['healthy']:
                results['overall_health'] = False

        return results

    def list_files(self, tier: MemoryTier, path: str = "",
                  file_pattern: str = "*") -> List[Dict[str, Any]]:
        """
        List files in a tier directory

        Args:
            tier: Memory tier
            path: Subdirectory within tier (optional)
            file_pattern: File pattern to match

        Returns:
            List of file dictionaries
        """
        tier_path = self.get_tier_path(tier)
        target_path = tier_path / path if path else tier_path

        if not target_path.exists():
            return []

        files = []
        for item in target_path.glob(file_pattern):
            if item.name in ['.gitignore', 'README.md', '.metadata']:
                continue

            rel_path = item.relative_to(tier_path)

            files.append({
                'name': item.name,
                'path': str(rel_path),
                'full_path': str(item),
                'is_dir': item.is_dir(),
                'size': item.stat().st_size if item.is_file() else 0,
                'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
            })

        return sorted(files, key=lambda x: (not x['is_dir'], x['name']))


def main():
    """Test MemoryManager functionality"""
    manager = MemoryManager()

    print("🧠 uDOS Memory Manager v1.0.20")
    print("=" * 50)

    # Show all tier stats
    stats = manager.get_all_stats()
    print(f"\n📊 Memory Statistics")
    print(f"Base Path: {stats['base_path']}")
    print(f"Total Files: {stats['total_files']}")
    print(f"Total Size: {stats['total_size_mb']} MB")

    print(f"\n📁 Tier Breakdown:")
    for tier_name, tier_stats in stats['tiers'].items():
        icon = {'private': '🔒', 'shared': '🤝', 'groups': '👥', 'public': '🌍'}.get(tier_name, '📂')
        print(f"\n  {icon} {tier_name.upper()}")
        print(f"    Files: {tier_stats['file_count']}")
        print(f"    Size: {tier_stats['total_size_mb']} MB")
        if tier_stats['last_modified']:
            print(f"    Modified: {tier_stats['last_modified']}")

    # Verify tier integrity
    print(f"\n🔍 Tier Integrity Check")
    health = manager.verify_all_tiers()
    status = "✅ HEALTHY" if health['overall_health'] else "⚠️  ISSUES FOUND"
    print(f"Overall: {status}")

    for tier_name, tier_health in health['tiers'].items():
        icon = '✅' if tier_health['healthy'] else '⚠️'
        print(f"  {icon} {tier_name}: ", end='')
        if tier_health['healthy']:
            print("OK")
        else:
            print(f"{len(tier_health['issues'])} issues")
            for issue in tier_health['issues']:
                print(f"      - {issue}")


if __name__ == "__main__":
    main()
