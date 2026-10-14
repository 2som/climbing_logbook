import datetime
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_extensions import uuid7
from sqlalchemy import Date, UniqueConstraint, ForeignKey, JSON
from features.training_plans.models.enum import ExerciseUnitEnum, SessionTypeEnum
from libraries.db.session import Base
from libraries.db.types import ValueEnum


class TrainingPlan(Base):
    __tablename__ = "training_plans"
    __table_args__ = (UniqueConstraint("name", "user_uuid"),)
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    name: Mapped[str]

    phases: Mapped[list["Phase"]] = relationship(order_by="Phase.order")


class ActiveTrainingPlan(Base):
    __tablename__ = "users_active_training_plans"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"), unique=True)
    plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
    start_date: Mapped[datetime.date] = mapped_column(Date, default=None)
    end_date: Mapped[datetime.date]= mapped_column(Date, default=None)

class Phase(Base):
    __tablename__ = "phases"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    name: Mapped[str]
    plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
    description: Mapped[str]
    duration_weeks: Mapped[int]
    order: Mapped[int]

    sessions: Mapped[list["Session"]] = relationship()

class Session(Base):
    __tablename__ = "sessions"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
    phase_uuid: Mapped[UUID] = mapped_column(ForeignKey("phases.uuid"))
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(default=None)
    duration_minutes: Mapped[int]
    type: Mapped[SessionTypeEnum] = mapped_column(ValueEnum(SessionTypeEnum), default=SessionTypeEnum.OPEN)

    excercises: Mapped[list["Exercise"]] = relationship(order_by="Exercise.order")


class Exercise(Base):
    __tablename__ = "exercises"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    session_uuid: Mapped[UUID] = mapped_column(ForeignKey("sessions.uuid"))
    exercise_template_uuid: Mapped[UUID | None] = mapped_column(ForeignKey("exercise_templates.uuid"), nullable=True)
    name: Mapped[str]
    description: Mapped[str]
    order: Mapped[int]
    feedback_enabled: Mapped[bool]
    sets: Mapped[int | None] = mapped_column(default=None)
    repetitions: Mapped[int | None] = mapped_column(default=None)
    duration_seconds: Mapped[int | None] = mapped_column(default=None)
    unit: Mapped[ExerciseUnitEnum | None] = mapped_column(ValueEnum(ExerciseUnitEnum), default=None)
    unit_label: Mapped[str | None] = mapped_column(default=None)