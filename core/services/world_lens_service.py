"""v1.3.22 world-lens feature flag and single-region readiness service."""

from __future__ import annotations

import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from core.services.chunking_contract import parse_place_ref
from core.services.logging_api import get_repo_root


class WorldLensService:
    """Manage first 3D world-lens enablement behind a feature flag."""

    def __init__(
        self,
        *,
        config_file: Optional[Path] = None,
        state_file: Optional[Path] = None,
        seed_file: Optional[Path] = None,
    ) -> None:
        repo_root = get_repo_root()
        self.config_file = config_file or repo_root / "core" / "config" / "v1_3_22_world_lens_mvp.json"
        self.seed_file = seed_file or repo_root / "core" / "src" / "spatial" / "locations-seed.default.json"
        private_root = repo_root / "memory" / "bank" / "private"
        private_root.mkdir(parents=True, exist_ok=True)
        self.state_file = state_file or private_root / "world_lens_state.json"
        self._config = self._load_config()
        self._state = self._load_state()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _default_config(self) -> Dict[str, Any]:
        return {
            "version": "1.3.22",
            "feature_flag": {
                "env_var": "UDOS_3D_WORLD_LENS_ENABLED",
                "default_enabled": False,
            },
            "single_region": {
                "id": "earth_subterra_slice",
                "title": "Subterra Relay Vertical Slice",
                "entry_place_id": "subterra-relay",
                "allowed_place_ids": ["andes-pass", "lunar-gateway", "subterra-relay"],
                "anchor_prefix": "EARTH:",
            },
            "contracts": {
                "locid": "v1.3.18",
                "seed_depth": "v1.3.19",
                "world_adapter": "v1.3.21",
            },
        }

    def _load_config(self) -> Dict[str, Any]:
        fallback = self._default_config()
        if not self.config_file.exists():
            return fallback
        try:
            parsed = json.loads(self.config_file.read_text(encoding="utf-8"))
        except Exception:
            return fallback
        if not isinstance(parsed, dict):
            return fallback
        merged = deepcopy(fallback)
        merged.update({k: v for k, v in parsed.items() if k in {"version"}})
        for key in {"feature_flag", "single_region", "contracts"}:
            incoming = parsed.get(key)
            if isinstance(incoming, dict):
                merged[key].update(incoming)
        return merged

    def _default_state(self) -> Dict[str, Any]:
        return {
            "version": self._config.get("version", "1.3.22"),
            "enabled": bool(self._config.get("feature_flag", {}).get("default_enabled", False)),
            "updated_at": self._now_iso(),
            "updated_by": "system-default",
        }

    def _load_state(self) -> Dict[str, Any]:
        if not self.state_file.exists():
            state = self._default_state()
            self._write_state(state)
            return state
        try:
            parsed = json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            state = self._default_state()
            self._write_state(state)
            return state
        if not isinstance(parsed, dict):
            return self._default_state()
        state = self._default_state()
        state.update({k: v for k, v in parsed.items() if k in {"enabled", "updated_at", "updated_by", "version"}})
        return state

    def _write_state(self, state: Dict[str, Any]) -> None:
        self.state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")

    @staticmethod
    def _coerce_env_bool(raw: Optional[str]) -> Optional[bool]:
        if raw is None:
            return None
        norm = str(raw).strip().lower()
        if norm in {"1", "true", "yes", "on", "enabled"}:
            return True
        if norm in {"0", "false", "no", "off", "disabled"}:
            return False
        return None

    def _effective_enabled(self) -> tuple[bool, str]:
        env_var = str(self._config.get("feature_flag", {}).get("env_var", "UDOS_3D_WORLD_LENS_ENABLED"))
        env_enabled = self._coerce_env_bool(os.getenv(env_var))
        if env_enabled is not None:
            return env_enabled, f"env:{env_var}"
        return bool(self._state.get("enabled", False)), "state"

    def _load_seed_places(self) -> Dict[str, Dict[str, Any]]:
        try:
            raw = json.loads(self.seed_file.read_text(encoding="utf-8"))
        except Exception:
            return {}
        out: Dict[str, Dict[str, Any]] = {}
        for row in raw.get("locations", []):
            if not isinstance(row, dict):
                continue
            place_id = str(row.get("placeId") or "").strip()
            if not place_id:
                continue
            out[place_id] = row
        return out

    def _slice_contract_status(self) -> Dict[str, Any]:
        region = self._config.get("single_region", {})
        allowed = [str(x).strip() for x in region.get("allowed_place_ids", []) if str(x).strip()]
        allowed_set = set(allowed)
        entry_place_id = str(region.get("entry_place_id") or "").strip()
        anchor_prefix = str(region.get("anchor_prefix") or "").strip()

        places = self._load_seed_places()
        missing_place_ids = [pid for pid in allowed if pid not in places]

        invalid_place_refs = []
        prefix_mismatch_place_ids = []
        for pid in allowed:
            row = places.get(pid)
            if not isinstance(row, dict):
                continue
            place_ref = str(row.get("placeRef") or "")
            if not parse_place_ref(place_ref):
                invalid_place_refs.append({"place_id": pid, "place_ref": place_ref})
            if anchor_prefix and not place_ref.startswith(anchor_prefix):
                prefix_mismatch_place_ids.append(pid)

        disconnected_place_ids = []
        if entry_place_id and entry_place_id in places and entry_place_id in allowed_set:
            seen = set()
            stack = [entry_place_id]
            while stack:
                cur = stack.pop()
                if cur in seen:
                    continue
                seen.add(cur)
                links = places.get(cur, {}).get("links", [])
                for nxt in links if isinstance(links, list) else []:
                    nxt_id = str(nxt).strip()
                    if nxt_id in allowed_set and nxt_id not in seen:
                        stack.append(nxt_id)
            disconnected_place_ids = [pid for pid in allowed if pid not in seen]
        elif allowed:
            disconnected_place_ids = list(allowed)

        valid = (
            len(allowed) > 0
            and not missing_place_ids
            and not invalid_place_refs
            and not prefix_mismatch_place_ids
            and not disconnected_place_ids
        )
        return {
            "valid": valid,
            "entry_place_id": entry_place_id,
            "allowed_place_ids": allowed,
            "missing_place_ids": missing_place_ids,
            "invalid_place_refs": invalid_place_refs,
            "prefix_mismatch_place_ids": prefix_mismatch_place_ids,
            "disconnected_place_ids": disconnected_place_ids,
        }

    def set_enabled(self, enabled: bool, actor: str = "unknown") -> Dict[str, Any]:
        self._state["enabled"] = bool(enabled)
        self._state["updated_at"] = self._now_iso()
        self._state["updated_by"] = actor
        self._write_state(self._state)
        return dict(self._state)

    def status(
        self,
        *,
        username: str,
        map_status: Optional[Dict[str, Any]] = None,
        progression_ready: bool = True,
    ) -> Dict[str, Any]:
        enabled, source = self._effective_enabled()
        region = self._config.get("single_region", {})
        slice_contract = self._slice_contract_status()

        blocking_reason = None
        in_region = False

        if not enabled:
            blocking_reason = "feature_flag_disabled"
        elif not progression_ready:
            blocking_reason = "progression_gate_blocked"
        elif not slice_contract.get("valid"):
            blocking_reason = "slice_contract_invalid"
        elif not isinstance(map_status, dict) or not map_status.get("ok"):
            blocking_reason = "map_runtime_unavailable"
        else:
            place_id = str(map_status.get("current_place_id") or "")
            allowed = {str(x) for x in region.get("allowed_place_ids", [])}
            in_region = place_id in allowed
            if not in_region:
                blocking_reason = "outside_single_region"

        ready = enabled and progression_ready and in_region and bool(slice_contract.get("valid")) and blocking_reason is None
        return {
            "ok": True,
            "username": username,
            "version": self._config.get("version", "1.3.22"),
            "lens": {
                "id": "world-3d-mvp",
                "enabled": enabled,
                "enabled_source": source,
                "ready": ready,
                "blocking_reason": blocking_reason,
            },
            "single_region": {
                "id": region.get("id"),
                "title": region.get("title"),
                "entry_place_id": region.get("entry_place_id"),
                "allowed_place_ids": list(region.get("allowed_place_ids", [])),
                "anchor_prefix": region.get("anchor_prefix"),
                "active": in_region,
            },
            "slice_contract": slice_contract,
            "contracts": dict(self._config.get("contracts", {})),
            "state": {
                "updated_at": self._state.get("updated_at"),
                "updated_by": self._state.get("updated_by"),
            },
        }


_world_lens_service: Optional[WorldLensService] = None


def get_world_lens_service() -> WorldLensService:
    global _world_lens_service
    if _world_lens_service is None:
        _world_lens_service = WorldLensService()
    return _world_lens_service
