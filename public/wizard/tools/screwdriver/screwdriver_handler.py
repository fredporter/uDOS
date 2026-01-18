#!/usr/bin/env python3
"""
SCREWDRIVER Command Handler - Sonic Screwdriver firmware management

Command interface for Layer 650 firmware provisioning, OTA updates,
flash pack management, and device health monitoring.

Commands:
- SCREWDRIVER PACKS [--list|--create|--validate]
- SCREWDRIVER FLASH <device_id> <version> [--force]
- SCREWDRIVER HEALTH <device_id|tile>
- SCREWDRIVER PROVISION <devices> <version> [--strategy=<strategy>]
- SCREWDRIVER STATUS [device_id]
- SCREWDRIVER JOBS [--list|--status=<job_id>]
- SCREWDRIVER ROLLBACK <device_id>
- SCREWDRIVER BANKS <device_id>

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import time
from typing import List, Optional, Dict
from pathlib import Path

from .screwdriver_flash_packs import FlashPackManager, FlashPackStatus, FlashStage
from .screwdriver_provisioner import (
    ScrewdriverProvisioner,
    ProvisionStrategy,
    HealthCheckResult,
)
from .meshcore_device_manager import (
    MeshCoreDeviceManager,
    DeviceType,
    DeviceStatus,
    FirmwareStatus,
)


class ScrewdriverCommandHandler:
    """
    Handle SCREWDRIVER commands for firmware management.

    Integrates flash pack management, device provisioning, and
    health monitoring for Layer 650 operations.
    """

    def __init__(self):
        """Initialize SCREWDRIVER command handler."""
        self.flash_manager = FlashPackManager()
        self.device_manager = MeshCoreDeviceManager()
        self.provisioner = ScrewdriverProvisioner(
            self.flash_manager, self.device_manager
        )

    def handle_command(self, args: List[str]) -> str:
        """
        Route SCREWDRIVER commands.

        Args:
            args: Command arguments

        Returns:
            Command output
        """
        if not args:
            return self._show_help()

        subcommand = args[0].upper()

        if subcommand == "PACKS":
            return self._handle_packs(args[1:])
        elif subcommand == "FLASH":
            return self._handle_flash(args[1:])
        elif subcommand == "HEALTH":
            return self._handle_health(args[1:])
        elif subcommand == "PROVISION":
            return self._handle_provision(args[1:])
        elif subcommand == "STATUS":
            return self._handle_status(args[1:])
        elif subcommand == "JOBS":
            return self._handle_jobs(args[1:])
        elif subcommand == "ROLLBACK":
            return self._handle_rollback(args[1:])
        elif subcommand == "BANKS":
            return self._handle_banks(args[1:])
        else:
            return f"Unknown SCREWDRIVER command: {subcommand}\n\n{self._show_help()}"

    def _handle_packs(self, args: List[str]) -> str:
        """Handle SCREWDRIVER PACKS command."""
        if not args or args[0] == "--list":
            return self._list_packs()
        elif args[0] == "--validate":
            if len(args) < 2:
                return "Usage: SCREWDRIVER PACKS --validate <version>"
            return self._validate_pack(args[1])
        else:
            return "Usage: SCREWDRIVER PACKS [--list|--validate <version>]"

    def _list_packs(self) -> str:
        """List available flash packs."""
        packs = self.flash_manager.list_flash_packs()

        if not packs:
            return "No flash packs available."

        lines = ["Flash Packs Available:", ""]

        # Sort by version
        packs.sort(key=lambda p: p.version, reverse=True)

        for pack in packs:
            status = self.flash_manager.validate_flash_pack(pack.version)

            lines.append(f"📦 v{pack.version} {status.value}")
            lines.append(f"   Built: {pack.build_date}")
            lines.append(f"   Size: {pack.binary_size:,} bytes")
            lines.append(f"   Targets: {', '.join(pack.target_devices)}")

            if pack.features:
                lines.append(f"   Features: {len(pack.features)} new")
            if pack.bugfixes:
                lines.append(f"   Fixes: {len(pack.bugfixes)} bugs")

            lines.append("")

        return "\n".join(lines)

    def _validate_pack(self, version: str) -> str:
        """Validate flash pack integrity."""
        status = self.flash_manager.validate_flash_pack(version)
        pack = self.flash_manager.get_flash_pack(version)

        if not pack:
            return f"Flash pack v{version} not found."

        lines = [f"Validating Flash Pack v{version}", ""]
        lines.append(f"Status: {status.value}")
        lines.append(f"Checksum: {pack.checksum_sha256[:16]}...")
        lines.append(f"Signature: {pack.signature[:16]}...")
        lines.append(f"Binary Size: {pack.binary_size:,} bytes")
        lines.append("")

        if status == FlashPackStatus.VALID:
            lines.append("✓ Flash pack is valid and ready to deploy")
        else:
            lines.append("✗ Flash pack validation failed")

        return "\n".join(lines)

    def _handle_flash(self, args: List[str]) -> str:
        """Handle SCREWDRIVER FLASH command."""
        if len(args) < 2:
            return "Usage: SCREWDRIVER FLASH <device_id> <version> [--force]"

        device_id = args[0]
        version = args[1]
        force = "--force" in args

        # Check if device exists
        device = self.device_manager.get_device(device_id)
        if not device:
            return f"Device {device_id} not found."

        # Check if flash pack exists
        pack = self.flash_manager.get_flash_pack(version)
        if not pack:
            return f"Flash pack v{version} not found."

        lines = [f"Flashing {device_id} to v{version}", ""]

        # Show current state
        lines.append(
            f"Current: v{device.firmware_version} {device.firmware_status.value}"
        )
        lines.append(f"Target:  v{version}")
        lines.append(f"Device:  {device.type.value} @ {device.tile}-{device.layer}")
        lines.append("")

        # Provision device
        success = self.provisioner.provision_device(device_id, version, force=force)

        if success:
            lines.append("✓ Flash complete!")
            lines.append(f"  Device {device_id} now running v{version}")
        else:
            lines.append("✗ Flash failed")
            lines.append("  Check device health and try again")

        return "\n".join(lines)

    def _handle_health(self, args: List[str]) -> str:
        """Handle SCREWDRIVER HEALTH command."""
        if not args:
            return "Usage: SCREWDRIVER HEALTH <device_id|tile>"

        target = args[0]

        # Check if target is a device ID or tile code
        if target in self.device_manager.devices:
            return self._show_device_health(target)
        else:
            # Assume it's a tile code
            return self._show_tile_health(target)

    def _show_device_health(self, device_id: str) -> str:
        """Show health check for single device."""
        health = self.provisioner.health_check(device_id)
        device = self.device_manager.get_device(device_id)

        lines = [f"Device Health Check: {device_id}", ""]

        lines.append(f"Result: {health.result.value} {health.result.name}")
        lines.append(f"Timestamp: {health.timestamp}")
        lines.append("")

        lines.append("Metrics:")
        lines.append(f"  Signal Strength: {health.signal_strength}%")
        lines.append(f"  Uptime: {health.uptime_hours:.1f}h")
        lines.append(f"  Message Rate: {health.message_rate} msgs/sec")
        lines.append(f"  Connections: {health.connection_count}")
        lines.append(f"  Memory Usage: {health.memory_usage}%")
        lines.append(f"  CPU Usage: {health.cpu_usage}%")
        lines.append("")

        if health.errors:
            lines.append("Errors:")
            for error in health.errors:
                lines.append(f"  ✗ {error}")
            lines.append("")

        if health.warnings:
            lines.append("Warnings:")
            for warning in health.warnings:
                lines.append(f"  ⚠ {warning}")
            lines.append("")

        if health.is_healthy():
            lines.append("✓ Device is healthy and ready for OTA updates")
        else:
            lines.append("✗ Device health check failed - not ready for OTA")

        return "\n".join(lines)

    def _show_tile_health(self, tile: str) -> str:
        """Show health summary for all devices in tile."""
        devices = [d for d in self.device_manager.devices.values() if d.tile == tile]

        if not devices:
            return f"No devices found in tile {tile}."

        lines = [f"Tile Health Summary: {tile}", ""]
        lines.append(f"Devices: {len(devices)}")
        lines.append("")

        healthy_count = 0
        warn_count = 0
        fail_count = 0

        for device in devices:
            health = self.provisioner.health_check(device.id)

            if health.result == HealthCheckResult.PASS:
                healthy_count += 1
                status_icon = "✓"
            elif health.result == HealthCheckResult.WARN:
                warn_count += 1
                status_icon = "⚠"
            else:
                fail_count += 1
                status_icon = "✗"

            lines.append(
                f"{status_icon} {device.id:<8} {device.type.value:<12} {health.signal_strength:>3}% signal"
            )

        lines.append("")
        lines.append(
            f"Summary: {healthy_count} healthy, {warn_count} warnings, {fail_count} failures"
        )

        return "\n".join(lines)

    def _handle_provision(self, args: List[str]) -> str:
        """Handle SCREWDRIVER PROVISION command."""
        if len(args) < 2:
            return (
                "Usage: SCREWDRIVER PROVISION <devices> <version> [--strategy=<strategy>]\n"
                "Strategies: sequential, parallel, rolling, critical, leaf"
            )

        # Parse device list
        device_spec = args[0]
        version = args[1]

        # Parse strategy
        strategy = ProvisionStrategy.SEQUENTIAL
        for arg in args[2:]:
            if arg.startswith("--strategy="):
                strategy_name = arg.split("=")[1].upper()
                strategy_map = {
                    "SEQUENTIAL": ProvisionStrategy.SEQUENTIAL,
                    "PARALLEL": ProvisionStrategy.PARALLEL,
                    "ROLLING": ProvisionStrategy.ROLLING,
                    "CRITICAL": ProvisionStrategy.CRITICAL_FIRST,
                    "LEAF": ProvisionStrategy.LEAF_FIRST,
                }
                strategy = strategy_map.get(strategy_name, ProvisionStrategy.SEQUENTIAL)

        # Parse device list (comma-separated or tile code)
        if "," in device_spec:
            device_ids = [d.strip() for d in device_spec.split(",")]
        elif device_spec in self.device_manager.devices:
            device_ids = [device_spec]
        else:
            # Assume tile code - get all devices
            device_ids = [
                d.id
                for d in self.device_manager.devices.values()
                if d.tile == device_spec
            ]

        if not device_ids:
            return f"No devices found: {device_spec}"

        # Create and execute provision job
        job = self.provisioner.create_provision_job(device_ids, version, strategy)

        lines = [f"Provision Job Created: {job.job_id}", ""]
        lines.append(f"Strategy: {strategy.value}")
        lines.append(f"Target Version: v{version}")
        lines.append(f"Devices: {len(device_ids)}")
        lines.append("")
        lines.append("Executing provision job...")
        lines.append("")

        # Execute (in production, this would be async)
        result = self.provisioner.execute_provision_job(job.job_id)

        lines.append(f"Job Complete: {result.job_id}")
        lines.append(f"  Success: {result.success_count}/{len(result.device_ids)}")
        lines.append(f"  Failures: {result.failure_count}")
        lines.append(f"  Rollbacks: {result.rollback_count}")

        return "\n".join(lines)

    def _handle_status(self, args: List[str]) -> str:
        """Handle SCREWDRIVER STATUS command."""
        if not args:
            # Show all devices with firmware status
            return self._show_all_status()
        else:
            # Show specific device
            device_id = args[0]
            return self._show_device_status(device_id)

    def _show_all_status(self) -> str:
        """Show firmware status for all devices."""
        devices = list(self.device_manager.devices.values())

        if not devices:
            return "No devices registered."

        lines = ["Firmware Status Overview", ""]
        lines.append(
            f"{'Device':<10} {'Type':<12} {'Version':<10} {'Status':<8} {'Signal':<8}"
        )
        lines.append("-" * 60)

        for device in devices:
            lines.append(
                f"{device.id:<10} "
                f"{device.type.value:<12} "
                f"v{device.firmware_version:<9} "
                f"{device.firmware_status.value:<8} "
                f"{device.signal:>3}%"
            )

        # Summary
        latest_version = self.flash_manager.get_latest_version()
        if latest_version:
            up_to_date = sum(1 for d in devices if d.firmware_version == latest_version)
            lines.append("")
            lines.append(
                f"Latest: v{latest_version} ({up_to_date}/{len(devices)} devices up to date)"
            )

        return "\n".join(lines)

    def _show_device_status(self, device_id: str) -> str:
        """Show detailed status for specific device."""
        device = self.device_manager.get_device(device_id)

        if not device:
            return f"Device {device_id} not found."

        lines = [f"Device Status: {device_id}", ""]

        lines.append(f"Type: {device.type.value}")
        lines.append(f"Location: {device.tile}-{device.layer}")
        lines.append(f"Status: {device.status.value} {device.status.name}")
        lines.append("")

        lines.append("Firmware:")
        lines.append(f"  Version: v{device.firmware_version}")
        lines.append(
            f"  Status: {device.firmware_status.value} {device.firmware_status.name}"
        )

        # Check for updates
        latest = self.flash_manager.get_latest_version(device.type.value)
        if latest and latest != device.firmware_version:
            lines.append(f"  Update Available: v{latest}")

        lines.append("")
        lines.append("Metrics:")
        lines.append(f"  Signal: {device.signal}%")
        lines.append(f"  Uptime: {device.uptime:.1f}h")
        lines.append(f"  Messages: {device.msgs_per_sec} msgs/sec")
        lines.append(f"  Connections: {len(device.connections)}")

        return "\n".join(lines)

    def _handle_jobs(self, args: List[str]) -> str:
        """Handle SCREWDRIVER JOBS command."""
        if not args or args[0] == "--list":
            return self._list_jobs()
        elif args[0].startswith("--status="):
            job_id = args[0].split("=")[1]
            return self._show_job_status(job_id)
        else:
            return "Usage: SCREWDRIVER JOBS [--list|--status=<job_id>]"

    def _list_jobs(self) -> str:
        """List all provision jobs."""
        jobs = self.provisioner.list_jobs()

        if not jobs:
            return "No provision jobs found."

        lines = ["Provision Jobs:", ""]
        lines.append(
            f"{'Job ID':<15} {'Status':<12} {'Devices':<10} {'Success':<10} {'Failures':<10}"
        )
        lines.append("-" * 70)

        for job in jobs:
            lines.append(
                f"{job.job_id:<15} "
                f"{job.status:<12} "
                f"{len(job.device_ids):<10} "
                f"{job.success_count:<10} "
                f"{job.failure_count:<10}"
            )

        return "\n".join(lines)

    def _show_job_status(self, job_id: str) -> str:
        """Show detailed job status."""
        job = self.provisioner.get_job_status(job_id)

        if not job:
            return f"Job {job_id} not found."

        lines = [f"Provision Job: {job.job_id}", ""]

        lines.append(f"Status: {job.status}")
        lines.append(f"Strategy: {job.strategy.value}")
        lines.append(f"Target Version: v{job.target_version}")
        lines.append("")

        lines.append(f"Created: {job.created_at}")
        if job.started_at:
            lines.append(f"Started: {job.started_at}")
        if job.completed_at:
            lines.append(f"Completed: {job.completed_at}")
        lines.append("")

        lines.append(f"Devices: {len(job.device_ids)}")
        lines.append(f"  Success: {job.success_count}")
        lines.append(f"  Failures: {job.failure_count}")
        lines.append(f"  Rollbacks: {job.rollback_count}")

        return "\n".join(lines)

    def _handle_rollback(self, args: List[str]) -> str:
        """Handle SCREWDRIVER ROLLBACK command."""
        if not args:
            return "Usage: SCREWDRIVER ROLLBACK <device_id>"

        device_id = args[0]

        # Get current active bank
        current_bank = self.provisioner.active_banks.get(device_id, "A")
        rollback_bank = "A" if current_bank == "B" else "B"

        lines = [f"Rolling back {device_id}", ""]
        lines.append(f"Current Bank: {current_bank}")
        lines.append(f"Rollback to Bank: {rollback_bank}")
        lines.append("")

        # Perform rollback
        self.provisioner.active_banks[device_id] = rollback_bank

        lines.append(f"✓ Rollback complete")
        lines.append(f"  Device {device_id} now running from Bank {rollback_bank}")

        return "\n".join(lines)

    def _handle_banks(self, args: List[str]) -> str:
        """Handle SCREWDRIVER BANKS command."""
        if not args:
            return "Usage: SCREWDRIVER BANKS <device_id>"

        device_id = args[0]
        device = self.device_manager.get_device(device_id)

        if not device:
            return f"Device {device_id} not found."

        active_bank = self.provisioner.active_banks.get(device_id, "A")
        inactive_bank = "B" if active_bank == "A" else "A"

        lines = [f"Dual-Bank Status: {device_id}", ""]

        lines.append(f"Bank {active_bank} (ACTIVE):")
        lines.append(f"  Version: v{device.firmware_version}")
        lines.append(f"  Status: Running")
        lines.append("")

        lines.append(f"Bank {inactive_bank} (INACTIVE):")
        lines.append(f"  Status: Available for OTA updates")
        lines.append(f"  Safe rollback available")

        return "\n".join(lines)

    def _show_help(self) -> str:
        """Show SCREWDRIVER command help."""
        return """Sonic Screwdriver - Firmware Management (Layer 650)

Commands:
  SCREWDRIVER PACKS [--list|--validate <version>]
    List or validate firmware flash packs
    
  SCREWDRIVER FLASH <device_id> <version> [--force]
    Flash device with specific firmware version
    --force: Skip health checks
    
  SCREWDRIVER HEALTH <device_id|tile>
    Run health check on device or all devices in tile
    
  SCREWDRIVER PROVISION <devices> <version> [--strategy=<strategy>]
    Batch provision multiple devices
    devices: comma-separated IDs or tile code
    strategies: sequential, parallel, rolling, critical, leaf
    
  SCREWDRIVER STATUS [device_id]
    Show firmware status (all devices or specific device)
    
  SCREWDRIVER JOBS [--list|--status=<job_id>]
    List provision jobs or show job status
    
  SCREWDRIVER ROLLBACK <device_id>
    Rollback device to previous firmware bank
    
  SCREWDRIVER BANKS <device_id>
    Show dual-bank flash status

Examples:
  SCREWDRIVER PACKS --list
  SCREWDRIVER FLASH D1 2.5.0
  SCREWDRIVER HEALTH AA340
  SCREWDRIVER PROVISION D1,D2,D3 2.5.0 --strategy=critical
  SCREWDRIVER STATUS
  SCREWDRIVER ROLLBACK D1
"""


def demo_screwdriver_commands():
    """Demonstrate SCREWDRIVER command handler."""

    print("=" * 80)
    print("SCREWDRIVER Command Handler Demo - v1.2.14")
    print("=" * 80)
    print()

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        handler = ScrewdriverCommandHandler()

        # Setup test environment
        handler.flash_manager = FlashPackManager(Path(tmpdir) / "packs")
        handler.device_manager = MeshCoreDeviceManager(Path(tmpdir) / "devices.json")
        handler.provisioner = ScrewdriverProvisioner(
            handler.flash_manager, handler.device_manager
        )

        # Create test flash pack
        temp_binary = Path(tmpdir) / "firmware.bin"
        with open(temp_binary, "wb") as f:
            f.write(b"FIRMWARE_v2.5.0" * 1000)

        handler.flash_manager.create_flash_pack(
            version="2.5.0",
            binary_path=temp_binary,
            target_devices=["NODE", "GATEWAY", "SENSOR"],
            release_notes="Major update",
            features=["Improved routing", "Better power"],
            bugfixes=["Fixed memory leak"],
        )

        # Register test devices
        handler.device_manager.register_device(
            "D1", "AA340", 600, DeviceType.NODE, "2.4.0"
        )
        handler.device_manager.register_device(
            "D2", "AA340", 600, DeviceType.GATEWAY, "2.4.0"
        )

        handler.device_manager.update_device_status(
            "D1", status=DeviceStatus.ONLINE, signal=75, uptime=24.0, msgs_per_sec=145
        )
        handler.device_manager.update_device_status(
            "D2", status=DeviceStatus.ONLINE, signal=85, uptime=48.0, msgs_per_sec=267
        )

        # Demo commands
        demos = [
            ("SCREWDRIVER PACKS --list", "List flash packs"),
            ("SCREWDRIVER STATUS", "Show all device firmware status"),
            ("SCREWDRIVER HEALTH D1", "Check device D1 health"),
            ("SCREWDRIVER BANKS D1", "Show dual-bank status"),
            ("SCREWDRIVER FLASH D1 2.5.0", "Flash device D1"),
        ]

        for cmd, desc in demos:
            print(f"Demo: {desc}")
            print(f"Command: {cmd}")
            print("-" * 80)

            result = handler.handle_command(cmd.split()[1:])
            print(result)
            print()

        print("✅ SCREWDRIVER command demo complete!")


if __name__ == "__main__":
    demo_screwdriver_commands()
