"""FIND command handler - Search for locations by name or type."""

from typing import List, Dict, Optional
from core.commands.base import BaseCommandHandler
from core.commands.handler_logging_mixin import HandlerLoggingMixin
from core.locations import load_locations
from core.services.error_contract import CommandError


class FindHandler(BaseCommandHandler, HandlerLoggingMixin):
    """Handler for FIND command - search locations with logging."""

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
        with self.trace_command(command, params) as trace:
            if not params:
                trace.set_status('error')
                self.log_param_error(command, params, "Search query required")
                raise CommandError(
                    code="ERR_COMMAND_INVALID_ARG",
                    message="FIND requires a search query (name, type, or region)",
                    recovery_hint="Usage: FIND <query> [--type <type>] [--region <region>]",
                    level="INFO",
                )

            try:
                db = load_locations()
                all_locations = list(db.get_all())
                trace.add_event('locations_loaded', {'count': len(all_locations)})
            except Exception as e:
                trace.record_error(e)
                trace.set_status('error')
                self.log_operation(command, 'load_failed', {'error': str(e)})
                raise CommandError(
                    code="ERR_LOCATION_LOAD_FAILED",
                    message=f"Failed to load locations: {str(e)}",
                    recovery_hint="Run VERIFY to check location data integrity",
                    level="WARNING",
                )

            trace.mark_milestone('data_loaded')

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

            trace.add_event('search_parsed', {
                'query_text': query_text[:50],
                'search_type': search_type,
                'search_region': search_region
            })

            trace.mark_milestone('filters_parsed')

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

            trace.add_event('search_completed', {'results_found': len(results)})
            trace.mark_milestone('results_found')

            if not results:
                from core.tui.output import OutputToolkit
                output = "\n".join(
                    [
                        OutputToolkit.banner("FIND RESULTS"),
                        f"No locations found for: {search_query}",
                    ]
                )
                trace.set_status('success')
                self.log_operation(command, 'no_results', {
                    'query': search_query[:50],
                    'search_scope': len(all_locations)
                })
                return {
                    "status": "success",
                    "message": f"No locations found for: {search_query}",
                    "output": output,
                    "query": search_query,
                    "results": [],
                }

            from core.tui.output import OutputToolkit
            rows = [
                [item["id"], item["name"], item["type"], item["region"]]
                for item in results[:20]
            ]
            output = "\n".join(
                [
                    OutputToolkit.banner("FIND RESULTS"),
                    OutputToolkit.table(["id", "name", "type", "region"], rows),
                    "",
                    f"Count: {len(results)}",
                ]
            )

            trace.set_status('success')
            trace.add_event('results_formatted', {
                'total_found': len(results),
                'displayed': min(len(results), 20),
                'output_size': len(output)
            })

            return {
                "status": "success",
                "message": f"Found {len(results)} locations",
                "output": output,
                "count": len(results),
                "query": search_query,
                "results": results[:20],  # Limit to 20 results
            }
