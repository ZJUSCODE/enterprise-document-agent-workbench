from dataclasses import dataclass

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


@dataclass(frozen=True)
class Principal:
    actor: str
    roles: set[str]
    authenticated: bool

    def has_any_role(self, expected: set[str]) -> bool:
        return "admin" in self.roles or bool(self.roles & expected)


def get_current_principal(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    x_actor: str | None = Header(default=None, alias="X-Actor"),
) -> Principal:
    settings = get_settings()
    if not settings.api_auth_enabled:
        return Principal(
            actor=x_actor or settings.default_actor,
            roles={"admin", "operator", "reviewer", "viewer"},
            authenticated=False,
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )

    credential = settings.api_credentials.get(x_api_key)
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return Principal(actor=credential.actor, roles=credential.roles, authenticated=True)


def require_roles(principal: Principal, *roles: str) -> None:
    expected = set(roles)
    if principal.has_any_role(expected):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Requires one of roles: {', '.join(sorted(expected))}",
    )
