"""REST API endpoints for Home Assistant gateway."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel

from wizard.services.logging_api import get_logger
from wizard.services.home_assistant.gateway.manager import GatewayManager
from wizard.services.home_assistant.schemas.device import DeviceSchema, DeviceType
from wizard.services.home_assistant.schemas.entity import EntitySchema

logger = get_logger("ha-rest-api")

router = APIRouter(prefix="/api/ha", tags=["home-assistant"])


# ============================================================================
# Request/Response Models
# ============================================================================


class ServiceCallRequest(BaseModel):
    """Service call request."""

    domain: str
    service: str
    entity_ids: List[str]
    data: Dict[str, Any] = {}


class ConfigUpdateRequest(BaseModel):
    """Gateway configuration update request."""

    name: Optional[str] = None
    auto_discovery: Optional[bool] = None
    discovery_interval: Optional[int] = None


# ============================================================================
# Dependency: Get Gateway Manager
# ============================================================================

_gateway_manager: Optional[GatewayManager] = None


def set_gateway_manager(manager: GatewayManager) -> None:
    """Set the gateway manager instance."""
    global _gateway_manager
    _gateway_manager = manager


def get_gateway_manager() -> GatewayManager:
    """Get the current gateway manager."""
    if _gateway_manager is None:
        raise RuntimeError("Gateway manager not initialized")
    return _gateway_manager


# ============================================================================
# Status & Health Endpoints
# ============================================================================


@router.get("/status")
async def get_gateway_status() -> Dict[str, Any]:
    """Get gateway status and health information."""
    try:
        manager = get_gateway_manager()
        status = manager.get_status()
        return {
            "success": True,
            "data": {
                "status": status.status,
                "connected": status.connected,
                "uptime_seconds": status.uptime_seconds,
                "total_devices": status.total_devices,
                "available_devices": status.available_devices,
                "total_entities": status.total_entities,
                "active_connections": status.active_connections,
                "last_heartbeat": status.last_heartbeat,
                "version": status.version,
                "error_message": status.error_message,
            },
        }
    except Exception as e:
        logger.error(f"[WIZ] Status endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        manager = get_gateway_manager()
        status = manager.get_status()
        return {
            "healthy": status.connected,
            "status": status.status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail="Gateway not available")


# ============================================================================
# Device Discovery & Management
# ============================================================================


@router.get("/discover")
async def discover_devices() -> Dict[str, Any]:
    """Trigger device discovery."""
    try:
        manager = get_gateway_manager()
        devices = await manager.discover_devices()
        logger.info(f"[WIZ] Device discovery: {len(devices)} devices found")
        return {
            "success": True,
            "data": {"devices": [d.to_dict() for d in devices], "count": len(devices)},
        }
    except Exception as e:
        logger.error(f"[WIZ] Discovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices")
async def list_devices(
    type_filter: Optional[DeviceType] = Query(None),
    manufacturer: Optional[str] = Query(None),
    available_only: bool = Query(False),
) -> Dict[str, Any]:
    """List all discovered devices with optional filtering."""
    try:
        manager = get_gateway_manager()
        devices = await manager.get_devices()

        # Apply filters
        if type_filter:
            devices = [d for d in devices if d.type == type_filter]
        if manufacturer:
            devices = [d for d in devices if d.manufacturer == manufacturer]
        if available_only:
            devices = [
                d for d in devices
                if manager.device_states.get(d.id, {}).is_available
            ]

        return {
            "success": True,
            "data": {
                "devices": [d.to_dict() for d in devices],
                "count": len(devices),
                "filters": {
                    "type": type_filter,
                    "manufacturer": manufacturer,
                    "available_only": available_only,
                },
            },
        }
    except Exception as e:
        logger.error(f"[WIZ] List devices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}")
async def get_device(device_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific device."""
    try:
        manager = get_gateway_manager()
        device = await manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        state = await manager.get_device_state(device_id)
        return {
            "success": True,
            "data": {
                "device": device.to_dict(),
                "state": state.to_dict() if state else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[WIZ] Get device error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/devices/{device_id}/state")
async def get_device_state(device_id: str) -> Dict[str, Any]:
    """Get current state of a device."""
    try:
        manager = get_gateway_manager()
        state = await manager.get_device_state(device_id)
        if not state:
            raise HTTPException(status_code=404, detail="Device state not found")
        return {"success": True, "data": state.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[WIZ] Get device state error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Entity Management
# ============================================================================


@router.get("/entities")
async def list_entities(
    domain: Optional[str] = Query(None),
    device_id: Optional[str] = Query(None),
) -> Dict[str, Any]:
    """List all entities with optional filtering."""
    try:
        manager = get_gateway_manager()
        entities = list(manager.entities.values())

        # Apply filters
        if domain:
            entities = [e for e in entities if e.domain == domain]
        if device_id:
            entities = [e for e in entities if e.device_id == device_id]

        return {
            "success": True,
            "data": {
                "entities": [e.to_dict() for e in entities],
                "count": len(entities),
            },
        }
    except Exception as e:
        logger.error(f"[WIZ] List entities error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/entities/{entity_id}")
async def get_entity(entity_id: str) -> Dict[str, Any]:
    """Get entity details and current state."""
    try:
        manager = get_gateway_manager()
        entity = manager.entities.get(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        state = await manager.get_entity_state(entity_id)
        return {
            "success": True,
            "data": {
                "entity": entity.to_dict(),
                "state": state.to_dict() if state else None,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[WIZ] Get entity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Service Calls
# ============================================================================


@router.post("/services/{domain}/{service}")
async def call_service(
    domain: str, service: str, request: ServiceCallRequest
) -> Dict[str, Any]:
    """Call a Home Assistant service."""
    try:
        manager = get_gateway_manager()
        success = await manager.call_service(
            domain, service, request.entity_ids, request.data
        )
        return {
            "success": success,
            "data": {"domain": domain, "service": service},
        }
    except Exception as e:
        logger.error(f"[WIZ] Service call error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turn-on")
async def turn_on(entity_ids: List[str] = Body(...)) -> Dict[str, Any]:
    """Turn on entities (light, switch, etc)."""
    try:
        manager = get_gateway_manager()
        success = await manager.call_service("homeassistant", "turn_on", entity_ids, {})
        return {"success": success, "data": {"entity_ids": entity_ids}}
    except Exception as e:
        logger.error(f"[WIZ] Turn on error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/turn-off")
async def turn_off(entity_ids: List[str] = Body(...)) -> Dict[str, Any]:
    """Turn off entities (light, switch, etc)."""
    try:
        manager = get_gateway_manager()
        success = await manager.call_service(
            "homeassistant", "turn_off", entity_ids, {}
        )
        return {"success": success, "data": {"entity_ids": entity_ids}}
    except Exception as e:
        logger.error(f"[WIZ] Turn off error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Configuration
# ============================================================================


@router.get("/config")
async def get_config() -> Dict[str, Any]:
    """Get gateway configuration."""
    try:
        manager = get_gateway_manager()
        return {
            "success": True,
            "data": manager.config.to_dict(),
        }
    except Exception as e:
        logger.error(f"[WIZ] Get config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/config")
async def update_config(request: ConfigUpdateRequest) -> Dict[str, Any]:
    """Update gateway configuration."""
    try:
        manager = get_gateway_manager()
        updated = False

        if request.name is not None:
            manager.config.name = request.name
            updated = True
        if request.auto_discovery is not None:
            manager.config.auto_discovery = request.auto_discovery
            updated = True
        if request.discovery_interval is not None:
            manager.config.discovery_interval = request.discovery_interval
            updated = True

        return {
            "success": updated,
            "data": manager.config.to_dict(),
        }
    except Exception as e:
        logger.error(f"[WIZ] Update config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


from datetime import datetime
