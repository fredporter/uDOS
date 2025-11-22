"""
uDOS v1.0.11 - Extension Metadata Manager

Enhanced metadata system for extension management with validation,
dependency checking, and security features.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re


class ExtensionMetadataManager:
    """Manages extension metadata with enhanced validation and security."""

    def __init__(self, root_dir: Optional[Path] = None):
        """
        Initialize the metadata manager.

        Args:
            root_dir: Root directory of uDOS installation (defaults to auto-detect)
        """
        if root_dir is None:
            # Auto-detect root (assuming this file is in core/services/)
            self.root = Path(__file__).parent.parent.parent
        else:
            self.root = Path(root_dir)

        self.extensions_dir = self.root / "extensions"
        self.bundled_dir = self.extensions_dir / "bundled" / "web"
        self.cloned_dir = self.extensions_dir / "cloned"

        # Supported uDOS version for compatibility checks
        self.udos_version = "1.0.11"

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def load_manifest(self, manifest_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Load and validate the extension manifest.

        Args:
            manifest_path: Path to manifest file (defaults to bundled manifest)

        Returns:
            Dictionary containing manifest data or empty dict on error
        """
        if manifest_path is None:
            manifest_path = self.bundled_dir / "version-manifest.json"

        try:
            if not manifest_path.exists():
                self.logger.warning(f"Manifest not found: {manifest_path}")
                return {}

            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)

            # Validate manifest structure
            validation_result = self.validate_manifest(manifest)
            if not validation_result[0]:
                self.logger.error(f"Manifest validation failed: {validation_result[1]}")
                return {}

            return manifest

        except Exception as e:
            self.logger.error(f"Error loading manifest: {e}")
            return {}

    def validate_manifest(self, manifest: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate manifest structure and required fields.

        Args:
            manifest: Manifest dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['name', 'version', 'description', 'extensions']

        for field in required_fields:
            if field not in manifest:
                return False, f"Missing required field: {field}"

        # Validate extensions structure
        extensions = manifest.get('extensions', {})
        if not isinstance(extensions, dict):
            return False, "Extensions must be a dictionary"

        for ext_name, ext_info in extensions.items():
            validation = self.validate_extension_metadata(ext_name, ext_info)
            if not validation[0]:
                return False, f"Extension {ext_name}: {validation[1]}"

        return True, "Manifest is valid"

    def validate_extension_metadata(self, name: str, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate individual extension metadata.

        Args:
            name: Extension name
            metadata: Extension metadata dictionary

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['version', 'description']

        for field in required_fields:
            if field not in metadata:
                return False, f"Missing required field: {field}"

        # Validate version format (semantic versioning)
        version = metadata.get('version', '')
        if not self.validate_version_format(version):
            return False, f"Invalid version format: {version}"

        # Validate port if specified
        port = metadata.get('port')
        if port is not None:
            if not isinstance(port, int) or port < 1024 or port > 65535:
                return False, f"Invalid port: {port} (must be 1024-65535)"

        # Validate dependencies
        dependencies = metadata.get('dependencies', [])
        if dependencies and not isinstance(dependencies, list):
            return False, "Dependencies must be a list"

        return True, "Extension metadata is valid"

    def validate_version_format(self, version: str) -> bool:
        """
        Validate semantic version format (x.y.z).

        Args:
            version: Version string to validate

        Returns:
            True if valid, False otherwise
        """
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def check_compatibility(self, extension_metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if extension is compatible with current system.

        Args:
            extension_metadata: Extension metadata dictionary

        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        issues = []

        # Check uDOS version compatibility
        if 'compatibility' in extension_metadata:
            compatibility = extension_metadata['compatibility']

            if 'uDOS' in compatibility:
                required_udos = compatibility['uDOS']
                if not self.check_version_requirement(self.udos_version, required_udos):
                    issues.append(f"Requires uDOS {required_udos}, current: {self.udos_version}")

            # Check Python version
            if 'python' in compatibility:
                required_python = compatibility['python']
                current_python = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                if not self.check_version_requirement(current_python, required_python):
                    issues.append(f"Requires Python {required_python}, current: {current_python}")

        # Check dependencies
        dependencies = extension_metadata.get('dependencies', [])
        for dep in dependencies:
            if not self.check_dependency_available(dep):
                issues.append(f"Missing dependency: {dep}")

        return len(issues) == 0, issues

    def check_version_requirement(self, current: str, required: str) -> bool:
        """
        Check if current version meets requirement.

        Args:
            current: Current version string
            required: Required version string (may include operators like >=)

        Returns:
            True if requirement is met, False otherwise
        """
        try:
            # Simple implementation for basic requirements
            if required.startswith('>='):
                required_version = required[2:].strip()
                return self.compare_versions(current, required_version) >= 0
            elif required.startswith('>'):
                required_version = required[1:].strip()
                return self.compare_versions(current, required_version) > 0
            elif required.startswith('<='):
                required_version = required[2:].strip()
                return self.compare_versions(current, required_version) <= 0
            elif required.startswith('<'):
                required_version = required[1:].strip()
                return self.compare_versions(current, required_version) < 0
            elif required.startswith('=='):
                required_version = required[2:].strip()
                return self.compare_versions(current, required_version) == 0
            else:
                # Exact match
                return current == required
        except:
            return False

    def compare_versions(self, version1: str, version2: str) -> int:
        """
        Compare two semantic version strings.

        Args:
            version1: First version string
            version2: Second version string

        Returns:
            -1 if version1 < version2, 0 if equal, 1 if version1 > version2
        """
        try:
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]

            # Pad shorter version with zeros
            max_length = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_length - len(v1_parts)))
            v2_parts.extend([0] * (max_length - len(v2_parts)))

            for v1, v2 in zip(v1_parts, v2_parts):
                if v1 < v2:
                    return -1
                elif v1 > v2:
                    return 1

            return 0
        except:
            return 0

    def check_dependency_available(self, dependency: str) -> bool:
        """
        Check if a dependency is available.

        Args:
            dependency: Dependency name to check

        Returns:
            True if available, False otherwise
        """
        # Check for CSS frameworks
        if dependency.endswith('.css'):
            css_path = self.bundled_dir / "shared" / dependency
            return css_path.exists()

        # Check for Node.js dependencies (basic check)
        if dependency.startswith('node:'):
            # Would need more sophisticated Node.js dependency checking
            return True

        # Check for Python packages (basic check)
        try:
            __import__(dependency)
            return True
        except ImportError:
            return False

    def get_extension_security_info(self, extension_name: str) -> Dict[str, Any]:
        """
        Get security information for an extension.

        Args:
            extension_name: Name of the extension

        Returns:
            Dictionary with security information
        """
        security_info = {
            'risk_level': 'unknown',
            'permissions': [],
            'sandboxed': False,
            'verified': False,
            'last_scanned': None
        }

        # Basic risk assessment based on extension type and location
        manifest = self.load_manifest()
        if extension_name in manifest.get('extensions', {}):
            ext_data = manifest['extensions'][extension_name]

            # Bundled extensions are considered safer
            if (self.bundled_dir / extension_name).exists():
                security_info['risk_level'] = 'low'
                security_info['verified'] = True

            # External extensions need more scrutiny
            if ext_data.get('external', False):
                security_info['risk_level'] = 'medium'
                security_info['permissions'].append('external_network')

            # Extensions with ports need network permissions
            if ext_data.get('port'):
                security_info['permissions'].append('network_server')

        security_info['last_scanned'] = datetime.now().isoformat()
        return security_info

    def generate_extension_report(self, extension_name: str) -> str:
        """
        Generate a comprehensive report for an extension.

        Args:
            extension_name: Name of the extension

        Returns:
            Formatted report string
        """
        manifest = self.load_manifest()
        if extension_name not in manifest.get('extensions', {}):
            return f"❌ Extension '{extension_name}' not found in manifest."

        ext_data = manifest['extensions'][extension_name]
        security_info = self.get_extension_security_info(extension_name)
        compatibility = self.check_compatibility(ext_data)

        report = f"📊 COMPREHENSIVE EXTENSION REPORT: {extension_name}\n"
        report += "=" * 60 + "\n\n"

        # Basic information
        report += f"📦 NAME: {extension_name}\n"
        report += f"🏷️  VERSION: {ext_data.get('version', 'unknown')}\n"
        report += f"📝 DESCRIPTION: {ext_data.get('description', 'No description')}\n\n"

        # Compatibility check
        report += "🔍 COMPATIBILITY CHECK:\n"
        if compatibility[0]:
            report += "  ✅ Compatible with current system\n"
        else:
            report += "  ❌ Compatibility issues found:\n"
            for issue in compatibility[1]:
                report += f"    • {issue}\n"
        report += "\n"

        # Security assessment
        report += "🔒 SECURITY ASSESSMENT:\n"
        risk_color = {"low": "🟢", "medium": "🟡", "high": "🔴", "unknown": "⚪"}
        report += f"  Risk Level: {risk_color.get(security_info['risk_level'], '⚪')} {security_info['risk_level'].upper()}\n"

        if security_info['verified']:
            report += "  ✅ Verified extension\n"
        else:
            report += "  ⚠️  Unverified extension\n"

        if security_info['permissions']:
            report += "  🔑 Permissions:\n"
            for perm in security_info['permissions']:
                report += f"    • {perm}\n"
        report += "\n"

        # Dependencies
        dependencies = ext_data.get('dependencies', [])
        if dependencies:
            report += "📦 DEPENDENCIES:\n"
            for dep in dependencies:
                available = "✅" if self.check_dependency_available(dep) else "❌"
                report += f"  {available} {dep}\n"
            report += "\n"

        # File system check
        ext_path = self.bundled_dir / extension_name
        if ext_path.exists():
            report += f"📂 INSTALLATION STATUS: ✅ Installed\n"
            report += f"📍 LOCATION: {ext_path}\n"

            try:
                files = list(ext_path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                report += f"📄 FILES: {file_count}\n"
                report += f"💾 SIZE: {total_size / 1024:.1f} KB\n"
            except:
                pass
        else:
            report += f"📂 INSTALLATION STATUS: ❌ Not installed\n"

        return report


def main():
    """CLI interface for extension metadata manager."""
    import argparse

    parser = argparse.ArgumentParser(description='uDOS Extension Metadata Manager')
    parser.add_argument('--validate', action='store_true', help='Validate manifest')
    parser.add_argument('--report', metavar='EXT', help='Generate report for extension')
    parser.add_argument('--check-compatibility', metavar='EXT', help='Check extension compatibility')
    parser.add_argument('--security-info', metavar='EXT', help='Get security information')

    args = parser.parse_args()

    manager = ExtensionMetadataManager()

    if args.validate:
        manifest = manager.load_manifest()
        if manifest:
            validation = manager.validate_manifest(manifest)
            if validation[0]:
                print("✅ Manifest is valid")
            else:
                print(f"❌ Manifest validation failed: {validation[1]}")
        else:
            print("❌ Could not load manifest")

    elif args.report:
        report = manager.generate_extension_report(args.report)
        print(report)

    elif args.check_compatibility:
        manifest = manager.load_manifest()
        if args.check_compatibility in manifest.get('extensions', {}):
            ext_data = manifest['extensions'][args.check_compatibility]
            compatibility = manager.check_compatibility(ext_data)

            if compatibility[0]:
                print(f"✅ {args.check_compatibility} is compatible")
            else:
                print(f"❌ {args.check_compatibility} has compatibility issues:")
                for issue in compatibility[1]:
                    print(f"  • {issue}")
        else:
            print(f"❌ Extension '{args.check_compatibility}' not found")

    elif args.security_info:
        security_info = manager.get_extension_security_info(args.security_info)
        print(f"🔒 Security Info for {args.security_info}:")
        for key, value in security_info.items():
            print(f"  {key}: {value}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
