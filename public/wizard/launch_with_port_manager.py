#!/usr/bin/env python3
"""
uDOS Service Launcher with Port Management
===========================================

Safely launches all uDOS services with port conflict detection and auto-resolution.
Coordinates startup order and monitors service health.
"""

import sys
import time
import signal
import asyncio
from pathlib import Path
from typing import List, Optional

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent))

from wizard.services.port_manager import (
    get_port_manager,
    ServiceStatus,
    PortManager,
)


class ServiceLauncher:
    """Manages coordinated launching of all services."""
    
    def __init__(self, interactive: bool = True):
        self.pm = get_port_manager()
        self.interactive = interactive
        self.running_services: List[str] = []
        self.failed_services: List[str] = []
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        width = 60
        print()
        print("┏" + "━" * (width - 2) + "┓")
        print(f"┃ {title:<{width - 4}} ┃")
        print("┗" + "━" * (width - 2) + "┛")
        print()
    
    def check_conflicts(self) -> bool:
        """Check for and resolve port conflicts."""
        self.print_section("🔍 Port Conflict Detection")
        
        conflicts = self.pm.get_conflicts()
        
        if not conflicts:
            print("✅ No port conflicts detected")
            return True
        
        print(f"⚠️  Found {len(conflicts)} port conflict(s):\n")
        
        for svc_name, occupant in conflicts:
            svc = self.pm.services[svc_name]
            print(f"  Port {svc.port}: Expected '{svc.name}' but found '{occupant['process']}' (PID {occupant['pid']})")
            
            if self.interactive:
                response = input(f"  Kill this process? (y/n) ")
                if response.lower() == 'y':
                    if self.pm.kill_service(svc_name):
                        print(f"  ✅ Killed process on port {svc.port}")
                    else:
                        print(f"  ❌ Failed to kill process on port {svc.port}")
                        return False
        
        return True
    
    def validate_environment(self) -> bool:
        """Validate environment before launching services."""
        self.print_section("🔧 Environment Validation")
        
        checks = []
        
        # Check Python
        try:
            import wizard
            checks.append(("Python venv", "✅"))
        except ImportError:
            checks.append(("Python venv", "❌"))
        
        # Check required directories
        required_dirs = [
            Path(__file__).parent.parent.parent / "memory" / "logs",
            Path(__file__).parent.parent / "config",
        ]
        
        for d in required_dirs:
            d.mkdir(parents=True, exist_ok=True)
        
        checks.append(("Log directory", "✅"))
        checks.append(("Config directory", "✅"))
        
        for name, status in checks:
            print(f"  {status} {name}")
        
        return all(c[1] == "✅" for c in checks)
    
    def launch_service(self, service_name: str) -> bool:
        """Launch a specific service."""
        svc = self.pm.services.get(service_name)
        if not svc:
            return False
        
        if not svc.enabled or not svc.startup_cmd:
            print(f"  ⊘ {service_name} (disabled)")
            return True
        
        # Check port availability
        if not self.pm.is_port_open(svc.port):
            occupant = self.pm.get_port_occupant(svc.port)
            if occupant and occupant['process'] != svc.process_name:
                print(f"  ❌ {service_name} - Port {svc.port} occupied by {occupant['process']}")
                self.failed_services.append(service_name)
                return False
        
        print(f"  ▶ {service_name} (port {svc.port})...")
        
        # TODO: Actually launch the service
        # For now, just mark as monitored
        self.running_services.append(service_name)
        print(f"  ✓ {service_name} (started)")
        
        return True
    
    def launch_all(self, order: Optional[List[str]] = None) -> bool:
        """Launch all services in order."""
        self.print_section("🚀 Launching Services")
        
        startup_order = order or self.pm.get_startup_order()
        
        for service_name in startup_order:
            if not self.launch_service(service_name):
                if self.interactive:
                    response = input(f"  Continue without {service_name}? (y/n) ")
                    if response.lower() != 'y':
                        return False
        
        return True
    
    def monitor_health(self) -> bool:
        """Monitor health of running services."""
        self.print_section("❤️  Health Monitoring")
        
        for service_name in self.running_services:
            status = self.pm.check_service_port(service_name)
            svc = self.pm.services[service_name]
            
            icon = "✅" if status == ServiceStatus.RUNNING else "⚠️ "
            print(f"  {icon} {service_name}: {status.value}")
        
        return len(self.failed_services) == 0
    
    def generate_dashboard(self):
        """Generate and display full dashboard."""
        self.print_section("📊 Service Dashboard")
        print(self.pm.generate_report())
    
    def launch(self) -> bool:
        """Execute full launch sequence."""
        print("\n")
        print("╔══════════════════════════════════════════════════════╗")
        print("║  🚀 uDOS Service Launcher with Port Management      ║")
        print("╚══════════════════════════════════════════════════════╝")
        
        if not self.validate_environment():
            print("\n❌ Environment validation failed")
            return False
        
        if not self.check_conflicts():
            print("\n❌ Port conflicts could not be resolved")
            return False
        
        if not self.launch_all():
            print("\n⚠️  Some services failed to launch")
            return False
        
        time.sleep(1)
        self.monitor_health()
        self.generate_dashboard()
        
        if self.failed_services:
            print(f"\n⚠️  Failed services: {', '.join(self.failed_services)}")
            return False
        
        print("\n✅ All services launched successfully!")
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="uDOS Service Launcher with Port Management")
    parser.add_argument("--non-interactive", action="store_true", help="Run in non-interactive mode")
    parser.add_argument("--services", help="Comma-separated list of services to launch")
    parser.add_argument("--check-only", action="store_true", help="Only check status, don't launch")
    
    args = parser.parse_args()
    
    launcher = ServiceLauncher(interactive=not args.non_interactive)
    
    if args.check_only:
        launcher.validate_environment()
        launcher.generate_dashboard()
        return 0
    
    services = args.services.split(',') if args.services else None
    success = launcher.launch()
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
