"""
Home Assistant Container Service
=================================

Main service entry point for Home Assistant gateway within uDOS Wizard.
Provides REST/WebSocket gateway for device integration and control.
"""

import asyncio
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

from wizard.services.logging_api import get_logger
from wizard.services.path_utils import get_repo_root
from wizard.services.home_assistant.gateway.manager import GatewayManager
from wizard.services.home_assistant.schemas.gateway import GatewayConfigSchema
from wizard.services.home_assistant.devices import DeviceRegistry, DiscoveryService, DeviceController, DeviceMonitor
from wizard.services.home_assistant.api.rest import router as rest_router, set_gateway_manager
from wizard.services.home_assistant.api.websocket import WebSocketManager

logger = get_logger("ha-service")


class HomeAssistantService:
    """Main Home Assistant gateway service."""

    def __init__(self, config: Optional[GatewayConfigSchema] = None):
        """Initialize Home Assistant service."""
        self.config = config or self._default_config()
        self.gateway_manager: Optional[GatewayManager] = None
        self.device_registry: Optional[DeviceRegistry] = None
        self.discovery_service: Optional[DiscoveryService] = None
        self.device_controller: Optional[DeviceController] = None
        self.device_monitor: Optional[DeviceMonitor] = None
        self.ws_manager: Optional[WebSocketManager] = None
        self.app = self._create_app()

    def _default_config(self) -> GatewayConfigSchema:
        """Create default configuration."""
        return GatewayConfigSchema(
            gateway_id="udos-ha-main",
            name="uDOS Home Assistant Gateway",
            ha_url="http://localhost:8123",
            ha_token="mock-token",
            ws_enabled=True,
            rest_enabled=True,
            auto_discovery=True,
        )

    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""

        @asynccontextmanager
        async def lifespan(_app: FastAPI):
            """Handle application startup/shutdown."""
            # Startup
            await self.startup()
            yield
            # Shutdown
            await self.shutdown()

        app = FastAPI(
            title="Home Assistant Gateway",
            description="REST/WebSocket gateway for Home Assistant",
            version="0.1.0",
            lifespan=lifespan,
        )

        # Include routers
        app.include_router(rest_router)

        # WebSocket endpoint
        @app.websocket("/ws/ha")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await self.ws_manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await self.ws_manager.handle_message(websocket, data)
            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)
            except Exception as e:
                logger.error(f"[WIZ] WebSocket error: {e}")
                self.ws_manager.disconnect(websocket)

        # Health check
        @app.get("/health")
        async def health():
            """Service health check."""
            return {"status": "ok", "service": "home-assistant"}

        return app

    async def startup(self) -> None:
        """Initialize service components."""
        try:
            logger.info("[WIZ] Starting Home Assistant service")

            # Initialize device components
            self.device_registry = DeviceRegistry()
            self.discovery_service = DiscoveryService(self.device_registry)
            self.device_controller = DeviceController(self.device_registry)
            self.device_monitor = DeviceMonitor(self.device_registry)

            # Initialize gateway manager
            self.gateway_manager = GatewayManager(self.config)
            if not await self.gateway_manager.initialize():
                raise RuntimeError("Failed to initialize gateway manager")

            set_gateway_manager(self.gateway_manager)

            # Initialize WebSocket manager
            self.ws_manager = WebSocketManager(self.gateway_manager)

            # Register event handlers
            self.gateway_manager.on_event(
                "device_discovered", self._on_device_discovered
            )
            self.gateway_manager.on_event(
                "state_changed", self._on_state_changed
            )

            logger.info("[WIZ] Home Assistant service started successfully")
        except Exception as e:
            logger.error(f"[WIZ] Service startup failed: {e}")
            raise

    async def shutdown(self) -> None:
        """Cleanup service components."""
        try:
            logger.info("[WIZ] Shutting down Home Assistant service")
            if self.gateway_manager:
                await self.gateway_manager.shutdown()
            logger.info("[WIZ] Home Assistant service stopped")
        except Exception as e:
            logger.error(f"[WIZ] Service shutdown error: {e}")

    async def _on_device_discovered(self, device) -> None:
        """Handle device discovered event."""
        logger.info(f"[WIZ] Device discovered: {device.name} ({device.id})")
        # Register device in registry
        self.device_registry.register_device(device.id, device.to_dict())
        # Broadcast to WebSocket clients
        if self.ws_manager:
            await self.ws_manager.broadcast_discovery([device.to_dict()])

    async def _on_state_changed(self, state_data) -> None:
        """Handle state changed event."""
        logger.debug(f"[WIZ] State changed: {state_data}")
        # Broadcast to WebSocket clients
        if self.ws_manager and isinstance(state_data, dict):
            await self.ws_manager.broadcast_state_change(
                state_data.get("device_id", "unknown"),
                state_data,
            )


# ============================================================================
# Module Entry Point
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info("[WIZ] Launching Home Assistant service")

    # Create service instance
    service = HomeAssistantService()

    # Run FastAPI app
    uvicorn.run(
        service.app,
        host="0.0.0.0",
        port=8765,
        log_level="info",
    )
