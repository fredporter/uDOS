import os
from typing import Callable, Iterable, Optional

from fastapi import HTTPException, Request

ROLE_HEADER = "X-UDOS-Role"
DEFAULT_ROLE = os.getenv("UDOS_DEFAULT_ROLE", "maintainer")


def _normalize_role(role: Optional[str]) -> str:
    if not role:
        return DEFAULT_ROLE.lower()
    return role.strip().lower()


def require_role(*allowed: str) -> Callable[[Request], None]:
    allowed_roles = {role.strip().lower() for role in allowed if role}

    async def guard(request: Request) -> None:
        role = _normalize_role(request.headers.get(ROLE_HEADER))
        if role in allowed_roles:
            return
        if not allowed_roles:
            return
        raise HTTPException(
            status_code=403,
            detail=f"Role '{role}' is not permitted; requires one of {sorted(allowed_roles)}",
        )

    return guard
