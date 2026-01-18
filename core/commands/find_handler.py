"""FIND command handler - Search for locations by name or type."""

from typing import List, Dict, Optional
from core.commands.base import BaseCommandHandler
from core.locations import load_locations


class FindHandler(BaseCommandHandler):
    """Handler for FIND command - search locations by name, type, or region."""

    def handle(self, command: str, params: List[str], grid=None, parser=None) -> Dict:
        """
        Handle FIND command.

        Args:
            command: Command name (FIND)
            params: Search parameters [query_text] or [--type TYPE] or [--region REGION]
            grid: Optional grid context
            parser: Optional parser

        Returns:
            Dict with status, results, count
        """
        if not params:
            return {
                "status": "error",
                "message": "FIND requires a search query (name, type, or region)",
            }

        try:
            db = load_locations()
            all_locations = list(db.get_all())
        except Exception as e:
            return {"status": "error", "message": f"Failed to load locations: {str(e)}"}

        # Parse search parameters
        search_query = " ".join(params).lower()

        # Check for flags
        search_type = None
        search_region = None
        query_text = search_query

        if "--type" in search_query:
            parts = search_query.split("--type")
            query_text = parts[0].strip()
            search_type = parts[1].strip().split()[0] if len(parts) > 1 else None

        if "--region" in search_query:
            parts = search_query.split("--region")
            query_text = parts[0].strip()
            search_region = parts[1].strip().split()[0] if len(parts) > 1 else None

        # Perform search
        results = []
        for location in all_locations:
            match = False

            # Search by text
            if query_text and (
                query_text in location.name.lower()
                or query_text in location.description.lower()
                or query_text in location.type.lower()
                or query_text in location.region.lower()
            ):
                match = True

            # Filter by type
            if search_type and location.type.lower() != search_type.lower():
                match = False

            # Filter by region
            if search_region and location.region.lower() != search_region.lower():
                match = False

            # If no query_text but filters specified, include if matches filters
            if not query_text and (search_type or search_region):
                match = True
                if search_type and location.type.lower() != search_type.lower():
                    match = False
                if search_region and location.region.lower() != search_region.lower():
                    match = False

            if match:
                results.append(
                    {
                        "id": location.id,
                        "name": location.name,
                        "type": location.type,
                        "region": location.region,
                        "description_preview": (
                            location.description[:80] + "..."
                            if len(location.description) > 80
                            else location.description
                        ),
                    }
                )

        if not results:
            return {
                "status": "no_results",
                "message": f"No locations found matching: {search_query}",
                "query": search_query,
            }

        return {
            "status": "success",
            "count": len(results),
            "query": search_query,
            "results": results[:20],  # Limit to 20 results
        }
