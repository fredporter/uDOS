"""Calendar provider factory (Phase 8.2)."""

from typing import Dict, Optional
from core.sync.base_providers import BaseCalendarProvider
from core.sync.google_calendar_provider import GoogleCalendarProvider
from core.sync.outlook_calendar_provider import OutlookCalendarProvider
from core.sync.apple_calendar_provider import AppleCalendarProvider
from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class CalendarProviderFactory:
    """Factory for creating calendar provider instances."""

    PROVIDERS = {
        "google_calendar": GoogleCalendarProvider,
        "outlook_calendar": OutlookCalendarProvider,
        "apple_calendar": AppleCalendarProvider,
    }

    @staticmethod
    def create_provider(provider_type: str) -> Optional[BaseCalendarProvider]:
        """Create a calendar provider instance.

        Args:
            provider_type: Type of provider (google_calendar, outlook_calendar, apple_calendar)

        Returns:
            Calendar provider instance or None if unknown type
        """
        if provider_type not in CalendarProviderFactory.PROVIDERS:
            logger.error(f"Unknown calendar provider type: {provider_type}")
            return None

        provider_class = CalendarProviderFactory.PROVIDERS[provider_type]
        logger.info(f"Creating {provider_type} calendar provider")
        return provider_class()

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available calendar provider types.

        Returns:
            List of provider type strings
        """
        return list(CalendarProviderFactory.PROVIDERS.keys())
