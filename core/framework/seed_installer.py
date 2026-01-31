"""
Seed Installer - Bootstrap initial data into memory/bank/

Handles copying framework seed data to user memory directory on first run
or via REPAIR --seed command.

Ensures /memory/bank/locations/, /memory/bank/help/, and other required
directories exist with initial data.
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
        self.bank_dir = self.memory_dir / "bank"

    def ensure_directories(self) -> bool:
        """
        Create required memory/bank/ directory structure.

        Returns:
            True if successful
        """
        try:
            # Core directories
            (self.bank_dir / "locations").mkdir(parents=True, exist_ok=True)
            (self.bank_dir / "help").mkdir(parents=True, exist_ok=True)
            (self.bank_dir / "templates").mkdir(parents=True, exist_ok=True)
            (self.bank_dir / "system").mkdir(parents=True, exist_ok=True)
            (self.bank_dir / "graphics" / "diagrams" / "templates").mkdir(
                parents=True, exist_ok=True
            )
            (self.bank_dir / "workflows").mkdir(parents=True, exist_ok=True)
            (self.memory_dir / "logs").mkdir(parents=True, exist_ok=True)

            logger.info("[LOCAL] Directory structure created in memory/bank/")
            return True
        except Exception as e:
            logger.error(f"[LOCAL] Failed to create directories: {e}")
            return False

    def install_locations_seed(self, force: bool = False) -> bool:
        """
        Install locations-seed.json to memory/bank/locations/locations.json

        Args:
            force: Overwrite if exists

        Returns:
            True if successful
        """
        seed_file = self.seed_dir / "locations-seed.json"
        target_file = self.bank_dir / "locations" / "locations.json"

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
        Install timezones-seed.json to memory/bank/timezones.json

        Args:
            force: Overwrite if exists

        Returns:
            True if successful
        """
        seed_file = self.seed_dir / "timezones-seed.json"
        target_file = self.bank_dir / "timezones.json"

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

    def install_bank_seeds(self, force: bool = False) -> Dict[str, bool]:
        """
        Install all bank seeds (help, templates, graphics).

        Args:
            force: Overwrite if exists

        Returns:
            Dict with status of each seed type
        """
        results = {}
        bank_seed_dir = self.seed_dir / "bank"

        if not bank_seed_dir.exists():
            logger.warning(f"[LOCAL] Bank seed directory not found: {bank_seed_dir}")
            return results

        try:
            # Recursively copy seed structure
            for seed_subdir in bank_seed_dir.iterdir():
                if seed_subdir.is_dir():
                    target_subdir = self.bank_dir / seed_subdir.name
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

            logger.info(f"[LOCAL] Installed bank seeds ({len(results)} files)")
            return results
        except Exception as e:
            logger.error(f"[LOCAL] Failed to install bank seeds: {e}")
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

        # 4. Install bank seeds
        bank_results = self.install_bank_seeds(force)
        messages.append(f"✅ Bank seeds installed ({len(bank_results)} files)")

        return True, messages

    def status(self) -> Dict[str, bool]:
        """
        Check status of seed installation.

        Returns:
            Dict with status of each seed component
        """
        return {
            "directories_exist": (self.bank_dir / "locations").exists(),
            "locations_seeded": (self.bank_dir / "locations" / "locations.json").exists(),
            "timezones_seeded": (self.bank_dir / "timezones.json").exists(),
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
