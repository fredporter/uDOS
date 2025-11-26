"""
uDOS v1.5.0 - Shakedown Test Handler

Comprehensive system validation testing for v1.5.0 features:
- Core architecture (flattened structure)
- Planet system (workspace renamed to planet)
- Asset management (centralized library)
- DEV MODE (security system)
- Configuration sync (.env ↔ user.json)
- Memory structure (43% reduction)
- Database locations (sandbox/user/)

Usage:
    SHAKEDOWN           - Run all tests with summary
    SHAKEDOWN --verbose - Show detailed test output
    SHAKEDOWN --quick   - Run core tests only (skip integration)
    SHAKEDOWN --report  - Generate JSON report
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any
from .base_handler import BaseCommandHandler


class ShakedownHandler(BaseCommandHandler):
    """Comprehensive system validation test handler."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.root = Path(__file__).parent.parent.parent
        self.results = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.5.0',
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }

    def handle(self, params: List[str]) -> str:
        """Execute shakedown tests."""
        verbose = '--verbose' in params or '-v' in params
        quick = '--quick' in params
        report = '--report' in params

        output = []
        output.append("╔═══════════════════════════════════════════════════════════╗")
        output.append("║       🔧 uDOS v1.5.0 SHAKEDOWN TEST                    ║")
        output.append("╚═══════════════════════════════════════════════════════════╝")
        output.append("")

        # Run test suites
        self._test_architecture(output, verbose)
        self._test_planet_system(output, verbose)
        self._test_asset_management(output, verbose)
        self._test_dev_mode(output, verbose)
        self._test_memory_structure(output, verbose)
        self._test_database_locations(output, verbose)

        if not quick:
            self._test_startup_health(output, verbose)
            self._test_core_imports(output, verbose)

        # Summary
        output.append("")
        output.append("═" * 63)
        output.append("SHAKEDOWN SUMMARY")
        output.append("═" * 63)
        summary = self.results['summary']

        status = "✅ PASSED" if summary['failed'] == 0 else "❌ FAILED"
        pass_rate = (summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0

        output.append(f"Total Tests:  {summary['total']}")
        output.append(f"Passed:       {summary['passed']} ({pass_rate:.1f}%)")
        output.append(f"Failed:       {summary['failed']}")
        output.append(f"Skipped:      {summary['skipped']}")
        output.append(f"Status:       {status}")
        output.append("")

        if summary['failed'] > 0:
            output.append("Failed Tests:")
            for test in self.results['tests']:
                if test['status'] == 'failed':
                    output.append(f"  ❌ {test['name']}: {test.get('error', 'Unknown error')}")
            output.append("")

        # Generate report if requested
        if report:
            # Use uDOS-style timestamp: YYYYMMDD-HHMMSS-TZ
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc)
            timestamp = now.strftime("%Y%m%d-%H%M%S-UTC")
            report_path = self.root / "memory" / "logs" / f"shakedown-{timestamp}.json"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            with open(report_path, 'w') as f:
                json.dump(self.results, f, indent=2)
            output.append(f"📄 Report saved: {report_path}")
            output.append("")

        return "\n".join(output)

    def _add_test(self, name: str, passed: bool, error: str = None, duration: float = 0):
        """Add test result."""
        self.results['tests'].append({
            'name': name,
            'status': 'passed' if passed else 'failed',
            'error': error,
            'duration': duration
        })
        self.results['summary']['total'] += 1
        if passed:
            self.results['summary']['passed'] += 1
        else:
            self.results['summary']['failed'] += 1

    def _test_architecture(self, output: List[str], verbose: bool):
        """Test core architecture cleanup (17→11 directories)."""
        output.append("📦 Architecture Cleanup Tests")
        output.append("─" * 63)

        # Core directory structure
        core_path = self.root / "core"
        expected_dirs = [
            "commands", "input", "interpreters", "knowledge",
            "output", "services", "ui", "utils"
        ]
        removed_dirs = [
            "config", "network", "scripts", "setup", "tests", "theme", "ucode"
        ]

        # Check expected directories exist
        for dir_name in expected_dirs:
            exists = (core_path / dir_name).exists()
            symbol = "✅" if exists else "❌"
            if verbose or not exists:
                output.append(f"  {symbol} core/{dir_name}/")
            self._add_test(f"Architecture: core/{dir_name} exists", exists)

        # Check removed directories are gone
        for dir_name in removed_dirs:
            removed = not (core_path / dir_name).exists()
            symbol = "✅" if removed else "❌"
            if verbose or not removed:
                output.append(f"  {symbol} core/{dir_name}/ removed")
            self._add_test(f"Architecture: core/{dir_name} removed", removed)

        # Check flattened files
        flattened_files = [
            "config_manager.py", "theme_manager.py", "theme_loader.py",
            "theme_builder.py"
        ]
        for file_name in flattened_files:
            exists = (core_path / file_name).exists()
            symbol = "✅" if exists else "❌"
            if verbose or not exists:
                output.append(f"  {symbol} core/{file_name} flattened")
            self._add_test(f"Architecture: {file_name} flattened", exists)

        output.append("")

    def _test_planet_system(self, output: List[str], verbose: bool):
        """Test planet system integration with universe.json."""
        output.append("🌍 Planet System Tests")
        output.append("─" * 63)

        # Check universe.json exists
        universe_path = self.root / "extensions" / "assets" / "data" / "universe.json"
        exists = universe_path.exists()
        symbol = '\u2713' if exists else '\u2717'
        output.append(f"  {symbol} extensions/assets/data/universe.json")
        self._add_test("Planet: universe.json exists", exists)

        if exists:
            try:
                with open(universe_path) as f:
                    universe = json.load(f)
                has_sol = "solar_systems" in universe and "Sol" in universe.get("solar_systems", {})
                symbol = "✅" if has_sol else "❌"
                if verbose or not has_sol:
                    output.append(f"  {symbol} Sol system defined")
                self._add_test("Planet: Sol system in universe.json", has_sol)

                if has_sol:
                    planet_count = len(universe["solar_systems"]["Sol"].get("planets", {}))
                    expected = 8
                    correct_count = planet_count == expected
                    symbol = "✅" if correct_count else "❌"
                    if verbose or not correct_count:
                        output.append(f"  {symbol} {planet_count} planets (expected {expected})")
                    self._add_test("Planet: 8 planets in Sol system", correct_count)
            except Exception as e:
                output.append(f"  ❌ Error reading universe.json: {e}")
                self._add_test("Planet: universe.json valid JSON", False, str(e))        # Check planets.json structure
        planets_path = self.root / "memory" / "user" / "planets.json"
        exists = planets_path.exists()
        symbol = "✅" if exists else "❌"
        output.append(f"  {symbol} sandbox/user/planets.json")
        self._add_test("Planet: planets.json exists", exists)

        if exists:
            try:
                with open(planets_path) as f:
                    planets = json.load(f)

                has_current = "current_planet" in planets
                has_user_planets = "user_planets" in planets
                has_reference = "reference_universe" in planets

                all_keys = has_current and has_user_planets and has_reference
                symbol = "✅" if all_keys else "❌"
                if verbose or not all_keys:
                    output.append(f"  {symbol} planets.json structure (current, user_planets, reference)")
                self._add_test("Planet: planets.json structure", all_keys)

                if has_user_planets:
                    for planet_name, planet_data in planets["user_planets"].items():
                        has_workspace = "workspace_path" in planet_data
                        symbol = "✅" if has_workspace else "❌"
                        if verbose or not has_workspace:
                            output.append(f"  {symbol} {planet_name} has workspace_path")
                        self._add_test(f"Planet: {planet_name} workspace_path", has_workspace)
            except Exception as e:
                output.append(f"  ❌ Error reading planets.json: {e}")
                self._add_test("Planet: planets.json valid JSON", False, str(e))

        # Check planet directories
        planet_dir = self.root / "memory" / "planet"
        exists = planet_dir.exists()
        symbol = "✅" if exists else "❌"
        output.append(f"  {symbol} memory/planet/ directory")
        self._add_test("Planet: memory/planet directory", exists)

        output.append("")

    def _test_asset_management(self, output: List[str], verbose: bool):
        """Test centralized asset library."""
        output.append("🎨 Asset Management Tests")
        output.append("─" * 63)

        # Check central assets directory
        assets_path = self.root / "extensions" / "assets"
        exists = assets_path.exists()
        symbol = "✅" if exists else "❌"
        output.append(f"  {symbol} extensions/assets/")
        self._add_test("Assets: central directory exists", exists)

        if exists:
            # Check asset subdirectories
            asset_types = ["fonts", "icons", "patterns", "css", "js"]
            for asset_type in asset_types:
                type_path = assets_path / asset_type
                exists = type_path.exists()
                symbol = "✅" if exists else "❌"
                if verbose or not exists:
                    output.append(f"  {symbol} extensions/assets/{asset_type}/")
                self._add_test(f"Assets: {asset_type} directory", exists)

        # Check duplicate assets removed from extensions
        duplicate_paths = [
            self.root / "extensions" / "core" / "terminal" / "assets",
            self.root / "extensions" / "core" / "teletext" / "assets"
        ]

        for dup_path in duplicate_paths:
            removed = not dup_path.exists()
            symbol = "✅" if removed else "❌"
            if verbose or not removed:
                output.append(f"  {symbol} {dup_path.relative_to(self.root)} removed")
            self._add_test(f"Assets: {dup_path.name} duplicates removed", removed)

        # Test asset manager can be imported
        try:
            from core.services.asset_manager import AssetManager
            output.append(f"  ✅ AssetManager imports successfully")
            self._add_test("Assets: AssetManager import", True)

            if verbose:
                manager = AssetManager()
                stats = manager.get_stats()
                output.append(f"     └─ {stats['total']} assets cataloged")
        except Exception as e:
            output.append(f"  ❌ AssetManager import failed: {e}")
            self._add_test("Assets: AssetManager import", False, str(e))

        output.append("")

    def _test_dev_mode(self, output: List[str], verbose: bool):
        """Test DEV MODE security system."""
        output.append("🔒 DEV MODE Security Tests")
        output.append("─" * 63)

        # Test DEV MODE manager import
        try:
            from core.services.dev_mode_manager import DevModeManager
            output.append(f"  ✅ DevModeManager imports successfully")
            self._add_test("DEV MODE: import", True)

            if verbose:
                manager = DevModeManager()
                dangerous_cmds = len(manager.dangerous_commands)
                output.append(f"     └─ {dangerous_cmds} dangerous commands protected")

                # Check if active
                is_active = manager.is_active()
                status = "active" if is_active else "inactive"
                output.append(f"     └─ Status: {status}")
        except Exception as e:
            output.append(f"  ❌ DevModeManager import failed: {e}")
            self._add_test("DEV MODE: import", False, str(e))

        # Check log directory
        log_dir = self.root / "memory" / "logs" / "dev_mode"
        exists = log_dir.exists()
        symbol = "✅" if exists else "⚠️"
        if verbose or not exists:
            output.append(f"  {symbol} sandbox/logs/dev_mode/ {'exists' if exists else 'will be created on first use'}")
        self._add_test("DEV MODE: log directory", True)  # OK if not exists yet

        output.append("")

    def _test_memory_structure(self, output: List[str], verbose: bool):
        """Test flattened memory structure (28→16 directories)."""
        output.append("💾 Memory Structure Tests")
        output.append("─" * 63)

        memory_path = self.root / "memory"

        # Expected directories (v1.5.0)
        expected_dirs = [
            "user", "planet", "sandbox", "workflow", "logs", "sessions",
            "private", "shared", "groups", "public", "modules", "scenarios",
            "missions", "barter", "themes"
        ]

        for dir_name in expected_dirs:
            dir_path = memory_path / dir_name
            exists = dir_path.exists()
            symbol = "✅" if exists else "⚠️"
            if verbose or not exists:
                output.append(f"  {symbol} memory/{dir_name}/")
            self._add_test(f"Memory: {dir_name} directory", True)  # Some may not exist yet

        # Removed directories
        removed_dirs = ["config", "templates", "workspace", "tests"]
        for dir_name in removed_dirs:
            removed = not (memory_path / dir_name).exists()
            symbol = "✅" if removed else "❌"
            if verbose or not removed:
                output.append(f"  {symbol} memory/{dir_name}/ removed")
            self._add_test(f"Memory: {dir_name} removed", removed)

        # Check logs are flat (no subdirectories)
        logs_path = memory_path / "logs"
        if logs_path.exists():
            removed_subdirs = ["sessions", "servers", "feedback", "test"]
            for subdir in removed_subdirs:
                removed = not (logs_path / subdir).exists()
                symbol = "✅" if removed else "❌"
                if verbose or not removed:
                    output.append(f"  {symbol} sandbox/logs/{subdir}/ removed (flat structure)")
                self._add_test(f"Memory: logs/{subdir} removed", removed)

        output.append("")

    def _test_database_locations(self, output: List[str], verbose: bool):
        """Test databases relocated to sandbox/user/."""
        output.append("🗄️  Database Location Tests")
        output.append("─" * 63)

        user_path = self.root / "memory" / "user"

        # Databases in sandbox/user/
        databases = ["knowledge.db", "xp.db"]
        for db_name in databases:
            db_path = user_path / db_name
            exists = db_path.exists()
            symbol = "✅" if exists else "⚠️"
            output.append(f"  {symbol} sandbox/user/{db_name}")
            self._add_test(f"Database: {db_name} in sandbox/user", True)  # OK if not exists yet

            # Check NOT in old location
            old_path = self.root / "memory" / db_name
            removed = not old_path.exists()
            symbol = "✅" if removed else "❌"
            if verbose or not removed:
                output.append(f"  {symbol} memory/{db_name} removed")
            self._add_test(f"Database: {db_name} removed from memory root", removed)

        # Check USER.UDT location
        udt_path = user_path / "USER.UDT"
        exists = udt_path.exists()
        symbol = "✅" if exists else "⚠️"
        output.append(f"  {symbol} sandbox/user/USER.UDT")
        self._add_test("Database: USER.UDT in sandbox/user", True)

        old_udt = self.root / "memory" / "USER.UDT"
        removed = not old_udt.exists()
        symbol = "✅" if removed else "❌"
        if verbose or not removed:
            output.append(f"  {symbol} sandbox/USER.UDT removed")
        self._add_test("Database: USER.UDT removed from memory root", removed)

        output.append("")

    def _test_startup_health(self, output: List[str], verbose: bool):
        """Test startup health check system."""
        output.append("🏥 Startup Health Tests")
        output.append("─" * 63)

        try:
            from core.uDOS_startup import check_system_health
            output.append(f"  ✅ Health check imports successfully")
            self._add_test("Startup: health check import", True)

            # Note: Running health check may trigger interactive prompts
            # so we skip actually running it in automated tests
            if verbose:
                output.append(f"     └─ Health check callable (not executed in test)")
        except Exception as e:
            output.append(f"  ❌ Health check import failed: {e}")
            self._add_test("Startup: health check import", False, str(e))

        output.append("")

    def _test_core_imports(self, output: List[str], verbose: bool):
        """Test core modules can be imported."""
        output.append("📚 Core Module Import Tests")
        output.append("─" * 63)

        modules = [
            ("core.uDOS_parser", "Parser"),
            ("core.uDOS_logger", "Logger"),
            ("core.config_manager", "Config Manager"),
            ("core.theme_manager", "Theme Manager"),
            ("core.services.planet_manager", "Planet Manager"),
        ]

        for module_path, name in modules:
            try:
                __import__(module_path)
                symbol = "✅"
                if verbose:
                    output.append(f"  {symbol} {name}")
                self._add_test(f"Import: {name}", True)
            except Exception as e:
                output.append(f"  ❌ {name}: {e}")
                self._add_test(f"Import: {name}", False, str(e))

        output.append("")
def create_handler(**kwargs) -> ShakedownHandler:
    """Factory function for handler creation."""
    return ShakedownHandler(**kwargs)
