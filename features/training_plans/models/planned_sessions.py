import datetime
from uuid import UUID

from sqlalchemy import Date, ForeignKey
from pydantic import BaseModel, Field
from sqlalchemy.orm import Mapped, mapped_column, relationship

from libraries.db.session import Base
from libraries.db.types import PydanticJSON
from uuid_extensions import uuid7


class ExerciseSet(BaseModel):
    repetitions: int | None = Field(default=None, ge=0)
    value: float | None = Field(default=None, ge=0)
    """In the exercise's ``unit`` (kg, seconds, mm, count)."""


class ExerciseFeedback(BaseModel):
    """Logged sets; exercise defaults only prefill, any number of sets allowed."""

    sets: list[ExerciseSet] = Field(default_factory=list)
    note: str | None = None


class PlannedSession(Base):
    __tablename__ = "planned_sessions"
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey("users.uuid"))
    plan_uuid: Mapped[UUID | None] = mapped_column(ForeignKey("training_plans.uuid"), nullable=True)
    session_uuid: Mapped[UUID] = mapped_column(ForeignKey("sessions.uuid"))
    finished: Mapped[bool] = mapped_column(default=False)
    duration_minutes: Mapped[int | None] = mapped_column(default=None)
    notes: Mapped[str | None] = mapped_column(default=None)
    start_date: Mapped[datetime.date] = mapped_column(Date)
    perveived_difficulty: Mapped[int | None] = mapped_column(default=None)

    exercises: Mapped[list["PlannedExercise"]] = relationship(cascade="all, delete-orphan")

class PlannedExercise(Base):
    __tablename__ = "planned_exercises"    
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    planned_session_uuid: Mapped[UUID] = mapped_column(ForeignKey("planned_sessions.uuid"))
    exercise_uuid: Mapped[UUID] = mapped_column(ForeignKey("exercises.uuid"))
    feedback: Mapped[ExerciseFeedback | None] = mapped_column(PydanticJSON(ExerciseFeedback), nullable=True)

