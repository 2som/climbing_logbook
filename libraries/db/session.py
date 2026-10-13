"""Async SQLAlchemy engine, session factory and request-scoped session dependency."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


_session_factory: async_sessionmaker[AsyncSession] | None = None

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models"""

    metadata = MetaData(naming_convention=convention)


def initialize_database(url: str) -> AsyncEngine:
    """Create the async engine and the process-wide session factory.

    Call once at application startup, before the first request.

    Returns:
        The created engine, so the caller can dispose it at shutdown.
    """
    global _session_factory
    engine = create_async_engine(url, echo=True)
    _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return engine


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped session; committing is the entry point's job.

    FastAPI runs dependency teardown after the HTTP response is sent, so a
    commit here would hide commit failures from the client (200 with lost
    data). Write endpoints therefore call ``session.commit()`` explicitly
    before returning; domain services still never commit. On teardown the
    session's context manager discards anything left uncommitted.

    Raises:
        RuntimeError: When ``initialize_database`` has not run yet.
    """
    async with open_session() as session:
        yield session


@asynccontextmanager
async def open_session() -> AsyncIterator[AsyncSession]:
    """Open a session outside a request (worker jobs, CLI); committing is the caller's job.

    Raises:
        RuntimeError: When ``initialize_database`` has not run yet.
    """
    if _session_factory is None:
        raise RuntimeError(
            "initialize_database() must be called at application startup"
        )
    async with _session_factory() as session:
        yield session
