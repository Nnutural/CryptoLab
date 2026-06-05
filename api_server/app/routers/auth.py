"""Authentication: register / login / logout / refresh."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.common import APIResponse

router = APIRouter()


@router.post("/register", response_model=APIResponse[None])
async def register(_req: RegisterRequest) -> APIResponse[None]:
    """Create a new user account."""
    raise NotImplementedError("services.user_service.register(req)")


@router.post("/login", response_model=APIResponse[LoginResponse])
async def login(_req: LoginRequest) -> APIResponse[LoginResponse]:
    """Verify credentials, mint and return a JWT."""
    raise NotImplementedError("services.user_service.login(req)")


@router.post("/logout", response_model=APIResponse[None])
async def logout(_user: User = Depends(get_current_user)) -> APIResponse[None]:
    """Add the current JWT to the Redis blacklist."""
    raise NotImplementedError("services.user_service.logout(user, jti)")
