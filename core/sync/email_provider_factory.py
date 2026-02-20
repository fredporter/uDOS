"""Email provider factory (Phase 8.3)."""

from typing import Optional
from core.sync.base_providers import BaseEmailProvider
from core.sync.gmail_provider import GmailProvider
from core.sync.outlook_email_provider import OutlookEmailProvider
from core.sync.imap_provider import IMAPProvider
from core.services.logging_manager import get_logger

logger = get_logger(__name__)


class EmailProviderFactory:
    """Factory for creating email provider instances."""

    PROVIDERS = {
        "gmail": GmailProvider,
        "outlook_email": OutlookEmailProvider,
        "imap": IMAPProvider,
    }

    @staticmethod
    def create_provider(provider_type: str) -> Optional[BaseEmailProvider]:
        """Create an email provider instance.

        Args:
            provider_type: Type of provider (gmail, outlook_email, imap)

        Returns:
            Email provider instance or None if unknown type
        """
        if provider_type not in EmailProviderFactory.PROVIDERS:
            logger.error(f"Unknown email provider type: {provider_type}")
            return None

        provider_class = EmailProviderFactory.PROVIDERS[provider_type]
        logger.info(f"Creating {provider_type} email provider")
        return provider_class()

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available email provider types.

        Returns:
            List of provider type strings
        """
        return list(EmailProviderFactory.PROVIDERS.keys())
