from uuid import UUID

from pydantic import BaseModel
from enum import Enum as PyEnum

from sqlalchemy import JSON, Enum, String
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


class PydanticJSON[T: BaseModel](TypeDecorator):
    """Pydantic model stored as JSON; loads back into the model on read.

    Assign a whole new model instance to mark the column dirty. Mutating a
    loaded instance in place is not tracked by the ORM.
    """

    impl = JSON
    cache_ok = True

    def __init__(self, model: type[T]) -> None:
        super().__init__()
        self.model = model

    def process_bind_param(self, value: T | dict | None, dialect: Dialect) -> dict | None:
        if value is None:
            return None
        if isinstance(value, dict):
            value = self.model.model_validate(value)
        return value.model_dump(mode="json")

    def process_result_value(self, value: dict | None, dialect: Dialect) -> T | None:
        if value is None:
            return None
        return self.model.model_validate(value)


def ValueEnum(enum_cls: type[PyEnum]) -> Enum:
    """Enum column that stores member values (e.g. "kg"), not member names ("KG")."""
    return Enum(enum_cls, values_callable=lambda e: [m.value for m in e])
