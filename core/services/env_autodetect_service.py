"""
Environment Auto-Detection Service

Auto-detects and writes system information to .env on startup:
- OS_TYPE (mac/alpine/ubuntu/windows)
- UDOS_TIMEZONE (from system)
- UDOS_VIEWPORT_* (terminal dimensions)
- UDOS_ROOT (repository root)

Author: uDOS Engineering
Version: v1.0.0
Date: 2026-02-09
"""

import os
import platform
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timezone

from core.services.logging_api import get_logger, get_repo_root
from core.services.config_sync_service import ConfigSyncManager
from core.services.os_detector import get_os_detector
from core.services.viewport_service import ViewportService


logger = get_logger("core", category="env-autodetect")


class EnvAutoDetectService:
    """Auto-detect system info and persist to .env."""

    def __init__(self):
        """Initialize service."""
        self.repo_root = get_repo_root()
        self.env_file = self.repo_root / ".env"
        self.sync = ConfigSyncManager()

    def detect_all(self, force: bool = False) -> Dict[str, any]:
        """
        Detect all system information and update .env.

        Args:
            force: If True, always update. If False, only update missing values.

        Returns:
            Dict with detected values and status
        """
        updates = {}
        results = {
            "os_type": None,
            "timezone": None,
            "location": None,
            "grid_id": None,
            "current_date": None,
            "current_time": None,
            "viewport_cols": None,
            "viewport_rows": None,
            "udos_root": None,
            "updated": [],
            "skipped": [],
            "errors": [],
        }

        # Detect OS Type
        try:
            os_type = self._detect_os_type()
            current_os = os.getenv("OS_TYPE")

            if force or not current_os:
                updates["OS_TYPE"] = os_type
                results["updated"].append(f"OS_TYPE={os_type}")
            else:
                results["skipped"].append(f"OS_TYPE={current_os} (already set)")

            results["os_type"] = os_type
        except Exception as e:
            results["errors"].append(f"OS detection failed: {e}")
            logger.warning(f"[AUTO-DETECT] OS detection failed: {e}")

        # Detect Timezone
        try:
            tz = self._detect_timezone()
            current_tz = os.getenv("UDOS_TIMEZONE")

            if force or not current_tz:
                updates["UDOS_TIMEZONE"] = tz
                results["updated"].append(f"UDOS_TIMEZONE={tz}")
            else:
                results["skipped"].append(f"UDOS_TIMEZONE={current_tz} (already set)")

            results["timezone"] = tz
        except Exception as e:
            results["errors"].append(f"Timezone detection failed: {e}")
            logger.warning(f"[AUTO-DETECT] Timezone detection failed: {e}")

# Extract location (city) from timezone
        try:
            if results.get("timezone"):
                city_name = self.parse_city_from_timezone(results["timezone"])
                if city_name:
                    results["location"] = city_name
                    logger.debug(f"[AUTO-DETECT] Parsed location '{city_name}' from timezone")

                    # Try to find matching location in database
                    try:
                        from core.locations.service import LocationService
                        loc_service = LocationService()

                        # Search for the city in locations
                        matches = loc_service.search(city_name, limit=1)
                        if matches:
                            location = matches[0]
                            grid_id = location.get("id")
                            results["grid_id"] = grid_id
                            logger.info(f"[AUTO-DETECT] Matched location: {city_name} → {grid_id}")

                            # Store in .env
                            current_location = os.getenv("UDOS_LOCATION")
                            current_grid = os.getenv("UDOS_GRID_ID")

                            if force or not current_location:
                                updates["UDOS_LOCATION"] = city_name
                                results["updated"].append(f"UDOS_LOCATION={city_name}")
                            else:
                                results["skipped"].append(f"UDOS_LOCATION={current_location} (already set)")

                            if force or not current_grid:
                                updates["UDOS_GRID_ID"] = grid_id
                                results["updated"].append(f"UDOS_GRID_ID={grid_id}")
                            else:
                                results["skipped"].append(f"UDOS_GRID_ID={current_grid} (already set)")
                    except Exception as loc_err:
                        logger.debug(f"[AUTO-DETECT] Could not find location for {city_name}: {loc_err}")
        except Exception as e:
            results["errors"].append(f"Location parsing failed: {e}")
            logger.warning(f"[AUTO-DETECT] Location parsing failed: {e}")

        # Detect Current Date/Time (for drift detection, not persisted to .env)
        try:
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")

            results["current_date"] = current_date
            results["current_time"] = current_time

            # Log for awareness but don't update .env (datetime changes constantly)
            logger.debug(f"[AUTO-DETECT] System time: {current_date} {current_time}")
        except Exception as e:
            results["errors"].append(f"DateTime detection failed: {e}")
            logger.warning(f"[AUTO-DETECT] DateTime detection failed: {e}")

        # Detect UDOS_ROOT
        try:
            root = str(self.repo_root)
            current_root = os.getenv("UDOS_ROOT")

            if force or not current_root:
                updates["UDOS_ROOT"] = root
                results["updated"].append(f"UDOS_ROOT={root}")
            else:
                results["skipped"].append(f"UDOS_ROOT={current_root} (already set)")

            results["udos_root"] = root
        except Exception as e:
            results["errors"].append(f"UDOS_ROOT detection failed: {e}")
            logger.warning(f"[AUTO-DETECT] UDOS_ROOT detection failed: {e}")

        # Viewport is handled separately by ViewportService (always updates)
        try:
            viewport_service = ViewportService()
            viewport_result = viewport_service.refresh(source="autodetect")

            results["viewport_cols"] = viewport_result.get("cols")
            results["viewport_rows"] = viewport_result.get("rows")
            results["updated"].append(
                f"UDOS_VIEWPORT_COLS={viewport_result.get('cols')}, "
                f"UDOS_VIEWPORT_ROWS={viewport_result.get('rows')}"
            )
        except Exception as e:
            results["errors"].append(f"Viewport detection failed: {e}")
            logger.warning(f"[AUTO-DETECT] Viewport detection failed: {e}")

        # Write updates to .env
        if updates:
            ok, message = self.sync.update_env_vars(updates)
            if not ok:
                results["errors"].append(f"Failed to write .env: {message}")
                logger.error(f"[AUTO-DETECT] .env update failed: {message}")
            else:
                logger.info(f"[AUTO-DETECT] Updated .env: {', '.join(updates.keys())}")

        return results

    def _detect_os_type(self) -> str:
        """
        Detect OS type using OSDetector.

        Returns:
            "mac", "alpine", "ubuntu", "windows", or "linux"
        """
        detector = get_os_detector()
        platform_name = detector.get_platform()

        # Map to .env OS_TYPE values
        os_map = {
            "macos": "mac",
            "alpine": "alpine",
            "ubuntu": "ubuntu",
            "windows": "windows",
            "linux": "ubuntu",  # Default Linux to ubuntu
        }

        return os_map.get(platform_name, "linux")

    def _detect_timezone(self) -> str:
        """
        Detect system timezone.

        Returns:
            IANA timezone string (e.g., "America/New_York")
        """
        # Method 1: Try timedatectl (Linux systemd)
        try:
            import subprocess
            result = subprocess.run(
                ['timedatectl', 'show', '--property=Timezone', '--value'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                tz = result.stdout.strip()
                if '/' in tz or tz == 'UTC':  # Validate IANA format
                    return tz
        except Exception:
            pass

        # Method 2: Read /etc/timezone (Debian/Ubuntu)
        try:
            tz_file = Path("/etc/timezone")
            if tz_file.exists():
                tz = tz_file.read_text().strip()
                if tz and ('/' in tz or tz == 'UTC'):
                    return tz
        except Exception:
            pass

        # Method 3: Check TZ environment variable
        tz_env = os.getenv("TZ", "").strip()
        if tz_env and ('/' in tz_env or tz_env == 'UTC'):
            return tz_env

        # Method 4: Try datetime with zone attribute (pytz-aware datetimes)
        try:
            now = datetime.now().astimezone()
            tzinfo = now.tzinfo
            if tzinfo:
                # Check for zone attribute (pytz)
                tz_name = getattr(tzinfo, "zone", None) or getattr(tzinfo, "key", None)
                if tz_name and ('/' in tz_name or tz_name == 'UTC'):
                    return tz_name
        except Exception:
            pass

        # Final fallback
        logger.warning("[AUTO-DETECT] Could not detect timezone, defaulting to UTC")
        return "UTC"

    def parse_city_from_timezone(self, timezone_str: str) -> Optional[str]:
        """
        Extract city name from IANA timezone string.

        Args:
            timezone_str: IANA timezone (e.g., "Australia/Brisbane", "America/New_York")

        Returns:
            City name or None
        """
        if not timezone_str or '/' not in timezone_str:
            return None

        # Extract the part after the last slash
        # e.g., "Australia/Brisbane" → "Brisbane"
        # e.g., "America/Argentina/Buenos_Aires" → "Buenos_Aires"
        city_part = timezone_str.split('/')[-1]

        # Replace underscores with spaces
        # e.g., "New_York" → "New York"
        # e.g., "Buenos_Aires" → "Buenos Aires"
        city_name = city_part.replace('_', ' ')

        return city_name


def get_autodetect_service() -> EnvAutoDetectService:
    """Get singleton instance of EnvAutoDetectService."""
    if not hasattr(get_autodetect_service, "_instance"):
        get_autodetect_service._instance = EnvAutoDetectService()
    return get_autodetect_service._instance


# CLI entry point for testing
if __name__ == "__main__":
    service = get_autodetect_service()
    results = service.detect_all(force=False)

    print("\n🔍 Environment Auto-Detection Results:\n")

    if results["updated"]:
        print("✅ Updated:")
        for item in results["updated"]:
            print(f"   {item}")

    if results["skipped"]:
        print("\n⏭️  Skipped:")
        for item in results["skipped"]:
            print(f"   {item}")

    if results["errors"]:
        print("\n❌ Errors:")
        for item in results["errors"]:
            print(f"   {item}")

    print()
