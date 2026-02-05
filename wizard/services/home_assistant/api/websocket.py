"""WebSocket gateway for Home Assistant real-time updates."""

from typing import Set, Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

from wizard.services.logging_manager import get_logger
from wizard.services.home_assistant.gateway.manager import GatewayManager

logger = get_logger("ha-websocket-gateway")


class WebSocketManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self, gateway: GatewayManager):
        self.gateway = gateway
        self.active_connections: Set[WebSocket] = set()
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        self._message_queue: asyncio.Queue = asyncio.Queue()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"[WIZ] WebSocket connected. Active: {len(self.active_connections)}")
        await self._send_welcome(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self.active_connections.discard(websocket)
        # Remove from all subscriptions
        for subscribers in self.subscriptions.values():
            subscribers.discard(websocket)
        logger.info(f"[WIZ] WebSocket disconnected. Active: {len(self.active_connections)}")

    async def handle_message(self, websocket: WebSocket, message: str) -> bool:
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "subscribe":
                await self._handle_subscribe(websocket, data)
            elif msg_type == "unsubscribe":
                await self._handle_unsubscribe(websocket, data)
            elif msg_type == "get_status":
                await self._handle_get_status(websocket)
            elif msg_type == "get_devices":
                await self._handle_get_devices(websocket)
            elif msg_type == "get_device":
                await self._handle_get_device(websocket, data)
            elif msg_type == "call_service":
                await self._handle_call_service(websocket, data)
            elif msg_type == "ping":
                await self._send_message(websocket, {"type": "pong"})
            else:
                await self._send_error(websocket, f"Unknown message type: {msg_type}")

            return True
        except json.JSONDecodeError:
            await self._send_error(websocket, "Invalid JSON")
            return False
        except Exception as e:
            logger.error(f"[WIZ] WebSocket message error: {e}")
            await self._send_error(websocket, str(e))
            return False

    async def broadcast_state_change(self, device_id: str, state: Dict[str, Any]) -> None:
        """Broadcast a device state change to subscribed clients."""
        message = {
            "type": "state_changed",
            "device_id": device_id,
            "state": state,
        }
        await self._broadcast_to_subscribers(f"device:{device_id}", message)

    async def broadcast_discovery(self, devices: List[Dict[str, Any]]) -> None:
        """Broadcast device discovery notification."""
        message = {
            "type": "discovery",
            "devices": devices,
            "count": len(devices),
        }
        await self._broadcast_to_all(message)

    # ============================================================================
    # Private Methods
    # ============================================================================

    async def _send_welcome(self, websocket: WebSocket) -> None:
        """Send welcome message to new connection."""
        status = self.gateway.get_status()
        message = {
            "type": "welcome",
            "gateway_id": self.gateway.config.gateway_id,
            "version": status.version,
            "connected": status.connected,
        }
        await self._send_message(websocket, message)

    async def _send_message(self, websocket: WebSocket, message: Dict[str, Any]) -> bool:
        """Send message to specific WebSocket."""
        try:
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"[WIZ] Failed to send WebSocket message: {e}")
            self.disconnect(websocket)
            return False

    async def _send_error(self, websocket: WebSocket, error: str) -> None:
        """Send error message to WebSocket."""
        await self._send_message(
            websocket, {"type": "error", "message": error, "timestamp": _get_timestamp()}
        )

    async def _broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected clients."""
        disconnected = set()
        for websocket in self.active_connections:
            if not await self._send_message(websocket, message):
                disconnected.add(websocket)
        for ws in disconnected:
            self.disconnect(ws)

    async def _broadcast_to_subscribers(
        self, channel: str, message: Dict[str, Any]
    ) -> None:
        """Broadcast message to subscribers of a channel."""
        if channel not in self.subscriptions:
            return
        disconnected = set()
        for websocket in self.subscriptions[channel]:
            if not await self._send_message(websocket, message):
                disconnected.add(websocket)
        for ws in disconnected:
            self.disconnect(ws)

    async def _handle_subscribe(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        """Handle subscription request."""
        topics = data.get("topics", [])
        for topic in topics:
            if topic not in self.subscriptions:
                self.subscriptions[topic] = set()
            self.subscriptions[topic].add(websocket)
        logger.info(f"[WIZ] WebSocket subscribed to: {topics}")
        await self._send_message(
            websocket,
            {
                "type": "subscribed",
                "topics": topics,
                "timestamp": _get_timestamp(),
            },
        )

    async def _handle_unsubscribe(
        self, websocket: WebSocket, data: Dict[str, Any]
    ) -> None:
        """Handle unsubscription request."""
        topics = data.get("topics", [])
        for topic in topics:
            if topic in self.subscriptions:
                self.subscriptions[topic].discard(websocket)
        logger.info(f"[WIZ] WebSocket unsubscribed from: {topics}")

    async def _handle_get_status(self, websocket: WebSocket) -> None:
        """Handle status request."""
        status = self.gateway.get_status()
        await self._send_message(
            websocket,
            {
                "type": "status",
                "data": {
                    "status": status.status,
                    "connected": status.connected,
                    "uptime_seconds": status.uptime_seconds,
                    "total_devices": status.total_devices,
                    "available_devices": status.available_devices,
                    "active_connections": status.active_connections,
                },
                "timestamp": _get_timestamp(),
            },
        )

    async def _handle_get_devices(self, websocket: WebSocket) -> None:
        """Handle get devices request."""
        devices = await self.gateway.get_devices()
        await self._send_message(
            websocket,
            {
                "type": "devices",
                "devices": [d.to_dict() for d in devices],
                "count": len(devices),
                "timestamp": _get_timestamp(),
            },
        )

    async def _handle_get_device(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        """Handle get device request."""
        device_id = data.get("device_id")
        if not device_id:
            await self._send_error(websocket, "device_id required")
            return
        device = await self.gateway.get_device(device_id)
        if not device:
            await self._send_error(websocket, f"Device not found: {device_id}")
            return
        state = await self.gateway.get_device_state(device_id)
        await self._send_message(
            websocket,
            {
                "type": "device",
                "device": device.to_dict(),
                "state": state.to_dict() if state else None,
                "timestamp": _get_timestamp(),
            },
        )

    async def _handle_call_service(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        """Handle service call request."""
        domain = data.get("domain")
        service = data.get("service")
        entity_ids = data.get("entity_ids", [])
        service_data = data.get("data", {})

        if not domain or not service:
            await self._send_error(websocket, "domain and service required")
            return

        success = await self.gateway.call_service(domain, service, entity_ids, service_data)
        await self._send_message(
            websocket,
            {
                "type": "service_called",
                "success": success,
                "domain": domain,
                "service": service,
                "timestamp": _get_timestamp(),
            },
        )


def _get_timestamp() -> str:
    """Get ISO format timestamp."""
    from datetime import datetime

    return datetime.now().isoformat()
