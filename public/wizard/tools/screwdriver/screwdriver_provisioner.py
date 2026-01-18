#!/usr/bin/env python3
"""
Sonic Screwdriver Device Provisioner - OTA orchestration for Layer 650

Coordinates firmware updates across mesh networks using dual-bank flash,
rollback protection, and health monitoring.

Provisioning Workflow:
1. Pre-flash health check
2. Dual-bank safety (Bank A active, flash Bank B)
3. Validate Bank B firmware
4. Health check after swap
5. Rollback if health fails
6. Batch updates with dependency ordering

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

import json
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from .screwdriver_flash_packs import (
    FlashPackManager,
    FlashStage,
    FlashProgress,
    FlashPackStatus,
)
from .meshcore_device_manager import (
    MeshCoreDeviceManager,
    DeviceStatus,
    DeviceType,
    FirmwareStatus,
)


class ProvisionStrategy(Enum):
    """Provisioning strategies for batch updates."""

    SEQUENTIAL = "sequential"  # One device at a time
    PARALLEL = "parallel"  # All devices simultaneously
    ROLLING = "rolling"  # Maintain network connectivity
    CRITICAL_FIRST = "critical"  # Gateways/coordinators first
    LEAF_FIRST = "leaf"  # Leaf nodes first, upward


class HealthCheckResult(Enum):
    """Health check outcomes."""

    PASS = "✓"  # Device healthy
    WARN = "⚠"  # Degraded but functional
    FAIL = "✗"  # Critical failure
    UNKNOWN = "?"  # Unable to determine


@dataclass
class HealthCheck:
    """Device health check results."""

    device_id: str
    timestamp: str
    result: HealthCheckResult
    signal_strength: int  # 0-100%
    uptime_hours: float
    message_rate: float  # msgs/sec
    connection_count: int
    memory_usage: int  # 0-100%
    cpu_usage: int  # 0-100%
    errors: List[str]
    warnings: List[str]

    def is_healthy(self) -> bool:
        """Check if device is healthy enough for OTA."""
        if self.result == HealthCheckResult.FAIL:
            return False
        if self.signal_strength < 30:
            return False
        if self.memory_usage > 90 or self.cpu_usage > 90:
            return False
        return True


@dataclass
class ProvisionJob:
    """Firmware provisioning job."""

    job_id: str
    device_ids: List[str]
    target_version: str
    strategy: ProvisionStrategy
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    rollback_count: int = 0
    status: str = "pending"  # pending/running/complete/failed

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = asdict(self)
        d["strategy"] = self.strategy.value
        return d


class ScrewdriverProvisioner:
    """
    Orchestrate OTA firmware updates across mesh networks.

    Handles health checks, dual-bank flashing, rollback protection,
    and batch provisioning strategies.
    """

    def __init__(
        self,
        flash_manager: Optional[FlashPackManager] = None,
        device_manager: Optional[MeshCoreDeviceManager] = None,
    ):
        """
        Initialize provisioner.

        Args:
            flash_manager: Flash pack manager instance
            device_manager: Device manager instance
        """
        self.flash_manager = flash_manager or FlashPackManager()
        self.device_manager = device_manager or MeshCoreDeviceManager()

        self.jobs: Dict[str, ProvisionJob] = {}
        self.health_history: Dict[str, List[HealthCheck]] = {}

        # Dual-bank flash state
        self.active_banks: Dict[str, str] = {}  # device_id -> "A" or "B"

    def health_check(self, device_id: str) -> HealthCheck:
        """
        Perform comprehensive device health check.

        Args:
            device_id: Device to check

        Returns:
            HealthCheck results
        """
        device = self.device_manager.get_device(device_id)

        if not device:
            return HealthCheck(
                device_id=device_id,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                result=HealthCheckResult.UNKNOWN,
                signal_strength=0,
                uptime_hours=0,
                message_rate=0,
                connection_count=0,
                memory_usage=0,
                cpu_usage=0,
                errors=["Device not found"],
                warnings=[],
            )

        # Collect health metrics
        errors = []
        warnings = []

        # Check status
        if device.status != DeviceStatus.ONLINE:
            errors.append(f"Device {device.status.value}")

        # Check signal
        if device.signal < 30:
            errors.append(f"Low signal: {device.signal}%")
        elif device.signal < 50:
            warnings.append(f"Weak signal: {device.signal}%")

        # Check firmware status
        if device.firmware_status == FirmwareStatus.INCOMPATIBLE:
            errors.append("Incompatible firmware version")
        elif device.firmware_status == FirmwareStatus.OUTDATED:
            warnings.append("Firmware update available")

        # Determine result
        if errors:
            result = HealthCheckResult.FAIL
        elif warnings:
            result = HealthCheckResult.WARN
        else:
            result = HealthCheckResult.PASS

        # Simulated metrics (in production, query from device)
        check = HealthCheck(
            device_id=device_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            result=result,
            signal_strength=device.signal,
            uptime_hours=device.uptime,
            message_rate=device.msgs_per_sec,
            connection_count=len(device.connections),
            memory_usage=45,  # Simulated
            cpu_usage=32,  # Simulated
            errors=errors,
            warnings=warnings,
        )

        # Store in history
        if device_id not in self.health_history:
            self.health_history[device_id] = []
        self.health_history[device_id].append(check)

        return check

    def provision_device(
        self, device_id: str, target_version: str, force: bool = False
    ) -> bool:
        """
        Provision single device with firmware update.

        Args:
            device_id: Device to update
            target_version: Target firmware version
            force: Skip health checks

        Returns:
            True if provisioned successfully
        """
        # Pre-flash health check
        if not force:
            health = self.health_check(device_id)
            if not health.is_healthy():
                print(f"  ✗ Device {device_id} failed health check")
                print(f"    Errors: {', '.join(health.errors)}")
                return False

        # Validate flash pack
        status = self.flash_manager.validate_flash_pack(target_version)
        if status != FlashPackStatus.VALID:
            print(f"  ✗ Flash pack v{target_version} invalid: {status.value}")
            return False

        # Determine active/inactive banks
        active_bank = self.active_banks.get(device_id, "A")
        inactive_bank = "B" if active_bank == "A" else "A"

        print(f"  → Flash Bank {inactive_bank} (keep Bank {active_bank} safe)")

        # Start flash operation
        progress = self.flash_manager.start_flash(device_id, target_version)
        if not progress:
            return False

        # Update device firmware status
        self.device_manager.update_firmware_status(
            device_id, status=FirmwareStatus.OUTDATED  # Mark as updating
        )

        # Simulate flash stages
        stages = [
            (FlashStage.VERIFYING, 10),
            (FlashStage.ERASING, 25),
            (FlashStage.WRITING, 75),
            (FlashStage.VALIDATING, 90),
        ]

        for stage, pct in stages:
            self.flash_manager.update_flash_progress(device_id, stage, pct)
            time.sleep(0.1)  # Simulated delay

        # Bank swap
        print(f"  → Bank swap: {active_bank} → {inactive_bank}")
        self.active_banks[device_id] = inactive_bank

        # Health check after swap
        self.flash_manager.update_flash_progress(device_id, FlashStage.HEALTH_CHECK, 95)

        post_health = self.health_check(device_id)

        if not post_health.is_healthy() and not force:
            print(f"  ⚠ Post-update health check failed - ROLLBACK!")

            # Rollback to previous bank
            self.active_banks[device_id] = active_bank

            self.device_manager.update_firmware_status(
                device_id, status=FirmwareStatus.INCOMPATIBLE
            )

            self.flash_manager.complete_flash(device_id, success=False)
            return False

        # Success!
        self.flash_manager.update_flash_progress(device_id, FlashStage.COMPLETE, 100)

        self.device_manager.update_firmware_status(
            device_id, version=target_version, status=FirmwareStatus.CURRENT
        )

        self.flash_manager.complete_flash(device_id, success=True)
        return True

    def create_provision_job(
        self,
        device_ids: List[str],
        target_version: str,
        strategy: ProvisionStrategy = ProvisionStrategy.SEQUENTIAL,
    ) -> ProvisionJob:
        """
        Create batch provisioning job.

        Args:
            device_ids: Devices to update
            target_version: Target firmware version
            strategy: Provisioning strategy

        Returns:
            Created ProvisionJob
        """
        job_id = f"JOB-{int(time.time())}"

        job = ProvisionJob(
            job_id=job_id,
            device_ids=device_ids,
            target_version=target_version,
            strategy=strategy,
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

        self.jobs[job_id] = job
        return job

    def execute_provision_job(self, job_id: str) -> ProvisionJob:
        """
        Execute provisioning job.

        Args:
            job_id: Job to execute

        Returns:
            Updated job with results
        """
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")

        job = self.jobs[job_id]
        job.status = "running"
        job.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Order devices by strategy
        ordered_devices = self._order_devices_by_strategy(job.device_ids, job.strategy)

        print(
            f"Executing {job.strategy.value} provisioning: {len(ordered_devices)} devices"
        )
        print()

        # Provision each device
        for idx, device_id in enumerate(ordered_devices, 1):
            print(f"[{idx}/{len(ordered_devices)}] Provisioning {device_id}...")

            success = self.provision_device(device_id, job.target_version)

            if success:
                job.success_count += 1
                print(f"  ✓ {device_id} updated to v{job.target_version}")
            else:
                job.failure_count += 1
                print(f"  ✗ {device_id} failed")

            print()

        job.status = "complete"
        job.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        return job

    def _order_devices_by_strategy(
        self, device_ids: List[str], strategy: ProvisionStrategy
    ) -> List[str]:
        """Order devices according to provisioning strategy."""

        if strategy == ProvisionStrategy.SEQUENTIAL:
            # Simple order
            return device_ids

        elif strategy == ProvisionStrategy.CRITICAL_FIRST:
            # Gateways first, then coordinators, then nodes
            critical = []
            normal = []

            for device_id in device_ids:
                device = self.device_manager.get_device(device_id)
                if device and device.type.value in ["GATEWAY", "COORDINATOR"]:
                    critical.append(device_id)
                else:
                    normal.append(device_id)

            return critical + normal

        elif strategy == ProvisionStrategy.LEAF_FIRST:
            # Leaf nodes first (fewest connections)
            devices_with_connections = []

            for device_id in device_ids:
                device = self.device_manager.get_device(device_id)
                conn_count = len(device.connections) if device else 0
                devices_with_connections.append((device_id, conn_count))

            # Sort by connection count (ascending)
            devices_with_connections.sort(key=lambda x: x[1])
            return [d[0] for d in devices_with_connections]

        else:
            # Default to simple order
            return device_ids

    def get_job_status(self, job_id: str) -> Optional[ProvisionJob]:
        """Get provision job status."""
        return self.jobs.get(job_id)

    def list_jobs(self) -> List[ProvisionJob]:
        """List all provision jobs."""
        return list(self.jobs.values())


def demo_screwdriver_provisioner():
    """Demonstrate Sonic Screwdriver provisioner functionality."""

    print("=" * 80)
    print("Sonic Screwdriver Device Provisioner Demo - v1.2.14")
    print("=" * 80)
    print()

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize managers
        flash_mgr = FlashPackManager(Path(tmpdir) / "flash_packs")
        device_mgr = MeshCoreDeviceManager(Path(tmpdir) / "devices.json")
        provisioner = ScrewdriverProvisioner(flash_mgr, device_mgr)

        # Create test firmware
        temp_binary = Path(tmpdir) / "firmware.bin"
        with open(temp_binary, "wb") as f:
            f.write(b"FIRMWARE_v2.5.0" * 1000)

        flash_mgr.create_flash_pack(
            version="2.5.0",
            binary_path=temp_binary,
            target_devices=["NODE", "GATEWAY"],
            release_notes="Performance improvements",
            features=["Faster mesh routing", "Better power management"],
            bugfixes=["Fixed memory leak"],
        )

        # Register test devices
        device_mgr.register_device("D1", "AA340", 600, DeviceType.NODE, "2.4.0")
        device_mgr.register_device("D2", "AA340", 600, DeviceType.GATEWAY, "2.4.0")
        device_mgr.register_device("D3", "AA340", 600, DeviceType.SENSOR, "2.4.0")

        device_mgr.update_device_status(
            "D1", status=DeviceStatus.ONLINE, signal=75, uptime=24.0, msgs_per_sec=145
        )
        device_mgr.update_device_status(
            "D2", status=DeviceStatus.ONLINE, signal=85, uptime=48.0, msgs_per_sec=267
        )
        device_mgr.update_device_status(
            "D3", status=DeviceStatus.ONLINE, signal=65, uptime=12.0, msgs_per_sec=89
        )

        # Demo 1: Health check
        print("Demo 1: Pre-Provision Health Check")
        print("-" * 80)

        health = provisioner.health_check("D1")
        print(f"  Device: D1")
        print(f"  Result: {health.result.value}")
        print(f"  Signal: {health.signal_strength}%")
        print(f"  Uptime: {health.uptime_hours:.1f}h")
        print(f"  Memory: {health.memory_usage}%")
        print(f"  CPU: {health.cpu_usage}%")
        print(f"  Healthy: {health.is_healthy()}")
        print()

        # Demo 2: Single device provision
        print("Demo 2: Single Device Provisioning")
        print("-" * 80)

        success = provisioner.provision_device("D1", "2.5.0")
        print(f"  Result: {'✓ Success' if success else '✗ Failed'}")
        print()

        # Demo 3: Batch provisioning job
        print("Demo 3: Batch Provisioning (Critical First)")
        print("-" * 80)

        job = provisioner.create_provision_job(
            device_ids=["D1", "D2", "D3"],
            target_version="2.5.0",
            strategy=ProvisionStrategy.CRITICAL_FIRST,
        )

        print(f"  Created job: {job.job_id}")
        print(f"  Strategy: {job.strategy.value}")
        print(f"  Devices: {len(job.device_ids)}")
        print()

        result = provisioner.execute_provision_job(job.job_id)

        print("Job Summary:")
        print(f"  Status: {result.status}")
        print(f"  Success: {result.success_count}/{len(result.device_ids)}")
        print(f"  Failures: {result.failure_count}")
        print(f"  Rollbacks: {result.rollback_count}")
        print()

        print("✅ Provisioner demo complete!")


if __name__ == "__main__":
    demo_screwdriver_provisioner()
