"""Algorithm metrics DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class AlgorithmMetricItem(BaseModel):
    algorithm: str
    operation: str
    duration_ns: int
    recorded_at: datetime
