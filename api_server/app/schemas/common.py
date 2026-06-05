"""Shared response envelope and primitive DTOs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Uniform response envelope (see design doc §3.2.1)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    code: int = Field(..., description="Business status code (see status_codes.StatusCode)")
    message: str = Field(..., description="Human-readable summary")
    data: T | None = Field(default=None, description="Operation payload, schema-typed per route")
    trace_id: str = Field(..., description="UUID propagated through middleware → logs → DB")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    debug: dict[str, Any] | None = Field(
        default=None,
        description="Set only when debug mode is enabled AND caller is an admin",
    )


class BytesField(BaseModel):
    """A bytes value carried across the wire as either base64 or hex."""

    model_config = ConfigDict(extra="forbid")

    encoding: str = Field(..., pattern="^(base64|hex)$")
    value: str
