#!/usr/bin/env python3
"""
uDOS Extension Manager v1.1.8
Automatic extension discovery, validation, and health monitoring.

Scans extensions/ directories for extension.json manifests and manages
extension lifecycle with comprehensive health checks.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ExtensionStatus(Enum):
    """Extension health status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class ExtensionCategory(Enum):
    """Extension categories."""
    CORE = "core"
    BUNDLED = "bundled"
    NATIVE = "native"
    CLONED = "cloned"
    PLAY = "play"
    WEB = "web"
    CLOUD = "cloud"


@dataclass
class ExtensionMetadata:
    """Validated extension metadata."""
    id: str
    name: str
    version: str
    description: str
    author: str
    license: str
    category: str
    type: str
    status: ExtensionStatus

    # Paths
    manifest_path: Path
    extension_dir: Path

    # Dependencies
    dependencies: Dict[str, Any] = field(default_factory=dict)
    requires_api: Dict[str, Any] = field(default_factory=dict)

    # Capabilities
    provides_commands: List[Dict] = field(default_factory=list)
    provides_services: List[Dict] = field(default_factory=list)
    provides_api_endpoints: List[Dict] = field(default_factory=list)

    # Configuration
    configuration: Dict[str, Any] = field(default_factory=dict)
    activation: Dict[str, Any] = field(default_factory=dict)

    # Health tracking
    loaded_at: Optional[datetime] = None
    last_health_check: Optional[datetime] = None
    health_status: str = "unknown"
    error_count: int = 0
    last_error: Optional[str] = None

    # Performance metrics
    load_time_ms: float = 0.0
    total_invocations: int = 0
    avg_response_time_ms: float = 0.0


class ExtensionValidator:
    """Validates extension.json manifests against schema."""

    REQUIRED_FIELDS = [
        'id', 'name', 'version', 'description', 'author',
        'license', 'category', 'type', 'status'
    ]

    VALID_CATEGORIES = ['core', 'bundled', 'native', 'cloned', 'play', 'web', 'cloud', 'api']
    VALID_TYPES = ['service', 'command', 'interface', 'integration', 'tool']
    VALID_STATUSES = ['active', 'inactive', 'experimental', 'deprecated']

    @staticmethod
    def validate(manifest: Dict[str, Any], manifest_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate extension manifest.

        Args:
            manifest: Parsed extension.json content
            manifest_path: Path to manifest file

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required fields
        for field in ExtensionValidator.REQUIRED_FIELDS:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")

        if errors:
            return False, errors

        # Validate category
        category = manifest.get('category', '').lower()
        if category not in ExtensionValidator.VALID_CATEGORIES:
            errors.append(f"Invalid category: {category}. Must be one of {ExtensionValidator.VALID_CATEGORIES}")

        # Validate type
        ext_type = manifest.get('type', '').lower()
        if ext_type not in ExtensionValidator.VALID_TYPES:
            errors.append(f"Invalid type: {ext_type}. Must be one of {ExtensionValidator.VALID_TYPES}")

        # Validate status
        status = manifest.get('status', '').lower()
        if status not in ExtensionValidator.VALID_STATUSES:
            errors.append(f"Invalid status: {status}. Must be one of {ExtensionValidator.VALID_STATUSES}")

        # Validate version format (semantic versioning)
        version = manifest.get('version', '')
        if version and not ExtensionValidator._is_valid_version(version):
            errors.append(f"Invalid version format: {version}. Expected format: X.Y.Z")

        # Validate dependencies
        if 'dependencies' in manifest:
            deps = manifest['dependencies']
            if not isinstance(deps, dict):
                errors.append("'dependencies' must be an object/dict")
            else:
                # Check uDOS version requirement
                if 'uDOS' in deps:
                    udos_version = deps['uDOS']
                    if not ExtensionValidator._is_valid_version_constraint(udos_version):
                        errors.append(f"Invalid uDOS version constraint: {udos_version}")

        # Validate provides section
        if 'provides' in manifest:
            provides = manifest['provides']

            # Validate commands
            if 'commands' in provides:
                if not isinstance(provides['commands'], list):
                    errors.append("'provides.commands' must be an array")
                else:
                    for i, cmd in enumerate(provides['commands']):
                        if not isinstance(cmd, dict):
                            errors.append(f"'provides.commands[{i}]' must be an object")
                        elif 'name' not in cmd:
                            errors.append(f"'provides.commands[{i}]' missing required field 'name'")

            # Validate services
            if 'services' in provides:
                if not isinstance(provides['services'], list):
                    errors.append("'provides.services' must be an array")
                else:
                    for i, svc in enumerate(provides['services']):
                        if not isinstance(svc, dict):
                            errors.append(f"'provides.services[{i}]' must be an object")
                        elif 'name' not in svc:
                            errors.append(f"'provides.services[{i}]' missing required field 'name'")

        # Validate files section
        if 'files' in manifest:
            files = manifest['files']
            extension_dir = manifest_path.parent

            # Check if main file exists
            if 'main' in files:
                main_file = extension_dir / files['main']
                if not main_file.exists():
                    errors.append(f"Main file not found: {files['main']}")

        return len(errors) == 0, errors

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version follows semantic versioning (X.Y.Z)."""
        parts = version.split('.')
        if len(parts) != 3:
            return False
        return all(part.isdigit() for part in parts)

    @staticmethod
    def _is_valid_version_constraint(constraint: str) -> bool:
        """Check if version constraint is valid (>=X.Y.Z, ==X.Y.Z, etc.)."""
        # Remove operators
        operators = ['>=', '<=', '==', '>', '<', '!=']
        version = constraint
        for op in operators:
            version = version.replace(op, '')
        version = version.strip()

        # Check if remaining part is valid version
        return ExtensionValidator._is_valid_version(version)


class ExtensionDiscovery:
    """Discovers extensions in extensions/ directories."""

    EXTENSION_DIRS = [
        'extensions/core',
        'extensions/bundled',
        'extensions/native',
        'extensions/cloned',
        'extensions/play',
        'extensions/web',
        'extensions/cloud',
        'extensions/api'
    ]

    def __init__(self, root_dir: Path = None):
        """
        Initialize extension discovery.

        Args:
            root_dir: uDOS root directory (defaults to current working directory)
        """
        self.root = root_dir or Path.cwd()
        self.validator = ExtensionValidator()

    def scan_all(self) -> Dict[str, ExtensionMetadata]:
        """
        Scan all extension directories for extension.json manifests.

        Returns:
            Dictionary of extension_id -> ExtensionMetadata
        """
        discovered = {}

        for ext_dir in self.EXTENSION_DIRS:
            dir_path = self.root / ext_dir
            if not dir_path.exists():
                continue

            # Find all extension.json files in this directory
            manifests = list(dir_path.rglob('extension.json'))

            for manifest_path in manifests:
                try:
                    metadata = self._load_extension(manifest_path)
                    if metadata:
                        discovered[metadata.id] = metadata
                except Exception as e:
                    print(f"⚠️  Failed to load {manifest_path}: {e}")

        return discovered

    def _load_extension(self, manifest_path: Path) -> Optional[ExtensionMetadata]:
        """
        Load and validate an extension from its manifest.

        Args:
            manifest_path: Path to extension.json

        Returns:
            ExtensionMetadata if valid, None otherwise
        """
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {manifest_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Error reading {manifest_path}: {e}")
            return None

        # Validate manifest
        is_valid, errors = self.validator.validate(manifest, manifest_path)

        if not is_valid:
            print(f"❌ Invalid manifest: {manifest_path}")
            for error in errors:
                print(f"   • {error}")
            return None

        # Parse status
        status_str = manifest.get('status', 'unknown').lower()
        try:
            status = ExtensionStatus(status_str)
        except ValueError:
            status = ExtensionStatus.UNKNOWN

        # Create metadata object
        metadata = ExtensionMetadata(
            id=manifest['id'],
            name=manifest['name'],
            version=manifest['version'],
            description=manifest['description'],
            author=manifest['author'],
            license=manifest['license'],
            category=manifest['category'],
            type=manifest['type'],
            status=status,
            manifest_path=manifest_path,
            extension_dir=manifest_path.parent,
            dependencies=manifest.get('dependencies', {}),
            requires_api=manifest.get('requires_api', {}),
            provides_commands=manifest.get('provides', {}).get('commands', []),
            provides_services=manifest.get('provides', {}).get('services', []),
            provides_api_endpoints=manifest.get('provides', {}).get('api_endpoints', []),
            configuration=manifest.get('configuration', {}),
            activation=manifest.get('activation', {})
        )

        return metadata


class ExtensionHealthMonitor:
    """Monitors extension health and performance."""

    def __init__(self):
        self.metrics = {}

    def check_extension(self, metadata: ExtensionMetadata) -> Tuple[bool, str]:
        """
        Perform health check on extension.

        Args:
            metadata: Extension metadata

        Returns:
            Tuple of (is_healthy, status_message)
        """
        checks = []

        # Check 1: Main file exists
        if 'main' in metadata.configuration or metadata.provides_services:
            main_file = self._get_main_file(metadata)
            if main_file and main_file.exists():
                checks.append(('main_file', True, 'Main file exists'))
            else:
                checks.append(('main_file', False, f'Main file not found: {main_file}'))

        # Check 2: Required dependencies
        if metadata.dependencies:
            udos_version = metadata.dependencies.get('uDOS')
            if udos_version:
                # Compare with current uDOS version (simplified check)
                checks.append(('dependencies', True, 'Dependencies declared'))

        # Check 3: API key requirements
        if metadata.requires_api:
            for api_name, api_config in metadata.requires_api.items():
                if api_config.get('required', False):
                    key_env = api_config.get('key_env')
                    if key_env:
                        import os
                        if os.getenv(key_env):
                            checks.append((f'api_{api_name}', True, f'{key_env} present'))
                        else:
                            checks.append((f'api_{api_name}', False, f'{key_env} not set'))

        # Check 4: Extension directory exists
        if metadata.extension_dir.exists():
            checks.append(('directory', True, 'Extension directory exists'))
        else:
            checks.append(('directory', False, 'Extension directory missing'))

        # Calculate overall health
        total_checks = len(checks)
        passed_checks = sum(1 for _, passed, _ in checks if passed)

        if total_checks == 0:
            return True, "No checks performed"

        is_healthy = passed_checks == total_checks

        # Build status message
        if is_healthy:
            status_msg = f"All checks passed ({passed_checks}/{total_checks})"
        else:
            failed = [check for check, passed, msg in checks if not passed]
            status_msg = f"Failed: {', '.join(failed)} ({passed_checks}/{total_checks} passed)"

        # Update metadata
        metadata.last_health_check = datetime.now()
        metadata.health_status = "healthy" if is_healthy else "unhealthy"

        return is_healthy, status_msg

    def _get_main_file(self, metadata: ExtensionMetadata) -> Optional[Path]:
        """Get main file path for extension."""
        # Try to find main file from various sources
        if metadata.provides_services:
            service = metadata.provides_services[0]
            if 'file' in service:
                return metadata.extension_dir / service['file']

        # Check configuration
        if 'main' in metadata.configuration:
            return metadata.extension_dir / metadata.configuration['main']

        return None


class ExtensionManager:
    """
    Central extension manager with discovery, validation, and monitoring.

    Usage:
        >>> manager = ExtensionManager()
        >>> manager.discover_extensions()
        >>> extensions = manager.list_extensions()
        >>> health = manager.get_health_report()
    """

    def __init__(self, root_dir: Path = None):
        """
        Initialize extension manager.

        Args:
            root_dir: uDOS root directory
        """
        self.root = root_dir or Path.cwd()
        self.discovery = ExtensionDiscovery(self.root)
        self.health_monitor = ExtensionHealthMonitor()
        self.extensions: Dict[str, ExtensionMetadata] = {}
        self.loaded_extensions: Dict[str, Any] = {}

    def discover_extensions(self, verbose: bool = True) -> int:
        """
        Discover all extensions in extensions/ directories.

        Args:
            verbose: Print discovery progress

        Returns:
            Number of extensions discovered
        """
        if verbose:
            print("🔍 Scanning for extensions...")

        self.extensions = self.discovery.scan_all()

        if verbose:
            print(f"✅ Discovered {len(self.extensions)} extensions")

            # Group by category
            by_category = {}
            for ext in self.extensions.values():
                category = ext.category
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(ext)

            for category, exts in sorted(by_category.items()):
                print(f"   {category}: {len(exts)} extension(s)")

        return len(self.extensions)

    def list_extensions(self, category: str = None, status: ExtensionStatus = None) -> List[ExtensionMetadata]:
        """
        List extensions with optional filtering.

        Args:
            category: Filter by category
            status: Filter by status

        Returns:
            List of matching extensions
        """
        results = list(self.extensions.values())

        if category:
            results = [ext for ext in results if ext.category == category]

        if status:
            results = [ext for ext in results if ext.status == status]

        return sorted(results, key=lambda e: (e.category, e.name))

    def get_extension(self, extension_id: str) -> Optional[ExtensionMetadata]:
        """Get extension by ID."""
        return self.extensions.get(extension_id)

    def check_health(self, extension_id: str = None) -> Dict[str, Any]:
        """
        Check health of extension(s).

        Args:
            extension_id: Check specific extension, or all if None

        Returns:
            Health report dictionary
        """
        if extension_id:
            # Check single extension
            ext = self.get_extension(extension_id)
            if not ext:
                return {'error': f'Extension not found: {extension_id}'}

            is_healthy, status_msg = self.health_monitor.check_extension(ext)

            return {
                'extension_id': extension_id,
                'healthy': is_healthy,
                'status': status_msg,
                'last_check': ext.last_health_check.isoformat() if ext.last_health_check else None
            }
        else:
            # Check all extensions
            results = {}
            healthy_count = 0

            for ext_id, ext in self.extensions.items():
                is_healthy, status_msg = self.health_monitor.check_extension(ext)
                results[ext_id] = {
                    'healthy': is_healthy,
                    'status': status_msg
                }
                if is_healthy:
                    healthy_count += 1

            return {
                'total': len(self.extensions),
                'healthy': healthy_count,
                'unhealthy': len(self.extensions) - healthy_count,
                'extensions': results
            }

    def get_health_report(self) -> str:
        """
        Generate formatted health report.

        Returns:
            Multi-line string with health status
        """
        if not self.extensions:
            return "No extensions discovered. Run discover_extensions() first."

        lines = []
        lines.append("\n🏥 Extension Health Report")
        lines.append("=" * 60)

        health_data = self.check_health()
        total = health_data['total']
        healthy = health_data['healthy']
        unhealthy = health_data['unhealthy']

        lines.append(f"Total Extensions: {total}")
        lines.append(f"Healthy: {healthy} ✅")
        lines.append(f"Unhealthy: {unhealthy} ❌")
        lines.append("")

        # Detail each extension
        for ext_id, ext_health in health_data['extensions'].items():
            ext = self.get_extension(ext_id)
            if ext:
                status_icon = "✅" if ext_health['healthy'] else "❌"
                lines.append(f"{status_icon} {ext.name} ({ext_id})")
                lines.append(f"   Category: {ext.category} | Version: {ext.version}")
                lines.append(f"   Status: {ext_health['status']}")

                if ext.provides_commands:
                    cmd_names = [cmd['name'] for cmd in ext.provides_commands]
                    lines.append(f"   Commands: {', '.join(cmd_names)}")

                lines.append("")

        return "\n".join(lines)

    def get_commands_registry(self) -> Dict[str, Dict[str, Any]]:
        """
        Build command registry from all active extensions.

        Returns:
            Dictionary mapping command names to extension metadata
        """
        registry = {}

        for ext in self.extensions.values():
            if ext.status != ExtensionStatus.ACTIVE:
                continue

            for cmd in ext.provides_commands:
                cmd_name = cmd.get('name')
                if cmd_name:
                    registry[cmd_name] = {
                        'extension_id': ext.id,
                        'extension_name': ext.name,
                        'description': cmd.get('description', ''),
                        'syntax': cmd.get('syntax', ''),
                        'examples': cmd.get('examples', []),
                        'category': ext.category
                    }

        return registry


# Singleton instance
_extension_manager = None


def get_extension_manager(root_dir: Path = None) -> ExtensionManager:
    """Get singleton extension manager instance."""
    global _extension_manager
    if _extension_manager is None:
        _extension_manager = ExtensionManager(root_dir)
    return _extension_manager


# CLI interface for testing
if __name__ == "__main__":
    import sys

    manager = get_extension_manager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == 'discover':
            count = manager.discover_extensions()
            print(f"\n✅ Discovered {count} extensions\n")

        elif command == 'list':
            manager.discover_extensions(verbose=False)
            extensions = manager.list_extensions()

            print("\n📦 Installed Extensions")
            print("=" * 60)

            for ext in extensions:
                status_icon = "✅" if ext.status == ExtensionStatus.ACTIVE else "⏸️"
                print(f"{status_icon} {ext.name} (v{ext.version})")
                print(f"   ID: {ext.id} | Category: {ext.category}")
                print(f"   {ext.description}")

                if ext.provides_commands:
                    cmds = [cmd['name'] for cmd in ext.provides_commands]
                    print(f"   Commands: {', '.join(cmds)}")

                print()

        elif command == 'health':
            manager.discover_extensions(verbose=False)
            print(manager.get_health_report())

        elif command == 'commands':
            manager.discover_extensions(verbose=False)
            registry = manager.get_commands_registry()

            print("\n⚙️  Extension Commands Registry")
            print("=" * 60)

            for cmd_name, cmd_info in sorted(registry.items()):
                print(f"• {cmd_name}")
                print(f"  Extension: {cmd_info['extension_name']}")
                print(f"  {cmd_info['description']}")
                if cmd_info['syntax']:
                    print(f"  Syntax: {cmd_info['syntax']}")
                print()

        else:
            print(f"Unknown command: {command}")
            print("Usage: python extension_manager.py [discover|list|health|commands]")

    else:
        # Default: show health report
        manager.discover_extensions()
        print(manager.get_health_report())
