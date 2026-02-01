"""
Empire - Business Intelligence & CRM Extension

Unified CRM system integrating:
- Contact management (local SQLite)
- HubSpot free CRM synchronization (bidirectional)
- Gmail contact extraction
- Google Business Profile integration
- Website parsing for staff directories
- Social media enrichment
- Email enrichment APIs
- Entity resolution

Data stored in: memory/bank/user/contacts.db
"""

import sys
from pathlib import Path

# Add parent repo root to path for modular imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import modular utilities from wizard services
try:
    from wizard.services.path_utils import get_repo_root
except ImportError:
    # Fallback if wizard services not available
    def get_repo_root():
        current = Path(__file__).resolve()
        for parent in [current.parent] + list(current.parents):
            if (parent / "uDOS.py").exists():
                return parent
        raise RuntimeError("Could not find uDOS repository root")


from .marketing_db import MarketingDB
from .entity_resolver import EntityResolver
from .contact_extractor import ContactExtractor
from .google_business_client import GoogleBusinessClient
from .hubspot_handler import HubSpotHandler

# Config - use modular repo root
try:
    REPO_ROOT = get_repo_root()
    EMPIRE_DATA_PATH = REPO_ROOT / "memory" / "bank" / "user"
    EMPIRE_DATA_PATH.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"Warning: Could not determine repo root: {e}")
    REPO_ROOT = Path(__file__).parent.parent.parent
    EMPIRE_DATA_PATH = REPO_ROOT / "memory" / "bank" / "user"
    EMPIRE_DATA_PATH.mkdir(parents=True, exist_ok=True)


class Empire:
    """Main Empire CRM interface."""

    def __init__(self, db_path: str = None):
        """Initialize Empire CRM.

        Args:
            db_path: Path to SQLite database (defaults to memory/bank/user/contacts.db)
        """
        if db_path is None:
            db_path = str(EMPIRE_DATA_PATH / "contacts.db")

        self.db = MarketingDB(db_path)
        self.resolver = EntityResolver(self.db)
        self.extractor = ContactExtractor(self.db)
        self.google = GoogleBusinessClient(self.db)
        self.hubspot = HubSpotHandler(self.db)

    async def sync_hubspot(self, direction: str = "both"):
        """Synchronize with HubSpot CRM.

        Args:
            direction: Sync direction - "import", "export", or "both" (default)

        Returns:
            Dict with sync statistics
        """
        if not self.hubspot.enabled:
            return {"error": "HubSpot API key not configured (HUBSPOT_API_KEY)"}

        if direction == "import":
            count = await self.hubspot.sync_from_hubspot()
            return {"imported": count}
        elif direction == "export":
            count = await self.hubspot.sync_to_hubspot()
            return {"exported": count}
        else:  # both
            return await self.hubspot.sync_bidirectional()

    def extract_from_gmail(self, max_results: int = 100):
        """Extract contacts from Gmail messages.

        Args:
            max_results: Maximum messages to process

        Returns:
            Number of contacts extracted
        """
        return self.extractor.extract_from_gmail(max_results)

    def search_google_business(self, query: str, location: str = None):
        """Search Google Business Profile.

        Args:
            query: Search query
            location: Optional location filter

        Returns:
            List of business results
        """
        return self.google.search(query, location)

    def get_stats(self):
        """Get CRM statistics.

        Returns:
            Dictionary of stats
        """
        return {
            "total_businesses": self.db.count_businesses(),
            "total_people": self.db.count_people(),
            "total_relationships": self.db.count_relationships(),
            "hubspot_enabled": self.hubspot.enabled,
        }
