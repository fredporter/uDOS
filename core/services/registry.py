"""
Service Registry for uDOS Core

Provides unified access to core services without direct imports.
Replaces verbose package imports with simple registry lookups.

BEFORE (verbose):
    from core.services.logging_service import get_logger
    from core.services.grid_config import load_grid_config
    from core.services.user_service import get_user_manager

AFTER (registry):
    from core.services.registry import get_service

    logger = get_service('logging').get_logger('category')
    grid_config = get_service('grid').load_config()
    user_mgr = get_service('user').get_manager()

Benefit: Lazy loading, better circular dependency handling, easier testing.
"""

from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Lazy-loaded services
_services: Dict[str, Any] = {}
_service_loaders = {
    # Core infrastructure services
    'logging': lambda: __import__('core.services.logging_service', fromlist=['get_logging_manager']).get_logging_manager(),
    'grid': lambda: __import__('core.services.grid_config', fromlist=['load_grid_config']),
    'dataset': lambda: __import__('core.services.dataset_service', fromlist=['DatasetManager']).DatasetManager(),
    'user': lambda: __import__('core.services.user_service', fromlist=['get_user_manager']).get_user_manager(),
    'history': lambda: __import__('core.services.history_service', fromlist=['get_history_manager']).get_history_manager(),

    # Containerized modules
    'groovebox': lambda: _load_groovebox_module(),
    'empire': lambda: _load_empire_module(),
    'sonic': lambda: _load_sonic_module(),
    'distribution': lambda: _load_distribution_module(),
    'extensions': lambda: _load_extensions_module(),
}


def _load_groovebox_module():
    """Load groovebox container module."""
    try:
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        # Try direct import first (if in-repo)
        from groovebox.engine import sequencer, mml_parser, midi_export
        from groovebox.instruments import drum_808
        return type('GrooveboxEngine', (), {
            'sequencer': sequencer,
            'mml_parser': mml_parser,
            'midi_export': midi_export,
            'instruments': type('Instruments', (), {'drum_808': drum_808})(),
            'Sequencer': sequencer.Sequencer,
            'MMLParser': mml_parser.MMLParser,
            'MidiExporter': midi_export.MidiExporter,
        })()
    except ImportError as exc:
        # Try extensions path (if loaded from containers)
        try:
            from extensions.groovebox.engine import sequencer, mml_parser, midi_export
            from extensions.groovebox.instruments import drum_808
            return type('GrooveboxEngine', (), {
                'sequencer': sequencer,
                'mml_parser': mml_parser,
                'midi_export': midi_export,
                'instruments': type('Instruments', (), {'drum_808': drum_808})(),
                'Sequencer': sequencer.Sequencer,
                'MMLParser': mml_parser.MMLParser,
                'MidiExporter': midi_export.MidiExporter,
            })()
        except ImportError as exc2:
            raise RuntimeError(
                f"Groovebox module not found (direct import failed: {exc})"
            ) from exc2


def _load_empire_module():
    """Load empire container module."""
    try:
        # Try direct import first (if in-repo)
        from empire import entity_resolver, contact_extractor
        from empire.enrichment_client import EnrichmentClient
        return type('EmpireAPI', (), {
            'entity_resolver': entity_resolver,
            'contact_extractor': contact_extractor,
            'EnrichmentClient': EnrichmentClient,
            'EntityResolver': entity_resolver.EntityResolver if hasattr(entity_resolver, 'EntityResolver') else None,
        })()
    except ImportError:
        # Try extensions path (if loaded from containers)
        try:
            from extensions.empire import entity_resolver, contact_extractor
            from extensions.empire.enrichment_client import EnrichmentClient
            return type('EmpireAPI', (), {
                'entity_resolver': entity_resolver,
                'contact_extractor': contact_extractor,
                'EnrichmentClient': EnrichmentClient,
                'EntityResolver': entity_resolver.EntityResolver if hasattr(entity_resolver, 'EntityResolver') else None,
            })()
        except ImportError:
            raise RuntimeError("Empire module not found in groovebox or extensions paths")


def get_service(service_name: str) -> Any:
    """Get a service by name (lazy-loaded).

    Args:
        service_name: Service identifier (logging, grid, dataset, user, history)

    Returns:
        Service instance or module

    Raises:
        KeyError: If service not found

    Example:
        logger_mgr = get_service('logging')
        logger = logger_mgr.get_logger('my-category')
    """
    if service_name not in _services:
        if service_name not in _service_loaders:
            raise KeyError(f"Unknown service: {service_name}. Available: {list(_service_loaders.keys())}")

        try:
            _services[service_name] = _service_loaders[service_name]()
        except Exception as e:
            raise RuntimeError(f"Failed to load service '{service_name}': {e}")

    return _services[service_name]


def register_service(name: str, loader) -> None:
    """Register a new service loader.

    Args:
        name: Service identifier
        loader: Callable that returns service instance

    Example:
        register_service('myservice', lambda: MyService())
    """
    _service_loaders[name] = loader
    # Clear cache if already loaded
    if name in _services:
        del _services[name]


def list_services() -> list:
    """List all available services."""
    return list(_service_loaders.keys())


# Convenience imports for common pattern
def get_logger(category: str, source: Optional[str] = None):
    """Shortcut to logging service."""
    return get_service('logging').get_logger(category, source=source)


def _load_sonic_module():
    """Load sonic container module."""
    try:
        # Try direct import first (if in-repo)
        from sonic.core import sonic_cli, manifest, plan
        return type('SonicScrewdriver', (), {
            'sonic_cli': sonic_cli,
            'manifest': manifest,
            'plan': plan,
            'SonicCLI': sonic_cli.SonicCLI if hasattr(sonic_cli, 'SonicCLI') else None,
            'Manifest': manifest.Manifest if hasattr(manifest, 'Manifest') else None,
            'PlanManager': plan.PlanManager if hasattr(plan, 'PlanManager') else None,
        })()
    except ImportError:
        raise RuntimeError("Sonic module not found in sonic/core path")


def _load_distribution_module():
    """Load distribution container module."""
    try:
        # Try direct import first (if in-repo)
        from distribution import packages, schemas
        return type('DistributionBuilder', (), {
            'packages': packages,
            'schemas': schemas,
            'PackageManager': packages.PackageManager if hasattr(packages, 'PackageManager') else None,
            'validate_schema': schemas.validate_schema if hasattr(schemas, 'validate_schema') else None,
        })()
    except ImportError:
        raise RuntimeError("Distribution module not found in distribution path")


def _load_extensions_module():
    """Load extensions container module."""
    try:
        # Try direct import first (if in-repo)
        from extensions import server_manager
        from extensions.api import server as api_server
        from extensions.transport import meshcore
        return type('ExtensionManager', (), {
            'server_manager': server_manager,
            'api_server': api_server,
            'meshcore': meshcore,
            'ServerManager': server_manager.ServerManager if hasattr(server_manager, 'ServerManager') else None,
            'APIServer': api_server.APIServer if hasattr(api_server, 'APIServer') else None,
        })()
    except ImportError:
        raise RuntimeError("Extensions module not found in extensions path")
