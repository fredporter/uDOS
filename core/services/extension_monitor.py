"""
Extension Monitor Service (v1.2.17)

Tracks installed extensions and provides status information for TUI display.
Integrates with extension manager and provides enable/disable controls.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ExtensionMonitor:
    """
    Monitor all uDOS extensions with status tracking and management.
    
    Features:
    - Extension discovery in extensions/ directory
    - Active/inactive status tracking
    - Dependency checking
    - Enable/disable controls
    - Version tracking
    """
    
    EXTENSION_DIRS = ['assistant', 'play', 'web', 'cloud', 'api', 'cloned']
    CORE_EXTENSIONS = ['assistant', 'play', 'web']  # Core cannot be disabled
    
    def __init__(self, extensions_path: Optional[Path] = None):
        """Initialize extension monitor"""
        if extensions_path is None:
            extensions_path = Path(__file__).parent.parent.parent / 'extensions'
        
        self.extensions_path = extensions_path
        self._extensions_cache = {}
        self._last_scan = None
        
    def scan_extensions(self) -> List[Dict]:
        """
        Scan extensions directory for installed extensions.
        
        Returns:
            List of extension info dicts
        """
        extensions = []
        
        for ext_dir in self.EXTENSION_DIRS:
            ext_path = self.extensions_path / ext_dir
            if not ext_path.exists():
                continue
            
            # Check for extension.json
            manifest_path = ext_path / 'extension.json'
            if manifest_path.exists():
                try:
                    with open(manifest_path) as f:
                        manifest = json.load(f)
                    
                    ext_info = {
                        'id': ext_dir,
                        'name': manifest.get('name', ext_dir),
                        'version': manifest.get('version', 'unknown'),
                        'description': manifest.get('description', ''),
                        'author': manifest.get('author', 'unknown'),
                        'type': manifest.get('type', 'extension'),
                        'path': str(ext_path),
                        'has_manifest': True,
                        'is_core': ext_dir in self.CORE_EXTENSIONS
                    }
                except (json.JSONDecodeError, FileNotFoundError):
                    ext_info = self._create_default_info(ext_dir, ext_path)
            else:
                ext_info = self._create_default_info(ext_dir, ext_path)
            
            # Check for Python files (indicates active code)
            py_files = list(ext_path.glob('**/*.py'))
            ext_info['has_code'] = len(py_files) > 0
            ext_info['file_count'] = len(py_files)
            
            # Check for README
            ext_info['has_readme'] = (ext_path / 'README.md').exists()
            
            # Determine status
            ext_info['status'] = self._determine_status(ext_info)
            
            extensions.append(ext_info)
        
        # Check cloned directory for user extensions
        cloned_path = self.extensions_path / 'cloned'
        if cloned_path.exists():
            for user_ext in cloned_path.iterdir():
                if user_ext.is_dir() and not user_ext.name.startswith('.'):
                    ext_info = self._scan_cloned_extension(user_ext)
                    if ext_info:
                        extensions.append(ext_info)
        
        self._extensions_cache = {ext['id']: ext for ext in extensions}
        self._last_scan = datetime.now()
        
        return extensions
    
    def _create_default_info(self, ext_dir: str, ext_path: Path) -> Dict:
        """Create default extension info when no manifest exists"""
        return {
            'id': ext_dir,
            'name': ext_dir.replace('_', ' ').title(),
            'version': 'unknown',
            'description': f'{ext_dir} extension',
            'author': 'uDOS',
            'type': 'extension',
            'path': str(ext_path),
            'has_manifest': False,
            'is_core': ext_dir in self.CORE_EXTENSIONS
        }
    
    def _scan_cloned_extension(self, ext_path: Path) -> Optional[Dict]:
        """Scan a cloned/user extension"""
        manifest_path = ext_path / 'extension.json'
        
        if manifest_path.exists():
            try:
                with open(manifest_path) as f:
                    manifest = json.load(f)
                
                ext_info = {
                    'id': f"cloned_{ext_path.name}",
                    'name': manifest.get('name', ext_path.name),
                    'version': manifest.get('version', 'unknown'),
                    'description': manifest.get('description', ''),
                    'author': manifest.get('author', 'community'),
                    'type': 'cloned',
                    'path': str(ext_path),
                    'has_manifest': True,
                    'is_core': False
                }
                
                # Check for code
                py_files = list(ext_path.glob('**/*.py'))
                ext_info['has_code'] = len(py_files) > 0
                ext_info['file_count'] = len(py_files)
                ext_info['has_readme'] = (ext_path / 'README.md').exists()
                ext_info['status'] = self._determine_status(ext_info)
                
                return ext_info
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return None
    
    def _determine_status(self, ext_info: Dict) -> str:
        """
        Determine extension status.
        
        Returns:
            'active', 'inactive', 'incomplete', or 'error'
        """
        if not ext_info['has_code']:
            return 'incomplete'
        
        if not ext_info['has_manifest']:
            return 'inactive'
        
        # For now, assume all with manifest and code are active
        # TODO: Check if extension is actually loaded/running
        return 'active'
    
    def get_extension(self, ext_id: str) -> Optional[Dict]:
        """Get info for a specific extension"""
        if not self._extensions_cache or not self._last_scan:
            self.scan_extensions()
        
        return self._extensions_cache.get(ext_id)
    
    def get_all_extensions(self) -> List[Dict]:
        """Get all extensions (rescan if needed)"""
        if not self._last_scan:
            return self.scan_extensions()
        
        return list(self._extensions_cache.values())
    
    def get_active_extensions(self) -> List[Dict]:
        """Get list of active extensions"""
        all_exts = self.get_all_extensions()
        return [ext for ext in all_exts if ext['status'] == 'active']
    
    def get_inactive_extensions(self) -> List[Dict]:
        """Get list of inactive extensions"""
        all_exts = self.get_all_extensions()
        return [ext for ext in all_exts if ext['status'] == 'inactive']
    
    def get_extension_count(self) -> Dict[str, int]:
        """Get count of extensions by status"""
        all_exts = self.get_all_extensions()
        
        return {
            'total': len(all_exts),
            'active': len([e for e in all_exts if e['status'] == 'active']),
            'inactive': len([e for e in all_exts if e['status'] == 'inactive']),
            'incomplete': len([e for e in all_exts if e['status'] == 'incomplete']),
            'core': len([e for e in all_exts if e['is_core']]),
            'cloned': len([e for e in all_exts if e['type'] == 'cloned'])
        }
    
    def enable_extension(self, ext_id: str) -> Dict:
        """
        Enable an extension.
        
        Args:
            ext_id: Extension identifier
            
        Returns:
            Result dict with success status
        """
        ext = self.get_extension(ext_id)
        if not ext:
            return {'success': False, 'error': 'Extension not found'}
        
        if ext['is_core']:
            return {'success': False, 'error': 'Core extensions cannot be disabled'}
        
        # TODO: Implement actual extension enabling
        # For now, just return a placeholder
        return {
            'success': False,
            'error': 'Extension enabling not yet implemented',
            'extension': ext_id,
            'name': ext['name']
        }
    
    def disable_extension(self, ext_id: str) -> Dict:
        """
        Disable an extension.
        
        Args:
            ext_id: Extension identifier
            
        Returns:
            Result dict with success status
        """
        ext = self.get_extension(ext_id)
        if not ext:
            return {'success': False, 'error': 'Extension not found'}
        
        if ext['is_core']:
            return {'success': False, 'error': 'Core extensions cannot be disabled'}
        
        # TODO: Implement actual extension disabling
        return {
            'success': False,
            'error': 'Extension disabling not yet implemented',
            'extension': ext_id,
            'name': ext['name']
        }
    
    def get_summary(self) -> Dict:
        """
        Get comprehensive extension summary.
        
        Returns:
            Summary dict with counts and lists
        """
        counts = self.get_extension_count()
        active = self.get_active_extensions()
        inactive = self.get_inactive_extensions()
        
        return {
            'counts': counts,
            'active': [{'id': e['id'], 'name': e['name'], 'version': e['version']} for e in active],
            'inactive': [{'id': e['id'], 'name': e['name'], 'version': e['version']} for e in inactive],
            'timestamp': datetime.now().isoformat(),
            'last_scan': self._last_scan.isoformat() if self._last_scan else None
        }


# Global instance
_extension_monitor_instance: Optional[ExtensionMonitor] = None


def get_extension_monitor() -> ExtensionMonitor:
    """Get global ExtensionMonitor instance"""
    global _extension_monitor_instance
    if _extension_monitor_instance is None:
        _extension_monitor_instance = ExtensionMonitor()
    return _extension_monitor_instance
