"""Per-request context shared by middleware, services, and response helpers."""

from __future__ import annotations

from contextvars import ContextVar

DEFAULT_TRACE_ID = "00000000-0000-0000-0000-000000000000"

_trace_id: ContextVar[str] = ContextVar("trace_id", default=DEFAULT_TRACE_ID)


def set_trace_id(trace_id: str) -> None:
    """Store the active request trace id in a context-local slot."""
    _trace_id.set(trace_id)


def get_trace_id() -> str:
    """Return the active request trace id, or the zero UUID outside a request."""
    return _trace_id.get()
