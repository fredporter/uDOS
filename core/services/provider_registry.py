"""
Core Provider Registry — v1.4.4

This module enables Wizard features to be accessed from Core without direct imports.
Core remains offline-first and stdlib-only; Wizard (optional) registers providers at startup.

Pattern:
  1. Core defines provider interface (abstract)
  2. Wizard registers concrete implementations at startup
  3. Core checks availability and calls providers
  4. If Wizard not available, features gracefully degrade

This breaks the circular dependency: Core no longer imports Wizard.
Instead, Wizard imports Core, runs after Core starts, and registers providers.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class ProviderNotAvailableError(Exception):
    """Raised when a provider is requested but not registered."""
    pass


class ProviderType(Enum):
    """Categories of optional providers"""
    PORT_MANAGER = "port_manager"
    LIBRARY_MANAGER = "library_manager"
    PLUGIN_REPOSITORY = "plugin_repository"
    MONITORING_MANAGER = "monitoring_manager"
    VIBE_SERVICE = "vibe_service"
    SETUP_PROFILES = "setup_profiles"
    SECRET_STORE = "secret_store"
    RATE_LIMITER = "rate_limiter"
    PROVIDER_LOAD_LOGGER = "provider_load_logger"


@dataclass
class ProviderInfo:
    """Metadata about a registered provider"""
    provider_type: ProviderType
    name: str
    description: str
    version: str
    available: bool = True


class CoreProviderRegistry:
    """
    Central registry for optional Core providers.

    Wizard registers implementations here at startup.
    Core queries this registry to conditionally use Wizard features.
    """

    _instance = None
    _registry: Dict[ProviderType, Any] = {}
    _metadata: Dict[ProviderType, ProviderInfo] = {}

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'CoreProviderRegistry':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def register(
        cls,
        provider_type: ProviderType,
        provider: Any,
        name: str = None,
        description: str = None,
        version: str = "1.0.0"
    ) -> None:
        """
        Register a provider implementation.

        Args:
            provider_type: Type of provider (from ProviderType enum)
            provider: The provider instance/callable
            name: Optional name (defaults to provider_type.value)
            description: Optional description
            version: Provider version

        Example:
            registry = CoreProviderRegistry.get_instance()
            registry.register(
                ProviderType.PORT_MANAGER,
                provider,
                name="Port Manager",
                description="Detects port conflicts and occupants",
                version="1.4.4"
            )
        """
        inst = cls.get_instance()
        inst._registry[provider_type] = provider
        inst._metadata[provider_type] = ProviderInfo(
            provider_type=provider_type,
            name=name or provider_type.value,
            description=description or f"Provider for {provider_type.value}",
            version=version,
            available=True
        )
        logger.debug("Provider registered: %s", provider_type.value)

    @classmethod
    def get(cls, provider_type: ProviderType) -> Any:
        """
        Get a registered provider.

        Args:
            provider_type: Type of provider to retrieve

        Returns:
            The provider instance/callable

        Raises:
            ProviderNotAvailableError: If provider not registered

        Example:
            registry = CoreProviderRegistry.get_instance()
            if registry.is_available(ProviderType.PORT_MANAGER):
                pm = registry.get(ProviderType.PORT_MANAGER)
                occupant = pm.get_port_occupant(8000)
        """
        inst = cls.get_instance()
        if provider_type not in inst._registry:
            raise ProviderNotAvailableError(
                f"Provider not available: {provider_type.value}. "
                f"Ensure Wizard is installed and running."
            )
        return inst._registry[provider_type]

    @classmethod
    def is_available(cls, provider_type: ProviderType) -> bool:
        """
        Check if a provider is registered and available.

        Args:
            provider_type: Type of provider to check

        Returns:
            True if provider is available, False otherwise

        Example:
            if registry.is_available(ProviderType.PORT_MANAGER):
                pm = registry.get(ProviderType.PORT_MANAGER)
        """
        inst = cls.get_instance()
        if provider_type not in inst._registry:
            return False
        info = inst._metadata.get(provider_type)
        return info is not None and info.available if info else False

    @classmethod
    def get_info(cls, provider_type: ProviderType) -> Optional[ProviderInfo]:
        """
        Get metadata about a provider.

        Args:
            provider_type: Type of provider

        Returns:
            ProviderInfo object or None if not registered
        """
        inst = cls.get_instance()
        return inst._metadata.get(provider_type)

    @classmethod
    def list_available(cls) -> Dict[str, ProviderInfo]:
        """
        List all available providers.

        Returns:
            Dict mapping provider type names to ProviderInfo objects
        """
        inst = cls.get_instance()
        return {
            ptype.value: info
            for ptype, info in inst._metadata.items()
            if info.available
        }

    @classmethod
    def unregister(cls, provider_type: ProviderType) -> None:
        """
        Unregister a provider (useful for testing).

        Args:
            provider_type: Type of provider to remove
        """
        inst = cls.get_instance()
        if provider_type in inst._registry:
            del inst._registry[provider_type]
        if provider_type in inst._metadata:
            del inst._metadata[provider_type]
        logger.debug("Provider unregistered: %s", provider_type.value)

    @classmethod
    def clear(cls) -> None:
        """Clear all registered providers (useful for testing)."""
        inst = cls.get_instance()
        inst._registry.clear()
        inst._metadata.clear()
        logger.debug("Provider registry cleared")

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """
        Get status of all registered providers.

        Returns:
            Dict with registered and available provider counts
        """
        inst = cls.get_instance()
        return {
            "total_registered": len(inst._registry),
            "total_available": sum(
                1 for info in inst._metadata.values() if info.available
            ),
            "providers": {
                ptype.value: {
                    "registered": ptype in inst._registry,
                    "available": inst._metadata.get(ptype, ProviderInfo(
                        ptype, ptype.value, "", "")).available,
                    "info": inst.get_info(ptype)
                }
                for ptype in ProviderType
            }
        }


# Convenience functions
def get_provider_registry() -> CoreProviderRegistry:
    """Get the global provider registry instance."""
    return CoreProviderRegistry.get_instance()


def register_provider(
    provider_type: ProviderType,
    provider: Any,
    name: str = None,
    description: str = None,
    version: str = "1.0.0"
) -> None:
    """
    Register a provider (convenience function).

    Example:
        from core.services.provider_registry import register_provider, ProviderType

        register_provider(
            ProviderType.PORT_MANAGER,
            provider,
            name="Port Manager",
            version="1.4.4"
        )
    """
    CoreProviderRegistry.register(provider_type, provider, name, description, version)


def get_provider(provider_type: ProviderType) -> Any:
    """
    Get a provider (convenience function).

    Raises ProviderNotAvailableError if not registered.

    Example:
        from core.services.provider_registry import get_provider, ProviderType

        try:
            pm = get_provider(ProviderType.PORT_MANAGER)
            occupant = pm.get_port_occupant(8000)
        except ProviderNotAvailableError:
            print("Wizard port manager not available")
    """
    return CoreProviderRegistry.get(provider_type)


def is_provider_available(provider_type: ProviderType) -> bool:
    """
    Check if a provider is available (convenience function).

    Example:
        from core.services.provider_registry import is_provider_available, ProviderType

        if is_provider_available(ProviderType.PORT_MANAGER):
            pm = get_provider(ProviderType.PORT_MANAGER)
    """
    return CoreProviderRegistry.is_available(provider_type)
