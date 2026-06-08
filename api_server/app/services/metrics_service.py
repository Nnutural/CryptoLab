"""Algorithm performance metrics emission and querying."""

from __future__ import annotations

import asyncio
import os
import random
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import CryptoAPIException
from app.core.logging import get_logger
from app.core.status_codes import StatusCode
from app.db.session import get_session_factory
from app.models.algorithm_metric import AlgorithmMetric

logger = get_logger(__name__)
_pending_tasks: set[asyncio.Task[object]] = set()


@dataclass(frozen=True)
class MetricRecord:
    algorithm: str
    operation: str
    data_size_bytes: int
    duration_ns: int
    memory_kb: int | None = None


async def record(
    algorithm: str,
    operation: str,
    data_size_bytes: int,
    duration_ns: int,
    memory_kb: int | None = None,
    *,
    sampling_rate: float | None = None,
) -> None:
    """Schedule one sampled metrics INSERT without blocking the caller."""
    rate = _sampling_rate(sampling_rate)
    if rate <= 0 or (rate < 1.0 and random.random() >= rate):
        return

    metric = MetricRecord(
        algorithm=algorithm[:32],
        operation=operation[:32],
        data_size_bytes=max(0, int(data_size_bytes)),
        duration_ns=max(0, int(duration_ns)),
        memory_kb=memory_kb,
    )
    try:
        _track_task(asyncio.create_task(_insert(metric)))
    except RuntimeError as exc:
        logger.warning("metrics insert skipped: no running event loop", error=str(exc))


def record_nowait(
    algorithm: str,
    operation: str,
    data_size_bytes: int,
    duration_ns: int,
    memory_kb: int | None = None,
    *,
    sampling_rate: float | None = None,
) -> None:
    """Schedule record() from synchronous code that is running inside FastAPI."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as exc:
        logger.warning("metrics insert skipped: no running event loop", error=str(exc))
        return
    _track_task(
        loop.create_task(
            record(
                algorithm,
                operation,
                data_size_bytes,
                duration_ns,
                memory_kb,
                sampling_rate=sampling_rate,
            )
        )
    )


async def flush_pending(timeout_s: float = 1.0) -> None:
    """Wait for scheduled metric writes; intended for tests and shutdown paths."""
    deadline = asyncio.get_running_loop().time() + timeout_s
    while _pending_tasks:
        remaining = max(0.0, deadline - asyncio.get_running_loop().time())
        if remaining == 0:
            return
        await asyncio.wait(set(_pending_tasks), timeout=remaining)


def _track_task(task: asyncio.Task[object]) -> None:
    _pending_tasks.add(task)
    task.add_done_callback(_pending_tasks.discard)


def query_metrics(
    db: Session,
    *,
    algorithm: str | None = None,
    operation: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 200,
) -> list[AlgorithmMetric]:
    """Return recent metrics rows as a time series."""
    try:
        statement: Select[tuple[AlgorithmMetric]] = select(AlgorithmMetric)
        if algorithm:
            statement = statement.where(AlgorithmMetric.algorithm == algorithm)
        if operation:
            statement = statement.where(AlgorithmMetric.operation == operation)
        if since:
            statement = statement.where(AlgorithmMetric.recorded_at >= since)
        if until:
            statement = statement.where(AlgorithmMetric.recorded_at <= until)
        statement = statement.order_by(AlgorithmMetric.recorded_at.desc()).limit(limit)
        rows = list(db.execute(statement).scalars().all())
        rows.reverse()
        return rows
    except SQLAlchemyError as exc:
        raise CryptoAPIException(StatusCode.DATABASE_ERROR, "metrics_query_failed") from exc


def row_to_item(row: AlgorithmMetric) -> dict[str, object]:
    return {
        "algorithm": row.algorithm,
        "operation": row.operation,
        "duration_ns": row.duration_ns,
        "recorded_at": row.recorded_at,
    }


async def _insert(metric: MetricRecord) -> None:
    try:
        session_factory = get_session_factory()
        with session_factory() as db:
            db.add(
                AlgorithmMetric(
                    algorithm=metric.algorithm,
                    operation=metric.operation,
                    data_size_bytes=metric.data_size_bytes,
                    duration_ns=metric.duration_ns,
                    memory_kb=metric.memory_kb,
                    recorded_at=datetime.now(UTC),
                )
            )
            db.commit()
    except Exception as exc:  # pragma: no cover - integration tests verify non-throwing path
        logger.warning(
            "algorithm metrics insert failed",
            error=type(exc).__name__,
            algorithm=metric.algorithm,
            operation=metric.operation,
        )


def _sampling_rate(explicit: float | None) -> float:
    if explicit is not None:
        return _clamp_rate(explicit)
    raw = os.getenv("METRICS_SAMPLING_RATE", "0.1")
    try:
        return _clamp_rate(float(raw))
    except ValueError:
        logger.warning("invalid METRICS_SAMPLING_RATE, using default", value=raw)
        return 0.1


def _clamp_rate(value: float) -> float:
    return max(0.0, min(1.0, value))
