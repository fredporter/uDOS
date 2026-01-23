"""
Port Manager CLI - Command-line interface for port management
"""

import sys
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from wizard.services.port_manager import (
    get_port_manager,
    ServiceEnvironment,
    ServiceStatus,
)


def cmd_status(args: list):
    """Show status of all services and ports."""
    pm = get_port_manager()
    print(pm.generate_report())


def cmd_check(args: list):
    """Check a specific service."""
    if not args:
        print("Usage: port-manager check <service_name>")
        return

    pm = get_port_manager()
    service_name = args[0]

    if service_name not in pm.services:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available: {', '.join(pm.services.keys())}")
        return

    status = pm.check_service_port(service_name)
    service = pm.services[service_name]

    print(f"\n📋 Service: {service.name}")
    print(f"   Port: {service.port}")
    print(f"   Environment: {service.environment.value}")
    print(f"   Description: {service.description}")
    print(f"   Status: {status.value}")

    if service.pid:
        print(f"   PID: {service.pid}")

    if service.health_endpoint:
        print(f"   Health: {service.health_endpoint}")


def cmd_conflicts(args: list):
    """Show port conflicts."""
    pm = get_port_manager()
    conflicts = pm.get_conflicts()

    if not conflicts:
        print("✅ No port conflicts detected")
        return

    print("\n⚠️  PORT CONFLICTS DETECTED:\n")
    for svc_name, occupant in conflicts:
        svc = pm.services[svc_name]
        print(
            f"  Port {svc.port}: Expected '{svc.name}' but found '{occupant['process']}' (PID {occupant['pid']})"
        )
        print(
            f"    Kill with: lsof -i :{svc.port} | grep -v COMMAND | awk '{{print $2}}' | xargs kill -9"
        )
        print()


def cmd_kill(args: list):
    """Kill a service or port."""
    if not args:
        print("Usage: port-manager kill <service_name|:port>")
        return

    pm = get_port_manager()
    target = args[0]

    if target.startswith(":"):
        port = int(target[1:])
        print(f"Killing process on port {port}...")
        import subprocess

        try:
            # Use lsof -ti to get PIDs directly
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"], capture_output=True, text=True, timeout=5
            )
            pids = result.stdout.strip().split("\n")

            if not pids or not pids[0]:
                print(f"⚠️  No process found on port {port}")
                return

            # Kill each PID
            killed = []
            for pid in pids:
                if pid:
                    try:
                        subprocess.run(["kill", "-9", pid], timeout=2, check=False)
                        killed.append(pid)
                    except Exception as e:
                        print(f"⚠️  Failed to kill PID {pid}: {e}")

            if killed:
                print(f"✅ Killed process(es) on port {port}: PIDs {', '.join(killed)}")
            else:
                print(f"❌ Failed to kill any processes on port {port}")

        except Exception as e:
            print(f"❌ Failed to kill port {port}: {e}")
    else:
        if pm.kill_service(target):
            print(f"✅ Killed service: {target}")
        else:
            print(f"❌ Failed to kill service: {target}")


def cmd_env(args: list):
    """Generate environment variable script."""
    pm = get_port_manager()
    print(pm.generate_env_script())


def cmd_available(args: list):
    """Find available port."""
    start = int(args[0]) if args else 9000
    pm = get_port_manager()
    port = pm.get_available_port(start)
    print(f"Available port: {port}")


def cmd_reassign(args: list):
    """Reassign service to new port."""
    if len(args) < 2:
        print("Usage: port-manager reassign <service_name> <new_port>")
        return

    pm = get_port_manager()
    service_name = args[0]
    new_port = int(args[1])

    if pm.reassign_port(service_name, new_port):
        print(f"✅ Reassigned {service_name} to port {new_port}")
    else:
        print(f"❌ Failed to reassign {service_name}")


def cmd_heal(args: list):
    """Automatically heal all port conflicts."""
    pm = get_port_manager()
    conflicts = pm.get_conflicts()
    
    if not conflicts:
        print("✅ No conflicts to heal")
        return
    
    print(f"\n🔧 Healing {len(conflicts)} port conflict(s)...\n")
    results = pm.heal_conflicts()
    
    success_count = sum(1 for v in results.values() if v)
    print(f"\n{'✅' if success_count == len(results) else '⚠️ '} Healed {success_count}/{len(results)} conflicts")


def print_help():
    """Print help message."""
    help_text = """
🔌 uDOS Port Manager CLI
========================

Commands:
  status          Show status of all services
  check <name>    Check specific service status
  conflicts       Show port conflicts
  kill <name|:port> Kill service or process on port
  heal            Automatically heal all port conflicts
  env             Generate environment variable script
  available [port] Find available port (default: 9000)
  reassign <name> <port> Reassign service to new port
  help            Show this help message

Examples:
  port-manager status
  port-manager check wizard
  port-manager conflicts
  port-manager heal
  port-manager kill :8767
  port-manager available 9000
  port-manager reassign goblin 9000
"""
    print(help_text)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "status": cmd_status,
        "check": cmd_check,
        "conflicts": cmd_conflicts,
        "kill": cmd_kill,
        "heal": cmd_heal,
        "env": cmd_env,
        "available": cmd_available,
        "reassign": cmd_reassign,
        "help": lambda a: print_help(),
    }

    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"❌ Unknown command: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
