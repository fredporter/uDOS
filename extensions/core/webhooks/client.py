"""
Python Client Library for uDOS Webhook API

Provides typed, easy-to-use interface for interacting with webhook API:
- Event querying and filtering
- Route management
- Statistics retrieval
- Health checks

Supports both sync and async operations.

Example:
    from extensions.core.webhooks.client import WebhookClient

    # Synchronous usage
    client = WebhookClient('http://localhost:5050')
    events = client.get_events(limit=10, platform='github')

    # Asynchronous usage
    async with WebhookClient('http://localhost:5050') as client:
        events = await client.get_events_async(limit=10)
"""

import asyncio
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

import requests
import aiohttp


@dataclass
class Event:
    """Webhook event."""
    event_id: str
    platform: str
    event_type: str
    timestamp: str
    source: Dict[str, Any]
    payload: Dict[str, Any]
    raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create Event from dictionary."""
        return cls(
            event_id=data['event_id'],
            platform=data['platform'],
            event_type=data['event_type'],
            timestamp=data['timestamp'],
            source=data['source'],
            payload=data['payload'],
            raw=data.get('raw')
        )


@dataclass
class Route:
    """Event route."""
    name: str
    pattern: Dict[str, Any]
    priority: int
    enabled: bool
    stats: Dict[str, int]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Route':
        """Create Route from dictionary."""
        return cls(
            name=data['name'],
            pattern=data['pattern'],
            priority=data['priority'],
            enabled=data['enabled'],
            stats=data['stats']
        )


@dataclass
class Stats:
    """System statistics."""
    api: Dict[str, int]
    processor: Dict[str, Any]
    router: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stats':
        """Create Stats from dictionary."""
        return cls(
            api=data['api'],
            processor=data['processor'],
            router=data['router']
        )


class WebhookClient:
    """Client for uDOS Webhook API."""

    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize webhook client.

        Args:
            base_url: Base URL of webhook API (e.g., http://localhost:5050)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    # Synchronous methods

    def get_events(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get event history.

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            platform: Filter by platform

        Returns:
            List of event dictionaries
        """
        params = {'limit': limit}
        if event_type:
            params['event_type'] = event_type
        if platform:
            params['platform'] = platform

        response = requests.get(
            f'{self.base_url}/api/events',
            params=params,
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['events']

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get specific event by ID.

        Args:
            event_id: Event ID

        Returns:
            Event dictionary
        """
        response = requests.get(
            f'{self.base_url}/api/events/{event_id}',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_routes(self) -> List[Route]:
        """
        Get all registered routes.

        Returns:
            List of Route objects
        """
        response = requests.get(
            f'{self.base_url}/api/routes',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        routes_data = response.json()['routes']
        return [Route.from_dict(r) for r in routes_data]

    def get_route(self, name: str) -> Route:
        """
        Get specific route by name.

        Args:
            name: Route name

        Returns:
            Route object
        """
        response = requests.get(
            f'{self.base_url}/api/routes/{name}',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return Route.from_dict(response.json())

    def enable_route(self, name: str) -> bool:
        """
        Enable a route.

        Args:
            name: Route name

        Returns:
            True if successful
        """
        response = requests.post(
            f'{self.base_url}/api/routes/{name}/enable',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['success']

    def disable_route(self, name: str) -> bool:
        """
        Disable a route.

        Args:
            name: Route name

        Returns:
            True if successful
        """
        response = requests.post(
            f'{self.base_url}/api/routes/{name}/disable',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['success']

    def delete_route(self, name: str) -> bool:
        """
        Delete a route.

        Args:
            name: Route name

        Returns:
            True if successful
        """
        response = requests.delete(
            f'{self.base_url}/api/routes/{name}',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['success']

    def get_stats(self) -> Stats:
        """
        Get system statistics.

        Returns:
            Stats object
        """
        response = requests.get(
            f'{self.base_url}/api/stats',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return Stats.from_dict(response.json())

    def reset_stats(self) -> bool:
        """
        Reset all statistics.

        Returns:
            True if successful
        """
        response = requests.post(
            f'{self.base_url}/api/stats/reset',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()['success']

    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health status dictionary
        """
        response = requests.get(
            f'{self.base_url}/api/health',
            headers=self._get_headers(),
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    # Asynchronous methods

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self._get_headers())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def get_events_async(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        platform: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get event history (async).

        Args:
            limit: Maximum number of events to return
            event_type: Filter by event type
            platform: Filter by platform

        Returns:
            List of event dictionaries
        """
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        params = {'limit': limit}
        if event_type:
            params['event_type'] = event_type
        if platform:
            params['platform'] = platform

        async with self.session.get(
            f'{self.base_url}/api/events',
            params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['events']

    async def get_event_async(self, event_id: str) -> Dict[str, Any]:
        """Get specific event by ID (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.get(
            f'{self.base_url}/api/events/{event_id}'
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_routes_async(self) -> List[Route]:
        """Get all registered routes (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.get(
            f'{self.base_url}/api/routes'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return [Route.from_dict(r) for r in data['routes']]

    async def get_route_async(self, name: str) -> Route:
        """Get specific route by name (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.get(
            f'{self.base_url}/api/routes/{name}'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return Route.from_dict(data)

    async def enable_route_async(self, name: str) -> bool:
        """Enable a route (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.post(
            f'{self.base_url}/api/routes/{name}/enable'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['success']

    async def disable_route_async(self, name: str) -> bool:
        """Disable a route (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.post(
            f'{self.base_url}/api/routes/{name}/disable'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['success']

    async def delete_route_async(self, name: str) -> bool:
        """Delete a route (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.delete(
            f'{self.base_url}/api/routes/{name}'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['success']

    async def get_stats_async(self) -> Stats:
        """Get system statistics (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.get(
            f'{self.base_url}/api/stats'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return Stats.from_dict(data)

    async def reset_stats_async(self) -> bool:
        """Reset all statistics (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.post(
            f'{self.base_url}/api/stats/reset'
        ) as response:
            response.raise_for_status()
            data = await response.json()
            return data['success']

    async def health_check_async(self) -> Dict[str, Any]:
        """Perform health check (async)."""
        if not self.session:
            raise RuntimeError("Use 'async with' context manager")

        async with self.session.get(
            f'{self.base_url}/api/health'
        ) as response:
            response.raise_for_status()
            return await response.json()
