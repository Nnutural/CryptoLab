"""Key-store endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.status_codes import DEFAULT_MESSAGES, StatusCode
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.common import APIResponse
from app.schemas.keys import KeyListItem, KeyPublicMaterialResponse
from app.services import key_service

router = APIRouter()
USER_DEP = Depends(get_current_user)
DB_DEP = Depends(get_db)


@router.get("", response_model=APIResponse[list[KeyListItem]])
async def list_keys(
    request: Request,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[list[KeyListItem]]:
    """List non-deleted keys owned by the current user."""
    rows = key_service.list_for_user(db, user)
    data = [
        KeyListItem(
            id=UUID(row.id),
            key_type=row.key_type,
            algorithm=row.algorithm,
            paired_key_id=UUID(row.paired_key_id) if row.paired_key_id else None,
            label=row.label,
            created_at=row.created_at,
            expires_at=row.expires_at,
        )
        for row in rows
    ]
    return _ok(request, data)


@router.get("/{key_id}/public", response_model=APIResponse[KeyPublicMaterialResponse])
async def get_public_material(
    key_id: str,
    request: Request,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[KeyPublicMaterialResponse]:
    """Retrieve decrypted public key material (only for public-type keys)."""
    material, row = key_service.fetch_public_material(db, user, key_id)
    data = KeyPublicMaterialResponse(
        key_id=key_id, algorithm=row.algorithm, material=material
    )
    return _ok(request, data)


@router.delete("/{key_id}", response_model=APIResponse[None])
async def revoke_key(
    key_id: str,
    request: Request,
    user=USER_DEP,
    db: Session = DB_DEP,
) -> APIResponse[None]:
    """Soft-delete a user-owned key."""
    key_service.revoke(db, user, key_id)
    return _ok(request, None)


def _ok(request: Request, data: object) -> APIResponse:
    return APIResponse(
        code=StatusCode.OK,
        message=DEFAULT_MESSAGES[StatusCode.OK],
        data=data,
        trace_id=getattr(request.state, "trace_id", "00000000-0000-0000-0000-000000000000"),
    )
