"""SQLAlchemy engine/session wiring and FastAPI dependency."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _engine_kwargs(database_url: str) -> dict[str, object]:
    if database_url in {"sqlite://", "sqlite:///:memory:"}:
        return {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
            "future": True,
        }
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}, "future": True}
    return {"pool_pre_ping": True, "future": True}


def init_engine(database_url: str | None = None) -> Engine:
    """Create or replace the configured engine."""
    global _engine, _session_factory
    url = database_url or get_settings().database_url
    if _engine is None or str(_engine.url) != url:
        _engine = create_engine(url, **_engine_kwargs(url))
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False, class_=Session)
    return _engine


def get_engine() -> Engine:
    """Return the active engine, creating it on first use."""
    return init_engine()


def get_session_factory() -> sessionmaker[Session]:
    """Return the active session factory."""
    if _session_factory is None:
        init_engine()
    if _session_factory is None:
        raise RuntimeError("database session factory is not initialized")
    return _session_factory


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a short-lived ORM session."""
    factory = get_session_factory()
    with factory() as session:
        yield session


def reset_database(database_url: str = "sqlite://") -> None:
    """Test helper: rebuild all metadata on a fresh engine."""
    engine = init_engine(database_url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def dispose_engine() -> None:
    """Dispose the active engine."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
