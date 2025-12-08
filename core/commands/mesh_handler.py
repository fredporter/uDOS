#!/usr/bin/env python3
"""
MESH Command Handler - MeshCore network commands for Layer 600-650

Provides command interface for MeshCore device management, network topology
visualization, signal analysis, and routing operations.

Commands:
- MESH DEVICES [tile] - List devices in network or tile
- MESH INFO <device_id> - Show detailed device information
- MESH HEATMAP [tile] - Display signal strength heatmap
- MESH ROUTE <source> <target> - Find route between devices
- MESH TOPOLOGY [tile] - Show network topology grid
- MESH REGISTER <id> <tile> <type> - Register new device
- MESH CONNECT <device_a> <device_b> - Connect two devices
- MESH STATS - Show network statistics

Version: v1.2.14
Author: Fred Porter
Date: December 7, 2025
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path

from extensions.play.meshcore_device_manager import (
    MeshCoreDeviceManager,
    Device,
    DeviceType,
    DeviceStatus,
    FirmwareStatus
)

try:
    from core.ui.grid_renderer import GridRenderer, GridCell, ViewportTier, Symbols
    from core.ui.grid_template_loader import GridTemplateLoader
    GRID_SUPPORT = True
except ImportError:
    GRID_SUPPORT = False


class MeshCommandHandler:
    """Handler for MESH commands."""
    
    def __init__(self, device_manager: Optional[MeshCoreDeviceManager] = None):
        """
        Initialize MESH command handler.
        
        Args:
            device_manager: Optional device manager instance
        """
        if device_manager is None:
            # Default to extensions/play/data/meshcore/
            data_dir = Path(__file__).parent / "data" / "meshcore"
            device_manager = MeshCoreDeviceManager(data_dir)
        
        self.manager = device_manager
        
        if GRID_SUPPORT:
            self.grid_renderer = GridRenderer()
            self.template_loader = GridTemplateLoader()
        else:
            self.grid_renderer = None
            self.template_loader = None
    
    def handle(self, command: str, args: List[str]) -> str:
        """
        Handle MESH command.
        
        Args:
            command: Command name (e.g., "DEVICES", "INFO")
            args: Command arguments
            
        Returns:
            Command output
        """
        command = command.upper()
        
        if command == "DEVICES":
            return self._handle_devices(args)
        elif command == "INFO":
            return self._handle_info(args)
        elif command == "HEATMAP":
            return self._handle_heatmap(args)
        elif command == "ROUTE":
            return self._handle_route(args)
        elif command == "TOPOLOGY":
            return self._handle_topology(args)
        elif command == "REGISTER":
            return self._handle_register(args)
        elif command == "CONNECT":
            return self._handle_connect(args)
        elif command == "STATS":
            return self._handle_stats(args)
        else:
            return self._help()
    
    def _handle_devices(self, args: List[str]) -> str:
        """List devices in network or tile."""
        tile = args[0] if args else None
        layer = int(args[1]) if len(args) > 1 else None
        
        devices = self.manager.list_devices(tile=tile, layer=layer)
        
        if not devices:
            return "No devices found."
        
        # Build table
        lines = []
        lines.append("=" * 80)
        lines.append(f"MeshCore Devices{f' - {tile}' if tile else ''}")
        lines.append("=" * 80)
        lines.append("")
        
        # Header
        header = f"{'ID':<6} {'Type':<8} {'Status':<8} {'Signal':<8} {'Uptime':<10} {'Msgs/s':<8} {'TILE':<12}"
        lines.append(header)
        lines.append("-" * 80)
        
        # Device rows
        for device in sorted(devices, key=lambda d: d.id):
            row = (
                f"{device.id:<6} "
                f"{device.type.value:<8} "
                f"{device.status.value:<8} "
                f"{device.signal:>3}%{' '*4} "
                f"{device.uptime:>5.1f}h{' '*4} "
                f"{device.msgs_per_sec:>5}{' '*3} "
                f"{device.tile}-{device.layer}"
            )
            lines.append(row)
        
        lines.append("")
        lines.append(f"Total: {len(devices)} devices")
        
        return '\n'.join(lines)
    
    def _handle_info(self, args: List[str]) -> str:
        """Show detailed device information."""
        if not args:
            return "Usage: MESH INFO <device_id>"
        
        device_id = args[0]
        device = self.manager.get_device(device_id)
        
        if not device:
            return f"Device not found: {device_id}"
        
        lines = []
        lines.append("=" * 60)
        lines.append(f"Device Information - {device.id}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"  TILE Code:        {device.full_code}")
        lines.append(f"  Type:             {device.type.name} {device.type.value}")
        lines.append(f"  Status:           {device.status.name} {device.status.value}")
        lines.append(f"  Signal Strength:  {device.signal}%")
        lines.append(f"  Firmware:         v{device.firmware_version} {device.firmware_status.value}")
        lines.append(f"  Uptime:           {device.uptime:.1f} hours")
        lines.append(f"  Throughput:       {device.msgs_per_sec} msgs/sec")
        lines.append("")
        
        if device.connections:
            lines.append(f"  Connections ({len(device.connections)}):")
            for conn_id in device.connections:
                conn_device = self.manager.get_device(conn_id)
                if conn_device:
                    lines.append(f"    → {conn_id} ({conn_device.type.value} {conn_device.status.value})")
        else:
            lines.append("  Connections: None")
        
        return '\n'.join(lines)
    
    def _handle_heatmap(self, args: List[str]) -> str:
        """Display signal strength heatmap."""
        if not GRID_SUPPORT:
            return "Grid rendering not available (missing grid_renderer module)"
        
        tile = args[0] if args else "AA340"
        
        # Generate heatmap data
        heatmap_data = self.manager.get_signal_heatmap(tile, width=6, height=4)
        
        # Render using template
        try:
            # Update template with actual heatmap data
            result = self.template_loader.render_template('meshcore_heatmap', {
                'tile_base': tile
            })
            return result
        except Exception as e:
            # Fallback to simple rendering
            lines = []
            lines.append(f"Signal Coverage Grid - {tile}")
            lines.append("=" * 40)
            
            for row in heatmap_data:
                row_str = ""
                for signal in row:
                    row_str += Symbols.signal_gradient(signal) * 4 + " "
                lines.append(row_str)
            
            lines.append("")
            lines.append("Legend: █=100% ▓=75% ▒=50% ░=25% ' '=0%")
            
            return '\n'.join(lines)
    
    def _handle_route(self, args: List[str]) -> str:
        """Find route between devices."""
        if len(args) < 2:
            return "Usage: MESH ROUTE <source> <target>"
        
        source = args[0]
        target = args[1]
        
        route = self.manager.find_route(source, target)
        
        if not route:
            return f"No route found between {source} and {target}"
        
        lines = []
        lines.append(f"Route: {source} → {target}")
        lines.append("=" * 60)
        lines.append("")
        
        # Build route visualization
        route_str = " → ".join(route)
        lines.append(f"  {route_str}")
        lines.append("")
        
        # Show hop details
        lines.append("Hop Details:")
        for i, device_id in enumerate(route):
            device = self.manager.get_device(device_id)
            if device:
                lines.append(
                    f"  {i+1}. {device.id} ({device.type.value}) - "
                    f"Signal: {device.signal}% - "
                    f"Status: {device.status.value}"
                )
        
        lines.append("")
        lines.append(f"Total Hops: {len(route)}")
        
        return '\n'.join(lines)
    
    def _handle_topology(self, args: List[str]) -> str:
        """Show network topology grid."""
        if not GRID_SUPPORT:
            return "Grid rendering not available (missing grid_renderer module)"
        
        tile = args[0] if args else "AA340"
        
        try:
            # Render topology template
            result = self.template_loader.render_template('meshcore_topology', {
                'tile_base': tile
            })
            return result
        except Exception as e:
            return f"Failed to render topology: {e}"
    
    def _handle_register(self, args: List[str]) -> str:
        """Register new device."""
        if len(args) < 3:
            return "Usage: MESH REGISTER <device_id> <tile> <type>\nTypes: NODE, GATEWAY, SENSOR, REPEATER, END_DEVICE"
        
        device_id = args[0]
        tile = args[1]
        type_str = args[2].upper()
        
        # Validate device type
        try:
            device_type = DeviceType[type_str]
        except KeyError:
            return f"Invalid device type: {type_str}\nValid types: NODE, GATEWAY, SENSOR, REPEATER, END_DEVICE"
        
        # Check if device already exists
        if self.manager.get_device(device_id):
            return f"Device already exists: {device_id}"
        
        # Register device
        device = self.manager.register_device(
            device_id=device_id,
            tile=tile,
            layer=600,
            device_type=device_type
        )
        
        return f"✓ Registered device {device_id} ({device_type.value}) at {device.full_code}"
    
    def _handle_connect(self, args: List[str]) -> str:
        """Connect two devices."""
        if len(args) < 2:
            return "Usage: MESH CONNECT <device_a> <device_b>"
        
        device_a = args[0]
        device_b = args[1]
        
        # Validate devices exist
        if not self.manager.get_device(device_a):
            return f"Device not found: {device_a}"
        
        if not self.manager.get_device(device_b):
            return f"Device not found: {device_b}"
        
        # Connect devices
        success = self.manager.connect_devices(device_a, device_b)
        
        if success:
            return f"✓ Connected {device_a} ↔ {device_b}"
        else:
            return f"Failed to connect {device_a} and {device_b}"
    
    def _handle_stats(self, args: List[str]) -> str:
        """Show network statistics."""
        stats = self.manager.get_network_stats()
        
        lines = []
        lines.append("=" * 60)
        lines.append("MeshCore Network Statistics")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"  Total Devices:      {stats['total_devices']}")
        lines.append(f"  Online:             {stats['online']}")
        lines.append(f"  Offline:            {stats['offline']}")
        lines.append(f"  Connecting:         {stats['connecting']}")
        lines.append(f"  Average Signal:     {stats['avg_signal']}%")
        lines.append(f"  Total Connections:  {stats['total_connections']}")
        lines.append("")
        
        return '\n'.join(lines)
    
    def _help(self) -> str:
        """Show MESH command help."""
        return """
MESH Commands - MeshCore Network Operations (v1.2.14)
=====================================================

Device Management:
  MESH DEVICES [tile] [layer]     - List all devices (optionally filtered)
  MESH INFO <device_id>            - Show detailed device information
  MESH REGISTER <id> <tile> <type> - Register new device
  MESH CONNECT <dev_a> <dev_b>     - Connect two devices

Network Visualization:
  MESH TOPOLOGY [tile]             - Show network topology grid
  MESH HEATMAP [tile]              - Display signal strength heatmap
  MESH ROUTE <source> <target>     - Find route between devices
  MESH STATS                       - Show network statistics

Device Types:
  NODE       ⊚  - Primary node/hub
  GATEWAY    ⊕  - Gateway/router
  SENSOR     ⊗  - Sensor/monitor
  REPEATER   ⊙  - Repeater/relay
  END_DEVICE ⊘  - End device/client

Examples:
  MESH DEVICES AA340              - List devices in tile AA340
  MESH INFO D1                    - Show info for device D1
  MESH ROUTE D1 D5                - Find route from D1 to D5
  MESH REGISTER D9 JF57 SENSOR    - Register new sensor at JF57
  MESH CONNECT D1 D9              - Connect D1 to D9
"""


def demo_mesh_commands():
    """Demonstrate MESH command handler."""
    
    print("=" * 80)
    print("MESH Command Handler Demo - v1.2.14")
    print("=" * 80)
    print()
    
    # Create handler with temp data
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = MeshCoreDeviceManager(Path(tmpdir))
        handler = MeshCommandHandler(manager)
        
        # Setup test network
        print("Setting up test network...")
        manager.register_device("D1", "AA340", 600, DeviceType.NODE, "2.4.1")
        manager.register_device("D2", "AA340", 600, DeviceType.GATEWAY, "2.4.1")
        manager.register_device("D3", "AA340", 600, DeviceType.SENSOR, "2.4.1")
        manager.register_device("D4", "AA340", 600, DeviceType.REPEATER, "2.3.0")
        manager.register_device("D5", "AA340", 600, DeviceType.END_DEVICE, "2.4.1")
        
        manager.update_device_status("D1", DeviceStatus.ONLINE, signal=82, uptime=24.0, msgs_per_sec=145)
        manager.update_device_status("D2", DeviceStatus.ONLINE, signal=76, uptime=18.0, msgs_per_sec=203)
        manager.update_device_status("D3", DeviceStatus.ONLINE, signal=91, uptime=36.0, msgs_per_sec=87)
        manager.update_device_status("D4", DeviceStatus.OFFLINE, signal=0, uptime=0.0, msgs_per_sec=0)
        manager.update_device_status("D5", DeviceStatus.ONLINE, signal=68, uptime=12.0, msgs_per_sec=54)
        
        manager.connect_devices("D1", "D2")
        manager.connect_devices("D1", "D3")
        manager.connect_devices("D2", "D5")
        manager.connect_devices("D3", "D5")
        print("  ✓ Test network ready (5 devices, 4 connections)")
        print()
        
        # Demo commands
        commands = [
            ("MESH STATS", []),
            ("MESH DEVICES", ["AA340"]),
            ("MESH INFO", ["D1"]),
            ("MESH ROUTE", ["D1", "D5"]),
            ("MESH HEATMAP", ["AA340"]),
        ]
        
        for cmd, args in commands:
            print(f"Command: {cmd} {' '.join(args)}")
            print("-" * 80)
            
            # Extract command name
            cmd_name = cmd.split()[1] if ' ' in cmd else cmd
            result = handler.handle(cmd_name, args)
            print(result)
            print()


if __name__ == "__main__":
    demo_mesh_commands()
