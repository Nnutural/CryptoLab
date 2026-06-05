"""Key-store endpoints: list / get / delete user-owned keys."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.keys import KeyListItem

router = APIRouter()


@router.get("", response_model=APIResponse[list[KeyListItem]])
async def list_keys(_user: User = Depends(get_current_user)) -> APIResponse[list[KeyListItem]]:
    """List non-deleted keys owned by the current user."""
    raise NotImplementedError("services.key_service.list_for_user(user)")


@router.delete("/{key_id}", response_model=APIResponse[None])
async def revoke_key(
    _key_id: UUID,
    _user: User = Depends(get_current_user),
) -> APIResponse[None]:
    """Soft-delete (sets `deleted_at`) — actual KEK-wrapped material is kept for forensics."""
    raise NotImplementedError("services.key_service.revoke(user, key_id)")
