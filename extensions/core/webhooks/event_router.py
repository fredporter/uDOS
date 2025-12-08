"""
Event Router & Handler Registry for uDOS Webhook System

Routes normalized events to:
1. Registered Python handlers
2. uCODE scripts (.upy)
3. System commands
4. Extension endpoints

Features:
- Pattern-based routing (event_type, platform, source filters)
- Priority-based handler execution
- Async event processing
- Error handling and retry logic
- Event history and logging
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional, Pattern
from collections import defaultdict

logger = logging.getLogger(__name__)


class EventRoute:
    """Represents a single event route configuration."""

    def __init__(
        self,
        name: str,
        pattern: Dict[str, Any],
        handler: Callable,
        priority: int = 50,
        enabled: bool = True
    ):
        """
        Initialize event route.

        Args:
            name: Route identifier
            pattern: Event matching pattern (event_type, platform, source)
            handler: Callable handler function
            priority: Execution priority (0-100, higher = earlier)
            enabled: Whether route is active
        """
        self.name = name
        self.pattern = pattern
        self.handler = handler
        self.priority = priority
        self.enabled = enabled
        self.stats = {'matched': 0, 'executed': 0, 'errors': 0}

    def matches(self, event: Dict[str, Any]) -> bool:
        """
        Check if event matches this route's pattern.

        Args:
            event: Normalized event dictionary

        Returns:
            True if event matches pattern
        """
        if not self.enabled:
            return False

        # Match event_type (regex supported)
        if 'event_type' in self.pattern:
            pattern = self.pattern['event_type']
            if isinstance(pattern, str):
                if not re.match(pattern, event.get('event_type', '')):
                    return False
            elif isinstance(pattern, list):
                if event.get('event_type') not in pattern:
                    return False

        # Match platform
        if 'platform' in self.pattern:
            if event.get('platform') != self.pattern['platform']:
                return False

        # Match source filters
        if 'source' in self.pattern:
            source = event.get('source', {})
            for key, value in self.pattern['source'].items():
                if source.get(key) != value:
                    return False

        self.stats['matched'] += 1
        return True

    async def execute(self, event: Dict[str, Any]) -> Any:
        """
        Execute handler for matched event.

        Args:
            event: Normalized event dictionary

        Returns:
            Handler result
        """
        try:
            result = await self.handler(event)
            self.stats['executed'] += 1
            return result
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Route {self.name} handler error: {e}")
            raise


class EventRouter:
    """Route webhook events to handlers and scripts."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize event router.

        Args:
            config_path: Path to routing configuration file
        """
        self.routes: List[EventRoute] = []
        self.script_handlers: Dict[str, Path] = {}
        self.event_history: List[Dict[str, Any]] = []
        self.config = self._load_config(config_path)

        # Statistics
        self.stats = {
            'routed': 0,
            'no_match': 0,
            'errors': 0
        }

    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load routing configuration."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return json.load(f)

        return {
            'max_history': 1000,
            'retry_failed': True,
            'max_retries': 3,
            'script_timeout': 30
        }

    def register_route(
        self,
        name: str,
        pattern: Dict[str, Any],
        handler: Callable,
        priority: int = 50
    ) -> EventRoute:
        """
        Register a new event route.

        Args:
            name: Route identifier
            pattern: Event matching pattern
            handler: Handler function (can be async)
            priority: Execution priority (0-100)

        Returns:
            Created EventRoute instance
        """
        # Wrap sync handlers in async
        if not asyncio.iscoroutinefunction(handler):
            async def async_wrapper(event):
                return handler(event)
            handler = async_wrapper

        route = EventRoute(name, pattern, handler, priority)
        self.routes.append(route)

        # Sort by priority (highest first)
        self.routes.sort(key=lambda r: r.priority, reverse=True)

        logger.info(f"Registered route: {name} (priority {priority})")
        return route

    def register_script(self, event_type: str, script_path: Path, priority: int = 50):
        """
        Register a uCODE script handler.

        Args:
            event_type: Event type pattern (regex supported)
            script_path: Path to .upy script
            priority: Execution priority
        """
        async def script_handler(event: Dict[str, Any]):
            """Execute uCODE script with event data."""
            from core.interpreters.ucode_interpreter import UCodeInterpreter

            interpreter = UCodeInterpreter()

            # Pass event data as variables
            interpreter.set_variable('EVENT', event)
            interpreter.set_variable('EVENT_TYPE', event['event_type'])
            interpreter.set_variable('PLATFORM', event['platform'])
            interpreter.set_variable('PAYLOAD', event['payload'])

            # Execute script
            result = await asyncio.wait_for(
                asyncio.to_thread(interpreter.execute_file, script_path),
                timeout=self.config.get('script_timeout', 30)
            )

            return result

        self.register_route(
            name=f"script:{script_path.name}",
            pattern={'event_type': event_type},
            handler=script_handler,
            priority=priority
        )

        self.script_handlers[event_type] = script_path
        logger.info(f"Registered script handler: {script_path}")

    async def route(self, event: Dict[str, Any]) -> List[Any]:
        """
        Route event to matching handlers.

        Args:
            event: Normalized event dictionary

        Returns:
            List of handler results
        """
        # Find matching routes
        matching_routes = [r for r in self.routes if r.matches(event)]

        if not matching_routes:
            self.stats['no_match'] += 1
            logger.warning(f"No routes matched event: {event['event_type']}")
            return []

        # Execute handlers (already sorted by priority)
        results = []
        for route in matching_routes:
            try:
                result = await route.execute(event)
                results.append({
                    'route': route.name,
                    'result': result,
                    'success': True
                })
            except Exception as e:
                self.stats['errors'] += 1
                results.append({
                    'route': route.name,
                    'error': str(e),
                    'success': False
                })

                # Continue executing other routes
                if self.config.get('stop_on_error', False):
                    break

        # Update statistics
        self.stats['routed'] += 1

        # Add to history
        self._add_to_history(event, results)

        return results

    def _add_to_history(self, event: Dict[str, Any], results: List[Any]):
        """Add event to history with results."""
        history_entry = {
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'event_id': event['event_id'],
            'event_type': event['event_type'],
            'platform': event['platform'],
            'routes_matched': len(results),
            'routes_succeeded': sum(1 for r in results if r['success']),
            'results': results
        }

        self.event_history.append(history_entry)

        # Trim history if needed
        max_history = self.config.get('max_history', 1000)
        if len(self.event_history) > max_history:
            self.event_history = self.event_history[-max_history:]

    def get_route(self, name: str) -> Optional[EventRoute]:
        """Get route by name."""
        for route in self.routes:
            if route.name == name:
                return route
        return None

    def remove_route(self, name: str) -> bool:
        """Remove route by name."""
        route = self.get_route(name)
        if route:
            self.routes.remove(route)
            logger.info(f"Removed route: {name}")
            return True
        return False

    def enable_route(self, name: str):
        """Enable a route."""
        route = self.get_route(name)
        if route:
            route.enabled = True
            logger.info(f"Enabled route: {name}")

    def disable_route(self, name: str):
        """Disable a route."""
        route = self.get_route(name)
        if route:
            route.enabled = False
            logger.info(f"Disabled route: {name}")

    def get_history(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict]:
        """
        Get event history.

        Args:
            limit: Maximum number of entries
            event_type: Filter by event type

        Returns:
            List of history entries
        """
        history = self.event_history

        if event_type:
            history = [h for h in history if h['event_type'] == event_type]

        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        route_stats = {r.name: r.stats for r in self.routes}

        return {
            'global': self.stats,
            'routes': route_stats,
            'total_routes': len(self.routes),
            'enabled_routes': sum(1 for r in self.routes if r.enabled)
        }

    def reset_stats(self):
        """Reset all statistics."""
        self.stats = {'routed': 0, 'no_match': 0, 'errors': 0}
        for route in self.routes:
            route.stats = {'matched': 0, 'executed': 0, 'errors': 0}
