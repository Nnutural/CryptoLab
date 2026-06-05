"""User account orchestration: register / login / logout."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest


async def register(_db: AsyncSession, _req: RegisterRequest) -> User:
    raise NotImplementedError(
        "generate salt (16 random bytes) → PBKDF2-SHA256(password, salt, 100_000) "
        "→ insert User → return"
    )


async def login(_db: AsyncSession, _req: LoginRequest) -> LoginResponse:
    raise NotImplementedError(
        "lookup user by username → constant-time verify_password "
        "→ issue_access_token → return LoginResponse"
    )


async def logout(_jti: str, _expires_at_epoch: int) -> None:
    raise NotImplementedError(
        "SET jwt_blacklist:{jti} = '1' EXPIRE (expires_at - now)"
    )
