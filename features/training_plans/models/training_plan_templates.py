from uuid_extensions import uuid7
from sqlalchemy import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column
from libraries.db.session import Base
from features.training_plans.models.enum import ExcerciseUnitEnum


class PhaseTemplate(Base):
    __tablename__ = "phase_templates"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: str
    description: str


class SessionTemplate(Base):
    __tablename__ = "session_templates"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    description: Mapped[str | None]
    duration_minutes: Mapped[int]


class ExcerciseTemplate(Base):
    __tablename__ = "excercise_templates"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    description: Mapped[str]
    feedback_enabled: Mapped[bool]
    sets: Mapped[int | None] = mapped_column(default=None)
    repetitions: Mapped[int | None] = mapped_column(default=None)
    duration_seconds: Mapped[int | None] = mapped_column(default=None)
    unit: Mapped[ExcerciseUnitEnum | None] = mapped_column(default=None)
    unit_label: Mapped[dict | None] = mapped_column(JSON)
