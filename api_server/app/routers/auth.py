"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.auth import (
    CurrentUserResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)
from app.schemas.common import APIResponse
from app.services import user_service

router = APIRouter()
DB_DEP = Depends(get_db)
USER_DEP = Depends(get_current_user)


@router.post("/register", response_model=APIResponse[RegisterResponse])
async def register(
    request: Request,
    req: RegisterRequest,
    db: Session = DB_DEP,
) -> APIResponse[RegisterResponse]:
    """Create a user account."""
    return _ok(request, user_service.register(db, req))


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(
    request: Request,
    req: LoginRequest,
    db: Session = DB_DEP,
) -> APIResponse[LoginResponse]:
    """Verify credentials and return a JWT."""
    return _ok(request, user_service.login(db, req))


@router.post("/logout", response_model=APIResponse[None])
async def logout(
    request: Request,
    user=USER_DEP,
) -> APIResponse[None]:
    """Revoke the current JWT by adding its jti to the blacklist."""
    await user_service.logout(request.app.state.cache, user)
    return _ok(request, None)


@router.get("/me", response_model=APIResponse[CurrentUserResponse])
async def me(
    request: Request,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[CurrentUserResponse]:
    """Return the authenticated user's public profile."""
    return _ok(request, user_service.me(db, user))


def _ok(request: Request, data):
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
