"""Key-store DTOs."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class KeyListItem(BaseModel):
    id: UUID
    key_type: str
    algorithm: str
    paired_key_id: UUID | None = None
    label: str | None
    created_at: datetime
    expires_at: datetime | None


class KeygenResponse(BaseModel):
    key_id: str
    paired_key_id: str | None = None
    algorithm: str
    key_type: str


class KeyPublicMaterialResponse(BaseModel):
    key_id: str
    algorithm: str
    material: dict[str, str]


class SymmetricKeygenRequest(BaseModel):
    algorithm: str = Field(..., pattern="^(aes|sm4|rc6)$")
    key_size: int = Field(default=16, description="Key size in bytes")
    label: str | None = None

    def validate_key_size(self) -> None:
        if self.algorithm in {"sm4", "rc6"} and self.key_size != 16:
            raise ValueError(f"{self.algorithm.upper()} key must be 16 bytes")
        if self.algorithm == "aes" and self.key_size not in {16, 24, 32}:
            raise ValueError("AES key must be 16, 24, or 32 bytes")
