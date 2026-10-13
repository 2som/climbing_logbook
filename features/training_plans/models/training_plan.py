from uuid import UUID

from enum import StrEnum


from sqlalchemy.orm import Mapped, mapped_column
from uuid_extensions import uuid7
from sqlalchemy import UniqueConstraint, ForeignKey, JSON
from libraries.db.session import Base


class ExcerciseUnitEnum(StrEnum):
    KG = "kg"
    SECONDS = "seconds"


class TrainingPlan(Base):
    __tablename__ = "training_plans"
    __table_args__ = (UniqueConstraint("name", "user_uuid"),)
    uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    user_uuid: Mapped[UUID] = mapped_column(ForeignKey('users.uuid'))
    name: Mapped[str]

# class TrainingPlanPhase(Base):
#     __tablename__ = "training_plan_phases"
#     uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
#     name: Mapped[str]
#     training_plan_uuid: Mapped[UUID] = mapped_column(ForeignKey("training_plans.uuid"))
#     description: str


# class TrainingPhaseTemplate(Base):
#     __tablename__ = "training_phase_templates"
#     uuid: UUID
#     name: str
#     description: str


# class TrainingSessionTemplate:
#     __tablename__ = "training_session_templates"
#     uuid: UUID
#     name: str
#     description: str


# class TrainingExcerciseTemplate:
#     __tablename__ = "training_excercise_templates"
#     uuid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
#     name: Mapped[str]
#     description: Mapped[str]
#     feedback_enabled: Mapped[bool]
#     sets: Mapped[int | None] = mapped_column(default=None)
#     repetitions: Mapped[int | None] = mapped_column(default=None)
#     duration_seconds: Mapped[int | None] = mapped_column(default=None)
#     unit: Mapped[ExcerciseUnitEnum | None] = mapped_column(default=None)
#     unit_label: Mapped[dict | None] = mapped_column(JSON)


# class UserTrainingPlanPhase:
#     pass
