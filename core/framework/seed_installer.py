"""
Seed Installer - Bootstrap initial data into memory/system/

Handles copying framework seed data to user memory directory on first run
or via REPAIR --seed command.

Ensures /memory/system/locations/ and other seed templates exist.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from core.services.logging_service import get_logger

logger = get_logger("seed_installer")


class SeedInstaller:
    """Install framework seed data into memory directory."""

    def __init__(self, framework_dir: Path = None, memory_dir: Path = None):
        """
        Initialize seed installer.

        Args:
            framework_dir: Path to core/framework/ (defaults to auto-detect)
            memory_dir: Path to memory/ (defaults to auto-detect)
        """
        if framework_dir is None:
            framework_dir = Path(__file__).parent
        if memory_dir is None:
            memory_dir = Path.cwd() / "memory"

        self.framework_dir = Path(framework_dir)
        self.memory_dir = Path(memory_dir)
        self.seed_dir = self.framework_dir / "seed"
        self.system_dir = self.memory_dir / "system"

    def ensure_directories(self) -> bool:
        """
        Create required memory/system/ directory structure.

        Returns:
            True if successful
        """
        try:
            # Core directories
            (self.system_dir / "locations").mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "logs").mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "logs" / "monitoring").mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "logs" / "quotas").mkdir(parents=True, exist_ok=True)

            logger.info("[LOCAL] Directory structure created in memory/system/")
            return True
        except Exception as e:
            logger.error(f"[LOCAL] Failed to create directories: {e}")
            return False

    def install_locations_seed(self, force: bool = False) -> bool:
        """
        Install locations-seed.json to memory/system/locations/locations.json

        Args:
            force: Overwrite if exists

        Returns:
            True if successful
        """
        seed_file = self.seed_dir / "locations-seed.json"
        target_file = self.system_dir / "locations" / "locations.json"

        if not seed_file.exists():
            logger.error(f"[LOCAL] Seed file not found: {seed_file}")
            return False

        if target_file.exists() and not force:
            logger.info(f"[LOCAL] Locations already seeded: {target_file}")
            return True

        try:
            # Load, validate, and copy
            with open(seed_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"[LOCAL] Installed locations seed ({len(data.get('locations', []))} locations)"
            )
            return True
        except Exception as e:
            logger.error(f"[LOCAL] Failed to install locations seed: {e}")
            return False

    def install_timezones_seed(self, force: bool = False) -> bool:
        """
        Install timezones-seed.json to memory/system/timezones.json

        Args:
            force: Overwrite if exists

        Returns:
            True if successful
        """
        seed_file = self.seed_dir / "timezones-seed.json"
        target_file = self.system_dir / "timezones.json"

        if not seed_file.exists():
            logger.error(f"[LOCAL] Seed file not found: {seed_file}")
            return False

        if target_file.exists() and not force:
            logger.info(f"[LOCAL] Timezones already seeded: {target_file}")
            return True

        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            with open(target_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"[LOCAL] Installed timezones seed")
            return True
        except Exception as e:
            logger.error(f"[LOCAL] Failed to install timezones seed: {e}")
            return False

    def install_system_seeds(self, force: bool = False) -> Dict[str, bool]:
        """
        Install all system seeds (help, templates, graphics, workflows).

        Args:
            force: Overwrite if exists

        Returns:
            Dict with status of each seed type
        """
        results = {}
        seed_root = self.seed_dir / "bank"

        if not seed_root.exists():
            logger.warning(f"[LOCAL] Seed directory not found: {seed_root}")
            return results

        try:
            # Recursively copy seed structure
            for seed_subdir in seed_root.iterdir():
                if seed_subdir.is_dir():
                    target_subdir = self.system_dir / seed_subdir.name
                    target_subdir.mkdir(parents=True, exist_ok=True)

                    # Copy files from seed
                    for item in seed_subdir.rglob("*"):
                        if item.is_file():
                            rel_path = item.relative_to(seed_subdir)
                            target_file = target_subdir / rel_path
                            target_file.parent.mkdir(parents=True, exist_ok=True)

                            if not target_file.exists() or force:
                                shutil.copy2(item, target_file)
                                results[f"{seed_subdir.name}/{rel_path}"] = True

            logger.info(f"[LOCAL] Installed system seeds ({len(results)} files)")
            return results
        except Exception as e:
            logger.error(f"[LOCAL] Failed to install system seeds: {e}")
            return results

    def install_all(self, force: bool = False) -> Tuple[bool, List[str]]:
        """
        Install all seeds (directories, locations, timezones, bank).

        Args:
            force: Overwrite existing files

        Returns:
            Tuple[success, List[messages]]
        """
        messages = []

        # 1. Ensure directories exist
        if not self.ensure_directories():
            messages.append("❌ Failed to create directory structure")
            return False, messages
        messages.append("✅ Directory structure created")

        # 2. Install locations seed
        if self.install_locations_seed(force):
            messages.append("✅ Locations seed installed")
        else:
            messages.append("⚠️  Locations seed installation failed")

        # 3. Install timezones seed
        if self.install_timezones_seed(force):
            messages.append("✅ Timezones seed installed")
        else:
            messages.append("⚠️  Timezones seed installation failed")

        # 4. Install system seeds
        system_results = self.install_system_seeds(force)
        messages.append(f"✅ System seeds installed ({len(system_results)} files)")

        return True, messages

    def status(self) -> Dict[str, bool]:
        """
        Check status of seed installation.

        Returns:
            Dict with status of each seed component
        """
        system_required = [
            self.system_dir / "startup-script.md",
            self.system_dir / "reboot-script.md",
            self.system_dir / "tui-setup-story.md",
            self.system_dir / "wizard-setup-story.md",
        ]
        return {
            "directories_exist": (self.system_dir / "locations").exists(),
            "locations_seeded": (self.system_dir / "locations" / "locations.json").exists(),
            "timezones_seeded": (self.system_dir / "timezones.json").exists(),
            "system_seeds": all(path.exists() for path in system_required),
            "framework_seed_dir_exists": self.seed_dir.exists(),
        }


def bootstrap_seed(force: bool = False) -> Tuple[bool, List[str]]:
    """
    Convenience function to bootstrap seed data.

    Args:
        force: Overwrite existing files

    Returns:
        Tuple[success, List[messages]]
    """
    installer = SeedInstaller()
    return installer.install_all(force)
