from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7
from sqlalchemy import UniqueConstraint, ForeignKey, JSON
from features.training_plans.models.enum import ExcerciseUnitEnum
from libraries.db.session import Base


class TrainingPlan(Base):
    __tablename__ = "training_plans"
    __table_args__ = (UniqueConstraint("name", "user_uuid"),)
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    name: Mapped[str]

class Phase(Base):
    __tablename__ = "phases"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
    order: Mapped[int]
    description: str


class Session(Base):
    __tablename__ = "sessions"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
    phase_uuid: Mapped[UUID] = mapped_column(ForeignKey("phases.uuid"))
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    duration_minutes: Mapped[int]


class Excercise(Base):
    __tablename__ = "excercises"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    session_uuid: Mapped[UUID] = mapped_column(ForeignKey(column="sessions.uuid"))
    name: Mapped[str]
    description: Mapped[str]
    order: Mapped[int]
    feedback_enabled: Mapped[bool]
    sets: Mapped[int | None] = mapped_column(default=None)
    repetitions: Mapped[int | None] = mapped_column(default=None)
    duration_seconds: Mapped[int | None] = mapped_column(default=None)
    unit: Mapped[ExcerciseUnitEnum | None] = mapped_column(default=None)
    unit_label: Mapped[dict | None] = mapped_column(JSON)
