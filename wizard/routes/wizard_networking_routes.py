"""Wizard Networking Standard routes."""

from typing import Awaitable, Callable, Optional, List

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel, Field

from wizard.services.wizard_networking_service import get_wizard_networking_service

AuthGuard = Optional[Callable[[Request], Awaitable[str]]]


class PairingStartResponse(BaseModel):
    pairing_token: str
    challenge: str
    wizard_public_key: str
    wizard_signature: str
    wizard_url: str
    wizard_ip: str
    expires_at: str
    channel: str


class PairingCompleteRequest(BaseModel):
    pairing_token: str
    peer_name: str
    peer_public_key: str
    signature: str


class WireGuardRegisterRequest(BaseModel):
    peer_public_key: str
    allowed_ips: Optional[List[str]] = None


class WireGuardConfigResponse(BaseModel):
    peer_id: str
    config: str


class PeerRecord(BaseModel):
    peer_id: str
    name: str
    public_key: str
    paired_at: str
    last_seen: Optional[str] = None


class RadioLinkStatus(BaseModel):
    enabled: bool
    transport_available: bool
    last_started: Optional[str] = None
    last_stopped: Optional[str] = None


class WizardIdentity(BaseModel):
    wizard_url: str
    wizard_ip: str
    public_key: str
    created_at: str


class PeeringCapsule(BaseModel):
    payload: dict
    signature: str


def create_wizard_networking_routes(auth_guard: AuthGuard = None) -> APIRouter:
    router = APIRouter(prefix="/api/networking", tags=["wizard-networking"])
    service = get_wizard_networking_service()

    def _auth(request: Request):
        if auth_guard:
            return auth_guard(request)
        return None

    @router.get("/identity", response_model=WizardIdentity)
    async def get_identity(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return service.get_identity()

    class PairingStartRequest(BaseModel):
        channel: str = Field(default="qr")

    @router.post("/pairing/start", response_model=PairingStartResponse)
    async def start_pairing(
        payload: PairingStartRequest = Body(default=PairingStartRequest()),
        request: Request = None,
    ):
        if auth_guard:
            await auth_guard(request)
        session = service.start_pairing(channel=payload.channel)
        payload = service.get_pairing_payload(session)
        return PairingStartResponse(
            pairing_token=payload["pairing_token"],
            challenge=payload["challenge"],
            wizard_public_key=payload["wizard_public_key"],
            wizard_signature=payload["wizard_signature"],
            wizard_url=payload["wizard_url"],
            wizard_ip=payload["wizard_ip"],
            expires_at=payload["expires_at"],
            channel=payload["channel"],
        )

    @router.post("/pairing/complete", response_model=PeerRecord)
    async def complete_pairing(payload: PairingCompleteRequest, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        try:
            peer = service.complete_pairing(
                token=payload.pairing_token,
                peer_name=payload.peer_name,
                peer_public_key=payload.peer_public_key,
                signature=payload.signature,
            )
            return PeerRecord(**peer.__dict__)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.get("/peers", response_model=List[PeerRecord])
    async def list_peers(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return [PeerRecord(**peer) for peer in service.list_peers()]

    @router.post("/peering/capsule", response_model=PeeringCapsule)
    async def create_peering_capsule(
        peer_id: str = Body(...), ttl_minutes: int = Body(default=60), request: Request = None
    ):
        if auth_guard:
            await auth_guard(request)
        return service.create_peering_capsule(peer_id, ttl_minutes=ttl_minutes)

    @router.post("/peering/verify")
    async def verify_peering_capsule(payload: PeeringCapsule, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        valid = service.verify_peering_capsule(payload.dict())
        return {"valid": valid}

    @router.post("/peers/{peer_id}/wireguard")
    async def register_wireguard_peer(
        peer_id: str, payload: WireGuardRegisterRequest, request: Request = None
    ):
        if auth_guard:
            await auth_guard(request)
        try:
            record = service.register_wireguard_peer(
                peer_id=peer_id,
                peer_public_key=payload.peer_public_key,
                allowed_ips=payload.allowed_ips,
            )
            return {"status": "success", "peer_id": peer_id, "wizard_public_key": record.wizard_public_key}
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @router.post("/peers/{peer_id}/wireguard/rotate")
    async def rotate_wireguard_keys(peer_id: str, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        try:
            record = service.rotate_wireguard_keys(peer_id)
            return {"status": "success", "peer_id": peer_id, "wizard_public_key": record.wizard_public_key}
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/peers/{peer_id}/wireguard/config", response_model=WireGuardConfigResponse)
    async def get_wireguard_config(peer_id: str, request: Request = None):
        if auth_guard:
            await auth_guard(request)
        try:
            config = service.get_wireguard_config(peer_id)
            return WireGuardConfigResponse(peer_id=peer_id, config=config)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @router.get("/radiolink/status", response_model=RadioLinkStatus)
    async def radiolink_status(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return RadioLinkStatus(**service.radiolink_status())

    @router.post("/radiolink/start", response_model=RadioLinkStatus)
    async def radiolink_start(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return RadioLinkStatus(**service.radiolink_start())

    @router.post("/radiolink/stop", response_model=RadioLinkStatus)
    async def radiolink_stop(request: Request = None):
        if auth_guard:
            await auth_guard(request)
        return RadioLinkStatus(**service.radiolink_stop())

    return router
