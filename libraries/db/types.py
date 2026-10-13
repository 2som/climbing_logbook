from uuid import UUID

from sqlalchemy import String
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class UUIDString(TypeDecorator):
    """UUID stored as its canonical 36-char form (with dashes) in a VARCHAR(36)."""

    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value: UUID | str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return str(UUID(str(value)))

    def process_result_value(self, value: str | None, dialect: Dialect) -> UUID | None:
        if value is None:
            return None
        return UUID(value)
