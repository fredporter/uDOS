"""
Server Monitor Service (v1.2.17)

Monitors all uDOS servers and provides status information for TUI display.
Integrates with existing ServerManager and port registry.
Includes system health metrics for memory, disk, and logs.
"""

import sys
import psutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Add extensions to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'extensions'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'extensions' / 'core'))


class ServerMonitor:
    """
    Monitor all uDOS servers with health checking and status tracking.
    
    Features:
    - Real-time server status
    - Health endpoint checking
    - Port availability monitoring
    - Process management integration
    - Extension server discovery
    """
    
    # Core servers from server_manager.py
    @staticmethod
    def get_core_servers(host='localhost'):
        """Get core server configurations with configurable host."""
        return {
            'api': {
                'name': 'API Server',
                'port': 5001,
                'health_url': f'http://{host}:5001/api/health',
                'type': 'core',
                'managed': True
            },
            'terminal': {
                'name': 'Retro Terminal',
                'port': 8889,
                'health_url': f'http://{host}:8889/health',
                'type': 'core',
                'managed': True
            },
            'dashboard': {
                'name': 'System Dashboard',
                'port': 8888,
                'health_url': f'http://{host}:8888/health',
                'type': 'core',
                'managed': True
            },
            'teletext': {
                'name': 'Teletext Display',
                'port': 9002,
                'health_url': f'http://{host}:9002/health',
                'type': 'core',
                'managed': True
            },
            'desktop': {
                'name': 'Retro Desktop',
                'port': 8892,
                'health_url': f'http://{host}:8892/health',
                'type': 'core',
                'managed': True
            }
        }
    
    # Extension servers (not managed by server_manager)
    @staticmethod
    def get_extension_servers(host='localhost'):
        """Get extension server configurations with configurable host."""
        return {
            'mission': {
                'name': 'Mission Control',
                'port': 5000,
                'health_url': f'http://{host}:5000/health',
                'type': 'extension',
                'managed': False
            },
            'graphics': {
                'name': 'Graphics Renderer',
                'port': 5555,
                'health_url': f'http://{host}:5555/health',
                'type': 'extension',
                'managed': False
            },
            'map': {
                'name': 'Map Server',
                'port': 8080,
                'health_url': f'http://{host}:8080/health',
                'type': 'extension',
                'managed': False
            }
        }
    
    def __init__(self, host='localhost'):
        """Initialize server monitor with configurable host"""
        self.host = host
        self.all_servers = {**self.get_core_servers(host), **self.get_extension_servers(host)}
        self._server_manager = None
        self._port_manager = None
        self._last_check = {}
        
    @property
    def server_manager(self):
        """Lazy load ServerManager"""
        if self._server_manager is None:
            try:
                from server_manager import ServerManager
                self._server_manager = ServerManager()
            except ImportError:
                pass
        return self._server_manager
    
    @property
    def port_manager(self):
        """Lazy load PortManager"""
        if self._port_manager is None:
            try:
                from extensions.core.shared.port_manager import PortManager
                self._port_manager = PortManager()
            except ImportError:
                pass
        return self._port_manager
    
    def check_server_health(self, server_key: str) -> Dict:
        """
        Check health of a specific server.
        
        Args:
            server_key: Server identifier (api, terminal, etc.)
            
        Returns:
            Dict with status information
        """
        server = self.all_servers.get(server_key)
        if not server:
            return {
                'server': server_key,
                'status': 'unknown',
                'error': 'Unknown server',
                'timestamp': datetime.now().isoformat()
            }
        
        result = {
            'server': server_key,
            'name': server['name'],
            'port': server['port'],
            'type': server['type'],
            'managed': server['managed'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Check if port is in use
        if self.port_manager:
            port_available = self.port_manager.is_port_available(server['port'])
            result['port_in_use'] = not port_available  # invert - if available, not in use
        else:
            result['port_in_use'] = None
        
        # Check health endpoint if managed
        if server['managed'] and self.server_manager:
            healthy, status_msg = self.server_manager.check_health(server_key)
            result['healthy'] = healthy
            result['status'] = 'running' if healthy else 'stopped'
            result['message'] = status_msg
        else:
            # For unmanaged servers, just check port
            if result.get('port_in_use'):
                result['status'] = 'running'
                result['healthy'] = True
                result['message'] = 'Port in use'
            else:
                result['status'] = 'stopped'
                result['healthy'] = False
                result['message'] = 'Port not in use'
        
        # Cache result
        self._last_check[server_key] = result
        
        return result
    
    def get_all_server_status(self) -> List[Dict]:
        """
        Get status of all servers.
        
        Returns:
            List of server status dicts
        """
        statuses = []
        
        for server_key in self.all_servers.keys():
            status = self.check_server_health(server_key)
            statuses.append(status)
        
        return statuses
    
    def get_running_servers(self) -> List[Dict]:
        """Get list of running servers"""
        all_status = self.get_all_server_status()
        return [s for s in all_status if s.get('status') == 'running']
    
    def get_stopped_servers(self) -> List[Dict]:
        """Get list of stopped servers"""
        all_status = self.get_all_server_status()
        return [s for s in all_status if s.get('status') == 'stopped']
    
    def get_server_count(self) -> Dict[str, int]:
        """Get count of servers by status"""
        all_status = self.get_all_server_status()
        
        return {
            'total': len(all_status),
            'running': len([s for s in all_status if s.get('status') == 'running']),
            'stopped': len([s for s in all_status if s.get('status') == 'stopped']),
            'core': len([s for s in all_status if s.get('type') == 'core']),
            'extension': len([s for s in all_status if s.get('type') == 'extension'])
        }
    
    def start_server(self, server_key: str) -> Dict:
        """
        Start a server (if managed).
        
        Args:
            server_key: Server to start
            
        Returns:
            Result dict with success status
        """
        server = self.all_servers.get(server_key)
        if not server:
            return {'success': False, 'error': 'Unknown server'}
        
        if not server['managed']:
            return {'success': False, 'error': 'Server not managed by uDOS'}
        
        # TODO: Implement server starting via server_manager
        # For now, just return a placeholder
        return {
            'success': False,
            'error': 'Server starting not yet implemented',
            'server': server_key,
            'name': server['name']
        }
    
    def stop_server(self, server_key: str) -> Dict:
        """
        Stop a server (if managed).
        
        Args:
            server_key: Server to stop
            
        Returns:
            Result dict with success status
        """
        server = self.all_servers.get(server_key)
        if not server:
            return {'success': False, 'error': 'Unknown server'}
        
        if not server['managed'] or not self.server_manager:
            return {'success': False, 'error': 'Server not managed or manager unavailable'}
        
        # Use server_manager cleanup
        success = self.server_manager.cleanup_server(server_key)
        
        return {
            'success': success,
            'server': server_key,
            'name': server['name']
        }
    
    def restart_server(self, server_key: str) -> Dict:
        """
        Restart a server (stop then start).
        
        Args:
            server_key: Server to restart
            
        Returns:
            Result dict with success status
        """
        # Stop first
        stop_result = self.stop_server(server_key)
        if not stop_result['success']:
            return stop_result
        
        # Wait a moment
        import time
        time.sleep(1)
        
        # Start
        start_result = self.start_server(server_key)
        
        return {
            'success': start_result['success'],
            'server': server_key,
            'stopped': stop_result['success'],
            'started': start_result['success']
        }
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive server summary.
        
        Returns:
            Summary dict with counts and status
        """
        counts = self.get_server_count()
        running = self.get_running_servers()
        stopped = self.get_stopped_servers()
        
        return {
            'counts': counts,
            'running': [{'server': s['server'], 'name': s['name'], 'port': s['port']} for s in running],
            'stopped': [{'server': s['server'], 'name': s['name'], 'port': s['port']} for s in stopped],
            'timestamp': datetime.now().isoformat()
        }
    
    # System Health Tracking
    
    def get_memory_usage(self) -> Dict:
        """
        Get system memory usage metrics.
        
        Returns:
            Dict with memory stats (MB and percentages)
        """
        mem = psutil.virtual_memory()
        
        return {
            'total_mb': round(mem.total / 1024 / 1024, 2),
            'available_mb': round(mem.available / 1024 / 1024, 2),
            'used_mb': round(mem.used / 1024 / 1024, 2),
            'percent': mem.percent,
            'status': 'healthy' if mem.percent < 80 else 'warning' if mem.percent < 90 else 'critical'
        }
    
    def get_disk_usage(self, path: Optional[Path] = None) -> Dict:
        """
        Get disk usage for uDOS workspace.
        
        Args:
            path: Path to check (defaults to project root)
            
        Returns:
            Dict with disk stats (GB and percentages)
        """
        if path is None:
            path = Path(__file__).parent.parent.parent
        
        disk = psutil.disk_usage(str(path))
        
        return {
            'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
            'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
            'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
            'percent': disk.percent,
            'status': 'healthy' if disk.percent < 80 else 'warning' if disk.percent < 90 else 'critical'
        }
    
    def get_log_file_sizes(self) -> Dict:
        """
        Get log file sizes from memory/logs/.
        
        Returns:
            Dict with log file stats
        """
        logs_path = Path(__file__).parent.parent.parent / 'memory' / 'logs'
        
        if not logs_path.exists():
            return {
                'total_size_mb': 0,
                'file_count': 0,
                'largest_file': None,
                'status': 'healthy'
            }
        
        total_size = 0
        file_count = 0
        largest_file = None
        largest_size = 0
        
        for log_file in logs_path.glob('**/*.log'):
            if log_file.is_file():
                size = log_file.stat().st_size
                total_size += size
                file_count += 1
                
                if size > largest_size:
                    largest_size = size
                    largest_file = {
                        'name': log_file.name,
                        'size_mb': round(size / 1024 / 1024, 2),
                        'path': str(log_file.relative_to(logs_path))
                    }
        
        total_mb = round(total_size / 1024 / 1024, 2)
        
        return {
            'total_size_mb': total_mb,
            'file_count': file_count,
            'largest_file': largest_file,
            'status': 'healthy' if total_mb < 100 else 'warning' if total_mb < 500 else 'critical'
        }
    
    def get_archive_health(self) -> Dict:
        """
        Get archive folder health metrics.
        
        Returns:
            Dict with archive stats from .archive/ folders
        """
        project_root = Path(__file__).parent.parent.parent
        
        total_size = 0
        archive_count = 0
        file_count = 0
        
        # Scan for .archive folders
        for archive_dir in project_root.glob('**/.archive'):
            if archive_dir.is_dir():
                archive_count += 1
                
                for file in archive_dir.glob('**/*'):
                    if file.is_file():
                        total_size += file.stat().st_size
                        file_count += 1
        
        total_mb = round(total_size / 1024 / 1024, 2)
        
        return {
            'archive_count': archive_count,
            'total_size_mb': total_mb,
            'file_count': file_count,
            'status': 'healthy' if total_mb < 50 else 'warning' if total_mb < 200 else 'critical'
        }
    
    def get_system_health(self) -> Dict:
        """
        Get comprehensive system health report.
        
        Returns:
            Dict with all health metrics
        """
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        logs = self.get_log_file_sizes()
        archive = self.get_archive_health()
        
        # Overall health status
        statuses = [memory['status'], disk['status'], logs['status'], archive['status']]
        if 'critical' in statuses:
            overall = 'critical'
        elif 'warning' in statuses:
            overall = 'warning'
        else:
            overall = 'healthy'
        
        return {
            'overall': overall,
            'memory': memory,
            'disk': disk,
            'logs': logs,
            'archive': archive,
            'timestamp': datetime.now().isoformat()
        }


# Global instance
_server_monitor_instance: Optional[ServerMonitor] = None


def get_server_monitor() -> ServerMonitor:
    """Get global ServerMonitor instance"""
    global _server_monitor_instance
    if _server_monitor_instance is None:
        _server_monitor_instance = ServerMonitor()

    return _server_monitor_instance
