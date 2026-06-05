"""Key-store DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class KeyListItem(BaseModel):
    id: UUID
    key_type: str
    algorithm: str
    label: str | None
    created_at: datetime
    expires_at: datetime | None
