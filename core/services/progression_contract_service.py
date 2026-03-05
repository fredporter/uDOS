"""Shared progression contract for PLAY LENS, SKIN, and MODE surfaces."""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any

from core.services.gameplay_service import PLAY_OPTIONS, PLAY_UNLOCK_RULES
from core.services.logging_api import get_repo_root

_DEFAULT_LENS_SKIN_RECOMMENDATIONS: dict[str, set[str]] = {
    "hethack": {"c64", "teletext", "nes", "default"},
    "nethack": {"c64", "teletext", "nes", "default"},
    "elite": {"teletext", "medium", "prose", "default"},
    "rpgbbs": {"prose", "medium", "c64", "default"},
    "crawler3d": {"nes", "teletext", "c64", "default"},
}

LENS_OPTION_MAP: dict[str, str] = {
    "hethack": "dungeon",
    "nethack": "dungeon",
    "elite": "galaxy",
    "rpgbbs": "social",
    "crawler3d": "ascension",
}


def _load_lens_skin_recommendations() -> dict[str, set[str]]:
    config_path = get_repo_root() / "core" / "config" / "lens_skin_game_catalog_v1_5.json"
    if not config_path.exists():
        return dict(_DEFAULT_LENS_SKIN_RECOMMENDATIONS)
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return dict(_DEFAULT_LENS_SKIN_RECOMMENDATIONS)
    if not isinstance(payload, dict):
        return dict(_DEFAULT_LENS_SKIN_RECOMMENDATIONS)

    profiles = payload.get("profiles", {})
    if not isinstance(profiles, dict):
        return dict(_DEFAULT_LENS_SKIN_RECOMMENDATIONS)

    out = dict(_DEFAULT_LENS_SKIN_RECOMMENDATIONS)
    for lens_id, row in profiles.items():
        if not isinstance(row, dict):
            continue
        recommended = row.get("recommended_skins", [])
        if not isinstance(recommended, list):
            continue
        items = {str(item).strip().lower() for item in recommended if str(item).strip()}
        if items:
            out[str(lens_id).strip().lower()] = items
    return out


LENS_SKIN_RECOMMENDATIONS: dict[str, set[str]] = _load_lens_skin_recommendations()


@dataclass(frozen=True)
class SkinPolicyContext:
    progression: dict[str, Any]
    policy_flag: str | None
    policy_note: str | None
    active_lens: str
    recommended_skins: list[str]
    lens_readiness: dict[str, Any] | None


def build_progression_contract(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Normalize progression snapshot into a canonical LENS/SKIN contract."""
    stats = snapshot.get("stats", {}) if isinstance(snapshot.get("stats"), dict) else {}
    progress = snapshot.get("progress", {}) if isinstance(snapshot.get("progress"), dict) else {}
    blocked = snapshot.get("blocked_requirements", [])
    blocked_requirements = [str(x) for x in blocked if str(x).strip()] if isinstance(blocked, list) else []
    token_rows = snapshot.get("unlock_tokens", [])
    token_ids = [
        str(row.get("id", "")).strip()
        for row in token_rows
        if isinstance(row, dict) and str(row.get("id", "")).strip()
    ] if isinstance(token_rows, list) else []
    play_options = snapshot.get("play_options", [])
    options_by_id = {
        str(item.get("id", "")).strip(): item
        for item in play_options
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    } if isinstance(play_options, list) else {}

    lens_readiness: dict[str, dict[str, Any]] = {}
    for lens, option_id in LENS_OPTION_MAP.items():
        option = options_by_id.get(option_id, {})
        if not isinstance(option, dict):
            option = {}
        blocked_by = option.get("blocked_by", [])
        blocked_list = [str(x) for x in blocked_by if str(x).strip()] if isinstance(blocked_by, list) else []
        lens_readiness[lens] = {
            "available": bool(option.get("available", lens == "hethack")),
            "option_id": option_id,
            "blocked_by": blocked_list,
            "recommendation": _recommendation_from_blocked(blocked_list),
        }

    token_rules: dict[str, list[str]] = {}
    for token_id, meta in PLAY_UNLOCK_RULES.items():
        req = meta.get("requirements", {})
        if not isinstance(req, dict):
            req = {}
        token_rules[token_id] = _requirements_to_labels(req)

    variables = {
        "xp": int(stats.get("xp", 0) or 0),
        "hp": int(stats.get("hp", 100) or 100),
        "gold": int(stats.get("gold", 0) or 0),
        "level": int(progress.get("level", 1) or 1),
        "achievement_level": int(progress.get("achievement_level", 0) or 0),
    }
    metrics = progress.get("metrics", {}) if isinstance(progress.get("metrics"), dict) else {}
    return {
        "active_lens": str(snapshot.get("active_lens", "hethack")),
        "variables": variables,
        "metrics": {str(k): int(v or 0) for k, v in metrics.items()},
        "blocked_requirements": blocked_requirements,
        "unlock_token_ids": token_ids,
        "token_requirements": token_rules,
        "lens_readiness": lens_readiness,
    }


def build_skin_policy_context(
    *,
    progression: dict[str, Any],
    selected_skin: str,
    available_skins: list[str],
) -> SkinPolicyContext:
    """Return advisory, non-blocking SKIN policy flags from shared contract."""
    contract = build_progression_contract(progression)
    active_lens = str(contract.get("active_lens", "")).strip().lower()
    recommended = sorted(LENS_SKIN_RECOMMENDATIONS.get(active_lens, set()))
    selected = str(selected_skin).strip().lower()
    readiness = contract.get("lens_readiness", {}).get(active_lens)

    if not recommended:
        return SkinPolicyContext(
            progression=progression,
            policy_flag="skin_lens_unmapped",
            policy_note=(
                "[policy-flag] No skin recommendation map for active lens yet. "
                "Current build flags this but does not enforce it."
            ),
            active_lens=active_lens or "unknown",
            recommended_skins=[],
            lens_readiness=readiness if isinstance(readiness, dict) else None,
        )

    available_set = {item.lower() for item in available_skins}
    if selected in set(recommended):
        if isinstance(readiness, dict) and not readiness.get("available", True):
            recommendation = readiness.get("recommendation") or "Progression requirements not met yet."
            return SkinPolicyContext(
                progression=progression,
                policy_flag="skin_lens_progression_drift",
                policy_note=(
                    "[policy-flag] Skin/lens pair is mapped but lens progression is currently blocked. "
                    f"{recommendation} Not enforced in this cycle."
                ),
                active_lens=active_lens,
                recommended_skins=recommended,
                lens_readiness=readiness,
            )
        return SkinPolicyContext(
            progression=progression,
            policy_flag=None,
            policy_note=None,
            active_lens=active_lens,
            recommended_skins=recommended,
            lens_readiness=readiness if isinstance(readiness, dict) else None,
        )

    if available_set and not (set(recommended) & available_set):
        return SkinPolicyContext(
            progression=progression,
            policy_flag=None,
            policy_note=None,
            active_lens=active_lens,
            recommended_skins=recommended,
            lens_readiness=readiness if isinstance(readiness, dict) else None,
        )

    hint = ", ".join(recommended)
    suffix = ""
    if isinstance(readiness, dict) and not readiness.get("available", True):
        if recommendation := readiness.get("recommendation"):
            suffix = f" Lens progression note: {recommendation}"
    return SkinPolicyContext(
        progression=progression,
        policy_flag="skin_lens_mismatch",
        policy_note=(
            "[policy-flag] Skin may not match active lens progression profile. "
            f"Recommended for {active_lens}: {hint}.{suffix} Not enforced in this cycle."
        ),
        active_lens=active_lens,
        recommended_skins=recommended,
        lens_readiness=readiness if isinstance(readiness, dict) else None,
    )


def _requirements_to_labels(requirements: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    if min_xp := int(requirements.get("min_xp", 0) or 0):
        labels.append(f"xp>={min_xp}")
    if min_hp := int(requirements.get("min_hp", 0) or 0):
        labels.append(f"hp>={min_hp}")
    if min_gold := int(requirements.get("min_gold", 0) or 0):
        labels.append(f"gold>={min_gold}")
    if min_level := int(requirements.get("min_level", 0) or 0):
        labels.append(f"level>={min_level}")
    if min_ach := int(requirements.get("min_achievement_level", 0) or 0):
        labels.append(f"achievement_level>={min_ach}")
    if required_gate := str(requirements.get("required_gate", "")).strip():
        labels.append(f"gate:{required_gate}")
    if required_token := str(requirements.get("required_token", "")).strip():
        labels.append(f"token:{required_token}")
    min_metric = requirements.get("min_metric", {})
    if isinstance(min_metric, dict):
        labels.extend(
            f"{str(key)}>={int(value or 0)}"
            for key, value in min_metric.items()
        )
    return labels


def _recommendation_from_blocked(blocked: list[str]) -> str | None:
    if not blocked:
        return None
    first = blocked[0]
    match first:
        case value if value.startswith("xp>="):
            return f"Increase XP until {value}."
        case value if value.startswith("achievement_level>="):
            return f"Increase achievements until {value}."
        case value if value.startswith("gold>="):
            return f"Earn more gold until {value}."
        case value if value.startswith("gate:"):
            gate_id = value.split(":", 1)[1]
            return f"Complete gate {gate_id}."
        case value if value.startswith("token:"):
            token_id = value.split(":", 1)[1]
            return f"Unlock token {token_id}."
        case _:
            return f"Resolve blocked requirement: {first}."
