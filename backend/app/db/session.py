from collections.abc import Generator

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record) -> None:  # type: ignore[no-untyped-def]
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_engine_from_url(database_url: str | URL, **engine_kwargs: object) -> Engine:
    url = make_url(str(database_url))
    resolved_engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
    resolved_engine_kwargs.update(engine_kwargs)
    if url.get_backend_name() == "sqlite":
        connect_args = dict(resolved_engine_kwargs.get("connect_args", {}))
        connect_args.setdefault("check_same_thread", False)
        resolved_engine_kwargs["connect_args"] = connect_args
    engine = create_engine(url, **resolved_engine_kwargs)
    if url.get_backend_name() == "sqlite":
        _enable_sqlite_foreign_keys(engine)
    return engine


def get_engine() -> Engine:
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    global _engine
    if _engine is None:
        _engine = create_engine_from_url(settings.database_url)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
    return _session_factory


def get_db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def reset_db_state() -> None:
    """Reset cached engine/session state for isolated tests and scripts."""

    global _engine, _session_factory

    if _engine is not None:
        _engine.dispose()

    _engine = None
    _session_factory = None
