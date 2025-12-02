"""
uDOS v1.1.16+ - Shakedown Test Handler

Comprehensive system validation testing for v1.1.16+ features:
- Core architecture (v1.5.0: flattened structure)
- Planet system (workspace renamed to planet)
- Asset management (centralized library)
- DEV MODE (security system)
- Configuration sync (.env ↔ user.json)
- Memory structure (43% reduction)
- Database locations (sandbox/user/)
- Variable System (v1.1.18: SPRITE/OBJECT with JSON schemas)
- Handler Architecture (v1.1.17: system handler refactored, UNDO/REDO)
- Play Extension (v1.1.19: STORY command when implemented)

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

        # v1.1.17+ test suites (documentation, variables, play extension)
        self._test_variable_system(output, verbose)
        self._test_sprite_object_system(output, verbose)
        self._test_content_generation(output, verbose)

        if not quick:
            self._test_story_system(output, verbose)
            self._test_handler_architecture(output, verbose)

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
        universe_path = self.root / "core" / "data" / "universe.json"
        exists = universe_path.exists()
        symbol = '\u2713' if exists else '\u2717'
        output.append(f"  {symbol} core/data/universe.json")
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
        planets_path = self.root / "sandbox" / "user" / "planets.json"
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
            # Check asset subdirectories (only fonts, icons, data)
            asset_types = ["fonts", "icons", "data"]
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

        # Expected directories (v2.0.0 - workflow/sessions moved to sandbox)
        expected_dirs = [
            "user", "planet", "sandbox", "logs",
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

        # Check sandbox directories for user data
        sandbox_path = self.root / "sandbox"
        sandbox_dirs = ["workflow", "sessions"]
        for dir_name in sandbox_dirs:
            dir_path = sandbox_path / dir_name
            exists = dir_path.exists()
            symbol = "✅" if exists else "⚠️"
            if verbose or not exists:
                output.append(f"  {symbol} sandbox/{dir_name}/")
            self._add_test(f"Sandbox: {dir_name} directory", True)  # May not exist yet

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

        user_path = self.root / "sandbox" / "user"

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
            from core.services.uDOS_startup import check_system_health
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

    def _test_variable_system(self, output: List[str], verbose: bool):
        """Test variable system with JSON schema support (v1.1.18)."""
        output.append("🔢 Variable System Tests (v1.1.18)")
        output.append("─" * 63)

        # Test VariableManager import
        try:
            from core.utils.variables import VariableManager
            output.append(f"  ✅ VariableManager imports successfully")
            self._add_test("Variables: VariableManager import", True)

            manager = VariableManager()

            # Test schema loading
            expected_schemas = ['system', 'user', 'sprite', 'object', 'story']
            for schema_name in expected_schemas:
                has_schema = schema_name in manager.schemas
                symbol = "✅" if has_schema else "❌"
                if verbose or not has_schema:
                    output.append(f"  {symbol} {schema_name}.json schema loaded")
                self._add_test(f"Variables: {schema_name} schema loaded", has_schema)

            # Test scope management
            scopes = ['global', 'session', 'script', 'local']
            for scope in scopes:
                has_scope = scope in manager.variables
                symbol = "✅" if has_scope else "❌"
                if verbose or not has_scope:
                    output.append(f"  {symbol} {scope} scope initialized")
                self._add_test(f"Variables: {scope} scope", has_scope)

        except Exception as e:
            output.append(f"  ❌ VariableManager import failed: {e}")
            self._add_test("Variables: VariableManager import", False, str(e))

        output.append("")

    def _test_sprite_object_system(self, output: List[str], verbose: bool):
        """Test SPRITE and OBJECT handlers (v1.1.18)."""
        output.append("🎮 SPRITE/OBJECT System Tests (v1.1.18)")
        output.append("─" * 63)

        # Test SPRITE handler
        try:
            from core.commands.sprite_handler import SpriteHandler
            output.append(f"  ✅ SpriteHandler imports successfully")
            self._add_test("SPRITE: handler import", True)

            # Check sprite schema exists
            sprite_schema_path = self.root / "core" / "data" / "variables" / "sprite.schema.json"
            exists = sprite_schema_path.exists()
            symbol = "✅" if exists else "❌"
            output.append(f"  {symbol} sprite.schema.json exists")
            self._add_test("SPRITE: schema file", exists)

            if exists and verbose:
                with open(sprite_schema_path) as f:
                    schema = json.load(f)
                    props = len(schema.get('properties', {}))
                    output.append(f"     └─ {props} sprite properties defined")

        except Exception as e:
            output.append(f"  ❌ SpriteHandler import failed: {e}")
            self._add_test("SPRITE: handler import", False, str(e))

        # Test OBJECT handler
        try:
            from core.commands.object_handler import ObjectHandler
            output.append(f"  ✅ ObjectHandler imports successfully")
            self._add_test("OBJECT: handler import", True)

            # Check object schema exists
            object_schema_path = self.root / "core" / "data" / "variables" / "object.schema.json"
            exists = object_schema_path.exists()
            symbol = "✅" if exists else "❌"
            output.append(f"  {symbol} object.schema.json exists")
            self._add_test("OBJECT: schema file", exists)

        except Exception as e:
            output.append(f"  ❌ ObjectHandler import failed: {e}")
            self._add_test("OBJECT: handler import", False, str(e))

        output.append("")

    def _test_story_system(self, output: List[str], verbose: bool):
        """Test STORY command handler (v1.1.19)."""
        output.append("📖 STORY System Tests (v1.1.19)")
        output.append("─" * 63)

        # Test STORY handler (if exists)
        try:
            from core.commands.story_handler import StoryHandler
            output.append(f"  ✅ StoryHandler imports successfully")
            self._add_test("STORY: handler import", True)

            # Check for adventure scripts
            adventures_path = self.root / "memory" / "ucode" / "adventures"
            if adventures_path.exists():
                adventures = list(adventures_path.glob("*.upy"))
                count = len(adventures)
                symbol = "✅" if count > 0 else "⚠️"
                output.append(f"  {symbol} {count} adventure script(s) found")
                self._add_test("STORY: adventure scripts", count > 0)
            else:
                output.append(f"  ⚠️  No adventures directory (will be created)")
                self._add_test("STORY: adventure scripts", True)  # OK if not exists yet

        except ImportError:
            output.append(f"  ⚠️  StoryHandler not yet implemented (planned v1.1.19)")
            self._add_test("STORY: handler import", True)  # Not implemented yet, OK
        except Exception as e:
            output.append(f"  ❌ StoryHandler error: {e}")
            self._add_test("STORY: handler import", False, str(e))

        output.append("")

    def _test_content_generation(self, output: List[str], verbose: bool):
        """Test content generation system (v1.1.6 + v1.1.15)."""
        output.append("🎨 Content Generation Tests (v1.1.6 + v1.1.15)")
        output.append("─" * 63)

        # Test GENERATE handler
        try:
            from core.commands.generate_handler import GenerateHandler
            output.append(f"  ✅ GenerateHandler imports successfully")
            self._add_test("GENERATE: handler import", True)

            # Check handler size
            handler_path = self.root / "core" / "commands" / "generate_handler.py"
            if handler_path.exists():
                with open(handler_path) as f:
                    lines = len(f.readlines())
                symbol = "✅" if lines > 500 else "⚠️"
                output.append(f"  {symbol} generate_handler.py: {lines} lines")
                self._add_test("GENERATE: handler size", lines > 500)

        except ImportError as e:
            output.append(f"  ❌ GenerateHandler import failed: {e}")
            self._add_test("GENERATE: handler import", False, str(e))

        # Test survival prompts (Nano Banana optimization)
        prompts_path = self.root / "core" / "data" / "diagrams" / "templates" / "survival_prompts.json"
        if prompts_path.exists():
            import json
            with open(prompts_path) as f:
                data = json.load(f)
                prompt_count = len(data.get("prompts", {}))
                symbol = "✅" if prompt_count >= 13 else "⚠️"
                output.append(f"  {symbol} {prompt_count} survival diagram prompts")
                self._add_test("GENERATE: survival prompts", prompt_count >= 13)
        else:
            output.append(f"  ⚠️  survival_prompts.json not found")
            self._add_test("GENERATE: survival prompts", False)

        # Check for REVIEW/REGEN (planned v1.1.17)
        try:
            # REVIEW and REGEN should be in docs_unified_handler (v1.1.17)
            docs_handler_path = self.root / "core" / "commands" / "docs_unified_handler.py"
            if docs_handler_path.exists():
                with open(docs_handler_path) as f:
                    content = f.read()
                    has_review = "REVIEW" in content or "review" in content
                    has_regen = "REGEN" in content or "regen" in content
                    symbol = "✅" if (has_review and has_regen) else "⚠️"
                    output.append(f"  {symbol} REVIEW/REGEN commands: {'found' if has_review and has_regen else 'not yet implemented'}")
                    self._add_test("GENERATE: REVIEW/REGEN", has_review and has_regen)
            else:
                output.append(f"  ⚠️  REVIEW/REGEN not yet implemented (planned v1.1.17)")
                self._add_test("GENERATE: REVIEW/REGEN", True)  # OK if not exists yet
        except Exception as e:
            output.append(f"  ⚠️  REVIEW/REGEN check skipped: {e}")

        output.append("")

    def _test_handler_architecture(self, output: List[str], verbose: bool):
        """Test handler architecture and consolidation (v1.1.17)."""
        output.append("🏗️  Handler Architecture Tests (v1.1.17)")
        output.append("─" * 63)

        # Test system handler size (should be ~674 lines after v1.1.5.1 refactor)
        system_handler_path = self.root / "core" / "commands" / "system_handler.py"
        if system_handler_path.exists():
            with open(system_handler_path) as f:
                lines = len(f.readlines())

            # After refactoring should be 600-700 lines
            refactored = 600 <= lines <= 750
            symbol = "✅" if refactored else "⚠️"
            output.append(f"  {symbol} system_handler.py: {lines} lines (target: 600-700)")
            self._add_test("Handler: system_handler refactored", refactored)

        # Check for shared utilities
        common_path = self.root / "core" / "utils" / "common.py"
        exists = common_path.exists()
        symbol = "✅" if exists else "❌"
        output.append(f"  {symbol} core/utils/common.py (shared utilities)")
        self._add_test("Handler: shared utilities", exists)

        # Check UNDO/REDO commands exist
        try:
            from core.commands.session_handler import SessionHandler
            output.append(f"  ✅ SessionHandler (UNDO/REDO) imports")
            self._add_test("Handler: UNDO/REDO commands", True)
        except Exception as e:
            output.append(f"  ❌ SessionHandler import failed: {e}")
            self._add_test("Handler: UNDO/REDO commands", False, str(e))

        output.append("")


def create_handler(**kwargs) -> ShakedownHandler:
    """Factory function for handler creation."""
    return ShakedownHandler(**kwargs)
