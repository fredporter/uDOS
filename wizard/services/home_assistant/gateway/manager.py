"""Home Assistant REST/WebSocket Gateway Manager.

Handles device discovery, state synchronization, and connection management.
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import asyncio
import logging

from wizard.services.logging_manager import get_logger
from wizard.services.home_assistant.schemas.gateway import (
    GatewayConfigSchema,
    GatewayStatusSchema,
)
from wizard.services.home_assistant.schemas.device import DeviceSchema, DeviceStateSchema
from wizard.services.home_assistant.schemas.entity import EntitySchema, EntityStateSchema

logger = get_logger("ha-gateway-manager")


class GatewayManager:
    """Manages Home Assistant gateway operations and device state."""

    def __init__(self, config: GatewayConfigSchema):
        """Initialize gateway manager with configuration."""
        self.config = config
        self.status = GatewayStatusSchema(status="initializing")
        self.devices: Dict[str, DeviceSchema] = {}
        self.device_states: Dict[str, DeviceStateSchema] = {}
        self.entities: Dict[str, EntitySchema] = {}
        self.entity_states: Dict[str, EntityStateSchema] = {}
        self._event_handlers: Dict[str, List[Callable]] = {
            "device_discovered": [],
            "device_updated": [],
            "device_removed": [],
            "entity_updated": [],
            "state_changed": [],
            "connection_status_changed": [],
        }
        self._ha_client = None
        self._discovery_task = None
        self._heartbeat_task = None
        self.start_time = datetime.now()

    async def initialize(self) -> bool:
        """Initialize gateway and connect to Home Assistant."""
        try:
            logger.info(f"[WIZ] Initializing HA gateway: {self.config.name}")
            # Initialize Home Assistant client
            self._ha_client = await self._create_ha_client()
            if not self._ha_client:
                raise ConnectionError("Failed to create HA client")

            # Test connection
            await self._test_connection()
            self.status.connected = True
            self.status.status = "running"

            # Start background tasks
            if self.config.auto_discovery:
                self._discovery_task = asyncio.create_task(self._discovery_loop())
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())

            logger.info(f"[WIZ] HA gateway initialized: {self.config.gateway_id}")
            return True
        except Exception as e:
            logger.error(f"[WIZ] Failed to initialize gateway: {e}")
            self.status.status = "error"
            self.status.error_message = str(e)
            return False

    async def shutdown(self) -> None:
        """Shutdown gateway and cleanup resources."""
        logger.info(f"[WIZ] Shutting down HA gateway: {self.config.gateway_id}")
        if self._discovery_task:
            self._discovery_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ha_client:
            await self._ha_client.close()
        self.status.connected = False
        self.status.status = "stopped"

    async def discover_devices(self) -> List[DeviceSchema]:
        """Discover available devices from Home Assistant."""
        try:
            logger.info("[WIZ] Starting device discovery")
            devices = await self._ha_client.get_devices()

            for device_data in devices:
                device = DeviceSchema(
                    id=device_data.get("id"),
                    name=device_data.get("name", "Unknown"),
                    type=device_data.get("type", "custom"),
                    model=device_data.get("model", ""),
                    manufacturer=device_data.get("manufacturer", ""),
                    hw_version=device_data.get("hw_version"),
                    sw_version=device_data.get("sw_version"),
                    via_device_id=device_data.get("via_device_id"),
                    suggested_area=device_data.get("suggested_area"),
                    config_entries=device_data.get("config_entries", []),
                    connections=device_data.get("connections", {}),
                    identifiers=device_data.get("identifiers", []),
                )
                self.devices[device.id] = device
                self._emit_event("device_discovered", device)

            self.status.total_devices = len(self.devices)
            logger.info(f"[WIZ] Discovered {len(self.devices)} devices")
            return list(self.devices.values())
        except Exception as e:
            logger.error(f"[WIZ] Device discovery failed: {e}")
            return []

    async def get_device(self, device_id: str) -> Optional[DeviceSchema]:
        """Get device by ID."""
        return self.devices.get(device_id)

    async def get_devices(self) -> List[DeviceSchema]:
        """Get all discovered devices."""
        return list(self.devices.values())

    async def get_device_state(self, device_id: str) -> Optional[DeviceStateSchema]:
        """Get current state of a device."""
        return self.device_states.get(device_id)

    async def get_entity_state(self, entity_id: str) -> Optional[EntityStateSchema]:
        """Get current state of an entity."""
        return self.entity_states.get(entity_id)

    async def call_service(
        self, domain: str, service: str, entity_ids: List[str], data: Dict[str, Any]
    ) -> bool:
        """Call a Home Assistant service."""
        try:
            logger.info(f"[WIZ] Calling service: {domain}.{service}")
            result = await self._ha_client.call_service(
                domain, service, entity_ids=entity_ids, data=data
            )
            return result.get("success", False)
        except Exception as e:
            logger.error(f"[WIZ] Service call failed: {e}")
            return False

    def on_event(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        if event_type in self._event_handlers:
            self._event_handlers[event_type].append(handler)

    def get_status(self) -> GatewayStatusSchema:
        """Get current gateway status."""
        self.status.uptime_seconds = int(
            (datetime.now() - self.start_time).total_seconds()
        )
        self.status.active_connections = len(
            [s for s in self.device_states.values() if s.is_available]
        )
        self.status.available_devices = self.status.active_connections
        self.status.total_entities = len(self.entities)
        return self.status

    # ============================================================================
    # Private Methods
    # ============================================================================

    async def _create_ha_client(self):
        """Create Home Assistant API client."""
        # Placeholder: would import actual HA client
        # This would be: from aiohttp_client import HomeAssistantClient
        return MockHAClient(self.config)

    async def _test_connection(self) -> bool:
        """Test connection to Home Assistant."""
        try:
            result = await self._ha_client.get_config()
            logger.info(f"[WIZ] Connected to HA: {result.get('location_name')}")
            return True
        except Exception as e:
            logger.error(f"[WIZ] Connection test failed: {e}")
            raise

    async def _discovery_loop(self) -> None:
        """Background task: periodic device discovery."""
        while True:
            try:
                await asyncio.sleep(self.config.discovery_interval)
                await self.discover_devices()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WIZ] Discovery loop error: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task: periodic heartbeat."""
        while True:
            try:
                await asyncio.sleep(self.config.heartbeat_interval)
                self.status.last_heartbeat = datetime.now().isoformat()
                if not self.status.connected:
                    # Attempt reconnection
                    self.status.connected = await self._test_connection()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[WIZ] Heartbeat error: {e}")

    def _emit_event(self, event_type: str, data: Any) -> None:
        """Emit an event to registered handlers."""
        if event_type in self._event_handlers:
            for handler in self._event_handlers[event_type]:
                try:
                    asyncio.create_task(handler(data)) if asyncio.iscoroutinefunction(
                        handler
                    ) else handler(data)
                except Exception as e:
                    logger.error(f"[WIZ] Event handler error: {e}")


class MockHAClient:
    """Mock Home Assistant client for development."""

    def __init__(self, config: GatewayConfigSchema):
        self.config = config

    async def get_config(self) -> Dict[str, Any]:
        """Get HA configuration."""
        return {
            "location_name": "Home",
            "latitude": 0.0,
            "longitude": 0.0,
            "elevation": 0,
        }

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get list of devices."""
        return []

    async def call_service(
        self, domain: str, service: str, entity_ids: List[str], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a service."""
        return {"success": True}

    async def close(self) -> None:
        """Close client."""
        pass
